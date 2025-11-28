"""
English Level Evaluator - SAORI AI Core V4.0
Evaluates English proficiency during technical interview responses

Features:
- Maps user-friendly levels (Básico, Intermedio, Avanzado) to numeric scale
- Evaluates 4 dimensions: Grammar, Vocabulary, Fluency, Comprehension
- Detects inconsistencies between declared and demonstrated level
- Integrates with dual evaluation system (technical + English)

Usage:
    evaluator = EnglishLevelEvaluator()
    result = evaluator.evaluate_during_conversation(responses, declared_level)
"""

class EnglishLevelEvaluator:
    """
    Evaluates English proficiency based on conversation responses
    """
    
    # Mapeo de niveles coloquiales a numéricos
    LEVEL_MAP = {
        "basico": 1,
        "básico": 1,
        "basic": 1,
        "beginner": 1,
        
        "intermedio": 2,
        "intermediate": 2,
        "medio": 2,
        "middle": 2,
        
        "avanzado": 3,
        "advanced": 3,
        "fluido": 3,
        "fluent": 3,
        
        "nativo": 4,
        "native": 4,
        "bilingue": 4,
        "bilingual": 4
    }
    
    # Equivalencias CEFR (para documentación)
    CEFR_EQUIVALENTS = {
        1: ["A1", "A2"],      # Básico
        2: ["B1", "B2"],      # Intermedio
        3: ["C1", "C2"],      # Avanzado
        4: ["Native"]         # Nativo
    }
    
    # Nombres amigables
    LEVEL_NAMES = {
        1: "Básico (Basic)",
        2: "Intermedio (Intermediate)",
        3: "Avanzado (Advanced)",
        4: "Nativo (Native)"
    }
    
    @staticmethod
    def normalize_level(declared_level):
        """
        Convierte nivel declarado a numérico
        
        Args:
            declared_level: "Básico", "Intermedio", "Avanzado", etc.
        
        Returns:
            int: 1-4 (default: 1 si no reconoce)
        """
        if not declared_level:
            return 1
        
        level_clean = declared_level.lower().strip()
        return EnglishLevelEvaluator.LEVEL_MAP.get(level_clean, 1)
    
    @staticmethod
    def get_level_name(level_num):
        """
        Convierte número a nombre amigable
        
        Args:
            level_num: 1-4
        
        Returns:
            str: "Básico (Basic)", etc.
        """
        return EnglishLevelEvaluator.LEVEL_NAMES.get(level_num, "Unknown")
    
    def evaluate_during_conversation(self, user_responses, declared_level):
        """
        Evalúa nivel de inglés basándose en respuestas reales
        
        Args:
            user_responses: Lista de respuestas del usuario (strings)
            declared_level: Nivel que declaró (1-4)
        
        Returns:
            dict: {
                "declared_level": int,
                "demonstrated_level": int,
                "consistency": bool,
                "issues": list,
                "score": float (0.0-1.0),
                "breakdown": {
                    "grammar": int (1-3),
                    "vocabulary": int (1-3),
                    "fluency": int (1-3),
                    "comprehension": int (1-3)
                }
            }
        """
        if not user_responses:
            return {
                "declared_level": declared_level,
                "demonstrated_level": 1,
                "consistency": False,
                "issues": ["No responses to evaluate"],
                "score": 0.0,
                "breakdown": {
                    "grammar": 1,
                    "vocabulary": 1,
                    "fluency": 1,
                    "comprehension": 1
                }
            }
        
        # Evaluar cada dimensión
        grammar_score = self._evaluate_grammar(user_responses)
        vocabulary_score = self._evaluate_vocabulary(user_responses)
        fluency_score = self._evaluate_fluency(user_responses)
        comprehension_score = self._evaluate_comprehension(user_responses)
        
        # Nivel demostrado (promedio ponderado)
        demonstrated_level = round(
            (grammar_score * 0.3 +
             vocabulary_score * 0.3 +
             fluency_score * 0.2 +
             comprehension_score * 0.2)
        )
        
        # Asegurar rango válido
        demonstrated_level = max(1, min(3, demonstrated_level))
        
        # Verificar consistencia (tolerancia de 1 nivel)
        level_difference = abs(declared_level - demonstrated_level)
        consistency = level_difference <= 1
        
        # Identificar issues
        issues = []
        if level_difference >= 2:
            issues.append(
                f"⚠️ Declaró nivel {self.get_level_name(declared_level)} "
                f"pero demuestra nivel {self.get_level_name(demonstrated_level)}"
            )
        
        # Score final (0.0-1.0)
        if consistency:
            score = min(demonstrated_level / 3.0, 1.0)
        else:
            # Penalización por inconsistencia
            score = max((demonstrated_level / 3.0) - 0.2, 0.0)
        
        return {
            "declared_level": declared_level,
            "demonstrated_level": demonstrated_level,
            "consistency": consistency,
            "issues": issues,
            "score": round(score, 2),
            "breakdown": {
                "grammar": grammar_score,
                "vocabulary": vocabulary_score,
                "fluency": fluency_score,
                "comprehension": comprehension_score
            }
        }
    
    def _evaluate_grammar(self, responses):
        """
        Evalúa calidad gramatical
        
        Indicadores:
        - Básico (1): Errores frecuentes, oraciones simples
        - Intermedio (2): Errores ocasionales, algunas estructuras complejas
        - Avanzado (3): Pocos errores, estructuras variadas
        
        Args:
            responses: Lista de strings
        
        Returns:
            int: 1-3
        """
        all_text = " ".join(responses).lower()
        
        # Indicadores de nivel avanzado
        advanced_structures = [
            "would have", "could have", "should have",  # Conditionals
            "which", "whom", "whose",                    # Relative pronouns
            "despite", "although", "whereas", "however", # Conjunctions
            "having", "been",                            # Perfect tenses
            "not only", "but also"                       # Correlatives
        ]
        
        # Indicadores de nivel intermedio
        intermediate_structures = [
            "because", "therefore", "thus",
            "can", "could", "should", "would",
            "if", "when", "while", "since",
            "will", "going to"
        ]
        
        advanced_count = sum(1 for struct in advanced_structures if struct in all_text)
        intermediate_count = sum(1 for struct in intermediate_structures if struct in all_text)
        
        # Scoring
        if advanced_count >= 2:
            return 3  # Avanzado
        elif intermediate_count >= 3 or advanced_count >= 1:
            return 2  # Intermedio
        else:
            return 1  # Básico
    
    def _evaluate_vocabulary(self, responses):
        """
        Evalúa riqueza de vocabulario
        
        Mide:
        - Diversidad de palabras (lexical diversity)
        - Uso de términos técnicos
        - Palabras sofisticadas vs comunes
        
        Args:
            responses: Lista de strings
        
        Returns:
            int: 1-3
        """
        all_text = " ".join(responses).lower()
        words = all_text.split()
        
        if len(words) < 10:
            return 1  # Muy pocas palabras
        
        # 1. Lexical Diversity (unique words / total words)
        unique_words = len(set(words))
        lexical_diversity = unique_words / len(words)
        
        # 2. Technical vocabulary
        technical_terms = [
            "implement", "optimize", "architecture", "scalability",
            "framework", "infrastructure", "deployment", "integration",
            "algorithm", "efficiency", "methodology", "collaborate",
            "database", "performance", "security", "reliability"
        ]
        technical_count = sum(1 for term in technical_terms if term in all_text)
        
        # 3. Sophisticated vocabulary
        sophisticated_words = [
            "utilize", "demonstrate", "analyze", "comprehensive",
            "facilitate", "enhance", "establish", "significant",
            "particularly", "specifically", "primarily", "essentially"
        ]
        sophisticated_count = sum(1 for word in sophisticated_words if word in all_text)
        
        # Scoring
        if lexical_diversity > 0.7 and (technical_count >= 3 or sophisticated_count >= 2):
            return 3  # Avanzado
        elif lexical_diversity > 0.5 and (technical_count >= 1 or sophisticated_count >= 1):
            return 2  # Intermedio
        else:
            return 1  # Básico
    
    def _evaluate_fluency(self, responses):
        """
        Evalúa fluidez basándose en:
        - Longitud de respuestas
        - Uso de conectores
        - Complejidad de oraciones
        
        Args:
            responses: Lista de strings
        
        Returns:
            int: 1-3
        """
        if not responses:
            return 1
        
        # Longitud promedio de respuestas
        avg_length = sum(len(r.split()) for r in responses) / len(responses)
        
        # Conectores de fluidez
        fluency_markers = [
            "well", "actually", "you know", "i mean",
            "so", "also", "additionally", "furthermore",
            "for example", "for instance", "in fact", "basically",
            "moreover", "consequently", "therefore"
        ]
        
        all_text = " ".join(responses).lower()
        connector_count = sum(1 for marker in fluency_markers if marker in all_text)
        
        # Scoring
        if avg_length > 20 and connector_count >= 3:
            return 3  # Avanzado: respuestas largas y bien conectadas
        elif avg_length > 10 and connector_count >= 1:
            return 2  # Intermedio: respuestas moderadas
        else:
            return 1  # Básico: respuestas cortas
    
    def _evaluate_comprehension(self, responses):
        """
        Evalúa comprensión basándose en:
        - Relevancia de respuestas a las preguntas
        - Capacidad de elaborar
        - Completitud de respuestas
        
        Args:
            responses: Lista de strings
        
        Returns:
            int: 1-3
        """
        # Simple heuristic: longitud y detalle indican buena comprensión
        avg_length = sum(len(r.split()) for r in responses) / len(responses) if responses else 0
        
        # Indicadores de buena comprensión
        elaboration_markers = [
            "for example", "such as", "like", "because",
            "first", "second", "also", "additionally",
            "specifically", "in particular"
        ]
        
        all_text = " ".join(responses).lower()
        elaboration_count = sum(1 for marker in elaboration_markers if marker in all_text)
        
        # Scoring
        if avg_length > 15 and elaboration_count >= 2:
            return 3  # Avanzado: respuestas elaboradas
        elif avg_length > 8 and elaboration_count >= 1:
            return 2  # Intermedio: respuestas con algo de detalle
        else:
            return 1  # Básico: respuestas breves


def calculate_english_penalty(vacancy_required_level, evaluation_result):
    """
    Calcula penalización por nivel de inglés insuficiente
    
    Args:
        vacancy_required_level: int (1-4) requerido por la vacante
        evaluation_result: dict retornado por evaluate_during_conversation()
    
    Returns:
        float: penalty (0.0 a 0.3)
    """
    demonstrated = evaluation_result["demonstrated_level"]
    consistency = evaluation_result["consistency"]
    
    # 1. Penalización por nivel insuficiente
    level_gap = vacancy_required_level - demonstrated
    
    if level_gap <= 0:
        level_penalty = 0.0  # Cumple o excede requisito
    elif level_gap == 1:
        level_penalty = 0.1  # 1 nivel abajo
    elif level_gap == 2:
        level_penalty = 0.2  # 2 niveles abajo
    else:
        level_penalty = 0.3  # 3+ niveles abajo (crítico)
    
    # 2. Penalización adicional por inconsistencia
    inconsistency_penalty = 0.05 if not consistency else 0.0
    
    total_penalty = level_penalty + inconsistency_penalty
    
    return round(total_penalty, 2)


# Example usage
if __name__ == "__main__":
    evaluator = EnglishLevelEvaluator()
    
    # Test 1: Usuario declara "Avanzado" pero respuestas son básicas
    declared = evaluator.normalize_level("Avanzado")  # 3
    responses = [
        "I use Node and databases.",
        "I know API.",
        "I think is good."
    ]
    
    result = evaluator.evaluate_during_conversation(responses, declared)
    
    print("=" * 60)
    print("TEST 1: Declared Advanced, Demonstrated Basic")
    print("=" * 60)
    print(f"Declared: {evaluator.get_level_name(result['declared_level'])}")
    print(f"Demonstrated: {evaluator.get_level_name(result['demonstrated_level'])}")
    print(f"Consistency: {'✅' if result['consistency'] else '⚠️'} {result['consistency']}")
    print(f"Score: {result['score']}")
    print(f"Issues: {result['issues']}")
    print(f"\nBreakdown:")
    for dimension, score in result['breakdown'].items():
        print(f"  - {dimension.capitalize()}: {score}/3")
    
    # Test 2: Usuario declara "Intermedio" y respuestas son intermedias
    declared2 = evaluator.normalize_level("Intermedio")  # 2
    responses2 = [
        "I have experience with backend development using Node.js and Express. I can implement REST APIs and handle async operations.",
        "When I optimize code, I usually analyze performance bottlenecks and refactor critical sections.",
        "For database queries, I use indexes and caching strategies to improve response time."
    ]
    
    result2 = evaluator.evaluate_during_conversation(responses2, declared2)
    
    print("\n" + "=" * 60)
    print("TEST 2: Declared Intermediate, Demonstrated Intermediate")
    print("=" * 60)
    print(f"Declared: {evaluator.get_level_name(result2['declared_level'])}")
    print(f"Demonstrated: {evaluator.get_level_name(result2['demonstrated_level'])}")
    print(f"Consistency: {'✅' if result2['consistency'] else '⚠️'} {result2['consistency']}")
    print(f"Score: {result2['score']}")
    print(f"Issues: {result2['issues']}")
    print(f"\nBreakdown:")
    for dimension, score in result2['breakdown'].items():
        print(f"  - {dimension.capitalize()}: {score}/3")

