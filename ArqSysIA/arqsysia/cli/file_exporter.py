"""
ArqSysIA - File Exporter Module
Exportación de archivos virtuales a filesystem físico
Versión: 1.0
Fecha: 02 Noviembre 2025
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class FileExporter:
    """
    Exportador de archivos virtuales a disco.
    
    Maneja:
    - Exportación manual de archivos seleccionados
    - Exportación automática post-iteración
    - Estructura de directorios organizada
    - Validación de rutas y permisos
    """
    
    def __init__(self, project_name: str, base_path: str = "./projects"):
        """
        Inicializar exportador.

        Args:
            project_name: Nombre del proyecto
            base_path: Ruta base donde están los proyectos
        """
        self.project_name = project_name
        self.base_path = Path(base_path)
        self.exports_dir = self.base_path / project_name / "exports"

    def _is_safe_filename(self, filename: str) -> bool:
        """
        Valida que filename no contiene caracteres peligrosos.

        Args:
            filename: Nombre del archivo

        Returns:
            True si es seguro, False si no
        """
        dangerous = ['..', '/', '\\', '\0', '<', '>', ':', '"', '|', '?', '*']
        return not any(char in filename for char in dangerous)

    def _is_subpath(self, path: Path, parent: Path) -> bool:
        """
        Valida que path está dentro de parent directory.

        Args:
            path: Path a validar
            parent: Path padre permitido

        Returns:
            True si path está dentro de parent, False si no
        """
        try:
            path.resolve().relative_to(parent.resolve())
            return True
        except ValueError:
            return False
    
    def export_files(
        self, 
        files: Dict[str, List], 
        iteration_number: int,
        selected_only: bool = False,
        selected_files: Optional[List] = None
    ) -> Dict[str, any]:
        """
        Exporta archivos a disco.
        
        Args:
            files: Dict con 'technical_docs' y 'source_code'
            iteration_number: Número de iteración
            selected_only: Si True, solo exporta archivos seleccionados
            selected_files: Lista de VirtualFile seleccionados
            
        Returns:
            Dict con resultado de la exportación:
            {
                'success': bool,
                'exported_count': int,
                'export_path': str,
                'files_created': List[str],
                'errors': List[str]
            }
        """
        result = {
            'success': False,
            'exported_count': 0,
            'export_path': '',
            'files_created': [],
            'errors': []
        }
        
        try:
            # Crear directorio de exportación
            iteration_dir = self.exports_dir / f"iteration_{iteration_number:03d}"
            iteration_dir.mkdir(parents=True, exist_ok=True)
            
            result['export_path'] = str(iteration_dir.absolute())
            
            # Determinar qué archivos exportar
            if selected_only and selected_files:
                files_to_export = selected_files
            else:
                # Exportar todos
                files_to_export = []
                for category_files in files.values():
                    files_to_export.extend(category_files)
            
            # Exportar archivos
            for vfile in files_to_export:
                try:
                    file_path = self._get_file_path(iteration_dir, vfile)
                    
                    # Crear subdirectorio si no existe
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Escribir archivo
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(vfile.content)
                    
                    result['files_created'].append(str(file_path.relative_to(self.base_path)))
                    result['exported_count'] += 1
                    
                except Exception as e:
                    error_msg = f"Error exporting {vfile.name}: {str(e)}"
                    result['errors'].append(error_msg)
            
            # Crear archivo README con info de la exportación
            self._create_export_readme(iteration_dir, iteration_number, result)
            
            result['success'] = result['exported_count'] > 0
            
        except Exception as e:
            result['errors'].append(f"Fatal error during export: {str(e)}")
        
        return result
    
    def _get_file_path(self, iteration_dir: Path, vfile) -> Path:
        """
        Determina la ruta completa del archivo según su categoría.
        CON VALIDACIÓN DE SEGURIDAD (Fix 5.1).

        Args:
            iteration_dir: Directorio base de la iteración
            vfile: VirtualFile a exportar

        Returns:
            Path completo del archivo

        Raises:
            ValueError: Si el filename es inseguro o escapa del directorio
        """
        # Fix 5.1: Validar nombre de archivo
        if not self._is_safe_filename(vfile.name):
            raise ValueError(f"Unsafe filename detected: {vfile.name}")

        # Determinar subdirectorio según categoría
        if vfile.category == 'technical_docs':
            subdir = iteration_dir / "technical_docs"
        elif vfile.category == 'source_code':
            subdir = iteration_dir / "source_code"
        else:
            subdir = iteration_dir

        # Construir path completo
        file_path = (subdir / vfile.name).resolve()

        # Fix 5.1: Validar que el path está dentro de iteration_dir
        if not self._is_subpath(file_path, iteration_dir):
            raise ValueError(f"Path escapes export directory: {vfile.name}")

        return file_path
    
    def _create_export_readme(
        self, 
        iteration_dir: Path, 
        iteration_number: int, 
        export_result: Dict
    ):
        """
        Crea un archivo README.md con información de la exportación.
        
        Args:
            iteration_dir: Directorio de la iteración
            iteration_number: Número de iteración
            export_result: Resultado de la exportación
        """
        readme_path = iteration_dir / "README.md"
        
        content = f"""# Iteration {iteration_number} - Export

**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Project:** {self.project_name}  
**Files exported:** {export_result['exported_count']}

## Structure

```
iteration_{iteration_number:03d}/
├── technical_docs/
│   ├── architecture.md
│   ├── components.md
│   ├── validation_report.md
│   └── ...
├── source_code/
│   └── ...
└── README.md (this file)
```

## Files Created

"""
        
        for file_path in export_result['files_created']:
            content += f"- `{file_path}`\n"
        
        if export_result['errors']:
            content += "\n## Errors\n\n"
            for error in export_result['errors']:
                content += f"- ⚠️ {error}\n"
        
        content += f"""

## Usage

These files are exported from the iteration JSON for easy access and editing.

**Original JSON:** `../iterations/iteration_{iteration_number:03d}.json`

---

*Generated by ArqSysIA v1.0*
"""
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def check_export_exists(self, iteration_number: int) -> bool:
        """
        Verifica si ya existe una exportación para esta iteración.
        
        Args:
            iteration_number: Número de iteración
            
        Returns:
            True si existe, False si no
        """
        iteration_dir = self.exports_dir / f"iteration_{iteration_number:03d}"
        return iteration_dir.exists()
    
    def get_export_path(self, iteration_number: int) -> Optional[str]:
        """
        Obtiene la ruta de exportación para una iteración.
        
        Args:
            iteration_number: Número de iteración
            
        Returns:
            Ruta absoluta del directorio de exportación o None si no existe
        """
        iteration_dir = self.exports_dir / f"iteration_{iteration_number:03d}"
        if iteration_dir.exists():
            return str(iteration_dir.absolute())
        return None
    
    def list_exported_iterations(self) -> List[int]:
        """
        Lista todas las iteraciones que tienen exportaciones.
        
        Returns:
            Lista de números de iteración con exportaciones
        """
        if not self.exports_dir.exists():
            return []
        
        exported = []
        for item in self.exports_dir.iterdir():
            if item.is_dir() and item.name.startswith("iteration_"):
                try:
                    num = int(item.name.split("_")[1])
                    exported.append(num)
                except (ValueError, IndexError):
                    continue
        
        return sorted(exported)


class ExportConfig:
    """
    Configuración de exportación automática.
    
    Maneja:
    - Habilitación/deshabilitación de auto-export
    - Persistencia de configuración
    - Validación de settings
    """
    
    def __init__(self, project_name: str, base_path: str = "./projects"):
        """
        Inicializar configuración.
        
        Args:
            project_name: Nombre del proyecto
            base_path: Ruta base de proyectos
        """
        self.project_name = project_name
        self.config_file = Path(base_path) / project_name / "export_config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """
        Carga configuración desde disco.
        
        Returns:
            Dict con configuración o valores por defecto
        """
        default_config = {
            'auto_export_enabled': False,
            'export_technical_docs': True,
            'export_source_code': True,
            'overwrite_existing': False
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge con defaults para mantener retrocompatibilidad
                    return {**default_config, **loaded}
            except Exception:
                pass
        
        return default_config
    
    def _save_config(self):
        """Guarda configuración a disco."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"⚠️ Warning: Could not save export config: {e}")
    
    def is_auto_export_enabled(self) -> bool:
        """Retorna True si auto-export está habilitado."""
        return self.config.get('auto_export_enabled', False)
    
    def enable_auto_export(self):
        """Habilita exportación automática."""
        self.config['auto_export_enabled'] = True
        self._save_config()
    
    def disable_auto_export(self):
        """Deshabilita exportación automática."""
        self.config['auto_export_enabled'] = False
        self._save_config()
    
    def toggle_auto_export(self) -> bool:
        """
        Alterna estado de auto-export.
        
        Returns:
            Nuevo estado (True/False)
        """
        new_state = not self.config['auto_export_enabled']
        self.config['auto_export_enabled'] = new_state
        self._save_config()
        return new_state
    
    def set_option(self, key: str, value: any):
        """
        Establece una opción de configuración.
        
        Args:
            key: Clave de configuración
            value: Valor a establecer
        """
        if key in self.config:
            self.config[key] = value
            self._save_config()
    
    def get_option(self, key: str, default=None) -> any:
        """
        Obtiene una opción de configuración.
        
        Args:
            key: Clave de configuración
            default: Valor por defecto si no existe
            
        Returns:
            Valor de la configuración
        """
        return self.config.get(key, default)
    
    def get_all_settings(self) -> Dict:
        """Retorna todas las configuraciones."""
        return self.config.copy()


# Ejemplo de uso
if __name__ == "__main__":
    print("FileExporter Module - Use with ArqSysIA CLI")
    print("\nExample usage:")
    print("  from arqsysia.cli.file_exporter import FileExporter, ExportConfig")
    print("  exporter = FileExporter('MyProject')")
    print("  result = exporter.export_files(files, iteration_number=2)")
    
