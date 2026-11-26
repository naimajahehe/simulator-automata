"""Pengujian aplikasi Streamlit tanpa browser (streamlit.testing.v1.AppTest)."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from automata.contoh import PRESET_DFA, PRESET_NFA

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def jalankan_app():
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception, at.exception
    return at


def semua_teks(at):
    bagian = [e.value for e in at.markdown] + [e.value for e in at.success] + [e.value for e in at.error] \
        + [e.value for e in at.info] + [e.value for e in at.warning] + [e.value for e in at.caption]
    return "\n".join(str(b) for b in bagian)


def test_app_terbuka_dengan_tiga_tab():
    at = jalankan_app()
    assert [t.label for t in at.tabs] == ["DFA", "NFA", "Konversi NFA → DFA"]


def test_tab_dfa_preset_awal_menerima_string_contoh():
    at = jalankan_app()
    assert any("DITERIMA" in s.value for s in at.success)


@pytest.mark.parametrize("nama", list(PRESET_DFA))
def test_setiap_preset_dfa_berjalan(nama):
    at = jalankan_app()
    at.selectbox(key="dfa_preset").set_value(nama).run()
    assert not at.exception


@pytest.mark.parametrize("nama", list(PRESET_NFA))
def test_setiap_preset_nfa_berjalan_di_tab_nfa_dan_konversi(nama):
    at = jalankan_app()
    at.selectbox(key="nfa_preset").set_value(nama).run()
    at.selectbox(key="konv_preset").set_value(nama).run()
    assert not at.exception


def test_string_ditolak_ditampilkan_sebagai_error():
    at = jalankan_app()
    at.selectbox(key="dfa_preset").set_value("Berakhiran 0 (Bab 4)").run()
    at.text_input(key="dfa_string").set_value("101").run()
    assert any("DITOLAK" in e.value for e in at.error)


def test_konversi_menampilkan_tabel_dan_hasil_sama():
    at = jalankan_app()
    at.selectbox(key="konv_preset").set_value("NFA q0–q2 (Bab 6-7)").run()
    at.text_input(key="konv_string").set_value("011").run()
    teks = semua_teks(at)
    assert "{q1,q2}" in teks or any("{q1,q2}" in str(df.value) for df in at.dataframe)
    assert "hasilnya sama" in teks


def test_preset_dapat_dibuka_lewat_parameter_url():
    at = AppTest.from_file(APP, default_timeout=30)
    at.query_params["nfa_preset"] = "NFA dengan ε-move (Bab 5)"
    at.run()
    assert not at.exception
    assert at.text_input(key="nfa_states").value == "q0, q1, q2, q3, q4"
    assert at.text_input(key="nfa_string").value == "ba"


def test_form_kosong_menampilkan_petunjuk_bukan_error():
    at = jalankan_app()
    at.selectbox(key="nfa_preset").set_value("Isi sendiri").run()
    assert not any("NFA belum valid" in e.value for e in at.error)
    assert any("Isi Q" in i.value for i in at.info)


def test_pesan_error_ditampilkan_per_baris():
    at = jalankan_app()
    at.selectbox(key="dfa_preset").set_value("Isi sendiri").run()
    at.text_input(key="dfa_states").set_value("q0").run()
    teks = next(e.value for e in at.error if "DFA belum valid" in e.value)
    assert "\n- " in teks


def test_preset_dfa_belum_lengkap_bisa_dilengkapi_dead_state():
    at = jalankan_app()
    at.selectbox(key="dfa_preset").set_value("DFA belum lengkap (Bab 4 slide 10)").run()
    assert any("δ(q1, b)" in e.value for e in at.error)
    at.checkbox(key="dfa_lengkapi").check().run()
    assert not at.exception
    assert not any("belum valid" in e.value for e in at.error)
    # setelah dilengkapi, simulasi berjalan: aab -> q1 -> q1 -> ∅ (dead state) = ditolak
    assert any("DITOLAK" in e.value and "∅" in e.value for e in at.error)


def test_dfa_tidak_lengkap_memunculkan_pesan_dead_state():
    at = jalankan_app()
    at.selectbox(key="dfa_preset").set_value("Isi sendiri").run()
    at.text_input(key="dfa_states").set_value("q0, q1").run()
    at.text_input(key="dfa_alfabet").set_value("a, b").run()
    at.text_input(key="dfa_awal").set_value("q0").run()
    assert any("dead state" in e.value for e in at.error)
