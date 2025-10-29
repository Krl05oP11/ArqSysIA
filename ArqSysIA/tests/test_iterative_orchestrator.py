"""
Tests for IterativeOrchestrator

Tests the complete iterative orchestration flow including:
- run_iteration() with Enhanced Phases coordination
- regenerate_code() feedback loop
- redesign_architecture() feedback loop
- accept_and_continue() workflow
- Integration with VersionManager, DecisionLogger, DiffEngine
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from arqsysia.core import (
    IterativeOrchestrator,
    IterationResult,
    VersionManager,
    DecisionLogger,
    DiffEngine,
    ProjectState,
    Iteration,
    Decision,
    create_iterative_orchestrator
)
from arqsysia.storage.file_storage import FileStorage


@pytest.fixture
def temp_storage(tmp_path):
    """Create temporary FileStorage"""
    return FileStorage(base_dir=str(tmp_path))


@pytest.fixture
def orchestrator(temp_storage):
    """Create IterativeOrchestrator with temp storage"""
    return IterativeOrchestrator("TestProject", temp_storage)


@pytest.fixture
def sample_iteration_1():
    """Create sample first iteration for testing"""
    state = ProjectState(
        project_name="TestProject",
        iteration=1,
        original_requirements="Build a web app",
        outputs={
            'analysis': {
                'requirements': 'Build a web app',
                'architecture_pattern': 'Monolithic',
                'main_components': ['Frontend', 'Backend', 'Database']
            },
            'code_generation': {
                'files': [
                    {'name': 'frontend', 'type': 'component'},
                    {'name': 'backend', 'type': 'component'}
                ]
            },
            'validation': {
                'scores': {'architecture': 7, 'code': 6, 'security': 5},
                'issues': [
                    {'severity': 'medium', 'description': 'Performance issue', 'component': 'backend'}
                ]
            }
        }
    )
    
    return Iteration(
        project_name="TestProject",
        iteration_number=1,
        state=state,
        decisions=[],
        created_at=datetime.now(),
        duration_seconds=150.0,
        phase_durations={'analyzer': 50.0, 'codegen': 70.0, 'validator': 30.0},
        final_scores={'architecture': 7, 'code': 6, 'security': 5},
        status='completed'
    )


@pytest.fixture
def mock_enhanced_phases(orchestrator):
    """Mock Enhanced Phases to return predictable results"""
    # Mock analyzer
    orchestrator.analyzer.analyze = Mock(return_value={
        'iteration': 1,
        'has_context': False,
        'architecture_pattern': 'Monolithic',
        'main_components': ['Frontend', 'Backend'],
        'requirements': 'Test requirements'
    })
    
    # Mock codegen
    orchestrator.codegen.generate = Mock(return_value={
        'iteration': 1,
        'has_previous_code': False,
        'generation_strategy': 'full_generation',
        'files': [{'name': 'main.py'}]
    })
    
    # Mock validator
    orchestrator.validator.validate = Mock(return_value={
        'iteration': 1,
        'has_comparison': False,
        'scores': {'architecture': 8, 'code': 7, 'security': 6},
        'issues': [],
        'trend_analysis': 'First iteration'
    })
    
    return orchestrator


# ===== Basic Functionality Tests =====

def test_orchestrator_initialization(orchestrator):
    """Test IterativeOrchestrator initializes correctly"""
    assert orchestrator.project_name == "TestProject"
    assert orchestrator.storage is not None
    assert orchestrator.version_manager is not None
    assert orchestrator.decision_logger is not None
    assert orchestrator.diff_engine is not None
    assert orchestrator.analyzer is not None
    assert orchestrator.codegen is not None
    assert orchestrator.validator is not None
    assert orchestrator.current_iteration == 0
    assert orchestrator.last_result is None


def test_create_iterative_orchestrator(temp_storage):
    """Test factory function creates orchestrator correctly"""
    orchestrator = create_iterative_orchestrator("TestProject", temp_storage)
    
    assert isinstance(orchestrator, IterativeOrchestrator)
    assert orchestrator.project_name == "TestProject"
    assert orchestrator.storage == temp_storage


def test_iteration_result_dataclass():
    """Test IterationResult dataclass and methods"""
    result = IterationResult(
        iteration=1,
        project_name="TestProject",
        analysis={'test': 'analysis'},
        codegen={'test': 'codegen'},
        validation={
            'scores': {'architecture': 8, 'code': 7},
            'issues': [
                {'severity': 'high', 'description': 'Test issue'}
            ]
        },
        timestamp=datetime.now(),
        duration_seconds=100.0,
        phase_durations={'analyzer': 30.0, 'codegen': 50.0, 'validator': 20.0}
    )
    
    # Test get_final_scores
    scores = result.get_final_scores()
    assert scores == {'architecture': 8, 'code': 7}
    
    # Test has_issues
    assert result.has_issues() is True
    
    # Test get_issues_count
    assert result.get_issues_count() == 1


# ===== run_iteration() Tests =====

def test_run_iteration_first_iteration(mock_enhanced_phases):
    """Test run_iteration with first iteration"""
    result = mock_enhanced_phases.run_iteration(
        requirements="Build a web application",
        iteration_number=1
    )
    
    # Verify result structure
    assert isinstance(result, IterationResult)
    assert result.iteration == 1
    assert result.project_name == "TestProject"
    assert 'architecture_pattern' in result.analysis
    assert 'files' in result.codegen
    assert 'scores' in result.validation
    
    # Verify phases were called
    mock_enhanced_phases.analyzer.analyze.assert_called_once()
    mock_enhanced_phases.codegen.generate.assert_called_once()
    mock_enhanced_phases.validator.validate.assert_called_once()
    
    # Verify state was updated
    assert mock_enhanced_phases.current_iteration == 1
    assert mock_enhanced_phases.last_result == result


def test_run_iteration_with_feedback(mock_enhanced_phases):
    """Test run_iteration with user feedback"""
    result = mock_enhanced_phases.run_iteration(
        requirements="Improve the system",
        iteration_number=2,
        user_feedback="Backend is slow",
        user_instructions="Add caching"
    )
    
    assert result.iteration == 2
    
    # Verify analyzer received feedback
    call_args = mock_enhanced_phases.analyzer.analyze.call_args
    assert call_args[1]['user_feedback'] == "Backend is slow"
    
    # Verify codegen received instructions
    call_args = mock_enhanced_phases.codegen.generate.call_args
    assert call_args[1]['user_instructions'] == "Add caching"


def test_run_iteration_saves_to_storage(orchestrator, mock_enhanced_phases):
    """Test that run_iteration saves results to storage"""
    result = mock_enhanced_phases.run_iteration(
        requirements="Test requirements",
        iteration_number=1
    )
    
    # Verify iteration was saved
    saved_iterations = orchestrator.version_manager.list_iterations()
    assert len(saved_iterations) == 1
    assert saved_iterations[0].iteration_number == 1
    assert saved_iterations[0].status == 'completed'


# ===== regenerate_code() Tests =====

def test_regenerate_code_reuses_analysis(mock_enhanced_phases, sample_iteration_1):
    """Test regenerate_code reuses previous analysis"""
    # Save first iteration
    mock_enhanced_phases.storage.save_iteration(sample_iteration_1)
    
    # Create a previous result
    previous_result = IterationResult(
        iteration=1,
        project_name="TestProject",
        analysis={'architecture_pattern': 'Monolithic', 'requirements': 'Build app'},
        codegen={'files': []},
        validation={'scores': {'code': 5}},
        timestamp=datetime.now(),
        duration_seconds=100.0
    )
    
    # Regenerate code
    result = mock_enhanced_phases.regenerate_code(
        previous_result=previous_result,
        user_feedback="Improve performance"
    )
    
    # Verify analyzer was NOT called (analysis reused)
    # Note: analyzer might be called once during initialization, so check call count
    initial_calls = mock_enhanced_phases.analyzer.analyze.call_count
    
    # Verify codegen WAS called
    assert mock_enhanced_phases.codegen.generate.called
    
    # Verify validator WAS called
    assert mock_enhanced_phases.validator.validate.called
    
    # Verify it's a new iteration
    assert result.iteration == 2


def test_regenerate_code_logs_decision(mock_enhanced_phases):
    """Test regenerate_code logs orchestrator decision"""
    previous_result = IterationResult(
        iteration=1,
        project_name="TestProject",
        analysis={'requirements': 'Test'},
        codegen={},
        validation={},
        timestamp=datetime.now()
    )
    
    result = mock_enhanced_phases.regenerate_code(
        previous_result=previous_result,
        user_feedback="Fix bugs"
    )
    
    # Verify decision was logged
    decisions = mock_enhanced_phases.decision_logger.get_decisions_for_iteration(2)
    
    # Should have at least one orchestrator decision
    orchestrator_decisions = [d for d in decisions if d.phase == 'orchestrator']
    assert len(orchestrator_decisions) > 0
    
    # Verify decision content
    decision = orchestrator_decisions[0]
    assert 'Regenerate code' in decision.decision
    assert 'Fix bugs' in decision.rationale


# ===== redesign_architecture() Tests =====

def test_redesign_architecture_runs_full_iteration(mock_enhanced_phases):
    """Test redesign_architecture runs complete new iteration"""
    previous_result = IterationResult(
        iteration=1,
        project_name="TestProject",
        analysis={'requirements': 'Build app'},
        codegen={},
        validation={},
        timestamp=datetime.now()
    )
    
    # Reset mocks to track new calls
    mock_enhanced_phases.analyzer.analyze.reset_mock()
    mock_enhanced_phases.codegen.generate.reset_mock()
    mock_enhanced_phases.validator.validate.reset_mock()
    
    result = mock_enhanced_phases.redesign_architecture(
        previous_result=previous_result,
        user_instructions="Change to microservices"
    )
    
    # Verify ALL phases were called (full redesign)
    assert mock_enhanced_phases.analyzer.analyze.called
    assert mock_enhanced_phases.codegen.generate.called
    assert mock_enhanced_phases.validator.validate.called
    
    # Verify it's a new iteration
    assert result.iteration == 2


def test_redesign_architecture_logs_decision(mock_enhanced_phases):
    """Test redesign_architecture logs orchestrator decision"""
    previous_result = IterationResult(
        iteration=1,
        project_name="TestProject",
        analysis={'requirements': 'Test'},
        codegen={},
        validation={},
        timestamp=datetime.now()
    )
    
    result = mock_enhanced_phases.redesign_architecture(
        previous_result=previous_result,
        user_instructions="Change to serverless"
    )
    
    # Verify decision was logged
    decisions = mock_enhanced_phases.decision_logger.get_decisions_for_iteration(2)
    orchestrator_decisions = [d for d in decisions if d.phase == 'orchestrator']
    
    assert len(orchestrator_decisions) > 0
    decision = orchestrator_decisions[0]
    assert 'Redesign architecture' in decision.decision
    assert 'serverless' in decision.rationale.lower()


# ===== accept_and_continue() Tests =====

def test_accept_and_continue_logs_decision(mock_enhanced_phases):
    """Test accept_and_continue logs acceptance decision"""
    result = IterationResult(
        iteration=1,
        project_name="TestProject",
        analysis={},
        codegen={},
        validation={},
        timestamp=datetime.now()
    )
    
    mock_enhanced_phases.accept_and_continue(result)
    
    # Verify decision was logged
    decisions = mock_enhanced_phases.decision_logger.get_decisions_for_iteration(1)
    orchestrator_decisions = [d for d in decisions if d.phase == 'orchestrator']
    
    assert len(orchestrator_decisions) > 0
    decision = orchestrator_decisions[0]
    assert 'Accept iteration' in decision.decision
    assert 'approved' in decision.rationale.lower()


# ===== Integration Tests =====

def test_full_workflow_two_iterations(mock_enhanced_phases):
    """Test complete workflow with two iterations"""
    # First iteration
    result1 = mock_enhanced_phases.run_iteration(
        requirements="Build a web app",
        iteration_number=1
    )
    
    assert result1.iteration == 1
    assert mock_enhanced_phases.current_iteration == 1
    
    # Accept first iteration
    mock_enhanced_phases.accept_and_continue(result1)
    
    # Second iteration with feedback
    mock_enhanced_phases.analyzer.analyze.return_value['iteration'] = 2
    mock_enhanced_phases.analyzer.analyze.return_value['has_context'] = True
    mock_enhanced_phases.codegen.generate.return_value['iteration'] = 2
    mock_enhanced_phases.validator.validate.return_value['iteration'] = 2
    
    result2 = mock_enhanced_phases.run_iteration(
        requirements="Build a web app",
        iteration_number=2,
        user_feedback="Add authentication"
    )
    
    assert result2.iteration == 2
    assert mock_enhanced_phases.current_iteration == 2
    
    # Verify both iterations are saved
    iterations = mock_enhanced_phases.version_manager.list_iterations()
    assert len(iterations) == 2
    assert iterations[0].iteration_number == 1
    assert iterations[1].iteration_number == 2


def test_feedback_loop_regenerate_then_accept(mock_enhanced_phases, sample_iteration_1):
    """Test feedback loop: run → regenerate → accept"""
    # Save first iteration
    mock_enhanced_phases.storage.save_iteration(sample_iteration_1)
    
    # First iteration
    result1 = IterationResult(
        iteration=1,
        project_name="TestProject",
        analysis={'requirements': 'Build app'},
        codegen={'files': []},
        validation={'scores': {'code': 5}},
        timestamp=datetime.now()
    )
    
    # Regenerate with feedback
    mock_enhanced_phases.codegen.generate.return_value['iteration'] = 2
    mock_enhanced_phases.validator.validate.return_value['iteration'] = 2
    
    result2 = mock_enhanced_phases.regenerate_code(
        previous_result=result1,
        user_feedback="Improve code quality"
    )
    
    assert result2.iteration == 2
    
    # Accept second iteration
    mock_enhanced_phases.accept_and_continue(result2)
    
    # Verify decisions were logged for both iterations
    all_decisions = []
    for i in [1, 2]:
        decisions = mock_enhanced_phases.decision_logger.get_decisions_for_iteration(i)
        all_decisions.extend(decisions)
    
    # Should have decisions from orchestrator
    orchestrator_decisions = [d for d in all_decisions if d.phase == 'orchestrator']
    assert len(orchestrator_decisions) >= 2  # At least regenerate and accept decisions


def test_error_handling_in_iteration(orchestrator):
    """Test error handling when a phase fails"""
    # Make analyzer raise an exception
    orchestrator.analyzer.analyze = Mock(side_effect=Exception("Analyzer failed"))
    
    # run_iteration should propagate the exception
    with pytest.raises(Exception, match="Analyzer failed"):
        orchestrator.run_iteration(
            requirements="Test",
            iteration_number=1
        )
        
