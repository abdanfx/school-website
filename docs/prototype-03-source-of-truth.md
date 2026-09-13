# PROTOTYPE 03 — IMPLEMENTATION SOURCE-OF-TRUTH PACK v1.0

Status: AUTHORITATIVE FOR IMPLEMENTATION
Project: school-web-prot-003
Homepage prototype: PROTOTYPE 03 — MINIMAL QURANIC FUTURE

---

## 1) IMPLEMENTATION PURPOSE

This document is the authoritative local source-of-truth for implementing the approved Prototype 03 homepage inside `school-web-prot-003`.

Use this file as the implementation reference for:
- final homepage information architecture
- final homepage section order
- homepage content copy
- selected photograph mapping
- navigation mapping
- CTA mapping
- footer content
- implementation guardrails

Do not redesign Prototype 03.
Do not change the approved homepage architecture.
Do not introduce new homepage sections beyond those listed here.
Do not convert the homepage into a card-heavy layout.
Do not add a large Berita/News homepage section.

---

## 2) LOCKED HOMEPAGE SECTION ORDER

Homepage section order is locked as:

1. Hero
2. School Profile / Profil Sekolah
3. Three Educational Pillars / Tiga Pilar Pendidikan
4. Qur'an × Technology
5. Capaian Tahfizh
6. Kehidupan di Pondok Pesantren
7. PPDB
8. Footer

Narrative flow must remain:

Arrival → Institution → Education → Differentiation → Evidence → Human Experience → Action → Institutional Close

---

## 3) LOCKED VISUAL / UX DIRECTION

Preserve the approved Prototype 03 direction:

- modern, minimalist, professional
- “Minimal Quranic Future”
- strong editorial feeling, not template-like
- dark Hero
- lighter warm Profile / Programs
- dark Qur'an × Technology signature section
- lighter evidence / life sections
- deep emerald PPDB close
- dark institutional footer
- Plus Jakarta Sans as the production typeface
- authentic photography as primary visual material
- restrained cyan accents, mainly in Qur'an × Technology
- no gold/amber as a core system color
- no card-everything design
- controlled asymmetry on desktop
- strong mobile readability
- accessibility-conscious implementation
- performance-first implementation

---

## 4) PHOTO SOURCE MAPPING (AUTHORITATIVE)

The approved selected source files are:

### Hero
- `1000534854.jpg`

### Profile
- `1000512148.jpg`

### Three Educational Pillars
- Program 01: `1000160830.jpg`
- Program 02: `1000520096.jpg`
- Program 03: `1000163805.jpg`

### Qur'an × Technology
- `1000344565.jpg`

### Kehidupan di Pondok Pesantren
- `1000512176.jpg`
- `1000512147.jpg`
- `1000213703.jpg`

### Archive / Reserve
- `IMG-20221202-WA0016.jpg`

Implementation note:
- The above file mapping is authoritative.
- Use these files as the approved prototype source pool.
- The reserve/archive photo is optional backup material and should not displace the approved primary mapping unless implementation necessity requires a safe fallback.

---

## 5) PRIMARY NAVIGATION MAPPING

Primary homepage navigation should prioritize the homepage sections and user flow.

Use the following main navigation structure:

- Beranda
- Profil
- Program
- Kehidupan
- PPDB
- Kontak

Expected behavior:
- `Beranda` → top of homepage
- `Profil` → `#profil`
- `Program` → `#program`
- `Kehidupan` → `#kehidupan`
- `PPDB` → `#ppdb`
- `Kontak` → footer/contact area or existing contact page depending shared implementation pattern

### Informasi mapping
Do not create a major homepage “Informasi” or “Berita” section.

If a shared navigation/footer implementation still needs a text link labeled `Informasi`, map it to:
- `about.html`

This resolves the “Informasi” internal-page mapping without promoting it into a major homepage content block.

---

## 6) HERO — FINAL CONTENT

### Eyebrow / institutional context
`Pondok Pesantren Daarul Quran Fantastis Pusat`

### Primary visible identity / H1
`SMP Tahfizh Quran Fantastis`

### Tagline / value proposition
`Membangun Generasi Qurani dan Melek Teknologi`

### Supporting paragraph
`SMP Tahfizh Quran Fantastis menghadirkan pendidikan menengah berbasis pondok pesantren yang memadukan tahfizh Al-Qur'an, pembelajaran akademik, dan pembinaan karakter dalam lingkungan belajar yang terarah, hangat, dan bertumbuh.`

### CTA group
Primary CTA:
`Daftar Sekarang`

Primary CTA destination:
- `#ppdb`
- In the PPDB section, the conversion CTA should continue to WhatsApp.

Secondary CTA:
`Pelajari Lebih Lanjut`

Secondary CTA destination:
- `#profil`

### Hero image
Use:
- `1000534854.jpg`

### Hero implementation note
Desktop:
- left = text content
- right = authentic image

Mobile:
- navigation integrated into Hero
- content order:
  1. eyebrow
  2. H1
  3. tagline
  4. supporting paragraph
  5. CTA group
  6. Hero photo

---

## 7) PROFILE / PROFIL SEKOLAH — FINAL CONTENT

### Section label / eyebrow
`Profil Sekolah`

### Heading
`Mengenal SMP Tahfizh Quran Fantastis`

### Body copy
`SMP Tahfizh Quran Fantastis adalah sekolah menengah berbasis pondok pesantren yang tumbuh untuk membantu siswa belajar, menghafal Al-Qur'an, dan berkembang sebagai pribadi yang berilmu, beradab, dan siap menghadapi masa depan.`

`Sebagai bagian dari Pondok Pesantren Daarul Quran Fantastis Pusat, sekolah ini menghadirkan suasana belajar yang dekat, terarah, dan membina. Proses pendidikan dirancang untuk menjaga keseimbangan antara pembentukan karakter Islami, penguatan akademik, dan kesiapan menghadapi perkembangan teknologi.`

### Supporting fact list
Use concise editorial facts, not loud badges:
- `Berbasis pondok pesantren`
- `Fokus pada tahfizh dan adab`
- `Pembelajaran akademik yang terarah`
- `Penguatan karakter dan kemandirian`

### Profile image
Use:
- `1000512148.jpg`

---

## 8) THREE EDUCATIONAL PILLARS / TIGA PILAR PENDIDIKAN — FINAL CONTENT

### Section label
`Tiga Pilar Pendidikan`

### Intro copy
`Pendidikan di SMP Tahfizh Quran Fantastis dibangun di atas tiga pilar utama yang saling melengkapi: Al-Qur'an dan tahfizh, pembelajaran akademik, serta pengembangan siswa.`

### Program 01
Title:
`Al-Qur'an & Tahfizh`

Description:
`Santri dibimbing untuk membangun kedekatan dengan Al-Qur'an melalui hafalan, murojaah, pembiasaan ibadah, dan adab belajar yang terjaga.`

Image:
- `1000160830.jpg`

### Program 02
Title:
`Pembelajaran Akademik`

Description:
`Siswa mengikuti pembelajaran akademik yang membantu mereka memahami ilmu pengetahuan, memperkuat literasi, dan bertumbuh secara intelektual dengan pendampingan yang terarah.`

Image:
- `1000520096.jpg`

### Program 03
Title:
`Pengembangan Siswa`

Description:
`Berbagai kegiatan harian dan kebersamaan di lingkungan pesantren membantu siswa belajar disiplin, tanggung jawab, kepemimpinan, kerja sama, dan kemandirian.`

Image:
- `1000163805.jpg`

### Implementation note
- three equal editorial stories on desktop
- vertical editorial stacking on mobile
- avoid boxed-card UI overload
- keep descriptions concise and readable

---

## 9) QUR'AN × TECHNOLOGY — FINAL CONTENT

### Section label
`Keunggulan`

### Heading
`Al-Qur'an × Technology`

### Body copy
`Kami percaya bahwa pendidikan Islam yang kuat tidak harus menjauh dari perkembangan zaman. Karena itu, SMP Tahfizh Quran Fantastis menghadirkan pendekatan belajar yang menumbuhkan generasi Qurani sekaligus melek teknologi.`

`Melalui pengenalan perangkat digital, pembelajaran yang terarah, dan budaya belajar yang bertanggung jawab, siswa dibimbing agar mampu memanfaatkan teknologi sebagai sarana belajar, berpikir, dan berkarya dengan nilai-nilai yang tetap terjaga.`

### Supporting point list
- `Literasi digital dasar`
- `Pembelajaran berbasis teknologi secara terarah`
- `Penggunaan teknologi yang bertanggung jawab`
- `Nilai Qurani sebagai fondasi`

### Image
Use:
- `1000344565.jpg`

### Section role
This is the homepage signature differentiation story and should feel special.

---

## 10) CAPAIAN TAHFIZH — FINAL CONTENT

### Section label
`Capaian Tahfizh`

### Metric value
`230+`

### Metric label
`Santri telah menyelesaikan setoran hafalan 30 juz`

### Supporting copy
`Capaian ini menjadi salah satu bukti kesungguhan pembinaan tahfizh di lingkungan Pondok Pesantren Daarul Quran Fantastis. Kehadiran data ini dimaksudkan sebagai penguat kepercayaan, sekaligus inspirasi bagi santri yang sedang menempuh proses hafalan.`

### Implementation note
- keep this section compact
- single-metric editorial evidence
- do not turn it into a crowded statistics dashboard

---

## 11) KEHIDUPAN DI PONDOK PESANTREN — FINAL CONTENT

### Section label
`Kehidupan di Pondok Pesantren`

### Intro copy
`Belajar di sini bukan hanya berlangsung di ruang kelas. Keseharian santri dibentuk melalui ibadah, belajar bersama, kebersamaan, disiplin, dan aktivitas yang membantu mereka bertumbuh menjadi pribadi yang lebih mandiri.`

### Approved image set
- `1000512176.jpg`
- `1000512147.jpg`
- `1000213703.jpg`

### Approved caption set
Caption 01:
`Kebersamaan santri dalam kegiatan harian`

Caption 02:
`Belajar aktif di lingkungan pondok pesantren`

Caption 03:
`Pembinaan karakter, disiplin, dan kemandirian`

### Implementation note
- editorial mosaic feeling
- curated and intentional
- do not make it look like a generic gallery dump

---

## 12) PPDB — FINAL CONTENT

### Section label
`PPDB`

### Heading
`Penerimaan Peserta Didik Baru`

### Supporting copy
`Bagi orang tua dan calon siswa yang ingin mengenal lebih dekat SMP Tahfizh Quran Fantastis, kami siap membantu melalui informasi pendaftaran, alur masuk, dan penjelasan program sekolah.`

`Silakan hubungi kami untuk memperoleh informasi lebih lanjut mengenai PPDB dan proses pendaftaran.`

### Primary CTA
`Tanya Informasi PPDB`

Destination:
`https://wa.me/6281315452107?text=Assalamu%27alaikum%2C%20saya%20ingin%20menanyakan%20informasi%20PPDB%20SMP%20Tahfizh%20Quran%20Fantastis.`

### Secondary CTA
`Pelajari Profil Sekolah`

Destination:
`#profil`

### Implementation note
- this is the homepage closing conversion section
- keep the layout clear, confident, and easy to act on

---

## 13) FOOTER — FINAL CONTENT

### Institutional name
`SMP Tahfizh Quran Fantastis`

### Tagline
`Membangun Generasi Qurani dan Melek Teknologi`

### Parent institution line
`Bagian dari Pondok Pesantren Daarul Quran Fantastis Pusat`

### Quick links
- `Profil`
- `Program`
- `Kehidupan`
- `PPDB`
- `Kontak`
- `Informasi`

### Quick-link destinations
- `Profil` → `#profil`
- `Program` → `#program`
- `Kehidupan` → `#kehidupan`
- `PPDB` → `#ppdb`
- `Kontak` → footer/contact area or existing contact destination
- `Informasi` → `about.html`

### Contact
WhatsApp:
`0813-1545-2107`

WhatsApp link:
`https://wa.me/6281315452107`

Location text:
`Bojong Gede, Bogor`

Map note:
Use the existing map implementation that points to the approved Yayasan Qur'an Fantastis / school location configuration already validated in the project.

### Copyright line
Use the current year dynamically if appropriate.

---

## 14) IMPLEMENTATION GUARDRAILS

### Must preserve
- Prototype 03 homepage architecture
- Prototype 03 visual rhythm
- shared production behavior where appropriate
- responsive behavior
- accessibility improvements
- performance-first asset handling

### Must not do
- no redesign into a different visual concept
- no new homepage news/blog section
- no card-everything layout
- no heavy decorative clutter
- no replacing selected images with unapproved alternatives
- no random content invention beyond this document
- no changing approved section order

### Technical intent
- integrate into production-grade structure
- optimize assets appropriately
- keep semantic HTML
- maintain good keyboard accessibility
- respect reduced motion
- preserve or improve responsive quality
- preserve About / Contact pages unless small shared-navigation alignment is required

---

## 15) IMPLEMENTATION COMPLETION EXPECTATION

After implementation, manual QA should verify:
- desktop composition
- mobile composition
- keyboard navigation
- contrast/readability
- reduced-motion behavior
- image loading/performance
- CTA behavior
- WhatsApp flow
- footer links
- section anchor behavior
