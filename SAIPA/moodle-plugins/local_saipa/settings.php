<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * Admin settings page for local_saipa.
 *
 * @package    local_saipa
 * @copyright  2026 Schaller & Ponce <dev@schaller-ponce.com.ar>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

if ($hassiteconfig) {
    $settings = new admin_settingpage(
        'local_saipa',
        get_string('pluginname', 'local_saipa')
    );

    $ADMIN->add('localplugins', $settings);

    // === Section: Engine Connection ===
    $settings->add(new admin_setting_heading(
        'local_saipa/heading_engine',
        get_string('settings:heading_engine', 'local_saipa'),
        ''
    ));

    $settings->add(new admin_setting_configtext(
        'local_saipa/engine_url',
        get_string('settings:engine_url', 'local_saipa'),
        get_string('settings:engine_url_desc', 'local_saipa'),
        'http://host.docker.internal:8052',
        PARAM_URL
    ));

    $settings->add(new admin_setting_configpasswordunmask(
        'local_saipa/engine_token',
        get_string('settings:engine_token', 'local_saipa'),
        get_string('settings:engine_token_desc', 'local_saipa'),
        ''
    ));

    // === Section: WhatsApp ===
    $settings->add(new admin_setting_heading(
        'local_saipa/heading_whatsapp',
        get_string('settings:heading_whatsapp', 'local_saipa'),
        ''
    ));

    $settings->add(new admin_setting_configselect(
        'local_saipa/whatsapp_provider',
        get_string('settings:whatsapp_provider', 'local_saipa'),
        get_string('settings:whatsapp_provider_desc', 'local_saipa'),
        'twilio',
        ['twilio' => 'Twilio', 'meta' => 'Meta Cloud API']
    ));

    $settings->add(new admin_setting_configtext(
        'local_saipa/twilio_sid',
        get_string('settings:twilio_sid', 'local_saipa'),
        '',
        '',
        PARAM_TEXT
    ));

    $settings->add(new admin_setting_configpasswordunmask(
        'local_saipa/twilio_token',
        get_string('settings:twilio_token', 'local_saipa'),
        '',
        ''
    ));

    $settings->add(new admin_setting_configtext(
        'local_saipa/twilio_from',
        get_string('settings:twilio_from', 'local_saipa'),
        '',
        'whatsapp:+14155238886',
        PARAM_TEXT
    ));
}
