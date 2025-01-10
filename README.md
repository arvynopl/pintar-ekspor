# Pintar Ekspor Platform Edukasi

Platform edukasi yang menyediakan pengetahuan tentang perdagangan ekspor melalui kursus interaktif dan API yang ramah pengembang. Proyek ini dapat diakses melalui internet pada link berikut: [Pintar Ekspor](https://pintar-ekspor-frontend.vercel.app/)

## Gambaran Umum Arsitektur 🏗️

```mermaid
graph TD
    A[Frontend - React/TS] --> B[API Gateway - NGINX]
    B --> C[Backend - FastAPI]
    C --> D[(PostgreSQL DB)]
    C --> E[Layanan Email Eksternal]
    
    F[Pengembang Eksternal] --> B
    G[Pengguna Umum] --> A
```

## Fitur Utama 💡

### Untuk Pengguna Umum
- **Akses Kursus**: Pendaftaran diri di kursus
- **Pelacakan Kemajuan**: Pemantauan kemajuan pembelajaran personal
- **Konten Interaktif**: Interaksi dengan materi kursus

### Untuk Pengembang
- **API RESTful**: Integrasi fitur Pintar Ekspor ke aplikasi eksternal
- **Modul Analitik**: Pemanfaatan modul analitik untuk melakukan pemrosesan awal, analisis dengan model prediktif, dan visualisasi grafik pada dasbor
- **Notifikasi Otomatis**: Pemberitahuan tentang kunci API dan peningkatan peran melalui email yang didaftarkan di Pintar Ekspor

### Untuk Administrator
- **Manajemen Pengguna**: Pengaturan peran dan tingkat akses pengguna
- **Manajemen Konten**: Pembuatan dan perubahan konten kursus
- **Dasbor Analitik**: Pemantauan penggunaan platform oleh pengguna umum

## Panduan Integrasi API 🔌

### Autentikasi

```python
# Menghasilkan kunci API
POST /api/v1/developer/key
Authorization: Bearer <jwt_token>

# Gunakan kunci API dalam permintaan
GET /api/v1/analytics/course-progress
Authorization: ApiKey <your_api_key>
```

### Endpoint Utama

```typescript
// Endpoint analitik
GET /api/v1/analytics/user-progress
GET /api/v1/analytics/course-engagement
GET /api/v1/analytics/completion-rates

// Manajemen kursus
GET /api/v1/courses
POST /api/v1/courses/{course_id}/enroll
GET /api/v1/courses/{course_id}/progress
```

## Implementasi Teknis 🛠️

### Arsitektur Backend
- **FastAPI Framework**: Operasi asinkron, dokumentasi OpenAPI otomatis
- **SQLAlchemy ORM**: Operasi database yang aman tipe
- **JWT + Kunci API Auth**: Sistem autentikasi ganda
- **Model Pydantic**: Validasi permintaan/response

### Struktur Frontend
- **React + TypeScript**: Pengembangan komponen aman tipe
- **Context API**: Manajemen status global
- **Rute Terproteksi**: Kontrol akses berbasis peran
- **Desain Responsif**: Pendekatan mobile-first

### Skema Database

```mermaid
erDiagram
    User ||--o{ Progress : has
    User ||--o{ ApiKey : owns
    Course ||--o{ Progress : tracks
    Course ||--o{ Section : contains
    Section ||--o{ Content : includes
```

## Panduan Pengaturan Pengembangan 🔧

### Prasyarat
- Docker & Docker Compose
- Node.js 16+
- Python 3.8+
- PostgreSQL 13+

### Pengembangan Lokal

```bash
# Pengaturan Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Pengaturan Frontend
cd frontend
npm install
npm run dev
```

### Variabel Lingkungan

```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost:5432/pintar_ekspor
JWT_SECRET=your_secret
API_KEY_SALT=your_salt

# Frontend (.env)
VITE_API_URL=http://localhost:8000
VITE_ENV=development
```

## Deployment 🚀

### Pengaturan Produksi

```bash
# Build dan deploy
docker-compose -f docker-compose.prod.yml up -d

# Migrasi database
docker-compose exec backend alembic upgrade head
```

### Infrastruktur
- Frontend: Vercel deployment
- Backend: Railway hosting
- Database: Railway PostgreSQL
- Email: Integrasi FinTrackIt

## Pengembang Proyek
- Nama: Arvyno Pranata Limahardja  
- NIM: 18222007

## Kontributor Layanan Eksternal
- Nama: David Dewanto  
- NIM: 18222027  
- Platform: FinTrackIt  
- Layanan Eksternal yang Dimanfaatkan: Layanan Email

## Tentang Proyek 📚
Dikembangkan sebagai tugas universitas untuk mata kuliah II3160 Teknologi Sistem Terintegrasi. Pengembangan fokus pada pembuatan prototipe fungsional yang menunjukkan praktik pengembangan full stack web dan kemampuan integrasi API.
