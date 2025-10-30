# 🧠 Tugas Besar 1 IF3070 — Dasar Inteligensi Artifisial  
## Pencarian Solusi *Bin Packing Problem* dengan *Local Search Algorithms*

### 👥 Best First Samuel Team Members
| NIM | Nama Lengkap |
|-----|---------------|
| 18223011 | Samuel Chris Michael Bagasta S. |
| 18223057 | Stanislaus Ardy Bramantyo |
| 18223097 | Audy Alicia Renatha Tirayoh |

---

## 📂 Repository Structure
```
Tubes_DAI/
│
├── src/                # Folder berisi source code program
│   ├── HillClimbingSteepest.py
│   ├── HillClimbingStochastic.py
│   ├── HillClimbingStochasticVisual.py
│   ├── SimulatedAnnealing.py
│   ├── GeneticAlgorithm.py
│   └── caseX.json      # Dataset uji (contoh: case1.json, case2.json, ...)
│
├── doc/                # Folder berisi laporan tugas besar (.pdf)
│   └── IF3070_T15_Tubes1.pdf
│
└── README.md           # File dokumentasi utama (ini)
```

---

## 📜 Project Overview
Proyek ini merupakan implementasi beberapa algoritma **Local Search** untuk menyelesaikan **Bin Packing Problem** — yaitu permasalahan optimasi dalam menempatkan sekumpulan barang ke dalam sejumlah kontainer berkapasitas tetap agar penggunaan ruang menjadi seefisien mungkin.

Algoritma yang diimplementasikan:
1. 🧱 **Steepest Ascent Hill-Climbing**
2. 🎲 **Stochastic Hill-Climbing**
3. 🔥 **Simulated Annealing**
4. 🧬 **Genetic Algorithm**

## 🏃‍♀️ How to Run

### 1️⃣ Environment Setup
Pastikan sudah menginstal **Python 3.8+** dan library berikut:
```bash
pip install matplotlib numpy
```

### 2️⃣ Running The Program
Pindah ke folder `src`:
```bash
cd src
```

Kemudian jalankan algoritma yang diinginkan, misalnya:
```bash
python3 HillClimbingSteepest.py case2.json
python3 HillClimbingStochastic.py case2.json
python3 SimulatedAnnealing.py case2.json
python3 GeneticAlgorithm.py case2.json
```
Jika tidak menuliskan nama file JSON, program akan otomatis menggunakan default (`case1.json` atau `case6.json` tergantung algoritma).

---

## 🧑‍💻 Task Distribution
| Anggota | Pekerjaan |
|----------|------------|
| **Samuel Chris Michael Bagasta S. (18223011)** | Visualisasi Steepest Hill-Climbing dan pembuatan laporan |
| **Stanislaus Ardy Bramantyo (18223057)** | Implementasi kode program dan visualisasi SA & GA|
| **Audy Alicia Renatha Tirayoh (18223097)** | Visualisasi Stochastic Hill-Climbing dan pembuatan laporan|

---
