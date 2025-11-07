import json
import random
from datetime import datetime
import os
import csv

# Load profiles and vacancies
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Match score based on shared stack
def calculate_match_score(profile_stack, vacancy_stack):
    return len(set(profile_stack) & set(vacancy_stack)) / len(vacancy_stack)

# Penalty logic
def apply_penalties(profile, vacancy):
    penalty = 0
    if profile["preferred_modality"] != vacancy["modality"]:
        penalty += 0.2
    if profile["zone"] != vacancy["zone"]:
        penalty += 0.2
    if vacancy.get("urgency", "low") == "high":
        penalty += 0.1
    return penalty

# Emotional message generator
def generate_message(profile, match_score, penalty):
    tone = profile["emotional_state"]
    if tone == "Negative":
        return f"Hi {profile['name']}, we understand you're going through a tough time. We're here to support you."
    elif tone == "Neutral":
        return f"Hello {profile['name']}, thanks for your interest. Here's a vacancy that might suit you."
    else:
        return f"Hey {profile['name']}! Great energy — this opportunity could be a perfect fit!"

# Main inference loop
def run_inference(profiles_path, vacancies_path):
    profiles = load_json(profiles_path)
    vacancies = load_json(vacancies_path)
    
    # Filter out metadata objects
    vacancies = [v for v in vacancies if "title" in v]
    
    results = []

    for profile in profiles:
        for vacancy in vacancies:
            match_score = calculate_match_score(profile["stack"], vacancy["stack"])
            penalty = apply_penalties(profile, vacancy)
            adjusted_score = round(match_score - penalty, 2)
            message = generate_message(profile, match_score, penalty)

            results.append({
                "name": profile["name"],
                "vacancy": vacancy["title"],
                "match_score": round(match_score, 2),
                "penalty": round(penalty, 2),
                "adjusted_score": adjusted_score,
                "emotional_state": profile["emotional_state"],
                "message": message
            })

    return results

# Save results to markdown log file
def save_results_to_log(results, profiles, vacancies, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_dir = "Logs"
    
    # Create Logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    filename = f"{log_dir}/inference_results_{timestamp}.md"
    
    # Group results by profile
    profiles_dict = {p["name"]: p for p in profiles}
    results_by_profile = {}
    for r in results:
        name = r["name"]
        if name not in results_by_profile:
            results_by_profile[name] = []
        results_by_profile[name].append(r)
    
    # Count emotional states
    emotional_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
    for profile in profiles:
        emotional_counts[profile["emotional_state"]] += 1
    
    # Generate markdown content
    content = f"""# Emotional Inference Engine Results

**Generation Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Total Profiles Evaluated:** {len(profiles)}  
**Total Vacancies:** {len(vacancies)}  
**Combinations Analyzed:** {len(results)}

---

## Executive Summary

This document contains the results of the TRS Engine Core emotional inference engine, which evaluates compatibility between candidates and job vacancies considering:

- **Match Score:** Technology/stack overlap between candidate and vacancy
- **Penalties:** Deductions for mismatches in modality, zone, and urgency
- **Adjusted Score:** Final score after applying penalties (match_score - penalty)
- **Emotional Message:** Personalized message based on candidate's emotional state

---

## Detailed Results by Candidate

"""
    
    # Add results for each profile
    for idx, (name, profile_results) in enumerate(results_by_profile.items(), 1):
        profile = profiles_dict[name]
        state_emoji = "⭐" if profile["emotional_state"] == "Positive" else ("🆘" if profile["emotional_state"] == "Negative" else "")
        
        content += f"""### {idx}. {name} ({profile["emotional_state"]}) {state_emoji}
**Stack:** {", ".join(profile["stack"])} | **Experience:** {profile["experience_years"]} years | **Preferred Modality:** {profile["preferred_modality"]} | **Zone:** {profile["zone"]}

| Vacancy | Match Score | Penalty | Adjusted Score | Message |
|---------|-------------|---------|----------------|---------|
"""
        
        for result in profile_results:
            content += f"| {result['vacancy']} | {result['match_score']:.2f} | {result['penalty']:.2f} | {result['adjusted_score']:.2f} | {result['message']} |\n"
        
        content += "\n---\n\n"
    
    # Add analysis section
    best_matches = sorted([r for r in results if r["adjusted_score"] >= -0.10], 
                         key=lambda x: x["adjusted_score"], reverse=True)[:5]
    
    content += f"""## Pattern Analysis

### Emotional States
- **Positive:** {emotional_counts['Positive']} candidates
- **Neutral:** {emotional_counts['Neutral']} candidates
- **Negative:** {emotional_counts['Negative']} candidates 🆘

### Best Matches (Top 5 by Adjusted Score)
"""
    
    for idx, match in enumerate(best_matches, 1):
        content += f"{idx}. **{match['name']}** → {match['vacancy']} ({match['adjusted_score']:.2f})\n"
    
    content += f"""

### Recommendations
- Candidates with negative emotional states require personalized support messages
- Most common penalties are due to modality and zone mismatches
- Consider adjusting stack requirements to improve overall match rates
- Implement upskilling strategies for promising candidates

---

**Generated by:** TRS Engine Core - Emotional Inference Engine  
**Version:** 1.0  
**Log file:** {filename}
"""
    
    # Write to file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    return filename

# Save results to CSV for data visualization
def save_to_csv(results, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    log_dir = "Logs"
    
    # Create Logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    path = f"{log_dir}/emotional_log_{timestamp}.csv"
    fieldnames = ["name", "vacancy", "match_score", "penalty", "adjusted_score", "emotional_state", "message"]
    
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    
    return path

def main():
    """Main function to run full inference pipeline"""
    profiles_path = "Data/profiles.json"
    vacancies_path = "Data/Vacancy.json"
    
    # Load data
    profiles = load_json(profiles_path)
    vacancies = load_json(vacancies_path)
    
    # Filter out metadata
    vacancies = [v for v in vacancies if "title" in v]
    
    # Run inference
    output = run_inference(profiles_path, vacancies_path)
    
    # Generate timestamp for both files
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Print results to console
    print(f"\n{'='*80}")
    print(f"TRS ENGINE CORE - EMOTIONAL INFERENCE RESULTS")
    print(f"{'='*80}\n")
    
    for entry in output:
        print(f"[{entry['name']:15}] | {entry['vacancy']:35} | Score: {entry['adjusted_score']:6.2f}")
    
    # Save to markdown log file
    log_file = save_results_to_log(output, profiles, vacancies, timestamp)
    
    # Save to CSV file for visualization
    csv_file = save_to_csv(output, timestamp)
    
    print(f"\n{'='*80}")
    print(f"[OK] Results saved to:")
    print(f"     Markdown: {log_file}")
    print(f"     CSV:      {csv_file}")
    print(f"     Total entries: {len(output)}")
    print(f"{'='*80}\n")

def run_inference_with_timestamp():
    """Run inference and generate files with current timestamp"""
    main()

if __name__ == "__main__":
    main()

