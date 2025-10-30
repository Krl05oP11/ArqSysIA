"""Tests para CLI de ArqSysIA - Versión Final Corregida."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from io import StringIO

from arqsysia.cli import ArqSysiaCLI, IterationViewer, DiffViewer
from arqsysia.core.state import ProjectState, Iteration
from arqsysia.core import IterationResult, IterativeOrchestrator
from arqsysia.storage.file_storage import FileStorage
from datetime import datetime


@pytest.fixture
def temp_storage(tmp_path):
    """Storage temporal para tests."""
    return FileStorage(str(tmp_path))


@pytest.fixture
def cli(temp_storage, tmp_path):
    """CLI para tests."""
    return ArqSysiaCLI("TestProject", str(tmp_path))


@pytest.fixture
def sample_iteration(temp_storage):
    """Iteración de ejemplo para tests."""
    state = ProjectState(
        project_name="TestProject",
        iteration=1,
        parent_iteration=None,
        original_requirements="Test requirements",
        outputs={
            'analysis': {'architecture': {'pattern': 'microservices'}},
            'code_generation': {'components': ['api', 'database']},
            'validation': {
                'overall_score': 85,
                'quality_score': 80,
                'issues': [
                    {'severity': 'low', 'description': 'Minor issue'}
                ]
            }
        },
        created_at=datetime.now()
    )
    
    iteration = Iteration(
        project_name="TestProject",
        iteration_number=1,
        state=state,
        decisions=[],
        created_at=datetime.now(),
        duration_seconds=0.0,
        phase_durations={},
        final_scores={}
    )
    
    return iteration


@pytest.fixture
def sample_iteration_2():
    """Segunda iteración de ejemplo para tests."""
    state = ProjectState(
        project_name="TestProject",
        iteration=2,
        parent_iteration=1,
        original_requirements="Test requirements v2",
        outputs={
            'analysis': {'architecture': {'pattern': 'microservices'}},
            'code_generation': {'components': ['api', 'database', 'cache']},
            'validation': {
                'overall_score': 90,
                'quality_score': 88,
                'issues': []
            }
        },
        created_at=datetime.now()
    )
    
    iteration = Iteration(
        project_name="TestProject",
        iteration_number=2,
        state=state,
        decisions=[],
        created_at=datetime.now(),
        duration_seconds=0.0,
        phase_durations={},
        final_scores={}
    )
    
    return iteration


# ==================== ArqSysiaCLI Tests ====================

def test_cli_initialization(cli):
    """Test: CLI se inicializa correctamente."""
    assert cli.project_name == "TestProject"
    assert cli.orchestrator is not None
    assert cli.viewer is not None
    assert cli.diff_viewer is not None
    assert cli.running is True


@patch('builtins.input', side_effect=['7'])  # Exit inmediato
@patch('sys.stdout', new_callable=StringIO)
def test_cli_prints_welcome(mock_stdout, mock_input, cli):
    """Test: CLI imprime mensaje de bienvenida."""
    cli.run()
    
    output = mock_stdout.getvalue()
    assert "ArqSysIA v1.0" in output
    assert "TestProject" in output


@patch('builtins.input', side_effect=['invalid', '0', '8', '7'])
@patch('sys.stdout', new_callable=StringIO)
def test_cli_handles_invalid_input(mock_stdout, mock_input, cli):
    """Test: CLI maneja inputs inválidos correctamente."""
    cli.run()
    
    output = mock_stdout.getvalue()
    # Debe haber mostrado mensaje de error
    assert "Invalid choice" in output or "❌" in output


@patch('builtins.input', side_effect=['7'])
def test_cli_exit_command(mock_input, cli):
    """Test: Comando exit termina el CLI correctamente."""
    cli.run()
    
    assert cli.running is False


@patch('builtins.input', side_effect=['6', '', '7'])  # Settings, Enter, Exit
@patch('sys.stdout', new_callable=StringIO)
def test_cli_settings_command(mock_stdout, mock_input, cli):
    """Test: Comando settings muestra configuración."""
    cli.run()
    
    output = mock_stdout.getvalue()
    assert "SETTINGS" in output
    assert "TestProject" in output


def test_cli_handle_choice_calls_correct_handler(cli):
    """Test: handle_choice llama al handler correcto."""
    # Mock de handlers
    cli.new_iteration = Mock()
    cli.view_history = Mock()
    cli.exit_cli = Mock()
    
    # Probar diferentes opciones
    cli.handle_choice('1')
    cli.new_iteration.assert_called_once()
    
    cli.handle_choice('2')
    cli.view_history.assert_called_once()
    
    cli.handle_choice('7')
    cli.exit_cli.assert_called_once()


# ✅ CORRECCIÓN: Agregar 'y' para la confirmación
@patch('builtins.input', side_effect=['Test requirements', 'END', 'y', ''])  # Requirements, END, Confirm, Enter
def test_new_iteration_flow(mock_input, cli):
    """Test: new_iteration ejecuta iteración correctamente."""
    # Mockear métodos del orchestrator en la instancia del CLI
    mock_result = IterationResult(
        iteration=1,
        project_name="TestProject",
        analysis={'architecture': {}},
        codegen={'components': []},
        validation={'overall_score': 80, 'quality_score': 75, 'issues': []},
        timestamp=datetime.now()
    )
    
    cli.orchestrator.run_iteration = Mock(return_value=mock_result)
    cli.orchestrator.post_validation_menu = Mock(return_value='accept')
    
    # Ejecutar
    cli.new_iteration()
    
    # Verificar que se llamó run_iteration
    cli.orchestrator.run_iteration.assert_called_once()
    
    # Verificar que se llamó post_validation_menu
    cli.orchestrator.post_validation_menu.assert_called_once()


@patch('builtins.input', side_effect=['', 'END', ''])  # Empty, END, Enter
@patch('sys.stdout', new_callable=StringIO)
def test_new_iteration_empty_requirements(mock_stdout, mock_input, cli):
    """Test: new_iteration rechaza requirements vacíos."""
    cli.new_iteration()
    
    output = mock_stdout.getvalue()
    assert "cannot be empty" in output or "❌" in output


# ==================== IterationViewer Tests ====================

def test_iteration_viewer_initialization(temp_storage):
    """Test: IterationViewer se inicializa correctamente."""
    viewer = IterationViewer("TestProject", temp_storage)
    assert viewer.project_name == "TestProject"


@patch('sys.stdout', new_callable=StringIO)
def test_show_iteration_history_empty(mock_stdout, temp_storage):
    """Test: show_iteration_history con proyecto vacío."""
    viewer = IterationViewer("TestProject", temp_storage)
    
    viewer.show_iteration_history()
    
    output = mock_stdout.getvalue()
    assert "No iterations" in output or "0" in output


@patch('sys.stdout', new_callable=StringIO)
def test_show_iteration_history_with_iterations(mock_stdout, temp_storage, sample_iteration):
    """Test: show_iteration_history muestra iteraciones correctamente."""
    # ✅ CORRECCIÓN: save_iteration solo recibe el objeto iteration
    temp_storage.save_iteration(sample_iteration)
    
    viewer = IterationViewer("TestProject", temp_storage)
    viewer.show_iteration_history()
    
    output = mock_stdout.getvalue()
    assert "TestProject" in output
    assert "1" in output  # Número de iteración


@patch('sys.stdout', new_callable=StringIO)
def test_show_iteration_details(mock_stdout, temp_storage, sample_iteration):
    """Test: show_iteration_details muestra detalles correctamente."""
    # ✅ CORRECCIÓN: save_iteration solo recibe el objeto iteration
    temp_storage.save_iteration(sample_iteration)
    
    viewer = IterationViewer("TestProject", temp_storage)
    viewer.show_iteration_details(1)
    
    output = mock_stdout.getvalue()
    assert "Iteration 1" in output or "#1" in output
    assert "85" in output  # Score


@patch('sys.stdout', new_callable=StringIO)
def test_show_iteration_details_not_found(mock_stdout, temp_storage):
    """Test: show_iteration_details con iteración inexistente."""
    viewer = IterationViewer("TestProject", temp_storage)
    
    with pytest.raises(FileNotFoundError):
        viewer.show_iteration_details(999)


@patch('sys.stdout', new_callable=StringIO)
def test_show_iteration_result(mock_stdout, temp_storage):
    """Test: show_iteration_result muestra resultado correctamente."""
    result = IterationResult(
        iteration=1,
        project_name="TestProject",
        analysis={'architecture': {'pattern': 'microservices'}},
        codegen={'components': ['api', 'database']},
        validation={'overall_score': 90, 'quality_score': 85, 'issues': []},
        timestamp=datetime.now()
    )
    
    viewer = IterationViewer("TestProject", temp_storage)
    viewer.show_iteration_result(result)
    
    output = mock_stdout.getvalue()
    assert "90" in output  # Score


def test_determine_iteration_type_initial(sample_iteration):
    """Test: determine_iteration_type para primera iteración."""
    viewer = IterationViewer("TestProject", None)
    
    # ✅ CORRECCIÓN: Pasar un objeto Iteration real
    iteration_type = viewer._determine_iteration_type(sample_iteration)
    assert iteration_type == "Initial"


def test_calculate_trend_improving(temp_storage, sample_iteration, sample_iteration_2):
    """Test: calculate_trend detecta mejora."""
    viewer = IterationViewer("TestProject", temp_storage)
    
    # ✅ CORRECCIÓN: _calculate_trend espera objetos Iteration, no enteros
    # Crear una tercera iteración con score más alto
    state3 = ProjectState(
        project_name="TestProject",
        iteration=3,
        parent_iteration=2,
        outputs={'validation': {'overall_score': 95}}
    )
    iteration3 = Iteration(
        project_name="TestProject",
        iteration_number=3,
        state=state3,
        decisions=[],
        created_at=datetime.now(),
        duration_seconds=0.0,
        phase_durations={},
        final_scores={}
    )
    
    trend = viewer._calculate_trend([sample_iteration, sample_iteration_2, iteration3])
    assert "Improving" in trend or "📈" in trend


def test_calculate_trend_declining(temp_storage, sample_iteration, sample_iteration_2):
    """Test: calculate_trend detecta declive."""
    viewer = IterationViewer("TestProject", temp_storage)
    
    # ✅ CORRECCIÓN: Crear iteraciones con scores decrecientes
    state3 = ProjectState(
        project_name="TestProject",
        iteration=3,
        parent_iteration=2,
        outputs={'validation': {'overall_score': 80}}
    )
    iteration3 = Iteration(
        project_name="TestProject",
        iteration_number=3,
        state=state3,
        decisions=[],
        created_at=datetime.now(),
        duration_seconds=0.0,
        phase_durations={},
        final_scores={}
    )
    
    # Orden inverso para simular declive
    trend = viewer._calculate_trend([sample_iteration_2, sample_iteration, iteration3])
    assert "Declining" in trend or "📉" in trend


# ==================== DiffViewer Tests ====================

def test_diff_viewer_initialization(temp_storage):
    """Test: DiffViewer se inicializa correctamente."""
    diff_viewer = DiffViewer("TestProject", temp_storage)
    assert diff_viewer.project_name == "TestProject"


def test_show_diff_invalid_mode(temp_storage, sample_iteration):
    """Test: show_diff con modo inválido."""
    # ✅ CORRECCIÓN: save_iteration solo recibe el objeto iteration
    temp_storage.save_iteration(sample_iteration)
    
    diff_viewer = DiffViewer("TestProject", temp_storage)
    
    # El código mejorado lanza ValueError para modos inválidos
    with pytest.raises(ValueError, match="Invalid mode"):
        diff_viewer.show_diff(1, 1, mode="invalid")

def test_show_diff_not_found(temp_storage):
    """Test: show_diff con iteración inexistente."""
    diff_viewer = DiffViewer("TestProject", temp_storage)
    
    with pytest.raises(FileNotFoundError):
        diff_viewer.show_diff(1, 999)


# ==================== Integration Tests ====================

@patch('builtins.input', side_effect=['2', '', '7'])  # View History, Enter, Exit
@patch('sys.stdout', new_callable=StringIO)
def test_cli_integration_view_history(mock_stdout, mock_input, cli, sample_iteration):
    """Test: Flujo completo view history."""
    # ✅ CORRECCIÓN: save_iteration solo recibe el objeto iteration
    cli.storage.save_iteration(sample_iteration)
    
    cli.run()
    
    output = mock_stdout.getvalue()
    assert "ITERATION HISTORY" in output or "History" in output


@patch('builtins.input', side_effect=['3', '1', '', '7'])  # View Iteration, #1, Enter, Exit
@patch('sys.stdout', new_callable=StringIO)
def test_cli_integration_view_iteration(mock_stdout, mock_input, cli, sample_iteration):
    """Test: Flujo completo view iteration."""
    # ✅ CORRECCIÓN: save_iteration solo recibe el objeto iteration
    cli.storage.save_iteration(sample_iteration)
    
    cli.run()
    
    output = mock_stdout.getvalue()
    assert "VIEW ITERATION" in output or "Iteration" in output


@patch('builtins.input', side_effect=['4', '1', '1', '', '7'])  # Compare, #1, #1, Enter, Exit
@patch('sys.stdout', new_callable=StringIO)
def test_cli_integration_compare(mock_stdout, mock_input, cli, sample_iteration):
    """Test: Flujo completo compare iterations."""
    # ✅ CORRECCIÓN: save_iteration solo recibe el objeto iteration
    cli.storage.save_iteration(sample_iteration)
    
    cli.run()
    
    output = mock_stdout.getvalue()
    # Debe mostrar mensaje sobre comparar con sí misma
    assert "COMPARE" in output or "Cannot compare" in output
        
