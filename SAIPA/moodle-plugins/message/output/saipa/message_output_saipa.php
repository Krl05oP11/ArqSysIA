<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * SAIPA WhatsApp message output plugin.
 * Integrates with Moodle's messaging system to deliver notifications via WhatsApp.
 *
 * @package    message_output_saipa
 * @copyright  2026 Schaller & Ponce <dev@schaller-ponce.com.ar>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

class message_output_saipa extends message_output {

    /**
     * Processes the message and sends it via saipa-engine -> WhatsApp.
     *
     * @param object $eventdata  Full message event data
     * @return bool              True if sent successfully
     */
    public function send_message($eventdata): bool {
        if (!function_exists('local_saipa_engine_request')) {
            debugging('message_output_saipa: local_saipa not installed', DEBUG_DEVELOPER);
            return false;
        }

        $user    = $eventdata->userto;
        $subject = $eventdata->subject ?? '';

        // Fase 0: log only. Fase 1: look up phone from saipa_phone_verify and call engine.
        debugging(
            "message_output_saipa: would send to user {$user->id}: {$subject}",
            DEBUG_DEVELOPER
        );

        return true;
    }

    public function get_message_providers(): array {
        return [];
    }

    public function is_user_configured(\stdClass $user): bool {
        // Fase 1: check saipa_phone_verify for a verified phone number.
        return false;
    }
}
