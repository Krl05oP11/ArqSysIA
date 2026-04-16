# PROJECT CHARTER — SAIPA + EVAL-IA

## Vision

Publicar SAIPA y EVAL-IA en el Moodle Marketplace (inauguracion junio 2026) como
productos comerciales listos para produccion, con documentacion profesional,
cumplimiento de todos los requisitos tecnicos del Plugin Directory y una
arquitectura SaaS-friendly que permita vender suscripciones al backend.

## Non-goals (lo que este proyecto NO es)

- NO estamos desarrollando features nuevas (el feature set de v0.5.1 / v0.4.8 es final).
- NO estamos migrando a otra arquitectura (engine, Docker, RAG quedan como estan).
- NO estamos publicando el engine como open source (es IP comercial separada).
- NO estamos construyendo un sistema de licencias/activation keys (eso es post-publicacion).
- NO estamos haciendo QA exhaustivo de toda la UI (solo smoke tests de los flujos criticos).

## Decisiones de diseno fundamentales

| # | Decision | Razon |
|---|----------|-------|
| 1 | Plugins GPL v3, engine propietario | GPL es obligatorio para Moodle; el engine (donde esta la IP real) queda fuera del ZIP publicado. |
| 2 | Un manual de instalacion + uno de usuario por plugin | Marketplace pide documentacion; 4 documentos cubren todos los roles y escenarios. |
| 3 | CI con GitHub Actions (PHPUnit + Behat) | El Plugin Directory espera tests automatizados; sin CI la aprobacion se complica. |
| 4 | Maturity BETA para ambos | ALPHA ahuyenta adoptantes; STABLE requiere mas rodaje del que tenemos. BETA es el sweet spot. |
| 5 | Mismo CSS/formato HTML para los 4 manuales | Coherencia visual, exportacion A4 PDF uniforme, mantenimiento simple. |
| 6 | Screenshots ya capturadas (8+8) son finales | No invertir mas tiempo en capturas salvo que cambie la UI (no deberia, ver non-goal 1). |
| 7 | i18n completa EN+ES; pt_br es opcional | EN es obligatorio para el Directory; ES es nuestro mercado; pt_br es nice-to-have. |

## Criterios de exito

- [ ] SAIPA pasa PHPCS con cero errores.
- [ ] EVAL-IA pasa PHPCS con cero errores.
- [ ] Ambos plugins tienen GitHub Actions CI verde (PHPUnit).
- [ ] Ambos plugins tienen archivo LICENSE, icon, CHANGES.md, README.md, privacy provider.
- [ ] EVAL-IA sube a MATURITY_BETA.
- [ ] Los 4 manuales (2 instalacion + 2 usuario) estan completos y exportados a PDF.
- [ ] package.sh genera ZIPs limpios para ambos plugins.
- [ ] Smoke test: instalar desde ZIP en un Moodle limpio y completar el wizard sin errores.

## Equipo

- **Carlos Ponce** — direccion de producto, decisiones de negocio, testing manual, validacion final.
- **Claude** — ingenieria, codigo, documentacion tecnica, CI, testing automatizado.
