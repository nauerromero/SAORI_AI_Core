import json
import random

# Sample data pools
names = ["Luis", "Camila", "Jorge", "Ana", "Mateo", "Valentina", "Carlos", "Sofia", "Diego", "Laura"]
stacks = ["Python", "JavaScript", "React", "Node.js", "SQL", "AWS", "Docker", "TensorFlow", "C#", "Go"]
modalities = ["Remote", "Hybrid", "On-site"]
emotional_states = ["Positive", "Neutral", "Negative"]
zones = ["North", "South", "East", "West", "Central"]

def generate_profile(name):
    return {
        "name": name,
        "stack": random.sample(stacks, k=3),
        "experience_years": random.randint(1, 10),
        "emotional_state": random.choice(emotional_states),
        "preferred_modality": random.choice(modalities),
        "zone": random.choice(zones)
    }

def generate_profiles(n=10):
    return [generate_profile(name) for name in names[:n]]

def save_profiles(profiles, path="data/profiles.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=4)

if __name__ == "__main__":
    profiles = generate_profiles()
    save_profiles(profiles)
    print(f"{len(profiles)} profiles saved to data/profiles.json")
