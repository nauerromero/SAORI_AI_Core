# TRS Engine Core - Data Flow Diagram

## 🔄 Pipeline de Producción (Flujo Integrado)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FUENTE DE DATOS                              │
│  📁 Data/profiles.json + Data/Vacancy.json + Data/recruiters.json  │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     PASO 1: INFERENCIA EMOCIONAL                    │
│              📊 emotional_inference_engine.py                       │
│                                                                      │
│  Input:  profiles.json, Vacancy.json                                │
│  Output: Logs/emotional_log_*.csv                                   │
│                                                                      │
│  Genera: match_scores, estados emocionales por candidato-vacante    │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
              ┌───────────────────┴───────────────────┐
              │                                       │
              ↓ (Pipeline estándar)                  ↓ (Pipeline con pre-generación)
┌──────────────────────────────┐     ┌────────────────────────────────────────┐
│  PASO 2A: SIMULACIÓN         │     │  PASO 1.5: GENERADOR DE CONSENTIMIENTOS│
│  DIRECTA                     │     │  (OPCIONAL)                            │
│                              │     │                                        │
│  💬 chat_simulator.py       │     │  🔄 consent_simulator.py              │
│                              │     │                                        │
│  - Lee emotional_log_*.csv   │     │  Input:  emotional_log_*.csv          │
│  - Simula entrevistas        │     │  Output: candidate_consent_log.json   │
│  - Captura consentimiento    │     │                                        │
│    en tiempo real            │     │  Genera consentimientos probabilísticos│
│                              │     │  basados en:                           │
│                              │     │    - Estado emocional real             │
│                              │     │    - Match scores reales               │
│                              │     │    - Adjusted scores                   │
└──────────────────────────────┘     └────────────────────────────────────────┘
              │                                       │
              │                                       ↓
              │                      ┌─────────────────────────────────────┐
              │                      │  PASO 2B: SIMULACIÓN CON DATOS      │
              │                      │  PRE-GENERADOS                      │
              │                      │                                     │
              │                      │  💬 chat_simulator.py              │
              │                      │                                     │
              │                      │  - Lee emotional_log_*.csv          │
              │                      │  - Puede usar consent_log.json      │
              │                      │  - Genera emotional_closure msgs    │
              │                      └─────────────────────────────────────┘
              │                                       │
              └───────────────────┬───────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│                   PASO 3: GENERACIÓN DE REPORTES                    │
│                     📄 report_generator.py                          │
│                                                                      │
│  Input:  all_results (entries + simulation data + consent data)     │
│  Output:                                                             │
│    - Logs/reports/rrhh_registry.md    (con sección Closure)        │
│    - Logs/reports/rrhh_registry.csv   (con columnas de consent)    │
│                                                                      │
│  Incluye:                                                            │
│    ✅ Mensaje de cierre adaptativo (de emotional_closure.py)        │
│    ✅ Estado de consentimiento (Sí/No)                              │
│    ✅ Estado emocional final                                        │
│    ✅ Estadísticas de consentimiento en resumen ejecutivo           │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    PASO 4: FILTRADO Y CLASIFICACIÓN                 │
│                      🎯 candidate_filter.py                         │
│                                                                      │
│  Input:  rrhh_registry.csv                                          │
│  Output:                                                             │
│    - Logs/reports/accepted_candidates.md                            │
│    - Logs/reports/rejected_candidates.md                            │
│    - Logs/reports/talent_pool.csv                                   │
│    - Logs/reports/feedback/* (archivos individuales)                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Módulo consent_simulator.py - Ahora Integrado

### ✅ Nueva Funcionalidad (Integrada con Pipeline)

El `consent_simulator.py` ahora:
- **LEE** de `emotional_log_*.csv` (datos reales del pipeline)
- **USA** candidatos y vacantes reales de profiles.json/Vacancy.json
- **CALCULA** probabilidades de consentimiento basadas en:
  - Estado emocional real
  - Match score real
  - Adjusted score real

### Lógica de Probabilidades

```python
def calculate_consent_probability(emotional_state, match_score, adjusted_score):
    """
    Positive/Enthusiastic + High Score = 85-95% probabilidad
    Confident + Medium Score = 75-85% probabilidad
    Neutral + Medium Score = 50-70% probabilidad
    Anxious/Frustrated + Low Score = 20-40% probabilidad
    Negative + Any Score = 10-20% probabilidad
    """
```

### Ejemplo con Datos Reales

```
Entrada (emotional_log.csv):
name: "Ana"
vacancy: "Executive Assistant"
emotional_state: "Positive"
match_score: 0.75
adjusted_score: 0.45

↓ (consent_simulator.py calcula)

consent_probability: 0.95 (95% probabilidad)
consent_given: True (generado probabilísticamente)

Salida (candidate_consent_log.json):
{
  "candidate_id": "ana_executive_assistant",
  "name": "Ana",
  "vacancy_selected": "Executive Assistant",
  "match_score": 0.75,
  "adjusted_score": 0.45,
  "emotional_state_initial": "Positive",
  "consent_probability": 0.95,
  "consent_given": true
}
```

---

## 📊 Resumen de Archivos de Datos

### Archivos Fuente (SOURCE DATA)
```
✅ Data/profiles.json        → Candidatos del sistema
✅ Data/Vacancy.json         → Vacantes disponibles
✅ Data/recruiters.json      → Base de datos de reclutadores
```

### Archivos Generados (PIPELINE OUTPUT)
```
📊 Logs/emotional_log_*.csv           → Paso 1 (emotional_inference_engine)
📊 Logs/inference_results_*.md        → Paso 1 (emotional_inference_engine)
🔄 Data/candidate_consent_log.json   → Paso 1.5 (consent_simulator - OPCIONAL)
📄 Logs/reports/rrhh_registry.md      → Paso 3 (report_generator - CON CONSENT)
📄 Logs/reports/rrhh_registry.csv     → Paso 3 (report_generator - CON CONSENT)
📄 Logs/reports/accepted_candidates.md → Paso 4 (candidate_filter)
📄 Logs/reports/rejected_candidates.md → Paso 4 (candidate_filter)
📄 Logs/reports/talent_pool.csv       → Paso 4 (candidate_filter)
```

---

## 🚀 Dos Formas de Ejecutar el Pipeline

### Opción A: Pipeline Estándar (Consentimiento en Tiempo Real)
```bash
python Modules/process_candidates.py
```

**Flujo:**
1. `emotional_inference_engine.py` → genera emotional_log
2. `chat_simulator.py` → captura consentimiento durante entrevista
3. `report_generator.py` → genera reportes con consentimiento
4. `candidate_filter.py` → filtra y clasifica

**Uso recomendado:** Producción con interacción real de usuarios

### Opción B: Pipeline con Pre-generación (Consentimiento Probabilístico)
```bash
# Paso 1: Generar emotional log
python Modules/emotional_inference_engine.py

# Paso 2: Pre-generar consentimientos (basados en probabilidades)
python Modules/consent_simulator.py

# Paso 3: Simular entrevistas (puede usar datos pre-generados)
python Modules/chat_simulator.py

# Los reportes finales incluyen los consentimientos
```

**Uso recomendado:** Testing, demos, análisis de escenarios

---

## ✅ Ventajas del Flujo Integrado

| Aspecto | Beneficio |
|---------|-----------|
| **Datos Coherentes** | consent_simulator usa MISMOS candidatos y vacantes que el pipeline |
| **Probabilidades Realistas** | Basadas en estados emocionales y scores reales |
| **Flexibilidad** | Puede usarse en modo tiempo-real O pre-generación |
| **Trazabilidad** | Cada consentimiento incluye probabilidad calculada |
| **Testing** | Permite generar múltiples escenarios sin re-ejecutar todo |

---

## 🔍 Verificación de Coherencia

| Criterio | Estado | Detalles |
|----------|--------|----------|
| Datos de entrada | ✅ REAL | Lee emotional_log.csv con candidatos reales |
| Candidatos | ✅ REAL | Nombres de profiles.json (Luis, Ana, Jorge...) |
| Vacantes | ✅ REAL | Títulos de Vacancy.json (Backend Node, Data Engineer...) |
| Estados emocionales | ✅ REAL | Del emotional_inference_engine |
| Match scores | ✅ REAL | Calculados por el engine |
| Probabilidades | ✅ LÓGICAS | Basadas en emociones y scores reales |
| Flujo integrado | ✅ SÍ | Parte opcional del pipeline completo |

---

**Conclusión**: El sistema ahora tiene **un flujo único e integrado**. El `consent_simulator.py` es una herramienta **opcional** que se basa en datos reales del pipeline, manteniendo coherencia total con el sistema.

**Última actualización:** 2025-11-07  
**Versión:** 2.0 (Integrado)
