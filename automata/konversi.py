"""
Modul konversi NFA → DFA dengan metode himpunan (Subset Construction) — bagian Anggota 3.

Ide utama: SATU state DFA mewakili SATU HIMPUNAN state NFA.
    1. Mulai : state awal DFA = ε-closure({q0})
    2. Pindah: untuk tiap simbol, gabungkan tujuan semua anggota himpunan, lalu ambil ε-closure-nya
    3. Ulangi: setiap himpunan baru didaftarkan sebagai state DFA baru, sampai tidak ada yang baru
State DFA menjadi state akhir jika himpunannya memuat minimal satu state akhir NFA.
Himpunan kosong ∅ (jika muncul) menjadi dead state yang berputar ke dirinya sendiri.
"""
from collections import deque
from dataclasses import dataclass, field

from automata.dfa import DFA
from automata.nfa import format_himpunan

NAMA_DEAD = "∅"


@dataclass
class BarisKonversi:
    """Satu baris tabel transisi DFA hasil konversi."""
    nama: str
    himpunan: frozenset
    tujuan: dict          # {simbol: nama state DFA tujuan}
    final: bool


@dataclass
class HasilKonversi:
    dfa: DFA
    baris: list                                  # urut sesuai ditemukan
    catatan: list = field(default_factory=list)  # penjelasan langkah demi langkah


def _nama_ke(i):
    """0 -> A, 1 -> B, ..., 25 -> Z, 26 -> A1, ..."""
    huruf = chr(ord("A") + i % 26)
    return huruf if i < 26 else f"{huruf}{i // 26}"


def nfa_ke_dfa(nfa):
    simbol_urut = sorted(nfa.alfabet)
    nama = {}          # himpunan state NFA -> nama state DFA
    antrean = deque()  # himpunan yang belum diproses (BFS)
    catatan = []

    def daftarkan(himpunan):
        """Beri nama untuk himpunan baru lalu masukkan ke antrean."""
        if himpunan not in nama:
            if himpunan:
                nama[himpunan] = _nama_ke(sum(1 for h in nama if h))
            else:
                nama[himpunan] = NAMA_DEAD
            antrean.append(himpunan)
            return True
        return False

    # Langkah 1: state awal DFA = ε-closure dari state awal NFA
    awal = nfa.epsilon_closure({nfa.awal})
    daftarkan(awal)
    catatan.append(f"Mulai: state awal DFA {nama[awal]} = "
                   f"ε-closure({{{nfa.awal}}}) = {format_himpunan(awal)}")

    # Langkah 2–3: proses antrean sampai tidak ada himpunan baru
    baris = []
    while antrean:
        himpunan = antrean.popleft()
        tujuan = {}
        for a in simbol_urut:
            hasil = nfa.epsilon_closure(nfa.move(himpunan, a))
            baru = daftarkan(hasil)
            tujuan[a] = nama[hasil]
            asal, ke = format_himpunan(himpunan), format_himpunan(hasil)
            info = f" → state baru {nama[hasil]}" if baru else f" = {nama[hasil]}"
            catatan.append(f"{nama[himpunan]} = {asal} --{a}--> {ke}{info}")
        final = bool(himpunan & nfa.akhir)
        baris.append(BarisKonversi(nama[himpunan], himpunan, tujuan, final))

    dfa = DFA(
        states={b.nama for b in baris},
        alfabet=nfa.alfabet,
        transisi={(b.nama, a): t for b in baris for a, t in b.tujuan.items()},
        awal=nama[awal],
        akhir={b.nama for b in baris if b.final},
    )
    finals = [b.nama for b in baris if b.final]
    daftar_final = "{" + ", ".join(finals) + "}" if finals else "∅"
    catatan.append(f"State akhir DFA = himpunan yang memuat state akhir NFA "
                   f"{format_himpunan(nfa.akhir)}: {daftar_final}")
    return HasilKonversi(dfa, baris, catatan)
