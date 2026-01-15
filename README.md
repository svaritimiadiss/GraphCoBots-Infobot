# GraphCoBots-Infobot

**GraphCoBots‑Infobot** is a conversational AI chatbot designed to provide structured, in‑depth information for museum and cultural heritage contexts. The chatbot focuses on the **Nikos Kazantzakis Museum (Crete, Greece)** and is part of the broader **GraphCoBots** research framework, which investigates distributed, collaborative, and Knowledge Graph–driven multi‑chatbot systems for museums.

The system combines rule‑based conversational logic, Knowledge Graph data, and modular deployment practices to support scalable and reusable museum chatbot services.

---

## Research Context

GraphCoBots‑Infobot is developed as part of an academic research effort exploring:

* Knowledge Graph–based conversational AI
* Distributed and collaborative chatbot architectures
* Intelligent access to cultural heritage information
* Human‑centered interaction design for museums

The system has been used as an experimental and evaluation platform in peer‑reviewed research publications.

---

## Repository Structure

```
.
├── actions/                # Automation and workflow configurations
├── data/                   # Knowledge Graph data, dialogue data, or exports
├── scripts/                # Utility and helper scripts
├── config.yml              # Bot configuration
├── domain.yml              # Conversational domain (intents, responses, entities)
├── endpoints.yml           # External service endpoints
├── credentials.yml         # Credentials file (NOT committed; user‑provided)
├── docker-compose.yml      # Docker Compose setup
├── Dockerfile              # Docker image definition
├── index.html              # Web interface or embed page
├── server.sh               # Startup script
├── LICENSE                 # Apache License 2.0 (source code)
├── LICENSE-DATA            # CC BY 4.0 (data and Knowledge Graphs)
└── README.md               # Project documentation
```

---

## Prerequisites

Before running the system, ensure you have:

* Docker and Docker Compose **(recommended)**, or
* Python 3.x environment (if running locally)
* Proper credentials for any external services (configured in `credentials.yml`)

---

## Configuration

### `config.yml`

Contains general chatbot configuration parameters such as ports, logging, and runtime options.

### `domain.yml`

Defines the conversational domain, including intents, entities, and responses relevant to the museum context.

### `endpoints.yml`

Specifies connections to external services or APIs used by the chatbot.

### `credentials.yml`

Stores sensitive information (API keys, tokens). **This file must not be committed to Git.**

---

## Running the Chatbot

### Option 1: Docker (Recommended)

```bash
docker compose up --build
```

This will build the required images and start the chatbot service using the predefined configuration.

---

### Option 2: Local Execution

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the chatbot service:

```bash
./server.sh
```

(Adjust commands if your environment differs.)

---

## Knowledge Graph Usage

The chatbot is designed to consume museum knowledge structured as **Knowledge Graphs**. Graph data may be provided as:

* Cypher scripts (`.cypher` files)
* CSV imports
* Preprocessed datasets in the `data/` directory

For research reproducibility, Knowledge Graphs are provided in **declarative formats**, not as database binaries.

---

## Licensing

This repository is **dual‑licensed**:

* **Source code**: Apache License 2.0 (see `LICENSE`)
* **Data, Knowledge Graphs, and metadata**: Creative Commons Attribution 4.0 International (CC BY 4.0) (see `LICENSE-DATA`)

Users must comply with the terms of each license depending on the material used.

---

## Citation

If you use this software or its data in academic work, please cite the relevant GraphCoBots publications.

A `CITATION.cff` file may be added for automated citation support.

---

## Notes for Researchers and Developers

* Do **not** commit credentials or secrets
* Use Docker for reproducible experiments
* Large binary files and database directories should not be tracked by Git
* Knowledge Graph updates should be versioned via `.cypher` or CSV files

---

## Contact

For questions related to research, collaboration, or reuse, please contact the repository owner via GitHub.

---

## Acknowledgements

This project is part of ongoing research on conversational AI and cultural heritage systems, with a focus on museum applications and intelligent visitor engagement.
