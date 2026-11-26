"""
Mengubah input pengguna (teks + tabel transisi) menjadi objek DFA/NFA, dan sebaliknya — bagian Anggota 4.

Format tabel: daftar baris, setiap baris berupa dict {"State": nama, simbol1: isi, simbol2: isi, ...}.
    - DFA: isi sel = satu state tujuan
    - NFA: isi sel = beberapa state dipisah koma; kosong, "-" atau "∅" berarti tidak ada transisi
"""
import re

from automata.dfa import DFA, DFATidakValid
from automata.nfa import NFA, EPSILON, urutan_alami

KOSONG = {"", "-", "∅", "{}"}


def pisah_daftar(teks):
    """'q0, q1 q2' -> ['q0', 'q1', 'q2']"""
    return [t for t in re.split(r"[,\s]+", (teks or "").strip()) if t]


def _isi_sel(nilai):
    """Isi satu sel tabel menjadi daftar state (kosong jika tidak ada transisi)."""
    teks = "" if nilai is None else str(nilai).strip().strip("{}")
    return [] if teks in KOSONG else pisah_daftar(teks)


def tabel_dari_automata(automata):
    """Ubah DFA/NFA menjadi baris tabel untuk ditampilkan dan diedit di aplikasi."""
    simbol = sorted(automata.alfabet)
    if isinstance(automata, NFA) and automata.punya_epsilon():
        simbol.append(EPSILON)
    baris = []
    for q in sorted(automata.states, key=urutan_alami):
        row = {"State": q}
        for a in simbol:
            tujuan = automata.transisi.get((q, a))
            if tujuan is None:
                row[a] = ""
            elif isinstance(tujuan, str):
                row[a] = tujuan
            else:
                row[a] = ", ".join(sorted(tujuan, key=urutan_alami))
        baris.append(row)
    return baris


def _baca_dasar(states_teks, alfabet_teks, akhir_teks):
    return set(pisah_daftar(states_teks)), set(pisah_daftar(alfabet_teks)), set(pisah_daftar(akhir_teks))


def dfa_dari_input(states_teks, alfabet_teks, awal, akhir_teks, baris, lengkapi=False):
    """lengkapi=True: transisi yang kosong otomatis diarahkan ke dead state ∅."""
    states, alfabet, akhir = _baca_dasar(states_teks, alfabet_teks, akhir_teks)
    transisi, ganda = {}, []
    for row in baris:
        q = str(row.get("State", "")).strip()
        if not q:
            continue
        for a in alfabet:
            tujuan = _isi_sel(row.get(a))
            if len(tujuan) > 1:
                ganda.append(f"δ({q}, {a}) = {{{', '.join(tujuan)}}}")
            elif tujuan:
                transisi[(q, a)] = tujuan[0]
    if ganda:
        raise DFATidakValid(
            "Pada DFA setiap (state, simbol) harus menuju tepat satu state, tetapi: "
            + "; ".join(ganda) + ". Gunakan tab NFA untuk transisi bercabang."
        )
    if lengkapi:
        return DFA.lengkapi_dengan_dead_state(states, alfabet, transisi, awal.strip(), akhir)
    return DFA(states, alfabet, transisi, awal.strip(), akhir)


def nfa_dari_input(states_teks, alfabet_teks, awal, akhir_teks, baris):
    states, alfabet, akhir = _baca_dasar(states_teks, alfabet_teks, akhir_teks)
    transisi = {}
    for row in baris:
        q = str(row.get("State", "")).strip()
        if not q:
            continue
        for a in list(alfabet) + [EPSILON]:
            tujuan = _isi_sel(row.get(a))
            if tujuan:
                transisi[(q, a)] = set(tujuan)
    return NFA(states, alfabet, transisi, awal.strip(), akhir)
