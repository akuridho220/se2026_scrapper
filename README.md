# SCRAPER DATA SENSUS EKONOMI 2026

## 📌 Deskripsi

Script ini digunakan untuk melakukan scraping data Sensus Ekonomi 2026 dari sistem terkait hingga level SLS.

---

## 🚀 Cara Penggunaan

### 1. Unduh Source Code

Clone repository ini atau unduh file **`se_scrapper.py`**.

---

### 2. Konfigurasi Awal

Buka file **`se_scrapper.py`**, lalu sesuaikan beberapa bagian berikut:

* **KODE_PROVINSI** → isi dengan kode provinsi Anda
* **NAMA_KABUPATEN** → isi dengan nama kabupaten Anda
* **base_path** → tentukan folder penyimpanan hasil scraping
* **headers** → isi dengan headers hasil dari browser
* **cookies** → isi dengan cookies hasil dari browser

**Opsional:**

* Anda dapat menambahkan filter untuk:

  * Kecamatan
  * Desa
    sesuai kebutuhan

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

## 🔐 Panduan Mengambil Cookies & Headers

1. Buka aplikasi **Fasih-sm** dan login
2. Pilih kegiatan **Sensus Ekonomi 2026**
3. Masuk ke halaman **Data**
4. Buka Developer Tools:

   * Klik kanan → *Inspect*, atau tekan **F12**
5. Masuk ke tab **Network**
6. Jika kosong, reload halaman
7. Cari request dengan nama:

   ```
   datatable-all-user-survey-periode
   ```
8. Klik kanan pada request tersebut → pilih **Copy → Copy as cURL (bash)**
9. Buka website: https://curlconverter.com
10. Paste hasil cURL
11. Salin bagian:

    * **cookies**
    * **headers**
12. Tempelkan ke dalam file `se_scrapper.py`

---

## ⚠️ Catatan Penting

* Data yang diambil adalah **level SLS**
* Maksimal data yang dapat diambil per SLS adalah **1000 baris**

  * Jika lebih dari itu, data selebihnya **tidak akan terambil**
* Gunakan script ini dengan bijak

  * Disarankan menjalankan pada **malam hari/tengah malam**, untuk menghindari gangguan terhadap server dan proses pendataan lapangan

---

## 🙏 Penutup

Gunakan tools ini secara bertanggung jawab dan hanya untuk keperluan yang sesuai.
