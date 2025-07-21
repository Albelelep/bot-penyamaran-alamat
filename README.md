# Telegram Address Obfuscation Bot

Bot Telegram untuk menyamarkan alamat yang dimasukkan user dengan menggunakan koordinat palsu dan obfuscation text.

## Fitur

- Menerima input alamat dalam format: kelurahan, kecamatan, kabupaten, provinsi, kode pos, negara
- Validasi format input alamat
- Generate koordinat palsu (Plus Code style)
- Obfuscation alamat menggunakan leetspeak (a→4, e→3, i→1, o→0, s→5, t→7, g→9)
- Output dalam format quote Telegram
- Tombol "Generate Lagi" untuk membuat hasil baru

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Buat bot baru di Telegram:
   - Chat dengan @BotFather di Telegram
   - Gunakan command `/newbot`
   - Ikuti instruksi untuk membuat bot
   - Dapatkan token bot

3. Edit file `telegram_bot.py`:
   - Ganti `YOUR_BOT_TOKEN_HERE` dengan token bot yang didapat dari BotFather

4. Jalankan bot:
```bash
python telegram_bot.py
```

## Cara Penggunaan

1. Start bot dengan command `/start`
2. Bot akan menampilkan pesan selamat datang dan instruksi format
3. Kirim alamat dengan format: `kelurahan, kecamatan, kabupaten, provinsi, kode pos, negara`
4. Bot akan memberikan hasil berupa:
   - Koordinat palsu (Plus Code)
   - Alamat asli lengkap
   - Alamat yang disamarkan
5. Klik tombol "🔄 Generate Lagi" untuk membuat hasil baru

## Contoh

**Input:**
```
karet kuningan, setiabudi, jakarta selatan, dki jakarta, 12940, indonesia
```

**Output:**
```
L82A86JK+RG3R59, k4r37 kun1ng4n, 537143ud1, Jakarta Selatan, DKI Jakarta, 12940, Indonesia

...k4r37 kun1ng4n, 537143ud1
```

## Struktur Project

- `telegram_bot.py` - File utama bot
- `requirements.txt` - Dependencies Python
- `README.md` - Dokumentasi

## Catatan

- Koordinat yang dihasilkan adalah palsu/acak untuk keperluan obfuscation
- Bot tidak melibatkan transaksi finansial
- Obfuscation menggunakan pola leetspeak sederhana
