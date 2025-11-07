# Changelog - TRS Engine Core

## [2.0.0] - 2025-11-07

### 🔄 Major Update: Full Integration
- **consent_simulator.py completamente integrado con el pipeline**
  - Ahora LEE de emotional_log.csv (datos reales del sistema)
  - USA candidatos reales de profiles.json
  - USA vacantes reales de Vacancy.json
  - CALCULA probabilidades basadas en estados emocionales y scores reales
  - Genera IDs únicos: `{nombre}_{vacante}`
  
### ✨ Added
- **Lógica de Probabilidades Inteligente**
  - Positive/Enthusiastic + High Score = 85-95% probabilidad de consent
  - Neutral + Medium Score = 50-70% probabilidad
  - Negative/Frustrated + Low Score = 10-40% probabilidad
  - Ajustes dinámicos según match_score y adjusted_score

- **Estadísticas Mejoradas**
  - Tasa de consentimiento por estado emocional
  - Distribución por vacantes reales
  - Match scores promedio del sistema
  - Total de pares candidato-vacante procesados

### 🔧 Changed
- **Pipeline ahora soporta dos modos:**
  - Modo A: Consentimiento en tiempo real (producción)
  - Modo B: Consentimiento pre-generado probabilístico (testing)

### 📝 Documentation
- `data_flow_diagram.md` v2.0 - Flujo integrado completo
- `COHERENCIA_DEL_SISTEMA.md` v2.0 - Verificación de integración
- `emotional_closure_integration.md` - Actualizado con flujo integrado
- `README.md` - Estructura reorganizada para claridad

---

## [1.1.0] - 2025-11-07

### ✨ Initial Integration (Replaced by v2.0)
- **Emotional Closure Integration**: Módulo `emotional_closure.py` integrado en el flujo principal
  - Mensajes de cierre adaptativos según estado emocional del candidato
  - Captura de consentimiento del candidato para continuar con el proceso
  - Trazabilidad completa con timestamps UTC

- **Consent Simulator**: Primer versión de `consent_simulator.py`
  - Generador inicial de datos de consentimiento
  - CLI con argumentos configurables
  - ⚠️ Versión inicial generaba datos sintéticos (reemplazado en v2.0)

- **Enhanced RRHH Reports**: Reportes mejorados con información de cierre
  - Nueva sección "🤝 Interview Closure" en reportes Markdown
  - 3 columnas adicionales en CSV: Mensaje de cierre, Consentimiento, Estado emocional final
  - Estadísticas de consentimiento en resumen ejecutivo
  - Tasa de aceptación/rechazo de candidatos

### 📦 Data Files
- `Data/candidate_consent_log.json`: Nuevo archivo para tracking de consentimientos

### 📝 Documentation
- `Docs/emotional_closure_integration.md`: Guía completa de integración
- README actualizado con estructura completa del proyecto
- Documentación de uso del consent_simulator

### 🔧 Modified Files
- `Modules/chat_simulator.py`: Integra generación de mensajes de cierre
- `Modules/report_generator.py`: Reportes con información de consentimiento
- `Modules/process_candidates.py`: Movido a carpeta Modules (previamente en raíz)

### 🎯 Benefits
- ✅ Trazabilidad legal de consentimientos (GDPR/CCPA compliance)
- ✅ Análisis de experiencia del candidato
- ✅ Priorización automática basada en consentimiento
- ✅ Mejora continua mediante análisis de conversión

### 🧪 Testing
- Generación de 20 perfiles de prueba exitosa
- Validación de formato JSON consistente
- Integración completa sin errores de linting

---

## [1.0.0] - 2025-11-05

### Initial Release
- Sistema base de matching de candidatos
- Motor de inferencia emocional
- Simulador de entrevistas
- Generación de reportes para RRHH
- Compatibilidad de zonas horarias
- Asignación dinámica de reclutadores

---

**Formato basado en [Keep a Changelog](https://keepachangelog.com/)**

