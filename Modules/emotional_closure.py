import csv
from datetime import datetime
import os

# Subtask 1: Generate adaptive closing message
def generate_closing_message(candidate_name, emotional_state, vacancy_name):
    messages = {
        "enthusiastic": f"Excellent, {candidate_name}! You seem highly aligned with the *{vacancy_name}* position. Would you like to move forward?",
        "frustrated": f"We understand this process can be challenging, {candidate_name}. We believe the *{vacancy_name}* role fits your profile well. Shall we proceed?",
        "neutral": f"We've found a position that matches your profile: *{vacancy_name}*. Would you like to continue with this option?",
        "anxious": f"Thank you for your time, {candidate_name}. The *{vacancy_name}* role looks like a good opportunity for you. Shall we take the next step together?",
        "confident": f"All set, {candidate_name}. The *{vacancy_name}* position is a strong match. Ready to move forward?"
    }
    return messages.get(emotional_state.lower(), f"{candidate_name}, would you like to proceed with the *{vacancy_name}* position?")

# Subtask 2: Register consent and export to CSV
def register_consent(candidate_id, vacancy_selected, emotional_state_final, consent_given, export_path="consent_log.csv"):
    log_entry = {
        "candidate_id": candidate_id,
        "vacancy_selected": vacancy_selected,
        "emotional_state_final": emotional_state_final,
        "consent_given": consent_given,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    file_exists = os.path.isfile(export_path)
    with open(export_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=log_entry.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(log_entry)

    print(" Consent log entry saved:", log_entry)
    return log_entry

# 🧪 Example usage
if __name__ == "__main__":
    name = "Luis"
    emotion = "enthusiastic"
    vacancy = "Backend LATAM"
    candidate_id = "luis_gomez_001"

    message = generate_closing_message(name, emotion, vacancy)
    print(" Closing message:", message)

    user_response = "yes"
    consent = user_response.lower() in ["yes", "y", "i want to proceed"]

    register_consent(candidate_id, vacancy, emotion, consent)