"""
Tests para VersionManager

Sesión 8 - ArqSysIA v1.0
Objetivo: Validar operaciones de gestión de versiones e historial
"""

import pytest
from datetime import datetime
from arqsysia.core.version_manager import VersionManager
from arqsysia.core.state import ProjectState, Iteration
from arqsysia.storage.file_storage import FileStorage
import tempfile
import shutil


@pytest.fixture
def temp_storage_dir():
    """Crea un directorio temporal para tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def version_manager(temp_storage_dir):
    """Crea VersionManager con storage temporal"""
    storage = FileStorage(base_dir=temp_storage_dir)
    vm = VersionManager("test_project", storage=storage)
    return vm


def create_mock_state(iteration: int = 1, arch: str = "monolito") -> ProjectState:
    """Helper: Crea un ProjectState mock para testing"""
    return ProjectState(
        project_name="test_project",
        iteration=iteration,
        parent_iteration=iteration - 1 if iteration > 1 else None,
        original_requirements=f"Requirements para iteración {iteration}",
        outputs={
            "analysis": {
                "architecture": arch,
                "components": [f"component_{i}" for i in range(3)],
                "description": f"Arquitectura {arch} para iteración {iteration}"
            },
            "code_generation": {
                "files": [
                    {"path": "main.py", "content": "# Main file"}
                ]
            },
            "validation": {
                "scores": {
                    "architecture": 7 + iteration,
                    "code": 6 + iteration,
                    "security": 6,
                    "optimization": 5
                },
                "issues": []
            }
        },
        user_feedback=f"Feedback para iteración {iteration}" if iteration > 1 else None
    )


# ========================================
# TEST 1: Save and Load Iteration
# ========================================

def test_save_and_load_iteration(version_manager):
    """Test: Guardar y recuperar una iteración"""
    
    # Crear estado mock
    state = create_mock_state(iteration=1)
    
    # Guardar iteración
    saved_iteration = version_manager.save_iteration(
        state=state,
        decisions=[],
        duration=1000.5,
        phase_durations={
            "analyzer": 300.0,
            "codegen": 600.0,
            "validator": 100.5
        }
    )
    
    # Verificar que se guardó correctamente
    assert saved_iteration.iteration_number == 1
    assert saved_iteration.project_name == "test_project"
    assert saved_iteration.state.iteration == 1
    assert saved_iteration.duration_seconds == 1000.5
    assert saved_iteration.status == "completed"
    
    # Recuperar iteración
    loaded_iteration = version_manager.get_iteration(1)
    
    # Verificar que se recuperó correctamente
    assert loaded_iteration.iteration_number == 1
    assert loaded_iteration.state.original_requirements == state.original_requirements
    assert loaded_iteration.state.outputs["analysis"]["architecture"] == "monolito"
    assert loaded_iteration.duration_seconds == 1000.5


# ========================================
# TEST 2: List Iterations
# ========================================

def test_list_iterations(version_manager):
    """Test: Listar múltiples iteraciones"""
    
    # Crear 3 iteraciones
    for i in range(1, 4):
        state = create_mock_state(iteration=i)
        version_manager.save_iteration(state, [], 1000.0, {})
    
    # Listar iteraciones
    iterations = version_manager.list_iterations()
    
    # Verificar
    assert len(iterations) == 3
    assert iterations[0].iteration_number == 1
    assert iterations[1].iteration_number == 2
    assert iterations[2].iteration_number == 3
    
    # Verificar orden cronológico
    for i in range(len(iterations) - 1):
        assert iterations[i].created_at <= iterations[i + 1].created_at


# ========================================
# TEST 3: Get Latest Iteration
# ========================================

def test_get_latest_iteration(version_manager):
    """Test: Obtener la última iteración"""
    
    # Inicialmente no hay iteraciones
    latest = version_manager.get_latest_iteration()
    assert latest is None
    
    # Crear 2 iteraciones
    state1 = create_mock_state(iteration=1)
    version_manager.save_iteration(state1, [], 1000.0, {})
    
    state2 = create_mock_state(iteration=2)
    version_manager.save_iteration(state2, [], 1500.0, {})
    
    # Obtener última
    latest = version_manager.get_latest_iteration()
    
    # Verificar
    assert latest is not None
    assert latest.iteration_number == 2
    assert latest.state.iteration == 2


# ========================================
# TEST 4: Compare Iterations
# ========================================

def test_compare_iterations(version_manager):
    """Test: Comparar dos iteraciones"""
    
    # Crear dos iteraciones con arquitecturas diferentes
    state_v1 = create_mock_state(iteration=1, arch="monolito")
    version_manager.save_iteration(state_v1, [], 1000.0, {})
    
    state_v2 = create_mock_state(iteration=2, arch="microservicios")
    version_manager.save_iteration(state_v2, [], 1200.0, {})
    
    # Comparar iteraciones
    comparison = version_manager.compare_iterations(1, 2)
    
    # Verificar que detectó cambio de arquitectura
    assert comparison["architecture_changed"]["changed"] == True
    assert comparison["architecture_changed"]["previous"] == "monolito"
    assert comparison["architecture_changed"]["current"] == "microservicios"
    
    # Verificar que hay información de componentes
    assert "components_changed" in comparison
    
    # Verificar diferencia de scores
    assert "scores_diff" in comparison
    scores_diff = comparison["scores_diff"]
    assert scores_diff["architecture"] == 1  # 8 - 7
    assert scores_diff["code"] == 1  # 7 - 6


# ========================================
# TEST 5: Rollback
# ========================================

def test_rollback(version_manager):
    """Test: Rollback a iteración anterior"""
    
    # Crear 3 iteraciones
    for i in range(1, 4):
        state = create_mock_state(iteration=i)
        version_manager.save_iteration(state, [], 1000.0, {})
    
    # Verificar que hay 3
    assert len(version_manager.list_iterations()) == 3
    
    # Rollback a iteración 2
    version_manager.rollback_to(2)
    
    # Verificar que solo quedan 2 iteraciones
    iterations = version_manager.list_iterations()
    assert len(iterations) == 2
    assert iterations[-1].iteration_number == 2
    
    # Verificar que la iteración 3 fue eliminada
    with pytest.raises(FileNotFoundError):
        version_manager.get_iteration(3)
    
    # Verificar que metadata se actualizó
    metadata = version_manager.storage.load_metadata("test_project")
    assert metadata.current_iteration == 2
    assert metadata.total_iterations == 2


# ========================================
# TEST 6: Iteration with Decisions
# ========================================

def test_iteration_with_decisions(version_manager):
    """Test: Guardar iteración con decisiones"""
    
    from arqsysia.core.state import Decision
    
    # Crear estado y decisión
    state = create_mock_state(iteration=1)
    decision = Decision(
        iteration=1,
        phase="analyzer",
        decision="Usar arquitectura monolítica",
        rationale="Simplicidad para MVP",
        alternatives_considered=["Microservicios", "Modular"],
        chosen_alternative="Monolito",
        impacted_components=["backend", "database"],
        triggered_by="user_requirements"
    )
    
    # Guardar iteración con decisión
    saved_iteration = version_manager.save_iteration(
        state=state,
        decisions=[decision],
        duration=1000.0,
        phase_durations={}
    )
    
    # Verificar que la decisión se guardó
    assert len(saved_iteration.decisions) == 1
    assert saved_iteration.decisions[0].decision == "Usar arquitectura monolítica"
    
    # Recuperar y verificar
    loaded_iteration = version_manager.get_iteration(1)
    assert len(loaded_iteration.decisions) == 1
    assert loaded_iteration.decisions[0].rationale == "Simplicidad para MVP"


# ========================================
# TEST 7: Parent-Child Relationship
# ========================================

def test_parent_child_relationship(version_manager):
    """Test: Relación padre-hijo entre iteraciones"""
    
    # Iteración 1 (sin padre)
    state1 = create_mock_state(iteration=1)
    version_manager.save_iteration(state1, [], 1000.0, {})
    
    # Iteración 2 (hijo de 1)
    state2 = create_mock_state(iteration=2)
    state2.parent_iteration = 1
    version_manager.save_iteration(state2, [], 1200.0, {})
    
    # Iteración 3 (hijo de 2)
    state3 = create_mock_state(iteration=3)
    state3.parent_iteration = 2
    version_manager.save_iteration(state3, [], 1400.0, {})
    
    # Verificar relaciones
    iter1 = version_manager.get_iteration(1)
    iter2 = version_manager.get_iteration(2)
    iter3 = version_manager.get_iteration(3)
    
    assert iter1.state.parent_iteration is None
    assert iter2.state.parent_iteration == 1
    assert iter3.state.parent_iteration == 2


# ========================================
# TEST 8: Error Handling
# ========================================

def test_error_handling(version_manager):
    """Test: Manejo de errores"""
    
    # Intentar cargar iteración inexistente
    with pytest.raises(FileNotFoundError):
        version_manager.get_iteration(999)
    
    # Intentar comparar iteraciones inexistentes
    with pytest.raises(FileNotFoundError):
        version_manager.compare_iterations(1, 999)
    
    # Intentar rollback a iteración inexistente (debe fallar silenciosamente o dar warning)
    # No debería crashear
    version_manager.rollback_to(999)


# ========================================
# INTEGRATION TEST: Full Workflow
# ========================================

def test_full_workflow(version_manager):
    """Test de integración: Flujo completo de 3 iteraciones"""
    
    # Iteración 1: Diseño inicial
    state1 = create_mock_state(iteration=1, arch="monolito")
    version_manager.save_iteration(state1, [], 1000.0, {"analyzer": 300, "codegen": 600, "validator": 100})
    
    # Iteración 2: Mejora basada en feedback
    state2 = create_mock_state(iteration=2, arch="modular")
    state2.user_feedback = "Agregar sistema de autenticación"
    state2.parent_iteration = 1
    version_manager.save_iteration(state2, [], 1200.0, {"analyzer": 350, "codegen": 700, "validator": 150})
    
    # Iteración 3: Refinamiento
    state3 = create_mock_state(iteration=3, arch="microservicios")
    state3.user_feedback = "Separar servicios de auth y pagos"
    state3.parent_iteration = 2
    version_manager.save_iteration(state3, [], 1400.0, {"analyzer": 400, "codegen": 800, "validator": 200})
    
    # Verificar historial completo
    iterations = version_manager.list_iterations()
    assert len(iterations) == 3
    
    # Comparar v1 vs v3
    comparison = version_manager.compare_iterations(1, 3)
    assert comparison["architecture_changed"]["changed"] == True
    assert comparison["architecture_changed"]["previous"] == "monolito"
    assert comparison["architecture_changed"]["current"] == "microservicios"
    
    # Rollback a v2
    version_manager.rollback_to(2)
    assert len(version_manager.list_iterations()) == 2
    
    # Verificar que la última iteración es v2
    latest = version_manager.get_latest_iteration()
    assert latest.iteration_number == 2
    assert latest.state.outputs["analysis"]["architecture"] == "modular"
    
