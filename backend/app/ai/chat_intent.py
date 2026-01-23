from sentence_transformers import SentenceTransformer, util

# Load once (important for performance)
model = SentenceTransformer("all-MiniLM-L6-v2")

INTENTS = {
    "most_category": [
        "which category has the most reports",
        "most common incident",
        "which incident type appears most"
    ],
    "pending_reports": [
        "how many reports are pending",
        "reports waiting for review",
        "pending incidents"
    ],
    "resolved_reports": [
        "how many reports are resolved",
        "resolved incidents",
        "closed reports"
    ]
}

# Precompute embeddings
intent_embeddings = {
    k: model.encode(v, convert_to_tensor=True)
    for k, v in INTENTS.items()
}

def detect_intent(user_message: str):
    query_embedding = model.encode(user_message, convert_to_tensor=True)

    best_intent = None
    best_score = 0

    for intent, embeddings in intent_embeddings.items():
        score = util.cos_sim(query_embedding, embeddings).max().item()
        if score > best_score:
            best_score = score
            best_intent = intent

    # Threshold prevents random matches
    if best_score < 0.5:
        return None

    return best_intent
