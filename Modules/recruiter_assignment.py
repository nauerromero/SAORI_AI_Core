"""
Recruiter Assignment Module for TRS Engine Core
Automatically assigns recruiters to candidates based on specialty, region, and workload

Features:
- Match candidates to recruiters by specialty (tech, admin, marketing, etc.)
- Match candidates to recruiters by geographic region (LATAM, US, EU, Remote)
- Balance workload across recruiters (assigns to recruiter with lowest active_profiles)
- Fallback to "Unassigned" if no matching recruiter found
- Batch processing for multiple candidates
"""

from typing import List, Dict


def assign_recruiter(candidate: Dict, recruiters: List[Dict]) -> Dict:
    """
    Asigna un reclutador al perfil según especialidad, región y carga de trabajo
    
    Priority:
    1. Perfect match: specialty + region
    2. Specialty match only
    3. Region match only (with Remote)
    4. Lowest workload as tiebreaker
    
    Args:
        candidate: Diccionario con datos del candidato
        recruiters: Lista de reclutadores disponibles
    
    Returns:
        Diccionario con datos del reclutador asignado o 'Unassigned'
    """
    vacancy_area = candidate.get("vacancy_area", "").lower()
    location_region = candidate.get("location_region", "").lower()
    
    # Priority 1: Perfect match (specialty + region)
    perfect_match = [
        r for r in recruiters 
        if vacancy_area in [s.lower() for s in r.get("specialties", [])]
        and location_region in [reg.lower() for reg in r.get("regions", [])]
    ]
    
    if perfect_match:
        # Sort by workload and return the one with lowest load
        perfect_match.sort(key=lambda r: r.get("active_profiles", 0))
        return perfect_match[0]
    
    # Priority 2: Specialty match only
    specialty_match = [
        r for r in recruiters 
        if vacancy_area in [s.lower() for s in r.get("specialties", [])]
    ]
    
    if specialty_match:
        specialty_match.sort(key=lambda r: r.get("active_profiles", 0))
        return specialty_match[0]
    
    # Priority 3: Region match with "Remote" capability
    region_match = [
        r for r in recruiters 
        if location_region in [reg.lower() for reg in r.get("regions", [])]
        or "remote" in [reg.lower() for reg in r.get("regions", [])]
    ]
    
    if region_match:
        region_match.sort(key=lambda r: r.get("active_profiles", 0))
        return region_match[0]
    
    # Fallback: Sin match
    return {
        "id": "R000",
        "name": "Unassigned",
        "email": "unassigned@empresa.com",
        "location": "Remote",
        "specialties": [],
        "regions": [],
        "active_profiles": 0,
        "reason": "No matching recruiter found"
    }


def assign_batch(candidates: List[Dict], recruiters: List[Dict]) -> List[Dict]:
    """
    Asigna reclutadores a un lote de candidatos
    
    Args:
        candidates: Lista de perfiles
        recruiters: Lista de reclutadores
    
    Returns:
        Lista de candidatos con campo 'assigned_recruiter'
    """
    assigned = []
    
    # Create a mutable copy of recruiters to track workload changes
    recruiters_copy = [dict(r) for r in recruiters]
    
    for candidate in candidates:
        recruiter = assign_recruiter(candidate, recruiters_copy)
        candidate["assigned_recruiter"] = recruiter
        assigned.append(candidate)
        
        # Update active_profiles count for workload balancing
        if recruiter.get("id") != "R000":
            for r in recruiters_copy:
                if r["id"] == recruiter["id"]:
                    r["active_profiles"] = r.get("active_profiles", 0) + 1
                    break
    
    return assigned


def infer_vacancy_area(vacancy_title: str) -> str:
    """
    Infer the area/specialty from vacancy title
    
    Args:
        vacancy_title: Title of the vacancy
    
    Returns:
        Inferred area (tech, admin, marketing, etc.)
    """
    vacancy_lower = vacancy_title.lower()
    
    # Mapping of keywords to areas
    area_keywords = {
        "tech": ["developer", "engineer", "backend", "frontend", "data", "cloud", "devops", "software"],
        "admin": ["administrative", "assistant", "support", "coordinator", "operations"],
        "marketing": ["marketing", "content", "social media", "seo", "growth"],
        "design": ["designer", "ux", "ui", "graphic", "product design"],
        "finance": ["accountant", "finance", "controller", "analyst"]
    }
    
    for area, keywords in area_keywords.items():
        if any(keyword in vacancy_lower for keyword in keywords):
            return area
    
    return "tech"  # Default to tech


def infer_location_region(location: str) -> str:
    """
    Infer the region from location string
    
    Args:
        location: Location string (e.g., "Santo Domingo, Dominican Republic")
    
    Returns:
        Region code (LATAM, US, EU, etc.)
    """
    location_lower = location.lower()
    
    # LATAM countries
    latam_keywords = ["colombia", "dominican", "argentina", "peru", "mexico", "chile", 
                     "brazil", "venezuela", "ecuador", "uruguay", "paraguay", "bolivia"]
    if any(keyword in location_lower for keyword in latam_keywords):
        return "LATAM"
    
    # US/North America
    us_keywords = ["usa", "united states", "canada", "new york", "california"]
    if any(keyword in location_lower for keyword in us_keywords):
        return "US"
    
    # Europe
    eu_keywords = ["spain", "madrid", "london", "uk", "france", "germany", "italy", "portugal"]
    if any(keyword in location_lower for keyword in eu_keywords):
        return "EU"
    
    return "Remote"  # Default to Remote


if __name__ == "__main__":
    """Demo usage"""
    print("=" * 60)
    print("RECRUITER ASSIGNMENT MODULE - DEMO")
    print("=" * 60)
    
    # Sample recruiters
    sample_recruiters = [
        {
            "id": "R001",
            "name": "Carla Méndez",
            "specialties": ["tech", "data", "backend"],
            "regions": ["LATAM", "US", "Remote"],
            "active_profiles": 2,
            "location": "Bogota, Colombia"
        },
        {
            "id": "R002",
            "name": "Javier Torres",
            "specialties": ["marketing", "design"],
            "regions": ["EU", "LATAM", "Remote"],
            "active_profiles": 1,
            "location": "Madrid, Spain"
        }
    ]
    
    # Sample candidates
    sample_candidates = [
        {"name": "Ana", "vacancy_area": "tech", "location_region": "LATAM"},
        {"name": "Carlos", "vacancy_area": "design", "location_region": "EU"},
        {"name": "Sofia", "vacancy_area": "tech", "location_region": "LATAM"}
    ]
    
    # Assign recruiters
    assigned = assign_batch(sample_candidates, sample_recruiters)
    
    print("\nAssignment Results:")
    for candidate in assigned:
        recruiter = candidate["assigned_recruiter"]
        print(f"  - {candidate['name']} -> {recruiter['name']} (ID: {recruiter['id']})")
    
    print("\n[Demo completed successfully]")

