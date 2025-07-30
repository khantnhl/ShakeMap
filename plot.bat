@echo off
set INPUT_FILE=C:\Users\khant\projects\ShakeMap\maps\earthquake.txt
set STATION_FILE=C:\Users\khant\projects\ShakeMap\maps\stations.txt
set BLOCKMEAN_FILE=blockmean.txt
set GRID_FILE=mmi_surface.nc
set CPT_FILE=shake.cpt
set PS_FILE=C:\Users\khant\projects\ShakeMap\maps\mmi_mandalay_map.ps
set PNG_FILE=C:\Users\khant\projects\ShakeMap\maps\mmi_mandalay_map.png
set INTERPOLATE_FILE=C:\Users\khant\projects\ShakeMap\maps\dyfi_city_points.txt
set BOUNDS=-R92.39/98.7/13.59/25.88
set PROJECTION=-JM12c

gmt blockmean %INTERPOLATE_FILE% %BOUNDS% -I2m > %BLOCKMEAN_FILE%
gmt surface %BLOCKMEAN_FILE% -G%GRID_FILE% -I2m %BOUNDS% -T0.35
gmt psbasemap %BOUNDS% %PROJECTION% -Baf -B+t"Mandalay, Myanmar" -K > %PS_FILE%
gmt grdimage %GRID_FILE% -C%CPT_FILE% %BOUNDS% %PROJECTION% -O -K >> %PS_FILE%
gmt pscoast %BOUNDS% %PROJECTION% -Dh -W0.5p,black -Slightblue -Na/0.25p,gray -O -K >> %PS_FILE%
gmt psxy %INPUT_FILE% %BOUNDS% %PROJECTION% -Sc0.45c -C%CPT_FILE% -W0.25p,black -O -K >> %PS_FILE%
gmt psxy %STATION_FILE% %BOUNDS% %PROJECTION% -St0.5c -Gblack -W0.3p,black -O -K >> %PS_FILE%
gmt psscale -C%CPT_FILE% -Dx8c/-1.5c+w10c/0.5c+jTC+h -Bx2+l"MMI" -O >> %PS_FILE%
gmt psconvert %PS_FILE% -A -Tg -P
del %BLOCKMEAN_FILE%
del %GRID_FILE%
echo Done. PNG map saved as %PNG_FILE%
pause
