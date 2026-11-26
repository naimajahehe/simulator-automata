"""Pengujian kelas NFA (termasuk ε-transisi). Kasus uji dari PPT Bab 5 dan Bab 6-7."""
import pytest

from automata.nfa import NFA, NFATidakValid, EPSILON


def nfa_bab67():
    # Bab 6-7 slide 7-8
    return NFA(
        states={"q0", "q1", "q2"},
        alfabet={"0", "1"},
        transisi={
            ("q0", "0"): {"q0", "q1"},
            ("q1", "1"): {"q1", "q2"},
            ("q2", "0"): {"q2"}, ("q2", "1"): {"q2"},
        },
        awal="q0",
        akhir={"q2"},
    )


def enfa_bab5():
    # Bab 5: q0 -ε-> q1 -b-> q2 -ε-> q3 -a-> q4, state akhir q1 dan q4
    return NFA(
        states={"q0", "q1", "q2", "q3", "q4"},
        alfabet={"a", "b"},
        transisi={
            ("q0", EPSILON): {"q1"},
            ("q1", "b"): {"q2"},
            ("q2", EPSILON): {"q3"},
            ("q3", "a"): {"q4"},
        },
        awal="q0",
        akhir={"q1", "q4"},
    )


@pytest.mark.parametrize("string, diterima", [
    ("0", False), ("01", True), ("011", True), ("1", False), ("001", True), ("", False),
])
def test_nfa_bab67(string, diterima):
    assert nfa_bab67().jalankan(string).diterima is diterima


def test_jejak_nfa_berupa_himpunan_state():
    hasil = nfa_bab67().jalankan("01")
    assert hasil.jalur == [frozenset({"q0"}), frozenset({"q0", "q1"}), frozenset({"q1", "q2"})]


def test_transisi_tidak_ada_menghasilkan_himpunan_kosong():
    hasil = nfa_bab67().jalankan("10")
    assert hasil.jalur[1] == frozenset()
    assert hasil.jalur[2] == frozenset()
    assert hasil.diterima is False


@pytest.mark.parametrize("state, closure", [
    ("q0", {"q0", "q1"}), ("q1", {"q1"}), ("q2", {"q2", "q3"}), ("q3", {"q3"}), ("q4", {"q4"}),
])
def test_epsilon_closure_bab5(state, closure):
    assert enfa_bab5().epsilon_closure({state}) == frozenset(closure)


def test_epsilon_closure_berantai():
    # ε-closure harus mengikuti ε berulang: p -ε-> q -ε-> r
    nfa = NFA({"p", "q", "r"}, {"a"},
              {("p", EPSILON): {"q"}, ("q", EPSILON): {"r"}}, "p", {"r"})
    assert nfa.epsilon_closure({"p"}) == frozenset({"p", "q", "r"})
    assert nfa.jalankan("").diterima is True


@pytest.mark.parametrize("string, diterima", [
    ("", True), ("b", False), ("ba", True), ("a", False), ("bab", False),
])
def test_enfa_bab5(string, diterima):
    assert enfa_bab5().jalankan(string).diterima is diterima


def test_jejak_enfa_mencatat_hasil_move_dan_closure():
    hasil = enfa_bab5().jalankan("b")
    assert hasil.jalur[0] == frozenset({"q0", "q1"})      # ε-closure state awal
    langkah = hasil.langkah[0]
    assert langkah.setelah_move == frozenset({"q2"})
    assert langkah.setelah_closure == frozenset({"q2", "q3"})


def test_nfa_mendeteksi_ada_epsilon():
    assert enfa_bab5().punya_epsilon() is True
    assert nfa_bab67().punya_epsilon() is False


def test_simbol_di_luar_alfabet_ditolak():
    hasil = nfa_bab67().jalankan("02")
    assert hasil.diterima is False
    assert "2" in hasil.pesan


def test_tujuan_tidak_terdaftar_tidak_valid():
    with pytest.raises(NFATidakValid):
        NFA({"q0"}, {"a"}, {("q0", "a"): {"qX"}}, "q0", set())


@pytest.mark.parametrize("string, diterima", [("ab", True), ("abb", True), ("ba", False)])
def test_latihan_nfa_p(string, diterima):
    from automata.contoh import nfa_latihan_p
    assert nfa_latihan_p().jalankan(string).diterima is diterima


@pytest.mark.parametrize("string, diterima", [
    ("", True),     # tidak ada kejadian: layanan normal
    ("m", True),    # MASTER mati, ada jalur VIP berhasil pindah ke BACKUP
    ("mm", False),  # kedua load balancer mati
    ("mr", True),   # mati lalu pulih
    ("s", True),    # satu server aplikasi mati: terdegradasi tapi tersedia
    ("ss", False),  # kedua server aplikasi mati
])
def test_nfa_failover_load_balancer(string, diterima):
    from automata.contoh import nfa_failover_lb
    assert nfa_failover_lb().jalankan(string).diterima is diterima
