"""
Tests para DecisionLogger.

Tests de registro, consulta y búsqueda de decisiones arquitectónicas.
"""

import pytest
from datetime import datetime
from arqsysia.core.decision_logger import DecisionLogger
from arqsysia.storage.file_storage import FileStorage


@pytest.fixture
def temp_storage(tmp_path):
    """Fixture: Storage temporal para tests"""
    storage = FileStorage(base_dir=str(tmp_path))
    return storage


@pytest.fixture
def logger(temp_storage):
    """Fixture: DecisionLogger con storage temporal"""
    return DecisionLogger("test_project", storage=temp_storage)


def test_log_single_decision(logger):
    """Test: Registrar una decisión simple"""
    
    decision = logger.log_decision(
        iteration=1,
        phase="analyzer",
        decision="Usar arquitectura de microservicios",
        rationale="Mejor escalabilidad y mantenibilidad",
        alternatives_considered=["Monolito", "Modular monolith"],
        chosen_alternative="Microservicios"
    )
    
    # Verificar que se creó correctamente
    assert decision.iteration == 1
    assert decision.phase == "analyzer"
    assert decision.decision == "Usar arquitectura de microservicios"
    assert decision.rationale == "Mejor escalabilidad y mantenibilidad"
    assert len(decision.alternatives_considered) == 2
    assert decision.chosen_alternative == "Microservicios"
    assert decision.triggered_by == "manual"
    assert isinstance(decision.timestamp, datetime)
    
    # Verificar que se puede recuperar
    all_decisions = logger.get_all_decisions()
    assert len(all_decisions) == 1
    assert all_decisions[0].decision == "Usar arquitectura de microservicios"


def test_log_multiple_decisions(logger):
    """Test: Registrar múltiples decisiones en diferentes iteraciones"""
    
    # Decisión 1: Iteración 1, analyzer
    logger.log_decision(
        iteration=1,
        phase="analyzer",
        decision="Sistema monolítico inicial",
        rationale="Simplicidad para MVP"
    )
    
    # Decisión 2: Iteración 2, validator
    logger.log_decision(
        iteration=2,
        phase="validator",
        decision="Separar servicio de pagos",
        rationale="Validator detectó problemas de seguridad",
        triggered_by="validator"
    )
    
    # Decisión 3: Iteración 2, codegen
    logger.log_decision(
        iteration=2,
        phase="codegen",
        decision="Implementar API Gateway",
        rationale="Centralizar autenticación",
        impacted_components=["API Gateway", "Auth Service"]
    )
    
    # Verificar que todas se registraron
    all_decisions = logger.get_all_decisions()
    assert len(all_decisions) == 3
    
    # Verificar orden cronológico
    assert all_decisions[0].iteration == 1
    assert all_decisions[1].iteration == 2
    assert all_decisions[2].iteration == 2


def test_get_decisions_for_iteration(logger):
    """Test: Filtrar decisiones por iteración"""
    
    # Crear decisiones en diferentes iteraciones
    logger.log_decision(1, "analyzer", "Decisión v1.1", "Razón 1")
    logger.log_decision(1, "codegen", "Decisión v1.2", "Razón 2")
    logger.log_decision(2, "analyzer", "Decisión v2.1", "Razón 3")
    logger.log_decision(2, "validator", "Decisión v2.2", "Razón 4")
    logger.log_decision(3, "analyzer", "Decisión v3.1", "Razón 5")
    
    # Filtrar por iteración 1
    decisions_v1 = logger.get_decisions_for_iteration(1)
    assert len(decisions_v1) == 2
    assert all(d.iteration == 1 for d in decisions_v1)
    
    # Filtrar por iteración 2
    decisions_v2 = logger.get_decisions_for_iteration(2)
    assert len(decisions_v2) == 2
    assert all(d.iteration == 2 for d in decisions_v2)
    
    # Filtrar por iteración 3
    decisions_v3 = logger.get_decisions_for_iteration(3)
    assert len(decisions_v3) == 1
    assert decisions_v3[0].decision == "Decisión v3.1"
    
    # Iteración sin decisiones
    decisions_v4 = logger.get_decisions_for_iteration(4)
    assert len(decisions_v4) == 0


def test_get_decisions_for_phase(logger):
    """Test: Filtrar decisiones por fase"""
    
    # Crear decisiones en diferentes fases
    logger.log_decision(1, "analyzer", "Análisis 1", "Razón 1")
    logger.log_decision(1, "analyzer", "Análisis 2", "Razón 2")
    logger.log_decision(1, "codegen", "Generación 1", "Razón 3")
    logger.log_decision(2, "validator", "Validación 1", "Razón 4")
    logger.log_decision(2, "validator", "Validación 2", "Razón 5")
    
    # Filtrar por fase analyzer
    analyzer_decisions = logger.get_decisions_for_phase("analyzer")
    assert len(analyzer_decisions) == 2
    assert all(d.phase == "analyzer" for d in analyzer_decisions)
    
    # Filtrar por fase validator
    validator_decisions = logger.get_decisions_for_phase("validator")
    assert len(validator_decisions) == 2
    assert all(d.phase == "validator" for d in validator_decisions)
    
    # Filtrar por fase codegen
    codegen_decisions = logger.get_decisions_for_phase("codegen")
    assert len(codegen_decisions) == 1
    assert codegen_decisions[0].decision == "Generación 1"


def test_search_decisions(logger):
    """Test: Búsqueda de decisiones por texto"""
    
    # Crear decisiones con diferentes textos
    logger.log_decision(
        1, "analyzer",
        decision="Usar microservicios",
        rationale="Mejor escalabilidad"
    )
    
    logger.log_decision(
        1, "codegen",
        decision="Implementar API REST",
        rationale="Estándar de la industria"
    )
    
    logger.log_decision(
        2, "validator",
        decision="Agregar autenticación OAuth",
        rationale="Seguridad mejorada",
        alternatives_considered=["JWT", "Session-based", "OAuth"],
        chosen_alternative="OAuth"
    )
    
    # Búsqueda en decision
    results = logger.search_decisions("microservicios")
    assert len(results) == 1
    assert results[0].decision == "Usar microservicios"
    
    # Búsqueda en rationale
    results = logger.search_decisions("escalabilidad")
    assert len(results) == 1
    
    # Búsqueda en alternatives_considered
    results = logger.search_decisions("JWT")
    assert len(results) == 1
    assert results[0].decision == "Agregar autenticación OAuth"
    
    # Búsqueda case-insensitive
    results = logger.search_decisions("OAUTH")
    assert len(results) == 1
    
    # Búsqueda sin resultados
    results = logger.search_decisions("blockchain")
    assert len(results) == 0


def test_decision_summary(logger):
    """Test: Resumen estadístico de decisiones"""
    
    # Crear decisiones variadas
    logger.log_decision(1, "analyzer", "D1", "R1", triggered_by="manual")
    logger.log_decision(1, "codegen", "D2", "R2", triggered_by="validator")
    logger.log_decision(2, "analyzer", "D3", "R3", triggered_by="validator")
    logger.log_decision(2, "validator", "D4", "R4", triggered_by="user_feedback")
    logger.log_decision(3, "validator", "D5", "R5", triggered_by="validator")
    
    # Obtener resumen
    summary = logger.get_decision_summary()
    
    # Verificar total
    assert summary['total'] == 5
    
    # Verificar por iteración
    assert summary['by_iteration'][1] == 2
    assert summary['by_iteration'][2] == 2
    assert summary['by_iteration'][3] == 1
    
    # Verificar por fase
    assert summary['by_phase']['analyzer'] == 2
    assert summary['by_phase']['codegen'] == 1
    assert summary['by_phase']['validator'] == 2
    
    # Verificar por trigger
    assert summary['by_trigger']['manual'] == 1
    assert summary['by_trigger']['validator'] == 3
    assert summary['by_trigger']['user_feedback'] == 1


def test_empty_logger(logger):
    """Test: DecisionLogger sin decisiones"""
    
    # Verificar estado inicial
    assert logger.get_decision_count() == 0
    assert logger.get_all_decisions() == []
    assert logger.get_decisions_for_iteration(1) == []
    assert logger.get_decisions_for_phase("analyzer") == []
    assert logger.search_decisions("test") == []
    
    # Verificar resumen vacío
    summary = logger.get_decision_summary()
    assert summary['total'] == 0
    assert summary['by_iteration'] == {}
    assert summary['by_phase'] == {}
    assert summary['by_trigger'] == {}


def test_persistence(temp_storage):
    """Test: Persistencia de decisiones entre instancias"""
    
    project_name = "test_persistence"
    
    # Crear logger 1 y registrar decisiones
    logger1 = DecisionLogger(project_name, storage=temp_storage)
    logger1.log_decision(1, "analyzer", "Decisión 1", "Razón 1")
    logger1.log_decision(2, "codegen", "Decisión 2", "Razón 2")
    
    # Crear logger 2 (nueva instancia)
    logger2 = DecisionLogger(project_name, storage=temp_storage)
    
    # Verificar que persisten las decisiones
    decisions = logger2.get_all_decisions()
    assert len(decisions) == 2
    assert decisions[0].decision == "Decisión 1"
    assert decisions[1].decision == "Decisión 2"
    
