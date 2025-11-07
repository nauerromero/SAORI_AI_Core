# timezone_compatibility.py

"""
Timezone Compatibility Module for TRS Engine Core
Evaluates timezone compatibility between candidates and vacancies

Features:
- Resolve timezone from real location (city/country)
- Calculate time offset and working hour overlap
- Assess compatibility level and generate adaptive messages
- Suggest optimal meeting times across zones
- Export results to CSV
"""

from datetime import datetime, time
from typing import Dict, List, Tuple
from timezonefinderL import TimezoneFinder
from geopy.geocoders import Nominatim
import pytz
import csv

# Standard working hours (9 AM - 6 PM)
STANDARD_WORK_START = time(9, 0)
STANDARD_WORK_END = time(18, 0)


def resolve_timezone_from_location(location_name: str) -> str:
    """Resolve timezone from real-world location name"""
    geolocator = Nominatim(user_agent="trs_timezone_resolver", timeout=10)
    location = geolocator.geocode(location_name)
    if not location:
        return "UTC"
    tf = TimezoneFinder()
    tz = tf.timezone_at(lat=location.latitude, lng=location.longitude)
    return tz or "UTC"


def calculate_time_offset(tz1_name: str, tz2_name: str) -> float:
    """Calculate time offset in hours between two timezones"""
    tz1 = pytz.timezone(tz1_name)
    tz2 = pytz.timezone(tz2_name)
    now = datetime.utcnow()
    offset1 = tz1.utcoffset(now).total_seconds() / 3600
    offset2 = tz2.utcoffset(now).total_seconds() / 3600
    return offset1 - offset2


def calculate_overlap_hours(tz1_name: str, tz2_name: str,
                            work_start: time = STANDARD_WORK_START,
                            work_end: time = STANDARD_WORK_END) -> float:
    """Calculate overlapping working hours between two timezones"""
    tz1 = pytz.timezone(tz1_name)
    tz2 = pytz.timezone(tz2_name)
    today = datetime.utcnow().date()
    start1 = tz1.localize(datetime.combine(today, work_start))
    end1 = tz1.localize(datetime.combine(today, work_end))
    start1_in_tz2 = start1.astimezone(tz2)
    end1_in_tz2 = end1.astimezone(tz2)
    start2 = tz2.localize(datetime.combine(today, work_start))
    end2 = tz2.localize(datetime.combine(today, work_end))
    overlap_start = max(start1_in_tz2, start2)
    overlap_end = min(end1_in_tz2, end2)
    if overlap_start < overlap_end:
        return (overlap_end - overlap_start).total_seconds() / 3600
    return 0.0


def assess_timezone_compatibility(candidate_tz: str, team_tz: str) -> Dict:
    """Assess compatibility between candidate and team timezones"""
    offset = calculate_time_offset(candidate_tz, team_tz)
    overlap = calculate_overlap_hours(candidate_tz, team_tz)
    score = min((overlap / 9.0) * 100, 100)
    if overlap >= 7:
        level = "Excellent"
        recommendation = "Full collaboration possible during regular hours"
    elif overlap >= 5:
        level = "Good"
        recommendation = "Sufficient overlap for daily syncs and collaboration"
    elif overlap >= 3:
        level = "Moderate"
        recommendation = "Limited overlap, may require flexible scheduling"
    elif overlap >= 1:
        level = "Challenging"
        recommendation = "Minimal overlap, requires async work or shift adjustments"
    else:
        level = "Difficult"
        recommendation = "No overlap, fully async work or shift work needed"
    return {
        "candidate_timezone": candidate_tz,
        "team_timezone": team_tz,
        "offset_hours": round(offset, 1),
        "overlap_hours": round(overlap, 1),
        "compatibility_score": round(score, 1),
        "compatibility_level": level,
        "recommendation": recommendation
    }


def generate_adaptive_message(level: str, candidate_tz: str, team_tz: str, offset: float) -> str:
    """Generate adaptive message based on compatibility level"""
    base = f"The job requires availability in {team_tz}. Your current timezone is {candidate_tz} (offset: {offset}h)."
    if level == "Excellent":
        return base + " You're perfectly aligned for collaboration!"
    elif level == "Good":
        return base + " You have strong overlap for daily syncs."
    elif level == "Moderate":
        return base + " Some flexibility may be needed."
    elif level == "Challenging":
        return base + " Async work or shift adjustments recommended."
    else:
        return base + " Full async mode or shift work will be required."


def suggest_meeting_time(zones: List[str]) -> Tuple[str, List[str]]:
    """Suggest optimal meeting time across multiple timezones"""
    if not zones:
        return "No zones provided", []
    best_hour = None
    max_overlap = 0
    for hour in range(24):
        meeting_time = time(hour, 0)
        total_overlap = 0
        for zone in zones:
            tz = pytz.timezone(zone)
            now = datetime.utcnow().date()
            meeting_dt = tz.localize(datetime.combine(now, meeting_time))
            if STANDARD_WORK_START <= meeting_dt.time() <= STANDARD_WORK_END:
                total_overlap += 1
        if total_overlap > max_overlap:
            max_overlap = total_overlap
            best_hour = hour
    if best_hour is None:
        return "No suitable time found", []
    best_time = time(best_hour, 0)
    local_times = []
    for zone in zones:
        tz = pytz.timezone(zone)
        now = datetime.utcnow().date()
        meeting_dt = pytz.utc.localize(datetime.combine(now, best_time))
        local_dt = meeting_dt.astimezone(tz)
        local_times.append(f"{zone}: {local_dt.strftime('%I:%M %p')}")
    recommendation = f"Suggested meeting time: {best_time.strftime('%I:%M %p')} UTC"
    return recommendation, local_times


def export_timezone_result(result: Dict, filename="rrhh_registry.csv"):
    """Export compatibility result to CSV"""
    fields = [
        "candidate_timezone", "team_timezone", "offset_hours", "overlap_hours",
        "compatibility_score", "compatibility_level", "recommendation"
    ]
    with open(filename, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writerow(result)

from datetime import datetime, time
import pytz
from typing import List, Tuple

STANDARD_WORK_START = time(9, 0)
STANDARD_WORK_END = time(18, 0)

def suggest_meeting_time(zones: List[str]) -> Tuple[str, List[str]]:
    """Suggest optimal meeting time across multiple timezones"""
    if not zones:
        return "No zones provided", []

    best_hour = None
    max_overlap = 0

    for hour in range(24):
        meeting_time = time(hour, 0)
        total_overlap = 0

        for zone in zones:
            tz = pytz.timezone(zone)
            now = datetime.utcnow().date()
            meeting_dt = tz.localize(datetime.combine(now, meeting_time))

            if STANDARD_WORK_START <= meeting_dt.time() <= STANDARD_WORK_END:
                total_overlap += 1

        if total_overlap > max_overlap:
            max_overlap = total_overlap
            best_hour = hour

    if best_hour is None:
        return "No suitable time found", []

    best_time = time(best_hour, 0)
    local_times = []

    for zone in zones:
        tz = pytz.timezone(zone)
        now = datetime.utcnow().date()
        meeting_dt = pytz.utc.localize(datetime.combine(now, best_time))
        local_dt = meeting_dt.astimezone(tz)
        local_times.append(f"{zone}: {local_dt.strftime('%I:%M %p')}")

    recommendation = f"Suggested meeting time: {best_time.strftime('%I:%M %p')} UTC"
    return recommendation, local_times

def main():
    """Demo usage"""
    print("=" * 60)
    print("TIMEZONE COMPATIBILITY MODULE - DEMO")
    print("=" * 60)

    candidate_location = "Santo Domingo, Dominican Republic"
    team_location = "New York, USA"

    candidate_tz = resolve_timezone_from_location(candidate_location)
    team_tz = resolve_timezone_from_location(team_location)

    result = assess_timezone_compatibility(candidate_tz, team_tz)
    message = generate_adaptive_message(
        result["compatibility_level"],
        candidate_tz,
        team_tz,
        result["offset_hours"]
    )

    print("\nCompatibility Report:")
    print(result)
    print("\nAdaptive Message:")
    print(message)

    export_timezone_result(result)

    print("\nSuggested Meeting Time:")
    suggestion, local_times = suggest_meeting_time([candidate_tz, team_tz])
    print(suggestion)
    for time_str in local_times:
        print(" -", time_str)


if __name__ == "__main__":
    main()
