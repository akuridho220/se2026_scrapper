import pandas as pd
import requests
import os
from datetime import datetime

# ================= SETTINGS =================
NAMA_KABUPATEN = "" #NAMA KABUPATEN 
URL_DATA = 'https://fasih-sm.bps.go.id/app/api/analytic/api/v2/assignment/report-progress-by-responsibility' 
base_path = ""                #FOLDER UNTUK MENYIMPAN DATA HASIL SCRAPPING
# ==========================================================

# ===================== GANTI COOKIE DI SINI =====================
cookies = {
    # Isi Cookies di sini
}

headers = {
    # Isi headers di sini
}

json_data = {
    # Isi json_data di sini
}
# ================================================================

if not os.path.exists(base_path):
    os.makedirs(base_path)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = os.path.join(base_path, f"SCRAPING_REKAP_SE2026_{NAMA_KABUPATEN}_{timestamp}.xlsx")


def save_and_merge(new_data):
    """Simpan berkala setiap 1 Desa selesai"""
    if not new_data:
        return

    df_new = pd.DataFrame(new_data)

    if os.path.exists(backup_file):
        df_old = pd.read_excel(backup_file)
        df_final = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_final = df_new

    df_final.to_excel(backup_file, index=False)

def fetch_data():
    all_rows = []
    page = 0
    size = 10

    while True:
        json_data['page'] = page
        json_data['size'] = size

        response = requests.post(
            URL_DATA,
            cookies=cookies,
            headers=headers,
            json=json_data,
        )

        if response.status_code != 200:
            print(f"❌ Error di page {page}")
            break

        json_res = response.json()
        data_block = json_res.get("data", {})
        data = data_block.get("content", [])
        is_last = data_block.get("last", True)

        print(f"📄 Page {page} | jumlah data: {len(data)} | last: {is_last}")

        # 🔽 Flatten
        for user in data:
            for region in user.get("regionSummary", []):
                row = {
                    "userId": user.get("userId"),
                    "username": user.get("username"),
                    "email": user.get("email"),
                    "role": user.get("roleName"),
                    "regionCode": region.get("regionCode"),
                    "total_data": region.get("total"),
                }

                for status in region.get("statusBreakdown", []):
                    row[status.get("status")] = status.get("count")

                all_rows.append(row)

        if is_last:
            print("✅ Sudah sampai halaman terakhir")
            break

        page += 1

    if all_rows:
        save_and_merge(all_rows)

    print("🎉 Semua data berhasil disimpan!")

if __name__ == "__main__":
    fetch_data()