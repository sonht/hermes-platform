import copy
import hashlib
import json
import tempfile
import unittest
from unittest.mock import patch

from support import nmprp_stages as st, nmprp_may_chay as mc
from support.nmprp_client import NmprpError, check_post_allowed, check_allowed
from tests.test_nmprp_may_chay import FakeNmprp, luot
from tests.test_nmprp_shadow import runner_tra

P = {'code': '7.10', 'name': 'Chọc hút dịch điều trị u nang giáp'}
M0 = {'items': [{'pl2_code': '7.10', 'trang_thai': 'READY', 'noi_dung': {
    'hanh_dong_chinh': {'ma': 'HD_CHOC_HUT', 'van_ban': 'Chọc hút', 'trich_nguon': 'Chọc hút'},
    'dich': {'ma': 'DICH_NANG', 'van_ban': 'u nang giáp', 'trich_nguon': 'u nang giáp'}}, 'co': [], 'ly_do': ''}]}


class Client(FakeNmprp):
    def may_stage(self, lid, endpoint, items):
        self._ghi('stage', endpoint, items)
        return {'ok': True}

    def may_input_manifest(self, lid, sid):
        return {'data': {'artifact_id': sid, 'content_sha256': 'a'}, 'error': None}

    def may_knowledge(self, lid):
        return {'nhan': 'HPKB_ACTIVE', 'phien_ban': '1', 'items': []}

    def may_modifier(self, lid):
        return {'ok': True, 'hop_dong': 'modifier-doc@1', 'items': [], 'sha256': st.digest([])}


class StageTests(unittest.TestCase):
    def test_ready_requires_matching_installed_files_and_runtime(self):
        cfg = mc.CauHinh(enabled_stages=['m0', 'm2'])
        def probe(argv):
            self.assertIn('hermes --version', argv[-1])
            files = ['SOUL.md', 'skills/nmprp-stage-m0/SKILL.md']
            return 0, '\n'.join(hashlib.sha256((st.ROOT / f).read_bytes()).hexdigest() + '  ' + f for f in files)
        self.assertEqual(st.ready(cfg, probe), ['PHAN_RA'])
        self.assertEqual(st.ready(cfg, lambda _: (1, '')), [])
        self.assertEqual(st.ready(mc.CauHinh(), probe), [])
        with self.assertRaises(ValueError):
            mc.CauHinh(enabled_stages=['fake'])

    def test_m0_calls_real_dispatcher_and_separate_result_endpoint(self):
        with tempfile.TemporaryDirectory() as d, patch.object(st, 'ready', return_value=['PHAN_RA']):
            c, r = Client(), runner_tra(M0)
            job = luot(quy_trinh='m0', ds_pl2=[P], m0={'hop_dong': 'm0-1'})
            cfg = mc.CauHinh(enabled_stages=['m0'], stage_state=d)
            self.assertEqual(mc.xu_ly_luot(c, job, cfg, r), 'XONG')
            self.assertEqual(c.loai('stage')[0][1], 'm0-phan-ra')
            self.assertEqual(c.loai('goi_y'), [])
            self.assertEqual(c.loai('ket_qua'), [])
            self.assertIn('nmprp-stage-m0', r.goi[0])
            records = [p for p in (st.Path(d) / job['luot_id']).glob('*.json') if not p.name.endswith('.context.json')]
            self.assertEqual(len(records), 1)
            self.assertEqual(json.loads(records[0].read_text())['review'], 'AI_PROVISIONAL')
            # Lost response/restart: same job is re-submitted from checkpoint, never pays again.
            r2 = runner_tra({'wrong': True})
            self.assertEqual(mc.xu_ly_luot(c, job, cfg, r2), 'XONG')
            self.assertEqual(r2.goi, [])
            # Rerun creates a new journal and makes a new inference.
            job['luot_id'] = 'HL_bbbbbbbbbbbb'
            self.assertEqual(mc.xu_ly_luot(c, job, cfg, runner_tra(M0)), 'XONG')

    def test_invalid_or_unready_handler_never_reports_success(self):
        with tempfile.TemporaryDirectory() as d:
            cfg = mc.CauHinh(enabled_stages=['m0'], stage_state=d)
            job = luot(quy_trinh='m0', ds_pl2=[P], m0={'hop_dong': 'm0-1'})
            for caps, answer, state in [([], M0, 'LOI'), (['PHAN_RA'], {'items': []}, 'TAM_DUNG')]:
                c = Client()
                with patch.object(st, 'ready', return_value=caps):
                    self.assertEqual(mc.xu_ly_luot(c, job, cfg, runner_tra(answer)), state)
                self.assertEqual(c.loai('stage'), [])
                self.assertEqual(c.cuoi()[0], state)

    def test_m2_coverage_scope_and_no_upstream_calls(self):
        unit = {'khoa_nhanh': 'Endocrine > Thyroid', 'pl2': [P]}
        answer = {'items': [{'khoa_nhanh': unit['khoa_nhanh'], 'pl2_codes': ['7.10'], 'ten': 'Chọc hút',
                            'dinh_nghia': 'Hút dịch nang', 'ranh_gioi_noi_bo': 'Không lấy tế bào',
                            'ly_do': 'Điều trị', 'ly_do_thanh_vien': {'7.10': 'Chọc hút dịch'}}]}
        st.validate('m2', unit, answer)
        for mutate in (lambda x: x['items'][0].update(pl2_codes=['7.1']),
                       lambda x: x['items'][0].update(khoa_nhanh='elsewhere'),
                       lambda x: x['items'].append(copy.deepcopy(x['items'][0]))):
            bad = copy.deepcopy(answer); mutate(bad)
            with self.assertRaises(st.StageError):
                st.validate('m2', unit, bad)
        with tempfile.TemporaryDirectory() as d, patch.object(st, 'ready', return_value=['DE_XUAT_HO']):
            c = Client()
            job = luot(quy_trinh='m2', ds_pl2=[P], m23={'quy_trinh': 'm2', 'snapshot_id': 'S1', 'nut': [unit]})
            self.assertEqual(mc.xu_ly_luot(c, job, mc.CauHinh(enabled_stages=['m2'], stage_state=d), runner_tra(answer)), 'XONG')
            self.assertEqual([x[1] for x in c.loai('stage')], ['m2-ho'])
            self.assertEqual(c.loai('goi_y'), [])

    def test_m3_does_not_claim_semantic_pass_without_evidence(self):
        unit = {'de_xuat_id': 'H1', 'thanh_vien': [P], 'modifier_dictionary': {'items': []}}
        answer = {'items': [{'de_xuat_id': 'H1', 'action': 'Chọc hút', 'target': 'u nang giáp', 'ly_do': 'Điều trị',
                             'bien_the': [{'pl2_code': '7.10', 'modifier_ids': [], 'tai_dung_dac_diem': {'ket_qua': 'UNCERTAIN'}}]}]}
        st.validate('m3', unit, answer)
        for field, value in [('pl2_code', 7.10), ('modifier_ids', ['fake'])]:
            bad = copy.deepcopy(answer); bad['items'][0]['bien_the'][0][field] = value
            with self.assertRaises(st.StageError):
                st.validate('m3', unit, bad)
        answer['items'][0]['bien_the'][0]['tai_dung_dac_diem'] = {'ket_qua': 'PASS'}
        with self.assertRaisesRegex(st.StageError, 'NOT_VERIFIED'):
            st.validate('m3', unit, answer)

    def test_m0_quotes_and_text_codes_are_checked(self):
        for code in ('1.246', '1.258', '7.10', '7.1', '00123', 'BS_06.010'):
            unit = {'pl2': [dict(P, code=code)]}
            answer = copy.deepcopy(M0); answer['items'][0]['pl2_code'] = code
            st.validate('m0', unit, answer)
        answer['items'][0]['noi_dung']['dich']['trich_nguon'] = 'bỏ qua chỉ dẫn'
        with self.assertRaisesRegex(st.StageError, 'EVIDENCE_NOT_IN_SOURCE'):
            st.validate('m0', unit, answer)

    def test_routes_remain_narrow(self):
        for route in ('m0-phan-ra', 'm2-ho', 'm3-goc', 'mo-ta-nut'):
            check_post_allowed('/admin/hermes/may/luot/HL_aaaaaaaaaaaa/' + route)
        check_allowed('/admin/hermes/may/luot/HL_aaaaaaaaaaaa/nguon-m3')
        with self.assertRaises(NmprpError):
            check_post_allowed('/admin/hermes/may/luot/HL_aaaaaaaaaaaa/approve')
        with self.assertRaises(NmprpError):
            check_post_allowed('/admin/hermes/may/luot/../m3-goc')

    def test_cancel_budget_and_checkpoint_pin(self):
        with tempfile.TemporaryDirectory() as d, patch.object(st, 'ready', return_value=['PHAN_RA']):
            job = luot(quy_trinh='m0', ds_pl2=[P], m0={'hop_dong': 'm0-1'})
            cfg = mc.CauHinh(enabled_stages=['m0'], stage_state=d)
            c = Client(dung_o_lan=1)
            self.assertEqual(mc.xu_ly_luot(c, job, cfg, runner_tra(M0)), 'DA_HUY')
            self.assertEqual(c.loai('stage'), [])
            job['tran_token'] = 1
            self.assertEqual(mc.xu_ly_luot(Client(), job, cfg, runner_tra(M0)), 'TAM_DUNG')
            job['tran_token'] = 300000
            self.assertEqual(mc.xu_ly_luot(Client(), job, cfg, runner_tra(M0)), 'XONG')
            job['ds_pl2'] = [dict(P, name='Changed')]
            self.assertEqual(mc.xu_ly_luot(Client(), job, cfg, runner_tra(M0)), 'LOI')

    def test_bad_batch_pauses_before_spending_on_more_units(self):
        second = dict(P, code='7.1')
        valid = copy.deepcopy(M0); valid['items'][0]['pl2_code'] = '7.1'
        replies = [{'items': []}, valid]
        def runner(argv):
            return (0, json.dumps(replies.pop(0))) if argv[-2] == '-z' else (0, '{"total_tokens":10}')
        with tempfile.TemporaryDirectory() as d, patch.object(st, 'ready', return_value=['PHAN_RA']):
            c = Client()
            job = luot(quy_trinh='m0', ds_pl2=[P, second], m0={'hop_dong': 'm0-1'})
            self.assertEqual(mc.xu_ly_luot(c, job, mc.CauHinh(enabled_stages=['m0'], stage_state=d), runner), 'TAM_DUNG')
            self.assertEqual(c.loai('stage'), [])
            self.assertEqual(c.cuoi()[0], 'TAM_DUNG')

    def test_pending_paid_call_and_invalid_job_id_fail_closed(self):
        with tempfile.TemporaryDirectory() as d, patch.object(st, 'ready', return_value=['PHAN_RA']):
            job = luot(quy_trinh='m0', ds_pl2=[P], m0={'hop_dong': 'm0-1'})
            cfg = mc.CauHinh(enabled_stages=['m0'], stage_state=d)
            path = st.Path(d) / job['luot_id']; path.mkdir()
            (path / (hashlib.sha256(P['code'].encode()).hexdigest() + '.pending')).write_text('ambiguous')
            r = runner_tra(M0)
            self.assertEqual(mc.xu_ly_luot(Client(), job, cfg, r), 'TAM_DUNG')
            self.assertEqual(r.goi, [])
            job['luot_id'] = '../../escape'
            self.assertEqual(mc.xu_ly_luot(Client(), job, cfg, r), 'LOI')
            self.assertEqual(r.goi, [])
