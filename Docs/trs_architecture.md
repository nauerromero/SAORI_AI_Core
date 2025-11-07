# TRS Engine Architecture

## 🧩 Core Modules

| Module                        | Description                                                                 |
|------------------------------|-----------------------------------------------------------------------------|
| `emotional_inference_engine.py` | Calculates match score, applies penalties, and generates emotional messages |
| `vacancy_query.py`           | Filters vacancies by modality, location, and technical stack                |
| `rrhh_response.py`           | Generates final HR-ready messages with follow-up tags                       |
| `profile_simulator.py`       | Creates simulated candidate profiles with emotional and technical traits    |

## 📁 Data Inputs

- `profiles.json` — Candidate profiles with emotional state and stack vector  
- `vacancies.json` — Job listings with modality, urgency, and required stack  
- `emotional_states.json` — Emotional tone definitions and message templates

## 📊 Outputs

- `emotional_log.csv` — Log of emotional responses and match scores  
- `rrhh_registry.md` — HR routing records with follow-up type and observations

## 🔁 Flow Diagram

```mermaid
graph TD
    A[profiles.json] --> B[vacancy_query.py]
    B --> C[vacancies.json]
    C --> D[emotional_inference_engine.py]
    D --> E[emotional_log.csv]
    D --> F[rrhh_registry.md]
