"""Bounded M0 batches and durable checkpoints. M1 and other stage engines are unchanged."""
import hashlib
import json
import os
import subprocess
import threading

from support import nmprp_shadow as sh
from support import nmprp_stages as st

BATCH_SIZE = 5
TIMEOUT = 150
MAX_ATTEMPTS = 3
HEARTBEAT = 15


def save(path, data):
    temporary = path.with_suffix('.tmp')
    with temporary.open('w', encoding='utf-8') as f:
        os.chmod(temporary, 0o600)
        json.dump(data, f, ensure_ascii=False, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    temporary.replace(path)


def bounded(argv):
    """Timeout INSIDE Docker kills Hermes too. A host-side timeout is ambiguous."""
    if '-z' in argv:
        argv = argv[:5] + ['timeout', '--signal=TERM', '--kill-after=5s', str(TIMEOUT) + 's'] + argv[5:]
        limit = TIMEOUT + 20
    else:
        limit = 20
    p = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, text=True, timeout=limit)
    if p.returncode == 124:
        raise KnownFailure('MODEL_TIMEOUT_%ds' % TIMEOUT)
    if p.returncode and '-z' in argv:
        # Exit 137/transport failures do not prove that all remote processes stopped.
        from support.nmprp_runtime_diagnostics import classify
        raise st.StageError('HERMES_EXIT_%d:%s;PENDING_REQUIRES_RECONCILIATION' %
                            (p.returncode, classify(p.stderr, p.stdout)))
    return p.returncode, p.stdout


class KnownFailure(st.StageError):
    pass


def infer(run, unit, identity, model, reasoning):
    from support.nmprp_may_chay import DungLuot, MUC_SUY_LUAN_MAC_DINH
    body = st.prompt('m0', unit)
    if len(body.encode()) > sh.MAX_PROMPT_BYTES:
        raise st.StageError('M0_BATCH_TOO_LARGE')
    key = hashlib.sha256(identity.encode()).hexdigest()
    target = run.path / (key + '.json')
    fingerprint = st.digest({'stage': 'm0', 'input': unit, 'model': model, 'reasoning': reasoning,
                             'body': body, 'profile': run.cfg.stage_profile,
                             'skill': (st.ROOT / 'skills/nmprp-stage-m0/SKILL.md').read_text()})
    if target.exists():
        saved = json.loads(target.read_text())
        if saved['input_hash'] != fingerprint:
            raise st.StageError('PINNED_INPUT_CHANGED')
        return saved['result']
    pending = target.with_suffix('.pending')
    if pending.exists():
        raise st.StageError('AMBIGUOUS_MODEL_CALL_REQUIRES_RECONCILIATION')
    # Revalidate paid, quarantined output after a validator repair. Preserve
    # the original artifact and all fingerprint/pending safeguards.
    for previous in sorted(run.path.glob(key + '.invalid-*'), reverse=True):
        saved = json.loads(previous.read_text())
        if saved.get('input_hash') != fingerprint:
            continue
        try:
            items = st.validate('m0', unit, saved['result'])
            if any(x['trang_thai'] == 'FAILED' for x in items):
                continue
        except st.StageError:
            continue
        save(target, saved)
        return saved['result']
    attempts_path = target.with_suffix('.attempts')
    attempts = int(attempts_path.read_text()) if attempts_path.exists() else 0
    if attempts >= MAX_ATTEMPTS:
        raise st.StageError('M0_RETRY_LIMIT_REQUIRES_REVIEW')
    if not run.client.ai_cong_tac_bat(chiu_loi_mang=True):
        raise DungLuot('TAM_DUNG', 'Công tắc AI đang TẮT')
    estimate = sh.uoc_token(body)
    if (run.job.get('han_goi') and run.calls >= run.job['han_goi']) or run.tokens + estimate > run.job['tran_token']:
        raise DungLuot('TAM_DUNG', 'Chạm ngân sách M0; nâng hạn rồi Chạy tiếp')
    run.calls += 1
    # Reserve input estimate durably; missing usage remains an estimate, never zero.
    save(run.path / 'm0-accounting.context.json', {'calls': run.calls, 'tokens': run.tokens + estimate})
    run.report('SUY_LUAN', 'DANG', run.batch_note + ' · token gồm ước tính khi thiếu usage')
    save(attempts_path, attempts + 1)
    save(pending, {'input_hash': fingerprint, 'call': run.calls})
    stopped = threading.Event()
    errors = []
    def heartbeat():
        while not stopped.wait(HEARTBEAT):
            try:
                run.report('SUY_LUAN', 'DANG', run.batch_note + ' · đang chờ Hermes')
            except Exception as exc:
                errors.append(exc)
                return
    thread = threading.Thread(target=heartbeat, daemon=True)
    thread.start()
    try:
        def stage_call(argv):
            # The shared M1 helper has a fixed M1 usage path. Isolate stage usage
            # without modifying M1's argv/engine or copying its credentials.
            old = sh.USAGE_DIR + '/'
            new = '/opt/data/profiles/' + run.cfg.stage_profile + '/workspace/'
            argv = [new + arg[len(old):] if arg.startswith(old) else arg for arg in argv]
            return (run.runner or bounded)(argv)
        out, usage = sh.goi_hermes(body, 'm0-%s-%d.json' % (run.job['luot_id'], run.calls),
                                   run.cfg.container, run.cfg.stage_profile, st.STAGES['m0'][1],
                                   stage_call, model, reasoning or MUC_SUY_LUAN_MAC_DINH)
    except KnownFailure:
        run.tokens += estimate
        pending.unlink()
        raise
    except (st.StageError, sh.ShadowStop, subprocess.SubprocessError):
        run.tokens += estimate
        raise
    finally:
        stopped.set()
        thread.join()
    run.tokens += int(usage.get('total_tokens') or estimate)
    save(run.path / 'm0-accounting.context.json', {'calls': run.calls, 'tokens': run.tokens})
    result = sh.tach_json(out)
    # Persist raw parsed result BEFORE any network/report/validation: never pay twice
    # because delivery failed. Invalid responses remain visible and require review.
    save(target, {'input_hash': fingerprint, 'result': result, 'worker_version': st.VERSION,
                  'stage': 'm0', 'job_id': run.job['luot_id'], 'scope_hash': key,
                  'model': model or 'profile-default', 'usage': usage, 'review': 'AI_PROVISIONAL'})
    pending.unlink()
    if errors:
        raise errors[0]
    run.report('SUY_LUAN', 'XONG', run.batch_note)
    return result


def execute(run):
    from support.nmprp_may_chay import DungLuot, ghi_nhat_ky
    job = run.job
    st._codes(job['ds_pl2'])
    scope = st.digest({'pl2': job['ds_pl2'], 'contract': job['m0']})
    plan_path = run.path / 'm0-plan.context.json'
    if plan_path.exists():
        plan = json.loads(plan_path.read_text())
        if plan['scope'] != scope:
            raise st.StageError('PINNED_INPUT_CHANGED')
    else:
        done = set(job.get('pl2_da_xong') or [])
        size = max(1, min(10, int(job.get('me') or BATCH_SIZE)))
        units, batch = [], []
        for p in job['ds_pl2']:
            key = hashlib.sha256(p['code'].encode()).hexdigest()
            if p['code'] in done:
                continue
            # Preserve old per-PL2 checkpoint identities and ambiguous calls.
            if any((run.path / (key + ext)).exists() for ext in ('.json', '.pending')):
                if batch:
                    units.append(batch); batch = []
                units.append([p])
            else:
                batch.append(p)
                if len(batch) == size:
                    units.append(batch); batch = []
        if batch:
            units.append(batch)
        plan = {'scope': scope, 'units': units}
        save(plan_path, plan)
    accounting = run.path / 'm0-accounting.context.json'
    if accounting.exists():
        counters = json.loads(accounting.read_text())
        run.calls = max(run.calls, counters['calls'])
        run.tokens = max(run.tokens, counters['tokens'])
    done = set(job.get('pl2_da_xong') or [])
    run.progress = {'pl2_xong': len(done), 'so_lo': len(plan['units']), 'lo_xong': 0}
    run.report('DOC', 'XONG', 'M0: %d/%d PL2; %d lô' % (len(done), len(job['ds_pl2']), len(plan['units'])))
    for index, rows in enumerate(plan['units'], 1):
        if all(p['code'] in done for p in rows):
            run.progress['lo_xong'] += 1
            continue
        codes = [p['code'] for p in rows]
        run.batch_note = 'M0 lô %d/%d · PL2 %s' % (index, len(plan['units']), ', '.join(codes))
        ghi_nhat_ky('%s %s bắt đầu' % (job['luot_id'], run.batch_note))
        try:
            unit = {'pl2': rows, 'contract': job['m0']}
            identity = codes[0] if len(rows) == 1 else 'm0-batch:' + st.digest(codes)
            result = run.infer('m0', unit, identity, model=job.get('mo_hinh', ''), reasoning=job.get('suy_luan', ''))
            try:
                items = st.validate('m0', unit, result)
                if any(x['trang_thai'] == 'FAILED' for x in items):
                    raise st.StageError('M0_MODEL_REPORTED_FAILED')
            except st.StageError:
                target = run.path / (hashlib.sha256(identity.encode()).hexdigest() + '.json')
                target.replace(target.with_suffix('.invalid-%d' % run.calls))
                raise
            run.report('KIEM_DINH', 'XONG', run.batch_note)
            remaining = [x for x in items if x['pl2_code'] not in done]
            run.client.may_stage(job['luot_id'], 'm0-phan-ra', remaining)
            done.update(x['pl2_code'] for x in remaining)
            run.progress.update(pl2_xong=len(done), lo_xong=index)
            run.report('GUI', 'XONG', run.batch_note + ' · %d/%d PL2' % (len(done), len(job['ds_pl2'])))
            ghi_nhat_ky('%s M0 %d/%d PL2; calls=%d tokens=%d' %
                       (job['luot_id'], len(done), len(job['ds_pl2']), run.calls, run.tokens))
        except (st.StageError, sh.ShadowStop, subprocess.TimeoutExpired) as exc:
            reason = str(exc) if isinstance(exc, st.StageError) else type(exc).__name__
            note = run.batch_note + ' · ' + reason
            ghi_nhat_ky('%s %s' % (job['luot_id'], note))
            run.report('KIEM_DINH', 'LOI', note)
            raise DungLuot('TAM_DUNG', note + ' · Chạy tiếp dùng checkpoint; không tạo lượt mới')
    run.client.may_ket_thuc(job['luot_id'], 'XONG', 'M0: %d/%d PL2' % (len(done), len(job['ds_pl2'])))
    return 'XONG'
