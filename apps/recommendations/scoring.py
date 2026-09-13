"""
recommendations/scoring.py — Hybrid provider scoring algorithm.

Scoring formula:
  Service Match  × 40%
  Location Match × 20%
  Skills Match   × 15%
  Rating         × 10%
  Experience     × 10%
  Availability   × 5%
"""
from django.db.models import Q


def normalize_rating(rating: float, max_rating: float = 5.0) -> float:
    """Convert rating to 0-1 scale."""
    return float(rating) / max_rating


def normalize_experience(years: int, max_years: int = 20) -> float:
    """Convert years of experience to 0-1 scale (capped at max_years)."""
    return min(years, max_years) / max_years


def check_location_match(provider, location: str) -> float:
    """
    Check if provider serves the customer's location.
    Returns 1.0 for exact match, 0.5 for city-level match, 0.0 for no match.
    """
    if not location:
        return 0.5  # Neutral if no location given

    location_lower = location.lower()

    # Check service areas
    for area in provider.service_areas.all():
        if location_lower in area.area_name.lower() or area.area_name.lower() in location_lower:
            return 1.0
        if location_lower in area.city.lower() or area.city.lower() in location_lower:
            return 0.7

    # Check base location
    if provider.base_location:
        base_lower = provider.base_location.lower()
        if location_lower in base_lower or base_lower in location_lower:
            return 0.8

    return 0.0


def check_category_match(provider, category_name: str) -> float:
    """Check if provider's category matches the required service."""
    if not category_name or not provider.category:
        return 0.5

    cat_lower = category_name.lower()
    provider_cat_lower = provider.category.name.lower()

    if cat_lower == provider_cat_lower:
        return 1.0
    if cat_lower in provider_cat_lower or provider_cat_lower in cat_lower:
        return 0.8
    # Check keywords
    if hasattr(provider.category, 'get_keywords_list'):
        if any(cat_lower in kw.lower() for kw in provider.category.get_keywords_list()):
            return 0.6
    return 0.0


def check_skills_match(provider, category_name: str) -> float:
    """Check how many of the provider's skills are relevant to the problem category."""
    if not category_name:
        return 0.5

    skill_names = [s.lower() for s in provider.get_skills_list()]
    if not skill_names:
        return 0.3  # No skills listed — penalise slightly

    cat_lower = category_name.lower()
    # Count skills that mention the category or common terms
    relevant_skills = sum(1 for skill in skill_names if cat_lower in skill or skill in cat_lower)
    # At least having skills is better than nothing
    base_score = 0.5 if skill_names else 0.0
    bonus = min(relevant_skills * 0.1, 0.5)
    return min(base_score + bonus, 1.0)


def check_availability(provider) -> float:
    """Check if the provider is currently marked as available."""
    return 1.0 if provider.is_available else 0.0


def score_provider(provider, category_name: str, location: str) -> float:
    """
    Calculate a composite recommendation score for a provider.
    
    Returns a float between 0.0 and 1.0.
    Higher = better match.
    """
    # Individual scores
    category_score = check_category_match(provider, category_name)
    location_score = check_location_match(provider, location)
    skills_score = check_skills_match(provider, category_name)
    rating_score = normalize_rating(provider.average_rating)
    experience_score = normalize_experience(provider.experience_years)
    availability_score = check_availability(provider)

    # Weighted formula
    composite = (
        category_score * 0.40 +
        location_score * 0.20 +
        skills_score   * 0.15 +
        rating_score   * 0.10 +
        experience_score * 0.10 +
        availability_score * 0.05
    )

    return round(composite, 4)
