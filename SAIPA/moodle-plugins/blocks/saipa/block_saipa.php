<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * Main class for block_saipa.
 *
 * @package    block_saipa
 * @copyright  2026 Schaller & Ponce <dev@schaller-ponce.com.ar>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

class block_saipa extends block_base {

    public function init(): void {
        $this->title = get_string('pluginname', 'block_saipa');
    }

    public function instance_allow_multiple(): bool {
        return false;
    }

    public function applicable_formats(): array {
        return [
            'course-view' => true,
            'site'        => false,
            'my'          => false,
        ];
    }

    public function get_content(): ?\stdClass {
        global $USER, $COURSE, $OUTPUT;

        if ($this->content !== null) {
            return $this->content;
        }

        $this->content = new \stdClass();
        $this->content->footer = '';

        $locallib = \core_component::get_component_directory('local_saipa') . '/lib.php';
        if (!$locallib || !file_exists($locallib)) {
            $this->content->text = get_string('requires_local', 'block_saipa');
            return $this->content;
        }
        require_once($locallib);

        $context = \context_course::instance($COURSE->id);
        if (!has_capability('local/saipa:chat', $context)) {
            return $this->content;
        }

        $template_data = [
            'courseid' => $COURSE->id,
            'userid'   => $USER->id,
            'username' => fullname($USER),
            'wwwroot'  => (new \moodle_url('/'))->out(false),
        ];

        $this->content->text = $OUTPUT->render_from_template(
            'block_saipa/chat_widget',
            $template_data
        );

        return $this->content;
    }
}
