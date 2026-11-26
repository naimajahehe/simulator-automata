"""
Modul NFA (Nondeterministic Finite Automata) dengan ε-move — bagian Anggota 2.

NFA juga 5-tuple  M = (Q, Σ, δ, q0, F), bedanya pada fungsi transisi:
    δ : Q × (Σ ∪ {ε}) → P(Q)
Hasil transisi berupa HIMPUNAN state (boleh kosong ∅, satu, atau banyak).
Transisi ε (ε-move) berarti pindah state TANPA membaca input.

Disimpan sebagai dict {(state, simbol): {state_tujuan, ...}}; simbol ε ditulis EPSILON.
"""
from dataclasses import dataclass, field

EPSILON = "ε"


class NFATidakValid(ValueError):
    """Dilempar jika definisi NFA tidak memenuhi syarat 5-tuple."""


@dataclass
class LangkahNFA:
    """Satu langkah: dari himpunan `dari`, baca `simbol`,
    hasil move = `setelah_move`, lalu ditambah ε-closure = `setelah_closure`."""
    dari: frozenset
    simbol: str
    setelah_move: frozenset
    setelah_closure: frozenset


@dataclass
class HasilNFA:
    diterima: bool
    jalur: list            # himpunan state aktif setelah tiap simbol (diawali ε-closure state awal)
    langkah: list = field(default_factory=list)
    pesan: str = ""


class NFA:
    def __init__(self, states, alfabet, transisi, awal, akhir):
        self.states = set(states)
        self.alfabet = set(alfabet) - {EPSILON}
        # simpan tujuan sebagai frozenset dan buang entri kosong
        self.transisi = {k: frozenset(v) for k, v in transisi.items() if v}
        self.awal = awal
        self.akhir = set(akhir)
        self._validasi()

    def _validasi(self):
        salah = []
        if not self.states:
            salah.append("Himpunan state Q tidak boleh kosong.")
        if not self.alfabet:
            salah.append("Alfabet Σ tidak boleh kosong.")
        if self.awal not in self.states:
            salah.append(f"State awal '{self.awal}' tidak ada di Q.")
        for q in sorted(self.akhir - self.states):
            salah.append(f"State akhir '{q}' tidak ada di Q.")
        for (q, a), tujuan in sorted(self.transisi.items()):
            if q not in self.states:
                salah.append(f"Transisi dari '{q}' tidak valid: state tidak ada di Q.")
            if a != EPSILON and a not in self.alfabet:
                salah.append(f"Simbol '{a}' pada δ({q}, {a}) tidak ada di Σ.")
            for t in sorted(tujuan - self.states):
                salah.append(f"δ({q}, {a}) memuat '{t}' yang tidak ada di Q.")
        if salah:
            raise NFATidakValid("\n".join(salah))

    def punya_epsilon(self):
        return any(a == EPSILON for (_, a) in self.transisi)

    def tujuan(self, state, simbol):
        """δ(state, simbol): himpunan tujuan, ∅ jika tidak ada transisi."""
        return self.transisi.get((state, simbol), frozenset())

    def epsilon_closure(self, himpunan):
        """
        ε-closure: semua state yang dapat dicapai dari `himpunan` hanya
        lewat transisi ε (termasuk state itu sendiri). Ditelusuri dengan
        tumpukan (stack) agar ε yang berantai ikut terhitung.
        """
        hasil = set(himpunan)
        tumpukan = list(himpunan)
        while tumpukan:
            q = tumpukan.pop()
            for p in self.tujuan(q, EPSILON):
                if p not in hasil:
                    hasil.add(p)
                    tumpukan.append(p)
        return frozenset(hasil)

    def move(self, himpunan, simbol):
        """Gabungan δ(q, simbol) untuk setiap q di himpunan (tanpa ε-closure)."""
        hasil = set()
        for q in himpunan:
            hasil |= self.tujuan(q, simbol)
        return frozenset(hasil)

    def jalankan(self, string):
        """
        Simulasi NFA: lacak SEMUA kemungkinan state sekaligus sebagai satu himpunan.
        String diterima jika himpunan terakhir memuat minimal satu state akhir.
        """
        sekarang = self.epsilon_closure({self.awal})
        jalur = [sekarang]
        daftar_langkah = []
        for simbol in string:
            if simbol not in self.alfabet:
                pesan = f"Simbol '{simbol}' tidak ada di alfabet Σ, string DITOLAK."
                return HasilNFA(False, jalur, daftar_langkah, pesan)
            setelah_move = self.move(sekarang, simbol)
            setelah_closure = self.epsilon_closure(setelah_move)
            langkah = LangkahNFA(sekarang, simbol, setelah_move, setelah_closure)
            daftar_langkah.append(langkah)
            jalur.append(setelah_closure)
            sekarang = setelah_closure

        final_tercapai = sekarang & self.akhir
        himpunan_akhir = format_himpunan(sekarang)
        if final_tercapai:
            pesan = (f"Himpunan akhir {himpunan_akhir} memuat state akhir "
                     f"{format_himpunan(final_tercapai)}, string DITERIMA.")
        else:
            pesan = (f"Himpunan akhir {himpunan_akhir} tidak memuat state akhir, "
                     "string DITOLAK.")
        return HasilNFA(bool(final_tercapai), jalur, daftar_langkah, pesan)


def format_himpunan(himpunan):
    """Tulis himpunan state seperti di PPT: {q0,q1}, atau ∅ jika kosong."""
    if not himpunan:
        return "∅"
    return "{" + ",".join(sorted(himpunan, key=urutan_alami)) + "}"


def urutan_alami(nama):
    """Urutkan q2 sebelum q10 (angka dibandingkan sebagai angka)."""
    import re
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", nama)]
