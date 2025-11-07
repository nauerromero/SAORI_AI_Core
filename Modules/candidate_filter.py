"""
Candidate Filter Module for TRS Engine Core
Filters and prioritizes candidates based on multiple criteria

Features:
- Filter by timezone compatibility
- Filter by emotional state
- Filter by inconsistency count
- Prioritize candidates using weighted scoring
- Generate final recommended batches
"""

from typing import List, Dict


def filter_by_timezone_compatibility(candidates: List[Dict], threshold: float = 70.0) -> List[Dict]:
    """
    Filter candidates with timezone compatibility above threshold
    
    Args:
        candidates: List of candidate dictionaries
        threshold: Minimum compatibility score (default: 70.0)
    
    Returns:
        List of candidates meeting the threshold
    """
    return [c for c in candidates if c.get("avg_score", 0) >= threshold]


def filter_by_emotional_state(candidates: List[Dict], desired_state: str = "Positive") -> List[Dict]:
    """
    Filter candidates by emotional state
    
    Args:
        candidates: List of candidate dictionaries
        desired_state: Target emotional state (default: "Positive")
    
    Returns:
        List of candidates with matching emotional state
    """
    return [c for c in candidates if c.get("emotional_state", "").lower() == desired_state.lower()]


def filter_by_issue_count(candidates: List[Dict], max_issues: int = 3) -> List[Dict]:
    """
    Filter candidates with fewer than specified number of inconsistencies
    
    Args:
        candidates: List of candidate dictionaries
        max_issues: Maximum allowed inconsistencies (default: 3)
    
    Returns:
        List of candidates with issues below threshold
    """
    return [c for c in candidates if c.get("issue_count", 0) <= max_issues]


def filter_by_match_score(candidates: List[Dict], min_score: float = 0.5) -> List[Dict]:
    """
    Filter candidates by minimum match score
    
    Args:
        candidates: List of candidate dictionaries
        min_score: Minimum match score (default: 0.5)
    
    Returns:
        List of candidates meeting minimum score
    """
    return [c for c in candidates if c.get("match_score", 0) >= min_score]


def prioritize_candidates(candidates: List[Dict]) -> List[Dict]:
    """
    Sort candidates by timezone compatibility, emotional state, and penalize for inconsistencies
    
    Scoring formula:
    - Base: Timezone compatibility score (0-100)
    - Bonus: +10 for positive emotional state
    - Penalty: -5 per inconsistency
    
    Args:
        candidates: List of candidate dictionaries
    
    Returns:
        List of candidates sorted by priority (highest first)
    """
    def score(c):
        # Base timezone compatibility score
        tz_score = c.get("avg_score", 0)
        
        # Bonus for positive emotional state
        emotion_bonus = 10 if c.get("emotional_state", "").lower() == "positive" else 0
        
        # Penalty for inconsistencies
        penalty = c.get("issue_count", 0) * 5
        
        return tz_score + emotion_bonus - penalty
    
    return sorted(candidates, key=score, reverse=True)


def generate_final_batch(candidates: List[Dict], 
                         tz_threshold: float = 70.0,
                         desired_state: str = "Positive",
                         max_issues: int = 3) -> List[Dict]:
    """
    Apply all filters and return prioritized batch of top candidates
    
    Process:
    1. Filter by timezone compatibility
    2. Filter by emotional state
    3. Filter by issue count
    4. Prioritize remaining candidates
    
    Args:
        candidates: List of candidate dictionaries
        tz_threshold: Minimum timezone compatibility (default: 70.0)
        desired_state: Desired emotional state (default: "Positive")
        max_issues: Maximum allowed issues (default: 3)
    
    Returns:
        Filtered and prioritized list of candidates
    """
    # Apply filters sequentially
    filtered = filter_by_timezone_compatibility(candidates, tz_threshold)
    filtered = filter_by_emotional_state(filtered, desired_state)
    filtered = filter_by_issue_count(filtered, max_issues)
    
    # Prioritize remaining candidates
    return prioritize_candidates(filtered)


def get_top_candidates(candidates: List[Dict], top_n: int = 5) -> List[Dict]:
    """
    Get top N candidates after filtering and prioritization
    
    Args:
        candidates: List of candidate dictionaries
        top_n: Number of top candidates to return (default: 5)
    
    Returns:
        Top N candidates
    """
    filtered = generate_final_batch(candidates)
    return filtered[:top_n]


def generate_filter_report(original: List[Dict], filtered: List[Dict]) -> str:
    """
    Generate a report showing filtering results
    
    Args:
        original: Original list of candidates
        filtered: Filtered list of candidates
    
    Returns:
        Formatted report as string
    """
    total = len(original)
    remaining = len(filtered)
    filtered_out = total - remaining
    
    report = f"""
# Candidate Filtering Report

## Summary
- **Original Candidates:** {total}
- **Candidates After Filtering:** {remaining}
- **Filtered Out:** {filtered_out} ({filtered_out/total*100:.1f}%)

## Top 5 Recommended Candidates
"""
    
    for i, candidate in enumerate(filtered[:5], 1):
        report += f"\n{i}. **{candidate.get('name', 'Unknown')}**"
        report += f"\n   - Vacancy: {candidate.get('vacancy', 'N/A')}"
        report += f"\n   - Timezone Score: {candidate.get('avg_score', 0):.1f}%"
        report += f"\n   - Emotional State: {candidate.get('emotional_state', 'Unknown')}"
        report += f"\n   - Issues: {candidate.get('issue_count', 0)}"
        report += f"\n   - Match Score: {candidate.get('match_score', 0)}"
        report += "\n"
    
    return report


def categorize_rejected_candidates(rejected: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Categorize rejected candidates by rejection reason for future opportunities
    
    Categories:
    - Low timezone compatibility
    - Negative emotional state
    - Too many inconsistencies
    - Low match score
    - Potential (close to threshold)
    
    Args:
        rejected: List of rejected candidate dictionaries
    
    Returns:
        Dictionary with categorized candidates
    """
    categories = {
        "low_timezone": [],
        "negative_emotion": [],
        "too_many_issues": [],
        "low_match_score": [],
        "potential": []  # Close to passing, worth revisiting
    }
    
    for candidate in rejected:
        tz_score = candidate.get("avg_score", 0)
        emotional_state = candidate.get("emotional_state", "").lower()
        issue_count = candidate.get("issue_count", 0)
        match_score = candidate.get("match_score", 0)
        
        # Check if candidate is "potential" (close to thresholds)
        is_potential = (
            tz_score >= 60 and tz_score < 70 and  # Close to timezone threshold
            emotional_state != "negative" and
            issue_count <= 4
        )
        
        if is_potential:
            categories["potential"].append(candidate)
        elif tz_score < 70:
            categories["low_timezone"].append(candidate)
        elif emotional_state == "negative":
            categories["negative_emotion"].append(candidate)
        elif issue_count > 3:
            categories["too_many_issues"].append(candidate)
        elif match_score < 0.5:
            categories["low_match_score"].append(candidate)
    
    return categories


def generate_feedback_for_rejected(candidate: Dict) -> str:
    """
    Generate personalized feedback for rejected candidates
    
    Args:
        candidate: Candidate dictionary
    
    Returns:
        Personalized feedback message
    """
    name = candidate.get("name", "Candidate")
    tz_score = candidate.get("avg_score", 0)
    emotional_state = candidate.get("emotional_state", "Unknown")
    issue_count = candidate.get("issue_count", 0)
    match_score = candidate.get("match_score", 0)
    
    feedback = f"Dear {name},\n\n"
    feedback += "Thank you for your interest in our position. "
    feedback += "While we've decided to move forward with other candidates at this time, "
    feedback += "we'd like to provide you with some feedback:\n\n"
    
    # Timezone feedback
    if tz_score < 70:
        feedback += f"- **Timezone Compatibility ({tz_score:.1f}%):** "
        if tz_score < 40:
            feedback += "Your location presents significant timezone challenges for real-time collaboration. "
            feedback += "Consider roles with fully async communication or regional teams.\n"
        else:
            feedback += "Your timezone has moderate overlap with our teams. "
            feedback += "You might be a better fit for positions with flexible hours.\n"
    
    # Emotional state feedback
    if emotional_state.lower() == "negative":
        feedback += "- **Interview Performance:** We noticed some hesitation during the interview. "
        feedback += "We encourage you to prepare thoroughly and showcase your enthusiasm in future opportunities.\n"
    
    # Technical issues feedback
    if issue_count > 3:
        feedback += f"- **Technical Responses ({issue_count} inconsistencies detected):** "
        feedback += "We recommend strengthening your technical knowledge in specific areas:\n"
        feedback += "  - Review core concepts and best practices\n"
        feedback += "  - Practice articulating technical solutions clearly\n"
        feedback += "  - Build more hands-on project experience\n"
    
    # Match score feedback
    if match_score < 0.5:
        feedback += f"- **Skill Match ({match_score:.1%}):** "
        feedback += "Your current skill set may be better suited for different role types. "
        feedback += "Consider exploring positions that align more closely with your experience.\n"
    
    feedback += "\n**Next Steps:**\n"
    
    # Provide actionable recommendations
    if tz_score >= 60 and tz_score < 70:
        feedback += "- You're close to our timezone requirements. Consider relocating or roles with flexible schedules.\n"
    
    if issue_count <= 4 and emotional_state.lower() != "negative":
        feedback += "- We'll keep your profile in our talent pool for future opportunities.\n"
        feedback += "- We may reach out in 3-6 months as new positions open.\n"
    
    feedback += "\nWe wish you the best in your job search!\n\nBest regards,\nHR Team"
    
    return feedback


def suggest_alternative_vacancies(candidate: Dict, all_vacancies: List[str]) -> List[str]:
    """
    Suggest alternative vacancies that might be a better fit
    
    Args:
        candidate: Candidate dictionary
        all_vacancies: List of available vacancy names
    
    Returns:
        List of recommended alternative vacancies
    """
    suggestions = []
    tz_score = candidate.get("avg_score", 0)
    current_vacancy = candidate.get("vacancy", "")
    issue_count = candidate.get("issue_count", 0)
    
    # If timezone is the main issue, suggest remote-friendly roles
    if tz_score < 60 and issue_count <= 3:
        remote_keywords = ["remote", "async", "administrative", "content", "writer"]
        for vacancy in all_vacancies:
            if any(keyword in vacancy.lower() for keyword in remote_keywords):
                if vacancy != current_vacancy:
                    suggestions.append(vacancy)
    
    # If technical issues, suggest junior or entry-level roles
    if issue_count > 3:
        junior_keywords = ["junior", "entry", "assistant", "trainee"]
        for vacancy in all_vacancies:
            if any(keyword in vacancy.lower() for keyword in junior_keywords):
                if vacancy != current_vacancy:
                    suggestions.append(vacancy)
    
    return suggestions[:3]  # Return top 3 suggestions


def create_talent_pool_entry(candidate: Dict, reason: str) -> Dict:
    """
    Create a talent pool entry for future consideration
    
    Args:
        candidate: Candidate dictionary
        reason: Reason for initial rejection
    
    Returns:
        Talent pool entry with metadata
    """
    from datetime import datetime, timedelta
    
    # Calculate review date (3-6 months from now)
    months_to_wait = 3 if candidate.get("avg_score", 0) >= 60 else 6
    review_date = datetime.now() + timedelta(days=30 * months_to_wait)
    
    return {
        "candidate_id": f"{candidate.get('name', 'Unknown')}_{candidate.get('vacancy', 'N/A')}",
        "name": candidate.get("name", "Unknown"),
        "original_vacancy": candidate.get("vacancy", "N/A"),
        "rejection_reason": reason,
        "timezone_score": candidate.get("avg_score", 0),
        "emotional_state": candidate.get("emotional_state", "Unknown"),
        "issue_count": candidate.get("issue_count", 0),
        "match_score": candidate.get("match_score", 0),
        "date_added": datetime.now().strftime("%Y-%m-%d"),
        "review_date": review_date.strftime("%Y-%m-%d"),
        "status": "talent_pool",
        "notes": ""
    }


def export_rejected_candidates_report(rejected: List[Dict], filename: str = "Logs/reports/rejected_candidates.md") -> None:
    """
    Generate comprehensive report for rejected candidates with recommendations
    
    Args:
        rejected: List of rejected candidates
        filename: Output filename (default: Logs/reports/rejected_candidates.md)
    """
    import os
    from datetime import datetime
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Categorize rejected candidates
    categories = categorize_rejected_candidates(rejected)
    
    report = f"# Rejected Candidates Report\n\n"
    report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += f"**Total Rejected:** {len(rejected)}\n\n"
    report += "---\n\n"
    
    # Summary by category
    report += "## 📊 Rejection Categories\n\n"
    report += f"- **Low Timezone Compatibility:** {len(categories['low_timezone'])} candidates\n"
    report += f"- **Negative Emotional State:** {len(categories['negative_emotion'])} candidates\n"
    report += f"- **Too Many Issues:** {len(categories['too_many_issues'])} candidates\n"
    report += f"- **Low Match Score:** {len(categories['low_match_score'])} candidates\n"
    report += f"- **Potential (Revisit Later):** {len(categories['potential'])} candidates ⭐\n\n"
    report += "---\n\n"
    
    # Potential candidates (priority for talent pool)
    if categories['potential']:
        report += "## ⭐ POTENTIAL Candidates (Priority for Talent Pool)\n\n"
        report += "*These candidates were close to passing and should be revisited in 3-6 months*\n\n"
        
        for candidate in categories['potential']:
            report += f"### {candidate['name']} - {candidate['vacancy']}\n"
            report += f"- **Timezone Score:** {candidate.get('avg_score', 0):.1f}% (threshold: 70%)\n"
            report += f"- **Emotional State:** {candidate.get('emotional_state', 'Unknown')}\n"
            report += f"- **Issues:** {candidate.get('issue_count', 0)}\n"
            report += f"- **Match Score:** {candidate.get('match_score', 0):.2f}\n"
            report += f"- **Recommendation:** Add to talent pool, revisit in 3 months\n\n"
    
    # Detailed breakdown by category
    for category_name, category_list in categories.items():
        if category_name != 'potential' and category_list:
            report += f"## {category_name.replace('_', ' ').title()}\n\n"
            for candidate in category_list[:10]:  # Limit to 10 per category
                report += f"- **{candidate['name']}** ({candidate['vacancy']})\n"
                report += f"  - TZ: {candidate.get('avg_score', 0):.1f}%, "
                report += f"Issues: {candidate.get('issue_count', 0)}, "
                report += f"State: {candidate.get('emotional_state', 'Unknown')}\n"
            report += "\n"
    
    # Write report
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"[SUCCESS] Rejected candidates report exported to: {filename}")


if __name__ == "__main__":
    """Demo usage"""
    print("=" * 60)
    print("CANDIDATE FILTER MODULE - DEMO")
    print("=" * 60)
    
    # Sample candidate data
    sample_candidates = [
        {
            "name": "Jorge",
            "vacancy": "Backend Developer",
            "avg_score": 85.0,
            "emotional_state": "Positive",
            "issue_count": 0,
            "match_score": 0.8
        },
        {
            "name": "Ana",
            "vacancy": "Data Engineer",
            "avg_score": 65.0,
            "emotional_state": "Neutral",
            "issue_count": 2,
            "match_score": 0.6
        },
        {
            "name": "Carlos",
            "vacancy": "Backend Developer",
            "avg_score": 75.0,
            "emotional_state": "Positive",
            "issue_count": 1,
            "match_score": 0.7
        },
        {
            "name": "Sofia",
            "vacancy": "Admin Assistant",
            "avg_score": 50.0,
            "emotional_state": "Negative",
            "issue_count": 5,
            "match_score": 0.3
        }
    ]
    
    print(f"\nOriginal candidates: {len(sample_candidates)}")
    
    # Apply filters
    filtered = generate_final_batch(sample_candidates)
    rejected = [c for c in sample_candidates if c not in filtered]
    
    print(f"After filtering: {len(filtered)} accepted, {len(rejected)} rejected")
    
    print("\n=== ACCEPTED CANDIDATES ===")
    for i, candidate in enumerate(filtered, 1):
        print(f"{i}. {candidate['name']} - {candidate['vacancy']} (TZ: {candidate['avg_score']:.1f}%)")
    
    # Handle rejected candidates
    if rejected:
        print("\n=== REJECTED CANDIDATES ===")
        print(f"Total rejected: {len(rejected)}\n")
        
        # Categorize rejected
        categories = categorize_rejected_candidates(rejected)
        print(f"Potential (revisit later): {len(categories['potential'])}")
        print(f"Low timezone: {len(categories['low_timezone'])}")
        print(f"Negative emotion: {len(categories['negative_emotion'])}")
        print(f"Too many issues: {len(categories['too_many_issues'])}")
        
        # Generate feedback for first rejected candidate
        if rejected:
            print(f"\n=== SAMPLE FEEDBACK FOR {rejected[0]['name']} ===")
            feedback = generate_feedback_for_rejected(rejected[0])
            print(feedback)
        
        # Create talent pool entries for potential candidates
        if categories['potential']:
            print("\n=== TALENT POOL ENTRIES ===")
            for candidate in categories['potential']:
                entry = create_talent_pool_entry(candidate, "Close to threshold")
                print(f"- {entry['name']}: Review on {entry['review_date']}")
    
    print("\n[Demo completed successfully]")

