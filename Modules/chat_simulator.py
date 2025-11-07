"""
Chat Simulator Module for TRS Engine Core
Simulates technical interviews with candidates and generates comprehensive reports

Features:
- Load emotional log data from CSV files
- Simulate technical conversations with questions based on vacancy and level
- Evaluate response quality and confidence
- Detect inconsistencies in candidate responses
- Suggest candidate upgrades based on performance
- Calculate timezone compatibility with team locations
- Suggest optimal meeting times across multiple timezones
- Export results to Markdown and CSV formats

Integration:
- questions_bank: Technical questions by vacancy and level
- response_evaluator: Response quality assessment
- timezone_compatibility: Timezone overlap and meeting suggestions
"""

import pandas as pd
import random
import glob
import os
from questions_bank import questions_bank
from response_evaluator import summarize_response_quality
from timezone_compatibility import (
    resolve_timezone_from_location,
    assess_timezone_compatibility,
    suggest_meeting_time
)
from report_generator import (
    generate_markdown_report,
    export_to_markdown_file,
    export_to_csv_file
)
from recruiter_assignment import (
    assign_recruiter,
    assign_batch,
    infer_vacancy_area,
    infer_location_region
)
from emotional_closure import generate_closing_message

# NOTE: Timezone locations are now read directly from JSON files
# profiles.json contains "location" for each candidate
# Vacancy.json contains "location" field (string or list) for each vacancy
# recruiters.json contains recruiters with their locations and specialties
# Recruiters are dynamically assigned based on specialty, region, and workload

response_templates = {
    "backend": [
        "I'd use async/await and proper error handling.",
        "We scaled using load balancers and caching layers.",
        "Yes, I've worked with that in production.",
        "I usually handle that with standard tools.",
        "I'm not sure, I haven't used that much."
    ],
    "data": [
        "ETL is essential for transforming raw data into usable formats.",
        "I built pipelines using Airflow and Python.",
        "We used Spark for distributed processing.",
        "I usually handle that with standard tools.",
        "I'm not sure, I haven't used that much."
    ],
    "admin": [
        "I use Google Calendar and Trello for scheduling.",
        "I prioritize tasks using urgency and impact.",
        "Yes, I've worked with that in production.",
        "I usually handle that with standard tools.",
        "I'm not sure, I haven't used that much."
    ]
}

def load_latest_emotional_log(log_dir="Logs/"):
    log_files = glob.glob(os.path.join(log_dir, "emotional_log_*.csv"))
    if not log_files:
        print("[ERROR] No emotional log files found.")
        return []

    latest_log = max(log_files, key=os.path.getmtime)
    print(f"[INFO] Loaded latest log: {latest_log}")
    df = pd.read_csv(latest_log)
    return df.to_dict(orient="records")

def infer_technical_level(score):
    if score >= 80:
        return "senior"
    elif score >= 60:
        return "mid"
    else:
        return "junior"

def simulate_english_level(emotional_state):
    if emotional_state == "negative":
        return random.choice(["A2", "B1"])
    elif emotional_state == "neutral":
        return random.choice(["B1", "B2", "C1"])
    else:
        return random.choice(["B2", "C1", "C2"])

def get_domain(vacancy):
    vacancy = vacancy.lower()
    if "node" in vacancy or "backend" in vacancy or "ror" in vacancy:
        return "backend"
    elif "data" in vacancy or "engineer" in vacancy:
        return "data"
    elif "admin" in vacancy or "assistant" in vacancy:
        return "admin"
    return "backend"

def simulate_responses(questions, domain):
    responses = []
    for q in questions:
        simulated = random.choice(response_templates.get(domain, response_templates["backend"]))
        latency = random.uniform(5, 25)
        quality = summarize_response_quality(simulated, latency)
        responses.append((q, simulated, quality, latency))
    return responses

def detect_inconsistencies(entry, responses):
    issues = []
    tech_level = entry.get("technical_level", "mid").lower()
    seen_responses = {}
    repeated_count = 0

    for q, r, quality, latency in responses:
        if r in seen_responses:
            repeated_count += 1
        seen_responses[r] = seen_responses.get(r, 0) + 1

        if tech_level == "senior":
            if "not sure" in r or "haven't used" in r:
                issues.append("Claimed seniority but lacked confidence in key topics.")
            if quality["confidence"] == "Low":
                issues.append("Senior level claimed but response confidence is low.")

        if quality["confidence"] == "Low" and "standard tools" in r.lower():
            issues.append("Generic response with low confidence detected.")

        if latency > 15 and quality["confidence"] in ["Low", "Medium"]:
            issues.append("Possible web lookup detected due to long latency and generic phrasing.")

        expected_keywords = {
            "ETL": ["etl", "extract", "transform", "load"],
            "ActiveRecord": ["activerecord", "orm", "model"],
            "calendar": ["calendar", "schedule", "google", "trello"],
            "environment variables": ["env", "dotenv", "config", "variables"]
        }
        for key, keywords in expected_keywords.items():
            if key.lower() in q.lower():
                if not any(k in r.lower() for k in keywords):
                    issues.append(f"Response to '{key}' question lacks expected keywords.")

    if repeated_count >= 1:
        issues.append("Repeated response detected across multiple questions.")

    vacancy = entry.get("vacancy", "")
    if "React" in vacancy and not any("hooks" in r.lower() for _, r, _, _ in responses):
        issues.append("React experience claimed but no mention of hooks or state management.")

    return issues

def suggest_upgrade(entry, responses):
    score = entry.get("match_score", 0)
    level = entry.get("technical_level", "mid")
    upgrade = None
    justification = []

    high_confidence_count = sum(1 for _, _, q, l in responses if q["confidence"] == "High" and l < 15)

    if level == "junior" and (score >= 60 or high_confidence_count >= 2):
        upgrade = "Mid-level " + entry["vacancy"]
        justification.append("Strong technical responses despite junior level")
    elif level == "mid" and (score >= 80 or high_confidence_count >= 2):
        upgrade = "Senior " + entry["vacancy"]
        justification.append("Consistent high-confidence answers")

    if upgrade:
        justification.append(f"{high_confidence_count} high-confidence responses under 15s")
        return upgrade, justification
    return None, []

# NOTE: generate_markdown, simulate_conversation, and export_to_csv functions
# have been replaced by the report_generator module for better code organization
def run_simulation():
    """Main function to run interview simulation for all candidates"""
    entries = load_latest_emotional_log()
    if not entries:
        print("[INFO] No entries found in emotional log.")
        return

    # Load vacancies, profiles, and recruiters
    import json
    try:
        # Load vacancies
        with open("Data/Vacancy.json", "r", encoding="utf-8") as f:
            vacancies_data = json.load(f)
        # Create mappings for vacancies
        vacancy_locations = {}  # vacancy title -> location(s)
        vacancy_zones = {}      # vacancy title -> zone (kept for reporting)
        for v in vacancies_data:
            if "title" in v:  # Skip metadata entries
                vacancy_locations[v["title"]] = v.get("location", "New York, USA")
                vacancy_zones[v["title"]] = v.get("zone", "Global")
        
        # Load profiles
        with open("Data/profiles.json", "r", encoding="utf-8") as f:
            profiles_data = json.load(f)
        # Create mappings for candidates
        candidate_locations = {}    # candidate name -> location
        candidate_zones = {}        # candidate name -> zone (kept for reporting)
        for p in profiles_data:
            candidate_locations[p["name"]] = p.get("location", "Bogota, Colombia")
            candidate_zones[p["name"]] = p.get("zone", "Central")
        
        # Load recruiters
        with open("Data/recruiters.json", "r", encoding="utf-8") as f:
            recruiters_data = json.load(f)
        
        # Prepare candidates for batch assignment
        # Analyze vacancies by MATCH SCORE (not just count) for better recruiter matching
        candidate_data = {}  # candidate name -> {area: total_match_score}
        
        for entry in entries:
            name = entry["name"]
            vacancy_title = entry["vacancy"]
            match_score = entry.get("match_score", 0)
            
            # Only consider meaningful matches (score > 0.2)
            if match_score < 0.2:
                continue
            
            area = infer_vacancy_area(vacancy_title)
            
            if name not in candidate_data:
                candidate_data[name] = {"areas": {}, "vacancies": []}
            
            # Accumulate match scores by area
            if area not in candidate_data[name]["areas"]:
                candidate_data[name]["areas"][area] = 0
            candidate_data[name]["areas"][area] += match_score
            candidate_data[name]["vacancies"].append(vacancy_title)
        
        # Create assignment list with weighted area analysis
        candidates_for_assignment = []
        
        for name, data in candidate_data.items():
            location = candidate_locations.get(name, "Bogota, Colombia")
            location_region = infer_location_region(location)
            
            # Determine primary area by TOTAL MATCH SCORE (weighted by quality of fit)
            if data["areas"]:
                primary_area = max(data["areas"], key=data["areas"].get)
            else:
                # Fallback if no good matches
                primary_area = "tech"
            
            candidates_for_assignment.append({
                "name": name,
                "vacancy_area": primary_area,
                "location_region": location_region,
                "location": location,
                "vacancy_count": len(data["vacancies"]),
                "area_distribution": data["areas"]
            })
        
        # Assign recruiters dynamically
        assigned_candidates = assign_batch(candidates_for_assignment, recruiters_data)
        
        # Create mapping of candidate name -> assigned recruiter
        candidate_recruiters = {c["name"]: c["assigned_recruiter"] for c in assigned_candidates}
                
    except Exception as e:
        print(f"[WARNING] Could not load data: {e}")
        vacancy_locations = {}
        vacancy_zones = {}
        candidate_locations = {}
        candidate_zones = {}
        candidate_recruiters = {}

    all_results = []

    for entry in entries:
        # Simulate conversation and capture all data
        name = entry["name"]
        vacancy = entry["vacancy"]
        emotion = entry["emotional_state"].lower()
        score = entry.get("match_score", 0)
        tech_level = entry.get("technical_level") or infer_technical_level(score)
        entry["technical_level"] = tech_level

        print("=" * 60)
        print(f"[CHAT] Simulating conversation with {name} -> {vacancy}")
        print("=" * 60)

        # Connection check
        connection_ok = random.choice(["yes", "no"])
        connection_flag = "unstable" if connection_ok == "no" else "stable"

        # English level
        english_level = simulate_english_level(emotion)

        # Get questions and responses
        questions = questions_bank.get(vacancy, {}).get(tech_level, [])
        domain = get_domain(vacancy)
        responses = simulate_responses(questions, domain)
        inconsistencies = detect_inconsistencies(entry, responses)
        upgrade, justification = suggest_upgrade(entry, responses)

        # Calculate timezone compatibility between candidate and their assigned recruiter
        try:
            # Get candidate's location and assigned recruiter
            candidate_location = candidate_locations.get(name, "Bogota, Colombia")
            candidate_zone = candidate_zones.get(name, "Central")
            candidate_tz = resolve_timezone_from_location(candidate_location)
            
            # Get candidate's dynamically assigned recruiter
            assigned_recruiter = candidate_recruiters.get(name)
            
            vacancy_zone = vacancy_zones.get(vacancy, "Global")
            
            # Special handling for "Global" positions
            if vacancy_zone == "Global":
                # Global positions accept candidates from anywhere
                # Assign high compatibility score (100%) since timezone is not a constraint
                avg_score = 100.0
                recruiter_name = assigned_recruiter.get("name", "N/A") if assigned_recruiter else "N/A"
                suggestion = f"Global position - flexible timezone, async work supported (Recruiter: {recruiter_name})"
                local_times = [f"{candidate_location}: Fully flexible"]
            else:
                # For specific zone positions, use recruiter's location for timezone calculation
                if assigned_recruiter and "location" in assigned_recruiter:
                    recruiter_location = assigned_recruiter["location"]
                    recruiter_name = assigned_recruiter["name"]
                    recruiter_tz = resolve_timezone_from_location(recruiter_location)
                    
                    # Calculate compatibility with recruiter's timezone
                    compatibility = assess_timezone_compatibility(candidate_tz, recruiter_tz)
                    avg_score = compatibility["compatibility_score"]
                    zones = [candidate_tz, recruiter_tz]
                    suggestion, local_times = suggest_meeting_time(zones)
                    suggestion = f"Meeting with recruiter {recruiter_name} ({recruiter_location}): {suggestion}"
                else:
                    # Fallback to vacancy location if recruiter not assigned
                    vacancy_location_data = vacancy_locations.get(vacancy, "New York, USA")
                    team_locations = [vacancy_location_data] if not isinstance(vacancy_location_data, list) else vacancy_location_data
                    team_tz_list = [resolve_timezone_from_location(loc) for loc in team_locations]
                    compatibilities = [assess_timezone_compatibility(candidate_tz, team_tz) for team_tz in team_tz_list]
                    avg_score = sum(c["compatibility_score"] for c in compatibilities) / len(compatibilities) if compatibilities else 0
                    zones = [candidate_tz] + team_tz_list
                    suggestion, local_times = suggest_meeting_time(zones)
                    recruiter_name = "Unassigned"
                    recruiter_location = "N/A"
            
            entry["timezone_data"] = {
                "candidate_zone": candidate_zone,
                "candidate_location": candidate_location,
                "candidate_tz": candidate_tz,
                "vacancy_zone": vacancy_zone,
                "recruiter_name": assigned_recruiter.get("name", "N/A") if assigned_recruiter else "Unassigned",
                "recruiter_location": assigned_recruiter.get("location", "N/A") if assigned_recruiter else "N/A",
                "avg_score": round(avg_score, 1),
                "meeting_suggestion": suggestion,
                "local_times": local_times
            }
        except Exception as e:
            print(f"[WARNING] Could not calculate timezone compatibility for {name}: {e}")

        # Generate closing message based on emotional state
        closing_message = generate_closing_message(name, emotion, vacancy)
        
        # Simulate candidate consent (in production, this would be actual user input)
        # For now, we simulate based on emotional state and match score
        consent_probability = 0.9 if emotion in ["enthusiastic", "confident"] and score >= 0.6 else 0.5
        consent_given = random.random() < consent_probability
        
        print(f"[CLOSURE] Message: {closing_message}")
        print(f"[CLOSURE] Candidate consent: {'YES' if consent_given else 'NO'}")
        
        # Store results
        all_results.append({
            "responses": responses,
            "inconsistencies": inconsistencies,
            "upgrade": upgrade,
            "justification": justification,
            "connection_flag": connection_flag,
            "english_level": english_level,
            "closing_message": closing_message,
            "consent_given": consent_given,
            "emotional_state_final": emotion
        })

    # Generate reports using report_generator module
    print("\n" + "=" * 60)
    print("[INFO] Generating reports...")
    print("=" * 60)
    
    markdown_report = generate_markdown_report(entries, all_results)
    export_to_markdown_file(markdown_report)
    export_to_csv_file(entries, all_results)

if __name__ == "__main__":
    run_simulation()
