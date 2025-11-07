"""
Report Generator Module for TRS Engine Core
Centralizes all report generation logic (Markdown, CSV, PDF)

Features:
- Generate executive summaries with key metrics
- Create navigable table of contents
- Format individual candidate sections
- Export to Markdown and CSV formats
- Timezone compatibility integration
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple
import os


def generate_executive_summary(entries: List[Dict], all_results: List[Dict] = None) -> str:
    """Generate executive summary section with key metrics"""
    total = len(entries)
    
    # Calculate metrics
    with_tz = sum(1 for e in entries if e.get('timezone_data'))
    avg_tz = 0
    if with_tz > 0:
        avg_tz = sum(e['timezone_data']['avg_score'] 
                     for e in entries if e.get('timezone_data')) / with_tz
    
    # Count by emotional state
    emotional_counts = {}
    for entry in entries:
        state = entry.get('emotional_state', 'Unknown')
        emotional_counts[state] = emotional_counts.get(state, 0) + 1
    
    # Calculate average scores
    avg_match = sum(e.get('match_score', 0) for e in entries) / total if total > 0 else 0
    avg_adjusted = sum(e.get('adjusted_score', 0) for e in entries) / total if total > 0 else 0
    
    # Calculate consent metrics (if available)
    consent_given = 0
    consent_declined = 0
    if all_results:
        consent_given = sum(1 for r in all_results if r.get('consent_given'))
        consent_declined = sum(1 for r in all_results if r.get('consent_given') == False)
    
    summary = f"""# RRHH Technical Sheet - {datetime.now().strftime('%Y-%m-%d')}

## 📊 Executive Summary
- **Total Candidates Evaluated:** {total}
- **Average Match Score:** {avg_match:.2f}
- **Average Adjusted Score:** {avg_adjusted:.2f}
- **Candidates with Timezone Data:** {with_tz}/{total}
- **Average Timezone Compatibility:** {avg_tz:.1f}%

### 🤝 Candidate Consent Status
"""
    if all_results:
        consent_rate = (consent_given / total * 100) if total > 0 else 0
        summary += f"- **Consented to Continue:** {consent_given} candidates ({consent_rate:.1f}%)\n"
        summary += f"- **Declined to Continue:** {consent_declined} candidates ({100-consent_rate:.1f}%)\n"
    else:
        summary += "- **No consent data available**\n"
    
    summary += "\n### 😊 Emotional State Distribution\n"
    for state, count in sorted(emotional_counts.items()):
        summary += f"- **{state}:** {count} candidates ({count/total*100:.1f}%)\n"
    
    summary += f"\n**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    summary += "---\n\n"
    
    return summary


def generate_table_of_contents(entries: List[Dict]) -> str:
    """Generate navigable table of contents"""
    toc = "## 📑 Table of Contents\n\n"
    
    # Group by candidate name
    candidates_seen = set()
    index = 1
    
    for entry in entries:
        name = entry.get('name', 'Unknown')
        vacancy = entry.get('vacancy', 'N/A')
        
        # Create unique entry for each candidate-vacancy combo
        anchor = f"{name.lower().replace(' ', '-')}-{index}"
        toc += f"{index}. [{name} - {vacancy}](#candidate-{anchor})\n"
        index += 1
    
    toc += "\n---\n\n"
    return toc


def generate_timezone_markdown(timezone_data: Dict) -> str:
    """Generate timezone compatibility section"""
    if not timezone_data:
        return ""
    
    md = f"""
#### 🌍 Timezone Compatibility
- **Candidate Location:** {timezone_data.get('candidate_location', 'N/A')}
- **Candidate Timezone:** {timezone_data.get('candidate_tz', 'N/A')}
- **Assigned Recruiter:** {timezone_data.get('recruiter_name', 'N/A')} ({timezone_data.get('recruiter_location', 'N/A')})
- **Average Compatibility Score:** {timezone_data.get('avg_score', 0)}/100
- **{timezone_data.get('meeting_suggestion', 'No suggestion available')}**
"""
    
    if 'local_times' in timezone_data and timezone_data['local_times']:
        md += "  - **Local times:**\n"
        for lt in timezone_data['local_times']:
            md += f"    - {lt}\n"
    
    return md


def generate_candidate_section(entry: Dict, responses: List[Tuple], inconsistencies: List, 
                               connection_flag: str, english_level: str,
                               upgrade=None, justification=None, index=1,
                               closing_message=None, consent_given=None) -> str:
    """Generate individual candidate section with full details"""
    name = entry.get('name', 'Unknown')
    anchor = f"{name.lower().replace(' ', '-')}-{index}"
    
    # Determine status emoji
    score = entry.get('match_score', 0)
    if score >= 0.7:
        status = "🟢 High Match"
    elif score >= 0.4:
        status = "🟡 Medium Match"
    else:
        status = "🔴 Low Match"
    
    md = f"""
### Candidate: {name} {{#{anchor}}}

#### 📋 Basic Information
- **Vacancy:** {entry.get('vacancy', 'N/A')}
- **Technical Level:** {entry.get('technical_level', 'mid').title()}
- **Match Status:** {status}
- **Match Score:** {entry.get('match_score', 0)}
- **Adjusted Score:** {entry.get('adjusted_score', 0)}
- **Emotional State:** {entry.get('emotional_state', 'Unknown')}
- **English Level:** {english_level} (estimated from audio)
- **Connection Status:** {connection_flag}
"""

    # Add timezone if available
    if 'timezone_data' in entry and entry['timezone_data']:
        md += generate_timezone_markdown(entry['timezone_data'])
    
    # Add upgrade suggestion
    if upgrade:
        md += f"\n#### ⭐ Suggested Upgrade\n"
        md += f"- **Upgrade to:** {upgrade}\n"
        if justification:
            md += f"- **Justification:**\n"
            for just in justification:
                md += f"  - {just}\n"
    
    # Add technical questions
    md += "\n#### 💬 Technical Interview\n"
    if responses:
        for i, (q, r, quality, latency) in enumerate(responses, 1):
            confidence_emoji = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}.get(quality.get('confidence', 'Medium'), "⚪")
            md += f"\n**Q{i}:** {q}\n"
            md += f"- **Response:** {r}\n"
            md += f"- **Confidence:** {confidence_emoji} {quality.get('confidence', 'Unknown')}\n"
            md += f"- **Response Time:** {latency:.1f}s\n"
            if quality.get('possible_web_lookup'):
                md += f"- ⚠️ **WARNING:** Possible web lookup detected (long latency + generic phrasing)\n"
    else:
        md += "\n*No technical questions available for this vacancy/level*\n"
    
    # Add inconsistencies
    if inconsistencies:
        md += f"\n#### ⚠️ Inconsistencies Detected ({len(inconsistencies)})\n"
        for issue in inconsistencies:
            md += f"- {issue}\n"
    else:
        md += "\n#### ✅ No Inconsistencies Detected\n"
    
    # Add emotional closure section
    if closing_message or consent_given is not None:
        md += "\n#### 🤝 Interview Closure\n"
        if closing_message:
            md += f"- **Closing Message:** {closing_message}\n"
        if consent_given is not None:
            consent_status = "✅ YES - Ready to proceed" if consent_given else "❌ NO - Declined to continue"
            md += f"- **Candidate Consent:** {consent_status}\n"
    
    md += "\n" + "=" * 80 + "\n"
    return md


def generate_markdown_report(entries: List[Dict], all_results: List[Dict]) -> str:
    """
    Generate complete markdown report with all sections
    
    Args:
        entries: List of candidate entry dictionaries
        all_results: List of simulation results (responses, inconsistencies, etc.)
    
    Returns:
        Complete markdown report as string
    """
    markdown_parts = []
    
    # 1. Executive Summary
    markdown_parts.append(generate_executive_summary(entries, all_results))
    
    # 2. Table of Contents
    markdown_parts.append(generate_table_of_contents(entries))
    
    # 3. Individual candidates
    for index, (entry, result) in enumerate(zip(entries, all_results), 1):
        candidate_md = generate_candidate_section(
            entry=entry,
            responses=result.get('responses', []),
            inconsistencies=result.get('inconsistencies', []),
            connection_flag=result.get('connection_flag', 'stable'),
            english_level=result.get('english_level', 'N/A'),
            upgrade=result.get('upgrade'),
            justification=result.get('justification'),
            index=index,
            closing_message=result.get('closing_message'),
            consent_given=result.get('consent_given')
        )
        markdown_parts.append(candidate_md)
    
    return "\n".join(markdown_parts)


def export_to_markdown_file(markdown: str, filename="Logs/reports/rrhh_registry.md"):
    """
    Export markdown to file
    
    Args:
        markdown: Markdown content as string
        filename: Target file path (default: Logs/reports/rrhh_registry.md)
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(markdown)
    print(f"[SUCCESS] Markdown export completed: {filename}")


def export_to_csv_file(entries: List[Dict], all_results: List[Dict], 
                       filename="Logs/reports/rrhh_registry.csv"):
    """
    Export data to CSV file with key metrics
    
    Args:
        entries: List of candidate entry dictionaries
        all_results: List of simulation results
        filename: Target file path (default: Logs/reports/rrhh_registry.csv)
    """
    rows = []
    
    for entry, result in zip(entries, all_results):
        # Extract timezone data
        timezone_data = entry.get("timezone_data", {})
        
        # Calculate average confidence
        confidences = {"Low": 1, "Medium": 2, "High": 3}
        responses = result.get('responses', [])
        if responses:
            scores = [confidences.get(r[2].get('confidence', 'Medium'), 2) for r in responses]
            avg_conf = round(sum(scores) / len(scores), 2) if scores else 0
        else:
            avg_conf = 0
        
        rows.append({
            "Nombre": entry.get("name", "Unknown"),
            "Vacante": entry.get("vacancy", "N/A"),
            "Nivel técnico": entry.get("technical_level", "N/A"),
            "Match Score": entry.get("match_score", 0),
            "Adjusted Score": entry.get("adjusted_score", 0),
            "Estado emocional": entry.get("emotional_state", "Unknown"),
            "Confianza promedio": avg_conf,
            "Inconsistencias detectadas": len(result.get("inconsistencies", [])),
            "Upgrade sugerido": result.get("upgrade", "—"),
            "Justificación": ", ".join(result.get("justification", [])) or "—",
            "Ubicación": timezone_data.get("candidate_location", "N/A"),
            "Timezone": timezone_data.get("candidate_tz", "N/A"),
            "Compatibilidad TZ": timezone_data.get("avg_score", "N/A"),
            "Mensaje de cierre": result.get("closing_message", "—"),
            "Consentimiento": "Sí" if result.get("consent_given") else "No",
            "Estado emocional final": result.get("emotional_state_final", entry.get("emotional_state", "Unknown"))
        })
    
    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"[SUCCESS] CSV export completed: {filename}")


if __name__ == "__main__":
    """Demo usage"""
    print("=" * 60)
    print("REPORT GENERATOR MODULE - DEMO")
    print("=" * 60)
    
    # Sample data
    sample_entries = [
        {
            "name": "Jorge",
            "vacancy": "Backend Developer",
            "technical_level": "junior",
            "match_score": 0.8,
            "adjusted_score": 0.75,
            "emotional_state": "positive",
            "timezone_data": {
                "candidate_location": "Santo Domingo, DR",
                "candidate_tz": "America/Santo_Domingo",
                "avg_score": 48.2,
                "meeting_suggestion": "Suggested: 09:00 AM UTC",
                "local_times": ["Santo Domingo: 05:00 AM", "New York: 04:00 AM"]
            }
        }
    ]
    
    sample_results = [
        {
            "responses": [("What is Node.js?", "It's a runtime", {"confidence": "High"}, 10.5)],
            "inconsistencies": [],
            "connection_flag": "stable",
            "english_level": "B2",
            "upgrade": "Mid-level Developer",
            "justification": ["Strong responses", "High confidence"]
        }
    ]
    
    # Generate report
    markdown = generate_markdown_report(sample_entries, sample_results)
    print("\nGenerated Markdown Preview (first 500 chars):")
    print(markdown[:500])
    print("\n[Demo completed successfully]")

