"""Pengujian kelas DFA. Kasus uji diambil dari PPT Bab 4 dan Bab 4-lanjutan."""
import pytest

from automata.dfa import DFA, DFATidakValid


def dfa_berakhiran_0():
    # Bab 4 slide 5-7: menerima string biner yang berakhir dengan 0
    return DFA(
        states={"q0", "q1"},
        alfabet={"0", "1"},
        transisi={
            ("q0", "0"): "q1", ("q0", "1"): "q0",
            ("q1", "0"): "q1", ("q1", "1"): "q0",
        },
        awal="q0",
        akhir={"q1"},
    )


@pytest.mark.parametrize("string, diterima", [
    ("1010", True), ("110", True), ("0", True),
    ("101", False), ("1", False), ("", False),
])
def test_dfa_berakhiran_0(string, diterima):
    assert dfa_berakhiran_0().jalankan(string).diterima is diterima


def test_jejak_mencatat_setiap_langkah():
    # Bab 4 slide 8: 1010 -> q0 -1-> q0 -0-> q1 -1-> q0 -0-> q1
    hasil = dfa_berakhiran_0().jalankan("1010")
    assert hasil.jalur == ["q0", "q0", "q1", "q0", "q1"]
    assert [l.simbol for l in hasil.langkah] == ["1", "0", "1", "0"]
    assert hasil.langkah[1].dari == "q0" and hasil.langkah[1].ke == "q1"
    assert hasil.state_akhir == "q1"


def test_string_kosong_diterima_jika_state_awal_juga_akhir():
    dfa = DFA({"q0"}, {"a"}, {("q0", "a"): "q0"}, "q0", {"q0"})
    assert dfa.jalankan("").diterima is True


def test_simbol_di_luar_alfabet_ditolak_dengan_pesan():
    hasil = dfa_berakhiran_0().jalankan("102")
    assert hasil.diterima is False
    assert "2" in hasil.pesan


def test_dfa_tidak_lengkap_ditolak_dan_menyarankan_dead_state():
    # Bab 4 slide 10: δ(q1, b) kosong -> belum memenuhi syarat DFA
    with pytest.raises(DFATidakValid) as info:
        DFA(
            states={"q0", "q1"},
            alfabet={"a", "b"},
            transisi={("q0", "a"): "q1", ("q0", "b"): "q0", ("q1", "a"): "q1"},
            awal="q0",
            akhir={"q1"},
        )
    assert "δ(q1, b)" in str(info.value)
    assert "dead state" in str(info.value)


def test_state_tujuan_harus_terdaftar():
    with pytest.raises(DFATidakValid):
        DFA({"q0"}, {"a"}, {("q0", "a"): "qX"}, "q0", set())


def test_state_awal_harus_terdaftar():
    with pytest.raises(DFATidakValid):
        DFA({"q0"}, {"a"}, {("q0", "a"): "q0"}, "q9", set())


def test_lengkapi_dengan_dead_state():
    # Perbaikan Bab 4 slide 10: tambah state jebakan d
    dfa = DFA.lengkapi_dengan_dead_state(
        states={"q0", "q1"},
        alfabet={"a", "b"},
        transisi={("q0", "a"): "q1", ("q0", "b"): "q0", ("q1", "a"): "q1"},
        awal="q0",
        akhir={"q1"},
        nama_dead="d",
    )
    assert "d" in dfa.states
    assert dfa.transisi[("q1", "b")] == "d"
    assert dfa.transisi[("d", "a")] == "d"
    assert dfa.jalankan("ab").diterima is False
    assert dfa.jalankan("aa").diterima is True


@pytest.mark.parametrize("string, diterima", [("110", True), ("101", False), ("0", True), ("1001", True)])
def test_dfa_habis_dibagi_3(string, diterima):
    # Bab 4 slide 15-16
    from automata.contoh import dfa_habis_dibagi_3
    assert dfa_habis_dibagi_3().jalankan(string).diterima is diterima


@pytest.mark.parametrize("string, diterima", [
    ("abbab", True), ("bba", True), ("baa", False), ("", False), ("babb", True),
])
def test_dfa_contoh_1_bab4_lanjutan(string, diterima):
    from automata.contoh import dfa_contoh_1
    assert dfa_contoh_1().jalankan(string).diterima is diterima


@pytest.mark.parametrize("string, diterima", [("111001", True), ("0101", False), ("001", True)])
def test_dfa_mengandung_001(string, diterima):
    from automata.contoh import dfa_mengandung_001
    assert dfa_mengandung_001().jalankan(string).diterima is diterima
