# Plan activo — Marketplace Readiness

**Objetivo**: dejar ambos plugins listos para submission al Moodle Marketplace.
**Fecha inicio**: 2026-04-15
**Deadline externo**: junio 2026 (inauguracion Marketplace)

---

## Dia 1 — 2026-04-15 (hoy)

- [x] B1: Crear archivo LICENSE (GPL v3) para EVAL-IA
- [x] B2: Crear pix/icon.svg para EVAL-IA (purpura, clipboard+checkmarks+sparkle)
- [x] B3: Crear .phpcs.xml.dist para EVAL-IA (PHPCS no disponible local — se validara en CI)
- [x] B4: Subir maturity a MATURITY_BETA en version.php de EVAL-IA
- [ ] Commit: manual de usuario EVAL-IA + B1-B4 cambios
- [ ] Push (con autorizacion)

## Dia 2 — CI

- [ ] R1: GitHub Actions workflow phpunit.yml para SAIPA
- [ ] R1: GitHub Actions workflow phpunit.yml para EVAL-IA
- [ ] R4: package.sh para ambos plugins

## Dia 3 — Tests

- [ ] R2: Behat features para EVAL-IA (flujo rubrica -> preguntas -> examen)
- [ ] R3: PHPUnit adicionales para SAIPA v0.5.0 WS (9 nuevos)

## Post-cierre (si hay tiempo)

- [ ] O3: Asistente SAIPA con tool-use (LangChain function calling)
- [ ] O2: Lang pt_br para EVAL-IA
- [ ] Investigacion requisitos oficiales Marketplace cuando abran inscripcion

---

## Completado

- [x] i18n setup wizard EVAL-IA steps 4-6 (2026-04-13)
- [x] i18n setup wizard SAIPA 7 steps completo (2026-04-13)
- [x] Screenshots 8+8 (2026-04-13)
- [x] Manual instalacion SAIPA (existia, backport page-break 2026-04-15)
- [x] Manual instalacion EVAL-IA (2026-04-15)
- [x] Manual usuario SAIPA (2026-04-15)
- [x] Manual usuario EVAL-IA (2026-04-15)
