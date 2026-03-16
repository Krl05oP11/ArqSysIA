<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * Scheduled task: nightly risk evaluation.
 * Fase 0: skeleton. Actual evaluation logic added in Fase 3.
 *
 * @package    local_saipa
 * @copyright  2026 Schaller & Ponce <dev@schaller-ponce.com.ar>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace local_saipa\task;

defined('MOODLE_INTERNAL') || die();

class risk_evaluation extends \core\task\scheduled_task {

    public function get_name(): string {
        return get_string('pluginname', 'local_saipa') . ' — Risk Evaluation';
    }

    public function execute(): void {
        global $DB;

        mtrace('SAIPA: Starting nightly risk evaluation...');

        // Fase 3: for each active course, call saipa-engine /risk/batch
        // and store results in saipa_risk_scores.

        mtrace('SAIPA: Risk evaluation complete (skeleton).');
    }
}
