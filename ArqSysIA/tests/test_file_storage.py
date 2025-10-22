"""
Tests para FileStorage Backend
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from arqsysia.storage.file_storage import FileStorage
from arqsysia.core.state import ProjectState, Iteration, Decision, ProjectMetadata


@pytest.fixture
def temp_storage():
    """Fixture: crea un FileStorage temporal"""
    temp_dir = tempfile.mkdtemp()
    storage = FileStorage(base_dir=temp_dir)
    
    yield storage
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_state():
    """Fixture: ProjectState de ejemplo"""
    return ProjectState(
        project_name="test_project",
        iteration=1,
        original_requirements="Sistema de blog personal"
    )


@pytest.fixture
def sample_iteration(sample_state):
    """Fixture: Iteration de ejemplo"""
    return Iteration(
        project_name="test_project",
        iteration_number=1,
        state=sample_state,
        decisions=[],
        created_at=datetime.now(),
        duration_seconds=120.5,
        phase_durations={"analyzer": 50.0, "codegen": 70.5},
        final_scores={"architecture": 85, "code_quality": 90}
    )


@pytest.fixture
def sample_decision():
    """Fixture: Decision de ejemplo"""
    return Decision(
        iteration=1,
        phase="analyzer",
        decision="Adoptar arquitectura MVC",
        rationale="Separación clara de responsabilidades",
        alternatives_considered=["Monolito", "Microservicios"],
        chosen_alternative="MVC",
        impacted_components=["Backend", "Frontend"]
    )


# ============================================================
# TESTS DE ESTRUCTURA
# ============================================================

def test_file_storage_initialization(temp_storage):
    """Test: FileStorage se inicializa correctamente"""
    assert temp_storage.base_dir.exists()
    assert temp_storage.base_dir.is_dir()


def test_project_structure_creation(temp_storage):
    """Test: Estructura de proyecto se crea correctamente"""
    project_name = "test_project"
    temp_storage._ensure_project_structure(project_name)
    
    project_dir = temp_storage._get_project_dir(project_name)
    iterations_dir = temp_storage._get_iterations_dir(project_name)
    
    assert project_dir.exists()
    assert iterations_dir.exists()
    assert (project_dir / "iterations").is_dir()


# ============================================================
# TESTS DE ITERACIONES
# ============================================================

def test_save_iteration(temp_storage, sample_iteration):
    """Test: Guardar iteración"""
    temp_storage.save_iteration(sample_iteration)
    
    # Verificar que el archivo existe
    iteration_file = temp_storage._get_iteration_file("test_project", 1)
    assert iteration_file.exists()
    
    # Verificar estructura del directorio
    project_dir = temp_storage._get_project_dir("test_project")
    assert (project_dir / "iterations").exists()
    assert (project_dir / "metadata.json").exists()


def test_load_iteration(temp_storage, sample_iteration):
    """Test: Cargar iteración"""
    # Guardar primero
    temp_storage.save_iteration(sample_iteration)
    
    # Cargar
    loaded = temp_storage.load_iteration("test_project", 1)
    
    assert loaded is not None
    assert loaded.project_name == "test_project"
    assert loaded.iteration_number == 1
    assert loaded.duration_seconds == 120.5
    assert loaded.final_scores == {"architecture": 85, "code_quality": 90}
    assert loaded.state.original_requirements == "Sistema de blog personal"


def test_load_nonexistent_iteration(temp_storage):
    """Test: Cargar iteración que no existe"""
    # load_iteration lanza FileNotFoundError si no existe
    with pytest.raises(FileNotFoundError):
        temp_storage.load_iteration("nonexistent_project", 1)


def test_list_iterations(temp_storage, sample_state):
    """Test: Listar iteraciones"""
    # Crear 3 iteraciones
    for i in range(1, 4):
        iteration = Iteration(
            project_name="test_project",
            iteration_number=i,
            state=sample_state,
            decisions=[],
            created_at=datetime.now(),
            duration_seconds=100.0 + i,
            phase_durations={},
            final_scores={}
        )
        temp_storage.save_iteration(iteration)
    
    # Listar
    iterations = temp_storage.list_iterations("test_project")
    
    assert len(iterations) == 3
    # list_iterations retorna objetos Iteration, no diccionarios
    assert iterations[0].iteration_number == 1
    assert iterations[1].iteration_number == 2
    assert iterations[2].iteration_number == 3
    
    # Verificar que contiene info básica
    assert hasattr(iterations[0], 'created_at')
    assert hasattr(iterations[0], 'duration_seconds')
    assert hasattr(iterations[0], 'status')


def test_list_iterations_empty_project(temp_storage):
    """Test: Listar iteraciones de proyecto sin iteraciones"""
    iterations = temp_storage.list_iterations("empty_project")
    assert iterations == []


def test_delete_iteration(temp_storage, sample_state):
    """Test: Eliminar iteración"""
    # Crear 3 iteraciones
    for i in range(1, 4):
        iteration = Iteration(
            project_name="test_project",
            iteration_number=i,
            state=sample_state,
            decisions=[],
            created_at=datetime.now(),
            duration_seconds=100.0,
            phase_durations={},
            final_scores={}
        )
        temp_storage.save_iteration(iteration)
    
    # Eliminar iteración 2
    temp_storage.delete_iteration("test_project", 2)
    
    # Verificar
    iterations = temp_storage.list_iterations("test_project")
    assert len(iterations) == 2
    
    # Objetos Iteration, no diccionarios
    iteration_numbers = [i.iteration_number for i in iterations]
    assert 2 not in iteration_numbers
    assert 1 in iteration_numbers
    assert 3 in iteration_numbers
    
    # Verificar que el archivo fue eliminado
    iteration_file = temp_storage._get_iteration_file("test_project", 2)
    assert not iteration_file.exists()


# ============================================================
# TESTS DE DECISIONES
# ============================================================

def test_save_decision(temp_storage, sample_decision):
    """Test: Guardar decisión"""
    temp_storage.save_decision("test_project", sample_decision)
    
    # Verificar que el archivo existe
    decisions_file = temp_storage._get_decisions_file("test_project")
    assert decisions_file.exists()


def test_get_decisions_all(temp_storage):
    """Test: Obtener todas las decisiones"""
    # Crear 3 decisiones en diferentes iteraciones
    for i in range(1, 4):
        decision = Decision(
            iteration=i,
            phase="analyzer",
            decision=f"Decisión {i}",
            rationale=f"Razón {i}"
        )
        temp_storage.save_decision("test_project", decision)
    
    # Obtener todas
    decisions = temp_storage.get_decisions("test_project")
    
    assert len(decisions) == 3
    assert decisions[0].decision == "Decisión 1"
    assert decisions[1].decision == "Decisión 2"
    assert decisions[2].decision == "Decisión 3"


def test_get_decisions_by_iteration(temp_storage):
    """Test: Obtener decisiones de una iteración específica"""
    # Crear decisiones en diferentes iteraciones
    for i in range(1, 4):
        for j in range(2):  # 2 decisiones por iteración
            decision = Decision(
                iteration=i,
                phase="analyzer",
                decision=f"Decisión iter={i}, num={j}",
                rationale="Razón"
            )
            temp_storage.save_decision("test_project", decision)
    
    # Obtener solo de iteración 2
    decisions = temp_storage.get_decisions("test_project", iteration=2)
    
    assert len(decisions) == 2
    assert all(d.iteration == 2 for d in decisions)


def test_get_decisions_empty(temp_storage):
    """Test: Obtener decisiones de proyecto sin decisiones"""
    decisions = temp_storage.get_decisions("empty_project")
    assert decisions == []


# ============================================================
# TESTS DE METADATA
# ============================================================

def test_save_metadata(temp_storage):
    """Test: Guardar metadata"""
    now = datetime.now()
    metadata = ProjectMetadata(
        project_name="test_project",
        created_at=now,
        last_updated=now,
        total_iterations=5,
        current_iteration=5,
        storage_backend="file",
        storage_path=str(temp_storage.base_dir)
    )
    
    temp_storage.save_metadata(metadata)
    
    # Verificar que el archivo existe
    metadata_file = temp_storage._get_metadata_file("test_project")
    assert metadata_file.exists()


def test_load_metadata(temp_storage):
    """Test: Cargar metadata"""
    now = datetime.now()
    metadata = ProjectMetadata(
        project_name="test_project",
        created_at=now,
        last_updated=now,
        total_iterations=5,
        current_iteration=5,
        storage_backend="file",
        storage_path=str(temp_storage.base_dir)
    )
    
    # Guardar
    temp_storage.save_metadata(metadata)
    
    # Cargar
    loaded = temp_storage.load_metadata("test_project")
    
    assert loaded is not None
    assert loaded.project_name == "test_project"
    assert loaded.total_iterations == 5
    assert loaded.current_iteration == 5
    assert loaded.storage_backend == "file"


def test_load_metadata_nonexistent(temp_storage):
    """Test: Cargar metadata de proyecto inexistente"""
    loaded = temp_storage.load_metadata("nonexistent")
    assert loaded is None


def test_metadata_auto_update_on_save_iteration(temp_storage, sample_state):
    """Test: Metadata se actualiza automáticamente al guardar iteración"""
    # Crear primera iteración
    iteration1 = Iteration(
        project_name="test_project",
        iteration_number=1,
        state=sample_state,
        decisions=[],
        created_at=datetime.now(),
        duration_seconds=100.0,
        phase_durations={},
        final_scores={}
    )
    temp_storage.save_iteration(iteration1)
    
    # Verificar metadata
    metadata = temp_storage.load_metadata("test_project")
    assert metadata is not None
    assert metadata.total_iterations == 1
    assert metadata.current_iteration == 1
    
    # Crear segunda iteración
    iteration2 = Iteration(
        project_name="test_project",
        iteration_number=2,
        state=sample_state,
        decisions=[],
        created_at=datetime.now(),
        duration_seconds=150.0,
        phase_durations={},
        final_scores={}
    )
    temp_storage.save_iteration(iteration2)
    
    # Verificar metadata actualizada
    metadata = temp_storage.load_metadata("test_project")
    assert metadata.total_iterations == 2
    assert metadata.current_iteration == 2


def test_metadata_update_on_delete_iteration(temp_storage, sample_state):
    """Test: Metadata se actualiza al eliminar iteración"""
    # Crear 3 iteraciones
    for i in range(1, 4):
        iteration = Iteration(
            project_name="test_project",
            iteration_number=i,
            state=sample_state,
            decisions=[],
            created_at=datetime.now(),
            duration_seconds=100.0,
            phase_durations={},
            final_scores={}
        )
        temp_storage.save_iteration(iteration)
    
    # Verificar metadata inicial
    metadata = temp_storage.load_metadata("test_project")
    assert metadata.total_iterations == 3
    assert metadata.current_iteration == 3
    
    # Eliminar iteración 3
    temp_storage.delete_iteration("test_project", 3)
    
    # Verificar metadata actualizada
    metadata = temp_storage.load_metadata("test_project")
    assert metadata.total_iterations == 2
    assert metadata.current_iteration == 2


# ============================================================
# TESTS DE INTEGRACIÓN
# ============================================================

def test_full_workflow(temp_storage, sample_state):
    """Test: Flujo completo - crear proyecto, iteraciones, decisiones"""
    project_name = "full_test"
    
    # Iteración 1
    iteration1 = Iteration(
        project_name=project_name,
        iteration_number=1,
        state=sample_state,
        decisions=[],
        created_at=datetime.now(),
        duration_seconds=120.0,
        phase_durations={},
        final_scores={}
    )
    temp_storage.save_iteration(iteration1)
    
    decision1 = Decision(
        iteration=1,
        phase="analyzer",
        decision="Primera decisión",
        rationale="Razón 1"
    )
    temp_storage.save_decision(project_name, decision1)
    
    # Iteración 2
    iteration2 = Iteration(
        project_name=project_name,
        iteration_number=2,
        state=sample_state,
        decisions=[],
        created_at=datetime.now(),
        duration_seconds=150.0,
        phase_durations={},
        final_scores={}
    )
    temp_storage.save_iteration(iteration2)
    
    decision2 = Decision(
        iteration=2,
        phase="codegen",
        decision="Segunda decisión",
        rationale="Razón 2"
    )
    temp_storage.save_decision(project_name, decision2)
    
    # Verificaciones finales
    iterations = temp_storage.list_iterations(project_name)
    assert len(iterations) == 2
    
    decisions = temp_storage.get_decisions(project_name)
    assert len(decisions) == 2
    
    metadata = temp_storage.load_metadata(project_name)
    assert metadata.total_iterations == 2
    assert metadata.current_iteration == 2
    
    # Cargar iteración específica
    loaded = temp_storage.load_iteration(project_name, 1)
    assert loaded.iteration_number == 1
    assert loaded.duration_seconds == 120.0


def test_multiple_projects(temp_storage, sample_state):
    """Test: Múltiples proyectos en el mismo storage"""
    projects = ["project_a", "project_b", "project_c"]
    
    for project in projects:
        for i in range(1, 3):
            iteration = Iteration(
                project_name=project,
                iteration_number=i,
                state=sample_state,
                decisions=[],
                created_at=datetime.now(),
                duration_seconds=100.0,
                phase_durations={},
                final_scores={}
            )
            temp_storage.save_iteration(iteration)
    
    # Verificar que cada proyecto tiene sus iteraciones
    for project in projects:
        iterations = temp_storage.list_iterations(project)
        assert len(iterations) == 2
        
        metadata = temp_storage.load_metadata(project)
        assert metadata.project_name == project
        assert metadata.total_iterations == 2
