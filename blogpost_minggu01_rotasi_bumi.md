# Metadata Blog Post (untuk Django Admin)
# ==========================================
# Title: Minggu 1: Fenomena Rotasi Bumi — Catatan Belajar Astronomi
# Slug: minggu-1-fenomena-rotasi-bumi
# Category: Astronomy
# Status: draft
# Content Type: markdown
# Excerpt: Bumi tidak pernah diam. Ia berputar pada porosnya setiap ~24 jam dan mengorbit Matahari setiap ~365.25 hari. Di minggu pertama belajar astronomi, kita menyelami konsep bola langit, sistem koordinat, dan bukti-bukti nyata bahwa Bumi berotasi.
# ==========================================

## Bumi Sebagai Planet dalam Tata Surya

Bumi adalah planet ketiga dari Matahari. Bumi tidak diam — ia melakukan dua gerakan utama: ==rotasi== (berputar pada porosnya, memakan waktu sekitar 24 jam) dan ==revolusi== (mengorbit Matahari, memakan waktu sekitar 365.25 hari).

Kedua gerakan ini bertanggung jawab atas hampir semua fenomena yang kita alami sehari-hari: siang-malam, pergantian musim, pergeseran rasi bintang sepanjang tahun, dan banyak lagi.

## Bola Bumi dan Geometri Bola

Bumi berbentuk mendekati bola, tapi sedikit pepat di kutub — bentuk ini disebut ==oblate spheroid==. Untuk astronomi posisi, kita perlu memahami beberapa konsep dasar geometri bola.

{size:large}**Titik-titik penting di Bumi:**{/size}

- **Kutub Utara & Kutub Selatan** — titik di mana sumbu rotasi Bumi menembus permukaan
- **Ekuator** — lingkaran besar yang membagi Bumi menjadi belahan utara dan selatan
- **Meridian** — lingkaran besar yang melewati kedua kutub
- **Lintang (latitude, φ)** — sudut dari ekuator ke utara (+) atau selatan (−), berkisar −90° sampai +90°. Bandung misalnya berada di lintang sekitar −6.9° (selatan ekuator)
- **Bujur (longitude, λ)** — sudut dari meridian Greenwich ke timur atau barat, berkisar −180° sampai +180°

## Kubah Langit — Bola Langit (Celestial Sphere)

Ini konsep yang sangat penting dalam astronomi. Bayangkan kamu berdiri di tengah lapangan terbuka dan melihat ke langit — langit tampak seperti kubah setengah bola yang menutupimu. Dalam astronomi, kita memperluas konsep ini menjadi ==bola langit penuh (celestial sphere)==: sebuah bola imajiner berukuran sangat besar, dengan Bumi di pusatnya, dan semua benda langit tampak "ditempelkan" di permukaan bola ini.

Tentu saja bola langit ini tidak nyata — bintang-bintang berada pada jarak yang sangat berbeda-beda. Tapi konsep ini sangat berguna karena memungkinkan kita membuat sistem koordinat untuk menentukan posisi benda langit.

{size:large}**Titik-titik penting di bola langit:**{/size}

- **Kutub Langit Utara (NCP)** — titik di bola langit tepat di atas Kutub Utara Bumi (dekat bintang Polaris)
- **Kutub Langit Selatan (SCP)** — titik di bola langit tepat di atas Kutub Selatan Bumi
- **Ekuator Langit (Celestial Equator)** — proyeksi ekuator Bumi ke bola langit
- **Ekliptika** — jalur semu Matahari di bola langit selama setahun (bidang orbit Bumi). Ekliptika membentuk sudut ==23.44°== terhadap ekuator langit — ini disebut **obliquitas ekliptika**, penyebab terjadinya musim!
- **Zenith** — titik tepat di atas kepala pengamat
- **Nadir** — titik tepat di bawah kaki pengamat (berlawanan dengan zenith)
- **Horizon** — lingkaran yang membatasi langit yang bisa dilihat

## Sistem Koordinat Langit

Ini bagian yang paling "matematis" di minggu pertama. Ada tiga sistem koordinat utama yang dipakai dalam astronomi.

### A. Sistem Koordinat Horizon (Horizontal/Altazimuth)

Sistem ini paling intuitif karena berbasis pada apa yang kamu lihat langsung dari posisimu.

- **Altitude (h)** — sudut dari horizon ke atas, 0° (di horizon) sampai 90° (zenith)
- **Azimuth (A)** — sudut diukur dari Utara searah jarum jam: Utara = 0°, Timur = 90°, Selatan = 180°, Barat = 270°

{color:orange}**Kelemahan sistem ini:**{/color} koordinat berubah terus karena Bumi berotasi, dan berbeda untuk setiap lokasi pengamat. Jadi kalau kamu bilang "bintang itu di altitude 45°, azimuth 90°" — itu hanya berlaku untuk lokasimu, pada waktu itu saja.

### B. Sistem Koordinat Ekuatorial

Ini sistem yang paling sering dipakai astronomer karena ==tidak bergantung pada lokasi dan waktu pengamat==.

- **Right Ascension (RA, α)** — analog bujur, diukur dalam jam (0h–24h) dari titik Vernal Equinox (titik Aries, ♈) searah berlawanan jarum jam
- **Declination (Dec, δ)** — analog lintang, diukur dalam derajat dari ekuator langit: +90° (NCP) sampai −90° (SCP)

Misalnya, bintang Polaris punya koordinat sekitar RA = 2h 31m, Dec = +89° 16' — artinya sangat dekat dengan Kutub Langit Utara.

### C. Sistem Koordinat Ekliptika

Berbasis bidang ekliptika (bidang orbit Bumi mengelilingi Matahari), bukan ekuator langit.

- **Lintang Ekliptika (β)** — sudut dari bidang ekliptika
- **Bujur Ekliptika (λ)** — sudut sepanjang ekliptika dari titik Vernal Equinox

Sistem ini berguna terutama untuk objek-objek tata surya karena planet-planet orbitnya mendekati bidang ekliptika.

## Bukti Bumi Berotasi

Bagaimana kita tahu Bumi berotasi? Ada beberapa bukti kuat.

### Ayunan Foucault (1851)

Léon Foucault menggantungkan pendulum besar (67 meter) di Panthéon, Paris. Pendulum berayun bolak-balik dalam bidang tetap, tapi lantai di bawahnya perlahan berputar! Dalam 24 jam, bidang ayunan tampak berputar. Kecepatan rotasi bidang ayunan bergantung pada lintang:

> **T = 24h / sin(φ)**, di mana φ adalah lintang pengamat.

Di kutub, bidang ayunan berputar 360° dalam 24 jam. Di ekuator, tidak berputar sama sekali.

Untuk Bandung (φ ≈ −6.9°): T = 24 / sin(6.9°) ≈ 24 / 0.12 ≈ ==200 jam== — sangat lambat! Itulah mengapa eksperimen Foucault sulit dilakukan di dekat ekuator.

### Trail Citra Bintang (Star Trails)

Kalau kamu membuka shutter kamera dengan exposure sangat lama (30 menit atau lebih) dan arahkan ke langit malam, bintang-bintang akan membentuk garis lengkung (trail). Bintang di dekat kutub langit membentuk lingkaran kecil, sementara bintang jauh dari kutub membentuk busur besar.

Ini adalah bukti visual bahwa Bumi berotasi — bukan langit yang berputar, melainkan kamera (dan Bumi) yang berputar.

### Efek Coriolis

Benda yang bergerak di permukaan Bumi mengalami pembelokan: ke kanan di belahan utara, ke kiri di belahan selatan. Ini mempengaruhi pola angin, arus laut, dan bahkan arah putaran siklon.

## Fenomena Siang dan Malam

Siang dan malam terjadi karena Bumi berotasi pada porosnya. Setengah Bumi yang menghadap Matahari mengalami siang, setengah yang membelakangi mengalami malam. Satu siklus penuh (siang + malam) disebut satu hari.

Ada dua definisi "hari" yang perlu kita pahami:

- ==Hari sideris== = 23 jam 56 menit 4 detik — waktu Bumi berotasi 360° tepat terhadap bintang
- ==Hari sinodis (hari Matahari)== = ~24 jam — waktu antara dua kali Matahari mencapai posisi tertinggi (transit meridian)

Mengapa berbeda sekitar 4 menit? Karena selama Bumi berotasi, Bumi juga bergerak sedikit dalam orbitnya mengelilingi Matahari (~1° per hari), sehingga Bumi perlu berotasi sedikit lebih dari 360° agar Matahari kembali ke posisi yang sama.

---

{size:large}**Versi Interaktif**{/size}

Mau eksplorasi materi ini dengan visualisasi dan quiz? Buka [versi interaktif lengkap di sini](https://ideasophia.com/courses/astronomi/minggu01_fenomena_rotasi_bumi.html) — ada simulasi bola langit, sistem koordinat, dan kuis untuk menguji pemahamanmu.

---

++Catatan ini adalah bagian dari seri belajar Astronomi A (AS6031) di IDEASOPHIA. Selamat belajar dan tetap memandang langit!++
