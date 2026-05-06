Capstone Project — Network Packet Analysis & Monitoring
=======================================================

Summary
-------
This project analyzes network traffic captured in PCAP/PCAPNG files, runs a two-stage detection/classification pipeline, and supports both user-driven file analysis via a small Flask web app and live monitoring via a Streamlit dashboard.
# Diagram 
![alt text](static/images/diagram.png)
Key features
- File-based analysis: upload a PCAP to the web UI (`main.py`) and receive flow-level predictions.
- Real-time monitoring: a Streamlit dashboard (`dashboard.py`) visualizes live packet capture metrics and detected attacks.
- Two-stage model pipeline: `models/pipeline.py` loads two pickled models (`model_phase1.pkl` for binary detection and `model_phase2.pkl` for attack-type classification).
- Retraining utilities: `retraning_pipeline/retraining_pipeline.py` contains scripts to retrain models from CSV data.

Requirements & setup
--------------------
- Python 3.8+ and the packages in `requirements.txt`.
- Scapy and packet capture dependencies. On Windows, install Npcap (winpcap replacement) and run with appropriate privileges to allow live capture.

Quick start (Windows example)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run the web upload app (Flask)
python main.py

# Run the real-time dashboard (Streamlit)
streamlit run dashboard.py
```

Project layout (important files)
--------------------------------
- `main.py` — Flask web application with routes:
  - `/` : index page (template/index.html)
  - `/predicting` : upload form (uses Flask-WTF) that saves uploaded PCAPs to `uploads/` and calls `src.Captured.analyze_pcap()`
  - `/model` : simple model metadata page (templates/model.html)

- `dashboard.py` — Streamlit app for live monitoring. When the user clicks "Start Live Capture" it calls `streaming.producer.producer_pcap()` which runs a Scapy sniff, writes a temp PCAP, and calls `src.Captured.analyze_pcap()` to produce metrics shown in the UI.

- `src/Captured.py` — Core PCAP parsing and feature extraction:
  - `extract_features(pkts)` converts packet lists into the flow-feature dictionary expected by the ML pipeline.
  - `analyze_pcap(pcap_file)` groups packets into flows, converts them to a DataFrame, runs `models.pipeline.Full_pipeline`, and returns prediction counts, attack details, and a `model_health` status (via `model_health/timebased.py`).
  - `convert_pcap_to_csv()` helper to export flow features to CSV for training.

- `models/pipeline.py` — Loads `model_phase1.pkl` and `model_phase2.pkl` and provides `Full_pipeline` which:
  - Cleans and selects features
  - Runs phase1 detection (binary) to find attack flows
  - Runs phase2 classification on attack flows to label attack types

- `streaming/producer.py` — Uses Scapy to sniff packets, stores a temporary pcap, calls `analyze_pcap()`, and returns results. It cleans up the temp file after analysis.

- `retraning_pipeline/retraining_pipeline.py` — Scripts and classes to retrain the phase1 and phase2 models from CSV datasets and save new pickle files.

- `model_health/timebased.py` — Simple time/confidence-based health checks used to decide whether models need retraining.

- `template/` — HTML templates used by the Flask app: `index.html`, `prediction.html`, `model.html`.

Two workflows (detailed)
------------------------
1) Web upload analysis (file-based)

Purpose: let a user upload a traffic capture and receive an analysis report and predicted attack types.

Flow (what `main.py` implements):
- User visits the web UI (`/`) and opens the upload view (`/predicting`).
- User uploads a PCAP/PCAPNG file; Flask saves it to `uploads/`.
- `main.py` calls `src.Captured.analyze_pcap(filepath)` which:
  - Reads packets with Scapy (`rdpcap`).
  - Groups packets into flows, extracts features per flow (`extract_features`).
  - Builds a DataFrame and runs `Full_pipeline.run()` which returns counts and attack entries.
  - Appends `model_health` status (via `model_health/timebased.timebased_model_health`) to the results.
- The Flask route returns `template/prediction.html` populated with counts, attack details, and model status.

How to run (example):

```powershell
# Start Flask app
python main.py
# Open: http://127.0.0.1:5000/ and upload a PCAP on the Predicting page
```

Notes:
- Uploaded files are saved to `uploads/` — you can process them offline by calling `src/Captured.analyze_pcap()` from a script.
- The upload flow depends on Flask-WTF form validation; adjust `SECRET_KEY` in `main.py` for production.

2) Real-time monitoring (dashboard-driven)

Purpose: capture live traffic in small batches, run online inference, and visualize metrics and alerts in near real time.

Flow (what `dashboard.py` implements):
- Start the dashboard with Streamlit: `streamlit run dashboard.py`.
- Click "Start Live Capture" in the Streamlit sidebar.
- The dashboard calls `producer_pcap(packet_count=60)` which:
  - Uses Scapy `sniff(count=packet_count)` to collect a short batch of packets.
  - Writes a temporary PCAP file and calls `src.Captured.analyze_pcap(tmp_path)`.
  - Receives the result (normal/attack counts, attack details, model health) and returns it to the dashboard.
- The dashboard updates the displayed metrics and tables, and includes a simple stop button.

How to run (example):

```powershell
# Run the dashboard
streamlit run dashboard.py
# Click 'Start Live Capture' in the UI
```

Notes & caveats:
- Live capture requires OS-level packet capture support (Npcap on Windows) and appropriate privileges — run as admin or install packet capture libraries correctly.
- On Windows, Scapy’s live capture can be limited — for robust deployments consider using a capture agent that writes PCAPs to a folder and a separate process that reads them.
- You can also run `streaming/producer.py` directly from a script to produce analysis runs if you prefer a non-interactive loop.

Maintenance & next steps
------------------------
- Rename `retraning_pipeline` → `retraining_pipeline` to fix the typo and make imports predictable.
- Add a small `CONTRIBUTING.md` with development steps and how to regenerate `model_phase1.pkl`/`model_phase2.pkl` from training data.
- Add command-line flags to `main.py` (port, debug, upload dir) and to the retraining scripts for automated pipelines.

Questions?
---------
Tell me if you want me to:
- (A) Rename `retraning_pipeline` to `retraining_pipeline` and update imports.
- (B) Add a short example script that runs `src/Captured.analyze_pcap()` on samples in `uploads/`.
- (C) Add a `CONTRIBUTING.md` and simple CI/test commands.
Capstone Project — Network Packet Analysis & Model Pipeline
==========================================================

Overview
--------
This repository implements a data pipeline and model workflow for analyzing captured network packets, training and evaluating models, and serving predictions (including a dashboard and templates for web-based interaction). It includes exploratory analysis notebooks, preprocessing and modeling code, scripts to simulate/stream packets, and utilities for retraining and model health checks.

Quick start
-----------
- Prerequisites: Python 3.8+, git, and optionally a virtual environment tool.
- Create and activate a virtual environment (Windows example):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- Common flows:
  - Explore the data with the notebooks in `eda/`.
  - Train and evaluate models using files in `models/`.
  - Run streaming/producer to feed packet data into the pipeline.
  - Start the dashboard or run `main.py` as the project's entry point (if configured for your deployment).

Repository layout and file descriptions
-------------------------------------
Top-level files
- `README.md`: This file — project overview and usage.
- `main.py`: Project entry point. Typically launches the application or orchestrates pipeline steps.
- `dashboard.py`: Script to start an interactive dashboard (visualizations and model insights).
- `requirements.txt`: Python package dependencies for the project.
- `Test_results/Test_results.txt`: Saved test outputs or evaluation run results.

Notebook and data directories
- `eda/`: Exploratory Data Analysis notebooks and CSV snapshots.
  - `data_man.ipynb`, `Eda_new.ipynb`, `eda_phase2.ipynb`, `model_evaluation.ipynb`: Notebooks used to explore data, run feature engineering experiments, and evaluate models.
  - `phase2.csv`, `phase2_cleaned.csv`, `cleaned_phase1_dataset.csv`: Dataset snapshots produced during EDA and cleaning.

Data and sample captures
- `uploads/Sample.pcapng` and `src/Sample.pcapng`: Example packet capture files you can use for testing and development.

Source code
- `src/Captured.py`: Utilities or classes for parsing/representing captured network packets (PCAP parsing helpers).

Streaming and producers
- `streaming/producer.py`: Simulates or streams packet data into the pipeline. Use this to generate real-time input for testing the streaming components.

Models and pipelines
- `models/pipeline.py`: The model training and inference pipeline. This is where feature extraction, model training, persistence (save/load), and prediction logic live.

Retraining and model maintenance
- `retraning_pipeline/retraining_pipeline.py`: Orchestrates automatic or scheduled retraining of models when new data arrives (note: folder name has a typo — `retraning_pipeline` — consider renaming to `retraining_pipeline` for clarity).

Model health and utilities
- `model_health/timebased.py`: Tools for validating model behavior over time, drift detection, or time-based performance checks.

Web/templates and static UI
- `template/`:
  - `index.html`, `model.html`, `prediction.html`: HTML templates for the web interface for prediction and model display.
- `static/images/`: Images or assets used by the dashboard or web UI.

How to use (common tasks)
-------------------------
- Run EDA notebooks: open the notebooks in `eda/` using Jupyter or VS Code to inspect the datasets and reproduce analysis steps.
- Train a model (typical): run `models/pipeline.py` (or follow the notebook instructions) to preprocess, train, and save model artifacts.
- Simulate streaming input: run `python streaming/producer.py` to emit packet events into the pipeline for testing real-time behavior.
- Retrain models: run `python retraning_pipeline/retraining_pipeline.py` to execute the retraining workflow (adjust schedule/params as needed).
- Start dashboard: run `python dashboard.py` (if implemented) to launch the visual dashboard for model metrics and results.

Workflows
---------
1) Web upload analysis (user-driven file analysis)

Overview:
- This workflow allows a user to upload a captured traffic file (PCAP/PCAPNG) via the web interface and get an analysis report and prediction results.

Typical flow:
- User opens the web UI (served by your web app) and navigates to the upload page (UI templates: `template/index.html` or a dedicated upload view).
- The user selects a traffic file (for example `uploads/Sample.pcapng`) and submits the form.
- Backend receives the uploaded file and saves it to a temporary location (e.g., `uploads/` or `live_packets/`).
- Backend parsing: the upload handler calls utilities in `src/Captured.py` to parse the PCAP and extract session/packet-level features.
- Feature pipeline: extracted features are passed to `models/pipeline.py` for preprocessing and inference (or for running the same feature transforms used during training).
- Results: predictions and analysis metrics are written to a results object or file, then displayed back to the user using `template/prediction.html` or a results page.

Commands / entrypoints (example):

```powershell
# Start the web app (if `main.py` provides a server)
python main.py

# Or run a minimal upload handler endpoint if implemented in your web framework
# Upload files via the UI at http://localhost:PORT/ (see project-specific docs)
```

Notes:
- If a web backend is not yet implemented, a simple local script can mimic the flow: place a PCAP in `uploads/` and run a small Python script that imports `src/Captured` and `models/pipeline` to process the file.

2) Real-time monitoring (dashboard-driven streaming)

Overview:
- This workflow supports monitoring of live packet streams and real-time model inference, visualized via `dashboard.py`. It's intended for continuous observation, alerts, and model-health metrics.

Typical flow:
- Start the packet producer or data source: `python streaming/producer.py` streams packets into your ingestion endpoint or writes them to a watched folder 
- Ingestion: a streaming component or process reads incoming packets, parses them (using `src/Captured.py`) and computes features in real time.
- Prediction: each feature vector is fed into the active model (from `models/pipeline.py`) for online inference.
- Dashboard: run `python dashboard.py` to start the monitoring UI that subscribes to the live stream or reads from a metrics store and shows live charts, recent predictions, and alerts.
- Model health: `model_health/timebased.py` provides routines for tracking metrics over time (latency, accuracy proxies, drift indicators) and can surface warnings on the dashboard.

Commands / entrypoints (example):

```powershell

# Start the dashboard to view the live stream and metrics
python dashboard.py
```




Next steps you might want me to do
---------------------------------
- Link `main.py` to a clear run example (add CLI flags or a short wrapper).
- Rename `retraning_pipeline` to `retraining_pipeline` and update imports.
- Add a brief `CONTRIBUTING.md` with dev setup and common commands.

Contact / Author
----------------
If you'd like me to update any file references, adjust wording, add run examples, or rename directories and fix imports, tell me which changes to make next.

License
-------
Add a license file if you intend to share this project publicly (e.g., `LICENSE` with MIT or Apache-2.0).
