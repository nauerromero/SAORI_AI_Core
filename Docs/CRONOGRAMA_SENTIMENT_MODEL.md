# 🧠 Cronograma: Implementación de Modelo de Sentimiento

## 📊 Objetivo
Entrenar e integrar modelo de análisis de sentimiento con **XLM-RoBERTa base** para reemplazar la simulación emocional actual por inferencia real.

---

## 🗓️ Día 1: Preparación del Dataset (5 horas)

### 📥 Recolección de datos (1h)
**Fuente:** Entrevistas simuladas del `chat_simulator.py`

**Tareas:**
- [ ] Extraer respuestas de candidatos del chat_simulator
- [ ] Recolectar respuestas reales de `Logs/reports/rrhh_registry.csv`
- [ ] Agregar respuestas de `emotional_log_*.csv`

**Output esperado:**
```python
{
    "text": "I'd use async/await and proper error handling.",
    "candidate": "Luis",
    "vacancy": "Backend Node + RoR Developer",
    "context": "technical_interview"
}
```

### 🏷️ Etiquetado emocional (2h)
**Clases emocionales:**
- `enthusiastic` - Alta energía, positivo
- `confident` - Seguro, profesional
- `neutral` - Equilibrado, informativo
- `anxious` - Nervioso, inseguro
- `frustrated` - Irritado, negativo
- `negative` - Pesimista, desanimado

**Criterios de etiquetado:**
```python
# Indicadores por clase
INDICATORS = {
    "enthusiastic": ["!", "great", "love", "excited", "definitely"],
    "confident": ["yes", "of course", "certainly", "I know", "I have"],
    "neutral": ["okay", "I think", "maybe", "could be"],
    "anxious": ["not sure", "I guess", "perhaps", "maybe"],
    "frustrated": ["but", "however", "don't", "can't"],
    "negative": ["no", "never", "impossible", "difficult"]
}
```

**Tareas:**
- [ ] Crear script de etiquetado semi-automático
- [ ] Revisar y validar etiquetas manualmente
- [ ] Documentar criterios de clasificación

### 🧹 Limpieza y formato (1h)
**Tareas:**
- [ ] Normalizar texto (lowercase, eliminar caracteres especiales)
- [ ] Tokenización básica
- [ ] Convertir a formato JSON/CSV para entrenamiento
- [ ] Dividir en train/validation/test (70/15/15)

**Formato objetivo:**
```json
[
  {
    "text": "i'd use async/await and proper error handling",
    "label": "confident",
    "metadata": {
      "candidate": "Luis",
      "vacancy": "Backend Developer",
      "language": "en"
    }
  }
]
```

### 📊 Balance de clases (1h)
**Tareas:**
- [ ] Analizar distribución de clases
- [ ] Aplicar técnicas de balanceo si es necesario:
  - Oversampling de clases minoritarias
  - Undersampling de clases mayoritarias
  - Data augmentation (parafraseo)

**Target de distribución:**
```
enthusiastic: 15-20%
confident: 15-20%
neutral: 20-25%
anxious: 15-20%
frustrated: 10-15%
negative: 10-15%
```

---

## 🗓️ Día 2: Configuración y Entrenamiento (5.5 horas)

### 🧠 Carga de modelo (1h)
**Modelo base:** `xlm-roberta-base` (279M parámetros)

**Tareas:**
- [ ] Instalar dependencias:
  ```bash
  pip install transformers torch datasets evaluate scikit-learn
  ```
- [ ] Cargar tokenizer y modelo pre-entrenado
- [ ] Configurar clasificación para 6 clases emocionales
- [ ] Verificar compatibilidad con GPU (si disponible)

**Script inicial:**
```python
from transformers import XLMRobertaTokenizer, XLMRobertaForSequenceClassification

model_name = "xlm-roberta-base"
tokenizer = XLMRobertaTokenizer.from_pretrained(model_name)
model = XLMRobertaForSequenceClassification.from_pretrained(
    model_name, 
    num_labels=6  # 6 clases emocionales
)
```

### 🧪 Fine-tuning (3h)
**Hiperparámetros sugeridos:**
```python
training_args = {
    "learning_rate": 2e-5,
    "batch_size": 16,
    "epochs": 3-5,
    "weight_decay": 0.01,
    "warmup_steps": 500,
    "evaluation_strategy": "epoch"
}
```

**Tareas:**
- [ ] Preparar DataLoader con dataset balanceado
- [ ] Configurar Trainer de Hugging Face
- [ ] Entrenar con validación por epoch
- [ ] Monitorear loss y accuracy
- [ ] Guardar checkpoints

**Métricas a monitorear:**
- Training loss
- Validation loss
- Accuracy
- F1-score (macro)

### 📈 Evaluación (1h)
**Tareas:**
- [ ] Calcular métricas en test set:
  - Accuracy general
  - Precision, Recall, F1 por clase
  - Matriz de confusión
- [ ] Analizar errores comunes
- [ ] Identificar clases problemáticas

**Métricas objetivo:**
- Accuracy general: >75%
- F1-score por clase: >0.65
- Confusión entre clases adyacentes es aceptable (enthusiastic ↔ confident)

### 💾 Exportación (0.5h)
**Tareas:**
- [ ] Guardar modelo entrenado:
  ```python
  model.save_pretrained("Models/xlm-roberta-sentiment")
  tokenizer.save_pretrained("Models/xlm-roberta-sentiment")
  ```
- [ ] Exportar configuración y métricas
- [ ] Crear archivo README del modelo
- [ ] Version control del modelo (Git LFS o similar)

---

## 🗓️ Día 3: Integración al TRS Engine Core (4 horas)

### 🔗 Módulo `sentiment_model.py` (1.5h)
**Crear nuevo módulo:** `Modules/sentiment_model.py`

**Funcionalidades:**
```python
class SentimentAnalyzer:
    def __init__(self, model_path):
        """Cargar modelo entrenado"""
        
    def predict_emotion(self, text, language="auto"):
        """
        Predecir emoción de un texto
        
        Returns:
            {
                "emotion": "confident",
                "confidence": 0.87,
                "all_scores": {...}
            }
        """
        
    def predict_batch(self, texts):
        """Predicción en lote para múltiples textos"""
        
    def detect_language(self, text):
        """Detectar idioma del texto (es/en)"""
```

**Tareas:**
- [ ] Implementar clase SentimentAnalyzer
- [ ] Función de inferencia optimizada
- [ ] Detección automática de idioma
- [ ] Manejo de errores y edge cases
- [ ] Tests unitarios básicos

### 🔄 Conexión con `emotional_inference_engine.py` (1h)
**Modificaciones necesarias:**

**ANTES (simulado):**
```python
def generate_message(profile, match_score, penalty):
    tone = profile["emotional_state"]  # Viene de profiles.json
    ...
```

**DESPUÉS (real):**
```python
from sentiment_model import SentimentAnalyzer

analyzer = SentimentAnalyzer("Models/xlm-roberta-sentiment")

def infer_emotional_state(candidate_responses):
    """Inferir emoción basada en respuestas reales"""
    emotions = []
    for response in candidate_responses:
        result = analyzer.predict_emotion(response["text"])
        emotions.append(result["emotion"])
    
    # Emoción predominante o promedio ponderado
    return aggregate_emotions(emotions)
```

**Tareas:**
- [ ] Integrar SentimentAnalyzer en el engine
- [ ] Reemplazar emotional_state simulado por inferencia real
- [ ] Mantener compatibilidad con flujo existente
- [ ] Agregar logging de inferencias

### ✍️ Adaptación de `emotional_closure.py` (1h)
**Mejoras al módulo de cierre:**

```python
def generate_closing_message(candidate_name, emotional_state, vacancy_name, confidence=None):
    """
    Generar mensaje adaptativo con información de confianza
    
    Args:
        emotional_state: Emoción inferida por el modelo
        confidence: Score de confianza (0-1)
    """
    
    # Ajustar mensaje según nivel de confianza
    if confidence and confidence < 0.6:
        # Usar mensaje más neutro si hay baja confianza
        return get_neutral_message(candidate_name, vacancy_name)
    
    # Mensaje específico según emoción con alta confianza
    return get_emotion_specific_message(...)
```

**Tareas:**
- [ ] Agregar parámetro de confidence al mensaje
- [ ] Crear mensajes de respaldo para baja confianza
- [ ] Enriquecer mensajes con contexto emocional
- [ ] Actualizar tests

### 📤 Exportación a ficha técnica (0.5h)
**Agregar campos al reporte:**

```python
# En report_generator.py
def generate_candidate_section(...):
    ...
    md += f"\n#### 🧠 Emotional Analysis (AI-powered)\n"
    md += f"- **Detected Emotion:** {emotion}\n"
    md += f"- **Confidence Score:** {confidence:.2f}\n"
    md += f"- **Model:** XLM-RoBERTa base\n"
    md += f"- **Analysis Timestamp:** {timestamp}\n"
```

**Tareas:**
- [ ] Agregar sección de análisis emocional AI
- [ ] Incluir confidence score en reportes
- [ ] Documentar modelo usado
- [ ] Agregar columnas al CSV

---

## 🗓️ Día 4: Validación y Ajustes (3 horas - OPCIONAL)

### 🧪 Pruebas con entrevistas reales (1h)
**Tareas:**
- [ ] Ejecutar pipeline completo con modelo real
- [ ] Validar inferencias en 20-30 entrevistas
- [ ] Comparar emociones inferidas vs esperadas
- [ ] Documentar casos problemáticos

### 🔄 Ajuste de clases o umbrales (1h)
**Posibles ajustes:**
- [ ] Re-entrenamiento con casos problemáticos
- [ ] Ajuste de thresholds de confianza
- [ ] Refinamiento de clases muy similares
- [ ] Mejora de mensajes de cierre

### 📊 Comparación con simulador (1h)
**Métricas de impacto:**
- Tasa de consentimiento: simulado vs real
- Distribución de emociones: simulado vs real
- Coherencia de mensajes de cierre
- Experiencia del usuario

**Tareas:**
- [ ] Análisis A/B (simulado vs real)
- [ ] Reportar mejoras/diferencias
- [ ] Documentar recomendaciones
- [ ] Preparar presentación de resultados

---

## ⏱️ Resumen de Tiempo

| Día | Tareas | Tiempo |
|-----|--------|--------|
| Día 1 | Preparación del dataset | 5h |
| Día 2 | Entrenamiento | 5.5h |
| Día 3 | Integración | 4h |
| Día 4 | Validación (opcional) | 3h |
| **TOTAL** | | **16-20h** |

---

## 📁 Estructura de Archivos Nueva

```
TRS_Engine_Core/
├── Models/                              # NUEVO
│   └── xlm-roberta-sentiment/
│       ├── config.json
│       ├── pytorch_model.bin
│       ├── tokenizer.json
│       └── README.md
├── Modules/
│   ├── sentiment_model.py              # NUEVO
│   ├── emotional_inference_engine.py   # MODIFICADO
│   ├── emotional_closure.py            # MODIFICADO
│   └── report_generator.py             # MODIFICADO
├── Data/
│   └── sentiment_training/             # NUEVO
│       ├── train.json
│       ├── validation.json
│       └── test.json
└── Notebooks/
    └── sentiment_model_training.ipynb  # NUEVO
```

---

## 🎯 Criterios de Éxito

### Técnicos
- [ ] Modelo con accuracy >75% en test set
- [ ] F1-score >0.65 por clase
- [ ] Inferencia <500ms por texto
- [ ] Integración sin breaking changes

### Funcionales
- [ ] Pipeline ejecuta end-to-end con modelo real
- [ ] Reportes incluyen análisis emocional AI
- [ ] Mensajes de cierre coherentes con emoción detectada
- [ ] Documentación completa

### De Negocio
- [ ] Mejora en tasa de consentimiento (vs simulado)
- [ ] Mayor precisión en clasificación emocional
- [ ] Sistema listo para producción
- [ ] Presentación para hackathon completa

---

## 🚀 Próximos Pasos Inmediatos

1. **Crear estructura de carpetas**
2. **Extraer datos de entrevistas existentes**
3. **Comenzar etiquetado del dataset**
4. **Instalar dependencias necesarias**

---

**Fecha creación:** 2025-11-07  
**Versión:** 1.0  
**Hackathon ready:** 3-4 días

