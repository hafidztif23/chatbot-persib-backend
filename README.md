# MaungBot — Chatbot Customer Service Berbasis RAG dari Persib Bandung

MaungBot adalah sistem chatbot customer service berbasis **Retrieval-Augmented
Generation (RAG)** untuk layanan digital Persib Bandung. Proyek ini merupakan
Tugas Akhir KoTA-110 D3-Teknik Informatika Politeknik Negeri Bandung
dan terdiri dari dua bagian utama dalam satu repository:

- **Frontend** — antarmuka chat berbasis web (React + Vite)
- **Backend** — REST API, pipeline RAG, autentikasi, dan manajemen knowledge
  base (FastAPI + PostgreSQL/pgvector)

## Fitur Utama

- Chat dengan deteksi intent (jadwal pertandingan, info pemain, merchandise,
  tiket, keanggotaan MemberSIB/Passport, regulasi Stadion GBLA, sejarah &
  prestasi klub)
- Pipeline RAG (LangChain + pgvector + Hugging Face Inference API)
- Auto-update knowledge base via file watcher (`watchdog`)
- Autentikasi JWT (bcrypt) dengan tingkatan membership (reguler / MemberSIB /
  Passport Persib)
- Riwayat percakapan per akun
- Mekanisme fallback & eskalasi otomatis ke tim Customer Service
- Dashboard untuk tim CS menangani tiket eskalasi

## Tech Stack

**Frontend**
- React 19 + Vite
- React Router

**Backend**
- FastAPI + SQLAlchemy
- PostgreSQL + ekstensi `pgvector`
- LangChain (`langchain-huggingface`)
- Sentence-Transformers (`all-MiniLM-L6-v2`) untuk embedding
- LLM: Qwen2.5-7B-Instruct (Hugging Face Inference API) / GPT-4o mini
- Autentikasi: JWT (`python-jose`) + `bcrypt`

**Infrastruktur**
- Docker (Cloud Run)
- Google Cloud Storage (sinkronisasi dokumen knowledge base)
- Firebase Hosting (frontend)
- CI/CD via GitHub Actions

## Struktur Project

```
.
├── src/                  # Frontend (React)
│   ├── components/
│   ├── pages/
│   ├── services/
│   └── styles/
├── core/                 # Backend - logic inti
│   ├── db.py
│   ├── rag.py
│   ├── embeddings.py
│   ├── intents.py
│   ├── memory.py
│   ├── security.py
│   └── ...
├── routes/               # Backend - REST API endpoints
│   ├── chat.py
│   ├── auth.py
│   ├── jadwal.py
│   ├── pemain.py
│   ├── ticket.py
│   ├── eskalasi.py
│   └── ...
├── docs/                 # Knowledge base (PDF/DOCX/TXT) untuk RAG
├── intents.json          # Definisi intent & contoh kalimat
├── main.py                # Entry point backend (FastAPI)
├── requirements.txt       # Dependencies backend
├── package.json           # Dependencies frontend
├── Dockerfile
└── .env.example
```

## Menjalankan Secara Lokal

### 1. Backend (FastAPI)

```bash
# buat virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# install dependencies
pip install -r requirements.txt

# jalankan server
uvicorn main:app --reload --port 8000
```

API akan berjalan di `http://localhost:8000`.

### 2. Frontend (React + Vite)

```bash
npm install
npm run dev
```

Frontend akan berjalan di `http://localhost:3000` (lihat `vite.config.js`).

## Konfigurasi Environment

Salin `.env.example` menjadi `.env` dan sesuaikan nilainya. Variabel utama
yang dibutuhkan backend:

| Variabel | Keterangan |
|---|---|
| `DATABASE_URL` | Connection string PostgreSQL (atau gunakan `INSTANCE_CONNECTION_NAME` + `DB_USER`/`DB_PASSWORD`/`DB_NAME` untuk Cloud SQL) |
| `HUGGINGFACEHUB_API_TOKEN` | API token Hugging Face untuk LLM & embedding |
| `JWT_SECRET_KEY` | Secret key untuk JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Lama masa berlaku token (default 60) |
| `API_BASE_URL` | Base URL backend (digunakan oleh `core/api_client.py`) |
| `CHATBOT_NAME` | Nama persona chatbot (default: "Asisten Persib") |
| `GCS_BUCKET_NAME` | Nama bucket GCS tempat dokumen knowledge base disimpan |

Variabel utama yang dibutuhkan frontend:

| Variabel | Keterangan |
|---|---|
| `VITE_API_URL` | URL backend API (contoh: `http://localhost:8000`) |
| `VITE_APP_NAME` | Nama aplikasi |

## Knowledge Base & RAG

Dokumen sumber (PDF/DOCX/TXT/XLSX) ditempatkan pada folder `docs/`. Saat
backend dijalankan:

1. Dokumen disinkronkan dari Google Cloud Storage (`core/storage.py`)
2. Setiap dokumen di-chunk dan diubah menjadi embedding (`core/embeddings.py`)
3. Embedding disimpan ke tabel `document_embeddings` (PostgreSQL + pgvector)
4. `core/docs_watcher.py` memantau folder `docs/` untuk update otomatis saat
   ada file baru, berubah, atau dihapus

## Deployment

- Backend: Docker image → Google Cloud Run (lihat `.github/workflows/deploy.yml`)
- Frontend: build Vite → Firebase Hosting

## Status

Project ini masih dalam pengembangan sebagai bagian dari Tugas Akhir.
