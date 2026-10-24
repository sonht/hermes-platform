"""Cross-repository integration: real queue, HTTP auth/allowlists, validators and persistence.

Model responses are controlled fixtures, NOT evidence of live LLM/clinical acceptance.
Run with the NMPRP venv and PYTHONPATH=<nmprp>/backend:<hermes-platform>.
"""
import io
import json
import tempfile
import urllib.error

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.api import auth_admin as A, hermes_admin as ha
from app.registry import hermes_luot as hl, hermes_m23_luot as m23, hermes_m2_de_xuat as dx
from app.registry import hermes_modifier_doc as md
from app.tests.test_hermes_m23_luot import e, _tao, _MAY
from app.tests.test_hermes_m0_http import san, _TOK
from support import nmprp_may_chay as mc, nmprp_stages as st
from support.nmprp_client import NmprpClient
from tests.test_nmprp_shadow import runner_tra


class Opener:
    def __init__(self):
        self.http = TestClient(app)

    def open(self, req, timeout=None):
        r = self.http.request(req.method, req.full_url, headers=dict(req.header_items()), content=req.data)
        if r.status_code >= 400:
            raise urllib.error.HTTPError(req.full_url, r.status_code, '', {}, io.BytesIO(r.content))
        return io.BytesIO(r.content)


def client(token='tok-may'):
    c = NmprpClient('http://testserver', 'unused', 'unused', opener=Opener())
    c._token = token
    c.ai_cong_tac_bat = lambda **_: True
    return c


def test_m0_http_claim_validate_persist_idempotent(san, monkeypatch, tmp_path):
    c = client('tok-admin')
    # Admin creates a real M0 job; runner authenticates separately.
    r = c._opener.http.post('/admin/hermes/m0/luot', headers={'Authorization': 'Bearer tok-admin'},
                            json={'chuong': '06', 'pl2_codes': ['1.050']})
    assert r.status_code == 200, r.text
    c._token = 'tok-may'
    job = c.may_nhan()['luot']
    monkeypatch.setattr(st, 'ready', lambda _: ['PHAN_RA'])
    answer = {'items': [{'pl2_code': '1.050', 'trang_thai': 'READY', 'noi_dung': {
        'hanh_dong_chinh': {'ma': 'HD_CHOC_HUT', 'van_ban': 'Chọc hút', 'trich_nguon': 'Chọc hút'},
        'dich': {'ma': 'DICH_NANG', 'van_ban': 'u nang giáp', 'trich_nguon': 'u nang giáp'}}}]}
    cfg = mc.CauHinh(enabled_stages=['m0'], stage_state=str(tmp_path))
    assert mc.xu_ly_luot(c, job, cfg, runner_tra(answer)) == 'XONG'
    with san.connect() as q:
        assert q.execute(text('SELECT pl2_code FROM hermes_m0_phan_ra')).scalars().all() == ['1.050']
        assert q.execute(text('SELECT COUNT(*) FROM hermes_luot_pl2')).scalar() == 0
    assert hl.chi_tiet(san, job['luot_id'])['trang_thai'] == 'XONG'


def setup_http(e, monkeypatch):
    monkeypatch.setenv('NMPRP_HERMES_MAY', _MAY)
    account = {'username': _MAY, 'user_id': _MAY, 'role': 'expert', 'tasks': ['studio_cpt'], 'chapters': []}
    monkeypatch.setattr(A, 'user_by_token', lambda eng, token: account if token == 'tok-may' else _TOK.get(token))
    monkeypatch.setattr(ha, 'engine', e)
    monkeypatch.setattr(ha, 'log_action', lambda *a, **k: None)
    c = client()
    return c


def test_m2_then_m3_http_real_artifacts_and_scope(e, monkeypatch, tmp_path):
    c = setup_http(e, monkeypatch)
    monkeypatch.setattr(st, 'ready', lambda _: ['DE_XUAT_HO', 'DE_XUAT_GOC'])
    # Approved knowledge retrieval is tested separately in NMPRP; empty bundle here is explicit.
    c.may_knowledge = lambda _: {'nhan': 'HPKB_ACTIVE', 'phien_ban': '0', 'items': []}
    job_id = _tao(e)['luot_id']
    job = c.may_nhan()['luot']
    answers = []
    for node in job['m23']['nut']:
        codes = [p['code'] for p in node['pl2']]
        answers.append({'items': [{'khoa_nhanh': node['khoa_nhanh'], 'pl2_codes': codes,
                                  'ten': 'Họ kiểm hợp đồng', 'dinh_nghia': 'Căn cứ chỉ dùng cho fixture',
                                  'ranh_gioi_noi_bo': 'Trong một nút', 'ly_do': 'Fixture kiểm API',
                                  'ly_do_thanh_vien': {p: 'Fixture' for p in codes}}]})
    calls = []
    def runner(argv):
        calls.append(argv)
        return (0, json.dumps(answers.pop(0), ensure_ascii=False)) if argv[-2] == '-z' else (0, '{"total_tokens":10}')
    cfg = mc.CauHinh(mo_hinh=['m'], suy_luan=['cao'], enabled_stages=['m2', 'm3'], stage_state=str(tmp_path))
    # The production model options are validated; use a runtime-supported reasoning choice in this fixture.
    cfg.suy_luan = ('cao',)
    assert mc.xu_ly_luot(c, job, cfg, runner) == 'XONG'
    with e.connect() as q:
        families = q.execute(text('SELECT de_xuat_id FROM hermes_m2_de_xuat_ho WHERE luot_id=:l'), {'l': job_id}).scalars().all()
        assert len(families) == 2
        before = q.execute(text('SELECT pl2_code, branch_key FROM hermes_m2_snapshot_dong ORDER BY pl2_code')).all()
    for did in families:
        dx.ghi_quyet_dinh(e, did, 'DONG_Y', 'expert', ly_do='Fixture review')
    from app.db import schema as sch
    sch.ensure_cpn_ai_tables(e)
    with e.begin() as q:
        q.execute(text("INSERT INTO modifier_definition(modifier_id,name_vi,evidence_status,version,created_at) "
                       "VALUES ('MOD_APPROACH','Đường tiếp cận','ACTIVE','1','t')"))
    lid3 = _tao(e, 'm3', luot_m2_id=job_id)['luot_id']
    job3 = c.may_nhan()['luot']
    answers[:] = [{'items': [{'de_xuat_id': f['de_xuat_id'], 'action': 'Cắt', 'target': 'Ruột thừa',
                              'ly_do': 'Fixture', 'bien_the': [{'pl2_code': p['code'], 'modifier_ids': [],
                              'tai_dung_dac_diem': {'ket_qua': 'UNCERTAIN', 'ghi_chu': 'Chưa có M0'}} for p in f['thanh_vien']]}]}
                 for f in job3['m23']['ho']]
    for response in answers:
        for variant in response['items'][0]['bien_the']:
            if variant['pl2_code'] == 'BS_07':
                variant['modifier_ids'] = ['MOD_APPROACH']
                variant['gia_tri_modifier'] = [{'modifier_id': 'MOD_APPROACH', 'loai': 'LM_DUONG_TIEP_CAN',
                    'gia_tri': 'nội soi', 'don_vi': '', 'trich_nguon': 'nội soi', 'anh_huong': 'UNKNOWN', 'vai_tro': 'UNCERTAIN'}]
    assert mc.xu_ly_luot(c, job3, cfg, runner) == 'XONG'
    with e.connect() as q:
        assert q.execute(text('SELECT COUNT(*) FROM hermes_m3_de_xuat_goc WHERE luot_id=:l'), {'l': lid3}).scalar() == 2
        assert q.execute(text('SELECT trich_nguon FROM hermes_m3_gia_tri_mod')).scalar() == 'nội soi'
        assert q.execute(text('SELECT pl2_code, branch_key FROM hermes_m2_snapshot_dong ORDER BY pl2_code')).all() == before
        assert q.execute(text('SELECT COUNT(*) FROM hermes_luot_pl2')).scalar() == 0


def test_modifier_reader_rejects_wrong_identity_and_unapproved(e, monkeypatch):
    c = setup_http(e, monkeypatch)
    lid = _tao(e)['luot_id']
    c.may_nhan()
    # M2 is not entitled to the M3 dictionary even for the same machine.
    with pytest.raises(NmprpClientError()):
        c.may_modifier(lid)


def NmprpClientError():
    from support.nmprp_client import NmprpError
    return NmprpError


def test_gd2_http_uses_existing_gd1_and_persists_real_evidence(e, monkeypatch, tmp_path):
    from app.tests.test_hermes_doi_chieu import _dung_lo, _nap_mo_ta, _N1
    from tests.test_nmprp_shadow import tot
    from app.registry import cong_tac as ct
    c = setup_http(e, monkeypatch)
    monkeypatch.setattr(hl, '_pl2_theo_chuong', lambda _: {'6': [('6.1', 'Cắt tuyến giáp')]})
    _dung_lo(e)
    _nap_mo_ta(e, [{'khoa': _N1, 'node_id': '007', 'bao_gom': ['Cắt tuyến giáp'], 'loai_tru': []}])
    hl.chao_may(e, _MAY, 'stage@1', [], ['low'], ['THAM_DINH_GD2'])
    lid = hl.tao_luot(e, '6', 1, 1, 300000, 0, '', '', 'admin', quy_trinh='v2')['luot_id']
    job = c.may_nhan()['luot']
    c.khung = lambda: {'khung': [{'khoa': 'k', 'vi': 'Cắt tuyến giáp', 'khoa_nhanh': _N1, 'la_nut_tan': True}]}
    monkeypatch.setattr(st, 'ready', lambda _: ['THAM_DINH_GD2'])
    gd1 = {'ket_qua': [tot('6.1', _N1, ['Cắt tuyến giáp'])]}
    stage2 = []
    calls = []
    def runner(argv):
        calls.append(argv)
        if argv[-2] != '-z':
            return 0, '{"total_tokens":10}'
        if len([x for x in calls if x[-2] == '-z']) == 1:
            return 0, json.dumps(gd1)
        unit = json.loads(argv[-1].split('PINNED_INPUT_JSON:\n')[1])
        source = unit['source']
        result = {'items': [{'pl2_code': '6.1', 'ho_so': {'lo_id': source['lo_id'], 'mo_ta_dau': source['mo_ta_dau'],
                   'hanh_dong': ['Cắt'], 'doi_tuong': ['tuyến giáp'], 'cau_hoi': []}, 'doi_chieu': [{
                   'khoa_nhanh': _N1, 'vai_tro': 'UNG_VIEN_GD1', 'bao_gom_trich': ['Cắt tuyến giáp'],
                   'loai_tru_trich': [], 'khop_hanh_dong': 'KHOP', 'khop_doi_tuong': 'KHOP',
                   'khop_phuong_phap': 'CHUA_RO', 'khop_cong_nghe_muc_dich': 'CHUA_RO',
                   'muc_nhan_vao': 'NHAN_VAO_CO_DIEU_KIEN', 'ket_luan_loai_tru': 'NGUON_TRONG',
                   'giai_thich': 'Tên kỹ thuật và đoạn Bao gồm cùng nêu cắt tuyến giáp, chưa xác định phương pháp.',
                   'nut_canh_tranh': [], 'phu_thanh_phan': []}]}]}
        stage2.append(result)
        return 0, json.dumps(result)
    cfg = mc.CauHinh(enabled_stages=['v2'], stage_state=str(tmp_path))
    from support.nmprp_client import NmprpError
    publish = c.may_goi_y
    c.may_goi_y = lambda *a: (_ for _ in ()).throw(NmprpError('simulated lost transport'))
    with pytest.raises(NmprpError):
        mc.xu_ly_luot(c, job, cfg, runner)
    assert hl.chi_tiet(e, lid)['trang_thai'] == 'DANG_CHAY'
    c.may_goi_y = publish
    resumed = c.may_nhan()['luot']
    assert resumed['pl2_da_xong'] == ['6.1']
    assert mc.xu_ly_luot(c, resumed, cfg, runner) == 'XONG'
    assert len([x for x in calls if x[-2] == '-z']) == 2
    with e.connect() as q:
        row = q.execute(text('SELECT ho_so FROM hermes_luot_pl2 WHERE luot_id=:l'), {'l': lid}).scalar()
        assert json.loads(row)['hanh_dong'] == ['Cắt']
        assert q.execute(text('SELECT COUNT(*) FROM hermes_doi_chieu WHERE luot_id=:l'), {'l': lid}).scalar() == 1
    assert len(stage2) == 1
    assert 'nmprp-retrieval-assist' in calls[0]
    assert 'nmprp-mapping' in calls[0]


def test_m3_explicit_family_replay_keeps_older_roots(e, monkeypatch, tmp_path):
    from app.registry import hermes_m3_goc as m3
    c = setup_http(e, monkeypatch)
    lid = _tao(e)['luot_id']
    hl.nhan_viec(e, _MAY)
    m23.ghi_m2(e, lid, _MAY, [{'khoa_nhanh': 'A > B', 'pl2_codes': ['1.10']},
                              {'khoa_nhanh': 'A > C', 'pl2_codes': ['1.050']}])
    hl.ket_thuc(e, lid, _MAY, 'XONG')
    with e.connect() as q:
        ids = q.execute(text('SELECT de_xuat_id FROM hermes_m2_de_xuat_ho WHERE luot_id=:l ORDER BY de_xuat_id'), {'l': lid}).scalars().all()
    for did in ids:
        dx.ghi_quyet_dinh(e, did, 'DONG_Y', 'expert', ly_do='Fixture')
        members = dx.doc_de_xuat(e, did)['thanh_vien']
        # Source ids are text. Use actual membership, without modifying the family.
        with e.connect() as q:
            codes = q.execute(text('SELECT pl2_code FROM hermes_m2_thanh_vien WHERE de_xuat_id=:d'), {'d': did}).scalars().all()
        m3.tao_de_xuat_goc(e, did, action='Cắt', target='Đích', bien_the=[{'pl2_code': p} for p in codes], nguoi='expert')
    with e.connect() as q:
        before = q.execute(text('SELECT goc_id FROM hermes_m3_de_xuat_goc ORDER BY goc_id')).scalars().all()
    job = m23.tao_luot(e, 'm3', 'S1', '1', 20, 200000, 0, '', '', 'admin',
                       luot_m2_id=lid, de_xuat_ids=[ids[0]], chay_lai=True)
    claimed = c.may_nhan()['luot']
    assert [f['de_xuat_id'] for f in claimed['m23']['ho']] == [ids[0]]
    c.may_knowledge = lambda _: {'nhan': 'HPKB_ACTIVE', 'phien_ban': '0', 'items': []}
    monkeypatch.setattr(st, 'ready', lambda _: ['DE_XUAT_GOC'])
    family = claimed['m23']['ho'][0]
    result = {'items': [{'de_xuat_id': ids[0], 'action': 'Cắt', 'target': 'Đích', 'ly_do': 'Fixture replay',
                        'bien_the': [{'pl2_code': p['code'], 'modifier_ids': [],
                                      'tai_dung_dac_diem': {'ket_qua': 'UNCERTAIN'}} for p in family['thanh_vien']]}]}
    cfg = mc.CauHinh(enabled_stages=['m3'], stage_state=str(tmp_path))
    assert mc.xu_ly_luot(c, claimed, cfg, runner_tra(result)) == 'XONG'
    with e.connect() as q:
        after = q.execute(text('SELECT goc_id FROM hermes_m3_de_xuat_goc ORDER BY goc_id')).scalars().all()
        assert set(before) < set(after) and len(after) == len(before) + 1
    with e.connect() as q:
        assert set(before) <= set(q.execute(text('SELECT goc_id FROM hermes_m3_de_xuat_goc ORDER BY goc_id')).scalars().all())
