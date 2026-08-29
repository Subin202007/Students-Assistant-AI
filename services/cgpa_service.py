def calculate_gpa(results):
    """Calculate GPA from a list of SemesterResult objects."""
    total_points = 0
    total_credits = 0
    for r in results:
        total_points += r.credits * r.grade_point
        total_credits += r.credits
    return round(total_points / total_credits, 2) if total_credits > 0 else 0


def calculate_cgpa(all_results):
    """Calculate CGPA from all semester results."""
    # Group by semester
    semesters = {}
    for r in all_results:
        if r.semester not in semesters:
            semesters[r.semester] = []
        semesters[r.semester].append(r)

    total_points = 0
    total_credits = 0
    for sem_results in semesters.values():
        for r in sem_results:
            total_points += r.credits * r.grade_point
            total_credits += r.credits

    return round(total_points / total_credits, 2) if total_credits > 0 else 0