<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * Upgrade steps for local_saipa.
 *
 * @package    local_saipa
 * @copyright  2026 Schaller & Ponce <dev@schaller-ponce.com.ar>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

function xmldb_local_saipa_upgrade(int $oldversion): bool {
    global $DB;
    $dbman = $DB->get_manager();

    // Add upgrade steps here when version.php version number is bumped.
    // Example:
    // if ($oldversion < 2026031601) {
    //     $table = new xmldb_table('saipa_sessions');
    //     $field = new xmldb_field('extra', XMLDB_TYPE_TEXT, null, null, null, null, null, 'timemodified');
    //     if (!$dbman->field_exists($table, $field)) {
    //         $dbman->add_field($table, $field);
    //     }
    //     upgrade_plugin_savepoint(true, 2026031601, 'local', 'saipa');
    // }

    return true;
}
