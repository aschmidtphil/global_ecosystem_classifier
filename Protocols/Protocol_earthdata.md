# NASA's EarthData Summary

## Overview
[NASA's EarthData](https://www.earthdata.nasa.gov/) provides access to a wide range of Earth science data from satellites, aircraft, and field measurements. It is a valuable resource for climate, environmental, and atmospheric research, enabling users to explore and analyze global environmental changes.

---

## Key Datasets and Their Applications

### [GLDAS Noah Land Surface Model](https://ldas.gsfc.nasa.gov/gldas)
The Global Land Data Assimilation System (GLDAS) Noah Land Surface Model uses satellite and ground-based observations to simulate land surface conditions, such as soil moisture, temperature, and energy fluxes.

| Model Version | Description                                    | Resolution         | Data Availability      | Data URL                                                                                  |
|---------------|-------------------------------------------------|--------------------|-----------------------|-------------------------------------------------------------------------------------------|
| **V2.1**      | Monthly data, useful for modern climate research | 0.25° x 0.25°      | 2000 - 2024           | [GLDAS Noah L4 V2.1](https://disc.gsfc.nasa.gov/datasets/GLDAS_NOAH025_M_2.1/summary)    |
| **V2.0**      | Historical data for long-term climate analysis  | 0.25° x 0.25°      | 1948 - 2014           | [GLDAS Noah L4 V2.0](https://disc.gsfc.nasa.gov/datasets/GLDAS_NOAH025_M_2.0/summary)    |

**Applications**:
- Monitoring soil moisture and temperature trends
- Researching land-atmosphere interactions
- Assessing environmental changes over short and long-term periods

---

### [VIIRS Nighttime Day/Night Band (DNB)](https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/VNP46A4/#overview)
The VIIRS (Visible Infrared Imaging Radiometer Suite) Nighttime DNB dataset captures illumination levels at night, making it valuable for urban and environmental studies.

- **Data Source**: [Suomi NPP satellite](https://en.wikipedia.org/wiki/Suomi_NPP)
- **Spatial Resolution**: 0.1° for latitude and longitude
- **Temporal Resolutions**:
  - **Nightly**: Illumination for specific nights
  - **Monthly**: Average nighttime lights over a month
  - **Annual**: Yearly aggregates of nighttime light data

**Use Cases**:
- Tracking urban development and human activity
- Assessing light pollution's ecological impact
- Supporting disaster response and monitoring power outages

---

### [MODIS (Moderate Resolution Imaging Spectroradiometer)](https://modis.gsfc.nasa.gov/about/)
MODIS provides data critical for studying Earth’s surface reflectance and monitoring vegetation, oceanic conditions, and the atmosphere.

- **Key Parameters**:
  - **Surface Temperature**: For climate modeling
  - **Albedo**: Measures surface reflectivity
  - **Chlorophyll Content**: Monitors ocean productivity and detects algal blooms

**Applications**:
- Evaluating vegetation health
- Researching atmospheric and oceanic processes
- Energy balance studies

---

### [SRTM (Shuttle Radar Topography Mission)](https://eospso.nasa.gov/missions/shuttle-radar-topography-mission)
SRTM delivers global elevation data, useful for mapping Earth’s topography and conducting geological and environmental assessments.

**Applications**:
- Flood risk analysis and water flow modeling
- Geological and topographic studies
- Infrastructure planning and hazard assessments

---

## API Overview: 

Using the example of the "Nighttime Illumination Data"

### API Framework
A FastAPI-based API fetches nighttime illumination data using NASA’s VIIRS dataset, offering functionality for various temporal resolutions and global coordinates.

### Key Endpoints
| Endpoint            | Method | Description                                              |
|---------------------|--------|----------------------------------------------------------|
| `/night_illumination` | POST   | Retrieves illumination data for specified coordinates and temporal resolution |
| `/earliest_date`    | GET    | Provides the earliest available date for the dataset     |

**Parameters for `/night_illumination`**:
- `resolution`: Degree increment for coordinates (default: 0.1°)
- `date`: Required for nightly and monthly resolutions
- `temporal_resolution`: Options include `'nightly'`, `'monthly'`, and `'annual'`

### Implementation Notes
- **Access Requirements**: Register on NASA EarthData and obtain an API key.
- **Metadata Access**: Use metadata APIs to determine data availability and earliest dates.

---

## Data Access and Best Practices

### Getting Started
1. **Register for an Account**: Sign up on [EarthData](https://urs.earthdata.nasa.gov) to gain access.
2. **Authentication**: Use API tokens for secure data access.
3. **Efficient Data Queries**: Specify date ranges and geographic boundaries clearly to optimize API usage.

### Best Practices
- **Rate Limiting**: Avoid exceeding API limits; implement caching where possible.
- **Data Formats**: Familiarize yourself with formats like NetCDF and HDF for seamless data handling.
- **Data Visualization**: Use tools like Python’s `matplotlib` and GIS software for analysis and mapping.

---

## Example Libraries and Tools
| Library    | Purpose                                    |
|------------|---------------------------------------------|
| `FastAPI`  | Building RESTful APIs                      |
| `Pandas`   | Data analysis and manipulation             |
| `Requests` | Making HTTP requests to APIs               |
| `xarray`   | Handling multi-dimensional scientific data |

### Running the API
Use `uvicorn` to start your FastAPI application:
```bash
uvicorn script_name:app --reload
```

## Further reading

|Source|Description|
|-|-|
|[Giovanni](https://giovanni.gsfc.nasa.gov/giovanni/#service=TmAvMp&starttime=1996-11-01T00:00:00Z&endtime=1997-12-31T23:59:59Z)|EarthData library for open access satellite data|
|[Earth Data Data Catalog](https://earthdata.nasa.gov/data/catalog)| Similar to the Giovanni library: overview of available datasets|
|[Black Mable Documentation](https://ladsweb.modaps.eosdis.nasa.gov/api/v2/content/archives/Document%20Archive/Science%20Data%20Product%20Documentation/VIIRS_Black_Marble_UG_v1.3_Sep_2022.pdf)|User guide for interpreation of night illumination data|
|[VIIRS DNB Download](https://forum.earthdata.nasa.gov/viewtopic.php?t=527)| Forum entry on how to download and access `.hdf` and `.h5` files used by VIIRS|
|[Change in Night Lights between 2013 and 2023](https://svs.gsfc.nasa.gov/5276/)|Exemplary visualisualisation of the night illumination data set|
