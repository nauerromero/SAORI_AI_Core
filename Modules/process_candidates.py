"""
TRS Engine - Candidate Processing Pipeline
Complete automation of recruitment process from simulation to final reports

Features:
- Automatic emotional log generation (always creates new log with current timestamp)
- Interview simulation with timezone compatibility
- Intelligent candidate filtering
- Specialized reports for accepted/rejected candidates
- Talent pool management
- Personalized feedback generation

Behavior:
- Each execution generates fresh logs with current date/time
- Old logs are automatically cleaned up before new generation
- All reports are timestamped for audit trail
"""

import os
import sys
import time
import pandas as pd
from datetime import datetime

# Import modules from same directory
from emotional_inference_engine import run_inference_with_timestamp
from chat_simulator import run_simulation
from candidate_filter import (
    generate_final_batch,
    categorize_rejected_candidates,
    generate_feedback_for_rejected,
    export_rejected_candidates_report,
    create_talent_pool_entry,
    generate_filter_report
)


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_step(step, total, message):
    """Print pipeline step"""
    print(f"[{step}/{total}] {message}...", end=" ", flush=True)


def print_done(elapsed=None):
    """Print completion message"""
    if elapsed:
        print(f"[OK] Done ({elapsed:.1f}s)")
    else:
        print("[OK] Done")


def step_1_generate_emotional_log():
    """Step 1: Generate emotional inference log with current timestamp"""
    print_step(1, 5, "Generating emotional log")
    start = time.time()
    
    try:
        # Always generate new log with current timestamp
        import glob
        
        # Save list of old logs before generating new one
        old_logs = glob.glob("../Logs/emotional_log_*.csv")
        old_results = glob.glob("../Logs/inference_results_*.md")
        
        # Generate new log with current timestamp
        run_inference_with_timestamp()
        
        # Verify new log was created
        new_logs = glob.glob("../Logs/emotional_log_*.csv")
        new_log_created = [log for log in new_logs if log not in old_logs]
        
        if new_log_created:
            print(f"   [INFO] Created: {os.path.basename(new_log_created[0])}")
            
            # Now remove old logs (keeping only the new one)
            for old_log in old_logs:
                try:
                    os.remove(old_log)
                    print(f"   [INFO] Removed old log: {os.path.basename(old_log)}")
                except:
                    pass
            
            # Remove old inference results
            for old_result in old_results:
                try:
                    os.remove(old_result)
                    print(f"   [INFO] Removed old result: {os.path.basename(old_result)}")
                except:
                    pass
        
        elapsed = time.time() - start
        print_done(elapsed)
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def step_2_simulate_interviews():
    """Step 2: Simulate interviews with timezone compatibility"""
    print_step(2, 5, "Simulating interviews")
    start = time.time()
    
    try:
        run_simulation()
        elapsed = time.time() - start
        print_done(elapsed)
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def step_3_filter_candidates():
    """Step 3: Filter and categorize candidates"""
    print_step(3, 5, "Filtering candidates")
    start = time.time()
    
    try:
        # Load CSV data
        csv_path = "../Logs/reports/rrhh_registry.csv" if os.path.exists("../Logs/reports/rrhh_registry.csv") else "Logs/reports/rrhh_registry.csv"
        df = pd.read_csv(csv_path)
        
        # Convert to candidate format
        candidates = []
        for _, row in df.iterrows():
            candidates.append({
                "name": row["Nombre"],
                "vacancy": row["Vacante"],
                "avg_score": row["Compatibilidad TZ"] if pd.notna(row["Compatibilidad TZ"]) else 0,
                "emotional_state": row["Estado emocional"],
                "issue_count": row["Inconsistencias detectadas"],
                "match_score": row["Match Score"]
            })
        
        # Filter candidates
        accepted = generate_final_batch(candidates)
        rejected = [c for c in candidates if c not in accepted]
        
        elapsed = time.time() - start
        print_done(elapsed)
        return candidates, accepted, rejected
    except Exception as e:
        print(f"[ERROR] {e}")
        return None, None, None


def step_4_generate_reports(accepted, rejected):
    """Step 4: Generate specialized reports"""
    print_step(4, 5, "Generating reports")
    start = time.time()
    
    try:
        # Generate accepted candidates report
        generate_accepted_report(accepted)
        
        # Generate rejected candidates report
        export_rejected_candidates_report(rejected)
        
        # Generate individual feedback files
        generate_feedback_files(rejected)
        
        elapsed = time.time() - start
        print_done(elapsed)
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def step_5_create_talent_pool(rejected):
    """Step 5: Create talent pool database"""
    print_step(5, 5, "Creating talent pool")
    start = time.time()
    
    try:
        categories = categorize_rejected_candidates(rejected)
        talent_pool = []
        
        for candidate in categories.get('potential', []):
            entry = create_talent_pool_entry(candidate, "Close to threshold")
            talent_pool.append(entry)
        
        # Save talent pool CSV
        if talent_pool:
            df_pool = pd.DataFrame(talent_pool)
            os.makedirs("../Logs/reports", exist_ok=True)
            df_pool.to_csv("../Logs/reports/talent_pool.csv", index=False, encoding="utf-8")
        
        elapsed = time.time() - start
        print_done(elapsed)
        return talent_pool
    except Exception as e:
        print(f"[ERROR] {e}")
        return []


def generate_accepted_report(accepted):
    """Generate report for accepted candidates"""
    report = f"# Accepted Candidates Report\n\n"
    report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += f"**Total Accepted:** {len(accepted)}\n\n"
    report += "---\n\n"
    
    report += "## Top Candidates for Hire\n\n"
    report += "*These candidates passed all filters and are recommended for hire*\n\n"
    
    for i, candidate in enumerate(accepted, 1):
        report += f"### {i}. {candidate['name']} - {candidate['vacancy']}\n\n"
        report += f"- **Timezone Compatibility:** {candidate.get('avg_score', 0):.1f}%\n"
        report += f"- **Emotional State:** {candidate.get('emotional_state', 'Unknown')}\n"
        report += f"- **Inconsistencies:** {candidate.get('issue_count', 0)}\n"
        report += f"- **Match Score:** {candidate.get('match_score', 0):.2f}\n"
        report += f"- **Status:** [APPROVED] Ready for offer\n\n"
    
    # Add next steps
    report += "---\n\n"
    report += "## Next Steps\n\n"
    report += "1. Schedule final interviews with hiring managers\n"
    report += "2. Prepare offer letters\n"
    report += "3. Conduct reference checks\n"
    report += "4. Send offers within 48 hours\n"
    
    # Save report
    os.makedirs("../Logs/reports", exist_ok=True)
    with open("../Logs/reports/accepted_candidates.md", "w", encoding="utf-8") as f:
        f.write(report)


def generate_feedback_files(rejected):
    """Generate individual feedback files for rejected candidates"""
    os.makedirs("../Logs/reports/feedback", exist_ok=True)
    
    for candidate in rejected[:10]:  # Limit to first 10
        feedback = generate_feedback_for_rejected(candidate)
        filename = f"../Logs/reports/feedback/{candidate['name']}_feedback.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(feedback)


def print_summary(candidates, accepted, rejected, talent_pool, total_time):
    """Print final summary dashboard"""
    categories = categorize_rejected_candidates(rejected)
    
    print_header("SUMMARY")
    
    print(f"\nTotal Candidates:              {len(candidates)}")
    print(f"[ACCEPTED]                     {len(accepted)}")
    
    if accepted:
        names = [c['name'] for c in accepted[:5]]
        print(f"   Top candidates: {', '.join(names)}")
    
    print(f"\n[REJECTED]                     {len(rejected)}")
    print(f"   [POTENTIAL] Talent pool:    {len(categories.get('potential', []))}")
    print(f"   [LOW TZ] Low timezone:      {len(categories.get('low_timezone', []))}")
    print(f"   [NEGATIVE] Emotion:         {len(categories.get('negative_emotion', []))}")
    print(f"   [ISSUES] Too many issues:   {len(categories.get('too_many_issues', []))}")
    print(f"   [LOW MATCH] Score:          {len(categories.get('low_match_score', []))}")
    
    print(f"\n[TALENT POOL] Created:         {len(talent_pool)} candidates")
    
    if talent_pool:
        for entry in talent_pool:
            print(f"   - {entry['name']}: Review on {entry['review_date']}")
    
    print(f"\n[REPORTS] Files generated:")
    print(f"   - Logs/reports/rrhh_registry.md (all candidates)")
    print(f"   - Logs/reports/rrhh_registry.csv (all candidates)")
    print(f"   - Logs/reports/accepted_candidates.md ({len(accepted)} candidates)")
    print(f"   - Logs/reports/rejected_candidates.md ({len(rejected)} candidates)")
    
    if talent_pool:
        print(f"   - Logs/reports/talent_pool.csv ({len(talent_pool)} entries)")
    
    feedback_count = min(10, len(rejected))
    if feedback_count > 0:
        print(f"   - Logs/reports/feedback/ ({feedback_count} feedback files)")
    
    print(f"\n[TIME] Total time: {total_time:.1f} seconds")
    print("=" * 60)


def main():
    """Main pipeline execution"""
    start_total = time.time()
    
    print_header("TRS ENGINE - CANDIDATE PROCESSING PIPELINE")
    
    # Step 1: Generate emotional log
    if not step_1_generate_emotional_log():
        print("\n[ERROR] Pipeline failed at step 1")
        return
    
    # Step 2: Simulate interviews
    if not step_2_simulate_interviews():
        print("\n[ERROR] Pipeline failed at step 2")
        return
    
    # Step 3: Filter candidates
    candidates, accepted, rejected = step_3_filter_candidates()
    if candidates is None:
        print("\n[ERROR] Pipeline failed at step 3")
        return
    
    # Step 4: Generate reports
    if not step_4_generate_reports(accepted, rejected):
        print("\n[ERROR] Pipeline failed at step 4")
        return
    
    # Step 5: Create talent pool
    talent_pool = step_5_create_talent_pool(rejected)
    
    # Calculate total time
    total_time = time.time() - start_total
    
    # Print summary
    print_summary(candidates, accepted, rejected, talent_pool, total_time)
    
    print("\n[SUCCESS] Pipeline completed successfully!\n")


if __name__ == "__main__":
    main()

