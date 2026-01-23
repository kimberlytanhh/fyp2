from app.ai.text_classifier import predict_text_category

tests = [
    "jalan rosak dekat taman perumahan",
    "air naik lepas hujan lebat",
    "accident happened but not sure how",
    "this looks dangerous",
    "garbage everywhere behind shops"
]

for t in tests:
    print(t, "→", predict_text_category(t))
