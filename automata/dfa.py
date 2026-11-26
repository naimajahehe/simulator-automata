"""
Modul DFA (Deterministic Finite Automata) — bagian Anggota 1.

DFA didefinisikan sebagai 5-tuple  M = (Q, Σ, δ, q0, F):
    Q  = states    : himpunan state
    Σ  = alfabet   : himpunan simbol input
    δ  = transisi  : fungsi Q × Σ → Q, disimpan sebagai dict {(state, simbol): state_tujuan}
    q0 = awal      : state awal
    F  = akhir     : himpunan state akhir (penerima)

Syarat deterministik: untuk SETIAP pasangan (state, simbol) harus ada TEPAT SATU tujuan.
"""
from dataclasses import dataclass, field


class DFATidakValid(ValueError):
    """Dilempar jika definisi DFA melanggar syarat 5-tuple."""


@dataclass
class Langkah:
    """Satu langkah pembacaan: dari state `dari`, membaca `simbol`, pindah ke `ke`."""
    dari: str
    simbol: str
    ke: str


@dataclass
class HasilDFA:
    diterima: bool
    jalur: list            # urutan state yang dilewati, termasuk state awal
    langkah: list = field(default_factory=list)
    pesan: str = ""

    @property
    def state_akhir(self):
        return self.jalur[-1]


class DFA:
    def __init__(self, states, alfabet, transisi, awal, akhir):
        self.states = set(states)
        self.alfabet = set(alfabet)
        self.transisi = dict(transisi)
        self.awal = awal
        self.akhir = set(akhir)
        self._validasi()

    def _validasi(self):
        """Periksa syarat DFA. Semua kesalahan dikumpulkan sekaligus
        agar pengguna dapat melihat seluruhnya dalam satu pesan."""
        salah = []
        if not self.states:
            salah.append("Himpunan state Q tidak boleh kosong.")
        if not self.alfabet:
            salah.append("Alfabet Σ tidak boleh kosong.")
        if self.awal not in self.states:
            salah.append(f"State awal '{self.awal}' tidak ada di Q.")
        for q in sorted(self.akhir - self.states):
            salah.append(f"State akhir '{q}' tidak ada di Q.")

        kosong = []
        for q in sorted(self.states):
            for a in sorted(self.alfabet):
                tujuan = self.transisi.get((q, a))
                if tujuan is None:
                    kosong.append(f"δ({q}, {a})")
                elif tujuan not in self.states:
                    salah.append(f"δ({q}, {a}) = '{tujuan}' tidak ada di Q.")
        if kosong:
            salah.append(
                "Transisi belum lengkap: " + ", ".join(kosong)
                + ". Setiap (state, simbol) wajib punya tepat satu tujuan — "
                "tambahkan dead state (state jebakan) untuk melengkapinya."
            )
        if salah:
            raise DFATidakValid("\n".join(salah))

    @classmethod
    def lengkapi_dengan_dead_state(cls, states, alfabet, transisi, awal, akhir, nama_dead="∅"):
        """Isi transisi yang kosong dengan dead state yang berputar ke dirinya sendiri."""
        states = set(states)
        transisi = dict(transisi)
        perlu_dead = any((q, a) not in transisi for q in states for a in alfabet)
        if perlu_dead:
            states.add(nama_dead)
            for q in states:
                for a in alfabet:
                    transisi.setdefault((q, a), nama_dead)
        return cls(states, alfabet, transisi, awal, akhir)

    def langkah(self, state, simbol):
        """Fungsi transisi δ(state, simbol): selalu tepat satu state tujuan."""
        return self.transisi[(state, simbol)]

    def jalankan(self, string):
        """
        Fungsi transisi diperluas δ*: baca string dari kiri ke kanan,
        satu simbol per langkah. String diterima jika setelah simbol
        terakhir mesin berada di salah satu state akhir.
        """
        sekarang = self.awal
        jalur = [sekarang]
        daftar_langkah = []
        for simbol in string:
            if simbol not in self.alfabet:
                pesan = f"Simbol '{simbol}' tidak ada di alfabet Σ, string DITOLAK."
                return HasilDFA(False, jalur, daftar_langkah, pesan)
            berikut = self.langkah(sekarang, simbol)
            daftar_langkah.append(Langkah(sekarang, simbol, berikut))
            jalur.append(berikut)
            sekarang = berikut

        diterima = sekarang in self.akhir
        if diterima:
            pesan = f"Berhenti di {sekarang} ∈ F, string DITERIMA."
        else:
            pesan = f"Berhenti di {sekarang} ∉ F, string DITOLAK."
        return HasilDFA(diterima, jalur, daftar_langkah, pesan)
