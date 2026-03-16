<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * Event observer definitions for local_saipa.
 * Fase 0: skeleton only. Observers wired in Fase 1+.
 *
 * @package    local_saipa
 * @copyright  2026 Schaller & Ponce <dev@schaller-ponce.com.ar>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$observers = [
    // Fase 1: re-index course when content is updated.
    // [
    //     'eventname'   => '\core\event\course_module_updated',
    //     'callback'    => '\local_saipa\event\observer::course_module_updated',
    //     'includefile' => null,
    //     'internal'    => false,
    //     'priority'    => 0,
    // ],
];
