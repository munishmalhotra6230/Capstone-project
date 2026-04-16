# Network Intrusion Detection Engine (NIDS)

## Overview
Next-generation Machine Learning framework engineered to analyze, detect, and isolate malicious network traffic patterns utilizing the CICIDS 2017 flow baseline dataset. This tool processes raw packet capture (`.pcap` or `.pcapng`) files and scans them for malicious threats using a dual-phase Machine Learning pipeline.

## Features
- **Data Ingestion and Feature Extraction**: Extracts 80 raw networking features from PCAP files utilizing `scapy`.
- **Optimal Feature Selection**: Drops unneeded metrics to a 36-optimal-node correlation to improve speed and performance.
- **Phase 1: Binary Gateway**: High accuracy (~99.1%) binary classifier evaluating safe against malicious traffic patterns.
- **Phase 2: Threat Classifier**: Multiclass Neural parameter categorizing the targeted specific threat (e.g., Bot, DDoS, PortScan, Infiltration).
- **Automated Health Monitoring**: Provides active insight on the degradation of the confidence mean in production, flagging the user if retraining the neural model is required.

## Installation
Ensure you have Python installed. Install the necessary dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application
To run the NIDS dashboard locally:

```bash
python main.py
```
Open your browser and navigate to `http://localhost:5000/`.

## Project Structure
- `main.py`: The entry point for the Flask web application.
- `models/`: Contains the pre-compiled `.pkl` models for the Phase 1 and Phase 2 executions.
- `src/`: Houses the complex correlation metric extraction, decoding raw packets (`Captured.py`).
- `model_health/`: Time-based tracking and confidence checking utilities for neural core health.
- `template/`: UI components and Web templates rendering the Security Dashboard.
