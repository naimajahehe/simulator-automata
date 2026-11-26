# Simulator Automata: DFA, NFA & Konversi NFA → DFA

Tugas Final Teori Bahasa dan Otomata. Aplikasi web (Python + Streamlit) untuk:

1. **Simulasi DFA**: menguji string, menampilkan jalur state, tabel langkah, dan diagram transisi.
2. **Simulasi NFA dengan ε-move**: melacak himpunan state, menampilkan ε-closure dan jejak himpunan.
3. **Konversi NFA → DFA** (subset construction): tabel transisi DFA, langkah konversi, diagram NFA & DFA, dan uji kesetaraan.

Contoh bawaan diambil dari bahan ajar (Bab 4, Bab 4 lanjutan, Bab 5, Bab 6-7), ditambah satu contoh kasus failover load balancer.

- 🎬 **Video demo:** https://youtu.be/5Cqkn-kDfE0
- 📊 **Slide presentasi:** https://docs.google.com/presentation/d/1W48XdIJ5IUvhkE_ayw2MsmCT6pSFQKk81L99pGyZaHQ/edit?usp=sharing

### Tim

| Nama | NIM | Modul |
|---|---|---|
| Muhammad Naim | 105841108124 | DFA (`automata/dfa.py`) |
| Khairunnisa Ramadhani | 105841108024 | NFA & ε-move (`automata/nfa.py`) |
| Nur Insani | 105841109224 | Konversi NFA → DFA (`automata/konversi.py`) |
| Riskawana Hamanjah | 105841109324 | Antarmuka, diagram & pengujian (`app.py`, `tampilan/`) |

Tugas Final mata kuliah Teori Bahasa dan Otomata. Dosen pengampu: Chyquitha Danuputri, S.Kom., M.Kom.
Program Studi Informatika, Universitas Muhammadiyah Makassar.

## Cara menjalankan

Butuh Python 3.10 atau lebih baru.

```bash
pip install -r requirements.txt
streamlit run app.py
```

Browser akan terbuka di `http://localhost:8501`.

Tab dan contoh yang dipilih tersimpan di URL, jadi bisa dibuka langsung, misalnya:
`http://localhost:8501/?tab=NFA&nfa_preset=NFA dengan ε-move (Bab 5)`

## Menjalankan pengujian

```bash
pip install pytest
python -m pytest
```

Pengujian memakai kasus dari PPT dosen, misalnya tabel konversi A–E Bab 6-7, ε-closure Bab 5, dan DFA habis dibagi 3. Ada juga pengujian yang membandingkan NFA dengan DFA hasil konversinya untuk semua string sampai panjang 6.

## Struktur kode dan pembagian tugas

| File | Isi | Penanggung jawab |
|---|---|---|
| `automata/dfa.py` | Kelas `DFA`: validasi 5-tuple, `langkah()` (δ), `jalankan()` (δ*), dead state | Muhammad Naim |
| `automata/nfa.py` | Kelas `NFA`: `epsilon_closure()`, `move()`, `jalankan()` | Khairunnisa Ramadhani |
| `automata/konversi.py` | `nfa_ke_dfa()`: subset construction | Nur Insani |
| `app.py`, `tampilan/` | Antarmuka Streamlit, parsing tabel input, diagram DOT | Riskawana Hamanjah |
| `automata/contoh.py` | Contoh bawaan dari PPT | bersama |
| `tests/` | Pengujian otomatis (pytest) | bersama |

## (Opsional) Publikasi online

Agar dosen bisa mencoba tanpa memasang Python:

1. Fork repositori ini (atau gunakan langsung).
2. Buka share.streamlit.io, masuk dengan akun GitHub, lalu pilih **Create app** dan arahkan ke `app.py`.
3. Salin link yang diberikan ke laporan.
