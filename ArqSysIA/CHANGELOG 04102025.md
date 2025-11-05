# Changelog

Todos los cambios notables de ArqSysIA serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2025-11-04

### 🎉 Primera Release Estable

La versión 1.0.0 marca el lanzamiento oficial de ArqSysIA con CLI completo y sistema de exportación funcional.

### Added

#### Sistema de Exportación Completo
- **FileExporter** módulo para exportación física de archivos
- **ExportConfig** para configuración persistente de exportación
- Exportación manual desde explorador interactivo de archivos
- Exportación automática post-iteración (configurable)
- Generación automática de README.md con metadata en cada export
- Soporte para exportar:
  - Documentos técnicos (architecture.md, components.md, etc.)
  - Código fuente generado
  - Reportes de validación

#### CLI Interactivo Mejorado
- **InteractiveFileExplorer** con navegación completa
  - Opción `[e]` para exportar archivos a disco
  - Opción `[s]` para seleccionar archivos individuales
  - Opción `[a]` para seleccionar todos los archivos
  - Opción `[d]` para mostrar información de descarga
  - Opción `[1]` para ver contenido de archivos
- **Settings Menu** completamente funcional
  - Toggle auto-export ON/OFF
  - Configurar elementos a exportar
  - Ver ubicaciones de exportaciones
  - Ver estadísticas del proyecto
- **View History** con tabla formateada
  - Muestra todas las iteraciones
  - Scores y estados
  - Fechas de creación
- **Delete Iteration** con confirmaciones de seguridad
  - Doble confirmación requerida
  - Advertencias sobre dependencias
  - Limpieza completa de archivos

#### Pipeline Completo
- **AnalyzerPhase** con DeepSeek-R1:32b
  - Análisis arquitectónico profundo
  - Diseño de componentes
  - Decisiones de arquitectura
- **CodeGenPhase** con Qwen2.5-Coder:32b
  - Generación de código estructurado
  - Documentación técnica
  - Scripts de configuración
- **ValidatorPhase** con DeepSeek-R1:14b
  - Validación arquitectural
  - Análisis de seguridad
  - Detección de issues
  - Scores multi-dimensionales

#### Gestión de Iteraciones
- **Continue Last** para continuar desde última iteración
  - Mantiene contexto histórico
  - Feedback integrado
  - Auto-export automático
- **Compare Iterations** para análisis de diferencias
  - Comparación lado a lado
  - Delta de scores
  - Cambios en componentes

#### Storage y Persistencia
- **FileStorage** backend robusto
  - JSON estructurado por iteración
  - Configuración persistente
  - Metadata de proyecto
- Estructura organizada:
  ```
  projects/
  └── ProjectName/
      ├── iterations/
      ├── exports/
      ├── metadata.json
      └── export_config.json
  ```

#### Testing
- 96 tests automatizados
- Cobertura de:
  - Core components
  - Phases
  - Storage
  - CLI functions
  - Export system

### Changed

- **Settings Menu** reescrito desde cero
  - Ya no muestra "Coming soon"
  - 4 opciones funcionales
  - Loop interactivo mejorado
- **InteractiveFileExplorer** refactorizado
  - Ahora requiere project_name e iteration_number
  - Integrado con FileExporter
  - Mejor manejo de errores
- **Main CLI** optimizado
  - Mejor validación de inputs
  - Mensajes de error más descriptivos
  - Manejo robusto de interrupciones

### Fixed

#### Session 21 Fixes
- Firma de `InteractiveFileExplorer.__init__` corregida
- Referencia `self.project.name` → `self.project_name` corregida
- Settings menu ahora completamente funcional
- Export files opción agregada al explorador

#### Session 22 Fixes
- `execute_iteration()` → `run_iteration()` en orchestrator calls
- Cálculo de `next_iteration` usando `max(iteration_number)` 
- `result.iteration_number` → `result.iteration` corregido
- `show_iteration_result()` → `show_iteration_details()` corregido
- Auto-export agregado a `continue_last()` function
- `view_history()` reimplementado con tabla formateada

### Testing Completed

#### Session 21
- ✅ Exportación manual validada
- ✅ Settings menu validado
- ✅ 2 archivos exportados exitosamente

#### Session 22
- ✅ Auto-export validado con iteración real (#3)
- ✅ Continue Last validado con iteración (#4)
- ✅ Compare Iterations validado (2 vs 3)
- ✅ View History validado

### Known Issues

- DiffViewer muestra información limitada en comparaciones
- CodeGen ocasionalmente genera errores de parsing JSON (no crítico)
- Validator scores pueden ser inconsistentes entre ejecuciones

### Performance

- **Analyzer**: ~4-5 minutos (DeepSeek-R1:32b)
- **CodeGen**: ~15-17 minutos (Qwen2.5-Coder:32b)
- **Validator**: ~1 minuto (DeepSeek-R1:14b)
- **Total por iteración**: ~20-23 minutos

### Documentation

- README.md actualizado con sección de exportación
- CONTINUITY_SESSION documents para tracking
- Session summaries (21, 22)
- Inline code documentation mejorada

---

## [0.9.0] - 2025-10-31

### Added
- Core orchestration system
- Basic CLI functionality
- Pipeline inicial (Analyzer → CodeGen → Validator)
- Storage system

### Changed
- Migración de prototipos a sistema robusto

---

## [0.1.0] - 2025-10-15

### Added
- Proyecto inicial
- Proof of concept
- Tests básicos

---

## Roadmap

### v1.1.0 (Planeado)
- 🎨 **GUI (Graphical User Interface)**
  - Interfaz web moderna
  - Visualización de arquitecturas
  - Editor de requirements
  - Dashboard de métricas
- 🔄 **Real-time Updates**
  - Streaming de progreso LLM
  - WebSocket para updates live
- 📊 **Enhanced Analytics**
  - Gráficos de tendencias
  - Comparación visual de iteraciones
  - Reportes exportables

### v1.2.0 (Planeado)
- 🌐 **Multi-Language Support**
  - Internacionalización (i18n)
  - Español, Inglés, más idiomas
- 🔌 **Plugin System**
  - Extensibilidad vía plugins
  - Custom phases
  - Custom exporters

### v2.0.0 (Futuro)
- ☁️ **Cloud Integration**
  - Cloud storage backends
  - Team collaboration
  - Shared projects
- 🤖 **Advanced AI**
  - Multi-agent systems
  - Specialized agents por dominio
  - Learning from feedback

---

## Contributing

Para contribuir, por favor:
1. Revisa los issues abiertos
2. Propón nuevas features via discussions
3. Sigue las convenciones del proyecto
4. Incluye tests para nuevas features

---

## Links

- **Repository**: https://github.com/yourusername/ArqSysIA
- **Issues**: https://github.com/yourusername/ArqSysIA/issues
- **Discussions**: https://github.com/yourusername/ArqSysIA/discussions

---

**Última actualización**: 2025-11-04
