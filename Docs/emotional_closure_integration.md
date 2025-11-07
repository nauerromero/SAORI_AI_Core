# Integración de Emotional Closure al Reporte de RRHH

## 📋 Resumen

El módulo `emotional_closure.py` ha sido integrado al flujo principal de procesamiento de candidatos, permitiendo que la información de cierre emocional y consentimiento se incluya automáticamente en los reportes entregados a RRHH.

## 🔄 Flujo de Integración

### 1. **Captura de Datos (chat_simulator.py)**
Durante la simulación de entrevistas:
- Al finalizar cada entrevista, se genera un mensaje de cierre adaptativo según el estado emocional del candidato
- Se simula/captura el consentimiento del candidato para continuar con el proceso
- Los datos se almacenan en los resultados de la simulación

```python
# Mensaje adaptativo según emoción
closing_message = generate_closing_message(name, emotion, vacancy)

# Captura de consentimiento (simulado o real)
consent_given = True/False  # Basado en respuesta del candidato
```

### 2. **Inclusión en Reportes (report_generator.py)**

#### Reporte Markdown (`rrhh_registry.md`)
Cada ficha de candidato ahora incluye una sección adicional:

**🤝 Interview Closure**
- **Closing Message:** [Mensaje personalizado según emoción]
- **Candidate Consent:** ✅ YES / ❌ NO

#### Reporte CSV (`rrhh_registry.csv`)
Se agregaron tres columnas nuevas:
- `Mensaje de cierre`: El mensaje adaptativo generado
- `Consentimiento`: Sí/No
- `Estado emocional final`: Confirmación del estado al finalizar

#### Executive Summary
El resumen ejecutivo ahora incluye estadísticas de consentimiento:
```
### 🤝 Candidate Consent Status
- Consented to Continue: X candidates (XX%)
- Declined to Continue: X candidates (XX%)
```

## 📊 Datos Capturados

### Información recolectada por emotional_closure:

1. **Mensaje de cierre adaptativo**
   - Varía según: `enthusiastic`, `frustrated`, `neutral`, `anxious`, `confident`
   - Personalizado con nombre del candidato y vacante

2. **Consentimiento del candidato**
   - Registro binario (Sí/No)
   - Timestamp de la decisión

3. **Estado emocional final**
   - Confirmación del estado al momento de cierre
   - Útil para detectar cambios durante la entrevista

## 💼 Beneficios para RRHH

### 1. **Trazabilidad Legal**
- Registro de consentimiento explícito para protección de datos
- Cumplimiento con normativas GDPR/CCPA

### 2. **Análisis de Experiencia del Candidato**
- Tasa de conversión (aceptación/rechazo)
- Correlación entre estado emocional y consentimiento
- Efectividad de los mensajes de cierre

### 3. **Priorización de Candidatos**
- Los candidatos que dieron consentimiento están listos para siguiente fase
- Los que declinaron pueden ir a talent pool para futuras oportunidades

### 4. **Mejora Continua**
- Identificar qué estados emocionales llevan a mayor tasa de aceptación
- Ajustar estrategias de cierre según datos históricos

## 🔍 Ejemplo de Uso

### Antes (sin emotional_closure):
```csv
Nombre,Vacante,Match Score,Estado emocional
Jorge,Backend LATAM,0.85,enthusiastic
```

### Después (con emotional_closure):
```csv
Nombre,Vacante,Match Score,Estado emocional,Mensaje de cierre,Consentimiento,Estado emocional final
Jorge,Backend LATAM,0.85,enthusiastic,"Excellent, Jorge! You seem highly aligned...",Sí,enthusiastic
```

## 📝 Notas Técnicas

### Simulación vs. Producción
Actualmente el consentimiento se **simula** basándose en:
- Estado emocional (enthusiastic/confident → 90% probabilidad de aceptar)
- Match score (score >= 0.6 aumenta probabilidad)

En **producción**, esto debe reemplazarse por:
```python
# Capturar respuesta real del candidato
user_response = input("Would you like to proceed? (yes/no): ")
consent_given = user_response.lower() in ["yes", "y", "sí"]
```

### Archivos Modificados
1. `Modules/chat_simulator.py`
   - Importa `generate_closing_message`
   - Genera mensaje y captura consentimiento
   - Agrega datos a `all_results`

2. `Modules/report_generator.py`
   - `generate_candidate_section()`: Nuevo parámetros para closure
   - `generate_executive_summary()`: Estadísticas de consentimiento
   - `export_to_csv_file()`: Columnas adicionales

### Compatibilidad
✅ Retrocompatible: Si los datos de closure no están presentes, los reportes funcionan normalmente
✅ No afecta módulos existentes
✅ Se integra sin cambios en `emotional_inference_engine.py`

## 🚀 Próximos Pasos

1. **Integrar entrada real de usuario** cuando el sistema pase a producción
2. **Exportar consent_log.csv separado** para auditoría legal (opcional)
3. **Dashboard de métricas** de aceptación/rechazo por estado emocional
4. **A/B testing** de diferentes mensajes de cierre

## 🔄 Generador de Consentimientos (Integrado con Pipeline)

El módulo `consent_simulator.py` genera datos de consentimiento **basados en el emotional_log real** del sistema.

### Flujo Integrado

```
profiles.json + Vacancy.json
        ↓
emotional_inference_engine.py
        ↓
emotional_log_*.csv (candidatos reales + estados emocionales)
        ↓
consent_simulator.py (OPCIONAL - genera consentimientos probabilísticos)
        ↓
candidate_consent_log.json (basado en datos reales)
        ↓
chat_simulator.py (con emotional_closure integrado)
        ↓
rrhh_registry.md/csv (reportes finales con consentimiento)
```

### Características del Simulador

El `consent_simulator.py` ahora:
- ✅ **Lee del emotional_log.csv real** (no genera datos sintéticos)
- ✅ **Usa candidatos reales** de profiles.json
- ✅ **Usa vacantes reales** de Vacancy.json  
- ✅ **Probabilidad de consentimiento basada en:**
  - Estado emocional del candidato
  - Match score (compatibilidad técnica)
  - Adjusted score (después de penalizaciones)
- ✅ Genera IDs únicos: `{nombre}_{vacante}`
- ✅ Timestamps UTC para trazabilidad

### Lógica de Probabilidades

```python
Estado Emocional + Match Score → Probabilidad de Consentimiento

- Positive/Enthusiastic + High Score (>0.7) = 85-95%
- Confident + Medium Score (0.5-0.7) = 75-85%
- Neutral + Medium Score = 50-70%
- Anxious/Frustrated + Low Score (<0.3) = 20-40%
- Negative + Any Score = 10-20%
```

### Uso del Simulador

```bash
# Usar el emotional_log más reciente
python Modules/consent_simulator.py

# Especificar un log específico
python Modules/consent_simulator.py --log Logs/emotional_log_2025-11-05.csv

# Cambiar archivo de salida
python Modules/consent_simulator.py --output Data/custom_consent.json
```

### Ejemplo de Salida

El archivo generado (`Data/candidate_consent_log.json`) contiene datos **basados en candidatos reales**:

```json
[
  {
    "candidate_id": "luis_backend_node_+_ror_developer",
    "name": "Luis",
    "vacancy_selected": "Backend Node + RoR Developer",
    "match_score": 0.5,
    "adjusted_score": 0.0,
    "emotional_state_initial": "Neutral",
    "emotional_state_final": "Neutral",
    "consent_probability": 0.55,
    "consent_given": false,
    "consent_timestamp": "2025-11-07T03:09:23.649748+00:00"
  },
  {
    "candidate_id": "ana_executive_assistant",
    "name": "Ana",
    "vacancy_selected": "Executive Assistant",
    "match_score": 0.75,
    "adjusted_score": 0.45,
    "emotional_state_initial": "Positive",
    "emotional_state_final": "Positive",
    "consent_probability": 0.95,
    "consent_given": true,
    "consent_timestamp": "2025-11-07T03:09:23.649820+00:00"
  }
]
```

### Integración con el Pipeline

El `consent_simulator.py` es **opcional** y se puede usar de dos formas:

**Opción A: Pipeline con simulación de consentimiento previo**
```bash
# 1. Generar emotional log
python Modules/emotional_inference_engine.py

# 2. Generar consentimientos probabilísticos
python Modules/consent_simulator.py

# 3. Ejecutar entrevistas (puede usar los datos pre-generados)
python Modules/chat_simulator.py
```

**Opción B: Pipeline estándar (consentimiento en tiempo real)**
```bash
# Ejecutar pipeline completo
python Modules/process_candidates.py

# El consentimiento se captura automáticamente en chat_simulator.py
```

### Datos de Consentimiento en Reportes

Los datos finales de consentimiento (sea del simulator o capturados en tiempo real) se incluyen en:
- `Logs/reports/rrhh_registry.md` - Sección "🤝 Interview Closure" 
- `Logs/reports/rrhh_registry.csv` - Columnas de consentimiento

---

**Última actualización:** 2025-11-07  
**Versión:** 1.1  
**Autor:** TRS Engine Core Team

