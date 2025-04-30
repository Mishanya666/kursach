import os
import pandas as pd
import time
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed


min_lat, max_lat = 50.0, 60.0
min_lon, max_lon = 95.0, 110.0
step_deg = 0.25  

cells = []
cell_id = 0

lat = min_lat
while lat < max_lat:
    lon = min_lon
    while lon < max_lon:
        cells.append({
            'id': cell_id,
            'left': lon,
            'bottom': lat,
            'right': lon + step_deg,
            'top': lat + step_deg
        })
        cell_id += 1
        lon += step_deg
    lat += step_deg

df = pd.DataFrame(cells)
df.to_csv('cells_deg.csv', index=False)
print(f"Создано ячеек: {len(df)}")


output_dir = "gpx_tracks"
os.makedirs(output_dir, exist_ok=True)

empty_gpx = b'<?xml version="1.0" encoding="UTF-8"?>\n<gpx version="1.0" creator="OpenStreetMap.org" xmlns="http://www.topografix.com/GPX/1/0">\n</gpx>\n'
headers = {"User-Agent": "Mozilla/5.0"}
MAX_WORKERS = 8
DELAY = 0.5

def download_cell(row):
    page = 0
    cell_id = int(row.id)
    downloaded_any = False

    while True:
        page += 1
        filename = f"track_{cell_id}_p{page}.gpx"
        filepath = os.path.join(output_dir, filename)

        if os.path.exists(filepath):
            print(f"[{cell_id}] Файл {filename} уже существует, пропускаем.")
            return None

        url = (
            f"https://api.openstreetmap.org/api/0.6/trackpoints?"
            f"bbox={row.left},{row.bottom},{row.right},{row.top}&page={page}"
        )

        try:
            response = requests.get(url, headers=headers, timeout=10)
        except Exception as e:
            return f"[{cell_id}] Ошибка запроса: {e}"


        with open(filepath, "wb") as f:
            f.write(content)

        downloaded_any = True
        print(f"[{cell_id}] Скачан файл {filename}")
        time.sleep(DELAY)

def download_all_cells(df):
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(download_cell, row) for _, row in df.iterrows()]
        for future in tqdm(as_completed(futures), total=len(futures), desc="Скачивание GPX"):
            result = future.result()
            if result:
                print(result)

download_all_cells(df)
