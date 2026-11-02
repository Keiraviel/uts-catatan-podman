# Aplikasi Catatan (CRUD) — UTS: Container (Podman) + CI/CD

Aplikasi web CRUD sederhana (Python Flask + SQLite) yang di-deploy memakai **Podman**
dan otomatis lewat **CI/CD GitHub Actions**.

## Struktur Project
```
.
├── app/
│   ├── app.py              # Logika aplikasi (CRUD)
│   ├── wsgi.py             # Pintu masuk untuk gunicorn
│   └── templates/index.html# Tampilan web
├── tests/test_app.py       # Unit test (dipakai di CI)
├── Containerfile           # Resep membuat image (pengganti Dockerfile)
├── compose.yaml            # Jalankan pakai podman compose (opsional)
├── requirements.txt        # Library aplikasi
├── requirements-dev.txt    # Library untuk testing
└── .github/workflows/cicd.yml  # Pipeline CI/CD
```

## Tahap 1 — Install Podman
- **Ubuntu/Debian/WSL2**: `sudo apt update && sudo apt install -y podman`
- **Windows**: install *Podman Desktop* (https://podman-desktop.io), atau pakai WSL2 Ubuntu.
- **macOS**: `brew install podman && podman machine init && podman machine start`

Cek: `podman --version`

## Tahap 2 — Jalankan aplikasi langsung (tanpa container, untuk coba dulu)
```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
python -m pytest tests -v         # harus 4 passed
cd app
DB_PATH=./catatan.db flask --app wsgi run --port 5000
```
Buka http://localhost:5000

## Tahap 3 — Jalankan memakai Podman (container)
```bash
# 1. Build image
podman build -t catatan-app:latest -f Containerfile .

# 2. Jalankan container (port 8080 di komputer -> 5000 di container)
podman run -d --name catatan-app -p 8080:5000 -v catatan-data:/data catatan-app:latest

# 3. Cek
podman ps
curl http://127.0.0.1:8080/health
```
Buka http://127.0.0.1:8080

Perintah penting lain:
```bash
podman logs catatan-app        # lihat log
podman stop catatan-app        # hentikan
podman rm -f catatan-app       # hapus container
podman images                  # daftar image
```
Opsional dengan compose: `podman compose up -d --build`

Penjelasan `-v catatan-data:/data`: data SQLite disimpan di *volume* agar tidak hilang
walaupun container dihapus/di-deploy ulang.

## Tahap 4 — Upload ke GitHub
1. Buat repository baru di GitHub (contoh: `uts-catatan-podman`), **tanpa** README bawaan.
2. Di folder project:
```bash
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/USERNAME/uts-catatan-podman.git
git push -u origin main
```
3. Buka repo > **Settings > Actions > General > Workflow permissions** > pilih
   **Read and write permissions** > Save. (Wajib agar bisa push image ke GHCR.)

## Tahap 5 — CI (Continuous Integration) berjalan otomatis
Setiap `git push` ke `main`, job **ci** di `.github/workflows/cicd.yml` akan:
1. Mengambil kode
2. Install dependency
3. Menjalankan unit test
4. Build image dengan **podman build**
5. Smoke test (menjalankan container dan cek `/health`)
6. Push image ke GitHub Container Registry (`ghcr.io/USERNAME/REPO`)

Lihat hasilnya di tab **Actions** di GitHub (centang hijau = berhasil).

## Tahap 6 — CD (Continuous Deployment) dengan Self-Hosted Runner
Job **cd** berjalan di komputer/server kamu sendiri (yang ada Podman-nya) dan otomatis
menarik image terbaru lalu menjalankan ulang container.

Pasang runner (di Linux/WSL2 Ubuntu yang sudah ada Podman):
1. GitHub repo > **Settings > Actions > Runners > New self-hosted runner** > pilih Linux.
2. Jalankan perintah yang ditampilkan GitHub (download, `./config.sh ...`).
3. Jalankan runner: `./run.sh` (biarkan terminal terbuka saat demo).
   Pastikan `podman --version` dan `curl --version` berfungsi di mesin itu.

Setelah runner berstatus **Idle** (hijau), lakukan perubahan kecil lalu push:
```bash
# contoh: ubah judul di app/templates/index.html
git add .
git commit -m "ubah judul"
git push
```
Pipeline akan: test -> build -> push -> **deploy otomatis**. Buka http://127.0.0.1:8080
untuk melihat perubahan, dan `curl http://127.0.0.1:8080/health` akan menampilkan
`versi` berisi hash commit terbaru.

> Alternatif jika punya VPS: ganti job `cd` dengan langkah SSH ke VPS lalu jalankan
> `podman pull` dan `podman run` yang sama.

## Tahap 7 — Skenario demo video
**Video 1 (Container/Podman):** tunjukkan Containerfile -> `podman build` -> `podman run`
-> `podman ps` -> buka web -> demo tambah/edit/hapus catatan.

**Video 2 (CI/CD):** tunjukkan file `cicd.yml` -> ubah kode -> `git push` -> tab Actions
(ci lalu cd hijau) -> `podman ps` menunjukkan container baru -> web berubah otomatis.

## Troubleshooting
| Masalah | Solusi |
|---|---|
| Push image gagal `permission denied` | Aktifkan *Read and write permissions* (Tahap 4 poin 3) |
| Job `cd` menunggu terus (*Waiting for a runner*) | Runner belum jalan: jalankan `./run.sh` |
| `podman: command not found` di runner | Install podman di mesin runner |
| Port 8080 dipakai | Ganti `-p 8080:5000` jadi `-p 8081:5000` (di workflow dan perintah manual) |
| Pull image gagal `unauthorized` | Pastikan job cd punya langkah login (sudah ada) |
