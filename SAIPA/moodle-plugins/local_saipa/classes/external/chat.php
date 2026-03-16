<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * External web service: chat
 * Sends a student message to saipa-engine and returns the AI reply.
 *
 * @package    local_saipa
 * @copyright  2026 Schaller & Ponce <dev@schaller-ponce.com.ar>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace local_saipa\external;

use core_external\external_api;
use core_external\external_function_parameters;
use core_external\external_multiple_structure;
use core_external\external_single_structure;
use core_external\external_value;

defined('MOODLE_INTERNAL') || die();

require_once($CFG->dirroot . '/local/saipa/lib.php');

class chat extends external_api {

    public static function execute_parameters(): external_function_parameters {
        return new external_function_parameters([
            'course_id'  => new external_value(PARAM_INT,  'Course ID'),
            'message'    => new external_value(PARAM_TEXT, 'Student message'),
            'session_id' => new external_value(PARAM_INT,  'Session ID (0 = new session)', VALUE_DEFAULT, 0),
        ]);
    }

    public static function execute(int $course_id, string $message, int $session_id = 0): array {
        global $USER;

        // Validate and normalise parameters.
        $params = self::validate_parameters(self::execute_parameters(), [
            'course_id'  => $course_id,
            'message'    => $message,
            'session_id' => $session_id,
        ]);

        // Require course context and chat capability.
        $context = \context_course::instance($params['course_id']);
        self::validate_context($context);
        require_capability('local/saipa:chat', $context);

        $payload = [
            'course_id'  => $params['course_id'],
            'user_id'    => (int) $USER->id,
            'message'    => $params['message'],
            'session_id' => $params['session_id'] > 0 ? $params['session_id'] : null,
        ];

        $response = local_saipa_engine_request('/chat', $payload, 60);

        if (isset($response['error'])) {
            return [
                'reply'      => get_string('engine_error', 'local_saipa') . ': ' . $response['error'],
                'session_id' => 0,
                'sources'    => [],
            ];
        }

        return [
            'reply'      => $response['reply']      ?? '',
            'session_id' => (int) ($response['session_id'] ?? 0),
            'sources'    => $response['sources']    ?? [],
        ];
    }

    public static function execute_returns(): external_single_structure {
        return new external_single_structure([
            'reply'      => new external_value(PARAM_RAW,  'Assistant reply'),
            'session_id' => new external_value(PARAM_INT,  'Conversation session ID'),
            'sources'    => new external_multiple_structure(
                new external_value(PARAM_TEXT, 'Source document identifier'),
                'Source documents used to generate the reply',
                VALUE_OPTIONAL
            ),
        ]);
    }
}
