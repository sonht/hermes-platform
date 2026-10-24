"""M1 v2 adapter: unchanged GĐ1 prompt/validator, then a separate evidence review.

Never used by M1 v1. NMPRP computes evidence levels and applies QG-16.
"""
from support import nmprp_shadow as sh
import hashlib
from support.nmprp_stages import StageError


def validate(unit, result):
    if not isinstance(result, dict) or set(result) != {'items'} or len(result['items']) != 1:
        raise StageError('GD2_JSON')
    row = result['items'][0]
    if set(row) != {'pl2_code', 'ho_so', 'doi_chieu'} or row['pl2_code'] != unit['pl2']['code']:
        raise StageError('GD2_SCOPE')
    hs, caps, source = row['ho_so'], row['doi_chieu'], unit['source']
    if not isinstance(hs, dict) or hs.get('lo_id') != source['lo_id'] or hs.get('mo_ta_dau') != source['mo_ta_dau']:
        raise StageError('GD2_SOURCE_CHANGED')
    if not isinstance(caps, list) or not caps:
        raise StageError('GD2_EVIDENCE_REQUIRED')
    seen = set()
    for cap in caps:
        key = cap.get('khoa_nhanh')
        if key not in source['nut'] or key in seen:
            raise StageError('GD2_NODE')
        seen.add(key)
        node = source['nut'][key]
        for field, origin in (('bao_gom_trich', 'bao_gom'), ('loai_tru_trich', 'loai_tru')):
            if not isinstance(cap.get(field), list) or any(not isinstance(x, str) or not x or not any(x in s for s in node[origin]) for x in cap[field]):
                raise StageError('GD2_QUOTE')
    if not set(unit['candidate_keys']) <= seen:
        raise StageError('GD2_CANDIDATE_NOT_REVIEWED')
    return row


def execute(run):
    from support.nmprp_may_chay import _kiem_cho_phep
    job, cfg, c = run.job, run.cfg, run.client
    _kiem_cho_phep(dict(job, mo_hinh=job.get('mo_hinh_gd2', ''), suy_luan=job.get('suy_luan_gd2', '')), cfg)
    nodes = sh.thu_nut_tan(c.khung())
    if not nodes:
        raise StageError('GD1_NO_LEAF_NODES')
    for p in job['ds_pl2']:
        delivered = run.path / (hashlib.sha256(('delivered/' + p['code']).encode()).hexdigest() + '.delivered')
        gd2_saved = run.path / (hashlib.sha256(('gd2/' + p['code']).encode()).hexdigest() + '.json')
        if p['code'] in set(job.get('pl2_da_xong') or []) and (delivered.exists() or not gd2_saved.exists()):
            continue
        # One PL2 keeps the existing GĐ2 reader's 10-code limit and the 8-comparison output limit.
        gd1 = run.infer('v2', {'pl2': p, 'nodes': nodes}, 'gd1/' + p['code'],
                        body=sh.dung_prompt([p], nodes), profile=cfg.profile, skill=cfg.ky_nang,
                        model=job.get('mo_hinh', ''), reasoning=job.get('suy_luan', ''))
        checked = sh.kiem_ket_qua(gd1, [p], nodes, 'nmprp-gd2@1')[p['code']]
        if checked['muc'] == 'KHONG_DAP_UNG':
            raise StageError('GD1_INVALID_OUTPUT')
        candidates = checked['chap_nhan']
        keys = list(dict.fromkeys(x['branch_key'] for x in candidates))
        if not keys:
            # No candidate evidence to review: fail closed, never label an unreviewed abstention as v2 complete.
            raise StageError('GD2_NO_CANDIDATE_REQUIRES_REVIEW')
        source = c.may_mo_ta(job['luot_id'], keys, [p['code']])
        if not source.get('ok') or source.get('thieu'):
            raise StageError('GD2_SOURCE_UNAVAILABLE')
        current = source.get('nut_hien_tai', {}).get(p['code'])
        if current and current not in keys:
            keys.append(current)
            source = c.may_mo_ta(job['luot_id'], keys, [p['code']])
            if not source.get('ok') or source.get('thieu'):
                raise StageError('GD2_CURRENT_NODE_UNAVAILABLE')
        unit = {'pl2': p, 'candidate_keys': [x['branch_key'] for x in candidates], 'source': source,
                'gd1': gd1, 'contract': 'doi-chieu@2'}
        raw = run.infer('v2', unit, 'gd2/' + p['code'], model=job.get('mo_hinh_gd2', ''), reasoning=job.get('suy_luan_gd2', ''))
        row = validate(unit, raw)
        # Validate/persist evidence FIRST. Server failure prevents suggestion writes.
        result = {'pl2_code': p['code'], 'muc': checked['muc'], 'ly_do': checked['ly_do'],
                  'so_nhan': len(candidates), 'so_bo': len(checked['bo']), 'lo': 0,
                  'ho_so': row['ho_so'], 'doi_chieu': row['doi_chieu']}
        run.report('KIEM_DINH', 'XONG', 'GD2 doi-chieu@2; nhan do may chu tinh')
        c.may_ket_qua(job['luot_id'], [result])
        excluded = {x['khoa_nhanh'] for x in row['doi_chieu'] if x.get('ket_luan_loai_tru') == 'BI_LOAI'}
        suggestions = [x for x in candidates if x['branch_key'] not in excluded]
        for x in suggestions:
            # No uncalibrated HIGH promotion from this new adapter.
            x['bang_chung']['muc_de_xuat'] = 'REVIEW_RECOMMENDED'
        if suggestions:
            c.may_goi_y(job['luot_id'], suggestions)
        delivered.touch(mode=0o600)
        run.report('GUI', 'XONG', 'GD2')
    c.may_ket_thuc(job['luot_id'], 'XONG', 'v2: ho so va doi chieu da gui; cho chuyen gia')
    return 'XONG'
