<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * Library functions for local_saipa.
 *
 * @package    local_saipa
 * @copyright  2026 Schaller & Ponce <dev@schaller-ponce.com.ar>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

/**
 * Extends the navigation bar. Used in Fase 1 to add a Teacher Dashboard link.
 *
 * @param global_navigation $navigation
 */
function local_saipa_extend_navigation(global_navigation $navigation): void {
    // Fase 1: add course-level navigation nodes for the teacher dashboard.
}

/**
 * Makes a GET/POST request to saipa-engine.
 *
 * @param  string $endpoint  Path relative to engine root, e.g. '/health'
 * @param  array  $data      POST body as associative array (null for GET)
 * @return array             Decoded JSON response or ['error' => message]
 */
function local_saipa_engine_request(string $endpoint, ?array $data = null, int $timeout = 10): array {
    $engine_url = get_config('local_saipa', 'engine_url');
    $token      = get_config('local_saipa', 'engine_token');

    if (empty($engine_url)) {
        return ['error' => 'SAIPA engine URL not configured'];
    }

    $url = rtrim($engine_url, '/') . $endpoint;

    $headers = [
        'Content-Type: application/json',
        'Accept: application/json',
        'Authorization: Bearer ' . ($token ?? ''),
    ];

    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL            => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT        => $timeout,
        CURLOPT_HTTPHEADER     => $headers,
    ]);

    if ($data !== null) {
        $body = json_encode($data);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $body);
    }

    $response_str = curl_exec($ch);
    $errno        = curl_errno($ch);
    $error        = curl_error($ch);
    curl_close($ch);

    if ($errno) {
        return ['error' => 'cURL error (' . $errno . '): ' . $error];
    }

    if ($response_str === false || $response_str === '') {
        return ['error' => 'Empty response from engine'];
    }

    $decoded = json_decode($response_str, true);
    if ($decoded === null) {
        return ['error' => 'Invalid JSON from engine: ' . substr($response_str, 0, 300)];
    }

    return $decoded;
}
