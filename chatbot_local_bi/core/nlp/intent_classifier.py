# core/nlp/intent_classifier.py
from sentence_transformers import SentenceTransformer, util
import torch # Added for torch.max

class IntentClassifier:
    def __init__(self):
        # Utilisation d'un modèle multilingue léger, excellent pour le français et l'arabe
        self.model = SentenceTransformer('intfloat/multilingual-e5-small') # Changed model
        self.intents = {
            'greet': [
                "bonjour", "salut", "hello", "coucou"
            ],
            'extract_data': [
                "extraire les données de ce document",
                "lis ce fichier",
                "peux-tu analyser ce pdf",
                "extrais le texte",
                "parse ce document"
            ],
            'analyze_data': [
                "fais une analyse de ces données",
                "montre-moi des indicateurs clés",
                "génère un graphique",
                "crée un dashboard",
                "analyse ce fichier excel"
            ],
            'generate_report': [
                "générer un rapport",
                "crée un compte rendu",
                "fais un résumé au format pdf",
                "je veux un rapport"
            ]
        }
        # Pré-calcul des embeddings pour l'efficacité
        self.intent_embeddings = {}
        for intent, phrases in self.intents.items():
            # Prepend "query: " for e5 models
            queries_to_embed = ["query: " + phrase for phrase in phrases]
            self.intent_embeddings[intent] = self.model.encode(queries_to_embed, convert_to_tensor=True)

    def classify(self, user_message):
        if not user_message:
            return 'unknown'

        # Prepend "query: " for e5 models
        message_to_embed = "query: " + user_message
        message_embedding = self.model.encode(message_to_embed, convert_to_tensor=True)

        best_score = 0.0 # Initialize best_score as float
        best_intent = 'unknown'

        for intent, phrases_embeddings in self.intent_embeddings.items():
            # Calculer la similarité cosinus entre le message et les phrases de l'intention
            # message_embedding is likely [1, dim], phrases_embeddings is [N, dim]
            # util.cos_sim returns a tensor of shape [1, N]
            cos_scores = util.cos_sim(message_embedding, phrases_embeddings)[0] # Get the scores for the single message_embedding

            # Find the max score for this intent's phrases
            current_max_score_tensor = torch.max(cos_scores)
            current_max_score = current_max_score_tensor.item() # Convert tensor to float

            if current_max_score > best_score:
                best_score = current_max_score
                best_intent = intent

        # Seuil de confiance pour éviter les faux positifs
        if best_score > 0.5: # best_score is now float
            return best_intent
        else:
            return 'unknown'
