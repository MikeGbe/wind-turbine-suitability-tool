# 🌬️ Wind Energy Land Suitability Tool (ArcGIS)

This project delivers a custom ArcGIS Toolbox and ArcPy script to automate the identification of land parcels suitable for wind turbine installation across Virginia. By integrating multiple geospatial datasets, environmental constraints, and user inputs, the tool streamlines suitability analysis for renewable energy development.

## 🎯 Objective

Identify land parcels free of environmental constraints and suitable for wind turbine installation. The tool performs preprocessing, raster reclassification, spatial masking, and final overlay analysis to return parcel IDs with area percentages that meet the criteria.

## 🧩 Features

- ArcGIS Toolbox with GUI prompts
- Python-based version of the tool (ArcPy)
- Input validation, error handling, and user warnings
- Repeatable county-level workflows
- Preloaded reclassification logic for slope and windspeed

## 📥 Inputs

| Layer Type     | Dataset Name            | Format         | Source |
|----------------|-------------------------|----------------|--------|
| Boundaries     | State & County Boundary | Vector         | [ArcGIS Hub](https://uofmd.maps.arcgis.com/home/item.html?id=29627d7c051a47dc8ce71b4484531ab3) |
| Elevation      | DEM (10m, 3DEP LiDAR)   | Raster         | [3DEP Lidar Explorer](https://apps.nationalmap.gov/lidar-explorer/) |
| Wind Speed     | Windspeed Raster        | Raster         | [NREL Wind Maps](https://www.nrel.gov/gis/wind-resource-maps.html), [Global Wind Atlas](https://globalwindatlas.info/en/download/gis-files) |
| Hydrology      | Wetlands, Rivers, Ponds | Vector (USFWS) | [FEMA NFHL](https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHLWMS/MapServer) |
| Infrastructure | Transmission Lines      | Vector         | [HIFLD GeoPlatform](https://hifld-geoplatform.opendata.arcgis.com/datasets/geoplatform::transmission-lines/) |
| Infrastructure | Substations, Power Plants | Vector       | [HIFLD GeoPlatform](https://hifld-geoplatform.opendata.arcgis.com/) |
| Ownership      | Land/Tax Parcels        | Vector         | Local or County GIS Portals |

## 🛠️ Methodology

1. **County Selection**
   - Filters spatial datasets using user-input county name.
   - Clips DEM and windspeed rasters to selected boundary.

2. **Raster Analysis**
   - Calculates slope from DEM.
   - Reclassifies slope and windspeed rasters.
   - Masks wetlands from resulting suitability layer.

3. **Infrastructure Buffering**
   - Buffers substations, power lines, and power plants.
   - Merges buffers to evaluate proximity suitability.

4. **Parcel Evaluation**
   - Intersects suitability raster with parcels.
   - Calculates pixel count and % of suitability per parcel.
   - 
