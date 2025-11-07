"""
Consent Data Simulator - TRS Engine Core
Generates consent data based on REAL emotional log from the pipeline

Features:
- Reads from actual emotional_log_*.csv files
- Generates consent decisions based on real emotional states and match scores
- Uses actual candidate-vacancy combinations from the system
- Probabilistic consent based on emotional state and compatibility
- UTC timestamps for all entries

Usage:
    python Modules/consent_simulator.py                    # Use latest emotional log
    python Modules/consent_simulator.py --log path/to/log.csv  # Use specific log
    
Integration:
    - Reads: Logs/emotional_log_*.csv (output from emotional_inference_engine.py)
    - Generates: Consent decisions for each candidate-vacancy pair
    - Can be used to pre-populate consent data before chat_simulator.py
"""

import random
import json
import argparse
import glob
import os
import pandas as pd
from datetime import datetime, timezone


def load_latest_emotional_log(log_dir="../Logs/"):
    """Load the most recent emotional log CSV file"""
    log_files = glob.glob(os.path.join(log_dir, "emotional_log_*.csv"))
    if not log_files:
        # Try without ../ prefix (if running from root)
        log_files = glob.glob(os.path.join("Logs/", "emotional_log_*.csv"))
    
    if not log_files:
        raise FileNotFoundError("No emotional log files found in Logs/ directory")
    
    latest_log = max(log_files, key=os.path.getmtime)
    print(f"[INFO] Loading emotional log: {latest_log}")
    return pd.read_csv(latest_log)


def calculate_consent_probability(emotional_state, match_score, adjusted_score):
    """
    Calculate probability of consent based on emotional state and scores
    
    Logic:
    - Enthusiastic/Confident + High score = High probability (80-95%)
    - Neutral + Medium score = Medium probability (50-70%)
    - Frustrated/Anxious + Low score = Low probability (20-40%)
    - Negative + Any score = Very low probability (10-30%)
    """
    base_probability = {
        'positive': 0.85,
        'enthusiastic': 0.90,
        'confident': 0.85,
        'neutral': 0.60,
        'anxious': 0.40,
        'frustrated': 0.35,
        'negative': 0.20
    }
    
    # Get base probability from emotional state (case insensitive)
    emotion_lower = emotional_state.lower()
    prob = base_probability.get(emotion_lower, 0.50)
    
    # Adjust based on match score
    if match_score >= 0.7:
        prob += 0.10  # High match increases consent
    elif match_score >= 0.5:
        prob += 0.05  # Medium match slight increase
    elif match_score < 0.3:
        prob -= 0.10  # Low match decreases consent
    
    # Adjust based on adjusted score (after penalties)
    if adjusted_score >= 0.6:
        prob += 0.05
    elif adjusted_score < 0.2:
        prob -= 0.10
    
    # Keep probability in valid range [0, 1]
    return max(0.0, min(1.0, prob))


def simulate_candidates_from_log(log_df, export_path='Data/candidate_consent_log.json'):
    """
    Generate consent data based on real emotional log
    
    Args:
        log_df: DataFrame from emotional_log_*.csv
        export_path: Output file path (JSON format)
    
    Returns:
        List of generated consent profiles
    """
    profiles = []
    
    for idx, row in log_df.iterrows():
        name = row['name']
        vacancy = row['vacancy']
        emotional_state = row['emotional_state']
        match_score = row.get('match_score', 0)
        adjusted_score = row.get('adjusted_score', 0)
        
        # Calculate consent probability based on real data
        consent_prob = calculate_consent_probability(
            emotional_state, 
            match_score, 
            adjusted_score
        )
        
        # Generate consent decision
        consent_given = random.random() < consent_prob
        
        profile = {
            'candidate_id': f"{name.lower().replace(' ', '_')}_{vacancy.lower().replace(' ', '_')}",
            'name': name,
            'vacancy_selected': vacancy,
            'match_score': round(match_score, 2),
            'adjusted_score': round(adjusted_score, 2),
            'emotional_state_initial': emotional_state,
            'emotional_state_final': emotional_state,  # Could vary in real interviews
            'consent_probability': round(consent_prob, 2),
            'consent_given': consent_given,
            'consent_timestamp': datetime.now(timezone.utc).isoformat()
        }
        profiles.append(profile)
    
    # Export to JSON
    with open(export_path, mode='w', encoding='utf-8') as file:
        json.dump(profiles, file, indent=2, ensure_ascii=False)
    
    print(f'[SUCCESS] {len(profiles)} consent profiles exported to {export_path}')
    
    # Calculate and display statistics
    display_statistics(profiles)
    
    return profiles


def display_statistics(profiles):
    """Display quick statistics about generated profiles"""
    n = len(profiles)
    if n == 0:
        print("[WARNING] No profiles to display statistics for")
        return
    
    consented = sum(1 for p in profiles if p['consent_given'])
    consent_rate = (consented / n * 100) if n > 0 else 0
    
    emotions_count = {}
    vacancies_count = {}
    consent_by_emotion = {}
    
    for p in profiles:
        # Count emotions
        emotion = p['emotional_state_final']
        emotions_count[emotion] = emotions_count.get(emotion, 0) + 1
        
        # Count vacancies
        vacancy = p['vacancy_selected']
        vacancies_count[vacancy] = vacancies_count.get(vacancy, 0) + 1
        
        # Track consent by emotion
        if emotion not in consent_by_emotion:
            consent_by_emotion[emotion] = {'consented': 0, 'total': 0}
        consent_by_emotion[emotion]['total'] += 1
        if p['consent_given']:
            consent_by_emotion[emotion]['consented'] += 1
    
    print(f'\n[STATS] Quick Stats:')
    print(f'   - Total candidate-vacancy pairs: {n}')
    print(f'   - Consented: {consented} ({consent_rate:.1f}%)')
    print(f'   - Declined: {n - consented} ({100 - consent_rate:.1f}%)')
    
    print(f'\n[EMOTIONS] Emotional State Distribution & Consent Rate:')
    for emotion, count in sorted(emotions_count.items()):
        percentage = (count / n * 100) if n > 0 else 0
        consent_data = consent_by_emotion[emotion]
        emotion_consent_rate = (consent_data['consented'] / consent_data['total'] * 100) if consent_data['total'] > 0 else 0
        print(f'   - {emotion}: {count} ({percentage:.1f}%) -> {emotion_consent_rate:.0f}% consented')
    
    print(f'\n[VACANCIES] Vacancy Distribution:')
    for vacancy, count in sorted(vacancies_count.items()):
        percentage = (count / n * 100) if n > 0 else 0
        print(f'   - {vacancy}: {count} ({percentage:.1f}%)')
    
    # Calculate average match score
    avg_score = sum(p['match_score'] for p in profiles) / n if n > 0 else 0
    avg_adjusted = sum(p['adjusted_score'] for p in profiles) / n if n > 0 else 0
    print(f'\n[SCORES] Match Scores:')
    print(f'   - Average match score: {avg_score:.2f}')
    print(f'   - Average adjusted score: {avg_adjusted:.2f}')
    print(f'   - Min: {min(p["match_score"] for p in profiles):.2f}')
    print(f'   - Max: {max(p["match_score"] for p in profiles):.2f}')


def main():
    """Main function with CLI argument parsing"""
    parser = argparse.ArgumentParser(
        description='Generate consent data based on emotional log from TRS Engine'
    )
    parser.add_argument(
        '--log', '-l',
        type=str,
        default=None,
        help='Path to emotional log CSV file (default: use latest from Logs/)'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='Data/candidate_consent_log.json',
        help='Output file path (default: Data/candidate_consent_log.json)'
    )
    
    args = parser.parse_args()
    
    print('=' * 60)
    print('CONSENT DATA SIMULATOR - TRS Engine Core')
    print('=' * 60)
    print('\nGenerating consent data from emotional log...\n')
    
    try:
        # Load emotional log
        if args.log:
            print(f"[INFO] Loading specified log: {args.log}")
            log_df = pd.read_csv(args.log)
        else:
            log_df = load_latest_emotional_log()
        
        # Generate consent data
        simulate_candidates_from_log(log_df, export_path=args.output)
        
        print('\n' + '=' * 60)
        print('[COMPLETE] Consent data generation finished successfully')
        print('=' * 60)
        
    except FileNotFoundError as e:
        print(f'\n[ERROR] {e}')
        print('[INFO] Please run emotional_inference_engine.py first to generate emotional log')
        print('\n' + '=' * 60)
        return 1
    except Exception as e:
        print(f'\n[ERROR] Unexpected error: {e}')
        print('=' * 60)
        return 1
    
    return 0


if __name__ == "__main__":
    main()

