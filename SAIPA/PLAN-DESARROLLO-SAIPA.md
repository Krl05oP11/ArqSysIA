# SAIPA — Plan de Desarrollo Detallado
**Versión:** 1.0 | **Fecha:** 2026-03-16 | **Autor:** Claude + Carlos Schaller

---

## 1. Visión General del Sistema

SAIPA es un **ecosistema de acompañamiento pedagógico** compuesto por tres capas tecnológicas distintas que deben funcionar en armonía:

```
CAPA 1 — Moodle (PHP 8.1+)
  └── Plugin local_saipa    ← núcleo: DB, cron, eventos, admin, web services
  └── Plugin block_saipa    ← widget UI: chat del estudiante en el curso
  └── Plugin message_output_saipa  ← canal WhatsApp en notificaciones de Moodle

CAPA 2 — Backend IA (Python / FastAPI)
  └── saipa_bridge.py       ← puente HTTP (puerto 8052, igual patrón que UCTP-IA)
  └── rag/                  ← LangChain + ChromaDB + Ollama (Qwen 2.5 14B)
  └── analytics/            ← scikit-learn: modelo de riesgo de abandono
  └── whatsapp/             ← cliente Meta Cloud API / Twilio

CAPA 3 — Servicios Externos
  └── WhatsApp Business API (Meta Cloud API o Twilio)
  └── Ollama (LLM local, ya disponible en el servidor)
  └── ChromaDB (vector store, mismo host)
```

---

## 2. Requisitos de Aceptación en el Plugin Directory de Moodle

### 2.1 Archivos OBLIGATORIOS por tipo de plugin

#### `local_saipa/`
```
local/saipa/
├── version.php                    ← OBLIGATORIO
├── db/
│   ├── access.php                 ← OBLIGATORIO (capabilities)
│   ├── install.xml                ← OBLIGATORIO si usa tablas propias (XML, no PHP)
│   ├── upgrade.php                ← OBLIGATORIO para migraciones de versión
│   ├── services.php               ← web services (API REST para JS/Python)
│   ├── tasks.php                  ← tareas programadas (cron)
│   └── events.php                 ← observadores de eventos Moodle
├── lang/
│   ├── en/local_saipa.php         ← OBLIGATORIO (inglés mínimo)
│   └── es/local_saipa.php         ← español
├── classes/
│   ├── privacy/provider.php       ← OBLIGATORIO GDPR (almacena datos personales)
│   ├── external/                  ← web services (namespaced, Moodle 4.2+)
│   │   ├── chat.php
│   │   ├── risk.php
│   │   └── notifications.php
│   ├── task/
│   │   ├── risk_evaluation.php    ← tarea diaria: calcula riesgo abandono
│   │   ├── index_course.php       ← adhoc: re-indexa curso en ChromaDB
│   │   └── weekly_summary.php    ← tarea semanal: resúmenes de progreso
│   └── event/
│       └── observer.php           ← reacciona a eventos Moodle (login, submit, etc.)
├── settings.php                   ← página admin: URL bridge Python, token API
└── tests/
    ├── privacy_test.php
    └── behat/saipa.feature
```

#### `block_saipa/`
```
blocks/saipa/
├── version.php                    ← OBLIGATORIO
├── block_saipa.php                ← OBLIGATORIO (clase principal extiende block_base)
├── edit_form.php                  ← configuración por instancia del bloque
├── db/
│   └── access.php                 ← OBLIGATORIO
├── lang/
│   ├── en/block_saipa.php         ← OBLIGATORIO
│   └── es/block_saipa.php
├── pix/
│   ├── icon.svg                   ← OBLIGATORIO (preferido)
│   └── icon.png                   ← OBLIGATORIO (fallback)
├── amd/
│   ├── src/chat.js                ← módulo JS del chat (RequireJS/ESM)
│   └── build/chat.min.js          ← versión minificada para producción
├── templates/
│   └── chat_widget.mustache       ← template Mustache para el widget
└── classes/
    └── privacy/provider.php       ← OBLIGATORIO GDPR
```

#### `message/output/saipa/`
```
message/output/saipa/
├── version.php                    ← OBLIGATORIO
├── message_output_saipa.php       ← OBLIGATORIO (extiende message_output)
├── db/
│   ├── access.php                 ← OBLIGATORIO
│   └── install.php                ← OBLIGATORIO: registra en tabla message_processors
├── lang/
│   └── en/message_output_saipa.php ← OBLIGATORIO (incluye 'pluginname')
└── settings.php                   ← config admin del canal (token, proveedor)
```

### 2.2 `version.php` — formato exacto Moodle 4.4

```php
<?php
defined('MOODLE_INTERNAL') || die();

$plugin->component = 'local_saipa';       // frankenstyle: type_name
$plugin->version   = 2026031600;          // yyyymmddHH
$plugin->requires  = 2024042200;          // Moodle 4.4 mínimo
$plugin->maturity  = MATURITY_ALPHA;      // ALPHA → BETA → RC → STABLE
$plugin->release   = '0.1.0';
$plugin->supported = [404, 405];          // rango de versiones Moodle soportadas
$plugin->dependencies = [
    'block_saipa' => 2026031600,
];
```

Tabla de versiones Moodle:
- `2022041900` = Moodle 4.0
- `2023042400` = Moodle 4.2
- `2024042200` = Moodle 4.4 ← target mínimo
- `2025041500` = Moodle 4.5

### 2.3 APIs de Seguridad — uso OBLIGATORIO

```php
// Al inicio de cada página PHP
require_login($course, true, $cm);
require_capability('local/saipa:view', $context);

// En formularios POST (CSRF)
require_sesskey();   // o: data_submitted() && confirm_sesskey()

// Parámetros de entrada — NUNCA $_GET/$_POST directo
$courseid = required_param('courseid', PARAM_INT);
$search   = optional_param('q', '', PARAM_TEXT);

// Base de datos — NUNCA SQL crudo
$record = $DB->get_record('saipa_sessions', ['userid' => $userid]);
$DB->insert_record('saipa_messages', $data);
```

### 2.4 Privacy API — OBLIGATORIO (almacenamos datos personales)

```php
// classes/privacy/provider.php
namespace local_saipa\privacy;

class provider implements
    \core_privacy\local\metadata\provider,
    \core_privacy\local\request\userlist_provider,
    \core_privacy\local\request\approved_deleter {

    public static function get_metadata(collection $c): collection {
        $c->add_database_table('saipa_messages', [
            'userid'      => 'privacy:metadata:userid',
            'message'     => 'privacy:metadata:message',
            'timecreated' => 'privacy:metadata:timecreated',
        ], 'privacy:metadata:messages');

        $c->add_database_table('saipa_risk_scores', [
            'userid'     => 'privacy:metadata:userid',
            'score'      => 'privacy:metadata:score',
            'factors'    => 'privacy:metadata:factors',
        ], 'privacy:metadata:risk');

        $c->add_external_location_link('whatsapp', [
            'phonenumber' => 'privacy:metadata:phonenumber',
            'message'     => 'privacy:metadata:message',
        ], 'privacy:metadata:whatsapp');

        return $c;
    }

    // + export_user_data(), delete_data_for_user(), etc.
}
```

### 2.5 Coding Standards
- PHPCS con estándar `moodle` (moodle-cs)
- Licencia GPL v3 en header de cada archivo PHP
- Indentación: 4 espacios (no tabs)
- Strings en lang files (nunca hardcodeados)
- Sin `var_dump`, `die()`, `print_r` en producción
- Tests: PHPUnit + Behat (necesarios para publicación en directorio)

---

## 3. Esquema de Base de Datos (`db/install.xml`)

```xml
<!-- Tablas propias de local_saipa -->

saipa_sessions       ← sesiones de chat (userid, courseid, contexto)
saipa_messages       ← historial mensajes (sessionid, role, content, timecreated)
saipa_risk_scores    ← scores de riesgo diarios (userid, courseid, score, factors, timecomputed)
saipa_phone_verify   ← verificación OTP WhatsApp (userid, phone, otp, verified, timecreated)
saipa_notifications  ← log de mensajes WhatsApp enviados (userid, template, status, timesent)
saipa_feedback       ← thumbs up/down por respuesta del asistente (messageid, rating, comment)
saipa_course_index   ← estado de indexación RAG por curso (courseid, last_indexed, chunk_count)
```

---

## 4. Stack Tecnológico Definitivo

| Componente | Tecnología | Justificación |
|---|---|---|
| Plugin PHP | Moodle 4.4 / PHP 8.1 | Estándar del ecosistema |
| UI widget | Mustache + AMD JS | Nativo Moodle (no React externo) |
| Backend IA | Python 3.11 / FastAPI | Mismo patrón que UCTP-IA |
| LLM | Ollama + Qwen 2.5 14B | Ya disponible en servidor, privado |
| Embeddings | all-MiniLM-L6-v2 | sentence-transformers, ligero y preciso |
| Vector store | ChromaDB | Simple, embebido, escalable a pgvector |
| Orquestación RAG | LangChain | Mayor soporte que Flowise para Python |
| Riesgo abandono | scikit-learn (XGBoost) | Bien integrado con datos de Moodle |
| WhatsApp | Meta Cloud API | Gratuito hasta 1000 conv/mes |
| Base de datos | PostgreSQL | Consistente con UCTP-IA |

---

## 5. Roadmap de Desarrollo — 5 Fases

### FASE 0 — Spike Técnico (2 semanas)
**Objetivo:** Probar conectividad Moodle ↔ Python ↔ WhatsApp end-to-end

**Tareas:**
- [ ] Levantar Moodle 4.4 + PostgreSQL en Docker local
- [ ] Crear esqueleto mínimo de `local_saipa` (version.php + settings.php)
- [ ] Crear `saipa_bridge.py` (FastAPI, puerto 8052)
- [ ] Configurar cuenta Meta Cloud API (sandbox WhatsApp)
- [ ] Enviar primer mensaje WhatsApp desde Moodle vía Python bridge
- [ ] Leer calificaciones de un curso de prueba desde el bridge

**Entregable:** Botón en Moodle → "Hola {nombre}" por WhatsApp en <3 segundos.

---

### FASE 1 — MVP: Chat + Mensajería Básica (4 semanas)
**Objetivo:** Plugin instalable con chat funcional y envío manual de mensajes.

**Tareas PHP (Moodle):**
- [ ] `block_saipa`: widget de chat (template Mustache + AMD JS + AJAX)
- [ ] `local_saipa`: web services para recibir/enviar mensajes del widget
- [ ] `message_output_saipa`: canal WhatsApp en sistema de notificaciones Moodle
- [ ] Panel docente básico: tabla de estudiantes + botón "Enviar recordatorio"
- [ ] Verificación de número celular (OTP por WhatsApp)
- [ ] Privacy API completa
- [ ] Página de settings admin: URL bridge, token, proveedor WhatsApp

**Tareas Python (Bridge):**
- [ ] Endpoint `/chat`: recibe mensaje, consulta RAG básico, retorna respuesta
- [ ] Endpoint `/whatsapp/send`: envía mensaje a número de teléfono
- [ ] Indexación inicial: descripción del curso + actividades + fechas de entrega
- [ ] ChromaDB setup + embeddings con all-MiniLM-L6-v2

**Entregable:** Plugin .zip instalable con chat funcional y mensajería WhatsApp manual.

---

### FASE 2 — Asistente RAG Completo (4 semanas)
**Objetivo:** El asistente responde preguntas del curso con ≥80% de precisión.

**Tareas PHP:**
- [ ] Scheduled task: re-indexa ChromaDB cuando se modifica contenido del curso
- [ ] Observer de eventos: `\core\event\course_module_updated` → adhoc task
- [ ] Historial de conversación persistente en DB (`saipa_sessions` + `saipa_messages`)
- [ ] Panel docente: visor de conversaciones por estudiante
- [ ] Feedback 👍/👎 por respuesta (alimenta fine-tuning futuro)

**Tareas Python:**
- [ ] RAG con contexto por rol (respuestas distintas para estudiante vs docente)
- [ ] Indexación de recursos: PDFs, páginas de contenido, foros, asignaciones
- [ ] Endpoint `/whatsapp/receive`: webhook para responder consultas por WhatsApp
- [ ] Gestión de contexto conversacional (últimos N mensajes como historial)

**Entregable:** "¿Cuándo vence el TP2?" → respuesta con fecha exacta del curso.

---

### FASE 3 — Analítica Predictiva (4 semanas)
**Objetivo:** Detectar estudiantes en riesgo y alertar automáticamente.

**Features del modelo (extraídas de Moodle logs):**
- Días desde último acceso al curso
- % de actividades completadas sobre el total
- Promedio de calificaciones últimas 2 semanas
- Participación en foros (posts enviados últimos 7 días)
- Tareas entregadas tarde vs a tiempo
- Tiempo total en plataforma (minutos/semana)

**Tareas Python:**
- [ ] Script de extracción de features desde DB de Moodle
- [ ] Entrenamiento del modelo XGBoost (dataset sintético inicial + datos reales)
- [ ] Endpoint `/risk/evaluate`: evalúa riesgo de un estudiante, retorna score + factores
- [ ] Endpoint `/risk/batch`: evalúa todos los estudiantes de un curso

**Tareas PHP:**
- [ ] Scheduled task diario: llama `/risk/batch`, guarda en `saipa_risk_scores`
- [ ] Panel docente avanzado: semáforo ROJO/AMARILLO/VERDE por estudiante con factores
- [ ] Alerta automática WhatsApp cuando riesgo = ALTO (con control docente on/off)
- [ ] "Vista de calor de la clase": gráfico de engagement global del curso

**Entregable:** Dashboard con semáforo de riesgo + alertas WhatsApp automáticas.

---

### FASE 4 — Personalización y Publicación (4 semanas)
**Objetivo:** Funcionalidades avanzadas + plugin listo para Moodle Plugin Directory.

**Tareas:**
- [ ] Resúmenes semanales automáticos de progreso (LLM genera texto personalizado)
- [ ] Generación de borradores de rúbricas para docentes
- [ ] Soporte multiidioma: es, en, pt
- [ ] Fine-tuning con datos de feedback acumulados (opcional si hay suficientes datos)
- [ ] Tests PHPUnit completos para todas las clases
- [ ] Tests Behat para flujos principales (chat, alerta, panel docente)
- [ ] README.md + CHANGELOG.md + LICENSE
- [ ] Verificación PHPCS completa (moodle coding standard)
- [ ] Compatibilidad verificada: Moodle 4.2, 4.3, 4.4, 4.5
- [ ] Empaquetado y envío al Plugin Directory

**Entregable:** Plugin publicado en moodle.org/plugins con MATURITY_STABLE.

---

## 6. Estructura de Directorios del Proyecto

```
/home/carlos/Projects/SAIPA/
├── Documento Fundacional de SAIPA.txt
├── PLAN-DESARROLLO-SAIPA.md         ← este archivo
├── moodle-plugin/
│   ├── local_saipa/                 ← plugin PHP núcleo
│   ├── blocks/saipa/                ← plugin PHP widget UI
│   └── message/output/saipa/        ← plugin PHP canal WhatsApp
├── saipa-bridge/                    ← FastAPI Python
│   ├── main.py
│   ├── requirements.txt
│   ├── rag/
│   │   ├── indexer.py               ← indexa cursos en ChromaDB
│   │   └── retriever.py             ← consultas RAG
│   ├── analytics/
│   │   ├── features.py              ← extracción de features
│   │   └── risk_model.py            ← modelo XGBoost
│   └── whatsapp/
│       ├── sender.py                ← envío de mensajes
│       └── webhook.py               ← recepción de mensajes entrantes
├── docker/
│   ├── docker-compose.yml           ← Moodle 4.4 + PostgreSQL + ChromaDB
│   └── moodle.env
└── docs/
    ├── api-reference.md
    └── installation.md
```

---

## 7. Decisiones Pendientes (a confirmar con Carlos)

1. **Proveedor WhatsApp:**
   - **Meta Cloud API** (recomendado): gratuito hasta 1000 conversaciones/mes, requiere verificación de negocio (2-6 semanas). Ideal para producción.
   - **Twilio**: más simple de configurar, pago desde el primer mensaje (~$0.005/msg). Ideal para la Fase 0 de prueba.
   - **Decisión sugerida:** Twilio para Fase 0-1, migrar a Meta para producción.

2. **¿Distribuir como 2 o 3 plugins?**
   - 2 plugins (`local_saipa` + `block_saipa`, con `message_output` integrado en `local`) simplifica la instalación del cliente.
   - 3 plugins es más limpio arquitectónicamente y permite al cliente desactivar el canal WhatsApp si no lo usa.
   - **Decisión sugerida:** 3 plugins separados (más profesional para el directorio).

3. **¿Moodle mínimo soportado?**
   - Moodle 4.2 (PHP 8.0) amplía mercado.
   - Moodle 4.4 (PHP 8.1) simplifica el desarrollo (APIs más modernas).
   - **Decisión sugerida:** Moodle 4.2 como mínimo, 4.4+ recomendado.

---

## 8. Lo Que Necesitamos Para Empezar (Fase 0)

| Recurso | Estado | Acción |
|---|---|---|
| Docker + Moodle 4.4 | Pendiente | `docker-compose.yml` a crear |
| Python 3.11 + venv | Disponible | Ya en el servidor |
| Ollama + Qwen 2.5 14B | Disponible | Ya instalado (UCTP-IA) |
| ChromaDB | Pendiente | `pip install chromadb` |
| Twilio (prueba) | Pendiente | Crear cuenta gratuita |
| sentence-transformers | Pendiente | `pip install sentence-transformers` |

**Tiempo estimado Fase 0:** 2 semanas a tiempo parcial.
**Tiempo estimado MVP (Fase 1):** 6 semanas desde inicio.
**Tiempo estimado sistema completo:** 4-5 meses.
