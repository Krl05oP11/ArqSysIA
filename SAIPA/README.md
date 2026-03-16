# SAIPA — Sistema Agéntico de Intervención Pedagógica Adaptativa

Sistema de acompañamiento pedagógico para Moodle con IA, analítica predictiva y mensajería WhatsApp.

## Fase actual: 0 — Spike Técnico

**Estado:** Esqueleto completo. Docker con Moodle 4.4 + PostgreSQL + saipa-engine corriendo.

## Inicio rápido

### 1. Levantar Moodle + PostgreSQL

```bash
cd /home/carlos/Projects/SAIPA/docker
docker compose up -d
```

Aguardar ~3-5 minutos. Seguir el progreso con `docker logs -f saipa-moodle`.
Cuando aparezca "Apache started", acceder a http://localhost:8080
- Usuario: `admin`
- Contraseña: `Admin1234!`

### 2. Instalar plugins en Moodle

Ir a: **Administración del sitio → Notifications → Upgrade Moodle database now**

Los tres plugins están montados via volúmenes Docker:
- `local/saipa` — núcleo, DB schema, configuración
- `blocks/saipa` — widget chat en páginas de curso
- `message/output/saipa` — canal WhatsApp (Fase 1)

### 3. Configurar saipa-engine

```bash
cd /home/carlos/Projects/SAIPA/saipa-engine
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tus valores (mínimo: SAIPA_API_TOKEN)
uvicorn main:app --host 0.0.0.0 --port 8052 --reload
```

### 4. Verificar conectividad

```bash
curl http://localhost:8052/health
# Respuesta esperada: {"status":"ok","message":"saipa-engine is running",...}
```

Desde Moodle: **Administración del sitio → Plugins → Local plugins → SAIPA**
- Setear Engine URL: `http://host.docker.internal:8052`
- Usar el web service `local_saipa_health_check` para confirmar la conexión

## Estructura del proyecto

```
docker/           docker-compose.yml + moodle.env
moodle-plugins/
  local_saipa/    Plugin núcleo (PHP, GPL v3)
  blocks/saipa/   Widget chat (PHP, GPL v3)
  message/        Canal WhatsApp (PHP, GPL v3)
    output/saipa/
saipa-engine/     Backend IA (Python/FastAPI, propietario)
  routers/        health.py, chat.py
  rag/            RAG pipeline — Fase 1
  analytics/      Risk model — Fase 3
  whatsapp/       Sender/webhook — Fase 1
docs/             Documentación técnica y comercial
```

## Hoja de ruta

| Fase | Objetivo | Estado |
|------|----------|--------|
| 0 | Docker + esqueleto plugins + saipa-engine base | ✅ Completada |
| 1 | Chat RAG funcional (LangChain + Ollama + ChromaDB) | Pendiente |
| 2 | Dashboard docente + alertas WhatsApp | Pendiente |
| 3 | Modelo predictivo de deserción (XGBoost) | Pendiente |
| 4 | Producción + integración continua | Pendiente |

## Licencia

- Plugins Moodle (`moodle-plugins/`): **GPL v3**
- saipa-engine: **Propietario** — © 2026 Schaller & Ponce. Todos los derechos reservados.
