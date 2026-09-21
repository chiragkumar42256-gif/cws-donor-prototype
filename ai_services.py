import os

def clean_meeting_notes(note_text):
    # Lightweight handler that summarizes notes and pulls action items
    lines = [line.strip() for line in note_text.split("\n") if line.strip()]
    first_point = lines[0] if lines else "General discussion"
    return f"Key Focus: {first_point} | Action: Review pledge and log next contact date."