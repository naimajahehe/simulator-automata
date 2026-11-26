"""
Membuat diagram transisi dalam bahasa DOT (Graphviz) — bagian Anggota 4.
Teks DOT dirender di browser oleh st.graphviz_chart, jadi tidak perlu memasang Graphviz.

Aturan gambar (sesuai PPT):
    lingkaran        = state
    lingkaran ganda  = state akhir
    panah tanpa asal = menunjuk state awal
    label panah      = simbol; beberapa simbol dengan tujuan sama digabung "a, b"
"""
from automata.nfa import EPSILON, urutan_alami

WARNA_SOROT = "#d1495b"
WARNA_AKTIF = "#ffe3a3"


def _q(nama):
    """Beri tanda kutip agar nama seperti ∅ atau {q0,q1} aman di DOT."""
    return '"' + str(nama).replace('"', '\\"') + '"'


def _kepala(states, awal, akhir, aktif=()):
    baris = [
        "digraph automata {",
        "  rankdir=LR;",
        '  node [fontname="Helvetica", fontsize=12];',
        '  edge [fontname="Helvetica", fontsize=11];',
        "  __start [shape=point, width=0.15];",
    ]
    for q in sorted(states, key=urutan_alami):
        bentuk = "doublecircle" if q in akhir else "circle"
        isi = f', style=filled, fillcolor="{WARNA_AKTIF}"' if q in aktif else ""
        baris.append(f"  {_q(q)} [shape={bentuk}{isi}];")
    baris.append(f"  __start -> {_q(awal)};")
    return baris


def _panah(kelompok, disorot=()):
    """kelompok: {(dari, ke): [simbol, ...]} -> baris DOT, satu panah per pasangan (dari, ke)."""
    baris = []
    for (dari, ke), simbol in sorted(kelompok.items(), key=lambda x: (urutan_alami(x[0][0]), urutan_alami(x[0][1]))):
        label = ", ".join(sorted(simbol, key=lambda s: (s == EPSILON, s)))
        gaya = f', color="{WARNA_SOROT}", fontcolor="{WARNA_SOROT}", penwidth=2.5' if (dari, ke) in disorot else ""
        baris.append(f'  {_q(dari)} -> {_q(ke)} [label="{label}"{gaya}];')
    return baris


def dot_dfa(dfa, langkah=None):
    """Diagram DFA. `langkah` (opsional) = daftar Langkah hasil
    jalankan(), dipakai untuk menyorot jalur string."""
    kelompok = {}
    for (dari, a), ke in dfa.transisi.items():
        kelompok.setdefault((dari, ke), []).append(a)
    disorot = {(l.dari, l.ke) for l in (langkah or [])}
    aktif = {langkah[-1].ke} if langkah else ()
    kepala = _kepala(dfa.states, dfa.awal, dfa.akhir, aktif)
    return "\n".join(kepala + _panah(kelompok, disorot) + ["}"])


def dot_nfa(nfa, aktif=()):
    """Diagram NFA. `aktif` (opsional) = himpunan state aktif terakhir, diberi warna."""
    kelompok = {}
    for (dari, a), tujuan in nfa.transisi.items():
        for ke in tujuan:
            kelompok.setdefault((dari, ke), []).append(a)
    return "\n".join(_kepala(nfa.states, nfa.awal, nfa.akhir, set(aktif)) + _panah(kelompok) + ["}"])
