<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * Spanish language strings for local_saipa.
 *
 * @package    local_saipa
 * @copyright  2026 Schaller & Ponce <dev@schaller-ponce.com.ar>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

$string['pluginname'] = 'SAIPA - Sistema Agéntico de Intervención Pedagógica Adaptativa';

$string['settings:engine_url']        = 'URL del Motor SAIPA';
$string['settings:engine_url_desc']   = 'URL del servicio FastAPI saipa-engine (ej. http://host.docker.internal:8052)';
$string['settings:engine_token']      = 'Token de API';
$string['settings:engine_token_desc'] = 'Token Bearer para autenticar peticiones al saipa-engine';
$string['settings:whatsapp_provider'] = 'Proveedor WhatsApp';
$string['settings:whatsapp_provider_desc'] = 'Seleccionar proveedor de WhatsApp Business API (twilio o meta)';
$string['settings:twilio_sid']        = 'Twilio Account SID';
$string['settings:twilio_token']      = 'Twilio Auth Token';
$string['settings:twilio_from']       = 'Número WhatsApp de salida (Twilio)';
$string['settings:heading_engine']    = 'Conexión al Motor SAIPA';
$string['settings:heading_whatsapp']  = 'Configuración de WhatsApp';

$string['saipa:view']    = 'Ver panel SAIPA';
$string['saipa:manage']  = 'Administrar configuración de SAIPA';
$string['saipa:chat']    = 'Usar el asistente de chat SAIPA';

$string['healthcheck:ok']      = 'El Motor SAIPA responde correctamente';
$string['healthcheck:fail']    = 'No se puede alcanzar el Motor SAIPA en la URL configurada';
$string['healthcheck:heading'] = 'Prueba de Conexión al Motor';
