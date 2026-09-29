EMERGENCY_KEYWORDS = [
    "can't breathe",
    "cannot breathe",
    "difficulty breathing",
    "severe chest pain",
    "heart attack",
    "unconscious",
    "fainted",
    "severe bleeding",
    "stroke",
    "suicide",
    "overdose",
    "severe allergic reaction"
]


def check_emergency(query):
    query_lower = query.lower()

    for keyword in EMERGENCY_KEYWORDS:
        if keyword in query_lower:
            return True

    return False


def safety_response():
    return (
        "This may require urgent medical attention. "
        "Please contact your local emergency service or seek "
        "immediate care from a qualified healthcare professional."
    )


def add_disclaimer(response):
    disclaimer = (
        "\n\n⚠️ Medical information only: "
        "This chatbot is for educational purposes and does not "
        "provide a diagnosis or replace advice from a qualified "
        "healthcare professional."
    )

    return response + disclaimer