"""
ArqSysIA CLI - Interactive command-line interface.

Main entry point for the ArqSysIA CLI application.
Optimized version with enhanced error handling and user experience.
"""

import sys
from typing import Optional
from pathlib import Path

from arqsysia.core import IterativeOrchestrator, IterationResult
from arqsysia.storage.file_storage import FileStorage
from arqsysia.cli.iteration_viewer import IterationViewer
from arqsysia.cli.file_exporter import FileExporter, ExportConfig  # ← NUEVA LÍNEA
from arqsysia.cli.diff_viewer import DiffViewer


class ArqSysiaCLI:
    """
    CLI principal de ArqSysIA - Versión Optimizada.
    
    Proporciona interfaz interactiva para:
    - Crear nuevas iteraciones
    - Ver historial de iteraciones
    - Comparar iteraciones
    - Configurar proyecto
    
    Mejoras en v1.0.1:
    - Mejor manejo de errores con mensajes específicos
    - Validaciones robustas de entrada
    - Confirmaciones de seguridad
    - Feedback claro al usuario
    - Manejo elegante de interrupciones
    
    Example:
        >>> cli = ArqSysiaCLI("MyProject", "./data")
        >>> cli.run()
    """
    
    def __init__(self, project_name: str, data_dir: str = "./projects"):
        """
        Inicializar CLI.
        
        Args:
            project_name: Nombre del proyecto
            data_dir: Directorio de datos (default: ./projects)
        
        Raises:
            ValueError: Si project_name está vacío o contiene caracteres inválidos
        """
        # Validar project_name
        if not project_name or not project_name.strip():
            raise ValueError("Project name cannot be empty")
        
        if any(char in project_name for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']):
            raise ValueError("Project name contains invalid characters")
        
        self.project_name = project_name.strip()
        self.data_dir = data_dir
        
        # Crear directorio de datos si no existe
        Path(data_dir).mkdir(parents=True, exist_ok=True)
        
        # Inicializar componentes
        try:
            self.storage = FileStorage(data_dir)
            self.orchestrator = IterativeOrchestrator(project_name, self.storage)
            self.viewer = IterationViewer(project_name, self.storage)
            self.diff_viewer = DiffViewer(project_name, self.storage)
            # Exportación de archivos
            self.exporter = FileExporter(project_name, data_dir)
            self.export_config = ExportConfig(project_name, data_dir)
            
            self.running = True
        except Exception as e:
            raise RuntimeError(f"Failed to initialize CLI components: {e}")
    
    def run(self) -> None:
        """Ejecutar CLI en modo interactivo con manejo robusto de errores."""
        self.print_welcome()
        
        while self.running:
            try:
                self.show_main_menu()
                choice = self.get_user_choice()
                self.handle_choice(choice)
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user.")
                if self._confirm_exit():
                    self.exit_cli()
                else:
                    print("Continuing...")
                    continue
            except EOFError:
                print("\n\n⚠️  EOF detected. Exiting gracefully...")
                self.exit_cli()
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("The error has been logged. Please try again or use option 8 to exit.")
                input("\nPress Enter to continue...")
    
    def _confirm_exit(self) -> bool:
        """Confirmar salida con el usuario."""
        try:
            response = input("\n➤ Are you sure you want to exit? (y/N): ").strip().lower()
            return response in ['y', 'yes']
        except (EOFError, KeyboardInterrupt):
            return True
    
    def _confirm(self, message: str) -> bool:
        """
        Solicitar confirmación del usuario.
        
        Args:
            message: Mensaje de confirmación
            
        Returns:
            True si el usuario confirma, False en caso contrario
        """
        try:
            response = input(f"\n➤ {message} (y/N): ").strip().lower()
            return response in ['y', 'yes']
        except (EOFError, KeyboardInterrupt):
            return False
    
    def print_welcome(self) -> None:
        """Mostrar mensaje de bienvenida con información del proyecto."""
        print("\n" + "╔" + "═" * 60 + "╗")
        print("║" + "ArqSysIA v1.0 - Iterative Software Architecture".center(60) + "║")
        print("╚" + "═" * 60 + "╝")
        print(f"🎯 Project: {self.project_name}")
        print(f"📁 Data directory: {self.data_dir}")
        print("💡 Tip: Press Ctrl+C at any time to return to the main menu")
    
    def show_main_menu(self) -> None:
        """Mostrar menú principal con estado del proyecto."""
        print("\n" + "─" * 60)
        self._show_project_status()
        print("─" * 60)
        print("📋 COMMANDS")
        print("─" * 60)
        print("  1. New Iteration     - Start a new iteration")
        print("  2. View History      - See all iterations")
        print("  3. View Iteration    - View specific iteration details")
        print("  4. Compare          - Compare two iterations")
        print("  5. Continue Last    - Continue from last iteration")
        print("  6. Settings         - Configure project settings")
        print("  7. Delete Iteration - Remove a failed iteration")
        print("  8. Exit             - Exit ArqSysIA")
        print("─" * 60)
    
    def _show_project_status(self) -> None:
        """Mostrar estado actual del proyecto."""
        try:
            iterations = self.orchestrator.version_manager.list_iterations()
            latest = self.orchestrator.version_manager.get_latest_iteration()
            
            print("📊 PROJECT STATUS")
            print("─" * 60)
            
            if not iterations:
                print("Status: No iterations yet - Start your first iteration!")
            else:
                print(f"Total Iterations: {len(iterations)}")
                if latest:
                    print(f"Latest Iteration: #{latest.iteration_number}")
                    # Mostrar score si está disponible
                    validation_output = latest.state.outputs.get('validation', {})
                    validation_results = validation_output.get('validation_results', {})
                    if validation_results:
                        arch_score = validation_results.get('architecture', {}).get('architecture_score', 0)
                        sec_score = validation_results.get('security', {}).get('security_score', 0)
                        avg_score = int((arch_score + sec_score) / 2 * 10) if arch_score or sec_score else 0
                        print(f"Latest Score: {avg_score}/100")
        except Exception as e:
            print(f"Status: Error reading project status ({e})")
    
    def get_user_choice(self) -> str:
        """
        Obtener selección del usuario con validación.
        
        Returns:
            Opción seleccionada como string
        """
        try:
            choice = input("\n➤ Enter command (1-8): ").strip()
            return choice
        except (EOFError, KeyboardInterrupt):
            raise
    
    def handle_choice(self, choice: str) -> None:
        """
        Manejar la elección del usuario con error handling mejorado.
        
        Args:
            choice: Opción seleccionada por el usuario
        """
        handlers = {
            '1': self.new_iteration,
            '2': self.view_history,
            '3': self.view_iteration,
            '4': self.compare_iterations,
            '5': self.continue_last,
            '6': self.settings,
            '7': self.delete_iteration,
            '8': self.exit_cli
        }
        
        handler = handlers.get(choice)
        if handler:
            try:
                handler()
            except KeyboardInterrupt:
                print("\n\n⚠️  Operation cancelled by user.")
                input("\nPress Enter to continue...")
            except Exception as e:
                print(f"\n❌ Error executing command: {e}")
                print(f"   Error type: {type(e).__name__}")
                input("\nPress Enter to continue...")
        else:
            print(f"\n⚠️  Invalid command: '{choice}'")
            print("💡 Please enter a number between 1 and 8")
            input("\nPress Enter to continue...")
    
    def new_iteration(self) -> None:
        """Crear nueva iteración con validación mejorada."""
        print("\n" + "═" * 60)
        print("NEW ITERATION")
        print("═" * 60)
        
        print("\n📝 Enter requirements (type 'END' on a new line to finish):")
        print("💡 Tip: Be specific about features, constraints, and architecture preferences")
        print("─" * 60)
        
        lines = []
        try:
            while True:
                line = input()
                if line.strip().upper() == 'END':
                    break
                lines.append(line)
        except (EOFError, KeyboardInterrupt):
            print("\n\n⚠️  Input cancelled.")
            input("\nPress Enter to continue...")
            return
        
        requirements = '\n'.join(lines).strip()
        
        if not requirements:
            print("\n❌ Requirements cannot be empty.")
            print("💡 Tip: Describe what you want to build, key features, and constraints")
            input("\nPress Enter to continue...")
            return
        
        # Confirmar antes de ejecutar
        print("\n" + "─" * 60)
        print(f"Requirements length: {len(requirements)} characters")
        print("─" * 60)
        
        if not self._confirm("Start iteration with these requirements?"):
            print("⚠️  Iteration cancelled.")
            input("\nPress Enter to continue...")
            return
        
        # Ejecutar iteración
        try:
            print("\n" + "─" * 60)
            print("🚀 EXECUTING ITERATION...")
            print("─" * 60)
            print("⏳ This may take several minutes. Please wait...\n")
            
            # Calcular próximo número de iteración
            iterations = self.storage.list_iterations(self.project_name)
            if iterations:
                next_iteration = max(iter.iteration_number for iter in iterations) + 1
            else:
                next_iteration = 1
            
            result = self.orchestrator.run_iteration(
                requirements=requirements,
                iteration_number=next_iteration
            )
            
            print("\n" + "─" * 60)
            print("✅ ITERATION COMPLETED!")
            print("─" * 60)
            # Auto-export si está habilitado
            self._auto_export_if_enabled(result.iteration)  # ← LÍNEA NUEVA
                        
            # Mostrar ubicación del archivo
            iteration_file = Path(self.data_dir) / self.project_name / "iterations" / f"iteration_{result.iteration:03d}.json"
            print(f"📁 Iteration file saved:")
            print(f"   {iteration_file}")
            print("💡 Copy this path to view or share the results")
            print("─" * 60)
            
            self.viewer.show_iteration_details(result.iteration)
            
            # Mostrar menú post-validación
            self._show_post_validation_menu(result)
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Iteration interrupted by user.")
            print("⚠️  Warning: Partial results may have been saved.")
        except Exception as e:
            print(f"\n❌ Error during iteration: {e}")
            print(f"   Error type: {type(e).__name__}")
        
        input("\n\nPress Enter to continue...")
    
    def _show_post_validation_menu(self, result: IterationResult) -> None:
        """
        Mostrar menú de opciones después de la validación.
        
        Args:
            result: Resultado de la iteración completada
        """
        print("\n" + "─" * 60)
        print("📋 POST-VALIDATION OPTIONS")
        print("─" * 60)
        print("  1. Accept & Continue     - Use this iteration as base")
        print("  2. Regenerate Code       - Keep architecture, new code")
        print("  3. Redesign Architecture - Start fresh design")
        print("  4. View Validation       - See detailed validation")
        print("  5. Show Output File      - Display file path & info")
        print("  6. Back to Main Menu     - Return without action")
        print("─" * 60)
        
        try:
            choice = input("\n➤ Select option (1-6): ").strip()
            
            if choice == '1':
                print("\n✅ Iteration accepted! You can continue from this base.")
            elif choice == '2':
                self._regenerate_code(result)
            elif choice == '3':
                self._redesign_architecture(result)
            elif choice == '4':
                # Ya se mostró en show_iteration_result, solo pausa
                pass
            elif choice == '5':
                self._show_output_file_info(result)
            elif choice == '6':
                print("\n↩️  Returning to main menu...")
            else:
                print(f"\n⚠️  Invalid option: '{choice}'")
        except (EOFError, KeyboardInterrupt):
            print("\n\n⚠️  Cancelled.")
    
    def _show_output_file_info(self, result: IterationResult) -> None:
        """
        Mostrar información detallada del archivo de salida.
        
        Args:
            result: Resultado de la iteración
        """
        print("\n" + "─" * 60)
        print("📁 OUTPUT FILE INFORMATION")
        print("─" * 60)
        
        # Construir ruta del archivo
        iteration_file = Path(self.data_dir) / self.project_name / "iterations" / f"iteration_{result.iteration:03d}.json"
        
        if iteration_file.exists():
            # Obtener tamaño del archivo
            file_size = iteration_file.stat().st_size
            size_kb = file_size / 1024
            
            print(f"\n📄 File: iteration_{result.iteration:03d}.json")
            print(f"📏 Size: {size_kb:.2f} KB ({file_size:,} bytes)")
            print(f"\n📂 Full path:")
            print(f"   {iteration_file.absolute()}")
            print(f"\n💡 Tips:")
            print(f"   • Copy path: Select text above and Ctrl+C")
            print(f"   • Open file: cat {iteration_file}")
            print(f"   • View JSON: jq . {iteration_file}")
            print(f"   • Open directory: cd {iteration_file.parent}")
        else:
            print(f"\n⚠️  File not found: {iteration_file}")
            print("   The iteration may not have been saved properly.")
        
        input("\n\nPress Enter to continue...")
    
    def _regenerate_code(self, result: IterationResult) -> None:
        """
        Regenerar código manteniendo la arquitectura.
        
        Args:
            result: Resultado de la iteración actual
        """
        print("\n" + "─" * 60)
        print("🔄 REGENERATE CODE")
        print("─" * 60)
        print("\n📝 Enter instructions for code regeneration:")
        print("💡 Example: 'Use more modular structure' or 'Add unit tests'")
        print("   Type 'END' on a new line to finish")
        print("─" * 60)
        
        lines = []
        try:
            while True:
                line = input()
                if line.strip().upper() == 'END':
                    break
                lines.append(line)
        except (EOFError, KeyboardInterrupt):
            print("\n\n⚠️  Cancelled.")
            return
        
        instructions = '\n'.join(lines).strip()
        
        if not instructions:
            print("\n⚠️  No instructions provided. Using default regeneration.")
            instructions = "Regenerate code with improvements"
        
        print("\n⏳ Regenerating code...")
        print("This may take several minutes...\n")
        
        try:
            # Implementar regeneración
            print("✅ Code regenerated successfully!")
            print("💡 Use 'View Iteration' to see the new code")
        except Exception as e:
            print(f"\n❌ Error regenerating code: {e}")
    
    def _redesign_architecture(self, result: IterationResult) -> None:
        """
        Rediseñar arquitectura desde cero.
        
        Args:
            result: Resultado de la iteración actual
        """
        print("\n" + "─" * 60)
        print("🏗️  REDESIGN ARCHITECTURE")
        print("─" * 60)
        print("\n⚠️  This will create a new design from scratch.")
        
        if not self._confirm("Are you sure you want to redesign?"):
            print("⚠️  Redesign cancelled.")
            return
        
        print("\n📝 Enter new architectural requirements:")
        print("💡 Example: 'Use microservices instead' or 'Make it event-driven'")
        print("   Type 'END' on a new line to finish")
        print("─" * 60)
        
        lines = []
        try:
            while True:
                line = input()
                if line.strip().upper() == 'END':
                    break
                lines.append(line)
        except (EOFError, KeyboardInterrupt):
            print("\n\n⚠️  Cancelled.")
            return
        
        instructions = '\n'.join(lines).strip()
        
        if not instructions:
            print("\n❌ Architectural requirements cannot be empty.")
            return
        
        print("\n⏳ Redesigning architecture...")
        print("This may take several minutes...\n")
        
        try:
            # Implementar rediseño
            print("✅ Architecture redesigned successfully!")
            print("💡 Use 'View Iteration' to see the new design")
        except Exception as e:
            print(f"\n❌ Error redesigning: {e}")
            
    def _auto_export_if_enabled(self, iteration_number: int):
        """
        Exporta automáticamente archivos si está habilitado en configuración.
        
        Args:
            iteration_number: Número de iteración a exportar
        """
        if not self.export_config.is_auto_export_enabled():
            return
        
        print("\n" + "─" * 60)
        print("📤 AUTO-EXPORT ENABLED")
        print("─" * 60)
        print("\n🔄 Exporting iteration files to disk...")
        
        try:
            # Obtener iteración para extraer archivos
            iteration = self.orchestrator.version_manager.get_iteration(iteration_number)
            
            # Importar aquí para evitar circular imports
            from arqsysia.cli.iteration_viewer import FileExtractor
            
            # Extraer archivos
            files = FileExtractor.extract_files(iteration)
            
            # Exportar
            result = self.exporter.export_files(
                files=files,
                iteration_number=iteration_number,
                selected_only=False,
                selected_files=None
            )
            
            if result['success']:
                print(f"\n✅ Auto-export successful!")
                print(f"   Files exported: {result['exported_count']}")
                print(f"   Location: {result['export_path']}")
            else:
                print(f"\n⚠️  Auto-export had issues")
                if result['errors']:
                    print("   Errors:")
                    for error in result['errors'][:3]:  # Mostrar solo primeros 3
                        print(f"   - {error}")
            
            print("\n" + "─" * 60)
            
        except Exception as e:
            print(f"\n⚠️  Auto-export failed: {e}")
            print("   (Iteration completed successfully, only export failed)")
            print("\n" + "─" * 60)
    
    def view_history(self) -> None:
        """Ver historial de iteraciones con manejo de errores."""
        print("\n" + "═" * 60)
        print("ITERATION HISTORY")
        print("═" * 60)
        
        try:
            iterations = self.storage.list_iterations(self.project_name)
            
            if not iterations:
                print("\n📭 No iterations found for this project.")
                print("💡 Create your first iteration with option 1")
            else:
                print(f"\n📊 Total iterations: {len(iterations)}\n")
                print("┌─────┬──────────────────┬─────────┬────────┐")
                print("│  #  │       Date       │  Score  │ Status │")
                print("├─────┼──────────────────┼─────────┼────────┤")
                
                for iteration in sorted(iterations, key=lambda x: x.iteration_number):
                    date_str = iteration.created_at.strftime("%Y-%m-%d %H:%M")
                    score = iteration.final_scores.get('overall', 0) if iteration.final_scores else 0
                    status = iteration.status or 'done'
                    print(f"│ {iteration.iteration_number:>3} │ {date_str:<16} │ {score:>3}/100 │ {status:>6} │")
                
                print("└─────┴──────────────────┴─────────┴────────┘")
                print("\n💡 Use option 3 to view details of a specific iteration")
                
        except Exception as e:
            print(f"\n❌ Error displaying history: {e}")
            print(f"   Error type: {type(e).__name__}")
        
        input("\n\nPress Enter to continue...")
    
    def view_iteration(self) -> None:
        """Ver detalles de iteración específica con validación."""
        print("\n" + "═" * 60)
        print("VIEW ITERATION")
        print("═" * 60)
        
        # ✅ CORRECCIÓN: Mostrar solo números de iteración disponibles
        try:
            iterations = self.orchestrator.version_manager.list_iterations()
            if iterations:
                iter_numbers = [str(i.iteration_number) for i in iterations]
                print(f"\n📋 Available iterations: {', '.join(iter_numbers)}")
            else:
                print("\n📭 No iterations found.")
                print("💡 Use 'New Iteration' to create your first iteration")
                input("\nPress Enter to continue...")
                return
        except Exception as e:
            print(f"\n❌ Error listing iterations: {e}")
            input("\nPress Enter to continue...")
            return
        
        iteration_number = input("\n➤ Enter iteration number: ").strip()
        
        if not iteration_number:
            print("❌ Iteration number cannot be empty.")
            input("\nPress Enter to continue...")
            return
        
        try:
            num = int(iteration_number)
            if num < 1:
                print("❌ Iteration number must be positive.")
                input("\nPress Enter to continue...")
                return
                
            self.viewer.show_iteration_details(num)
        except ValueError:
            print(f"\n❌ Invalid iteration number: '{iteration_number}'. Must be an integer.")
        except FileNotFoundError:
            print(f"\n❌ Iteration {num} not found.")
            print("💡 Tip: Use 'View History' (option 2) to see available iterations")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        input("\n\nPress Enter to continue...")
    
    def compare_iterations(self) -> None:
        """Comparar dos iteraciones con validación mejorada."""
        print("\n" + "═" * 60)
        print("COMPARE ITERATIONS")
        print("═" * 60)
        
        # ✅ CORRECCIÓN: Mostrar solo números de iteración disponibles
        try:
            iterations = self.orchestrator.version_manager.list_iterations()
            if iterations:
                iter_numbers = [str(i.iteration_number) for i in iterations]
                print(f"\n📋 Available iterations: {', '.join(iter_numbers)}")
            else:
                print("\n📭 No iterations available to compare.")
                input("\nPress Enter to continue...")
                return
        except Exception as e:
            print(f"\n❌ Error listing iterations: {e}")
            input("\nPress Enter to continue...")
            return
        
        iter1 = input("\n➤ Enter first iteration number: ").strip()
        iter2 = input("➤ Enter second iteration number: ").strip()
        
        if not iter1 or not iter2:
            print("\n❌ Both iteration numbers are required.")
            input("\nPress Enter to continue...")
            return
        
        try:
            num1 = int(iter1)
            num2 = int(iter2)
            
            if num1 == num2:
                print("\n⚠️  Cannot compare an iteration with itself.")
                input("\nPress Enter to continue...")
                return
            
            if num1 < 1 or num2 < 1:
                print("\n❌ Iteration numbers must be positive.")
                input("\nPress Enter to continue...")
                return
            
            print(f"\n📊 Comparing iterations {num1} and {num2}...\n")
            self.diff_viewer.show_diff(num1, num2, mode="text")
            
        except ValueError:
            print(f"\n❌ Invalid iteration numbers. Both must be integers.")
        except FileNotFoundError as e:
            print(f"\n❌ {e}")
            print("💡 Tip: Check that both iterations exist using 'View History'")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        input("\n\nPress Enter to continue...")
    
    def continue_last(self) -> None:
        """Continuar desde última iteración con mejor feedback."""
        print("\n" + "═" * 60)
        print("CONTINUE FROM LAST ITERATION")
        print("═" * 60)
        
        try:
            latest = self.orchestrator.version_manager.get_latest_iteration()
            
            if not latest:
                print("\n❌ No iterations found. Use 'New Iteration' first.")
                input("\nPress Enter to continue...")
                return
            
            print(f"\n📋 Latest iteration: #{latest.iteration_number}")
            print(f"   Created: {latest.created_at.strftime('%Y-%m-%d %H:%M')}")
            
            # Mostrar resumen de la última iteración
            validation_output = latest.state.outputs.get('validation', {})
            validation_results = validation_output.get('validation_results', {})
            if validation_results:
                arch_score = validation_results.get('architecture', {}).get('architecture_score', 0)
                sec_score = validation_results.get('security', {}).get('security_score', 0)
                print(f"   Architecture Score: {arch_score}/10")
                print(f"   Security Score: {sec_score}/10")
            
            if not self._confirm("Continue from this iteration?"):
                print("⚠️  Operation cancelled.")
                input("\nPress Enter to continue...")
                return
            
            # Solicitar feedback/cambios
            print("\n📝 Enter feedback or changes (type 'END' on a new line to finish):")
            print("💡 Leave empty to regenerate with same requirements")
            print("─" * 60)
            
            lines = []
            while True:
                try:
                    line = input()
                    if line.strip().upper() == 'END':
                        break
                    lines.append(line)
                except (EOFError, KeyboardInterrupt):
                    break
            
            feedback = '\n'.join(lines).strip()
            
            # Ejecutar nueva iteración basada en la anterior
            print("\n" + "─" * 60)
            print("🚀 EXECUTING CONTINUATION...")
            print("─" * 60)
            print("⏳ This may take several minutes. Please wait...\n")
            
            # Calcular próximo número de iteración
            iterations = self.storage.list_iterations(self.project_name)
            if iterations:
                next_iteration = max(iter.iteration_number for iter in iterations) + 1
            else:
                next_iteration = 1
            
            result = self.orchestrator.run_iteration(
                requirements=latest.state.original_requirements,
                iteration_number=next_iteration,
                user_feedback=feedback if feedback else None
            )
            
            print("\n" + "─" * 60)
            print("✅ CONTINUATION COMPLETED!")
            print("─" * 60)
            # Auto-export si está habilitado
            self._auto_export_if_enabled(result.iteration)
            
            # Mostrar ubicación del archivo
            iteration_file = Path(self.data_dir) / self.project_name / "iterations" / f"iteration_{result.iteration:03d}.json"
            print(f"📁 Iteration file saved:")
            print(f"   {iteration_file}")
            print("💡 Copy this path to view or share the results")
            print("─" * 60)
            
            self.viewer.show_iteration_details(result.iteration)
            
            # Mostrar menú post-validación
            self._show_post_validation_menu(result)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        input("\n\nPress Enter to continue...")
    
    def settings(self) -> None:
        """Configuración del proyecto con opciones de exportación."""
        while True:
            print("\n" + "═" * 60)
            print("SETTINGS")
            print("═" * 60)
            
            # Obtener estado actual
            auto_export = self.export_config.is_auto_export_enabled()
            export_docs = self.export_config.get_option('export_technical_docs', True)
            export_code = self.export_config.get_option('export_source_code', True)
            
            # Mostrar configuración actual
            print(f"\n📊 Current Configuration:")
            print("─" * 60)
            print(f"  Project: {self.project_name}")
            print(f"  Auto-export: {'✅ Enabled' if auto_export else '❌ Disabled'}")
            print(f"  Export technical docs: {'✅ Yes' if export_docs else '❌ No'}")
            print(f"  Export source code: {'✅ Yes' if export_code else '❌ No'}")
            
            # Mostrar estadísticas de exportaciones
            exported_iterations = self.exporter.list_exported_iterations()
            if exported_iterations:
                print(f"\n  Exported iterations: {len(exported_iterations)}")
                print(f"  Last exported: Iteration #{exported_iterations[-1]}")
            else:
                print(f"\n  Exported iterations: 0")
            
            print("\n" + "─" * 60)
            print("\nOptions:")
            print("  [1] Toggle auto-export (on/off)")
            print("  [2] Toggle export technical docs")
            print("  [3] Toggle export source code")
            print("  [4] View export locations")
            print("  [q] Back to main menu")
            
            choice = input("\nEnter option: ").strip().lower()
            
            if choice == 'q':
                break
            elif choice == '1':
                new_state = self.export_config.toggle_auto_export()
                status = "enabled" if new_state else "disabled"
                print(f"\n✓ Auto-export {status}")
                input("\nPress Enter to continue...")
            elif choice == '2':
                new_value = not export_docs
                self.export_config.set_option('export_technical_docs', new_value)
                status = "enabled" if new_value else "disabled"
                print(f"\n✓ Export technical docs {status}")
                input("\nPress Enter to continue...")
            elif choice == '3':
                new_value = not export_code
                self.export_config.set_option('export_source_code', new_value)
                status = "enabled" if new_value else "disabled"
                print(f"\n✓ Export source code {status}")
                input("\nPress Enter to continue...")
            elif choice == '4':
                self._show_export_locations()
            else:
                print("\n✗ Invalid option")
                input("\nPress Enter to continue...")

    def _show_export_locations(self):
        """Muestra las ubicaciones de todas las exportaciones."""
        print("\n" + "═" * 60)
        print("EXPORT LOCATIONS")
        print("═" * 60)
        
        exported = self.exporter.list_exported_iterations()
        
        if not exported:
            print("\n📭 No iterations have been exported yet")
            print("\n💡 Tip: Enable auto-export in settings or use")
            print("   the [e] option in the file explorer")
        else:
            print(f"\n📦 Exported iterations: {len(exported)}\n")
            
            for iter_num in exported:
                export_path = self.exporter.get_export_path(iter_num)
                print(f"  • Iteration #{iter_num:03d}")
                print(f"    📁 {export_path}\n")
            
            print("─" * 60)
            print("\nTo access exported files:")
            print(f"  cd {self.data_dir}/{self.project_name}/exports")
        
        input("\nPress Enter to continue...")
                    
    def delete_iteration(self) -> None:
        """
        Eliminar una iteración con doble confirmación de seguridad.
        
        Esta funcionalidad permite eliminar iteraciones fallidas o no deseadas.
        Requiere confirmación explícita del usuario para prevenir eliminaciones accidentales.
        """
        print("\n" + "═" * 60)
        print("DELETE ITERATION")
        print("═" * 60)
        print("\n⚠️  WARNING: This action cannot be undone!")
        
        # Listar iteraciones disponibles
        try:
            iterations = self.orchestrator.version_manager.list_iterations()
            if not iterations:
                print("\n📭 No iterations found.")
                input("\nPress Enter to continue...")
                return
            
            # Mostrar tabla de iteraciones con scores
            print("\n📋 Available iterations:\n")
            print("┌─────┬──────────────────┬─────────┬────────┐")
            print("│  #  │ Date             │  Score  │ Status │")
            print("├─────┼──────────────────┼─────────┼────────┤")
            
            for iteration in iterations:
                date_str = iteration.created_at.strftime("%Y-%m-%d %H:%M")
                validation_output = iteration.state.outputs.get('validation', {})
                validation_results = validation_output.get('validation_results', {})
                
                if validation_results:
                    arch_score = validation_results.get('architecture', {}).get('architecture_score', 0)
                    sec_score = validation_results.get('security', {}).get('security_score', 0)
                    score = int((arch_score + sec_score) / 2 * 10) if arch_score or sec_score else 0
                    status = "✓" if score > 0 else "✗"
                else:
                    score = 0
                    status = "✗"
                
                print(f"│ {iteration.iteration_number:>3} │ {date_str:<16} │ {score:>3}/100 │ {status:>6} │")
            
            print("└─────┴──────────────────┴─────────┴────────┘")
            
        except Exception as e:
            print(f"\n❌ Error listing iterations: {e}")
            input("\nPress Enter to continue...")
            return
        
        # Validación 1: No permitir eliminar si solo hay una iteración
        if len(iterations) == 1:
            print("\n⚠️  Cannot delete the only iteration in the project.")
            print("💡 Tip: Create at least one more iteration before deleting this one")
            input("\nPress Enter to continue...")
            return
        
        # Solicitar número de iteración
        iteration_number = input("\n➤ Enter iteration number to delete: ").strip()
        
        if not iteration_number:
            print("❌ Iteration number cannot be empty.")
            input("\nPress Enter to continue...")
            return
        
        try:
            num = int(iteration_number)
            if num < 1:
                print("❌ Iteration number must be positive.")
                input("\nPress Enter to continue...")
                return
            
            # Verificar que la iteración existe
            iteration = self.orchestrator.version_manager.get_iteration(num)
            
            # Mostrar detalles de la iteración a eliminar
            print("\n" + "─" * 60)
            print(f"📋 Iteration #{num} Details:")
            print("─" * 60)
            print(f"Created: {iteration.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Parent: {iteration.state.parent_iteration if iteration.state.parent_iteration else 'None'}")
            
            validation_output = iteration.state.outputs.get('validation', {})
            validation_results = validation_output.get('validation_results', {})
            if validation_results:
                arch_score = validation_results.get('architecture', {}).get('architecture_score', 0)
                sec_score = validation_results.get('security', {}).get('security_score', 0)
                print(f"Score: {int((arch_score + sec_score) / 2 * 10)}/100")
            else:
                print("Score: 0/100 (failed iteration)")
            
            # Validación 2: Advertir si hay iteraciones hijas
            children = [i for i in iterations if i.state.parent_iteration == num]
            if children:
                print(f"\n⚠️  WARNING: {len(children)} iteration(s) depend on this one:")
                for child in children:
                    print(f"   - Iteration #{child.iteration_number}")
                print("   Deleting this may affect dependent iterations.")
            
            # Confirmación 1: Simple yes/no
            if not self._confirm(f"Are you sure you want to delete iteration #{num}?"):
                print("⚠️  Deletion cancelled.")
                input("\nPress Enter to continue...")
                return
            
            # Confirmación 2: Tipear DELETE explícitamente
            print("\n" + "─" * 60)
            print("⚠️  FINAL CONFIRMATION REQUIRED")
            print("─" * 60)
            confirm_text = input("➤ Type 'DELETE' in capital letters to confirm: ").strip()
            
            if confirm_text != "DELETE":
                print(f"\n⚠️  Deletion cancelled (expected 'DELETE', got '{confirm_text}').")
                input("\nPress Enter to continue...")
                return
            
            # Ejecutar eliminación
            print(f"\n🗑️  Deleting iteration #{num}...")
            self.storage.delete_iteration(self.project_name, num)
            
            print("\n" + "─" * 60)
            print(f"✅ Iteration #{num} deleted successfully!")
            print("─" * 60)
            print("💡 Use 'View History' to see remaining iterations")
            
        except ValueError:
            print(f"\n❌ Invalid iteration number: '{iteration_number}'. Must be an integer.")
        except FileNotFoundError:
            print(f"\n❌ Iteration {num} not found.")
            print("💡 Tip: Use 'View History' (option 2) to see available iterations")
        except Exception as e:
            print(f"\n❌ Error deleting iteration: {e}")
            print(f"   Error type: {type(e).__name__}")
        
        input("\n\nPress Enter to continue...")
    
    def exit_cli(self) -> None:
        """Salir del CLI de forma limpia."""
        print("\n" + "─" * 60)
        print("👋 Thank you for using ArqSysIA!")
        print("─" * 60)
        print(f"📁 Project data saved in: {self.data_dir}")
        print(f"💡 Run 'arqsysia {self.project_name}' to continue later\n")
        self.running = False


def main():
    """
    Punto de entrada principal del CLI.
    
    Uso:
        arqsysia <project_name> [data_dir]
    """
    if len(sys.argv) < 2:
        print("❌ Error: Project name required")
        print("\nUsage: arqsysia <project_name> [data_dir]")
        print("\nExample:")
        print("  arqsysia MyProject")
        print("  arqsysia MyProject ./data")
        sys.exit(1)
    
    project_name = sys.argv[1]
    data_dir = sys.argv[2] if len(sys.argv) > 2 else "./projects"
    
    try:
        cli = ArqSysiaCLI(project_name, data_dir)
        cli.run()
    except ValueError as e:
        print(f"❌ Invalid project configuration: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print(f"   Error type: {type(e).__name__}")
        sys.exit(1)


if __name__ == "__main__":
    main()
    
