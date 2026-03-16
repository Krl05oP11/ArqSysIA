<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * Web service function definitions for local_saipa.
 * These are the AJAX endpoints called by the block_saipa JS widget.
 *
 * @package    local_saipa
 * @copyright  2026 Schaller & Ponce <dev@schaller-ponce.com.ar>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$functions = [

    'local_saipa_health_check' => [
        'classname'     => 'local_saipa\external\health_check',
        'methodname'    => 'execute',
        'description'   => 'Checks connectivity between Moodle and saipa-engine',
        'type'          => 'read',
        'ajax'          => true,
        'capabilities'  => 'local/saipa:manage',
        'loginrequired' => true,
    ],

    'local_saipa_chat' => [
        'classname'     => 'local_saipa\external\chat',
        'methodname'    => 'execute',
        'description'   => 'Sends a student message to saipa-engine and returns the AI reply',
        'type'          => 'write',
        'ajax'          => true,
        'capabilities'  => 'local/saipa:chat',
        'loginrequired' => true,
    ],

];

$services = [
    'SAIPA External Service' => [
        'functions'       => ['local_saipa_health_check', 'local_saipa_chat'],
        'restrictedusers' => 0,
        'enabled'         => 1,
        'shortname'       => 'saipa_service',
    ],
];
