"""
Feature extraction from Moodle activity data — Fase 3 stub.
"""
# TODO Fase 3: extract features from Moodle logs via REST API.


def extract_features(user_id: int, course_id: int, moodle_token: str) -> dict:
    """
    Extracts activity features for a student in a course.

    Returns dict with keys: forum_posts, resource_views, assignment_submissions,
    last_access_days_ago, quiz_avg_score, login_frequency_7d
    """
    raise NotImplementedError("Feature extraction not yet implemented (Fase 3)")
