import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, LogNorm
from mpl_toolkits.basemap import Basemap
import matplotlib.patches as mpatches


def basemap_imshow_discrete_or_heatmap(lat, lon, plotting_col, lat_min, lat_max, lon_min, lon_max, title="default", scale ="linear", color = "default"):
    """
    Creates a Basemap plot using the provided lat, lon grid and a column of values to visualize.
    Adjusts colormap based on data type: uses a heatmap for numeric data and categorical colormap for strings.

    Parameters:
    - lat, lon: floats of latitude and longitude values for each grid cell
    - plotting_col: Series of values (numeric or strings) to plot at each lat-lon position
    - lat_min, lat_max: minimum and maximum latitude boundaries
    - lon_min, lon_max: minimum and maximum longitude boundaries
    - title: string for the plot title
    - scale: "linear" for no transformation or "log" for logarithmic transformation for float values
    - color: for linear data accepts a string for a matplotlib color libraries. Check with `plt.colormaps()`. For discrete values accepts are dictionary 
    """
    # Calculate aspect ratio based on latitude and longitude bounding box
    aspect_ratio = abs((lat_max - lat_min) / (lon_max - lon_min))
    fig_width = 10  # Set a base width
    fig_height = fig_width * aspect_ratio  # Adjust height to match aspect ratio

    # Create a DataFrame for pivoting to a consistent grid
    data = pd.DataFrame({'lat': lat, 'lon': lon, 'value': plotting_col})

    # Determine if values are numeric or categorical (strings)
    if pd.api.types.is_numeric_dtype(plotting_col):
        # If numeric, pivot the data and apply a heatmap colormap
        if color == "default":
            cmap = "viridis"
        else:
            cmap = color  
        
        pivoted_data = data.pivot(index='lat', columns='lon', values='value')
        
        # Apply logarithmic scaling if specified
        if scale == "log":
            vmin = pivoted_data[pivoted_data > 0].min().min()
            norm = LogNorm(vmin=vmin, vmax=pivoted_data.max().max())
        else:
            norm = None  # Linear scale
    
    else:
        # Categorical data handling remains the same
        unique_values = plotting_col.dropna().unique()
        value_to_int = {val: i for i, val in enumerate(unique_values)}
        data['value_int'] = data['value'].map(value_to_int)
        #color mapping
        if color == "default":
            cmap = ListedColormap(plt.cm.get_cmap('tab20').colors[:len(unique_values)])
        else:
            if color in plt.colormaps():
                return print("!Warning!:\t color your provided appears to be a heatmap colorscale\n\tnot applicable for discrete values")
            color = [color[val] for val in unique_values if val in color]
            cmap = ListedColormap(color)
        pivoted_data = data.pivot(index='lat', columns='lon', values='value_int')
        norm = None  # Norm not needed for categorical data
    
    # Ensure the latitude and longitude grid arrays are aligned with the pivoted data
    lat_grid = pivoted_data.index.values
    lon_grid = pivoted_data.columns.values
    int_col_reshaped = pivoted_data.values  # This now contains NaN for missing values

    # Set up figure with dynamically calculated size
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    
    # Flexible Basemap projection with dynamic bounding box
    m = Basemap(
        projection='cyl',  # Using cylindrical projection for better alignment
        llcrnrlat=lat_min, urcrnrlat=lat_max, 
        llcrnrlon=lon_min, urcrnrlon=lon_max, 
        resolution='i', ax=ax
    )
    m.drawcoastlines()
    m.drawmapboundary(fill_color='lightblue',zorder=0)  # Ocean color
    m.fillcontinents(color='lightgrey', lake_color='lightblue', zorder=1)  # Continent color, lake color to match ocean

    # Transforming lat-lon to Basemap coordinates and plotting
    x, y = np.meshgrid(lon_grid, lat_grid)
    c = ax.imshow(int_col_reshaped, extent=[lon_min, lon_max, lat_min, lat_max], 
                  origin='lower', cmap=cmap, aspect='auto', zorder=2, norm=norm)

    # Add legend for categorical data
    if not pd.api.types.is_numeric_dtype(plotting_col):
        handles = [mpatches.Patch(color=cmap(i), label=val) for i, val in enumerate(unique_values)]
        plt.legend(handles=handles, title="Categories", bbox_to_anchor=(1.05, 1), loc='upper left')
    
    if title == "default":
        plt.title('Basemap with Heatmap or Discrete Values')
    else: 
        plt.title(title)
    plt.colorbar(c, ax=ax, label='Value') if pd.api.types.is_numeric_dtype(plotting_col) else None
    plt.show()