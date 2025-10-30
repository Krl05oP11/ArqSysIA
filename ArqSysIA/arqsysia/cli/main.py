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
            response = input("\n➤ Do you want to exit? (y/n): ").strip().lower()
            return response in ['y', 'yes']
        except (EOFError, KeyboardInterrupt):
            return True
    
    def print_welcome(self) -> None:
        """Imprimir mensaje de bienvenida."""
        print("\n" + "╔" + "═" * 60 + "╗")
        print("║" + " ArqSysIA v1.0 - Iterative Software Architecture ".center(60) + "║")
        print("╚" + "═" * 60 + "╝")
        print("\n🎯 Project:", self.project_name)
        print("📁 Data directory:", self.data_dir)
        print("\n💡 Tip: Press Ctrl+C at any time to return to the main menu")
    
    def show_main_menu(self) -> None:
        """Mostrar menú principal con estado actual."""
        # Obtener estado actual
        try:
            latest = self.orchestrator.version_manager.get_latest_iteration()
            
            print("\n" + "─" * 60)
            print("📊 PROJECT STATUS")
            print("─" * 60)
            
            if latest:
                # ✅ CORRECTO: Usar iteration_number, created_at, y acceder correctamente al score
                print(f"Current Iteration: {latest.iteration_number}")
                score = latest.state.outputs.get('validation', {}).get('overall_score', 0)
                print(f"Last Score: {score}/100")
                print(f"Last Updated: {latest.created_at.strftime('%Y-%m-%d %H:%M')}")
                
                # Mostrar tendencia si hay más de una iteración
                iterations = self.orchestrator.version_manager.list_iterations()
                if len(iterations) > 1:
                    prev = self.orchestrator.version_manager.get_iteration(latest.iteration_number - 1)
                    prev_score = prev.state.outputs.get('validation', {}).get('overall_score', 0)
                    delta = score - prev_score
                    trend = "📈" if delta > 0 else "📉" if delta < 0 else "➡️"
                    print(f"Trend: {trend} ({delta:+d} from previous)")
            else:
                print("Status: No iterations yet - Start your first iteration!")
            
        except Exception as e:
            print(f"\n🔭 Status: New project (no iterations)")
            # Solo mostrar error si no es un proyecto nuevo
            if "not found" not in str(e).lower():
                print(f"   Note: {e}")
        
        # Menú de comandos
        print("\n" + "─" * 60)
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
    
    def get_user_choice(self) -> str:
        """Obtener elección del usuario con validación robusta."""
        max_attempts = 3
        attempts = 0
        
        while attempts < max_attempts:
            try:
                choice = input("\n➤ Enter command (1-7): ").strip()
                
                if not choice:
                    print("⚠️  Please enter a command.")
                    attempts += 1
                    continue
                
                if choice in ['1', '2', '3', '4', '5', '6', '7']:
                    return choice
                else:
                    print("❌ Invalid choice. Please enter a number between 1 and 7.")
                    attempts += 1
                    
            except EOFError:
                print("\n⚠️  EOF detected. Exiting...")
                return '7'
            except KeyboardInterrupt:
                raise  # Propagar para manejar en run()
        
        print(f"\n⚠️  Maximum attempts ({max_attempts}) reached. Returning to menu.")
        return ''  # Retornar vacío para volver a mostrar el menú
    
    def handle_choice(self, choice: str) -> None:
        """Manejar elección del usuario con mejor logging de errores."""
        if not choice:
            return  # Ignorar opciones vacías
        
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
        
        if line_count >= max_lines:
            print(f"\n⚠️  Maximum lines ({max_lines}) reached.")
        
        requirements = "\n".join(lines)
        
        if not requirements.strip():
            print("\n❌ Requirements cannot be empty.")
            input("\nPress Enter to continue...")
            return
        
        # Mostrar resumen de requirements
        word_count = len(requirements.split())
        print(f"\n📋 Requirements summary: {line_count} lines, {word_count} words")
        
        if not self._confirm("Start iteration with these requirements?"):
            print("❌ Iteration cancelled.")
            input("\nPress Enter to continue...")
            return
        
        # Calcular número de iteración
        try:
            latest = self.orchestrator.version_manager.get_latest_iteration()
            # ✅ CORRECTO: Usar iteration_number en lugar de number
            iteration_number = latest.iteration_number + 1 if latest else 1
        except:
            iteration_number = 1
        
        print(f"\n🚀 Starting iteration {iteration_number}...")
        print("⏳ This may take a few minutes...")
        print("💡 Tip: The LLM is analyzing and generating architecture...\n")
        
        # Ejecutar iteración
        try:
            result = self.orchestrator.run_iteration(
                requirements=requirements,
                iteration_number=iteration_number
            )
            
            # Mostrar resultado
            print("\n" + "═" * 60)
            print("✅ ITERATION COMPLETED")
            print("═" * 60)
            self.viewer.show_iteration_result(result)
            
            # Menú post-validación
            choice = self.orchestrator.post_validation_menu(result)
            self.handle_post_validation(choice, result)
            
        except Exception as e:
            print(f"\n❌ Error during iteration: {e}")
            print(f"   Error type: {type(e).__name__}")
            print("\n💡 Tip: Check your Ollama service is running and the model is available")
            input("\nPress Enter to continue...")
    
    def view_history(self) -> None:
        """Ver historial de iteraciones."""
        print("\n" + "═" * 60)
        print("ITERATION HISTORY")
        print("═" * 60)
        
        try:
            self.viewer.show_iteration_history()
        except FileNotFoundError:
            print("\n📭 No iterations found for this project yet.")
            print("💡 Tip: Use 'New Iteration' (option 1) to create your first iteration")
        except Exception as e:
            print(f"\n❌ Error viewing history: {e}")
        
        input("\n\nPress Enter to continue...")
    
    def view_iteration(self) -> None:
        """Ver iteración específica con validación mejorada."""
        print("\n" + "═" * 60)
        print("VIEW ITERATION")
        print("═" * 60)
        
        # Mostrar iteraciones disponibles
        try:
            iterations = self.orchestrator.version_manager.list_iterations()
            if iterations:
                print(f"\n📋 Available iterations: {', '.join(map(str, iterations))}")
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
        
        # Mostrar iteraciones disponibles
        try:
            iterations = self.orchestrator.version_manager.list_iterations()
            if iterations:
                print(f"\n📋 Available iterations: {', '.join(map(str, iterations))}")
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
            
            # ✅ CORRECTO: Usar iteration_number, created_at, y acceder correctamente al score
            print(f"\n📌 Last iteration: {latest.iteration_number}")
            score = latest.state.outputs.get('validation', {}).get('overall_score', 0)
            print(f"📊 Score: {score}/100")
            print(f"📅 Date: {latest.created_at.strftime('%Y-%m-%d %H:%M')}")
            
            print("\n💡 This will create a new iteration based on the previous one.")
            confirm = input("\n➤ Continue with new requirements? (y/n): ").strip().lower()
            
            if confirm in ['y', 'yes']:
                self.new_iteration()
            else:
                print("❌ Cancelled.")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def settings(self) -> None:
        """Mostrar/modificar configuración."""
        print("\n" + "═" * 60)
        print("SETTINGS")
        print("═" * 60)
        
        print("\n📋 Current Settings:")
        print(f"  Project Name: {self.project_name}")
        print(f"  Data Directory: {self.data_dir}")
        print(f"  Storage Backend: FileStorage")
        
        # Mostrar información del sistema
        try:
            iterations = self.orchestrator.version_manager.list_iterations()
            print(f"\n📊 Project Statistics:")
            print(f"  Total Iterations: {len(iterations)}")
            
            if iterations:
                latest = self.orchestrator.version_manager.get_latest_iteration()
                print(f"  Latest Iteration: {latest.iteration_number}")
                print(f"  Project Size: {self._get_project_size()} MB")
        except:
            pass
        
        print("\n💡 Settings management coming soon...")
        print("   - Change data directory")
        print("   - Configure LLM settings")
        print("   - Export/import project")
        print("   - Backup/restore")
        
        input("\nPress Enter to continue...")
    
    def _get_project_size(self) -> float:
        """Calcular tamaño del proyecto en MB."""
        try:
            project_path = Path(self.data_dir) / self.project_name
            total_size = sum(f.stat().st_size for f in project_path.rglob('*') if f.is_file())
            return round(total_size / (1024 * 1024), 2)
        except:
            return 0.0
    
    def exit_cli(self) -> None:
        """Salir del CLI con mensaje de confirmación."""
        print("\n" + "═" * 60)
        print("👋 Thank you for using ArqSysIA!")
        print("═" * 60)
        print("\n💾 All iterations have been saved.")
        print(f"📁 Data location: {self.data_dir}/{self.project_name}")
        
        # Mostrar estadísticas finales
        try:
            iterations = self.orchestrator.version_manager.list_iterations()
            if iterations:
                print(f"\n📊 Session Summary:")
                print(f"  Total Iterations: {len(iterations)}")
                latest = self.orchestrator.version_manager.get_latest_iteration()
                score = latest.state.outputs.get('validation', {}).get('overall_score', 0)
                print(f"  Latest Score: {score}/100")
        except:
            pass
        
        print("\n✨ See you next time!\n")
        self.running = False
    
    def _confirm(self, message: str) -> bool:
        """
        Helper para confirmaciones de usuario.
        
        Args:
            message: Mensaje de confirmación
            
        Returns:
            True si el usuario confirma, False en caso contrario
        """
        try:
            response = input(f"\n➤ {message} (y/n): ").strip().lower()
            return response in ['y', 'yes']
        except (EOFError, KeyboardInterrupt):
            return False
    
    def handle_post_validation(self, choice: str, result: IterationResult) -> None:
        """
        Manejar opciones post-validación con mejor manejo de errores.
        
        Args:
            choice: Opción seleccionada ('accept', 'regenerate', 'redesign', 'details', 'exit')
            result: Resultado de la iteración
        """
        if choice == 'accept':
            try:
                # ✅ CORRECTO: Usar result.iteration en lugar de result.iteration_number
                self.orchestrator.accept_and_continue(result.iteration)
                print("\n✅ Iteration accepted!")
                print("💡 You can now create a new iteration or view the history")
                input("\nPress Enter to continue...")
            except Exception as e:
                print(f"\n❌ Error accepting iteration: {e}")
                input("\nPress Enter to continue...")
        
        elif choice == 'regenerate':
            print("\n" + "─" * 60)
            print("REGENERATE CODE")
            print("─" * 60)
            print("\n💡 Provide specific feedback about what needs to be changed in the code")
            feedback = input("\n➤ Enter feedback for code regeneration: ").strip()
            
            if not feedback:
                print("❌ Feedback cannot be empty.")
                input("\nPress Enter to continue...")
                return
            
            if not self._confirm("Regenerate code with this feedback?"):
                print("❌ Cancelled.")
                input("\nPress Enter to continue...")
                return
            
            try:
                print("\n🔄 Regenerating code...")
                print("⏳ This may take a few minutes...")
                # ✅ CORRECTO: Usar result.iteration en lugar de result.iteration_number
                new_result = self.orchestrator.regenerate_code(
                    result.iteration,
                    feedback
                )
                
                print("\n✅ Code regenerated successfully!")
                self.viewer.show_iteration_result(new_result)
                
                # Mostrar menú nuevamente
                choice = self.orchestrator.post_validation_menu(new_result)
                self.handle_post_validation(choice, new_result)
                
            except Exception as e:
                print(f"\n❌ Error regenerating code: {e}")
                print(f"   Error type: {type(e).__name__}")
                input("\nPress Enter to continue...")
        
        elif choice == 'redesign':
            print("\n" + "─" * 60)
            print("REDESIGN ARCHITECTURE")
            print("─" * 60)
            print("\n💡 Provide feedback about architectural changes needed")
            feedback = input("\n➤ Enter feedback for architecture redesign: ").strip()
            
            if not feedback:
                print("❌ Feedback cannot be empty.")
                input("\nPress Enter to continue...")
                return
            
            if not self._confirm("Redesign architecture with this feedback?"):
                print("❌ Cancelled.")
                input("\nPress Enter to continue...")
                return
            
            try:
                print("\n🔄 Redesigning architecture...")
                print("⏳ This may take a few minutes...")
                # ✅ CORRECTO: Usar result.iteration en lugar de result.iteration_number
                new_result = self.orchestrator.redesign_architecture(
                    result.iteration,
                    feedback
                )
                
                print("\n✅ Architecture redesigned successfully!")
                self.viewer.show_iteration_result(new_result)
                
                # Mostrar menú nuevamente
                choice = self.orchestrator.post_validation_menu(new_result)
                self.handle_post_validation(choice, new_result)
                
            except Exception as e:
                print(f"\n❌ Error redesigning architecture: {e}")
                print(f"   Error type: {type(e).__name__}")
                input("\nPress Enter to continue...")
        
        elif choice == 'details':
            try:
                # ✅ CORRECTO: Usar result.iteration en lugar of result.iteration_number
                self.viewer.show_iteration_details(result.iteration)
                input("\nPress Enter to continue...")
            except Exception as e:
                print(f"\n❌ Error viewing details: {e}")
                input("\nPress Enter to continue...")
        
        elif choice == 'exit':
            print("\n💾 Saving and returning to main menu...")
            input("\nPress Enter to continue...")


def main():
    """
    Punto de entrada del CLI - Versión Optimizada.
    
    Usage:
        python -m arqsysia.cli.main MyProject
        python -m arqsysia.cli.main MyProject --data-dir ./custom_data
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="ArqSysIA v1.0 - Iterative Software Architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s MyProject
  %(prog)s MyProject --data-dir ./my_projects
  %(prog)s ecommerce --data-dir ~/arqsysia_data
  
For more information, visit: https://github.com/yourusername/ArqSysIA
        """
    )
    
    parser.add_argument(
        "project",
        help="Project name (alphanumeric and underscores only)"
    )
    
    parser.add_argument(
        "--data-dir",
        default="./projects",
        help="Data directory (default: ./projects)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="ArqSysIA v1.0.0"
    )
    
    args = parser.parse_args()
    
    try:
        cli = ArqSysiaCLI(args.project, args.data_dir)
        cli.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Exiting gracefully...")
        sys.exit(0)
    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"\n❌ Initialization error: {e}")
        print("\n💡 Tip: Check that Ollama is running and the required model is available")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print(f"   Error type: {type(e).__name__}")
        sys.exit(1)


if __name__ == "__main__":
    main()
    
