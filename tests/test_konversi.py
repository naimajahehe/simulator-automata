"""Pengujian konversi NFA → DFA (subset construction). Kasus uji dari PPT Bab 5 dan Bab 6-7."""
from itertools import product

import pytest

from automata import contoh
from automata.dfa import DFA
from automata.konversi import nfa_ke_dfa


def tabel(hasil):
    """Ubah hasil konversi menjadi {nama: (himpunan, {simbol: nama_tujuan}, final)} agar mudah dibandingkan."""
    return {b.nama: (set(b.himpunan), dict(b.tujuan), b.final) for b in hasil.baris}


def test_konversi_bab67_sesuai_tabel_ppt():
    # PPT Bab 6-7 slide 10-12 (nama E pada PPT = D di sini; D=∅ pada PPT = ∅ di sini)
    hasil = nfa_ke_dfa(contoh.nfa_bab67())
    assert tabel(hasil) == {
        "A": ({"q0"}, {"0": "B", "1": "∅"}, False),
        "B": ({"q0", "q1"}, {"0": "B", "1": "C"}, False),
        "C": ({"q1", "q2"}, {"0": "D", "1": "C"}, True),
        "D": ({"q2"}, {"0": "D", "1": "D"}, True),
        "∅": (set(), {"0": "∅", "1": "∅"}, False),
    }
    assert isinstance(hasil.dfa, DFA)
    assert hasil.dfa.awal == "A"
    assert hasil.dfa.akhir == {"C", "D"}


def test_konversi_latihan_p_sesuai_pembahasan_ppt():
    # PPT Bab 6-7 slide 16
    hasil = nfa_ke_dfa(contoh.nfa_latihan_p())
    assert tabel(hasil) == {
        "A": ({"p0"}, {"a": "B", "b": "∅"}, False),
        "B": ({"p0", "p1"}, {"a": "B", "b": "C"}, False),
        "C": ({"p2"}, {"a": "C", "b": "C"}, True),
        "∅": (set(), {"a": "∅", "b": "∅"}, False),
    }


def test_konversi_enfa_memakai_epsilon_closure():
    # State awal DFA = ε-closure(q0) = {q0,q1}; sudah final karena memuat q1
    hasil = nfa_ke_dfa(contoh.enfa_bab5())
    assert tabel(hasil) == {
        "A": ({"q0", "q1"}, {"a": "∅", "b": "B"}, True),
        "B": ({"q2", "q3"}, {"a": "C", "b": "∅"}, False),
        "C": ({"q4"}, {"a": "∅", "b": "∅"}, True),
        "∅": (set(), {"a": "∅", "b": "∅"}, False),
    }


def test_tanpa_dead_state_jika_tidak_ada_himpunan_kosong():
    nfa = contoh.nfa_failover_lb()
    hasil = nfa_ke_dfa(nfa)
    assert "∅" not in tabel(hasil)


def test_langkah_proses_tercatat_berurutan():
    # Untuk penjelasan langkah demi langkah di aplikasi
    hasil = nfa_ke_dfa(contoh.nfa_bab67())
    pertama = hasil.catatan[0]
    assert "A" in pertama and "{q0}" in pertama


@pytest.mark.parametrize("pembuat", [
    contoh.nfa_bab67, contoh.nfa_latihan_p, contoh.enfa_bab5, contoh.nfa_failover_lb,
])
def test_nfa_dan_dfa_hasil_konversi_menerima_bahasa_yang_sama(pembuat):
    nfa = pembuat()
    dfa = nfa_ke_dfa(nfa).dfa
    simbol = sorted(nfa.alfabet)
    for panjang in range(7):
        for huruf in product(simbol, repeat=panjang):
            s = "".join(huruf)
            assert nfa.jalankan(s).diterima == dfa.jalankan(s).diterima, s
