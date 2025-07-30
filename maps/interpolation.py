import csv

input_file = r"C:\Users\khant\projects\ShakeMap\maps\DYFI_cities.txt"
output_file = r"C:\Users\khant\projects\ShakeMap\maps\dyfi_city_points.txt"

with open(input_file, "r") as infile, open(output_file, "w") as outfile:
    reader = csv.reader(infile)
    for row in reader:
        try:
            cdi = float(row[1].strip())
            lat = float(row[4].strip())
            lon = float(row[5].strip())
            outfile.write(f"{lon} {lat} {cdi}\n")
        except (IndexError, ValueError):
            continue  # Skip malformed lines