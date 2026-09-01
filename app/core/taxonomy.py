from app.models.enums import OpportunityFormat


ALLOWED_SKILLS = {
    "python",
    "sql",
    "javascript",
    "typescript",
    "git",
    "linux",
    "fastapi",
    "rest_api",
    "databases",
    "postgresql",
    "docker",
    "html_css",
    "react",
    "numpy",
    "pandas",
    "matplotlib",
    "scikit_learn",
    "pytorch",
    "machine_learning",
    "data_analysis",
    "data_visualization",
    "algorithms",
    "data_structures",
    "linear_algebra",
    "calculus",
    "probability",
    "statistics",
    "optimization",
    "technical_writing",
    "presentation",
    "teamwork",
    "english",
}


ALLOWED_FIELDS = {
    "machine_learning",
    "deep_learning",
    "data_science",
    "data_analytics",
    "computer_vision",
    "natural_language_processing",
    "generative_ai",
    "recommendation_systems",
    "backend_development",
    "frontend_development",
    "fullstack_development",
    "mobile_development",
    "devops",
    "cloud_computing",
    "api_development",
    "algorithms",
    "competitive_programming",
    "applied_mathematics",
    "statistics",
    "optimization",
    "probability",
    "operations_research",
    "product_analytics",
    "fintech",
    "quantitative_finance",
    "research",
    "open_source",
    "startup_projects",
    "education_technology",
}


ALLOWED_GOALS = {
    "find_internship",
    "find_research_opportunity",
    "join_hackathon",
    "build_portfolio",
    "improve_skills",
    "find_scholarship_or_grant",
    "prepare_for_big_tech",
    "explore_career_direction",
    "contribute_to_open_source",
    "find_summer_school",
    "find_competitions",
    "network_with_people",
}


ALLOWED_PREFERRED_FORMATS = {
    pref_for.value for pref_for in OpportunityFormat
}


SKILL_LEVEL_TO_SCORE = {
    "novice": 1,
    "beginner": 2,
    "intermediate": 3,
    "advanced": 4,
    "expert": 5,
}


def validate_allowed_value(
    value: str,
    allowed_values: set[str],
    field_name: str,
) -> str:
    if value not in allowed_values:
        raise ValueError(
            f"Unknown {field_name}: '{value}'. "
            f"Allowed values: {sorted(allowed_values)}"
        )

    return value


def validate_allowed_values(
    values: list[str],
    allowed_values: set[str],
    field_name: str,
) -> list[str]:
    seen: set[str] = set()

    for value in values:
        validate_allowed_value(
            value=value,
            allowed_values=allowed_values,
            field_name=field_name,
        )

        if value in seen:
            raise ValueError(
                f"Duplicate value in {field_name}: '{value}'"
            )

        seen.add(value)

    return values


def validate_skill_requirements(
    skills: dict[str, int],
    field_name: str,
) -> dict[str, int]:
    for skill_name, level in skills.items():
        validate_allowed_value(
            value=skill_name,
            allowed_values=ALLOWED_SKILLS,
            field_name=field_name,
        )

        if not 1 <= level <= 5:
            raise ValueError(
                f"Skill level for '{skill_name}' in {field_name} "
                "must be between 1 and 5"
            )

    return skills


def validate_disjoint_skill_groups(
    required_skills: dict[str, int],
    nice_to_have_skills: dict[str, int],
) -> None:
    overlap = set(required_skills) & set(nice_to_have_skills)

    if overlap:
        raise ValueError(
            "The same skill cannot be both required and nice-to-have: "
            f"{sorted(overlap)}"
        )