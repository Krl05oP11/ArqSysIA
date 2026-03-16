"""
Risk Model — Fase 3 stub.
XGBoost model for predicting student dropout risk from Moodle activity data.
"""
# TODO Fase 3: train and load XGBoost model.


def evaluate_risk(features: dict) -> dict:
    """
    Returns a risk assessment for a student.

    Args:
        features: dict of extracted Moodle features (see features.py)

    Returns:
        dict with keys: score (float 0-1), risk_level (low/medium/high), factors (dict)
    """
    raise NotImplementedError("Risk model not yet implemented (Fase 3)")
