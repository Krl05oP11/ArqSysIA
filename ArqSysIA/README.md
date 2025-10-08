# ArqSysIA

**Arquitecto de Sistemas con Inteligencia Artificial**

Aplicación de escritorio inteligente para asistir en el diseño y definición de arquitecturas de aplicaciones de software.

---

## 🎯 Visión

ArqSysIA automatiza y optimiza el proceso de arquitectura de software, reduciendo significativamente el tiempo y esfuerzo necesarios para:

- ✅ Analizar y documentar requerimientos
- ✅ Diseñar arquitecturas de sistemas
- ✅ Definir estructuras de archivos y componentes
- ✅ Identificar dependencias tecnológicas
- ✅ Generar documentación técnica (MVP y roadmap completo)

---

## 🏗️ Arquitectura

### Pipeline de Tres Fases

```
┌─────────────────────────────────────────────────────┐
│                 ArqSysIA Core                       │
│                                                     │
│  FASE 1: Analyzer    → DeepSeek-R1-32B            │
│  FASE 2: CodeGen     → DeepSeek-R1-32B            │
│  FASE 3: Validator   → DeepSeek-R1-32B            │
│                                                     │
│  State Manager       → JSON/YAML Persistence       │
│  Output Generator    → Documentos Técnicos         │
└─────────────────────────────────────────────────────┘
```

### Decisiones Clave

- **Pipeline Tradicional** (NO agentes) - Flujo lineal con control explícito
- **Un Solo Modelo** - DeepSeek-R1-32B para todas las fases (MVP)
- **Infraestructura Híbrida** - App en Docker + Ollama en host
- **Local-First** - Todo procesamiento en máquina local (privacidad total)

---

## 🚀 Estado del Proyecto

### ✅ Implementado (v0.1-alpha)

- **Cliente Ollama** - Comunicación robusta con modelos locales
- **State Manager** - Gestión completa del estado del proyecto
- **Analyzer (Fase 1)** - Análisis arquitectural profundo

### ⏳ En Desarrollo

- CodeGen (Fase 2) - Generación de código y estructura
- Validator (Fase 3) - Validación y mejoras
- Orchestrator - Coordinación de fases
- CLI Interactiva - Interfaz de usuario

---

## 🖥️ Requisitos

### Hardware Recomendado

- **CPU:** 8+ cores
- **RAM:** 32GB+ (64GB+ recomendado)
- **GPU:** NVIDIA con 16GB+ VRAM (para DeepSeek-R1-32B)
- **Storage:** 50GB+ libres

### Software

- **OS:** Linux (Ubuntu/Debian recomendado)
- **Python:** 3.11+
- **Ollama:** Instalado y corriendo
- **Modelos:** `deepseek-r1:32b` (19GB)

---

## 📦 Instalación

### 1. Clonar Repositorio

```bash
git clone https://github.com/[tu-usuario]/ArqSysIA.git
cd ArqSysIA
```

### 2. Instalar Ollama

```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve &
```

### 3. Descargar Modelo

```bash
ollama pull deepseek-r1:32b
```

### 4. Configurar Entorno Python

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Verificar Instalación

```bash
python test_ollama_client.py
python test_state_manager.py
python test_analyzer.py
```

---

## 🧪 Tests

Ejecutar todos los tests:

```bash
# Cliente Ollama
python test_ollama_client.py

# State Manager
python test_state_manager.py

# Analyzer (Fase 1)
python test_analyzer.py
```

---

## 📚 Documentación

- **[Documento Fundacional](arqsysia-foundational-doc.md)** - Diseño completo del sistema
- **[PROJECT_LOG.md](PROJECT_LOG.md)** - Bitácora de desarrollo
- **[Transfer Documents](Transfer_Document_2025-10-07.md)** - Documentos de transferencia entre sesiones

---

## 🛠️ Stack Tecnológico

- **Lenguaje:** Python 3.11+
- **IA Backend:** Ollama (local)
- **Modelo:** DeepSeek-R1-32B
- **Serialización:** JSON, YAML
- **Testing:** pytest (futuro)
- **Contenedores:** Docker (futuro)

---

## 📊 Performance

| Componente | Tiempo | VRAM |
|------------|--------|------|
| Cliente Ollama | ~10s | N/A |
| State Manager | <1s | N/A |
| Analyzer | ~4-5 min | ~15GB |

---

## 🤝 Contribuciones

Este es un proyecto personal en desarrollo activo. Actualmente no acepta contribuciones externas.

---

## 📝 Licencia

[Pendiente de definir]

---

## 👤 Autor

Desarrollador de Software IA  
Crespo, Entre Ríos, Argentina

---

## 🔄 Versión

**v0.1.0-alpha** - MVP en desarrollo

Última actualización: 7 de Octubre, 2025
