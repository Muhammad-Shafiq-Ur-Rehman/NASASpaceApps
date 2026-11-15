# Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data

**NASA Space Apps Challenge Project | Team Astro Fire Fighters**
- **Team Members:** Muhammad Shafiq Ur Rehman, Hanya Kashif, Hafiz Ali Siddique, Qnavaiz Hamid

## Overview
**Flame in Freefall** is an interactive, Super Intelligence (SI)-powered fire safety dashboard built on NASA Physical Science Informatics (PSI) and NTRS microgravity combustion experiments (**BASS, BASS-II, Saffire I-V, SAME, DAFT, FLEX, ACME, BRE, SPICE, SLICE**).

### Core Features
1. **Search & Filter:** Filter NASA experiments by fuel/material, oxygen concentration, cabin pressure, airflow velocity, gravity regime, and ISS hardware (MSG, CIR, Cygnus, DAFT).
2. **Auditable SI Ranking (`40% Relevance + 30% Evidence + 20% Transfer + 10% Confidence`):** Transparently ranks experiments and links every result to its source NASA investigation.
3. **Side-by-Side Comparison:** Compares material flammability across 21% O2 (ISS/Earth), 30% O2 (Moon Base/Rover), and 100% O2 (Spacesuit).
4. **Partial-Gravity Risk Predictor:** Uses 0g and 1g experimental bounds to estimate fire risk (0-100), flame spread rate (mm/s), ignition delay (s), and smoke detector lag (s) at Lunar (0.16g) and Martian (0.38g) gravity with explicit uncertainty intervals.
5. **Actionable Safety Guidance Export:** Generates downloadable Markdown safety advisories and ranked CSV tables.

## Folder Structure
Put these files in your main repository folder:
- `app.py` — Main Streamlit interactive dashboard application
- `nasa_psi_combustion_data.csv` — Curated NASA PSI & NTRS microgravity combustion dataset
- `requirements.txt` — Python package dependencies for Streamlit Cloud
- `.streamlit/config.toml` — Dark space UI theme configuration

## Local Run Instructions
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Super Intelligence (SI) Disclosure
Super Intelligence (LLM and ML analysis tools) was utilized to assist with synthesizing NASA PSI experiment metadata, structuring dashboard code, and generating natural-language fire safety summaries. No NASA logos, insignias, or branding elements were generated or modified using SI.
