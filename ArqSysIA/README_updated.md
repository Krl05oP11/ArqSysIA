# ArqSysIA v1.0

**Iterative Software Architecture with AI** - Sistema de diseño arquitectónico iterativo asistido por IA.

[![Tests](https://img.shields.io/badge/tests-96%2F96-brightgreen)](tests/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

---

## 🎯 ¿Qué es ArqSysIA?

ArqSysIA es un sistema iterativo que utiliza IA (Large Language Models) para diseñar, generar y validar arquitecturas de software. A través de un proceso iterativo guiado, permite refinar progresivamente una arquitectura hasta alcanzar la calidad deseada.

### Características Principales

- 🔄 **Proceso Iterativo**: Refinamiento continuo basado en feedback
- 🤖 **Asistido por IA**: Utiliza LLMs para análisis, generación y validación
- 📊 **Métricas y Validación**: Scores automáticos y detección de issues
- 💾 **Persistencia Completa**: Historial completo de iteraciones
- 📝 **Comparación de Versiones**: Diff entre iteraciones
- 📋 **Logging de Decisiones**: Rastreabilidad completa
- 🎨 **CLI Interactivo**: Interfaz de usuario amigable
- 📤 **Sistema de Exportación**: Exporta archivos a disco (manual + automático)

---

## 🚀 Inicio Rápido

### Prerequisitos

- Python 3.11 o superior
- [Ollama](https://ollama.ai/) instalado y corriendo
- Modelos recomendados en Ollama:
  - `deepseek-r1:32b` (análisis)
  - `qwen2.5-coder:32b` (generación de código)
  - `deepseek-r1:14b` (validación)

### Instalación

1. **Clonar el repositorio:**
```bash
git clone https://github.com/yourusername/ArqSysIA.git
cd ArqSysIA
```

2. **Crear entorno virtual:**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Instalar el paquete:**
```bash
pip install -e .
```

5. **Verificar instalación:**
```bash
pytest tests/ -v
```

Deberías ver: `96 passed` ✅

### Primer Uso

```bash
python -m arqsysia.cli.main MiProyecto
```

Esto iniciará el CLI interactivo donde podrás:
1. Crear tu primera iteración
2. Ver el historial
3. Exportar archivos a disco
4. Comparar iteraciones
5. Refinar tu arquitectura

---

## 📖 Guía de Uso

### Comandos del CLI

El CLI de ArqSysIA proporciona 8 comandos principales:

#### 1. **New Iteration** - Crear Nueva Iteración
Inicia un nuevo ciclo de diseño arquitectónico:
```
1. New Iteration
   - Ingresa tus requirements
   - El sistema analiza, genera y valida
   - Obtienes un score y recomendaciones
   - Auto-export (si está habilitado)
```

#### 2. **View History** - Ver Historial
Muestra todas las iteraciones con:
- Números de iteración
- Scores de validación
- Fechas de creación
- Estado de cada iteración

#### 3. **View Iteration** - Ver Detalles de Iteración
Muestra información completa de una iteración específica:
- Análisis arquitectónico
- Componentes generados
- Resultados de validación
- Issues detectados
- **Explorador interactivo de archivos**
- **Opción de exportación manual**

#### 4. **Compare** - Comparar Iteraciones
Compara dos iteraciones lado a lado:
- Cambios en arquitectura
- Componentes agregados/removidos/modificados
- Delta de scores
- Issues nuevos vs resueltos

#### 5. **Continue Last** - Continuar desde Última Iteración
Resume desde donde dejaste:
- Muestra estado de última iteración
- Permite crear nueva iteración basada en la anterior
- Mantiene contexto histórico

#### 6. **Settings** - Configuración del Proyecto
Configurar opciones del proyecto:
- Toggle auto-export ON/OFF
- Configurar qué exportar (docs técnicos, código fuente)
- Ver ubicaciones de exportaciones
- Estadísticas del proyecto

#### 7. **Delete Iteration** - Eliminar Iteración
Elimina una iteración con confirmaciones de seguridad:
- Doble confirmación requerida
- Advertencias sobre dependencias
- Limpieza completa de archivos

#### 8. **Exit** - Salir
Cierra el CLI mostrando:
- Resumen de la sesión
- Ubicación de los datos
- Estadísticas finales

---

## 📤 Sistema de Exportación

ArqSysIA incluye un sistema completo de exportación de archivos que permite guardar los resultados de cada iteración al disco físico.

### Exportación Manual

**Desde el explorador de archivos:**
1. Ejecuta: `python -m arqsysia.cli.main MiProyecto`
2. Selecciona: `3. View Iteration`
3. Elige el número de iteración
4. Selecciona: `[2] Open interactive file explorer`
5. Presiona: `[e] Export files to disk`

Los archivos se exportarán a:
```
projects/MiProyecto/exports/iteration_XXX/
├── technical_docs/
│   ├── architecture.md
│   ├── components.md
│   ├── database_design.md
│   └── validation_report.md
├── source_code/
│   └── (código generado)
└── README.md
```

### Exportación Automática

**Configurar auto-export:**
1. Ejecuta: `python -m arqsysia.cli.main MiProyecto`
2. Selecciona: `6. Settings`
3. Selecciona: `[1] Toggle auto-export`
4. Confirma para habilitar

Una vez habilitado, cada nueva iteración exportará automáticamente sus archivos después de completarse.

**Ventajas del auto-export:**
- ✅ No necesitas recordar exportar manualmente
- ✅ Archivos listos inmediatamente después de cada iteración
- ✅ Fácil acceso a documentos técnicos y código
- ✅ Ideal para integración con editores de texto

### Ubicación de Archivos

**Archivos exportados:**
```
projects/
└── MiProyecto/
    ├── iterations/          # JSON completo de cada iteración
    │   ├── iteration_001.json
    │   ├── iteration_002.json
    │   └── ...
    ├── exports/             # Archivos exportados
    │   ├── iteration_001/
    │   ├── iteration_002/
    │   └── ...
    └── export_config.json   # Configuración de exportación
```

### Flujo de Trabajo Típico

```
1. Crear proyecto nuevo
   └─> python -m arqsysia.cli.main MiEcommerce

2. Habilitar auto-export (una sola vez)
   └─> Comando 6: Settings
   └─> Opción [1]: Toggle auto-export

3. Primera iteración
   └─> Comando 1: New Iteration
   └─> Ingresar requirements detallados
   └─> Archivos exportados automáticamente ✅

4. Revisar archivos exportados
   └─> Abrir: projects/MiEcommerce/exports/iteration_001/
   └─> Leer: technical_docs/architecture.md
   └─> Editar en tu IDE favorito

5. Refinar si es necesario
   └─> Comando 5: Continue Last
   └─> Ingresar feedback basado en lo revisado
   └─> Nueva iteración con mejoras
   └─> Archivos exportados automáticamente ✅

6. Comparar versiones
   └─> Comando 4: Compare
   └─> Ver diferencias entre iteraciones
```

---

## 🏗️ Arquitectura del Sistema

### Componentes Principales

```
arqsysia/
├── core/                    # Componentes nucleares
│   ├── orchestrator.py      # Coordinación de fases
│   ├── version_manager.py   # Gestión de versiones
│   ├── decision_logger.py   # Registro de decisiones
│   └── diff_engine.py       # Motor de comparación
├── phases/                  # Fases del pipeline
│   ├── analyzer.py          # Análisis arquitectónico
│   ├── codegen.py           # Generación de código
│   └── validator.py         # Validación
├── storage/                 # Persistencia
│   └── file_storage.py      # Backend de archivos
├── clients/                 # Clientes externos
│   └── ollama_client.py     # Cliente Ollama
└── cli/                     # Interfaz CLI
    ├── main.py              # CLI principal
    ├── iteration_viewer.py  # Visualización
    ├── diff_viewer.py       # Comparación
    └── file_exporter.py     # Sistema de exportación
```

### Pipeline de Ejecución

```
Requirements
    ↓
[1] ANALYZER PHASE
    ├─> Análisis de requirements
    ├─> Diseño arquitectónico
    └─> Decisiones de diseño
    ↓
[2] CODEGEN PHASE
    ├─> Generación de estructura
    ├─> Generación de código
    └─> Documentación técnica
    ↓
[3] VALIDATOR PHASE
    ├─> Validación arquitectural
    ├─> Análisis de seguridad
    ├─> Detección de issues
    └─> Scores y recomendaciones
    ↓
[4] EXPORT (si habilitado)
    ├─> Exportación a disco
    └─> Generación de README
    ↓
Results (Iteration JSON + Exported Files)
```

---

## 🧪 Testing

ArqSysIA incluye 96 tests automatizados:

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Ejecutar tests específicos
pytest tests/test_analyzer.py -v
pytest tests/test_codegen.py -v
pytest tests/test_validator.py -v

# Ver cobertura
pytest tests/ --cov=arqsysia --cov-report=html
```

---

## 🔧 Configuración Avanzada

### Modelos LLM Personalizados

Edita `arqsysia/core/iterative_orchestrator.py`:

```python
self.analyzer = AnalyzerPhase(
    ollama_client=self.ollama_client,
    model_name="tu-modelo-personalizado"  # Cambiar aquí
)
```

### Configuración de Exportación

El archivo `export_config.json` controla el comportamiento de exportación:

```json
{
  "auto_export_enabled": true,
  "export_technical_docs": true,
  "export_source_code": true,
  "overwrite_existing": false
}
```

---

## 📊 Métricas y Scores

El sistema genera scores en múltiples dimensiones:

- **Architecture Score** (0-10): Calidad del diseño arquitectónico
- **Security Score** (0-10): Nivel de seguridad implementado
- **Performance Score** (0-10): Optimización y escalabilidad
- **Overall Score** (0-100): Score agregado global

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea un branch para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Changelog

Ver [CHANGELOG.md](CHANGELOG.md) para el historial completo de cambios.

### v1.0.0 (2025-11-XX)
- ✅ Sistema de exportación completo (manual + automático)
- ✅ CLI interactivo con 8 comandos
- ✅ Pipeline completo: Analyzer → CodeGen → Validator
- ✅ Comparación de iteraciones
- ✅ Continue from last iteration
- ✅ 96 tests automatizados

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

## 🙏 Agradecimientos

- [Ollama](https://ollama.ai/) por el runtime de LLMs local
- [DeepSeek](https://deepseek.com/) por los modelos de IA
- [Qwen](https://github.com/QwenLM) por el modelo de generación de código

---

## 📞 Contacto

Para preguntas, issues o sugerencias, por favor abre un issue en GitHub.

---

**ArqSysIA v1.0** - Diseño arquitectónico iterativo asistido por IA 🚀
