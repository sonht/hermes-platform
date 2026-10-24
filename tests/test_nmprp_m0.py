import copy
import json
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from support import nmprp_m0 as m0, nmprp_stages as st, nmprp_may_chay as mc
from support.nmprp_client import NmprpError
from tests.test_nmprp_stages import Client, P, M0
from tests.test_nmprp_may_chay import luot


def responder(fail_at=0):
    calls = []
    def runner(argv):
        if argv[-2] != '-z':
            return 0, '{"total_tokens": 500}'
        unit = json.loads(argv[-1].split('PINNED_INPUT_JSON:\n')[1])
        calls.append([p['code'] for p in unit['pl2']])
        if len(calls) == fail_at:
            raise m0.KnownFailure('MODEL_TIMEOUT_150s')
        items = []
        for p in unit['pl2']:
            row = copy.deepcopy(M0['items'][0]); row['pl2_code'] = p['code']; items.append(row)
        return 0, json.dumps({'items': items}, ensure_ascii=False)
    runner.calls = calls
    return runner


class M0BatchTests(unittest.TestCase):
    def test_unknown_marker_is_canonicalized_but_real_evidence_is_checked(self):
        for code in ('CHUA_RO', 'MD_CHUA_RO'):
            result = copy.deepcopy(M0)
            value = {'ma': code, 'van_ban': 'CHUA_RO', 'trich_nguon': ''}
            result['items'][0]['noi_dung']['muc_dich'] = value
            st.validate('m0', {'pl2': [P]}, result)
            self.assertEqual(value['van_ban'], '')
        for code, text, quote in [('MD_DIEU_TRI', 'CHUA_RO', ''),
                                  ('CHUA_RO', 'invented', ''),
                                  ('CHUA_RO', 'CHUA_RO', 'invented')]:
            result = copy.deepcopy(M0)
            result['items'][0]['noi_dung']['muc_dich'] = {
                'ma': code, 'van_ban': text, 'trich_nguon': quote}
            with self.assertRaises(st.StageError):
                st.validate('m0', {'pl2': [P]}, result)

    def test_repaired_quarantined_batch_is_replayed_without_model_call(self):
        self.job['ds_pl2'] = self.job['ds_pl2'][:10]
        r = responder()
        self.assertEqual(mc.xu_ly_luot(Client(), self.job, self.cfg, r), 'XONG')
        from pathlib import Path
        folder = Path(self.tmp.name) / self.job['luot_id']
        target = next(p for p in folder.glob('*.json') if not p.name.endswith('.context.json'))
        saved = json.loads(target.read_text())
        for item in saved['result']['items']:
            item['noi_dung']['muc_dich'] = {'ma': 'CHUA_RO', 'van_ban': 'CHUA_RO', 'trich_nguon': ''}
        invalid = target.with_suffix('.invalid-1')
        invalid.write_text(json.dumps(saved))
        target.unlink()
        r2, c2 = responder(), Client()
        self.assertEqual(mc.xu_ly_luot(c2, self.job, self.cfg, r2), 'XONG')
        self.assertEqual(r2.calls, [])
        self.assertTrue(invalid.exists())
        self.assertEqual(c2.loai('stage')[0][2][0]['noi_dung']['muc_dich']['van_ban'], '')

    def test_python_m_worker_keeps_resumable_stop_state(self):
        import sys
        script = r"""
import os, sys, tempfile, runpy
from support import nmprp_client, nmprp_stages
class Client:
    def may_chao(self, *a, **kw): return {}
    def may_nhan(self): return {'luot': {'luot_id': 'HL_aaaaaaaaaaaa', 'quy_trinh': 'm0'}}
    def may_ket_thuc(self, lid, state, note): print('FINAL_STATE=' + state)
def stop(*args):
    from support.nmprp_may_chay import DungLuot
    raise DungLuot('TAM_DUNG', 'M0_EVIDENCE_NOT_IN_SOURCE')
nmprp_client.NmprpClient = Client
nmprp_stages.execute = stop
with tempfile.TemporaryDirectory() as td:
    os.environ['HERMES_RUNNER_LOCK'] = td + '/lock'
    os.environ['HERMES_RUNNER_DUNG'] = td + '/stop'
    sys.argv = ['worker', '--mot-lan']
    runpy._run_module_as_main('support.nmprp_may_chay')
"""
        result = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('FINAL_STATE=TAM_DUNG', result.stdout)
        self.assertNotIn('FINAL_STATE=LOI', result.stdout)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.ready = patch.object(st, 'ready', return_value=['PHAN_RA'])
        self.ready.start(); self.addCleanup(self.ready.stop)
        self.cfg = mc.CauHinh(enabled_stages=['m0'], stage_state=self.tmp.name)
        self.job = luot(quy_trinh='m0', ds_pl2=[dict(P, code='BS_%03d.10' % n) for n in range(130)],
                        m0={'hop_dong': 'm0-1'}, me=10, han_goi=0, tran_token=3000000)

    def test_130_pl2_are_13_calls_with_progress_and_text_codes(self):
        c, r = Client(), responder()
        self.assertEqual(mc.xu_ly_luot(c, self.job, self.cfg, r), 'XONG')
        self.assertEqual(len(r.calls), 13)
        progress = [g[2]['pl2_xong'] for g in c.loai('tien_do') if g[1].get('GUI', {}).get('tt') == 'XONG']
        self.assertEqual(progress, list(range(10, 131, 10)))
        self.assertEqual(c.loai('stage')[0][2][0]['pl2_code'], 'BS_000.10')

    def test_default_five_and_upper_bound_ten(self):
        for count, size in [(None, 5), (60, 10)]:
            self.job['luot_id'] = 'HL_' + ('a' if count is None else 'b') * 12
            self.job['me'] = count
            self.job['ds_pl2'] = self.job['ds_pl2'][:11]
            r = responder()
            self.assertEqual(mc.xu_ly_luot(Client(), self.job, self.cfg, r), 'XONG')
            self.assertEqual(len(r.calls[0]), size)

    def test_timeout_pauses_names_batch_and_resume_skips_delivered_pl2(self):
        c, r = Client(), responder(fail_at=2)
        self.assertEqual(mc.xu_ly_luot(c, self.job, self.cfg, r), 'TAM_DUNG')
        self.assertIn('lô 2/13', c.cuoi()[1])
        self.assertIn('BS_010.10', c.cuoi()[1])
        self.assertIn('MODEL_TIMEOUT', c.cuoi()[1])
        self.job['pl2_da_xong'] = r.calls[0]
        r2 = responder()
        self.assertEqual(mc.xu_ly_luot(Client(), self.job, self.cfg, r2), 'XONG')
        self.assertEqual(len(r2.calls), 12)
        self.assertNotIn('BS_000.10', sum(r2.calls, []))

    def test_network_error_after_model_replays_without_paying(self):
        c, r = Client(), responder()
        c.may_stage = lambda *a: (_ for _ in ()).throw(NmprpError('network'))
        with self.assertRaises(NmprpError):
            mc.xu_ly_luot(c, self.job, self.cfg, r)
        self.assertEqual(len(r.calls), 1)
        r2 = responder()
        self.assertEqual(mc.xu_ly_luot(Client(), self.job, self.cfg, r2), 'XONG')
        self.assertEqual(len(r2.calls), 12)

    def test_partial_delivery_replays_original_batch_but_sends_only_missing(self):
        self.job['ds_pl2'] = self.job['ds_pl2'][:10]
        c, r = Client(), responder()
        self.assertEqual(mc.xu_ly_luot(c, self.job, self.cfg, r), 'XONG')
        self.job['pl2_da_xong'] = [p['code'] for p in self.job['ds_pl2'][:5]]
        c2, r2 = Client(), responder()
        self.assertEqual(mc.xu_ly_luot(c2, self.job, self.cfg, r2), 'XONG')
        self.assertEqual(r2.calls, [])
        self.assertEqual(len(c2.loai('stage')[0][2]), 5)

    def test_repeated_timeout_is_bounded_and_accounted(self):
        self.job['ds_pl2'] = self.job['ds_pl2'][:5]
        for _ in range(m0.MAX_ATTEMPTS):
            self.assertEqual(mc.xu_ly_luot(Client(), self.job, self.cfg, responder(fail_at=1)), 'TAM_DUNG')
        r = responder()
        c = Client()
        self.assertEqual(mc.xu_ly_luot(c, self.job, self.cfg, r), 'TAM_DUNG')
        self.assertIn('RETRY_LIMIT', c.cuoi()[1])
        self.assertEqual(r.calls, [])

    def test_container_timeout_and_host_timeout_are_distinguished(self):
        argv = ['docker', 'exec', '-u', 'hermes', 'container', 'hermes', '-z', 'body']
        with patch.object(m0.subprocess, 'run', return_value=subprocess.CompletedProcess([], 124, '')) as p:
            with self.assertRaises(m0.KnownFailure):
                m0.bounded(argv)
            cmd = p.call_args.args[0]
            self.assertEqual(cmd[5:10], ['timeout', '--signal=TERM', '--kill-after=5s', '150s', 'hermes'])
            self.assertEqual(p.call_args.kwargs['timeout'], 170)
        with patch.object(m0.subprocess, 'run', side_effect=subprocess.TimeoutExpired(argv, 170)):
            with self.assertRaises(subprocess.TimeoutExpired):
                m0.bounded(argv)

    def test_heartbeat_and_cancel_before_publish(self):
        import time
        r = responder()
        def slow(argv):
            if '-z' in argv:
                time.sleep(.05)
            return r(argv)
        c = Client(dung_o_lan=3)
        with patch.object(m0, 'HEARTBEAT', .01):
            self.assertEqual(mc.xu_ly_luot(c, self.job, self.cfg, slow), 'DA_HUY')
        self.assertEqual(c.loai('stage'), [])
        self.assertGreaterEqual(c.n_tien_do, 3)

    def test_exit_one_reports_safe_cause_estimate_and_preserves_pending(self):
        c = Client()
        result = subprocess.CompletedProcess([], 1, '', 'AuthenticationError: invalid api key sk-secret')
        with patch.object(m0.subprocess, 'run', return_value=result) as process:
            self.assertEqual(mc.xu_ly_luot(c, self.job, self.cfg), 'TAM_DUNG')
            self.assertIn('HERMES_EXIT_1:AUTHENTICATION_FAILED', c.cuoi()[1])
            self.assertNotIn('sk-secret', c.cuoi()[1])
            self.assertGreater(c.loai('tien_do')[-1][2]['token_da_dung'], 0)
            argv = process.call_args.args[0]
            self.assertTrue(argv[argv.index('--usage-file') + 1].startswith('/opt/data/profiles/nmprp-stages/workspace/'))
            self.assertEqual(mc.xu_ly_luot(Client(), self.job, self.cfg), 'TAM_DUNG')
            self.assertEqual(process.call_count, 1)


if __name__ == '__main__':
    unittest.main()
