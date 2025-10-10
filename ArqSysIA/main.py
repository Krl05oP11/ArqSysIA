#!/usr/bin/env python3
"""
ArqSysIA - CLI Principal

Aplicación de escritorio para diseño y definición de arquitecturas de software.
"""

import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.markdown import Markdown
from rich import box

from arqsysia.core.state import ProjectState
from arqsysia.core.orchestrator import create_orchestrator
from arqsysia.outputs.generator import create_generator

console = Console()


def print_banner():
    """Muestra el banner de bienvenida."""
    banner_text = """
[bold cyan]╔════════════════════════════════════════════════════════════════════════════════╗
║                                                                                   ║
║                  █████╗ ██████╗  ██████╗ ███████╗██╗   ██╗███████╗██╗ █████╗      ║
║                 ██╔══██╗██╔══██╗██╔═══██╗██╔════╝╚██╗ ██╔╝██╔════╝██║██╔══██╗     ║
║                 ███████║██████╔╝██║   ██║███████╗ ╚████╔╝ ███████╗██║███████║    
║                 ██╔══██║██╔══██╗██║▄▄ ██║╚════██║  ╚██╔╝  ╚════██║██║██╔══██║   ║
║                 ██║  ██║██║  ██║╚██████╔╝███████║   ██║   ███████║██║██║  ██║   ║
║                 ╚═╝  ╚═╝╚═╝  ╚═╝ ╚══▀▀═╝ ╚══════╝   ╚═╝   ╚══════╝╚═╝╚═╝  ╚═╝   ║
║                                                                                 ║
║              Arquitecto de Sistemas con Inteligencia Artificial                 ║
║                            MVP v0.1                                             ║
╚════════════════════════════════════════════════════════════════════════════════╝[/bold cyan]
    """
    console.print(banner_text)
    console.print()


def print_welcome():
    """Muestra mensaje de bienvenida."""
    welcome = Panel(
        "[bold white]Bienvenido a ArqSysIA[/bold white]\n\n"
        "Esta herramienta te ayudará a:\n"
        "• Analizar y documentar requerimientos\n"
        "• Diseñar arquitecturas de sistemas\n"
        "• Generar estructuras de código\n"
        "• Validar diseños arquitecturales\n"
        "• Crear documentación técnica profesional\n\n"
        "[dim]Desarrollado en Libertador San Martín, Entre Ríos, Argentina 🇦🇷[/dim]",
        title="💡 Información",
        border_style="cyan",
        box=box.ROUNDED
    )
    console.print(welcome)
    console.print()


def get_project_requirements() -> tuple[str, str]:
    """
    Solicita el nombre del proyecto y sus requerimientos.
    
    Returns:
        Tupla (project_name, requirements)
    """
    console.print("[bold yellow]📋 Configuración del Proyecto[/bold yellow]")
    console.print()
    
    # Nombre del proyecto
    console.print("[dim]El nombre del proyecto se usará para identificar archivos y documentación.[/dim]")
    console.print("[dim]Ejemplos: 'TiendaOnline', 'SistemaInventario', 'AppDelivery'[/dim]")
    console.print()
    
    project_name = Prompt.ask(
        "[cyan]Nombre del proyecto[/cyan]",
        default="MiProyecto"
    )
    
    console.print()
    
    # Requerimientos
    console.print("[cyan]¿Cómo deseas proporcionar los requerimientos?[/cyan]")
    console.print("  1. Ingresar manualmente (editor)")
    console.print("  2. Cargar desde archivo")
    console.print()
    
    choice = Prompt.ask(
        "Selecciona opción",
        choices=["1", "2"],
        default="1"
    )
    
    requirements = ""
    
    if choice == "1":
        console.print()
        console.print("[yellow]Ingresa los requerimientos del proyecto:[/yellow]")
        console.print("[dim]Escribe los requerimientos y presiona Ctrl+D (Linux/Mac) o Ctrl+Z (Windows) cuando termines[/dim]")
        console.print()
        
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            requirements = "\n".join(lines)
        
        if not requirements.strip():
            console.print("[red]⚠️  No se ingresaron requerimientos. Usando ejemplo por defecto.[/red]")
            requirements = "Sistema de gestión genérico con usuarios, autenticación y dashboard."
    
    else:
        console.print()
        file_path = Prompt.ask(
            "[cyan]Ruta al archivo de requerimientos[/cyan]",
            default="requirements.txt"
        )
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                requirements = f.read()
            console.print(f"[green]✅ Archivo cargado: {len(requirements)} caracteres[/green]")
        except FileNotFoundError:
            console.print(f"[red]❌ Archivo no encontrado: {file_path}[/red]")
            console.print("[yellow]Usando requerimientos por defecto[/yellow]")
            requirements = "Sistema de gestión genérico con usuarios, autenticación y dashboard."
    
    console.print()
    
    # Confirmar
    console.print(Panel(
        f"[bold]Proyecto:[/bold] {project_name}\n"
        f"[bold]Requerimientos:[/bold] {len(requirements)} caracteres\n\n"
        f"[dim]{requirements[:200]}...[/dim]" if len(requirements) > 200 else f"[dim]{requirements}[/dim]",
        title="📝 Resumen",
        border_style="green",
        box=box.ROUNDED
    ))
    console.print()
    
    confirmed = Confirm.ask("¿Deseas continuar con esta configuración?", default=True)
    
    if not confirmed:
        console.print("[yellow]Operación cancelada[/yellow]")
        sys.exit(0)
    
    return project_name, requirements


def run_pipeline_with_progress(project_name: str, requirements: str):
    """
    Ejecuta el pipeline mostrando progress bars.
    
    Args:
        project_name: Nombre del proyecto
        requirements: Requerimientos del sistema
    """
    console.print()
    console.print("[bold cyan]🚀 Iniciando Pipeline de Análisis[/bold cyan]")
    console.print()
    
    # Crear orchestrator (sin modo interactivo, ya que la CLI es interactiva)
    orchestrator = create_orchestrator(interactive=False)
    
    # Crear progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        transient=False
    ) as progress:
        
        # Task principal
        main_task = progress.add_task("[cyan]Pipeline completo...", total=100)
        
        # Fase 1: Analyzer
        progress.update(main_task, description="[yellow]📐 Fase 1: Analyzer (esto puede tomar ~5 min)...")
        analyzer_task = progress.add_task("[yellow]Analizando arquitectura...", total=100)
        
        # Simular progreso (ya que no tenemos hooks reales en el orchestrator)
        import time
        for i in range(0, 101, 10):
            progress.update(analyzer_task, completed=i)
            time.sleep(0.2)
        
        # Ejecutar analyzer (esto tomará el tiempo real)
        try:
            state = ProjectState(
                project_name=project_name,
                original_requirements=requirements
            )
            state = orchestrator.analyzer.run(state)
            progress.update(analyzer_task, completed=100, description="[green]✅ Analyzer completado")
            progress.update(main_task, completed=33)
        except Exception as e:
            console.print(f"[red]❌ Error en Analyzer: {e}[/red]")
            raise
        
        console.print()
        
        # Fase 2: CodeGen
        progress.update(main_task, description="[yellow]💻 Fase 2: CodeGen (esto puede tomar ~14 min)...")
        codegen_task = progress.add_task("[yellow]Generando código...", total=100)
        
        for i in range(0, 101, 10):
            progress.update(codegen_task, completed=i)
            time.sleep(0.2)
        
        try:
            state = orchestrator.codegen.run(state)
            progress.update(codegen_task, completed=100, description="[green]✅ CodeGen completado")
            progress.update(main_task, completed=66)
        except Exception as e:
            console.print(f"[red]❌ Error en CodeGen: {e}[/red]")
            raise
        
        console.print()
        
        # Fase 3: Validator
        progress.update(main_task, description="[yellow]🔍 Fase 3: Validator (esto puede tomar ~1 min)...")
        validator_task = progress.add_task("[yellow]Validando diseño...", total=100)
        
        for i in range(0, 101, 10):
            progress.update(validator_task, completed=i)
            time.sleep(0.1)
        
        try:
            state = orchestrator.validator.run(state)
            progress.update(validator_task, completed=100, description="[green]✅ Validator completado")
            progress.update(main_task, completed=100, description="[green]✅ Pipeline completado")
        except Exception as e:
            console.print(f"[red]❌ Error en Validator: {e}[/red]")
            raise
        
        console.print()
    
    # Guardar estado
    console.print("[cyan]💾 Guardando estado...[/cyan]")
    orchestrator.state_manager.save_state(state)
    console.print("[green]✅ Estado guardado[/green]")
    console.print()
    
    return state


def show_results_summary(state):
    """
    Muestra resumen de resultados con tablas.
    
    Args:
        state: ProjectState con todos los resultados
    """
    console.print()
    console.print("[bold cyan]📊 RESUMEN DE RESULTADOS[/bold cyan]")
    console.print()
    
    # Tabla de scores
    validation_results = state.get_output("validation_results", {})
    
    if validation_results:
        table = Table(title="Scores de Validación", box=box.ROUNDED)
        table.add_column("Área", style="cyan", no_wrap=True)
        table.add_column("Score", justify="center", style="yellow")
        table.add_column("Estado", justify="center")
        
        arch = validation_results.get("architecture", {})
        code = validation_results.get("code", {})
        sec = validation_results.get("security", {})
        
        arch_score = arch.get("architecture_score", 0)
        arch_status = "✅ Bueno" if arch_score >= 7 else "⚠️ Mejorable" if arch_score >= 5 else "❌ Requiere atención"
        table.add_row("Arquitectura", f"{arch_score}/10", arch_status)
        
        if code:
            code_score = code.get("code_quality_score", 0)
            code_status = "✅ Bueno" if code_score >= 7 else "⚠️ Mejorable" if code_score >= 5 else "❌ Requiere atención"
            table.add_row("Calidad de Código", f"{code_score}/10", code_status)
        
        sec_score = sec.get("security_score", 0)
        sec_status = "✅ Bueno" if sec_score >= 7 else "⚠️ Mejorable" if sec_score >= 5 else "❌ Requiere atención"
        table.add_row("Seguridad", f"{sec_score}/10", sec_status)
        
        console.print(table)
        console.print()
    
    # Información de outputs
    analysis = state.get_output("analysis") or state.get_output("architecture_analysis") or {}
    
    info_table = Table(title="Información del Proyecto", box=box.ROUNDED)
    info_table.add_column("Concepto", style="cyan")
    info_table.add_column("Valor", style="white")
    
    pattern = analysis.get('architectural_pattern') or analysis.get('architecture_pattern', 'N/A')
    info_table.add_row("Patrón Arquitectural", pattern)
    
    components = analysis.get('main_components') or analysis.get('components', [])
    info_table.add_row("Componentes Principales", str(len(components)))
    
    file_structure = state.get_output("file_structure")
    if file_structure:
        info_table.add_row("Estructura Generada", "✅ Sí")
    
    console.print(info_table)
    console.print()


def generate_documents(state):
    """
    Genera documentos finales.
    
    Args:
        state: ProjectState
    """
    console.print("[bold cyan]📄 Generando Documentos Finales[/bold cyan]")
    console.print()
    
    with console.status("[yellow]Generando documentos...[/yellow]", spinner="dots"):
        generator = create_generator()
        docs = generator.generate_all(state)
    
    console.print("[green]✅ Documentos generados[/green]")
    console.print()
    
    # Tabla de documentos
    table = Table(title="Documentos Generados", box=box.ROUNDED)
    table.add_column("Documento", style="cyan")
    table.add_column("Ruta", style="white")
    table.add_column("Tamaño", justify="right", style="yellow")
    
    for doc_type, filepath in docs.items():
        size = filepath.stat().st_size
        size_str = f"{size:,} bytes"
        
        # Nombres amigables
        friendly_names = {
            "mvp_proposal": "Propuesta de MVP",
            "technical_architecture": "Arquitectura Técnica",
            "validation_report": "Reporte de Validación"
        }
        
        name = friendly_names.get(doc_type, doc_type)
        table.add_row(name, str(filepath), size_str)
    
    console.print(table)
    console.print()


def main():
    """Función principal de la CLI."""
    
    # Banner y bienvenida
    print_banner()
    print_welcome()
    
    # Obtener configuración
    project_name, requirements = get_project_requirements()
    
    # Confirmación final
    console.print()
    estimated_time = Panel(
        "[yellow]⏱️  Tiempo estimado total: ~20 minutos[/yellow]\n\n"
        "• Analyzer:  ~5 min  (DeepSeek-R1-32B)\n"
        "• CodeGen:   ~14 min (Qwen2.5-Coder-32B)\n"
        "• Validator: ~1 min  (DeepSeek-R1-14B)",
        title="⏰ Duración",
        border_style="yellow",
        box=box.ROUNDED
    )
    console.print(estimated_time)
    console.print()
    
    ready = Confirm.ask("¿Listo para comenzar?", default=True)
    
    if not ready:
        console.print("[yellow]Operación cancelada[/yellow]")
        return
    
    try:
        # Ejecutar pipeline
        state = run_pipeline_with_progress(project_name, requirements)
        
        # Mostrar resumen
        show_results_summary(state)
        
        # Generar documentos
        generate_documents(state)
        
        # Mensaje final
        console.print()
        success_panel = Panel(
            "[bold green]✨ ¡Análisis completado exitosamente! ✨[/bold green]\n\n"
            f"Proyecto: [cyan]{project_name}[/cyan]\n"
            "Estado guardado en: [yellow]output/[/yellow]\n"
            "Documentos generados en: [yellow]output/[/yellow]\n\n"
            "[dim]Puedes revisar los documentos markdown generados[/dim]",
            title="🎉 ¡Éxito!",
            border_style="green",
            box=box.DOUBLE
        )
        console.print(success_panel)
        console.print()
        
    except KeyboardInterrupt:
        console.print()
        console.print("[yellow]⚠️  Operación interrumpida por el usuario[/yellow]")
        sys.exit(1)
    
    except Exception as e:
        console.print()
        console.print(f"[red]❌ Error durante la ejecución: {e}[/red]")
        import traceback
        console.print("[dim]" + traceback.format_exc() + "[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    main()
    
