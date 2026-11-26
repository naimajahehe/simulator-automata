"""
Aplikasi Simulator Automata: DFA, NFA (dengan ε), dan Konversi NFA → DFA.
Jalankan:  streamlit run app.py

Bagian tampilan (antarmuka) — Anggota 4.
Logika automata ada di folder automata/ (DFA: Anggota 1, NFA: Anggota 2, Konversi: Anggota 3).
"""
import pandas as pd
import streamlit as st

from automata.contoh import PRESET_DFA, PRESET_NFA
from automata.dfa import DFATidakValid
from automata.konversi import nfa_ke_dfa
from automata.nfa import EPSILON, NFATidakValid, format_himpunan, urutan_alami
from tampilan.diagram import dot_dfa, dot_nfa
from tampilan.input_tabel import (
    dfa_dari_input, nfa_dari_input, pisah_daftar, tabel_dari_automata,
)

ISI_SENDIRI = "Isi sendiri"

st.set_page_config(page_title="Simulator Automata", page_icon="🔁", layout="wide")


# ------------------------------------------------------------------ util --

def isi_dari_preset(prefix, presets, nama):
    """Salin definisi preset `nama` ke kolom-kolom input (dipanggil saat preset berganti)."""
    if nama == ISI_SENDIRI:
        nilai = {"states": "", "alfabet": "", "awal": "", "akhir": "", "string": "", "tabel": []}
    else:
        pembuat, contoh_string = presets[nama]
        m = pembuat()
        nilai = {
            "states": ", ".join(sorted(m.states, key=urutan_alami)),
            "alfabet": ", ".join(sorted(m.alfabet)),
            "awal": m.awal,
            "akhir": ", ".join(sorted(m.akhir, key=urutan_alami)),
            "string": contoh_string,
            "tabel": tabel_dari_automata(m),
        }
    for kunci, isi in nilai.items():
        st.session_state[f"{prefix}_{kunci}"] = isi
    st.session_state[f"{prefix}_versi"] = st.session_state.get(f"{prefix}_versi", 0) + 1
    st.session_state[f"{prefix}_dimuat"] = nama


def form_definisi(prefix, presets, jenis):
    """
    Form input 5-tuple + tabel transisi. Mengembalikan (states_teks, alfabet_teks, awal, akhir_teks, baris_tabel).
    jenis = "DFA" atau "NFA" (NFA boleh punya kolom ε dan sel berisi beberapa state).
    """
    # bind="query-params": contoh yang dipilih tersimpan di URL, jadi bisa dibagikan/dibuka langsung
    nama = st.selectbox("Pilih contoh", list(presets) + [ISI_SENDIRI], key=f"{prefix}_preset",
                        bind="query-params")
    if st.session_state.get(f"{prefix}_dimuat") != nama:
        isi_dari_preset(prefix, presets, nama)

    k1, k2, k3, k4 = st.columns(4)
    states_teks = k1.text_input("Q — himpunan state", key=f"{prefix}_states", help="Pisahkan dengan koma, mis. q0, q1, q2")
    alfabet_teks = k2.text_input("Σ — alfabet", key=f"{prefix}_alfabet", help="Mis. 0, 1  atau  a, b")
    awal = k3.text_input("q0 — state awal", key=f"{prefix}_awal")
    akhir_teks = k4.text_input("F — state akhir", key=f"{prefix}_akhir", help="Boleh lebih dari satu, pisahkan dengan koma")

    states = sorted(set(pisah_daftar(states_teks)), key=urutan_alami)
    simbol = sorted(set(pisah_daftar(alfabet_teks)))
    if jenis == "NFA":
        ada_eps = any(row.get(EPSILON) for row in st.session_state.get(f"{prefix}_tabel", []))
        if st.checkbox("Gunakan transisi ε (ε-move)", value=ada_eps, key=f"{prefix}_pakai_eps"):
            simbol = simbol + [EPSILON]

    # Tabel dasar: baris = state, kolom = simbol; isinya diambil dari preset/tabel terakhir bila ada
    lama = {row["State"]: row for row in st.session_state.get(f"{prefix}_tabel", [])}
    dasar = pd.DataFrame(
        [{"State": q, **{a: lama.get(q, {}).get(a, "") for a in simbol}} for q in states],
        columns=["State"] + simbol,
    )
    petunjuk = ("Isi setiap sel dengan SATU state tujuan." if jenis == "DFA"
                else "Isi sel dengan satu atau beberapa state dipisah koma; kosongkan jika ∅.")
    st.caption(f"Tabel transisi δ — baris = state saat ini, kolom = simbol. {petunjuk}")
    kunci_tabel = f"{prefix}_editor_{st.session_state.get(f'{prefix}_versi', 0)}_{'|'.join(states)}_{'|'.join(simbol)}"
    if states and simbol:
        hasil_edit = st.data_editor(dasar, key=kunci_tabel, hide_index=True, width="stretch",
                                    disabled=["State"])
        baris = hasil_edit.fillna("").to_dict("records")
    else:
        baris = []
    st.session_state[f"{prefix}_tabel"] = baris
    return states_teks, alfabet_teks, awal, akhir_teks, baris


def tampilkan_5_tuple(m, jenis):
    teks_delta = "Q × Σ → Q" if jenis == "DFA" else "Q × (Σ ∪ {ε}) → P(Q)"
    st.markdown(
        f"**M = (Q, Σ, δ, q0, F)**  \n"
        f"Q = {format_himpunan(m.states)} · Σ = {{{', '.join(sorted(m.alfabet))}}} · "
        f"δ : {teks_delta} · q0 = {m.awal} · F = {format_himpunan(m.akhir)}"
    )


def form_masih_kosong(data):
    """True jika Q dan Σ belum diisi sama sekali (mode Isi sendiri baru dibuka)."""
    states_teks, alfabet_teks = data[0], data[1]
    if not pisah_daftar(states_teks) and not pisah_daftar(alfabet_teks):
        st.info("Isi Q, Σ, q0, dan F terlebih dahulu, lalu lengkapi tabel transisi yang muncul.")
        return True
    return False


def tampilkan_tidak_valid(jenis, galat):
    """Tampilkan setiap kesalahan definisi sebagai satu butir daftar."""
    butir = "\n".join(f"- {baris}" for baris in str(galat).splitlines())
    st.error(f"**{jenis} belum valid:**\n{butir}")


def tampilkan_hasil(diterima, pesan):
    if diterima:
        st.success(f"✅ DITERIMA — {pesan}")
    else:
        st.error(f"❌ DITOLAK — {pesan}")


# ------------------------------------------------------------- tab DFA --

def tab_dfa():
    st.subheader("Simulasi DFA (Deterministic Finite Automata)")
    st.caption("Setiap pasangan (state, simbol) menuju tepat satu state. String diterima jika "
               "setelah simbol terakhir mesin berhenti di state akhir.")
    data = form_definisi("dfa", PRESET_DFA, "DFA")
    if form_masih_kosong(data):
        return
    try:
        lengkapi = st.session_state.get("dfa_lengkapi", False)
        dfa = dfa_dari_input(*data, lengkapi=lengkapi)
    except DFATidakValid as e:
        tampilkan_tidak_valid("DFA", e)
        if "dead state" in str(e):
            st.checkbox("Lengkapi otomatis dengan dead state ∅", key="dfa_lengkapi")
        return

    kiri, kanan = st.columns([1, 1])
    with kiri:
        tampilkan_5_tuple(dfa, "DFA")
        string = st.text_input("String yang diuji (kosongkan untuk ε)", key="dfa_string")
        hasil = dfa.jalankan(string)
        tampilkan_hasil(hasil.diterima, hasil.pesan)
        jejak = hasil.jalur[0] + "".join(f" –{l.simbol}→ {l.ke}" for l in hasil.langkah)
        st.markdown(f"**Jalur:** `{jejak}`")
        if hasil.langkah:
            st.dataframe(pd.DataFrame(
                [{"Langkah": i, "State saat ini": l.dari, "Baca": l.simbol,
                  "Transisi": f"δ({l.dari}, {l.simbol})", "State baru": l.ke}
                 for i, l in enumerate(hasil.langkah, 1)]
            ), hide_index=True, width="stretch")
    with kanan:
        st.markdown("**Diagram transisi** (jalur string disorot merah)")
        st.graphviz_chart(dot_dfa(dfa, hasil.langkah))


# ------------------------------------------------------------- tab NFA --

def tabel_closure(nfa):
    return pd.DataFrame([{"State": q, "ε-closure": format_himpunan(nfa.epsilon_closure({q}))}
                         for q in sorted(nfa.states, key=urutan_alami)])


def tab_nfa():
    st.subheader("Simulasi NFA (Nondeterministic Finite Automata) dengan ε-move")
    st.caption("Satu simbol boleh menuju beberapa state atau tidak ke mana pun (∅). Program melacak "
               "SEMUA kemungkinan state sebagai satu himpunan. String diterima jika himpunan terakhir "
               "memuat minimal satu state akhir.")
    data = form_definisi("nfa", PRESET_NFA, "NFA")
    if form_masih_kosong(data):
        return
    try:
        nfa = nfa_dari_input(*data)
    except NFATidakValid as e:
        tampilkan_tidak_valid("NFA", e)
        return

    kiri, kanan = st.columns([1, 1])
    with kiri:
        tampilkan_5_tuple(nfa, "NFA")
        if nfa.punya_epsilon():
            st.markdown("**ε-closure tiap state** (state yang dicapai tanpa membaca input)")
            st.dataframe(tabel_closure(nfa), hide_index=True, width="stretch")
        string = st.text_input("String yang diuji (kosongkan untuk ε)", key="nfa_string")
        hasil = nfa.jalankan(string)
        tampilkan_hasil(hasil.diterima, hasil.pesan)
        jejak = format_himpunan(hasil.jalur[0]) + "".join(
            f" –{l.simbol}→ {format_himpunan(l.setelah_closure)}" for l in hasil.langkah)
        st.markdown(f"**Jejak himpunan state:** `{jejak}`")
        if hasil.langkah:
            st.dataframe(pd.DataFrame(
                [{"Langkah": i, "Himpunan saat ini": format_himpunan(l.dari), "Baca": l.simbol,
                  "move": format_himpunan(l.setelah_move), "ε-closure": format_himpunan(l.setelah_closure)}
                 for i, l in enumerate(hasil.langkah, 1)]
            ), hide_index=True, width="stretch")
    with kanan:
        st.markdown("**Diagram transisi** (state aktif terakhir diberi warna)")
        st.graphviz_chart(dot_nfa(nfa, hasil.jalur[-1]))


# ------------------------------------------------------ tab Konversi --

def tab_konversi():
    st.subheader("Konversi NFA → DFA (Subset Construction)")
    st.caption("Satu state DFA = satu himpunan state NFA. Transisi DFA = gabungan tujuan semua anggota "
               "himpunan (ditambah ε-closure). State DFA final jika himpunannya memuat state akhir NFA.")
    data = form_definisi("konv", PRESET_NFA, "NFA")
    if form_masih_kosong(data):
        return
    try:
        nfa = nfa_dari_input(*data)
    except NFATidakValid as e:
        tampilkan_tidak_valid("NFA", e)
        return

    hasil = nfa_ke_dfa(nfa)
    simbol = sorted(nfa.alfabet)

    st.markdown("### Tabel transisi DFA hasil konversi")
    st.dataframe(pd.DataFrame(
        [{"State DFA": ("→ " if b.nama == hasil.dfa.awal else "") + b.nama,
          "Himpunan NFA": format_himpunan(b.himpunan),
          **{f"Input {a}": b.tujuan[a] for a in simbol},
          "Final?": "Ya" if b.final else "Tidak"} for b in hasil.baris]
    ), hide_index=True, width="stretch")
    st.markdown(f"**F DFA** = {{{', '.join(sorted(hasil.dfa.akhir)) or '∅'}}} — yaitu himpunan yang memuat "
                f"state akhir NFA {format_himpunan(nfa.akhir)}.")

    with st.expander("Lihat langkah konversi satu per satu"):
        for i, c in enumerate(hasil.catatan, 1):
            st.markdown(f"{i}. `{c}`")

    kiri, kanan = st.columns(2)
    with kiri:
        st.markdown("**NFA asal**")
        st.graphviz_chart(dot_nfa(nfa))
    with kanan:
        st.markdown("**DFA hasil konversi**")
        st.graphviz_chart(dot_dfa(hasil.dfa))

    st.markdown("### Uji kesetaraan: string yang sama pada NFA dan DFA")
    string = st.text_input("String yang diuji", key="konv_string")
    h_nfa, h_dfa = nfa.jalankan(string), hasil.dfa.jalankan(string)
    a, b = st.columns(2)
    with a:
        st.markdown("**NFA**")
        tampilkan_hasil(h_nfa.diterima, h_nfa.pesan)
    with b:
        st.markdown("**DFA**")
        jalur = " → ".join(h_dfa.jalur)
        tampilkan_hasil(h_dfa.diterima, f"lintasan {jalur}. {h_dfa.pesan}")
    if h_nfa.diterima == h_dfa.diterima:
        st.info("NFA dan DFA hasil konversi memberi keputusan yang sama — hasilnya sama, bahasa yang diterima setara.")
    else:
        st.warning("Keputusan berbeda — periksa kembali definisi automata.")


# ------------------------------------------------------------- halaman --

st.title("🔁 Simulator Automata: DFA, NFA & Konversi NFA → DFA")
st.caption("Tugas Final Teori Bahasa dan Otomata · contoh diambil dari bahan ajar perkuliahan")

with st.sidebar:
    st.header("Petunjuk")
    st.markdown(
        "1. Pilih tab **DFA**, **NFA**, atau **Konversi**.\n"
        "2. Pilih contoh, atau pilih **Isi sendiri** lalu isi Q, Σ, q0, F, dan tabel transisi.\n"
        "3. Ketik string yang ingin diuji.\n\n"
        "**Notasi**  \n"
        "∅ = himpunan kosong / dead state  \n"
        "ε = string kosong / transisi tanpa input  \n"
        "→ = state awal"
    )
    st.header("Pembagian modul")
    st.markdown(
        "- `automata/dfa.py` — Muhammad Naim\n"
        "- `automata/nfa.py` — Khairunnisa Ramadhani\n"
        "- `automata/konversi.py` — Nur Insani\n"
        "- `app.py`, `tampilan/` — Riskawana Hamanjah"
    )

tab1, tab2, tab3 = st.tabs(["DFA", "NFA", "Konversi NFA → DFA"], key="tab", bind="query-params")
with tab1:
    tab_dfa()
with tab2:
    tab_nfa()
with tab3:
    tab_konversi()
