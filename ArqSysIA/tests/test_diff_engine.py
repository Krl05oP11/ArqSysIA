"""
Tests for DiffEngine
"""

import pytest
from datetime import datetime

from arqsysia.core.diff_engine import DiffEngine, DiffResult
from arqsysia.core.state import ProjectState, Decision


@pytest.fixture
def diff_engine():
    """Create a DiffEngine instance"""
    return DiffEngine()


@pytest.fixture
def base_state():
    """Create a base ProjectState for testing"""
    return ProjectState(
        project_name="TestProject",
        iteration=1,
        original_requirements="Build a web app",
        outputs={
            'analysis': {
                'architecture_pattern': 'Monolithic',
                'main_components': ['Frontend', 'Backend', 'Database']
            },
            'validation': {
                'scores': {
                    'architecture': 7,
                    'code': 6,
                    'scalability': 5
                },
                'issues': [
                    {'severity': 'high', 'description': 'Security vulnerability in auth'},
                    {'severity': 'medium', 'description': 'Performance bottleneck in API'}
                ]
            }
        }
    )


@pytest.fixture
def evolved_state():
    """Create an evolved ProjectState for testing"""
    return ProjectState(
        project_name="TestProject",
        iteration=2,
        original_requirements="Build a web app",
        outputs={
            'analysis': {
                'architecture_pattern': 'Microservices',
                'main_components': ['Frontend', 'Auth Service', 'API Gateway', 'Database']
            },
            'validation': {
                'scores': {
                    'architecture': 9,
                    'code': 7,
                    'scalability': 8
                },
                'issues': [
                    {'severity': 'medium', 'description': 'Performance bottleneck in API'},
                    {'severity': 'low', 'description': 'Missing documentation'}
                ]
            }
        }
    )


def test_compare_no_changes(diff_engine, base_state):
    """Test comparing identical states shows no changes"""
    state1 = base_state
    state2 = ProjectState(
        project_name="TestProject",
        iteration=2,
        original_requirements="Build a web app",
        outputs=state1.outputs
    )
    
    diff = diff_engine.compare_iterations(state1, state2)
    
    assert diff.iteration_from == 1
    assert diff.iteration_to == 2
    assert not diff.architecture_changed
    assert len(diff.components_added) == 0
    assert len(diff.components_removed) == 0
    assert len(diff.score_improvements) == 0
    assert len(diff.score_regressions) == 0


def test_compare_architecture_change(diff_engine, base_state, evolved_state):
    """Test detecting architecture pattern changes"""
    diff = diff_engine.compare_iterations(base_state, evolved_state)
    
    assert diff.architecture_changed
    assert diff.architecture_from == 'Monolithic'
    assert diff.architecture_to == 'Microservices'


def test_compare_components_added_removed(diff_engine, base_state, evolved_state):
    """Test detecting added and removed components"""
    diff = diff_engine.compare_iterations(base_state, evolved_state)
    
    # Auth Service and API Gateway added, Backend removed
    assert 'Auth Service' in diff.components_added
    assert 'API Gateway' in diff.components_added
    assert 'Backend' in diff.components_removed
    assert len(diff.components_added) == 2
    assert len(diff.components_removed) == 1


def test_compare_score_improvements_regressions(diff_engine, base_state, evolved_state):
    """Test detecting score improvements and regressions"""
    diff = diff_engine.compare_iterations(base_state, evolved_state)
    
    # Improvements
    assert diff.score_improvements['architecture'] == 2  # 7 -> 9
    assert diff.score_improvements['code'] == 1  # 6 -> 7
    assert diff.score_improvements['scalability'] == 3  # 5 -> 8
    
    # No regressions in this case
    assert len(diff.score_regressions) == 0


def test_compare_with_score_regression(diff_engine, base_state):
    """Test detecting score regressions"""
    worse_state = ProjectState(
        project_name="TestProject",
        iteration=2,
        original_requirements="Build a web app",
        outputs={
            'analysis': {
                'architecture_pattern': 'Monolithic',
                'main_components': ['Frontend', 'Backend', 'Database']
            },
            'validation': {
                'scores': {
                    'architecture': 5,  # Regressed from 7
                    'code': 6,  # No change
                    'scalability': 3  # Regressed from 5
                },
                'issues': []
            }
        }
    )
    
    diff = diff_engine.compare_iterations(base_state, worse_state)
    
    assert diff.score_regressions['architecture'] == -2
    assert diff.score_regressions['scalability'] == -2
    assert 'code' not in diff.score_regressions


def test_compare_issues_new_resolved(diff_engine, base_state, evolved_state):
    """Test detecting new and resolved issues"""
    diff = diff_engine.compare_iterations(base_state, evolved_state)
    
    # New issue: Missing documentation
    assert len(diff.new_issues) == 1
    assert diff.new_issues[0]['description'] == 'Missing documentation'
    
    # Resolved issue: Security vulnerability
    assert len(diff.resolved_issues) == 1
    assert diff.resolved_issues[0]['description'] == 'Security vulnerability in auth'
    
    # Persisting issue: Performance bottleneck
    assert len(diff.persisting_issues) == 1
    assert diff.persisting_issues[0]['description'] == 'Performance bottleneck in API'


def test_format_diff_text_basic(diff_engine, base_state, evolved_state):
    """Test formatting diff as text"""
    diff = diff_engine.compare_iterations(base_state, evolved_state)
    text = diff_engine.format_diff_text(diff)
    
    # Check header
    assert "DIFF: Iteration 1 → 2" in text
    
    # Check architecture section
    assert "ARCHITECTURE CHANGES" in text
    assert "Monolithic" in text
    assert "Microservices" in text
    
    # Check components section
    assert "COMPONENT CHANGES" in text
    assert "Auth Service" in text
    assert "API Gateway" in text
    assert "Backend" in text
    
    # Check scores section
    assert "SCORE CHANGES" in text
    assert "Improvements" in text
    assert "architecture: +2" in text
    
    # Check issues section
    assert "ISSUE CHANGES" in text
    assert "New Issues" in text
    assert "Resolved Issues" in text


def test_format_diff_text_no_changes(diff_engine, base_state):
    """Test formatting diff with no changes"""
    state2 = ProjectState(
        project_name="TestProject",
        iteration=2,
        original_requirements="Build a web app",
        outputs=base_state.outputs
    )
    
    diff = diff_engine.compare_iterations(base_state, state2)
    text = diff_engine.format_diff_text(diff)
    
    assert "ARCHITECTURE: No changes" in text
    assert "COMPONENTS: No changes" in text
    assert "SCORES: No changes" in text
    assert "ISSUES: No changes" in text


def test_diff_result_dataclass():
    """Test DiffResult dataclass creation and defaults"""
    diff = DiffResult(
        iteration_from=1,
        iteration_to=2,
        architecture_changed=True,
        architecture_from="Old",
        architecture_to="New",
        components_added=["A"],
        components_removed=["B"],
        components_modified=["C"]
    )
    
    assert diff.iteration_from == 1
    assert diff.iteration_to == 2
    assert diff.architecture_changed
    assert diff.architecture_from == "Old"
    assert diff.architecture_to == "New"
    assert diff.components_added == ["A"]
    
    # Check defaults
    assert isinstance(diff.score_improvements, dict)
    assert isinstance(diff.score_regressions, dict)
    assert isinstance(diff.new_issues, list)
    assert isinstance(diff.resolved_issues, list)
    assert isinstance(diff.persisting_issues, list)
    assert isinstance(diff.decisions_made, list)
    assert isinstance(diff.timestamp, datetime)
    
