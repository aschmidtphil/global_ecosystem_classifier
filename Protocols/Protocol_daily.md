# Protocol #1

**Date: Friday, 25.10.2024**

| **Role**           | **Team Member**                                |
|--------------------|------------------------------------------------|
| Literature Research | Noah                                          |
| Data Acquisition & Maintenance | Alexander                          |
| Web Development & Database Maintenance | Soma                      |
| Communications & Project Management | Heiko                         |

### Potential Ecosystem Classification:

<table >
    <tr>
        <th rowspan="5">Forest Ecosystems</th>
        <td><b>Tropical Rainforest</b></td>
        <td>- Sub-Canopy: Ferns, lianas, palms, epiphytes <br> - Canopy Layer: Kapok trees, strangler figs <br> - Forest Floor: Decomposing matter, fungi</td>
    </tr>
    <tr>
        <td><b>Mangrove Forest</b></td>
        <td>- Red mangrove, black mangrove, crabs, mudskippers</td>
    </tr>
    <tr>
        <td><b>Peat Swamp Forest</b></td>
        <td>- Sago palm, peat soil, endemic fish, fungi</td>
    </tr>
    <tr>
        <td><b>Temperate Forest</b></td>
        <td>- Deciduous: Oak, maple, birch <br> - Coniferous: Pine, spruce, fir</td>
    </tr>
    <tr>
        <td><b>Boreal (Taiga) Forest</b></td>
        <td>- Cold-Tolerant Trees: Spruce, fir <br> - Migratory Birds: Swans, cranes</td>
    </tr>
    <tr>
        <th rowspan="3">Grassland Ecosystems</th>
        <td><b>Savanna</b></td>
        <td>- Grasses: Elephant grass, bluestem <br> - Herbivores: Elephants, giraffes</td>
    </tr>
    <tr>
        <td><b>Temperate Grasslands</b></td>
        <td>- Prairie Grasses: Buffalo grass, wheatgrass <br> - Bird Species: Grouse, hawks</td>
    </tr>
    <tr>
        <td><b>Tundra</b></td>
        <td>- Low Shrubs: Willows, dwarf birch <br> - Migratory Animals: Caribou, arctic hare</td>
    </tr>
    <tr>
        <th rowspan="3">Desert Ecosystems</th>
        <td><b>Hot Desert</b></td>
        <td>- Drought-Resistant Plants: Cacti, sagebrush <br> - Nocturnal Animals: Fennec fox</td>
    </tr>
    <tr>
        <td><b>Cold Desert</b></td>
        <td>- Winter Annuals: Cheatgrass, shadscale <br> - Adapted Mammals: Mule deer</td>
    </tr>
    <tr>
        <td><b>Semi-Arid Desert</b></td>
        <td>- Low-Water Plants: Agave, mesquite <br> - Small Mammals: Kangaroo mouse</td>
    </tr>
    <tr>
        <th rowspan="3">Aquatic Ecosystems</th>
        <td><b>Freshwater</b></td>
        <td>- Lakes & Ponds: Algae, lily pads <br> - Rivers & Streams: Catfish, salmon</td>
    </tr>
    <tr>
        <td><b>Marine</b></td>
        <td>- Coral Reefs: Coral polyps, clownfish <br> - Open Ocean: Plankton, sharks</td>
    </tr>
    <tr>
        <td><b>Brackish Water</b></td>
        <td>- Mangroves, salt marshes, tidal flats</td>
    </tr>
    <tr>
        <th rowspan="3">Mountain and Alpine Ecosystems</th>
        <td><b>Montane Forest</b></td>
        <td>- Evergreen Trees: Pine, fir, cedar <br> - Highland Mammals: Mountain lion</td>
    </tr>
    <tr>
        <td><b>Subalpine Zone</b></td>
        <td>- Dwarf Shrubs: Alpine willow, bilberry <br> - Pollinators: Bumblebees, beetles</td>
    </tr>
    <tr>
        <td><b>Alpine Tundra</b></td>
        <td>- Cushion Plants: Moss campion <br> - Cold-Adapted Animals: Snow hare, pika</td>
    </tr>
</table>

## MVP
- A website that shows the development of ecosystems over recorded time.

## Goal
- Show a trend of ecological parameters over time.

## Validation
- Examples: Great Green Wall Initiative (Africa), Chinese Loess Plateau Rehabilitation, Marker Wadden (The Netherlands). See main README

## Database Setup
- *Still pending*

---
---
---

# Protocol #2

**Date: Monday, 28.10.2024**

### Daily Goal Set
#### Alexander
- Potential database sources research ([Earthdata](https://www.earthdata.nasa.gov/))

#### Noah
- Potential database sources research ([Meteostat](https://meteostat.net/en/))

---

### Result
- Meteostat GitHub data records suitable
- Missing weather station data gets replaced by nearby weather station data

---

#### Soma
- Potential webpage design and operation

---

#### Heiko
- Prepare presentation for upcoming stakeholder "Check-In"
- Timeline notation

---
---
---


# Protocol #3

**Date: Tuesday, 29.10.2024**

### Noah, Alexander, and Heiko
- Gathering data sources and preparing data APIs to present weather station data for the year 2020
- Uploaded in "Scripts" on GitHub

---

### Soma
- Created frontend and backend modules in the web app to communicate between APIs

---
---
---

# Protocol #4

**Date: Wednesday, 30.10.2024**

### Preparation and Data Gathering
- Using data sources to extract data for further processing

---

### Stakeholder Check-In Presentation
- Presenting our capstone project to Jugnu (Coach) and Matthias Motl (Data Analytics Team Lead)
- Clarify realistic goals within the capstone project timeframe and establish minimum results for the end of the capstone phase

---

### Data Extraction
- Set filtering and formatting script to timerange in interactive exploring (with Meteostat database)

---

### Webpage
- Created a map to interact with and visualize information using landmarks

---

### Globe Map
- Created an albedo map for each month of the year

---
---
---

# Protocol #4

**Date: Thursday, 31.10.2024**

| Member | Task | Remarks | 
|-|-|-|
|Heiko| - | - Public holiday in Hamburg|
|Soma| Web application | - Established front end of website and entry points <br>  - Coordinates can now be fed into the map to plot parameters <br> - working on resolving remaining db log in issues for Noah|
|Alex| Data acquisition earth data| - Improved earthaccess data sourcing [`.ipynb`](/scripts/earthacess_mastertable_2020.ipynb) for [GLDAS](/protocols/Protocol_earthaccess_GLDAS.md) <br> - started to address `.h5` file assessing for illumination data for [VIIRS](/protocols/Protocol_earthdata.md) |
|Noah| Pipeline setup  & <br> Github cleanup| - finished [`meteostat_sourcing.py`](/scripts/meteostat_sourcing.py) to automatically source weather data to Postgres database. Script could not be initiated due to connection issues  <br> github cleanup for protocols folder (see below)|

#### Git hub state as of now:
 - [`/protocols`](/protocols/) now contains project based protocols including documentation for the sourcing of satellite data
    - general overview of NASAs Earth Data including information on API setup and Night lights overview: [`protocols/Protocol_earthdata.md`](/protocols/Protocol_earthdata.md) 
    - specialised information onf the GLADS project featuring climate data: [`protocols/Protocol_earthaccess_GLDAS.md`](/protocols/Protocol_earthaccess_GLDAS.md)
    - The information on how to calculate the classifier should be deposited and updated in [`protocols/classifier_definitions.md`](/protocols/Protocol_classifier_definitions.md)
    - The daily protocls were summarised in this file and individual files deleted

#### Next steps: 
- Run pipelines for GLDAS and meteostat downloads and upload on SQL directly through remote desktop `.py` scripts @aschmidtphil @pasumaso @NoahKuertoes
- Write pipeline for DNB illumination data @aschmidtphil
- Research data for Chlorophyll content (optional) @aschmidtphil
- Start integration of parameters on webpage @pasumaso
- Idependently calculate ecosystem definition @NoahKuertoes
- Update [README](/README.md) sections `Literature research`, `Data acquisition`, `Web integration` for the status quo @HeikoFrae
- Upload and improve stakeholder presentations @HeikoFrae
  
---
---
---
# Protocol #5

**Date: Wednesday, 06.11.2024**

#### Stakeholder presentation no.2

Discussion on possible future targets for next presentation. Potential interests to focus on will be "Great Green Wall" in Africa to see different states of vegetation and changes in the weather data through the years to show future solutions on conserving nature projects. Next goal to present is the classification of ecosystems and map based statements for that.

Site note: Dropped the idea to implement the extinction rate of species   

#### Database scripts

Working on a script for maximum and minimum latitude of landscapes.
Plotting data for Africa in 2020 and 2015.

#### Webpage improvements

Working on webpage scattering in region limitation for weather station locations.   

#### Map based plotting
Working on visualisation and implementing nighttime lights and illumination to determine urban areas.

---
---
---
# Protocol #6

**Date: Thursday, 07.11.2024** 

#### Merge Meteostat into SQL

Uploading and merge meteostat Data via python scripts on SQL. Debugging Python scripts and updated permissions.




