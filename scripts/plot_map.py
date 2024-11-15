# IMPORTS

# Standard library imports
import argparse
import json  # For reading JSON configuration files

# Third-party library imports
import numpy as np  # Array handling
import pandas as pd  # Data manipulation
import matplotlib.pyplot as plt  # Plotting
from matplotlib.colors import ListedColormap, LogNorm  # Custom color mapping and log scaling
from mpl_toolkits.basemap import Basemap  # Mapping functions
import matplotlib.patches as mpatches  # For custom legend patches

# Local module imports
from fetch_map_df import fetch_map_df  # Function to fetch data with bounding boxes
from basemap_imshow_discrete_or_heatmap import basemap_imshow_discrete_or_heatmap  # Custom mapping function

# ARGUMENTPARSER SETUP
parser = argparse.ArgumentParser(description="Plot a map with customizable parameters")
parser.add_argument('--plotting_parameters', nargs='+', default=["predicted_ecosystem"], help="List of parameters to plot. Default: 'predicted_ecoystem'")
parser.add_argument('--level', type=int, default=3, help="Level of ecosystem detail. Only relevant for plotting_parameters==predicted_ecosystem")
parser.add_argument('--year', type=int, default=2020, help="Year to fetch data for. Default: '2020'")
parser.add_argument('--region', type=str, default="World", help="Geographic region for the data. Sourced from 'bounding_boxes.json'. Default: 'World'")
parser.add_argument('--silent', action='store_true', help="Suppress print statements.")
parser.add_argument('--color', type=str, default="default", help="Color scheme for the plot.\nFor discrete data 'custom' will source values from custom_colors.json.\nFor continous data any heatmap-string can be used")
parser.add_argument('--scale', type=str, choices=["linear", "log"], default="linear", help=" For conitnous data: Scale for the color mapping (linear or log).")

args = parser.parse_args()

# Assigning parsed arguments to variables
plotting_parameters = args.plotting_parameters
level = args.level
year = args.year
region = args.region
silent = args.silent
color = args.color
scale = args.scale

# Load custom colors from JSON
if color == "custom":
    with open("../scripts/custom_colors.json", "r") as json_file:
        color = json.load(json_file)  # Dictionary for custom color mapping

#START SCRIPT
#fetch dataframe
df = fetch_map_df(year = year, region=region, plotting_parameters=plotting_parameters)

#modify dataframe if necessary
if "predicted_ecosystem" in df.columns:
    df[['ecosystem_level_1', 'ecosystem_level_2', 'ecosystem_level_3']] = df['predicted_ecosystem'].str.split('-', expand=True)
    df["ecosystem_level_3"] = df["ecosystem_level_2"]+"-"+df["ecosystem_level_3"]
    if level == 1:
        plotting_col = "ecosystem_level_1"
    elif level == 2:
        plotting_col = "ecosystem_level_2"
    elif level == 3:
        plotting_col = "ecosystem_level_3"
    else:
        plotting_col = "predicted_ecosystem"
else:
    plotting_col=plotting_parameters[0]   
    
# Output
basemap_imshow_discrete_or_heatmap(
    df["lat"], 
    df["lon"], 
    df[plotting_col], 
    lat_min=df['lat'].min(), 
    lat_max=df['lat'].max(), 
    lon_min=df['lon'].min(), 
    lon_max=df['lon'].max(),
    title=plotting_parameters[0],
    scale=scale,
    color=color
)
