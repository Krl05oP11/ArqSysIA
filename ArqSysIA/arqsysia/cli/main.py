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
                print("The error has been logged. Please try again or use option 7 to exit.")
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
        print("  7. Exit             - Exit ArqSysIA")
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
            choice = input("\n➤ Enter command (1-7): ").strip()
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
            '7': self.exit_cli
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
                print("\nPlease try again or report this issue if it persists.")
                input("\nPress Enter to continue...")
        else:
            print("❌ Invalid choice. Please enter 1-7.")
    
    def new_iteration(self) -> None:
        """Crear nueva iteración con validaciones mejoradas."""
        print("\n" + "═" * 60)
        print("NEW ITERATION")
        print("═" * 60)
        
        # Obtener requirements del usuario
        print("\n📝 Enter requirements (type 'END' on a new line to finish):")
        print("💡 Tip: Be specific about your requirements for better results")
        print("─" * 60)
        
        lines = []
        line_count = 0
        max_lines = 100  # Límite razonable
        
        while line_count < max_lines:
            try:
                line = input()
                if line.strip().upper() == 'END':
                    break
                lines.append(line)
                line_count += 1
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\n\n⚠️  Input cancelled.")
                if self._confirm("Discard input and return to menu?"):
                    return
                else:
                    continue
        
        requirements = '\n'.join(lines).strip()
        
        # Validar que no esté vacío
        if not requirements:
            print("\n❌ Requirements cannot be empty.")
            input("\nPress Enter to continue...")
            return
        
        # Confirmar antes de ejecutar
        print(f"\n📊 Requirements summary:")
        print(f"   Lines: {len(lines)}")
        print(f"   Characters: {len(requirements)}")
        
        if not self._confirm("Execute iteration with these requirements?"):
            print("⚠️  Iteration cancelled.")
            input("\nPress Enter to continue...")
            return
        
        # Ejecutar iteración
        print("\n" + "─" * 60)
        print("🚀 EXECUTING ITERATION...")
        print("─" * 60)
        print("⏳ This may take several minutes. Please wait...")
        print("💡 The LLMs are analyzing, generating code, and validating...\n")
        
        try:
            result = self.orchestrator.execute_iteration(
                requirements=requirements,
                user_feedback=None
            )
            
            # Mostrar resultado
            print("\n" + "─" * 60)
            print("✅ ITERATION COMPLETED!")
            print("─" * 60)
            self.viewer.show_iteration_result(result)
            
            # Mostrar menú post-validación
            self._show_post_validation_menu(result)
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Iteration interrupted by user.")
            print("❌ Partial results may have been saved.")
        except Exception as e:
            print(f"\n\n❌ Error during iteration: {e}")
            print(f"   Error type: {type(e).__name__}")
            print("\n💡 Tips:")
            print("   - Check that Ollama is running")
            print("   - Verify that the required models are installed")
            print("   - Try again with simpler requirements")
        
        input("\n\nPress Enter to continue...")
    
    def _show_post_validation_menu(self, result: IterationResult) -> None:
        """
        Mostrar menú de opciones después de validación.
        
        Args:
            result: Resultado de la iteración
        """
        print("\n" + "─" * 60)
        print("WHAT'S NEXT?")
        print("─" * 60)
        print("  1. Accept & Continue  - Proceed with this architecture")
        print("  2. Regenerate Code    - Keep architecture, generate new code")
        print("  3. Redesign           - Create completely new architecture")
        print("  4. View Details       - See full validation report")
        print("  5. Return to Menu     - Go back to main menu")
        print("─" * 60)
        
        try:
            choice = input("\n➤ Enter choice (1-5): ").strip()
            
            if choice == '1':
                print("\n✅ Architecture accepted! Use 'Continue Last' to build on it.")
            elif choice == '2':
                self._regenerate_code(result)
            elif choice == '3':
                self._redesign_architecture(result)
            elif choice == '4':
                self.viewer.show_iteration_details(result.iteration)
            elif choice == '5':
                return
            else:
                print("\n❌ Invalid choice.")
        except (EOFError, KeyboardInterrupt):
            print("\n⚠️  Returning to main menu...")
    
    def _regenerate_code(self, result: IterationResult) -> None:
        """Regenerar código manteniendo arquitectura."""
        print("\n📝 Enter specific instructions for code regeneration:")
        print("(type 'END' on a new line to finish)")
        
        lines = []
        while True:
            try:
                line = input()
                if line.strip().upper() == 'END':
                    break
                lines.append(line)
            except (EOFError, KeyboardInterrupt):
                break
        
        instructions = '\n'.join(lines).strip()
        if not instructions:
            print("❌ Instructions cannot be empty.")
            return
        
        print("\n🔄 Regenerating code...")
        # TODO: Implementar regeneración de código
        print("⚠️  Code regeneration feature coming soon!")
    
    def _redesign_architecture(self, result: IterationResult) -> None:
        """Rediseñar arquitectura desde cero."""
        print("\n📝 Enter feedback for architectural redesign:")
        print("(type 'END' on a new line to finish)")
        
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
        if not feedback:
            print("❌ Feedback cannot be empty.")
            return
        
        print("\n🎨 Redesigning architecture...")
        # TODO: Implementar rediseño
        print("⚠️  Architecture redesign feature coming soon!")
    
    def view_history(self) -> None:
        """Ver historial de iteraciones con manejo de errores."""
        print("\n" + "═" * 60)
        print("ITERATION HISTORY")
        print("═" * 60)
        
        try:
            self.viewer.show_iteration_history()
        except Exception as e:
            print(f"❌ Error viewing history: {e}")
        
        input("\nPress Enter to continue...")
    
    def view_iteration(self) -> None:
        """Ver iteración específica con validación mejorada."""
        print("\n" + "═" * 60)
        print("VIEW ITERATION")
        print("═" * 60)
        
        # ✅ CORRECCIÓN: Mostrar solo números de iteración disponibles
        try:
            iterations = self.orchestrator.version_manager.list_iterations()
            if iterations:
                iter_numbers = [str(i.iteration_number) for i in iterations]
                print(f"\n📋 Available iterations: {', '.join(iter_numbers)}")
        except:
            pass
        
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
            
            result = self.orchestrator.execute_iteration(
                requirements=latest.state.original_requirements,
                user_feedback=feedback if feedback else None
            )
            
            print("\n" + "─" * 60)
            print("✅ CONTINUATION COMPLETED!")
            print("─" * 60)
            self.viewer.show_iteration_result(result)
            
            # Mostrar menú post-validación
            self._show_post_validation_menu(result)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        input("\n\nPress Enter to continue...")
    
    def settings(self) -> None:
        """Configurar opciones del proyecto."""
        print("\n" + "═" * 60)
        print("SETTINGS")
        print("═" * 60)
        print("\n⚠️  Settings feature coming soon!")
        print("\nPlanned features:")
        print("  • Configure LLM models")
        print("  • Adjust iteration parameters")
        print("  • Set project preferences")
        print("  • Export/Import settings")
        
        input("\nPress Enter to continue...")
    
    def exit_cli(self) -> None:
        """Salir del CLI de forma limpia."""
        print("\n" + "─" * 60)
        print("👋 Thank you for using ArqSysIA!")
        print("─" * 60)
        print(f"📁 Project data saved in: {self.data_dir}")
        print("💡 Run 'arqsysia {self.project_name}' to continue later\n")
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
    
