# 🚀 Plan Inmediato: Inicio del Proyecto de Sentimiento

## ✅ Estado Actual
- [x] Repositorio subido a GitHub
- [x] Pipeline v2.0 funcionando
- [x] Cronograma detallado creado
- [x] Estructura de carpetas creada

---

## 🎯 ¿Por Dónde Empezar?

### Opción A: Comenzar Ahora (Recomendado)
**Primer paso: Extracción de datos**

Podemos usar las respuestas ya generadas en el sistema para crear el dataset inicial:

```python
# Fuentes de datos disponibles:
1. Logs/reports/rrhh_registry.csv - 70 respuestas con contexto
2. Respuestas del chat_simulator - plantillas base
3. Emotional log histórico - estados emocionales actuales
```

**Tiempo estimado:** 30 minutos para tener primer dataset

### Opción B: Preparación Completa
**Pasos previos:**
1. Instalar dependencias nuevas
2. Preparar entorno de entrenamiento
3. Diseñar estructura de datos
4. Comenzar etiquetado manual

**Tiempo estimado:** 2 horas de setup

---

## 🔥 Inicio Rápido (Opción A - Recomendada)

### Paso 1: Script de Extracción (15 min)
Crear `Modules/data_extractor.py` para extraer respuestas existentes:

```python
import pandas as pd
import json

def extract_interview_responses():
    """Extraer respuestas de entrevistas del sistema"""
    
    # Leer reportes existentes
    df = pd.read_csv('Logs/reports/rrhh_registry.csv')
    
    responses = []
    for idx, row in df.iterrows():
        # Extraer información
        response = {
            "text": row.get('response_text', ''),
            "candidate": row['Nombre'],
            "vacancy": row['Vacante'],
            "emotional_state": row['Estado emocional'],
            "context": "technical_interview"
        }
        responses.append(response)
    
    return responses

def save_initial_dataset(responses, output_path='Data/sentiment_training/raw_data.json'):
    """Guardar dataset inicial"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(responses, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {len(responses)} respuestas extraídas")

if __name__ == "__main__":
    responses = extract_interview_responses()
    save_initial_dataset(responses)
```

### Paso 2: Etiquetado Semi-Automático (30 min)
Crear `Modules/label_emotions.py`:

```python
def auto_label_emotion(text, current_emotion):
    """
    Etiquetado inicial basado en indicadores simples
    Luego se revisa manualmente
    """
    
    # Indicadores básicos
    indicators = {
        "enthusiastic": ["!", "great", "love", "excited", "definitely", "absolutely"],
        "confident": ["yes", "of course", "certainly", "I know", "I have", "clearly"],
        "neutral": ["okay", "I think", "could be", "generally", "usually"],
        "anxious": ["not sure", "I guess", "perhaps", "maybe", "uncertain"],
        "frustrated": ["but", "however", "don't", "can't", "difficult"],
        "negative": ["no", "never", "impossible", "won't", "unable"]
    }
    
    # Scoring por indicadores
    scores = {}
    text_lower = text.lower()
    
    for emotion, keywords in indicators.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        scores[emotion] = score
    
    # Combinar con emoción actual (si existe)
    if current_emotion and current_emotion.lower() in scores:
        scores[current_emotion.lower()] += 2  # Bonus por coherencia
    
    # Retornar emoción con mayor score
    predicted = max(scores, key=scores.get) if max(scores.values()) > 0 else "neutral"
    confidence = max(scores.values()) / sum(scores.values()) if sum(scores.values()) > 0 else 0.3
    
    return {
        "predicted_emotion": predicted,
        "confidence": confidence,
        "needs_review": confidence < 0.5,
        "scores": scores
    }
```

### Paso 3: Revisar y Ajustar (30 min)
Crear interfaz simple para revisar etiquetas:

```python
def review_labels(dataset_path):
    """Revisar etiquetas generadas automáticamente"""
    
    with open(dataset_path, 'r') as f:
        data = json.load(f)
    
    reviewed = []
    for i, item in enumerate(data):
        print(f"\n[{i+1}/{len(data)}] Texto: {item['text']}")
        print(f"Emoción sugerida: {item['predicted_emotion']} (confianza: {item['confidence']:.2f})")
        
        if item.get('needs_review', False):
            print("⚠️  Requiere revisión manual")
            user_input = input("Confirmar (Enter) o ingresar nueva emoción: ")
            if user_input:
                item['predicted_emotion'] = user_input
        
        reviewed.append(item)
    
    # Guardar versión revisada
    with open('Data/sentiment_training/labeled_data.json', 'w') as f:
        json.dump(reviewed, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ {len(reviewed)} etiquetas revisadas")
```

---

## 📊 Dataset Inicial Estimado

Con el sistema actual podemos generar:

```
Fuente: rrhh_registry.csv
- 70 pares candidato-vacante
- ~140-210 respuestas técnicas (2-3 por entrevista)
- Estados emocionales ya asignados

Fuente: chat_simulator templates
- ~15 plantillas de respuesta
- 3 dominios (backend, data, admin)
- Variaciones por nivel técnico

Total estimado: 150-250 textos etiquetados
```

**¿Es suficiente?**
- Para fine-tuning inicial: **SÍ** ✅
- Para producción robusta: Idealmente 500-1000+

**Solución:**
- Data augmentation (parafraseo)
- Agregar respuestas sintéticas
- Incrementar progresivamente con uso real

---

## 🎯 Mi Recomendación

**OPCIÓN INMEDIATA:**

1. **Ahora (15 min):** Crear script de extracción
2. **Hoy (30 min):** Etiquetado automático + revisión de 50 casos
3. **Mañana (2h):** Completar etiquetado de 150-200 textos
4. **Día 2:** Comenzar entrenamiento

**Ventajas:**
- Usamos datos reales del sistema
- Validamos pipeline de etiquetado
- Podemos iterar rápidamente
- No bloqueamos con decisiones de arquitectura

---

## 💬 Pregunta para ti:

**¿Quieres que creemos ahora mismo el script de extracción de datos?**

Opciones:
1. ✅ **Sí, comencemos con la extracción** → Creo `data_extractor.py` y extraemos primer dataset
2. 🔧 **Primero instalar dependencias** → Instalamos transformers, torch, etc.
3. 📝 **Revisar plan antes** → Discutimos ajustes al cronograma

**Tu decisión:**

