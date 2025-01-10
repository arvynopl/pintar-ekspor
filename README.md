# Pintar Ekspor Platform Edukasi

Platform edukasi yang menyediakan pengetahuan tentang perdagangan ekspor melalui kursus interaktif dan API yang ramah pengembang. <b>Proyek ini dapat diakses melalui internet pada link berikut: [Pintar Ekspor](https://pintar-ekspor-frontend.vercel.app/).</b>

## Catatan Khusus untuk Pemeriksa
Dimohon untuk <b>melakukan pencarian keyword 'Dokumentasi Arsitektur Pintar Ekspor' dengan Ctrl + F</b> supaya dimudahkan dalam melakukan pemeriksaan terhadap penjelasan komprehensif yang ditujukan untuk pembuatan laporan.

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

# Dokumentasi Arsitektur Teknik Pintar Ekspor

## Arsitektur Sistem Backend

Arsitektur backend menerapkan desain bertingkat yang menekankan pada keamanan, auditabilitas, dan skalabilitas. Berikut adalah penjelasan tentang setiap komponen:

### Lapisan Arsitektur Utama

```mermaid
graph TB
    subgraph "Pemrosesan Permintaan"
        A[Permintaan Klien] --> B[Proxy NGINX]
        B --> C[Middleware Pembatasan Laju]
        C --> D[Middleware Keamanan]
    end
    
    subgraph "Lapisan Autentikasi"
        D --> E[Autentikasi JWT]
        D --> F[Autentikasi Kunci API]
        E & F --> G[Validasi Peran]
    end
    
    subgraph "Layanan Inti"
        G --> H[Penangani Permintaan]
        H --> I[Logika Bisnis]
        I --> J[Akses Data]
    end
    
    subgraph "Lapisan Audit"
        J --> K[Logger Audit]
        K --> L[Penyimpanan Audit]
    end

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style D fill:#bbf,stroke:#333,stroke-width:2px
    style G fill:#bfb,stroke:#333,stroke-width:2px
    style K fill:#fbf,stroke:#333,stroke-width:2px
```

### Rincian Implementasi Keamanan

Sistem keamanan mengimplementasikan beberapa strategi autentikasi melalui antarmuka yang terintegrasi:

```python
class SecuritySystem:
    """
    Implementasi keamanan terpadu dengan:
    - Token JWT untuk pengguna web
    - Kunci API untuk pengembang
    - Kontrol akses berbasis peran
    - Pembatasan laju
    - Pencatatan audit
    """
    
    async def authenticate_request(request) -> User:
        # Alur autentikasi utama
        if jwt_token := get_jwt_token(request):
            return await validate_jwt(jwt_token)
        elif api_key := get_api_key(request):
            return await validate_api_key(api_key)
        raise AuthenticationError()

    async def validate_permissions(user: User, required_roles: List[UserRole]):
        if not user.role in required_roles:
            audit_logger.log_access_denied(user.id)
            raise PermissionError()
```

### Arsitektur Rate Limiting

Sistem rate limiting menggunakan algoritma sliding window dengan batasan yang berbeda untuk berbagai endpoint:

```python
RATE_LIMITS = {
    "general": (100, 60),     # 100 permintaan per menit
    "auth": (20, 60),         # 20 permintaan per menit
    "api": (1000, 3600)       # 1000 permintaan per jam
}
```

Sistem ini melacak permintaan menggunakan pendekatan berbasis waktu:

```mermaid
sequenceDiagram
    participant C as Klien
    participant R as Pembatas Laju
    participant B as Backend
    
    C->>R: Permintaan
    R->>R: Periksa Jendela
    alt Jendela Penuh
        R-->>C: 429 Terlalu Banyak Permintaan
    else Jendela Tersedia
        R->>B: Teruskan Permintaan
        B-->>C: Respons
        R->>R: Perbarui Penghitung
    end
```

### Arsitektur Sistem Audit

Sistem audit menangkap semua perubahan data dengan konteks yang rinci:

```mermaid
graph TD
    A[Operasi Database] --> B{Pemicu Audit}
    B --> C[Menangkap Perubahan]
    C --> D[Mencatat Konteks]
    D --> E[Menyimpan Log Audit]
    
    subgraph "Konteks Audit"
        F[ID Pengguna]
        G[Alamat IP]
        H[Stempel Waktu]
        I[Tipe Operasi]
    end
    
    D --> F & G & H & I
```

Log audit mencatat:
- Pengguna yang melakukan tindakan
- Alamat IP
- Stempel waktu
- Jenis operasi (INSERT/UPDATE/DELETE)
- Nilai lama dan baru
- Tabel dan pengidentifikasi rekaman

## Gambaran Umum Arsitektur Sistem

Platform ini menggunakan arsitektur yang terinspirasi oleh microservices, yang dirancang untuk skalabilitas dan pemeliharaan yang baik. Berikut adalah rincian setiap komponen:

```mermaid
graph TB
    subgraph "Lapisan Frontend"
        A[UI React] --> B[Manajemen Status]
        B --> C[Klien API]
    end
    
    subgraph "API Gateway"
        D[Proxy Terbalik NGINX]
    end
    
    subgraph "Layanan Backend"
        E[Aplikasi FastAPI]
        F[Layanan Autentikasi]
        G[Layanan Kursus]
        H[Layanan Analitik]
        I[Layanan Email]
    end
    
    subgraph "Lapisan Data"
        J[(Database PostgreSQL)]
    end
    
    C --> D
    D --> E
    E --> F & G & H & I
    F & G & H & I --> J
    
    subgraph "Layanan Eksternal"
        K[API Email FinTrackIt]
    end
    
    I --> K
```

## Rincian Integrasi Komponen

### Arsitektur Frontend

Implementasi frontend mengikuti pola arsitektur berbasis fitur dengan penekanan kuat pada keamanan autentikasi dan pemeliharaan status secara global.

### Manajemen Status dan Autentikasi

Aplikasi menggunakan React Context untuk manajemen status global, dengan fokus pada status autentikasi:

```mermaid
graph TD
    A[AuthProvider] --> B[Manajemen JWT]
    A --> C[Manajemen Peran]
    A --> D[Manajemen Kunci API]
    
    B --> E[Penyimpanan Token]
    B --> F[Segarkan Token]
    
    C --> G[Validasi Peran]
    C --> H[Periksa Izin]
    
    D --> I[Generasi Kunci]
    D --> J[Penyimpanan Kunci]
    
    subgraph "Komponen Aplikasi"
        K[Rute yang Dilindungi]
        L[Penjaga Peran]
        M[Klien API]
    end
    
    A --> K & L & M
```

### Lapisan Integrasi API

Lapisan integrasi API mengimplementasikan sistem penanganan permintaan yang kuat dengan pembaruan otomatis token dan manajemen kesalahan:

```mermaid
sequenceDiagram
    participant C as Komponen
    participant A as Klien API
    participant I as Interseptor
    participant S as Server
    
    C->>A: Buat Permintaan
    A->>I: Proses Permintaan
    I->>I: Tambahkan Header Auth
    I->>S: Kirim Permintaan
    
    alt Token Kedaluwarsa
        S-->>I: Respons 401
        I->>I: Segarkan Token
        I->>S: Ulangi Permintaan
    end
    
    S-->>C: Respons/Kesalahan
```

Implementasi ini memiliki penanganan kesalahan yang canggih dan pengelolaan token:

```typescript
// Klien API dengan interceptor
export const api = axios.create({
    baseURL: normalizeURL(import.meta.env.VITE_API_URL),
    headers: {
        'Content-Type': 'application/json',
    },
});
```

### Arsitektur Komponen

Arsitektur komponen mengimplementasikan sistem perlindungan hierarkis dengan:

```mermaid
graph TD
    A[Akar Aplikasi] --> B[Router]
    B --> C[Layout]
    C --> D[Rute Dilindungi]
    C --> E[Rute Publik]
    
    D --> F[Penjaga Peran]
    F --> G[Komponen Fitur]
    
    G --> H[Dasbor Analitik]
    G --> I[Manajemen Kursus]
    G --> J[Manajemen Profil]
    
    subgraph "Fitur yang Dilindungi"
        H
        I
        J
    end
```

### Autentikasi dan Proses Otorisasi

Sistem mengimplementasikan mekanisme autentikasi ganda yang menangani autentikasi berbasis JWT untuk pengguna web dan kunci API untuk pengembang.

```mermaid
sequenceDiagram
    participant C as Klien
    participant M as Middleware
    participant A as Layanan Autentikasi
    participant D as Database
    participant E as Layanan Email
    
    C->>M: Permintaan dengan Auth
    
    alt Autentikasi JWT
        M->>A: Validasi JWT
        A->>D: Periksa Pengguna & Peran
        D-->>A: Data Pengguna
        A-->>M: Konteks Pengguna
    else Autentikasi Kunci API
        M->>A: Validasi Kunci API
        A->>D: Periksa Status Pengembang
        D-->>A: Data Pengembang
        A-->>M: Konteks Pengembang
    end
    
    alt Pembaruan Peran
        C->>A: Permintaan Peran Pengembang
        A->>D: Pembaruan Peran Pengguna
        A->>A: Generasi Kunci API
        A->>E: Kirim Pemberitahuan Email
        A-->>C: Kembalikan Kunci API
    end
    
    alt Segarkan Token
        C->>A: Segarkan Token
        A->>D: Validasi Token Segarkan
        D-->>A: Token Valid
        A->>A: Buat Token Baru
        A-->>C: Token Akses + Segarkan
    end
```

### Arsitektur Skema Database

```mermaid
erDiagram
    User {
        uuid id PK
        string email
        string hashed_password
        enum role
        timestamp created_at
    }
    
    Course {
        uuid id PK
        string title
        text description
        json content
        timestamp created_at
    }
    
    Progress {
        uuid id PK
        uuid user_id FK
        uuid course_id FK
        json completion_data
        timestamp last_accessed
    }
    
    Analytics {
        uuid id PK
        uuid user_id FK
        uuid course_id FK
        json metrics
        timestamp recorded_at
    }
    
    User ||--o{ Progress : tracks
    User ||--o{ Analytics : generates
    Course ||--o{ Progress : has
    Course ||--o{ Analytics : provides
```

### Integrasi Layanan Email

Untuk layanan email, kami mengintegrasikan dengan API FinTrackIt dan mengembangkan sistem manajemen token dan penanganan kesalahan. Implementasi ini memastikan pengiriman email dengan mekanisme pembaruan token otomatis dan retry:

```mermaid
graph TD
    A[Email Request] --> B{Valid Token?}
    B -->|Yes| C[Send Email]
    B -->|No| D[Request New Token]
    D --> E{Token Obtained?}
    E -->|Yes| C
    E -->|No| F[Raise Error]
    C -->|Success| G[Return Success]
    C -->|Failure| H{Token Expired?}
    H -->|Yes| D
    H -->|No| F

    style B fill:#f9f,stroke:#333,stroke-width:2px
    style E fill:#bbf,stroke:#333,stroke-width:2px
    style H fill:#bfb,stroke:#333,stroke-width:2px
```

Implementasi ini memiliki manajemen token dan penanganan kesalahan:

```python
class EmailService:
    def __init__(self):
        self.auth_base_url = "https://api.fintrackit.my.id/v1/auth"
        self.email_base_url = "https://api.fintrackit.my.id/v1/secure"
        self.api_key = settings.FINTRACKIT_API_KEY
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None

    async def _get_access_token(self) -> str:
        if self._access_token and self._token_expiry and datetime.now() < self._token_expiry:
            return self._access_token
        headers = {"X-API-Key": self.api_key}
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.auth_base_url}/token", headers=headers, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                self._access_token = data["access_token"]
                self._token_expiry = datetime.now() + timedelta(minutes=55)
                return self._access_token

    async def send_api_key_notification(self, user_email: str, api_key: str, expiry_date: Optional[str] = None) -> bool:
        try:
            token = await self._get_access_token()
            if not token:
                raise EmailServiceError("Could not obtain access token")
            subject = "Your Pintar Ekspor API Key"
            body = self._generate_api_key_email(api_key, expiry_date)
            return await self._send_email(user_email, subject, body)
        except Exception as e:
            logger.error(f"Email service error: {str(e)}")
            raise EmailDeliveryFailed("Failed to send API key notification")
```

Fitur utama layanan email:
1. **Manajemen Token**: Pembaruan otomatis, caching token, penanganan kedaluwarsa.
2. **Penanganan Kesalahan**: Mekanisme retry, pencatatan kesalahan, penanganan kegagalan.
3. **Fitur Keamanan**: Penyimpanan token yang aman, komunikasi HTTPS, perlindungan kunci API.

```python
class EmailService:
    def __init__(self, api_key: str, base_url: str):
        self.client = FinTrackItClient(api_key, base_url)
        self.token_cache = TokenCache()
    
    async def send_developer_notification(self, email: str, event_type: str):
        try:
            token = await self.token_cache.get_token()
            if not token:
                token = await self.client.refresh_token()
                await self.token_cache.set_token(token)
            template = self.get_notification_template(event_type)
            await self.client.send_email(email, template, token)
        except TokenExpiredError:
            token = await self.client.refresh_token()
            await self.token_cache.set_token(token)
            await self.send_developer_notification(email, event_type)
        except EmailServiceError as e:
            logger.error(f"Email service error: {str(e)}")
            raise EmailDeliveryFailed(f"Failed to send {event_type} notification")
```

### Arsitektur Layanan Analitik

Layanan analitik mengimplementasikan pipeline pemrosesan data yang komprehensif dengan penanganan kesalahan dan validasi data. Berikut alur data dalam sistem:

```mermaid
graph TD
    A[Data Upload] --> B[Data Handler]
    B --> C[Data Cleaner]
    C --> D[Data Transformer]
    D --> E[Analytics Processor]
    E --> F[Results Generator]
    
    subgraph "Data Validation"
        B --> G[Format Check]
        B --> H[Schema Validation]
        B --> I[Size Validation]
    end
    
    subgraph "Data Processing"
        C --> J[Missing Data Handler]
        C --> K[Outlier Detection]
        C --> L[Data Normalization]
    end
    
    subgraph "Analytics Pipeline"
        E --> M[Trend Analysis]
        E --> N[Growth Metrics]
        E --> O[Forecasting]
    end

    style B fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#bbf,stroke:#333,stroke-width:2px
    style E fill:#bfb,stroke:#333,stroke-width:2px
```

Implementasi ini memiliki penanganan data dan analisis:

1. **Pipeline Pemrosesan Data**
```python
class DataHandler:
    async def process_upload(self, file: Union[UploadFile, io.BytesIO], input_format: str = None) -> Dict[str, pd.DataFrame]:
        try:
            if not input_format:
                input_format = self._detect_format(getattr(file, 'filename', ''))
            if input_format == 'csv':
                return self._process_csv(content)
            elif input_format == 'json':
                return self._process_json(content)
            else:
                raise ValueError(f"Unsupported format: {input_format}")
```

2. **Perhitungan Analitik**
```python
class DataAnalytics:
    def analyze_pair(self, df: pd.DataFrame, include_forecast: bool = True) -> AnalyticsResults:
        try:
            basic_stats = self._calculate_basic_stats(df)
            trend_analysis = self._analyze_trend(df)
            growth_metrics = self._calculate_growth_metrics(df)
            forecast = None
            if include_forecast:
                forecast = self._generate_forecast(df)
            return AnalyticsResults(trend_analysis=trend_analysis, growth_metrics=growth_metrics, basic_stats=basic_stats, forecast=forecast)
```

3. **Keamanan dan Validasi**
```python
def _safe_numeric(self, value: Any) -> Optional[float]:
    try:
        if pd.isna(value) or value is None:
            return None
        value = float(value)
        if np.isnan(value) or np.isinf(value):
            return None
        if abs(value) > self.config['numeric_limits']['max_value']:
            logger.warning(f"Value {value} exceeds safe limits")
            return None
        return value
    except (TypeError, ValueError) as e:
        logger.warning(f"Error converting numeric value: {str(e)}")
        return None
```

4. **Penanganan Kesalahan dan Pencatatan**
```python
class AnalyticsError(Exception):
    def __init__(self, message: str, details: Optional[Dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

@router.post("/analyze")
async def analyze_data(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_authenticated_user), include_forecast: bool = Query(True), include_visualizations: bool = Query(False), export_format: Optional[str] = Query(None, regex="^(csv|json)$")):
    try:
        pair_dataframes = await process_with_timeout(data_handler.process_upload(file))
        await asyncio.to_thread(audit_logger.log_change, action="ANALYZE_DATA", table_name="analytics_data", user_id=current_user.id, ip_address=request.client.host)
        response_data = _safe_json_response(analysis_results)
        return JSONResponse(content=response_data)
    except AnalyticsError as e:
        logger.error(f"Analytics error: {e.message}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": e.message, "details": e.details})
```

Layanan analitik menyediakan:
- Validasi dan pembersihan data yang kuat
- Penanganan kesalahan komprehensif
- Pemrosesan numerik yang aman
- Pencatatan audit
- Perlindungan waktu habis
- Pemrosesan berbasis format
- Pilihan ekspor ganda

### Arsitektur Deployment

Arsitektur deployment mengutamakan keamanan, keandalan, dan skalabilitas di berbagai layanan cloud.

### Tata Letak Infrastruktur Cloud

```mermaid
graph TD
    subgraph "Pengiriman Konten"
        A[Vercel Edge Network] --> B[Frontend Static Assets]
    end
    
    subgraph "Lapisan API"
        C[NGINX Proxy] --> D[Railway Load Balancer]
        D --> E[FastAPI Containers]
    end
    
    subgraph "Lapisan Database"
        E --> F[Railway PostgreSQL]
        F --> G[Backup Service]
    end
    
    subgraph "Layanan Eksternal"
        E --> H[FinTrackIt Email]
    end
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#bbf,stroke:#333,stroke-width:2px
    style F fill:#bfb,stroke:#333,stroke-width:2px
```

### Konfigurasi Kontainer

Konfigurasi Docker produksi menekankan pada keamanan dan kinerja:

```dockerfile
# Implementasi Dockerfile produksi
FROM python:3.11-slim

# Setel variabel lingkungan untuk optimasi
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install hanya dependensi sistem yang diperlukan
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Buat pengguna non-root untuk keamanan
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Perintah untuk menjalankan aplikasi dengan beberapa worker
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4
```

### Orkestrasi Layanan

Layanan produksi diorkestrasi menggunakan Docker Compose dengan alokasi sumber daya yang efisien:

```yaml
version: '3.8'
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    ports:
      - "${PORT}:${PORT}"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - JWT_ALGORITHM=${JWT_ALGORITHM}
      - ENV=production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:${PORT}/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 1G
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Konfigurasi NGINX

Konfigurasi NGINX mengimplementasikan langkah-langkah keamanan yang kuat dan penanganan permintaan yang efisien:

```nginx
server {
    listen 443 ssl;
    server_name api.your-domain.com;

    # Konfigurasi SSL dengan pengaturan keamanan modern
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:
                ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # Header Keamanan
    add_header Strict-Transport-Security "max-age=31536000" always;
    
    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # Konfigurasi CORS
        add_header 'Access-Control-Allow-Origin' 
                  'https://your-frontend-domain.com' always;
        add_header 'Access-Control-Allow-Methods' 
                  'GET, POST, PUT, DELETE, OPTIONS' always;
    }
}
```

### Proses Deployment

```mermaid
sequenceDiagram
    participant D as Developer
    participant G as GitHub
    participant CI as GitHub Actions
    participant V as Vercel
    participant R as Railway
    
    D->>G: Push ke main
    G->>CI: Memicu workflow
    
    par Deployment Frontend
        CI->>V: Membangun frontend
        V->>V: Menjalankan tes
        V->>V: Deploy ke edge
    and Deployment Backend
        CI->>R: Membangun kontainer
        R->>R: Menjalankan migrasi
        R->>R: Deploy layanan
    end
```

### Konfigurasi Railway Deployment

Konfigurasi Railway disiapkan untuk kinerja yang optimal:

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "backend/Dockerfile.prod"

[deploy]
startCommand = "bash scripts/railway_deploy.sh"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 5
```

Proses deployment mencakup beberapa langkah otomatis:

```bash
#!/bin/bash
# Implementasi railway_deploy.sh

echo "Memulai proses deployment..."

# Migrasi database
python scripts/init_db.py

# Pengaturan keamanan
bash scripts/setup_firewall.sh

# Menyalakan aplikasi dengan pengaturan produksi
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} \
    --workers 4 --proxy-headers --forwarded-allow-ips='*'
```

### Langkah-langkah Keamanan

```mermaid
graph TD
    A[Lapisan Keamanan] --> B[Keamanan Jaringan]
    A --> C[Keamanan Aplikasi]
    A --> D[Keamanan Data]
    
    B --> E[SSL/TLS]
    B --> F[Aturan Firewall]
    B --> G[Kebijakan CORS]
    
    C --> H[Validasi JWT]
    C --> I[Rate Limiting]
    C --> J[Sanitisasi Input]
    
    D --> K[Enkripsi di Rest]
    D --> L[Backup Aman]
    D --> M[Kendali Akses]
```

Konfigurasi firewall mengimplementasikan pertahanan berlapis:

```bash
# Implementasi pengaturan firewall
# Reset UFW ke default
sudo ufw --force reset

# Kebijakan default
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Izinkan layanan tertentu
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https

# Pembatasan akses database
sudo ufw allow from 127.0.0.1 to any port 5432

# Pembatasan untuk SSH
sudo ufw limit ssh/tcp
```

### Pemantauan dan Pemeliharaan

Lingkungan produksi mengimplementasikan pemantauan yang komprehensif:

1. **Health Checks**
   - Pengujian endpoint secara teratur
   - Pemantauan koneksi database
   - Pelacakan penggunaan sumber daya

2. **Strategi Logging**
   - Logging terstruktur dalam format JSON
   - Rotasi log
   - Pelacakan kesalahan

3. **Prosedur Backup**
   - Backup database otomatis
   - Backup konfigurasi
   - Perencanaan pemulihan bencana

4. **Prosedur Skalabilitas**
   - Kemampuan untuk melakukan scaling horizontal
   - Konfigurasi load balancer
   - Pengelolaan alokasi sumber daya

Arsitektur ini memastikan operasi yang efektif sekaligus mampu mempertahankan keamanan dan kinerja di lingkungan produksi.

```mermaid
graph TB
    subgraph "Lingkungan Produksi"
        A[Vercel - Frontend]
        B[Railway - Backend]
        C[Railway - PostgreSQL]
        D[FinTrackIt - Email]
    end
    
    subgraph "CI/CD Pipeline"
        E[GitHub Actions]
        F[Docker Build]
        G[Automated Tests]
        H[Deployment]
    end
    
    E --> F
    F --> G
    G --> H
    H --> A & B
    B --> C
    B --> D
```

### Konfigurasi Produksi

Lingkungan produksi dikonfigurasi menggunakan Docker Compose:

```yaml
version: '3.8'
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - JWT_SECRET=${JWT_SECRET}
      - EMAIL_API_KEY=${EMAIL_API_KEY}
    depends_on:
      - db
    networks:
      - app-network

  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=${DB_NAME}
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  postgres_data:
```

## Pemantauan dan Penanganan Kesalahan

Strategi penanganan kesalahan mengikuti pendekatan hierarkis:

```mermaid
graph TD
    A[Kegagalan Aplikasi] --> B{Tipe Kesalahan}
    B -->|API| C[API Error Handler]
    B -->|Database| D[DB Error Handler]
    B -->|Autentikasi| E[Auth Error Handler]
    B -->|Email| F[Email Error Handler]
    
    C & D & E & F --> G[Error Logger]
    G --> H[Monitoring Service]
```

### Pemantauan Kinerja

Metode yang dipantau di seluruh layanan:

1. Waktu Respons API
2. Kinerja Kuery Database
3. Tingkat Keberhasilan Autentikasi
4. Tingkat Keberhasilan Pengiriman Email

## Langkah-langkah Keamanan

Keamanan diimplementasikan pada berbagai level:

1. **Tingkat Jaringan**
   - Penegakan HTTPS
   - Konfigurasi CORS
   - Pembatasan laju (rate limiting)

2. **Tingkat Aplikasi**
   - Validasi token JWT
   - Autentikasi API key
   - Kontrol akses berbasis peran

3. **Tingkat Database**
   - Prepared statements
   - Pooling koneksi
   - Enkripsi data sensitif

## Pertimbangan Skalabilitas

Arsitektur ini dirancang untuk skalabilitas horizontal:

1. **Backend Stateless**
   - Memungkinkan banyak instansi
   - Load balancer siap

2. **Strategi Caching**
   - Redis untuk data sesi
   - Caching hasil kuery
   - Caching aset statis

3. **Optimisasi Database**
   - Optimisasi indeks
   - Penyempurnaan kinerja kuery
   - Pooling koneksi
