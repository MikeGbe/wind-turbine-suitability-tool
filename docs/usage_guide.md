## 💡 How to Use

### Option 1: ArcGIS Toolbox

1. Open ArcGIS Pro.
2. Load `SolarLandSuitability.tbx` from `toolbox/`.
3. Select input datasets using the prompt interface.
4. Choose a county from the dropdown.
5. Run tool. Output will include raster maps and parcel suitability tables.

### Option 2: Python Script

1. Ensure ArcGIS Pro’s Python environment is active.
2. Edit dataset paths in `scripts/land_suitability.py`.
3. Run the script to produce the same outputs as the toolbox.

## 💻 Requirements

- ArcGIS Pro 2.9+
- ArcPy
- Python 3.x
- Standard vector and raster data for Virginia counties

## 🔬 Sample Data

Basic datasets for testing are included in `sample-data/`. These are clipped and anonymized examples for public sharing.

## 📊 Outputs

- Suitability rasters
- Parcel-level suitability percentage
- Final vector layer of suitable parcels with area statistics

## 📄 License

MIT License — Free to use and adapt with credit.

[technical report](report.pdf) for project design, methodology, and setup steps.
