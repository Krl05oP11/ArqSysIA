# 🔧 FIXES PRIORITARIOS: ArqSysIA v1.0.0

**Tipo:** Mejoras técnicas específicas
**Prioridad:** Alta para robustez
**Tiempo estimado:** 2-3 horas adicionales

---

## 🎯 OBJETIVO

Este documento contiene mejoras técnicas específicas de código que aumentarán la robustez de ArqSysIA v1.0.0. Estos fixes son **opcionales pero recomendados** para un release más sólido.

---

## 1️⃣ VALIDACIÓN DE INPUTS

### 1.1 Validar Requirements Vacíos

**Archivo:** `arqsysia/cli/main.py`
**Línea:** ~250-280 (método `_get_requirements`)

**Problema actual:**
- No valida si requirements están vacíos
- Podría generar iteración sin sentido

**Fix recomendado:**
```python
def _get_requirements(self) -> Optional[str]:
    """Obtiene requirements del usuario con validación."""
    self.console.print("\n[bold cyan]📝 Enter your system requirements:[/bold cyan]")
    self.console.print("[dim]Type your requirements (end with 'END' on a new line):[/dim]")

    lines = []
    line_count = 0
    max_lines = 1000  # Límite razonable

    while True:
        try:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
            line_count += 1

            if line_count >= max_lines:
                self.console.print(f"[yellow]⚠ Maximum lines reached ({max_lines})[/yellow]")
                break

        except EOFError:
            break
        except KeyboardInterrupt:
            self.console.print("\n[yellow]⚠ Input cancelled[/yellow]")
            return None

    requirements = "\n".join(lines)

    # NUEVO: Validar que no esté vacío
    if not requirements.strip():
        self.console.print("[red]❌ Requirements cannot be empty[/red]")
        return None

    # NUEVO: Validar longitud mínima
    if len(requirements.strip()) < 10:
        self.console.print("[yellow]⚠ Requirements seem too short (< 10 chars)[/yellow]")
        confirm = self._confirm("Continue anyway?")
        if not confirm:
            return None

    # Mostrar resumen
    word_count = len(requirements.split())
    self.console.print(f"\n[dim]Requirements: {line_count} lines, {word_count} words[/dim]")

    return requirements
```

**Beneficio:**
- Previene iteraciones sin requirements
- Alerta sobre inputs sospechosamente cortos

---

### 1.2 Sanitizar Nombres de Proyecto

**Archivo:** `arqsysia/cli/main.py`
**Línea:** ~100-120 (método `__init__`)

**Problema actual:**
- Validación básica pero podría ser más robusta
- Caracteres especiales podrían causar problemas

**Fix recomendado:**
```python
def __init__(self, project_name: str, storage: Optional[FileStorage] = None):
    """
    Inicializa el CLI para un proyecto.

    Args:
        project_name: Nombre del proyecto
        storage: Storage backend (opcional)
    """
    # MEJORADO: Validación más robusta
    if not project_name or not project_name.strip():
        raise ValueError("Project name cannot be empty")

    # NUEVO: Lista de caracteres inválidos
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\0']
    for char in invalid_chars:
        if char in project_name:
            raise ValueError(
                f"Project name cannot contain '{char}'. "
                f"Invalid characters: {', '.join(invalid_chars)}"
            )

    # NUEVO: Validar longitud
    if len(project_name) > 100:
        raise ValueError("Project name is too long (max 100 chars)")

    # NUEVO: Validar que no empiece/termine con espacios
    if project_name != project_name.strip():
        raise ValueError("Project name cannot start/end with spaces")

    # NUEVO: Advertir sobre nombres reservados
    reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'LPT1']  # Windows
    if project_name.upper() in reserved_names:
        raise ValueError(f"'{project_name}' is a reserved name")

    self.project_name = project_name
    self.storage = storage or FileStorage()
    # ... resto del código ...
```

**Beneficio:**
- Previene directory traversal
- Evita problemas con nombres reservados (Windows)
- Mejor experiencia de usuario

---

### 1.3 Validar Feedback en Continue Last

**Archivo:** `arqsysia/cli/main.py`
**Línea:** ~450-500 (método `continue_last_iteration`)

**Problema actual:**
- No valida si feedback está vacío

**Fix recomendado:**
```python
def continue_last_iteration(self):
    """Continúa desde la última iteración con feedback del usuario."""
    try:
        iterations = self._list_iterations()
        if not iterations:
            self.console.print("[yellow]⚠ No iterations found. Create a new iteration first.[/yellow]")
            return

        last_iteration = iterations[-1]

        # Mostrar resumen
        self.console.print(f"\n[bold cyan]📋 Continue from Iteration {last_iteration}[/bold cyan]")
        # ... mostrar detalles ...

        # Obtener feedback
        self.console.print("\n[bold cyan]💬 Provide feedback for refinement:[/bold cyan]")
        self.console.print("[dim]What would you like to improve? (end with 'END'):[/dim]")

        feedback_lines = []
        while True:
            try:
                line = input()
                if line.strip().upper() == "END":
                    break
                feedback_lines.append(line)
            except (EOFError, KeyboardInterrupt):
                self.console.print("\n[yellow]⚠ Input cancelled[/yellow]")
                return

        feedback = "\n".join(feedback_lines)

        # NUEVO: Validar feedback
        if not feedback.strip():
            self.console.print("[yellow]⚠ No feedback provided[/yellow]")
            confirm = self._confirm("Continue without feedback? (will generate similar architecture)")
            if not confirm:
                return
            feedback = None  # Explícitamente None
        else:
            # Mostrar resumen de feedback
            self.console.print(f"\n[dim]Feedback: {len(feedback_lines)} lines[/dim]")

        # Confirmar
        confirm = self._confirm(f"Continue from iteration {last_iteration} with this feedback?")
        if not confirm:
            return

        # ... resto del código ...
```

**Beneficio:**
- Usuario consciente de que puede continuar sin feedback
- Previene iteraciones sin cambios significativos

---

## 2️⃣ MANEJO DE ERRORES

### 2.1 Mejorar Manejo de Iteraciones Corruptas

**Archivo:** `arqsysia/storage/file_storage.py`
**Línea:** ~80-120 (método `load_iteration`)

**Problema actual:**
- Error genérico podría no ser claro

**Fix recomendado:**
```python
def load_iteration(self, project_name: str, iteration_number: int) -> Optional[Iteration]:
    """
    Carga una iteración desde disco.

    Args:
        project_name: Nombre del proyecto
        iteration_number: Número de iteración

    Returns:
        Iteration o None si no existe

    Raises:
        ValueError: Si el archivo está corrupto
        RuntimeError: Si hay error de I/O
    """
    iteration_path = self._get_iteration_path(project_name, iteration_number)

    if not iteration_path.exists():
        return None

    try:
        with open(iteration_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Convertir data a Iteration
        iteration = Iteration(**data)
        return iteration

    except json.JSONDecodeError as e:
        # MEJORADO: Error más específico
        raise ValueError(
            f"Iteration {iteration_number} file is corrupted.\n"
            f"File: {iteration_path}\n"
            f"Error: {e}\n"
            f"Suggestion: Delete the corrupted file or restore from backup."
        )

    except (TypeError, KeyError, ValidationError) as e:
        # NUEVO: Manejar schema inválido
        raise ValueError(
            f"Iteration {iteration_number} has invalid format.\n"
            f"File: {iteration_path}\n"
            f"Error: {e}\n"
            f"Suggestion: File may be from older version. Check CHANGELOG for migrations."
        )

    except PermissionError as e:
        # NUEVO: Manejar permisos
        raise RuntimeError(
            f"Permission denied reading iteration {iteration_number}.\n"
            f"File: {iteration_path}\n"
            f"Suggestion: Check file permissions."
        )

    except Exception as e:
        # Catch-all para errores inesperados
        raise RuntimeError(
            f"Unexpected error loading iteration {iteration_number}.\n"
            f"File: {iteration_path}\n"
            f"Error: {type(e).__name__}: {e}"
        )
```

**Beneficio:**
- Errores más claros y accionables
- Sugerencias de solución para el usuario

---

### 2.2 Agregar Retry Logic en Export

**Archivo:** `arqsysia/cli/file_exporter.py`
**Línea:** ~150-200 (método `export_iteration`)

**Problema actual:**
- Si export falla, no hay retry

**Fix recomendado:**
```python
def export_iteration(
    self,
    iteration: Iteration,
    export_technical_docs: bool = True,
    export_source_code: bool = True,
    max_retries: int = 3
) -> bool:
    """
    Exporta una iteración a disco con retry logic.

    Args:
        iteration: Iteración a exportar
        export_technical_docs: Exportar docs técnicos
        export_source_code: Exportar código fuente
        max_retries: Número máximo de reintentos

    Returns:
        True si éxito, False si falla
    """
    for attempt in range(1, max_retries + 1):
        try:
            # Crear directorio de exportación
            export_dir = self._get_export_dir(
                iteration.project_name,
                iteration.iteration_number
            )
            export_dir.mkdir(parents=True, exist_ok=True)

            # Exportar archivos
            if export_technical_docs:
                self._export_technical_docs(iteration, export_dir)

            if export_source_code:
                self._export_source_code(iteration, export_dir)

            # Generar README
            self._generate_readme(iteration, export_dir)

            return True  # Éxito

        except PermissionError as e:
            if attempt < max_retries:
                # Retry después de 1 segundo
                time.sleep(1)
                continue
            else:
                print(f"❌ Export failed: Permission denied after {max_retries} attempts")
                print(f"   Directory: {export_dir}")
                return False

        except OSError as e:
            if attempt < max_retries and e.errno == 28:  # ENOSPC: No space left
                print(f"⚠ Disk full. Attempt {attempt}/{max_retries}")
                time.sleep(2)
                continue
            else:
                print(f"❌ Export failed: {e}")
                return False

        except Exception as e:
            print(f"❌ Unexpected error during export: {type(e).__name__}: {e}")
            return False

    return False  # Todos los reintentos fallaron
```

**Beneficio:**
- Más robusto ante errores temporales
- Mejor experiencia de usuario

---

## 3️⃣ LOGGING Y DEBUGGING

### 3.1 Agregar Logging Opcional

**Archivo:** `arqsysia/utils/logger.py` (NUEVO)

**Crear nuevo archivo:**
```python
"""
Logging utilities para ArqSysIA.
"""
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

def setup_logger(
    name: str = "arqsysia",
    log_level: int = logging.INFO,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Configura logger para ArqSysIA.

    Args:
        name: Nombre del logger
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
        log_file: Path para archivo de log (opcional)

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Evitar duplicados
    if logger.handlers:
        return logger

    # Formato
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler para consola (solo WARNING+)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler para archivo (todo)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

def get_logger(name: str = "arqsysia") -> logging.Logger:
    """Obtiene logger existente o crea uno nuevo."""
    return logging.getLogger(name)
```

**Usar en código crítico:**
```python
# arqsysia/core/iterative_orchestrator.py
from arqsysia.utils.logger import get_logger

class IterativeOrchestrator:
    def __init__(self, ...):
        # ...
        self.logger = get_logger("arqsysia.orchestrator")

    def run_iteration(self, ...):
        self.logger.info(f"Starting iteration {iteration_number} for {project_name}")

        try:
            # ... código existente ...
            self.logger.info("Analyzer phase completed successfully")

        except Exception as e:
            self.logger.error(f"Analyzer phase failed: {e}", exc_info=True)
            raise
```

**Beneficio:**
- Debugging más fácil
- Trazabilidad de errores
- No interfiere con UX (solo WARNING+ en consola)

---

### 3.2 Agregar Debug Mode

**Archivo:** `arqsysia/cli/main.py`

**Agregar opción de debug:**
```python
def main():
    """Entry point para CLI."""
    parser = argparse.ArgumentParser(description="ArqSysIA - AI Architecture Assistant")
    parser.add_argument("project_name", help="Nombre del proyecto")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--log-file", type=str, help="Path to log file")

    args = parser.parse_args()

    # Setup logging
    if args.debug or args.log_file:
        from arqsysia.utils.logger import setup_logger
        log_level = logging.DEBUG if args.debug else logging.INFO
        log_file = Path(args.log_file) if args.log_file else None
        setup_logger(log_level=log_level, log_file=log_file)

    try:
        cli = ArqSysiaCLI(args.project_name)
        cli.run()
    except Exception as e:
        if args.debug:
            raise  # Mostrar traceback completo
        else:
            print(f"❌ Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
```

**Uso:**
```bash
# Normal
arqsysia MyProject

# Debug mode (muestra traceback completo)
arqsysia MyProject --debug

# Con log file
arqsysia MyProject --log-file ~/arqsysia.log
```

**Beneficio:**
- Debugging más fácil durante desarrollo
- Usuarios pueden generar logs para reportar bugs

---

## 4️⃣ PERFORMANCE

### 4.1 Lazy Loading de Iteraciones

**Archivo:** `arqsysia/cli/main.py`
**Línea:** ~200-230 (método `view_history`)

**Problema actual:**
- Carga todas las iteraciones completas en memoria

**Fix recomendado:**
```python
def view_history(self):
    """Muestra historial de iteraciones (solo metadata)."""
    try:
        # MEJORADO: Solo cargar metadata, no iteraciones completas
        iterations = self._list_iterations()

        if not iterations:
            self.console.print("[yellow]⚠ No iterations found[/yellow]")
            return

        # Crear tabla con metadata ligera
        table = Table(title=f"📚 Iteration History - {self.project_name}")
        table.add_column("#", style="cyan")
        table.add_column("Date", style="green")
        table.add_column("Duration", style="yellow")
        table.add_column("Score", style="magenta")
        table.add_column("Status", style="blue")

        for iter_num in iterations:
            # NUEVO: Cargar solo metadata, no todo el Iteration
            metadata = self._load_iteration_metadata(iter_num)

            if metadata:
                table.add_row(
                    str(iter_num),
                    metadata['created_at'][:10],  # Solo fecha
                    f"{metadata.get('duration_seconds', 0):.0f}s",
                    str(metadata.get('final_scores', {}).get('overall', '-')),
                    metadata.get('status', 'unknown')
                )

        self.console.print(table)

    except Exception as e:
        self.console.print(f"[red]❌ Error loading history: {e}[/red]")
```

**Agregar método auxiliar:**
```python
def _load_iteration_metadata(self, iteration_number: int) -> Optional[dict]:
    """
    Carga solo metadata de una iteración (no todo el objeto).

    Más rápido que cargar Iteration completo.
    """
    try:
        iteration_path = self.storage.base_path / self.project_name / "iterations" / f"iteration_{iteration_number:03d}.json"

        if not iteration_path.exists():
            return None

        # Leer JSON pero no parsear todo
        with open(iteration_path, 'r') as f:
            data = json.load(f)

        # Retornar solo campos necesarios
        return {
            'created_at': data.get('created_at', ''),
            'duration_seconds': data.get('duration_seconds', 0),
            'final_scores': data.get('final_scores', {}),
            'status': data.get('status', 'unknown')
        }

    except Exception:
        return None
```

**Beneficio:**
- View History es instantáneo incluso con 100+ iteraciones
- Reduce uso de memoria

---

## 5️⃣ SEGURIDAD

### 5.1 Validar Paths en Export

**Archivo:** `arqsysia/cli/file_exporter.py`

**Problema actual:**
- Podría haber directory traversal si iteration contiene paths maliciosos

**Fix recomendado:**
```python
def _export_technical_docs(self, iteration: Iteration, export_dir: Path):
    """Exporta documentos técnicos con validación de paths."""
    docs_dir = export_dir / "technical_docs"
    docs_dir.mkdir(exist_ok=True)

    # Obtener outputs de validation
    validation = iteration.state.outputs.get('validation', {})

    # Documentos a exportar
    docs = {
        'architecture.md': validation.get('architecture_analysis', ''),
        'components.md': validation.get('component_breakdown', ''),
        'database_design.md': validation.get('database_design', ''),
        'validation_report.md': validation.get('validation_report', '')
    }

    for filename, content in docs.items():
        # NUEVO: Validar filename
        if not self._is_safe_filename(filename):
            print(f"⚠ Skipping unsafe filename: {filename}")
            continue

        # NUEVO: Validar que path resuelto está dentro de docs_dir
        file_path = (docs_dir / filename).resolve()
        if not self._is_subpath(file_path, docs_dir):
            print(f"⚠ Skipping path outside export dir: {filename}")
            continue

        # Escribir archivo
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

def _is_safe_filename(self, filename: str) -> bool:
    """Valida que filename no contiene caracteres peligrosos."""
    dangerous = ['..', '/', '\\', '\0', '<', '>', ':', '"', '|', '?', '*']
    return not any(char in filename for char in dangerous)

def _is_subpath(self, path: Path, parent: Path) -> bool:
    """Valida que path está dentro de parent."""
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False
```

**Beneficio:**
- Previene directory traversal
- Previene sobrescritura de archivos críticos

---

## 📋 RESUMEN DE FIXES

| # | Fix | Archivo | Prioridad | Tiempo |
|---|-----|---------|-----------|--------|
| 1.1 | Validar requirements vacíos | main.py | Alta | 15 min |
| 1.2 | Sanitizar nombres de proyecto | main.py | Alta | 20 min |
| 1.3 | Validar feedback | main.py | Media | 15 min |
| 2.1 | Mejorar manejo de corruptos | file_storage.py | Alta | 20 min |
| 2.2 | Retry logic en export | file_exporter.py | Media | 20 min |
| 3.1 | Agregar logging opcional | logger.py (nuevo) | Baja | 30 min |
| 3.2 | Debug mode | main.py | Baja | 15 min |
| 4.1 | Lazy loading iteraciones | main.py | Media | 25 min |
| 5.1 | Validar paths en export | file_exporter.py | Alta | 20 min |

**Total:** ~3 horas

---

## 🎯 PRIORIZACIÓN RECOMENDADA

### CRÍTICO (Implementar para v1.0.0):
- ✅ 1.1: Validar requirements vacíos
- ✅ 1.2: Sanitizar nombres de proyecto
- ✅ 2.1: Mejorar manejo de corruptos
- ✅ 5.1: Validar paths en export

**Subtotal:** ~1.25 horas

### IMPORTANTE (Implementar si hay tiempo):
- 🔶 1.3: Validar feedback
- 🔶 2.2: Retry logic en export
- 🔶 4.1: Lazy loading iteraciones

**Subtotal:** ~1 hora

### NICE-TO-HAVE (Pueden ir a v1.0.1):
- 🔹 3.1: Logging opcional
- 🔹 3.2: Debug mode

**Subtotal:** ~45 min

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### Antes de Implementar
- [ ] Leer todo este documento
- [ ] Backup del código actual
- [ ] Crear branch: `git checkout -b fixes/v1.0-improvements`

### Durante Implementación
- [ ] Implementar fixes uno por uno
- [ ] Ejecutar tests después de cada fix: `pytest tests/ -v`
- [ ] Probar manualmente cada fix
- [ ] Commitear cada fix por separado

### Después de Implementar
- [ ] Todos los tests pasan (96/96)
- [ ] Testing manual de nuevas validaciones
- [ ] Actualizar CHANGELOG con fixes
- [ ] Merge a develop: `git checkout develop && git merge fixes/v1.0-improvements`

---

## 🧪 TESTING DE FIXES

### Test 1.1: Requirements Vacíos
```bash
arqsysia TestValidation
# Opción 1: New Iteration
# Presionar: END (sin escribir nada)
# Esperado: Error "Requirements cannot be empty"
```

### Test 1.2: Nombres Inválidos
```bash
# Debe fallar
arqsysia "Mi/Proyecto"
arqsysia "Proyecto*Test"
arqsysia "../../etc/passwd"

# Debe funcionar
arqsysia "MiProyecto"
arqsysia "Project_123"
```

### Test 2.1: Archivo Corrupto
```bash
# Crear archivo corrupto
echo '{"corrupto": "json' > projects/Test/iterations/iteration_001.json

# Intentar cargar
arqsysia Test
# Opción 3: View Iteration #1
# Esperado: Error claro con sugerencias
```

### Test 5.1: Path Traversal
```python
# Test automatizado
def test_safe_filename():
    exporter = FileExporter()

    assert exporter._is_safe_filename("normal.md") == True
    assert exporter._is_safe_filename("../etc/passwd") == False
    assert exporter._is_safe_filename("sub/dir.md") == False
    assert exporter._is_safe_filename("file\0.md") == False
```

---

## 📝 COMMIT MESSAGES SUGERIDOS

```bash
# Fix 1.1
git commit -m "Add validation for empty requirements in CLI

- Validate requirements are not empty before creating iteration
- Warn if requirements are suspiciously short (< 10 chars)
- Improve user experience with clear error messages"

# Fix 1.2
git commit -m "Improve project name validation

- Add comprehensive character validation
- Prevent directory traversal attacks
- Block reserved Windows names (CON, PRN, etc)
- Validate length and whitespace
- Better error messages with specific guidance"

# Fix 2.1
git commit -m "Enhance error handling for corrupted iterations

- Add specific error types for different failure modes
- Provide actionable suggestions in error messages
- Handle JSON decode errors, schema validation, and permissions
- Improve user experience when files are corrupted"

# Fix 5.1
git commit -m "Add path validation in file export

- Prevent directory traversal in export filenames
- Validate all exported paths stay within export directory
- Add _is_safe_filename() and _is_subpath() validators
- Enhance security of export system"
```

---

## 🎓 NOTAS FINALES

### Estos fixes son opcionales
- v1.0.0 puede lanzarse sin ellos
- Aumentan robustez y experiencia de usuario
- Pueden implementarse en v1.0.1 si no hay tiempo

### Si tienes poco tiempo
- Implementa solo los CRÍTICOS (~1.25 horas)
- El resto puede ir a v1.0.1 como mejoras

### Si tienes más tiempo
- Implementa todos (~3 horas)
- Tendrás un release más sólido

---

**Recomendación final:** Implementa al menos los 4 fixes CRÍTICOS antes de v1.0.0.

---

**Última actualización:** 2025-11-07
**Versión del documento:** 1.0
