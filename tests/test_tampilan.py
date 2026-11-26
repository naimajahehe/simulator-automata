"""Pengujian modul tampilan: parsing input tabel dan pembuatan diagram DOT."""
import pytest

from automata import contoh
from automata.dfa import DFATidakValid
from automata.nfa import EPSILON
from tampilan.diagram import dot_dfa, dot_nfa
from tampilan.input_tabel import (
    pisah_daftar, tabel_dari_automata, dfa_dari_input, nfa_dari_input,
)


def test_pisah_daftar_menerima_koma_dan_spasi():
    assert pisah_daftar("q0, q1  q2,,") == ["q0", "q1", "q2"]
    assert pisah_daftar("  ") == []


def test_tabel_dari_dfa_lalu_dibaca_kembali_menghasilkan_dfa_sama():
    asli = contoh.dfa_mengandung_001()
    baris = tabel_dari_automata(asli)
    assert baris[0]["State"] == "q0"           # urutan alami
    assert baris[0]["0"] == "q1"
    dfa = dfa_dari_input("q0, q1, q2, q3", "0, 1", "q0", "q3", baris)
    assert dfa.transisi == asli.transisi
    assert dfa.jalankan("111001").diterima


def test_input_dfa_sel_kosong_memberi_pesan_dead_state():
    baris = [{"State": "q0", "a": "q1", "b": "q0"}, {"State": "q1", "a": "q1", "b": ""}]
    with pytest.raises(DFATidakValid, match="dead state"):
        dfa_dari_input("q0,q1", "a,b", "q0", "q1", baris)


def test_input_dfa_bisa_dilengkapi_otomatis_dengan_dead_state():
    baris = [{"State": "q0", "a": "q1", "b": "q0"}, {"State": "q1", "a": "q1", "b": ""}]
    dfa = dfa_dari_input("q0,q1", "a,b", "q0", "q1", baris, lengkapi=True)
    assert dfa.transisi[("q1", "b")] == "∅"
    assert dfa.jalankan("ab").diterima is False


def test_input_dfa_sel_berisi_dua_state_ditolak():
    baris = [{"State": "q0", "a": "q0,q1"}, {"State": "q1", "a": "q1"}]
    with pytest.raises(DFATidakValid, match="tepat satu"):
        dfa_dari_input("q0,q1", "a", "q0", "q1", baris)


def test_tabel_dari_nfa_memuat_kolom_epsilon_dan_himpunan():
    baris = tabel_dari_automata(contoh.enfa_bab5())
    q0 = baris[0]
    assert q0["State"] == "q0" and q0[EPSILON] == "q1" and q0["a"] == ""
    q1 = next(b for b in baris if b["State"] == "q1")
    assert q1["b"] == "q2"


def test_input_nfa_dengan_himpunan_dan_simbol_kosong():
    baris = [
        {"State": "q0", "0": "q0, q1", "1": "∅", EPSILON: ""},
        {"State": "q1", "0": "-", "1": "q1,q2", EPSILON: ""},
        {"State": "q2", "0": "q2", "1": "q2", EPSILON: ""},
    ]
    nfa = nfa_dari_input("q0,q1,q2", "0,1", "q0", "q2", baris)
    assert nfa.tujuan("q0", "0") == frozenset({"q0", "q1"})
    assert nfa.tujuan("q0", "1") == frozenset()
    assert nfa.jalankan("001").diterima


def test_input_nfa_epsilon():
    baris = tabel_dari_automata(contoh.enfa_bab5())
    nfa = nfa_dari_input("q0,q1,q2,q3,q4", "a,b", "q0", "q1,q4", baris)
    assert nfa.punya_epsilon()
    assert nfa.jalankan("ba").diterima


def test_dot_dfa_menandai_awal_akhir_dan_menggabung_label():
    dot = dot_dfa(contoh.dfa_contoh_1())
    assert "digraph" in dot
    assert '"q1" [shape=doublecircle' in dot
    assert '__start -> "q0"' in dot
    assert '"q1" -> "q1" [label="a, b"' in dot     # dua simbol, satu panah


def test_dot_dfa_menyorot_jalur():
    dfa = contoh.dfa_berakhiran_0()
    hasil = dfa.jalankan("10")
    dot = dot_dfa(dfa, hasil.langkah)
    assert '"q0" -> "q1" [label="0", color="#d1495b"' in dot


def test_dot_nfa_menampilkan_epsilon_dan_state_aktif():
    nfa = contoh.enfa_bab5()
    dot = dot_nfa(nfa, aktif={"q4"})
    assert 'label="ε"' in dot
    assert '"q4" [shape=doublecircle, style=filled' in dot


def test_dot_aman_untuk_nama_state_khusus():
    from automata.konversi import nfa_ke_dfa
    dot = dot_dfa(nfa_ke_dfa(contoh.nfa_bab67()).dfa)
    assert '"∅"' in dot
