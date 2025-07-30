import os

# Input: Mandalay earthquake MMI file
INPUT_DATA_FILE = r'C:\Users\khant\projects\ShakeMap\maps\earthquake.txt'
STATION_DATA_FILE = r'C:\Users\khant\projects\ShakeMap\maps\stations.txt'
OUTPUT_PS_FILE = r'C:\Users\khant\projects\ShakeMap\maps\mmi_mandalay_map.ps'
OUTPUT_PNG_FILE = r'C:\Users\khant\projects\ShakeMap\maps\mmi_mandalay_map.png'
INTERPOLATE = r"C:\Users\khant\projects\ShakeMap\maps\dyfi_city_points.txt"

SHAKEMAP_CPT = """
0    0 0 0 1    255 255 255
1    255 255 255 2    191 204 255
2    191 204 255 3    160 230 255
3    160 230 255 4    128 255 255
4    128 255 255 5    122 255 147
5    122 255 147 6    255 255 0
6    255 255 0   7    255 200 0
7    255 200 0   8    255 145 0
8    255 145 0   9    255 0   0
9    255 0   0   10   200 0   0
10   200 0   0   13   128 0   0
B    255 255 255
F    255 255 255
"""

def generate_gmt_script():
    with open('shake.cpt', 'w') as f:
        f.write(SHAKEMAP_CPT)

    # Manually define bounds centered on Mandalay
    center_lon, center_lat = 96.1, 21.95
    lon_range = 5.0  # degrees left/right
    lat_range = 6.0  # degrees up/down

    def get_bounds(filepath):
        lons, lats = [], []
        with open(filepath) as f:
            for line in f:
                try:
                    lon, lat, _ = map(float, line.strip().split())
                    lons.append(lon)
                    lats.append(lat)
                except:
                    continue
        return min(lons), max(lons), min(lats), max(lats)
    
    min_lon, max_lon, min_lat, max_lat = get_bounds(INTERPOLATE)
    bounds = f"-R{min_lon-0.5}/{max_lon+0.5}/{min_lat-0.5}/{max_lat+0.5}"

    # min_lon = center_lon - lon_range
    # max_lon = center_lon + lon_range
    # min_lat = center_lat - lat_range
    # max_lat = center_lat + lat_range

    # bounds = f"-R{min_lon}/{max_lon}/{min_lat}/{max_lat}"

    with open('plot.bat', 'w') as f:
        f.write("@echo off\n")
        f.write(f"set INPUT_FILE={INPUT_DATA_FILE}\n")
        f.write(f"set STATION_FILE={STATION_DATA_FILE}\n")
        f.write(f"set BLOCKMEAN_FILE=blockmean.txt\n")
        f.write(f"set GRID_FILE=mmi_surface.nc\n")
        f.write(f"set CPT_FILE=shake.cpt\n")
        f.write(f"set PS_FILE={OUTPUT_PS_FILE}\n")
        f.write(f"set PNG_FILE={OUTPUT_PNG_FILE}\n")
        f.write(f"set INTERPOLATE_FILE={INTERPOLATE}\n")
        f.write(f"set BOUNDS={bounds}\n")

        f.write("set PROJECTION=-JM12c\n\n")

        # Step 1: Interpolate surface from input points
        f.write("gmt blockmean %INTERPOLATE_FILE% %BOUNDS% -I2m > %BLOCKMEAN_FILE%\n")
        f.write("gmt surface %BLOCKMEAN_FILE% -G%GRID_FILE% -I2m %BOUNDS% -T0.35\n")

        # Step 2: Initialize base map
        f.write("gmt psbasemap %BOUNDS% %PROJECTION% -Baf -B+t\"Mandalay, Myanmar\" -K > %PS_FILE%\n")

        # Step 3: Plot interpolated surface (gridded MMI)
        f.write("gmt grdimage %GRID_FILE% -C%CPT_FILE% %BOUNDS% %PROJECTION% -O -K >> %PS_FILE%\n")

        # Step 4: Re-draw coastlines and borders to avoid being hidden
        f.write("gmt pscoast %BOUNDS% %PROJECTION% -Dh -W0.5p,black -Slightblue -Na/0.25p,gray -O -K >> %PS_FILE%\n")

        # Step 5: Plot MMI input points as colored circles
        f.write("gmt psxy %INPUT_FILE% %BOUNDS% %PROJECTION% -Sc0.45c -C%CPT_FILE% -W0.25p,black -O -K >> %PS_FILE%\n")

        # Step 6: Plot seismic stations as black triangles
        f.write("gmt psxy %STATION_FILE% %BOUNDS% %PROJECTION% -St0.5c -Gblack -W0.3p,black -O -K >> %PS_FILE%\n")

        # Step 7: Add legend scale for MMI
        f.write("gmt psscale -C%CPT_FILE% -Dx8c/-1.5c+w10c/0.5c+jTC+h -Bx2+l\"MMI\" -O >> %PS_FILE%\n")

        # Step 8: Convert to PNG
        f.write("gmt psconvert %PS_FILE% -A -Tg -P\n")

        # Step 9: Cleanup temp files
        f.write("del %BLOCKMEAN_FILE%\n")
        f.write("del %GRID_FILE%\n")

        f.write("echo Done. PNG map saved as %PNG_FILE%\n")
        f.write("pause\n")

if __name__ == '__main__':
    generate_gmt_script()
    print("Run: plot.bat")
