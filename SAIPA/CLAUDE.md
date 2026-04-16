# SAIPA — Instrucciones para Claude Code

## ¿Qué es SAIPA?
Plugin de acompañamiento pedagógico para Moodle 4.x con IA embebida.
Detecta riesgo de abandono (XGBoost), ofrece chat RAG por rol (LangChain + ChromaDB + Ollama)
y envía alertas proactivas a estudiantes vía Telegram/WhatsApp.
Cliente objetivo: universidades latinoamericanas que ya usan Moodle.

---

## Arquitectura — 3 capas

```
CAPA 1 — Moodle (PHP 8.1+) — puerto 8081
  ├── local_saipa/    ← núcleo: DB, cron, eventos, web services (20+ WS)
  ├── block_saipa/    ← widget UI del chat en el bloque del curso
  └── message/        ← canal de mensajería (Telegram/WhatsApp en Moodle)

CAPA 2 — saipa-engine (Python / FastAPI) — puerto 8052
  ├── rag/            ← LangChain + ChromaDB + Ollama (qwen2.5:14b)
  ├── analytics/      ← XGBoost dropout risk (11 features)
  ├── telegram/       ← bot polling + webhook + moodle.py
  └── whatsapp/       ← Evolution API (Baileys) para dev

CAPA 3 — Servicios externos
  ├── Ollama localhost:11434 (en HOST, no en Docker)
  ├── Evolution API puerto 8055 (WhatsApp)
  └── Telegram Bot API (polling mode activo)
```

---

## Ubicaciones clave

```
/home/carlos/Projects/SAIPA/
├── CLAUDE.md                        ← este archivo
├── PLAN-DESARROLLO-SAIPA.md         ← plan de fases completo
├── README.md                        ← estado actualizado del proyecto
├── moodle-plugins/
│   ├── local_saipa/                 ← plugin principal
│   │   ├── lib.php                  ← local_saipa_engine_request() vive aquí
│   │   ├── teacher.php              ← panel docente URL: localhost:8081/local/saipa/teacher.php?courseid=2
│   │   ├── classes/external/        ← 20 web services (PHP classes)
│   │   ├── amd/src/                 ← JS fuente (teacher_dashboard.js, etc.)
│   │   ├── amd/build/              ← JS minificado (copiar manualmente en dev)
│   │   ├── db/services.php          ← registro de WS
│   │   ├── db/upgrade.php           ← migraciones de versión
│   │   └── db/install.xml           ← schema inicial de tablas
│   ├── block_saipa/
│   └── message/
├── saipa-engine/
│   ├── main.py                      ← FastAPI app (v0.2.0)
│   ├── config.py                    ← configuración centralizada
│   ├── rag/                         ← pipeline RAG
│   ├── analytics/                   ← XGBoost model
│   ├── telegram/
│   │   ├── webhook.py               ← handler de mensajes + mark_alert_responded
│   │   ├── moodle.py                ← WS calls a Moodle
│   │   └── polling.py               ← polling loop (activo cuando TELEGRAM_WEBHOOK_URL vacío)
│   ├── routers/                     ← endpoints FastAPI
│   ├── tests/                       ← pytest (6/6 pasan)
│   └── venv/                        ← SIEMPRE usar ./venv/bin/python
└── docker/
    ├── docker-compose.yml
    ├── saipa-engine.env             ← vars del engine (MOODLE_URL, TOKEN, TELEGRAM, etc.)
    └── moodle.env
```

---

## Comandos de desarrollo — usar SIEMPRE estos

```bash
# Arrancar todo
cd /home/carlos/Projects/SAIPA/docker && docker compose up -d

# Ver logs del engine en tiempo real
docker logs saipa-saipa-engine --tail 30 -f

# Después de cambiar PHP (upgrade + purge caches)
docker exec saipa-moodle php /var/www/html/admin/cli/upgrade.php --non-interactive
docker exec saipa-moodle php /var/www/html/admin/cli/purge_caches.php

# Después de cambiar Python en saipa-engine (rebuild + recreate)
cd /home/carlos/Projects/SAIPA/docker
docker compose build saipa-engine && docker compose up -d --force-recreate saipa-engine

# Después de cambiar JS en amd/src/ (copiar build manualmente en dev)
SRC=/home/carlos/Projects/SAIPA/moodle-plugins/local_saipa/amd
cp $SRC/src/teacher_dashboard.js    $SRC/build/teacher_dashboard.min.js
cp $SRC/src/my_courses_dashboard.js $SRC/build/my_courses_dashboard.min.js
cp $SRC/src/advisor_dashboard.js    $SRC/build/advisor_dashboard.min.js
# Luego purge_caches (ver arriba)

# Correr tests del engine
cd /home/carlos/Projects/SAIPA/saipa-engine && ./venv/bin/pytest tests/ -v

# Incrementar versión del plugin (OBLIGATORIO antes de upgrade.php)
# Editar version.php: version = YYYYMMDDNN, release = X.Y.Z
```

---

## Versiones actuales (2026-03-27)

| Componente | Versión |
|-----------|---------|
| local_saipa | 2026032403 / 0.5.0 |
| block_saipa | 2026032401 / 0.5.0 |
| saipa-engine | v0.2.0 |
| Moodle | 4.4 en Docker (puerto 8081) |
| Modelo LLM | qwen2.5:14b-16k via Ollama |
| XGBoost | 11 features, entrenado con datos sintéticos |

---

## Estado de desarrollo (2026-03-27)

### Completado ✅
- **Fase 1**: Chat web, historial, panel docente, feedback 👍/👎, indexado RAG
- **Fase 2**: RAG por rol, WhatsApp (infraestructura lista, bloqueada por WhatsApp rate-limit)
- **Fase 3**: XGBoost dropout risk, 11 features, badges 🟢🟡🔴, demo mode
- **Fase 4**: Telegram bidireccional, alertas proactivas docente→alumno, métricas de engagement
- **Consolidación v0.4.2**: bugs críticos corregidos, schema sincronizado, CORS seguro, cron validado
- **Fase 5** (v0.4.2): LICENSE, CHANGES.md, privacy/provider.php, PHPUnit, Behat, PHPCS, package.sh, MATURITY_BETA
- **Fase 6** (v0.5.0): Dashboard asesor 5 tabs, my_courses.php, barra métricas teacher, 9 nuevos WS (30 total), 3 nuevas tablas, asistente SAIPA (FAB)
- **Infraestructura pública** (2026-03-27): `https://demo.saipa.online` + `https://engine.saipa.online` operativos con SSL Let's Encrypt

### Detalles Fase 6 — v0.5.0 (2026-03-26)
- **Tablas nuevas**: `saipa_course_settings`, `saipa_daily_stats`, `saipa_risk_history`
- **Capabilities**: `local/saipa:viewall`, `local/saipa:advisor`
- **Cron**: `aggregate_daily_stats` (03:00 diario, disabled=1 por defecto)
- **WS** (30 total): get_course_summary, get_my_courses, get_institution_summary, get_risk_dashboard,
  get_engagement_stats, get_course_settings, set_course_settings, save_institution_config, **admin_chat**
- **Páginas**: `my_courses.php` (multi-curso), `advisor.php` (5 tabs institucionales)
- **Asistente SAIPA**: FAB arrastrable (posición persiste en localStorage), panel de chat, engine endpoint
  `/chat/advisor`, WS `local_saipa_admin_chat`; disponible en `advisor.php`
- **Idioma**: pack `es` instalado, sitio y usuarios admin/teacher1 en español
- **Datos demo**: `scripts/seed_demo_full.py` — 32 alumnos, 5 perfiles, 8 semanas de historial completo
- URLs: `http://localhost:8081/local/saipa/advisor.php` | `http://localhost:8081/local/saipa/my_courses.php`

### Infraestructura pública — COMPLETA ✅
- **IP pública fija**: `190.211.89.27`
- **Port forwarding activo**: `80→80`, `443→443` (ISP configuró hoy)
- **Dominio**: `saipa.online` en DonWeb
  - `demo.saipa.online` → `190.211.89.27` ✅
  - `engine.saipa.online` → `190.211.89.27` ✅
- **SSL**: Certbot Let's Encrypt, válido hasta 2026-06-25, auto-renovación activa
- **Apache**: VirtualHosts con `X-Forwarded-Proto` + Moodle `sslproxy=true`
- **Moodle wwwroot**: `https://demo.saipa.online`

### Bloqueado ⚠️
- WhatsApp QR: Evolution API llega a estado `connecting` pero WhatsApp no envía challenge QR.
  - **Causa**: Rate-limit de WhatsApp (4+ intentos fallidos desde 20/03 + logout 401).
  - **Solución**: Han pasado >7 días desde el último intento — probar el re-scan.
  - **Para reintentar**: `curl -X GET -H "apikey: saipa_evolution_key" http://localhost:8055/instance/connect/saipa_whatsapp`
    Si devuelve `base64`, escanear con el celular.

---

## Convenciones críticas — LEER ANTES DE TOCAR CÓDIGO

### PHP / Moodle

1. **Strings PHP siempre con comillas simples**
   ```php
   // CORRECTO
   $string['alert_message'] = 'Hola {$a->student}, tienes riesgo de abandono.';
   // MAL — PHP interpola y vacía los placeholders
   $string['alert_message'] = "Hola {$a->student}, tienes riesgo de abandono.";
   ```

2. **HTTP requests al engine: NUNCA usar `\curl` de Moodle — usar PHP nativo**
   ```php
   // CORRECTO: curl_init() + curl_setopt_array() en lib.php → local_saipa_engine_request()
   // MAL: new \curl() → retorna respuesta vacía sin error visible
   ```

3. **AMD builds: siempre copiar src → build después de editar JS**
   ```bash
   cp amd/src/teacher_dashboard.js amd/build/teacher_dashboard.min.js
   # Si el archivo tiene permisos root: sudo cp
   ```

4. **JavaScript AMD en Moodle usa jQuery Deferreds, NO Promises nativas**
   ```javascript
   // CORRECTO
   Ajax.call([...])[0].then(success).fail(error).always(cleanup);
   // MAL — .catch() y .finally() no existen en jQuery Deferreds
   ```

5. **External PHP classes necesitan require_once explícito para lib.php**
   ```php
   // Al inicio de cualquier clase en classes/external/:
   require_once($CFG->dirroot . '/local/saipa/lib.php');
   ```

6. **Versión del plugin**: siempre incrementar `version` en `version.php` antes de
   cualquier cambio que requiera `upgrade.php`. Formato: `YYYYMMDDNN` (NN = 00-99).

### Python / saipa-engine

1. **Entorno virtual**: `./venv/bin/python` SIEMPRE — nunca `python3` del sistema
2. **MOODLE_URL debe ser `http://localhost:8081`** (coincide con wwwroot de Moodle)
   - Usar `saipa-moodle:8080` NO funciona porque Moodle redirige 303 → localhost:8081
   - El docker-compose.yml tiene `localhost:host-gateway` en extra_hosts por esto
3. **course_id=0**: cuando `saipa_sessions` está vacío para un user, `telegram_get_session`
   retorna course_id=0. Siempre castear: `course_id = int(session.get("course_id") or 0)`

### Docker

1. Puerto 8080 ocupado por open-webui (proceso host) — Moodle está en 8081 de forma permanente
2. Si el engine no levanta: verificar que uvicorn no corra en el host (`ss -tlnp | grep 8052`)

---

## Configuración activa en docker/saipa-engine.env

```
MOODLE_URL=http://localhost:8081
MOODLE_TOKEN=81e88908efd1db93ce3858b6c36f5475
TELEGRAM_BOT_TOKEN=8632554631:AAGDF8yl24-HJsnJtGCsHn2SD6AIIvRybuE
TELEGRAM_BOT_USERNAME=saipa_asistente_bot
TELEGRAM_WEBHOOK_URL=  ← vacío = polling mode activo
```

## Usuarios de prueba

| Usuario | Contraseña | Rol | Telegram |
|---------|------------|-----|----------|
| admin | (el de siempre) | Site Admin | — |
| teacher1 | Teacher1234! | editingteacher | — |
| carlosponce | (el suyo) | student | ✅ chat_id=8591829566 |
| rotundo.mamerto / ana.garcia / luis.martinez / sofia.lopez / diego.fernandez / valeria.torres | Demo1234! / Student1234! | student | — |

URL panel docente: `http://localhost:8081/local/saipa/teacher.php?courseid=2`

---

## Nivel de autonomía

- **Código PHP/Python/JS**: proceder directamente. No pedir confirmación para edits.
- **`upgrade.php` + `version.php`**: proceder, pero mostrar el diff antes de ejecutar el upgrade.
- **`install.xml`** (schema de tablas): mostrar plan y pedir confirmación — afecta instalaciones limpias.
- **`docker-compose.yml`** o variables de entorno: mostrar cambio y confirmar antes de aplicar.
- **`db/services.php`** (registro de WS): proceder, pero recordar que requiere upgrade + purge.
- **Git push / publicación**: NUNCA sin autorización explícita.

---

## Orquestacion — Regla anti-drift

**Archivos ancla** (leer al inicio de cada sesion):
- `docs/PROJECT_CHARTER.md` — vision, non-goals, decisiones de diseno, criterios de exito
- `tasks/current-plan.md` — roadmap activo con tareas pendientes y completadas
- `tasks/parking-lot.md` — ideas/tangentes capturadas para revision posterior

**Regla de conducta**: cuando el usuario introduzca un tema no previsto en `current-plan.md`,
Claude debe decir explicitamente: *"Esto no esta en el plan actual (estabamos en X). Lo anoto
al parking lot y seguimos, o pivoteamos?"* y esperar decision. No continuar en silencio.

---

## Proceso de trabajo en SAIPA

1. Antes de tocar PHP: verificar versión en version.php e incrementar si el cambio requiere upgrade
2. Después de PHP: `docker exec saipa-moodle php .../upgrade.php --non-interactive && purge_caches.php`
3. Después de JS: `cp amd/src/*.js amd/build/*.min.js` + purge_caches
4. Después de Python: `docker compose build saipa-engine && docker compose up -d --force-recreate saipa-engine`
5. Verificar con logs: `docker logs saipa-saipa-engine --tail 20`
6. Siempre probar el flujo completo (chat o alerta) después de cualquier cambio en la cadena
