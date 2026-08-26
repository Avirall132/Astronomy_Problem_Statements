# Inter IIT Team Selection Test — ISRO Track

Comprehensive solution repository for the Inter-IIT Selection Test covering Chandrayaan-2 CLASS/XSM Lunar XRF analysis and GeoNLI Satellite Image Captioning.

## Structure & Deliverables

### Task 1: CLASS Lunar XRF Elemental Ratio Pipeline — Design & Visualization
- **Objective**: Visualize raw CLASS & XSM spectra for Mare and Highland footprints (`Footprint A`: 2022-04-15, `Footprint B`: 2021-08-28) and devise a comprehensive physical and computational pipeline for deriving lunar elemental ratios (Mg/Si, Al/Si, Ca/Si, etc.).
- **Folder**: `task1/`
  - Raw spectral visualization plots with observational notes.
  - In-depth pipeline design methodology document (`pipeline_design.md`).
  - Python scripts and Jupyter notebooks for FITS parsing and data filtering.

### Task 2: GeoNLI — Satellite Image Captioning & Evaluation
- **Objective**: Build an open-source vision-language model (VLM) pipeline on satellite imagery from the VRSBench dataset, generate captions for 6 benchmark images, evaluate against human-verified references using BLEU metrics, and conduct a detailed failure mode analysis.
- **Folder**: `task2/`
  - Open-source VLM inference pipeline code.
  - Generated captions and comparative BLEU score tables.
  - Concrete failure mode and remote sensing visual reasoning analysis.

---

## Environment Setup
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```
