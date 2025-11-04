"""
ArqSysIA - Enhanced Iteration Viewer with Interactive File Explorer
Versión: 1.0
Fecha: 02 Noviembre 2025
"""

from arqsysia.cli.file_exporter import FileExporter
from arqsysia.core import VersionManager
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime
import json


@dataclass
class VirtualFile:
    """Representa un archivo virtual extraído del JSON de una iteración"""
    name: str
    category: str  # "technical_docs" o "source_code"
    file_type: str  # "markdown", "python", "javascript", "json", etc.
    content: str
    size_bytes: int
    description: str = ""
    
    def get_display_name(self) -> str:
        """Retorna el nombre para mostrar en el menú"""
        return f"{self.name} ({self.size_bytes} bytes)"


class FileExtractor:
    """Extrae archivos virtuales del JSON de una iteración"""
    
    @staticmethod
    def extract_files(iteration) -> Dict[str, List[VirtualFile]]:
        """
        Extrae todos los archivos de una iteración
        
        Returns:
            Dict con dos keys: 'technical_docs' y 'source_code'
        """
        files = {
            'technical_docs': [],
            'source_code': []
        }
        
        outputs = iteration.state.outputs
        
        # 1. DOCUMENTOS TÉCNICOS
        
        # Architecture Document
        analysis_output = outputs.get('analysis', {})
        analysis_data = analysis_output.get('analysis', {})
        
        if analysis_data:
            arch_content = FileExtractor._build_architecture_doc(analysis_data)
            files['technical_docs'].append(VirtualFile(
                name="architecture.md",
                category="technical_docs",
                file_type="markdown",
                content=arch_content,
                size_bytes=len(arch_content),
                description="Software architecture design and justification"
            ))
        
        # Database Design Document
        if analysis_data and 'database_design' in analysis_data:
            db_content = FileExtractor._build_database_doc(analysis_data['database_design'])
            files['technical_docs'].append(VirtualFile(
                name="database_design.md",
                category="technical_docs",
                file_type="markdown",
                content=db_content,
                size_bytes=len(db_content),
                description="Database schema and design decisions"
            ))
        
        # Components Document
        if analysis_data and 'main_components' in analysis_data:
            comp_content = FileExtractor._build_components_doc(analysis_data['main_components'])
            files['technical_docs'].append(VirtualFile(
                name="components.md",
                category="technical_docs",
                file_type="markdown",
                content=comp_content,
                size_bytes=len(comp_content),
                description="Main application components and their responsibilities"
            ))
        
        # Validation Report
        validation_output = outputs.get('validation', {})
        validation_data = validation_output.get('validation', {})
        
        if validation_data:
            val_content = FileExtractor._build_validation_report(validation_data)
            files['technical_docs'].append(VirtualFile(
                name="validation_report.md",
                category="technical_docs",
                file_type="markdown",
                content=val_content,
                size_bytes=len(val_content),
                description="Architecture validation results and recommendations"
            ))
        
        # 2. CÓDIGO FUENTE
        
        code_output = outputs.get('code_generation', {})
        code_data = code_output.get('code', '')
        structure = code_output.get('structure', {})
        
        if code_data:
            # Si code_data es un string (código concatenado)
            if isinstance(code_data, str):
                files['source_code'].append(VirtualFile(
                    name="generated_code.txt",
                    category="source_code",
                    file_type="text",
                    content=code_data,
                    size_bytes=len(code_data),
                    description="Generated source code"
                ))
            
            # Si code_data es un dict con archivos individuales
            elif isinstance(code_data, dict):
                for filename, content in code_data.items():
                    file_type = FileExtractor._get_file_type(filename)
                    files['source_code'].append(VirtualFile(
                        name=filename,
                        category="source_code",
                        file_type=file_type,
                        content=content,
                        size_bytes=len(content),
                        description=f"{file_type.upper()} source file"
                    ))
        
        # File Structure Document
        if structure:
            struct_content = FileExtractor._build_structure_doc(structure)
            files['technical_docs'].append(VirtualFile(
                name="file_structure.md",
                category="technical_docs",
                file_type="markdown",
                content=struct_content,
                size_bytes=len(struct_content),
                description="Project file and directory structure"
            ))
        
        return files
    
    @staticmethod
    def _build_architecture_doc(analysis_data: Dict) -> str:
        """Construye documento de arquitectura"""
        content = "# Software Architecture Document\n\n"
        content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        content += "## Architecture Pattern\n\n"
        content += f"**Pattern:** {analysis_data.get('architecture_pattern', 'N/A')}\n\n"
        
        content += "## Justification\n\n"
        content += f"{analysis_data.get('architecture_justification', 'N/A')}\n\n"
        
        content += "## Technology Stack\n\n"
        tech_stack = analysis_data.get('tech_stack', {})
        for key, value in tech_stack.items():
            content += f"- **{key.replace('_', ' ').title()}:** {value}\n"
        
        content += "\n## Functional Requirements\n\n"
        for req in analysis_data.get('functional_requirements', []):
            content += f"- {req}\n"
        
        return content
    
    @staticmethod
    def _build_database_doc(db_design: Dict) -> str:
        """Construye documento de diseño de base de datos"""
        content = "# Database Design Document\n\n"
        content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        content += "## Database Type\n\n"
        content += f"{db_design.get('type', 'N/A')}\n\n"
        
        content += "## Tables/Collections\n\n"
        tables = db_design.get('tables', [])
        for table in tables:
            content += f"### {table.get('name', 'Unknown')}\n\n"
            content += f"**Purpose:** {table.get('purpose', 'N/A')}\n\n"
            
            fields = table.get('fields', [])
            if fields:
                content += "**Fields:**\n\n"
                for field in fields:
                    content += f"- `{field.get('name')}` ({field.get('type')}) - {field.get('description', '')}\n"
            content += "\n"
        
        return content
    
    @staticmethod
    def _build_components_doc(components: List[Dict]) -> str:
        """Construye documento de componentes"""
        content = "# Application Components\n\n"
        content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for i, comp in enumerate(components, 1):
            content += f"## {i}. {comp.get('name', 'Unknown')}\n\n"
            content += f"**Purpose:** {comp.get('purpose', 'N/A')}\n\n"
            
            responsibilities = comp.get('responsibilities', [])
            if responsibilities:
                content += "**Responsibilities:**\n\n"
                for resp in responsibilities:
                    content += f"- {resp}\n"
            
            dependencies = comp.get('dependencies', [])
            if dependencies:
                content += "\n**Dependencies:**\n\n"
                for dep in dependencies:
                    content += f"- {dep}\n"
            
            content += "\n"
        
        return content
    
    @staticmethod
    def _build_validation_report(validation_data: Dict) -> str:
        """Construye reporte de validación"""
        content = "# Architecture Validation Report\n\n"
        content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        content += "## Overall Score\n\n"
        content += f"**Score:** {validation_data.get('overall_score', 0)}/100\n\n"
        
        validation_results = validation_data.get('validation_results', {})
        
        if validation_results:
            content += "## Validation Results\n\n"
            
            for category, results in validation_results.items():
                content += f"### {category.replace('_', ' ').title()}\n\n"
                
                if isinstance(results, dict):
                    score_key = f"{category}_score"
                    if score_key in results:
                        content += f"**Score:** {results[score_key]}/10\n\n"
                    
                    issues = results.get('issues', [])
                    if issues:
                        content += "**Issues:**\n\n"
                        for issue in issues:
                            content += f"- {issue}\n"
                    
                    recommendations = results.get('recommendations', [])
                    if recommendations:
                        content += "\n**Recommendations:**\n\n"
                        for rec in recommendations:
                            content += f"- {rec}\n"
                
                content += "\n"
        
        return content
    
    @staticmethod
    def _build_structure_doc(structure: Dict) -> str:
        """Construye documento de estructura de archivos"""
        content = "# Project File Structure\n\n"
        content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        content += "```\n"
        content += json.dumps(structure, indent=2)
        content += "\n```\n"
        
        return content
    
    @staticmethod
    def _get_file_type(filename: str) -> str:
        """Determina el tipo de archivo por su extensión"""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.md': 'markdown',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.sql': 'sql',
            '.sh': 'shell',
            '.ipynb': 'jupyter',
        }
        
        for ext, ftype in ext_map.items():
            if filename.endswith(ext):
                return ftype
        
        return 'text'


class InteractiveFileExplorer:
    """Explorador interactivo de archivos virtuales"""
    
    def __init__(self, files: Dict[str, List], project_name: str, iteration_number: int):
        """
        Inicializar explorador.
        
        Args:
            files: Dict con 'technical_docs' y 'source_code'
            project_name: Nombre del proyecto
            iteration_number: Número de iteración
        """
        self.files = files
        self.selected_files: List = []
        self.project_name = project_name
        self.iteration_number = iteration_number
        self.exporter = FileExporter(project_name)
            
    def show_menu(self):
        """Muestra el menú principal del explorador"""
        while True:
            self._clear_screen()
            print("\n╔" + "═" * 70 + "╗")
            print("║" + " FILE EXPLORER ".center(70) + "║")
            print("╚" + "═" * 70 + "╝\n")
            
            print("📁 Available Files:\n")
            
            # Mostrar documentos técnicos
            tech_docs = self.files.get('technical_docs', [])
            if tech_docs:
                print("📄 TECHNICAL DOCUMENTS:")
                for i, file in enumerate(tech_docs, 1):
                    print(f"  {i}. {file.get_display_name()}")
                    print(f"     └─ {file.description}")
            
            print()
            
            # Mostrar código fuente
            source_code = self.files.get('source_code', [])
            if source_code:
                print("💻 SOURCE CODE:")
                offset = len(tech_docs)
                for i, file in enumerate(source_code, offset + 1):
                    print(f"  {i}. {file.get_display_name()}")
                    print(f"     └─ {file.description}")
            
            print("\n" + "─" * 70)
            print("\nOptions:")
            print("  [number]  - View file content")
            print("  [s]       - Select/mark files for download info")
            print("  [a]       - Select all files")
            print("  [e]       - Export files to disk")  # ← LÍNEA NUEVA
            print("  [d]       - Show download info for selected files")
            print("  [c]       - Clear selection")
            print("  [q]       - Return to main menu")
            
            if self.selected_files:
                print(f"\n✓ Selected: {len(self.selected_files)} file(s)")
            
            choice = input("\nEnter option: ").strip().lower()
            
            if choice == 'q':
                break
            elif choice == 's':
                self._select_files_menu()
            elif choice == 'a':
                self._select_all()
            elif choice == 'e':  # ← LÍNEA NUEVA
                self._export_files()  # ← LÍNEA NUEVA
            elif choice == 'd':
                self._show_download_info()
            elif choice == 'c':
                self.selected_files.clear()
                print("\n✓ Selection cleared")
                input("\nPress Enter to continue...")
            elif choice.isdigit():
                file_num = int(choice)
                all_files = tech_docs + source_code
                if 1 <= file_num <= len(all_files):
                    self._view_file(all_files[file_num - 1])
                else:
                    print("\n✗ Invalid file number")
                    input("\nPress Enter to continue...")
            else:
                print("\n✗ Invalid option")
                input("\nPress Enter to continue...")
    
    def _view_file(self, file: VirtualFile):
        """Muestra el contenido de un archivo"""
        self._clear_screen()
        print("\n╔" + "═" * 70 + "╗")
        print("║" + f" {file.name} ".center(70) + "║")
        print("╚" + "═" * 70 + "╝\n")
        
        print(f"Type: {file.file_type}")
        print(f"Size: {file.size_bytes} bytes")
        print(f"Description: {file.description}\n")
        print("─" * 70)
        print()
        
        # Mostrar contenido con paginación si es muy largo
        lines = file.content.split('\n')
        lines_per_page = 30
        
        for i in range(0, len(lines), lines_per_page):
            page_lines = lines[i:i + lines_per_page]
            for line in page_lines:
                print(line)
            
            if i + lines_per_page < len(lines):
                print("\n" + "─" * 70)
                choice = input(f"\n[Enter] Next page | [q] Back to menu: ").strip().lower()
                if choice == 'q':
                    break
                print()
        
        print("\n" + "─" * 70)
        input("\nPress Enter to return to file list...")
    
    def _select_files_menu(self):
        """Menú para seleccionar archivos"""
        self._clear_screen()
        print("\n╔" + "═" * 70 + "╗")
        print("║" + " SELECT FILES ".center(70) + "║")
        print("╚" + "═" * 70 + "╝\n")
        
        all_files = self.files.get('technical_docs', []) + self.files.get('source_code', [])
        
        for i, file in enumerate(all_files, 1):
            selected = "✓" if file in self.selected_files else " "
            print(f"  [{selected}] {i}. {file.name}")
        
        print("\nEnter file numbers separated by commas (e.g., 1,3,5)")
        print("Or 'all' to select all, 'none' to clear")
        
        choice = input("\nSelection: ").strip().lower()
        
        if choice == 'all':
            self.selected_files = all_files.copy()
            print("\n✓ All files selected")
        elif choice == 'none':
            self.selected_files.clear()
            print("\n✓ Selection cleared")
        elif choice:
            try:
                numbers = [int(n.strip()) for n in choice.split(',')]
                for num in numbers:
                    if 1 <= num <= len(all_files):
                        file = all_files[num - 1]
                        if file in self.selected_files:
                            self.selected_files.remove(file)
                        else:
                            self.selected_files.append(file)
                print(f"\n✓ Selection updated: {len(self.selected_files)} file(s)")
            except ValueError:
                print("\n✗ Invalid input")
        
        input("\nPress Enter to continue...")
    
    def _select_all(self):
        """Selecciona todos los archivos"""
        all_files = self.files.get('technical_docs', []) + self.files.get('source_code', [])
        self.selected_files = all_files.copy()
        print(f"\n✓ All files selected ({len(self.selected_files)} files)")
        input("\nPress Enter to continue...")
    
    def _show_download_info(self):
        """Muestra información para 'descargar' archivos seleccionados"""
        if not self.selected_files:
            print("\n✗ No files selected")
            input("\nPress Enter to continue...")
            return
        
        self._clear_screen()
        print("\n╔" + "═" * 70 + "╗")
        print("║" + " DOWNLOAD INFORMATION ".center(70) + "║")
        print("╚" + "═" * 70 + "╝\n")
        
        print(f"Selected files: {len(self.selected_files)}\n")
        print("To save these files to your filesystem, you can:")
        print("\n1. Copy content from 'View file' option")
        print("2. Use the iteration JSON at:")
        print(f"   ~/Projects/ArqSysIA/projects/[project_name]/iterations/iteration_XXX.json")
        print("\n3. Or use 'jq' to extract specific data:")
        
        print("\n" + "─" * 70)
        print("\nSelected Files:\n")
        
        for i, file in enumerate(self.selected_files, 1):
            print(f"{i}. {file.name}")
            print(f"   Type: {file.file_type}")
            print(f"   Size: {file.size_bytes} bytes")
            print(f"   Category: {file.category}")
            print()
        
        print("─" * 70)
        input("\nPress Enter to continue...")

    def _export_files(self):
        """Exporta archivos seleccionados (o todos) a disco."""
        self._clear_screen()
        print("\n╔" + "═" * 70 + "╗")
        print("║" + " EXPORT FILES TO DISK ".center(70) + "║")
        print("╚" + "═" * 70 + "╝\n")
        
        # Determinar qué exportar
        if self.selected_files:
            print(f"📦 Files to export: {len(self.selected_files)} selected file(s)\n")
            for i, file in enumerate(self.selected_files, 1):
                print(f"  {i}. {file.name}")
            print()
        else:
            all_files = self.files.get('technical_docs', []) + self.files.get('source_code', [])
            print(f"📦 Files to export: {len(all_files)} file(s) (ALL)\n")
            print("💡 Tip: Use [s] to select specific files before exporting\n")
        
        # Verificar si ya existe exportación
        if self.exporter.check_export_exists(self.iteration_number):
            export_path = self.exporter.get_export_path(self.iteration_number)
            print(f"⚠️  Export already exists at:\n   {export_path}\n")
            
            overwrite = input("Overwrite existing export? [y/N]: ").strip().lower()
            if overwrite != 'y':
                print("\n✗ Export cancelled")
                input("\nPress Enter to continue...")
                return
        
        # Confirmar exportación
        confirm = input("Start export? [Y/n]: ").strip().lower()
        if confirm == 'n':
            print("\n✗ Export cancelled")
            input("\nPress Enter to continue...")
            return
        
        # Ejecutar exportación
        print("\n🔄 Exporting files...")
        
        result = self.exporter.export_files(
            files=self.files,
            iteration_number=self.iteration_number,
            selected_only=len(self.selected_files) > 0,
            selected_files=self.selected_files if self.selected_files else None
        )
        
        # Mostrar resultado
        print("\n" + "─" * 70)
        if result['success']:
            print(f"\n✅ Export successful!")
            print(f"   Files exported: {result['exported_count']}")
            print(f"   Location: {result['export_path']}\n")
            
            print("📁 Files created:\n")
            for file_path in result['files_created']:
                print(f"   ✓ {file_path}")
            
            if result['errors']:
                print("\n⚠️  Warnings:\n")
                for error in result['errors']:
                    print(f"   - {error}")
        else:
            print(f"\n✗ Export failed!")
            if result['errors']:
                print("\n❌ Errors:\n")
                for error in result['errors']:
                    print(f"   - {error}")
        
        print("\n" + "─" * 70)
        input("\nPress Enter to continue...")
    
    @staticmethod
    def _clear_screen():
        """Limpia la pantalla (simulado con líneas en blanco)"""
        print("\n" * 2)


class IterationViewer:
    """Visor de iteraciones con explorador interactivo de archivos"""
    
    def __init__(self, project_name: str, storage):
       """
       Inicializar viewer.
    
       Args:
           project_name: Nombre del proyecto
           storage: Backend de almacenamiento (StorageBackend)
       """
       self.project_name = project_name
       self.storage = storage
       self.version_manager = VersionManager(project_name, storage)
           
    def show_iteration_details(self, iteration_number: int):
        """
        Muestra detalles de una iteración con opción de explorador interactivo
        
        Args:
            iteration_number: Número de iteración a mostrar
        """
        iteration = self.version_manager.get_iteration(iteration_number)
        
        # Mostrar resumen básico
        self._show_summary(iteration, iteration_number)
        
        # Ofrecer opciones
        while True:
            print("\n" + "─" * 70)
            print("\nOptions:")
            print("  [1] View summary again")
            print("  [2] Open interactive file explorer")
            print("  [3] Show raw JSON structure")
            print("  [q] Return to main menu")
            
            choice = input("\nEnter option: ").strip().lower()
            
            if choice == 'q':
                break
            elif choice == '1':
                self._show_summary(iteration, iteration_number)
            elif choice == '2':
                files = FileExtractor.extract_files(iteration)
                explorer = InteractiveFileExplorer(
                    files,
                    self.project_name,
                    iteration_number
                )
                explorer.show_menu()
            elif choice == '3':
                self._show_raw_structure(iteration)
            else:
                print("\n✗ Invalid option")
    
    def _show_summary(self, iteration, iteration_number: int):
        """Muestra resumen de la iteración"""
        print("\n╔" + "═" * 70 + "╗")
        print("║" + f" Iteration {iteration_number} - Summary ".center(70) + "║")
        print("╚" + "═" * 70 + "╝\n")
        
        # Información básica
        print("📋 BASIC INFORMATION")
        print("─" * 70)
        print(f"Date: {iteration.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Parent: {iteration.state.parent_iteration if iteration.state.parent_iteration else 'None (initial)'}")
        
        # Score
        validation_output = iteration.state.outputs.get('validation', {})
        score = self._get_overall_score(validation_output)
        print(f"Score: {score}/100")
        
        # Arquitectura (resumen)
        print("\n🏗️  ARCHITECTURE")
        print("─" * 70)
        
        analysis_output = iteration.state.outputs.get('analysis', {})
        analysis_data = analysis_output.get('analysis', {})
        
        if analysis_data:
            pattern = analysis_data.get('architecture_pattern', 'N/A')
            tech_stack = analysis_data.get('tech_stack', {})
            components = analysis_data.get('main_components', [])
            
            print(f"Pattern: {pattern}")
            print(f"Components: {len(components)}")
            print(f"Tech Stack Items: {len(tech_stack)}")
        else:
            print("No architecture data available")
        
        # Código (resumen)
        print("\n💻 CODE GENERATION")
        print("─" * 70)
        
        code_output = iteration.state.outputs.get('code_generation', {})
        code_data = code_output.get('code', '')
        
        if code_data:
            if isinstance(code_data, str):
                print(f"Generated code: {len(code_data)} characters")
            elif isinstance(code_data, dict):
                print(f"Generated files: {len(code_data)}")
        else:
            print("No code generated")
    
    def _get_overall_score(self, validation_output: Dict[str, Any]) -> int:
        """Calcula score general de validación"""
        validation_results = validation_output.get('validation_results', {})
        
        if validation_results:
            scores = []
            
            # Architecture score
            arch = validation_results.get('architecture', {})
            if 'architecture_score' in arch:
                scores.append(arch['architecture_score'] * 10)
            
            # Security score
            security = validation_results.get('security', {})
            if 'security_score' in security:
                scores.append(security['security_score'] * 10)
            
            if scores:
                return int(sum(scores) / len(scores))
        
        return 0
    
    def _show_raw_structure(self, iteration):
        """Muestra estructura raw del JSON"""
        print("\n╔" + "═" * 70 + "╗")
        print("║" + " RAW JSON STRUCTURE ".center(70) + "║")
        print("╚" + "═" * 70 + "╝\n")
        
        print("Keys in iteration.state.outputs:")
        for key in iteration.state.outputs.keys():
            print(f"  - {key}")
        
        print("\nFor full JSON, check:")
        print(f"  ~/Projects/ArqSysIA/projects/[project]/iterations/iteration_{iteration.state.iteration:03d}.json")
        
        input("\nPress Enter to continue...")


# Ejemplo de uso
if __name__ == "__main__":
    print("This is a module to be imported by ArqSysIA CLI")
    print("Use: from arqsysia.cli.iteration_viewer import IterationViewer")
            
