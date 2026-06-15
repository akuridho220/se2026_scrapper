import requests
import pandas as pd
import logging
import time
import os
import random
from datetime import datetime

# ================= SETTING VARIABEL UTAMA =================
ID_SURVEI = "a0429e96-51a5-477b-a415-485f9c153004"  # ada di URL survei yang mau di scrap
KODE_PROVINSI = ""
NAMA_KABUPATEN = ""
# ==========================================================

base_path = ""
if not os.path.exists(base_path):
    os.makedirs(base_path)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_path = os.path.join(base_path, f"error_log_{timestamp}.txt")
backup_file = os.path.join(base_path, f"SCRAPING_SE2026_{NAMA_KABUPATEN}_{timestamp}.xlsx")

logging.basicConfig(
    filename=log_path,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

URL_SURVEY_INFO = f"https://fasih-sm.bps.go.id/survey/api/v1/surveys/{ID_SURVEI}"
URL_REGION = "https://fasih-sm.bps.go.id/region/api/v1/region"
URL_DATA = "https://fasih-sm.bps.go.id/analytic/api/v2/assignment/datatable-all-user-survey-periode"

# ===================== GANTI COOKIE DI SINI =====================
cookies = {
    # Isi cookies
}

headers = {
    # Isi headers
}
# ================================================================

def get_survey_meta(session):
    try:
        res = session.get(URL_SURVEY_INFO, headers=headers)
        data = res.json()['data']
        print(f"[INFO] Survei: {data['name']}")
        return data['regionGroupId'], data['surveyPeriods'][0]['id'], data['name']
    except Exception as e:
        print(f"[ERROR] Gagal ambil metadata survei: {e}")
        return None, None, None

def get_list(session, url_path, params):
    try:
        res = session.get(url_path, headers=headers, params=params)
        return res.json().get('data', []) if res.status_code == 200 else []
    except:
        return []

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

def fetch_data_desa(session, kec_id, desa, kec_name, prov_id, kab_id, period_id, idx_desa, total_desa, total_scrap):
    print(f"   >> DESA ({idx_desa}/{total_desa}): {desa['name']}")
    desa_results = []
    start_point = 0
    total_count = 0

    while True:
        payload = {
            "draw": random.randint(1, 100),
            "start": start_point,
            "length": 100,
            "assignmentExtraParam": {
                "region1Id": prov_id,
                "region2Id": kab_id,
                "region3Id": kec_id,
                "region4Id": desa["id"],
                "region5Id": None,  # ❗ TANPA SLS
                "surveyPeriodId": period_id,
                "assignmentErrorStatusType": -1,
                "filterTargetType": "ALL"
            }
        }

        try:
            time.sleep(random.uniform(0.2, 0.5))
            res = session.post(URL_DATA, headers=headers, cookies=cookies, json=payload)

            data = res.json()
            items = data.get("searchData", [])

            agg = data.get("searchAggregation", [])
            total_count = sum(a.get("docCount", 0) for a in agg)

            if total_count == 0:
                total_count = data.get("totalHit", 0)
            elif total_count >= 1000:
                return desa_results, total_count, total_scrap

            if items:
                for item in items:
                    # Parse region berjenjang sampai level 6 (SubSLS)
                    region = item.get("region", {})
                    lvl1 = region.get("level1", {})
                    lvl2 = lvl1.get("level2", {})
                    lvl3 = lvl2.get("level3", {})   # Kecamatan
                    lvl4 = lvl3.get("level4", {})   # Desa
                    lvl5 = lvl4.get("level5", {})   # SLS
                    lvl6 = lvl5.get("level6", {})   # SubSLS

                    desa_results.append({
                        "KECAMATAN":    kec_name,
                        "DESA":         desa["name"],
                        "Nama SLS":     lvl5.get("name", ""),
                        "Kode SubSLS":  lvl6.get("fullCode", ""),
                        "Nama SubSLS":  lvl6.get("name", ""),
                        "Nama Usaha":   item.get("data1", ""),
                        "Alamat":       item.get("data2", ""),
                        "Jenis":        item.get("data6", ""),   # UMKM / BANGUNAN_LAIN / dll
                        "Status":       item.get("assignmentStatusAlias", ""),
                        "Username":     item.get("currentUserUsername", ""),
                        "Pencacah":     item.get("currentUserFullname", ""),
                        "codeIdentity": item.get("codeIdentity", ""),
                    })
                total_scrap += len(items)
                # desa_results.extend(items)

            print(
                f"      [DESA] {desa['name']} | "
                f"Batch: {start_point}-{start_point + len(items) - 1 if items else start_point} | "
                f"Ambil: {len(items)} | Total: {total_count}"
                f" | Akumulasi: {total_scrap}"
            )

            start_point += 100
            if start_point >= total_count or not items:
                break

        except Exception as e:
            logging.error(f"[DESA ERROR] {desa['name']} start {start_point}: {e}")
            break

    mark_done(desa["name"], "desa")
    return desa_results, total_count, total_scrap

def fetch_data_sls(session, kec_id, desa, kec_name, sls_list, prov_id, kab_id, period_id, total_scrap):
    total_sls = len(sls_list)
    all_results = []

    for idx_sls, sls in enumerate(sls_list, 1):
        print(f"      >> SLS ({idx_sls}/{total_sls}): {sls['name']}")
        start_point = 0

        while True:
            payload = {
                "draw": random.randint(1, 100),
                "start": start_point,
                "length": 100,
                "assignmentExtraParam": {
                    "region1Id": prov_id,
                    "region2Id": kab_id,
                    "region3Id": kec_id,
                    "region4Id": desa["id"],
                    "region5Id": sls["id"],  # 🔥 pakai SLS
                    "surveyPeriodId": period_id,
                    "assignmentErrorStatusType": -1,
                    "filterTargetType": "ALL"
                }
            }

            try:
                time.sleep(random.uniform(0.2, 0.5))
                res = session.post(URL_DATA, headers=headers, cookies=cookies, json=payload)
                data = res.json()

                items = data.get("searchData", [])
                # Hitung total data
                agg = data.get("searchAggregation", [])
                total_count = sum(a.get("docCount", 0) for a in agg)
                if total_count == 0:
                    total_count = data.get("totalHit", 0)

                if items:
                    for item in items:
                        # Parse region berjenjang sampai level 6 (SubSLS)
                        region = item.get("region", {})
                        lvl1 = region.get("level1", {})
                        lvl2 = lvl1.get("level2", {})
                        lvl3 = lvl2.get("level3", {})   # Kecamatan
                        lvl4 = lvl3.get("level4", {})   # Desa
                        lvl5 = lvl4.get("level5", {})   # SLS
                        lvl6 = lvl5.get("level6", {})   # SubSLS

                        all_results.append({
                            "KECAMATAN":    kec_name,
                            "DESA":         desa["name"],
                            "Nama SLS":     lvl5.get("name", ""),
                            "Kode SubSLS":  lvl6.get("fullCode", ""),
                            "Nama SubSLS":  lvl6.get("name", ""),
                            "Nama Usaha":   item.get("data1", ""),
                            "Alamat":       item.get("data2", ""),
                            "Jenis":        item.get("data6", ""),   # UMKM / BANGUNAN_LAIN / dll
                            "Status":       item.get("assignmentStatusAlias", ""),
                            "Username":     item.get("currentUserUsername", ""),
                            "Pencacah":     item.get("currentUserFullname", ""),
                            "codeIdentity": item.get("codeIdentity", ""),
                        })
                    total_scrap += len(items)
                    # all_results.extend(items)
                
                print(
                    f"         [SLS] {sls['name']} | "
                    f"Batch: {start_point}-{start_point + len(items) - 1 if items else start_point} | "
                    f"Ambil: {len(items)}"
                    f" | Akumulasi: {total_scrap}"
                )

                start_point += 100
                if start_point >= total_count or not items:
                    break

                if not items:
                    break

            except Exception as e:
                logging.error(f"[SLS ERROR] {sls['name']}: {e}")
                break
            
    mark_done(sls["name"], "sls")
    return all_results, total_scrap

def mark_done(name, level="desa"):
    with open("progress.txt", "a") as f:
        f.write(f"{level}:{name}\n")


def fetch_data():
    overall_start_time = time.time()
    total_scrap = 0

    # SESSION REUSE (GLOBAL DALAM 1 RUN)
    session = requests.Session()
    
    group_id, period_id, survey_name = get_survey_meta(session)
    if not group_id:
        return

    # Ambil ID Provinsi
    prov_list = get_list(session, f"{URL_REGION}/level1", {"groupId": group_id})
    prov_id = next((item['id'] for item in prov_list if item['code'] == KODE_PROVINSI), None)
    if not prov_id:
        print(f"[ERROR] Provinsi dengan kode {KODE_PROVINSI} tidak ditemukan!")
        return

    # Ambil ID Kabupaten
    kab_list = get_list(session, f"{URL_REGION}/level2", {"groupId": group_id, "level1FullCode": KODE_PROVINSI})
    kab_id = next((item['id'] for item in kab_list if NAMA_KABUPATEN.upper() in item['name'].upper()), None)
    if not kab_id:
        print(f"[ERROR] Kabupaten '{NAMA_KABUPATEN}' tidak ditemukan!")
        return

    # Ambil daftar Kecamatan
    kec_list = get_list(session, f"{URL_REGION}/level3", {"groupId": group_id, "level2Id": kab_id})
    total_kec = len(kec_list)

    print(f"\n[START] Mulai scraping {survey_name}")
    print(f"[INFO] Kabupaten: {NAMA_KABUPATEN} | Total Kecamatan: {total_kec}")
    print(f"[INFO] Output: {backup_file}\n")

    # LOOP KECAMATAN
    for idx_kec, kec in enumerate(kec_list, 1):
        kec_id = kec['id']
        kec_name = kec['name'].upper()

        # FILTER KECAMATAN JIKA DIPERLUKAN
        # if kec_name != "":
        #     continue

        # Ambil daftar Desa
        desa_list = get_list(session, f"{URL_REGION}/level4", {"groupId": group_id, "level3Id": kec_id})
        total_desa = len(desa_list)

        print(f"\n>> ({idx_kec}/{total_kec}) KECAMATAN: {kec_name} | {total_desa} Desa")

        # LOOP DESA
        for idx_desa, desa in enumerate(desa_list, 1):
            # FILTER DESA JIKA DIPERLUKAN
            # desa_name = desa["name"].upper()
            # if (desa_name != ""):
            #     continue
            
            desa_data, total_count, total_hasil_scrap_desa = fetch_data_desa(session, kec_id, desa, kec_name, prov_id, kab_id, period_id, idx_desa, total_desa, total_scrap)
            if total_count >= 1000:
                print(f"   [!] Desa {desa['name']} kena limit → fallback SLS")

                sls_list = get_list(session,f"{URL_REGION}/level5", {
                    "groupId": group_id,
                    "level4Id": desa["id"]
                })

                desa_data, total_hasil_scrap_sls = fetch_data_sls(session, kec_id, desa, kec_name, sls_list, prov_id, kab_id, period_id, total_scrap)
                total_scrap += total_hasil_scrap_sls

            if total_count < 1000:
                total_scrap += total_hasil_scrap_desa

            # 🔥 SAVE SEKALI PER DESA
            if desa_data:
                save_and_merge(desa_data)

    # Hitung durasi
    end_time = time.time()
    duration_seconds = end_time - overall_start_time
    minutes = int(duration_seconds // 60)
    seconds = int(duration_seconds % 60)

    print(f"\n{'=' * 50}")
    print(f"SELESAI!")
    print(f"Total Data  : {total_scrap:,}")
    print(f"Total Waktu : {minutes} menit {seconds} detik")
    print(f"File Akhir  : {backup_file}")
    print(f"{'=' * 50}")

if __name__ == "__main__":
    fetch_data()
