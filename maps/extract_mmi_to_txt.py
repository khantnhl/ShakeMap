import json

inputFile = r"C:\Users\khant\projects\ShakeMap\maps\records1.json"
output_file = r"C:\Users\khant\projects\ShakeMap\maps\earthquake.txt"

with open(inputFile, "r") as f:
    data = json.load(f)

with open(output_file, 'w') as f : 
    for entry in data:
        coords = entry.get("location", {}).get("coordinates", [0.0,0.0])
        mmi = entry.get("mmi_estimation", 0.0)

        lat = coords[0]
        lon = coords[1]

        if(lat == 0.0 and lon == 0.0):
            continue

        if(mmi==0.0):
            continue

        f.write(f"{lon} {lat} {mmi}\n")

print("Done Writing")