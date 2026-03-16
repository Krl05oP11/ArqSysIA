<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * English language strings for local_saipa.
 *
 * @package    local_saipa
 * @copyright  2026 Schaller & Ponce <dev@schaller-ponce.com.ar>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

$string['pluginname'] = 'SAIPA - Adaptive Pedagogical Intervention System';

// Settings
$string['settings:engine_url']        = 'SAIPA Engine URL';
$string['settings:engine_url_desc']   = 'URL of the saipa-engine FastAPI service (e.g. http://host.docker.internal:8052)';
$string['settings:engine_token']      = 'API Token';
$string['settings:engine_token_desc'] = 'Bearer token for authenticating requests to saipa-engine';
$string['settings:whatsapp_provider'] = 'WhatsApp Provider';
$string['settings:whatsapp_provider_desc'] = 'Select WhatsApp Business API provider (twilio or meta)';
$string['settings:twilio_sid']        = 'Twilio Account SID';
$string['settings:twilio_token']      = 'Twilio Auth Token';
$string['settings:twilio_from']       = 'Twilio WhatsApp From Number';
$string['settings:heading_engine']    = 'SAIPA Engine Connection';
$string['settings:heading_whatsapp']  = 'WhatsApp Configuration';

// Capabilities
$string['saipa:view']    = 'View SAIPA dashboard';
$string['saipa:manage']  = 'Manage SAIPA settings';
$string['saipa:chat']    = 'Use SAIPA chat assistant';

// Privacy
$string['privacy:metadata:messages']             = 'Chat messages between the student and the SAIPA assistant';
$string['privacy:metadata:messages:userid']      = 'The ID of the user who sent the message';
$string['privacy:metadata:messages:message']     = 'The content of the message';
$string['privacy:metadata:messages:timecreated'] = 'The time the message was sent';
$string['privacy:metadata:risk']                 = 'Risk scores computed for students';
$string['privacy:metadata:risk:userid']          = 'The ID of the student';
$string['privacy:metadata:risk:score']           = 'The computed risk score (0.0–1.0)';
$string['privacy:metadata:risk:factors']         = 'JSON object listing the contributing factors';
$string['privacy:metadata:whatsapp']             = 'Data sent to external WhatsApp provider';
$string['privacy:metadata:phonenumber']          = 'The phone number used for WhatsApp communication';
$string['privacy:metadata:message']              = 'The content of the WhatsApp message';
$string['privacy:metadata:sessions']             = 'SAIPA chat session records';
$string['privacy:metadata:sessions:userid']      = 'The ID of the user';
$string['privacy:metadata:sessions:courseid']    = 'The course the session belongs to';

// Health check
$string['healthcheck:ok']      = 'SAIPA Engine is reachable';
$string['healthcheck:fail']    = 'Cannot reach SAIPA Engine at configured URL';
$string['healthcheck:heading'] = 'Engine Connection Test';

// Chat
$string['engine_error'] = 'SAIPA engine error';
