import os
import gpxpy
import geojson
from geojson import Feature, Point, FeatureCollection

gpx_folder = 'gpx_tracks/'  
output_file = 'all_tracks.geojson' 

all_features = []

for filename in os.listdir(gpx_folder):
    if filename.endswith(".gpx"):
        filepath = os.path.join(gpx_folder, filename)
        print(f"Обработка файла: {filename}")

        with open(filepath, 'r', encoding='utf-8') as gpx_file:
            gpx = gpxpy.parse(gpx_file)

            for track in gpx.tracks:
                for segment in track.segments:
                    for point in segment.points:
                        all_features.append(
                            Feature(
                                geometry=Point((point.longitude, point.latitude)),
                                properties={
                                    "elevation": point.elevation,
                                    "time": point.time.isoformat() if point.time else None,
                                    "source_file": filename  # можно добавить имя файла как метку
                                }
                            )
                        )

if all_features:
    collection = FeatureCollection(all_features)
    with open(output_file, 'w', encoding='utf-8') as out_file:
        geojson.dump(collection, out_file, ensure_ascii=False, indent=2)
        print(f"\nВсе треки сохранены в: {output_file}")
else:
    print("Нет данных для сохранения.")
