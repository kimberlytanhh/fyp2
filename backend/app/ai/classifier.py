def classify_image(filename: str):
    filename = filename.lower()

    if "flood" in filename:
        return "flood", 0.92
    if "road" in filename or "pothole" in filename:
        return "road_damage", 0.88
    if "light" in filename:
        return "streetlight", 0.90

    return "other", 0.60
