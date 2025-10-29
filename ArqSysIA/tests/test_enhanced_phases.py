"""
Tests for Enhanced Phases (Analyzer, CodeGen, Validator)
"""

import pytest
from datetime import datetime
from pathlib import Path

from arqsysia.phases.enhanced_analyzer import EnhancedAnalyzer
from arqsysia.phases.enhanced_codegen import EnhancedCodeGen
from arqsysia.phases.enhanced_validator import EnhancedValidator
from arqsysia.core import (
    VersionManager,
    DecisionLogger,
    DiffEngine,
    ProjectState,
    Iteration,
    Decision
)
from arqsysia.storage.file_storage import FileStorage


@pytest.fixture
def temp_storage(tmp_path):
    """Create temporary FileStorage"""
    return FileStorage(base_dir=str(tmp_path))


@pytest.fixture
def version_manager(temp_storage):
    """Create VersionManager with temp storage"""
    return VersionManager("TestProject", temp_storage)


@pytest.fixture
def decision_logger(temp_storage):
    """Create DecisionLogger with temp storage"""
    return DecisionLogger("TestProject", temp_storage)


@pytest.fixture
def diff_engine():
    """Create DiffEngine"""
    return DiffEngine()


@pytest.fixture
def enhanced_analyzer(version_manager, decision_logger, diff_engine):
    """Create EnhancedAnalyzer with dependencies"""
    return EnhancedAnalyzer(version_manager, decision_logger, diff_engine)


@pytest.fixture
def enhanced_codegen(version_manager, decision_logger):
    """Create EnhancedCodeGen with dependencies"""
    return EnhancedCodeGen(version_manager, decision_logger)


@pytest.fixture
def enhanced_validator(version_manager, diff_engine):
    """Create EnhancedValidator with dependencies"""
    return EnhancedValidator(version_manager, diff_engine)


@pytest.fixture
def sample_iteration_1():
    """Create sample first iteration"""
    state = ProjectState(
        project_name="TestProject",
        iteration=1,
        original_requirements="Build a web app",
        outputs={
            'analysis': {
                'architecture_pattern': 'Monolithic',
                'main_components': ['Frontend', 'Backend', 'Database']
            },
            'code_generation': {
                'files': [
                    {'name': 'frontend', 'type': 'component', 'path': '/src/frontend'},
                    {'name': 'backend', 'type': 'component', 'path': '/src/backend'}
                ]
            },
            'validation': {
                'scores': {'architecture': 7, 'code': 6, 'security': 5},
                'issues': [
                    {'severity': 'medium', 'description': 'Performance bottleneck', 'component': 'backend'}
                ]
            }
        }
    )
    
    return Iteration(
        project_name="TestProject",
        iteration_number=1,
        state=state,
        decisions=[
            Decision(
                iteration=1,
                phase='analyzer',
                decision='Use Monolithic architecture',
                rationale='Simplicity for MVP',
                alternatives_considered=['Microservices', 'Serverless'],
                chosen_alternative='Monolithic',
                impacted_components=['all'],
                triggered_by='initial'
            )
        ],
        created_at=datetime.now(),
        duration_seconds=350.0,  # Sum of phase_durations: 100 + 200 + 50
        phase_durations={'analyzer': 100.0, 'codegen': 200.0, 'validator': 50.0},
        final_scores={'architecture': 7, 'code': 6, 'security': 5},
        status='completed'
    )


# ===== EnhancedAnalyzer Tests =====

def test_enhanced_analyzer_first_iteration(enhanced_analyzer):
    """Test EnhancedAnalyzer with first iteration (no context)"""
    result = enhanced_analyzer.analyze(
        requirements="Build a web application",
        project_name="TestProject",
        current_iteration=1
    )
    
    assert result['iteration'] == 1
    assert result['has_context'] is False
    assert result['context_summary'] == "First iteration - no previous context"
    assert len(result['previous_decisions']) == 0
    assert result['diff_summary'] is None


def test_enhanced_analyzer_second_iteration_with_context(
    enhanced_analyzer,
    version_manager,
    decision_logger,
    sample_iteration_1
):
    """Test EnhancedAnalyzer with second iteration (has context)"""
    # Save first iteration directly using storage
    version_manager.storage.save_iteration(sample_iteration_1)
    
    # Log a decision
    decision = sample_iteration_1.decisions[0]
    decision_logger.log_decision(
        iteration=decision.iteration,
        phase=decision.phase,
        decision=decision.decision,
        rationale=decision.rationale,
        alternatives_considered=decision.alternatives_considered,
        chosen_alternative=decision.chosen_alternative,
        impacted_components=decision.impacted_components,
        triggered_by=decision.triggered_by
    )
    
    # Analyze second iteration
    result = enhanced_analyzer.analyze(
        requirements="Improve performance",
        project_name="TestProject",
        current_iteration=2,
        user_feedback="Backend is slow"
    )
    
    assert result['iteration'] == 2
    assert result['has_context'] is True
    assert result['user_feedback'] == "Backend is slow"
    assert 'previous_iteration' in result
    assert len(result['previous_decisions']) > 0
    assert result['context_summary'] is not None


def test_enhanced_analyzer_build_prompt(enhanced_analyzer):
    """Test prompt building with context"""
    context = {
        'previous_iteration': {
            'iteration': 1,
            'status': 'completed',
            'scores': {'architecture': 7, 'code': 6}
        },
        'decisions': [
            {
                'phase': 'analyzer',
                'decision': 'Use Monolithic architecture',
                'rationale': 'Simplicity for MVP'
            }
        ],
        'diff_summary': {
            'architecture_changed': False,
            'components_added': 0,
            'components_removed': 0,
            'score_improvements': 0,
            'new_issues': 1,
            'resolved_issues': 0
        }
    }
    
    prompt = enhanced_analyzer.build_prompt(
        requirements="New requirements",
        context=context
    )
    
    assert "ARCHITECTURAL ANALYSIS" in prompt
    assert "CURRENT REQUIREMENTS" in prompt
    assert "PREVIOUS ITERATION" in prompt
    assert "PREVIOUS DECISIONS" in prompt
    assert "RECENT CHANGES" in prompt


# ===== EnhancedCodeGen Tests =====

def test_enhanced_codegen_first_iteration(enhanced_codegen):
    """Test EnhancedCodeGen with first iteration"""
    result = enhanced_codegen.generate(
        analysis_result={'iteration': 1},
        project_name="TestProject",
        current_iteration=1
    )
    
    assert result['iteration'] == 1
    assert result['has_previous_code'] is False
    assert result['generation_strategy'] == 'full_generation'
    assert len(result['reused_components']) == 0


def test_enhanced_codegen_second_iteration_with_memory(
    enhanced_codegen,
    version_manager,
    sample_iteration_1
):
    """Test EnhancedCodeGen with code memory from previous iteration"""
    # Save first iteration directly using storage
    version_manager.storage.save_iteration(sample_iteration_1)
    
    # Generate code for second iteration
    analysis_result = {
        'analysis': {
            'main_components': ['Frontend', 'Backend', 'Database', 'Cache']
        }
    }
    
    result = enhanced_codegen.generate(
        analysis_result=analysis_result,
        project_name="TestProject",
        current_iteration=2,
        user_instructions="Add caching layer"
    )
    
    assert result['iteration'] == 2
    assert result['has_previous_code'] is True
    assert result['generation_strategy'] in ['incremental', 'minimal_changes', 'partial_regeneration']
    assert result['code_context'] is not None


def test_enhanced_codegen_categorizes_components(
    enhanced_codegen,
    version_manager,
    sample_iteration_1
):
    """Test that CodeGen correctly categorizes components"""
    version_manager.storage.save_iteration(sample_iteration_1)
    
    analysis_result = {
        'analysis': {
            'main_components': ['Frontend', 'Backend', 'Database', 'NewService']
        }
    }
    
    result = enhanced_codegen.generate(
        analysis_result=analysis_result,
        project_name="TestProject",
        current_iteration=2
    )
    
    # Frontend and Database should be reusable (no issues)
    # Backend has issues, should be modified
    # NewService should be created
    assert len(result['reused_components']) + len(result['modified_components']) + len(result['new_components']) > 0


def test_enhanced_codegen_build_prompt(enhanced_codegen):
    """Test prompt building for code generation"""
    code_context = {
        'strategy': 'incremental',
        'reusable': ['Frontend', 'Database'],
        'to_modify': [{'name': 'Backend', 'reason': '1 issues found'}],
        'to_create': ['Cache'],
        'previous_code_summary': {
            'files_generated': 5,
            'issues_found': 1,
            'scores': {'code': 6}
        }
    }
    
    analysis_result = {
        'analysis': {
            'architecture_pattern': 'Monolithic',
            'main_components': ['Frontend', 'Backend', 'Database', 'Cache']
        }
    }
    
    prompt = enhanced_codegen.build_prompt(analysis_result, code_context)
    
    assert "CODE GENERATION WITH MEMORY" in prompt
    assert "GENERATION STRATEGY: INCREMENTAL" in prompt
    assert "PREVIOUS CODE" in prompt
    assert "COMPONENTS TO REUSE" in prompt
    assert "COMPONENTS TO MODIFY" in prompt
    assert "NEW COMPONENTS TO CREATE" in prompt


# ===== EnhancedValidator Tests =====

def test_enhanced_validator_first_iteration(enhanced_validator):
    """Test EnhancedValidator with first iteration (no comparison)"""
    result = enhanced_validator.validate(
        codegen_result={},
        analysis_result={},
        project_name="TestProject",
        current_iteration=1
    )
    
    assert result['iteration'] == 1
    assert result['has_comparison'] is False
    assert result['trend_analysis'] == "First iteration - no historical data"


def test_enhanced_validator_with_comparison(
    enhanced_validator,
    version_manager,
    sample_iteration_1
):
    """Test EnhancedValidator with historical comparison"""
    # Save first iteration directly using storage
    version_manager.storage.save_iteration(sample_iteration_1)
    
    # Validate second iteration
    result = enhanced_validator.validate(
        codegen_result={},
        analysis_result={},
        project_name="TestProject",
        current_iteration=2
    )
    
    assert result['iteration'] == 2
    assert result['has_comparison'] is True
    assert result['trend_analysis'] is not None
    assert isinstance(result['trend_analysis'], dict)
    assert 'summary' in result['trend_analysis']


def test_enhanced_validator_detects_regressions(enhanced_validator):
    """Test regression detection in validator"""
    prev_scores = {'architecture': 8, 'code': 7, 'security': 6}
    current_scores = {'architecture': 6, 'code': 5, 'security': 6}
    
    regressions = enhanced_validator._detect_regressions(prev_scores, current_scores)
    
    # Architecture dropped by 2, code dropped by 2
    assert len(regressions) == 2
    assert any(r['metric'] == 'architecture' for r in regressions)
    assert any(r['metric'] == 'code' for r in regressions)


def test_enhanced_validator_analyzes_trends(enhanced_validator):
    """Test trend analysis"""
    prev_scores = {'architecture': 7, 'code': 6, 'security': 5}
    current_scores = {'architecture': 8, 'code': 6, 'security': 4}
    
    trends = enhanced_validator._analyze_score_trends(prev_scores, current_scores)
    
    assert 'improvements' in trends
    assert 'regressions' in trends
    assert 'stable' in trends
    assert 'summary' in trends
    
    assert 'architecture' in trends['improvements']
    assert 'security' in trends['regressions']
    assert 'code' in trends['stable']


def test_enhanced_validator_generates_recommendations(
    enhanced_validator,
    sample_iteration_1
):
    """Test recommendation generation"""
    trends = {
        'overall_trend': 'declining',
        'improvements': {},
        'regressions': {}
    }
    
    regressions = [
        {'metric': 'code', 'severity': 'high', 'delta': -3}
    ]
    
    recommendations = enhanced_validator._generate_recommendations(
        trends,
        regressions,
        sample_iteration_1
    )
    
    assert len(recommendations) > 0
    assert any('URGENT' in rec for rec in recommendations)


def test_enhanced_validator_build_prompt(enhanced_validator):
    """Test prompt building for validation"""
    validation_context = {
        'trends': {
            'summary': 'Overall improving',
            'improvements': {
                'architecture': {'previous': 7, 'current': 8, 'delta': 1}
            },
            'regressions': {
                'security': {'previous': 6, 'current': 4, 'delta': -2}
            }
        },
        'regressions': [
            {
                'metric': 'security',
                'previous_score': 6,
                'current_score': 4,
                'delta': -2,
                'severity': 'medium'
            }
        ],
        'recommendations': [
            'Address security regression',
            'Continue current approach for architecture'
        ]
    }
    
    prompt = enhanced_validator.build_prompt({}, validation_context)
    
    assert "VALIDATION WITH HISTORICAL COMPARISON" in prompt
    assert "SCORE TRENDS" in prompt
    assert "DETECTED REGRESSIONS" in prompt
    assert "RECOMMENDATIONS" in prompt


# ===== Integration Tests =====

def test_full_pipeline_integration(
    enhanced_analyzer,
    enhanced_codegen,
    enhanced_validator,
    version_manager,
    decision_logger,
    sample_iteration_1
):
    """Test full pipeline: Analyzer → CodeGen → Validator"""
    # Setup: Save first iteration directly using storage
    version_manager.storage.save_iteration(sample_iteration_1)
    decision = sample_iteration_1.decisions[0]
    decision_logger.log_decision(
	iteration=decision.iteration,
	phase=decision.phase,
	decision=decision.decision,
	rationale=decision.rationale,
	alternatives_considered=decision.alternatives_considered,
	chosen_alternative=decision.chosen_alternative,
	impacted_components=decision.impacted_components,
	triggered_by=decision.triggered_by
    )    
    # Step 1: Analyze
    analysis_result = enhanced_analyzer.analyze(
        requirements="Improve the system",
        project_name="TestProject",
        current_iteration=2
    )
    
    assert analysis_result['has_context'] is True
    
    # Step 2: Generate Code
    codegen_result = enhanced_codegen.generate(
        analysis_result=analysis_result,
        project_name="TestProject",
        current_iteration=2
    )
    
    assert codegen_result['has_previous_code'] is True
    
    # Step 3: Validate
    validation_result = enhanced_validator.validate(
        codegen_result=codegen_result,
        analysis_result=analysis_result,
        project_name="TestProject",
        current_iteration=2
    )
    
    assert validation_result['has_comparison'] is True
    assert validation_result['trend_analysis'] is not None
            
