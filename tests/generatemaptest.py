import pygmt
import numpy as np
import pandas as pd

# --- 1. Define Hypothetical Earthquake Parameters and Region ---
# Hypothetical earthquake epicenter for Mandalay, Myanmar
eq_lon, eq_lat = 96.09, 21.96 # Approximate coordinates for Mandalay
eq_magnitude = 6.5
eq_depth = 10 # km

# Define the map region around Mandalay, Myanmar
# Based on search results, a region like [95.5, 96.5, 21.5, 22.5] should cover Mandalay well.
region = [95.5, 96.5, 21.5, 22.5] # [west, east, south, north]

# Define map projection and frame
# M for Mercator, 10c for map width
projection = "M10c"
frame = ["a", f"WSNE+t'Hypothetical M{eq_magnitude} Earthquake Shakemap near Mandalay'"]

# --- 2. Generate Synthetic Intensity Data (MMI Scale) ---
# In a real scenario, you would load actual MMI data from stations or a model.
# Here, we simulate a decay of intensity with distance from the epicenter.

# Create a grid of points within the region
lon_grid, lat_grid = np.meshgrid(
    np.linspace(region[0], region[1], 100),
    np.linspace(region[2], region[3], 100)
)

# Calculate approximate distance from epicenter (simplified Euclidean distance for demonstration)
# In reality, use haversine distance for accurate geographical distances
distances = np.sqrt((lon_grid - eq_lon)**2 + (lat_grid - eq_lat)**2)

# Simulate MMI decay (this is a very simplified, arbitrary function for demonstration)
# MMI typically ranges from I to XII. We'll simulate values from ~III to VIII.
# A simple inverse relationship with distance, scaled by magnitude.
intensity_values = eq_magnitude * 1.5 - (distances * 2.5)
# Clip values to a reasonable MMI range (e.g., 2 to 9)
intensity_values = np.clip(intensity_values, 2, 9)

# Flatten the arrays for PyGMT's surface/nearneighbor
data = pd.DataFrame({
    'x': lon_grid.flatten(),
    'y': lat_grid.flatten(),
    'z': intensity_values.flatten()
})

# --- 3. Create a PyGMT Figure ---
fig = pygmt.Figure()

# --- 4. Plot Basemap ---
# Plot land and water
fig.grdimage(
    "@earth_relief_03m",
    region=region,
    projection=projection,
    shading=True, # Add shading for relief
    cmap="geo" # Geographic colormap for topography
)
fig.coast(
    region=region,
    projection=projection,
    borders="1/0.5p,black", # State borders
    shorelines="1/0.5p,black", # Coastlines
    frame=frame,
    land="lightgray", # Light gray land color
    water="skyblue" # Sky blue water color
)

# --- 5. Interpolate Intensity Data to a Grid ---
# Correct approach for interpolation using pygmt.surface
# pygmt.surface requires a DataFrame with 'x', 'y', 'z' columns.
# The 'spacing' parameter defines the grid cell size.
# The 'tension' parameter (T) controls the smoothness of the surface.
intensity_grid = pygmt.surface(
    data=data,
    region=region,
    spacing=0.05, # Grid spacing for the output grid (e.g., 0.05 degrees)
    # tension="0.25" # Tension factor (optional, adjust for smoothness)
)


# --- 6. Plot Intensity Contours and/or Filled Areas ---
# Define colormap for MMI (Modified Mercalli Intensity)
# We'll create a custom CPT (Color Palette Table) for MMI.
# MMI typically ranges from I to XII.
# Let's use colors typically associated with shakemaps (e.g., USGS colors).
# MMI I-II: White/Gray (not felt/felt by few)
# MMI III-IV: Light Green/Yellow (felt by many, light shaking)
# MMI V-VI: Orange/Red (strong shaking, damage begins)
# MMI VII-VIII: Dark Red/Purple (very strong, moderate-heavy damage)
# MMI IX+: Brown/Black (violent, heavy-very heavy damage)

# Define MMI color levels and corresponding colors
# Using a simple list of colors for illustration.
# You can define a more precise CPT file if needed.
# pygmt.makecpt(cmap="jet", series=[2, 9, 1], reverse=True, background=True, output="mmi.cpt")
# Or define it directly in Python:
# Define MMI color levels and their corresponding colors (hex codes)
# These are representative colors for MMI from USGS-like shakemaps
mmi_colors = [
    (2, "#d9f0a3"),  # MMI II-III (Not felt to weak) - Light green
    (3, "#addd8e"),  # MMI III-IV (Weak to Light)
    (4, "#78c679"),  # MMI IV-V (Light to Moderate)
    (5, "#41ab5d"),  # MMI V-VI (Moderate to Strong)
    (6, "#238b45"),  # MMI VI-VII (Strong to Very Strong)
    (7, "#006837"),  # MMI VII-VIII (Very Strong to Severe)
    (8, "#004529"),  # MMI VIII-IX (Severe to Violent)
    (9, "#002010")   # MMI IX+ (Violent to Extreme)
]

# Create a CPT from the defined colors
# pygmt.makecpt can take a list of (value, color) tuples.
# Here, we'll map our intensity_values (2-9) to colors.
# Let's use a standard colormap and reverse it, or define custom levels.
# For MMI, a diverging or sequential colormap is often used.
# Let's use 'hot' and reverse it for higher intensity = darker color.
# Or better, define custom discrete levels.
pygmt.makecpt(
    cmap="hot",
    series=[2, 9, 1], # From 2 to 9, increment by 1
    reverse=True, # Higher intensity = darker/hotter color
    background=True, # Add background color for values outside range
    output="mmi_shakemap.cpt" # Save the CPT to a file
)

# Plot the interpolated intensity grid as filled contours
fig.grdimage(
    grid=intensity_grid,
    region=region,
    projection=projection,
    cmap="mmi_shakemap.cpt", # Use our custom MMI colormap
    # transparency=30 # Optional: Add transparency to see basemap better
)

# Optionally, add contour lines on top of the filled areas
fig.grdcontour(
    grid=intensity_grid,
    region=region,
    projection=projection,
    interval=1, # Contour interval (e.g., every 1 MMI unit)
    pen="0.8p,black", # Black pen for contours
    # label=True # Label contours (can be messy for many contours)
)

# --- 7. Plot Earthquake Epicenter ---
fig.plot(
    x=eq_lon,
    y=eq_lat,
    style="a0.8c", # Star symbol, 0.8 cm size
    color="red",   # Red color
    pen="1p,black", # Black outline
    label=f"M{eq_magnitude} Epicenter"
)

# Add a legend for the epicenter (optional, but good practice)
fig.legend()

# --- 8. Add Colorbar for MMI Scale ---
fig.colorbar(
    cmap="mmi_shakemap.cpt",
    frame=["a1", "x+l'MMI Scale'", "y+l'Intensity'"], # Label colorbar
    # Position the colorbar (e.g., bottom-right)
    position="JBC+w10c/0.5c+h" # Justified Bottom Center, width 10cm, height 0.5cm, horizontal
)

# --- 9. Save the Map ---
fig.savefig("shakemap_pygmt.png")
print("Shakemap 'shakemap_pygmt.png' created successfully!")