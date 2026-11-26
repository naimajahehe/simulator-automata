"""
Kumpulan contoh automata siap pakai (preset), diambil dari bahan ajar dosen
ditambah satu contoh kasus failover load balancer.
"""
from types import SimpleNamespace

from automata.dfa import DFA
from automata.nfa import NFA, EPSILON


# ---------------------------------------------------------------- DFA ----

def dfa_berakhiran_0():
    """Bab 4 slide 5–7: string biner yang berakhir dengan 0."""
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


def dfa_habis_dibagi_3():
    """Bab 4 slide 15: bilangan biner habis dibagi 3. State r = sisa bagi, sisa baru = (2·r + bit) mod 3."""
    transisi = {}
    for sisa in range(3):
        for bit in (0, 1):
            transisi[(f"r{sisa}", str(bit))] = f"r{(2 * sisa + bit) % 3}"
    return DFA({"r0", "r1", "r2"}, {"0", "1"}, transisi, "r0", {"r0"})


def dfa_contoh_1():
    """Bab 4-lanjutan slide 7: DFA dengan state q0–q3, Σ = {a, b}, F = {q1}."""
    return DFA(
        states={"q0", "q1", "q2", "q3"},
        alfabet={"a", "b"},
        transisi={
            ("q0", "a"): "q1", ("q0", "b"): "q2",
            ("q1", "a"): "q1", ("q1", "b"): "q1",
            ("q2", "a"): "q2", ("q2", "b"): "q3",
            ("q3", "a"): "q1", ("q3", "b"): "q1",
        },
        awal="q0",
        akhir={"q1"},
    )


def dfa_mengandung_001():
    """Bab 4-lanjutan slide 11–12: string biner yang mengandung substring 001."""
    return DFA(
        states={"q0", "q1", "q2", "q3"},
        alfabet={"0", "1"},
        transisi={
            ("q0", "0"): "q1", ("q0", "1"): "q0",
            ("q1", "0"): "q2", ("q1", "1"): "q0",
            ("q2", "0"): "q2", ("q2", "1"): "q3",
            ("q3", "0"): "q3", ("q3", "1"): "q3",
        },
        awal="q0",
        akhir={"q3"},
    )


def definisi_dfa_belum_lengkap():
    """
    Bab 4 slide 10: δ(q1, b) belum didefinisikan sehingga BELUM memenuhi syarat DFA.
    Dikembalikan sebagai definisi mentah (bukan objek DFA) agar aplikasi bisa
    menunjukkan pesan validasi dan fitur melengkapi dengan dead state.
    """
    return SimpleNamespace(
        states={"q0", "q1"},
        alfabet={"a", "b"},
        transisi={("q0", "a"): "q1", ("q0", "b"): "q0", ("q1", "a"): "q1"},
        awal="q0",
        akhir={"q1"},
    )


# ---------------------------------------------------------------- NFA ----

def nfa_bab67():
    """Bab 6-7 slide 7–8: NFA yang akan dikonversi ke DFA (Σ = {0,1}, F = {q2})."""
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


def nfa_latihan_p():
    """Bab 6-7 slide 15: latihan mandiri NFA p0–p2 (Σ = {a,b}, F = {p2})."""
    return NFA(
        states={"p0", "p1", "p2"},
        alfabet={"a", "b"},
        transisi={
            ("p0", "a"): {"p0", "p1"},
            ("p1", "b"): {"p2"},
            ("p2", "a"): {"p2"}, ("p2", "b"): {"p2"},
        },
        awal="p0",
        akhir={"p2"},
    )


def enfa_bab5():
    """Bab 5: NFA dengan ε-move  q0 -ε-> q1 -b-> q2 -ε-> q3 -a-> q4, F = {q1, q4}."""
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


def nfa_failover_lb():
    """
    Contoh tambahan: model sederhana ketersediaan layanan pada topologi load balancer
    aktif-pasif (Nginx + Keepalived, MASTER/BACKUP).

    State : N = normal, D = terdegradasi (satu server aplikasi mati),
            F = failover (BACKUP mengambil alih VIP), X = layanan mati (down)
    Simbol: m = mesin LB MASTER mati, s = satu server aplikasi mati, r = komponen pulih
    Nondeterminisme: saat MASTER mati (N, m) hasilnya bisa F (VIP berhasil pindah)
    atau X (VIP gagal pindah). State akhir = layanan masih tersedia.
    """
    return NFA(
        states={"N", "D", "F", "X"},
        alfabet={"m", "s", "r"},
        transisi={
            ("N", "m"): {"F", "X"}, ("N", "s"): {"D"}, ("N", "r"): {"N"},
            ("D", "m"): {"X"}, ("D", "s"): {"X"}, ("D", "r"): {"N"},
            ("F", "m"): {"X"}, ("F", "s"): {"X"}, ("F", "r"): {"N"},
            ("X", "m"): {"X"}, ("X", "s"): {"X"}, ("X", "r"): {"N"},
        },
        awal="N",
        akhir={"N", "D", "F"},
    )


# Daftar preset untuk ditampilkan di aplikasi: nama -> (fungsi pembuat, contoh string uji)
PRESET_DFA = {
    "Berakhiran 0 (Bab 4)": (dfa_berakhiran_0, "1010"),
    "Biner habis dibagi 3 (Bab 4)": (dfa_habis_dibagi_3, "110"),
    "DFA contoh 1, q0–q3 (Bab 4 lanjutan)": (dfa_contoh_1, "abbab"),
    "Mengandung 001 (Bab 4 lanjutan)": (dfa_mengandung_001, "111001"),
    "DFA belum lengkap (Bab 4 slide 10)": (definisi_dfa_belum_lengkap, "aab"),
}

PRESET_NFA = {
    "NFA q0–q2 (Bab 6-7)": (nfa_bab67, "001"),
    "Latihan NFA p0–p2 (Bab 6-7)": (nfa_latihan_p, "abb"),
    "NFA dengan ε-move (Bab 5)": (enfa_bab5, "ba"),
    "Tambahan: failover load balancer": (nfa_failover_lb, "msr"),
}
