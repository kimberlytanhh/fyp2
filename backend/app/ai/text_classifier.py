import joblib
import os

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "text_model.joblib"
)

_bundle = joblib.load(MODEL_PATH)
_embedder = _bundle["embedder"]
_classifier = _bundle["classifier"]
_encoder = _bundle["label_encoder"]

def predict_text_category(text: str):
    emb = _embedder.encode([text])
    probs = _classifier.predict_proba(emb)[0]
    idx = probs.argmax()

    return {
        "category": _encoder.inverse_transform([idx])[0],
        "confidence": float(probs[idx])
    }
