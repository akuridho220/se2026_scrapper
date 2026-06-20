# SCRAPER DATA REKAP PROGRES SENSUS EKONOMI 2026

## 📌 Deskripsi

Script ini digunakan untuk melakukan scraping data rekapitulasi progres Sensus Ekonomi 2026 dari sistem Fasih hingga level Sub SLS.

---

## 🚀 Cara Penggunaan

### 1. Unduh Source Code

Clone repository ini atau unduh file **`recap_se_scrapper.py`**.

---

### 2. Konfigurasi Awal

Buka file **`recap_se_scrapper.py`**, lalu sesuaikan beberapa bagian berikut:

* **NAMA_KABUPATEN** → isi dengan nama kabupaten Anda
* **base_path** → tentukan folder penyimpanan hasil scraping
* **headers** → isi dengan headers hasil dari browser
* **cookies** → isi dengan cookies hasil dari browser
* **json_data** isi dengan json_data hasil dari browser


---

### 3. Install Dependencies

Jalankan perintah berikut di terminal:

```
pip install -r requirements.txt
```

### 4. Jalankan Code
Jalankan perintah berikut di terminal:
``` 
py se_scrapper.py
```

---

## 🔐 Panduan Mengambil Cookies, Headers & Json_data

1. Buka aplikasi **Fasih-sm** dan login
2. Pilih kegiatan **Sensus Ekonomi 2026**
3. Masuk ke halaman **Dasbor** lalu pilih **Rekap Petugas** dan pilih **Pencacah**
4. Buka Developer Tools:

   * Klik kanan → *Inspect*, atau tekan **F12**
5. Masuk ke tab **Network**
6. Jika kosong, reload halaman atau reload pada rekap petugas
7. Cari request dengan nama:

   ```
   report-progress-by-responsibility
   ```
8. Klik kanan pada request tersebut → pilih **Copy → Copy as cURL (bash)**
9. Buka website: https://curlconverter.com
10. Paste hasil cURL
11. Salin bagian:

    * **cookies**
    * **headers**
    * **json_data**

12. Tempelkan ke dalam file `recap_se_scrapper.py`
13. **PENTING** Jika baris terkahir **headers** terdapat comment (#), hapus tanda pagar tersebut! Selain itu hapus baris berisi informasi **page** dan **size** pada **json_data**

---


## 🙏 Penutup

Gunakan tools ini secara bertanggung jawab dan hanya untuk keperluan yang monitoring.
