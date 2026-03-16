<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * Privacy API provider for local_saipa.
 * Required for any plugin that stores personal data (GDPR compliance).
 *
 * @package    local_saipa
 * @copyright  2026 Schaller & Ponce <dev@schaller-ponce.com.ar>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace local_saipa\privacy;

use core_privacy\local\metadata\collection;
use core_privacy\local\request\approved_contextlist;
use core_privacy\local\request\approved_userlist;
use core_privacy\local\request\contextlist;
use core_privacy\local\request\userlist;
use core_privacy\local\request\writer;

defined('MOODLE_INTERNAL') || die();

class provider implements
    \core_privacy\local\metadata\provider,
    \core_privacy\local\request\core_userlist_provider,
    \core_privacy\local\request\plugin\provider {

    public static function get_metadata(collection $collection): collection {

        $collection->add_database_table('saipa_sessions', [
            'userid'   => 'privacy:metadata:sessions:userid',
            'courseid' => 'privacy:metadata:sessions:courseid',
        ], 'privacy:metadata:sessions');

        $collection->add_database_table('saipa_messages', [
            'userid'      => 'privacy:metadata:messages:userid',
            'message'     => 'privacy:metadata:messages:message',
            'timecreated' => 'privacy:metadata:messages:timecreated',
        ], 'privacy:metadata:messages');

        $collection->add_database_table('saipa_risk_scores', [
            'userid'  => 'privacy:metadata:risk:userid',
            'score'   => 'privacy:metadata:risk:score',
            'factors' => 'privacy:metadata:risk:factors',
        ], 'privacy:metadata:risk');

        $collection->add_external_location_link('whatsapp', [
            'phonenumber' => 'privacy:metadata:phonenumber',
            'message'     => 'privacy:metadata:message',
        ], 'privacy:metadata:whatsapp');

        return $collection;
    }

    public static function get_contexts_for_userid(int $userid): contextlist {
        $contextlist = new contextlist();
        $sql = "SELECT ctx.id
                  FROM {context} ctx
                  JOIN {saipa_sessions} s ON s.courseid = ctx.instanceid
                 WHERE ctx.contextlevel = :contextlevel
                   AND s.userid = :userid";
        $contextlist->add_from_sql($sql, [
            'contextlevel' => CONTEXT_COURSE,
            'userid'       => $userid,
        ]);
        return $contextlist;
    }

    public static function get_users_in_context(userlist $userlist): void {
        $context = $userlist->get_context();
        if ($context->contextlevel !== CONTEXT_COURSE) {
            return;
        }
        $sql = "SELECT s.userid
                  FROM {saipa_sessions} s
                 WHERE s.courseid = :courseid";
        $userlist->add_from_sql('userid', $sql, ['courseid' => $context->instanceid]);
    }

    public static function export_user_data(approved_contextlist $contextlist): void {
        global $DB;
        $userid = $contextlist->get_user()->id;

        foreach ($contextlist->get_contexts() as $context) {
            if ($context->contextlevel !== CONTEXT_COURSE) {
                continue;
            }
            $sessions = $DB->get_records('saipa_sessions', [
                'userid'   => $userid,
                'courseid' => $context->instanceid,
            ]);
            foreach ($sessions as $session) {
                $messages = $DB->get_records('saipa_messages', ['sessionid' => $session->id]);
                writer::with_context($context)->export_data(
                    ['SAIPA', 'Session ' . $session->id],
                    (object)['session' => $session, 'messages' => array_values($messages)]
                );
            }
        }
    }

    public static function delete_data_for_all_users_in_context(\context $context): void {
        global $DB;
        if ($context->contextlevel !== CONTEXT_COURSE) {
            return;
        }
        $sessions = $DB->get_records('saipa_sessions', ['courseid' => $context->instanceid]);
        foreach ($sessions as $session) {
            $DB->delete_records('saipa_messages', ['sessionid' => $session->id]);
        }
        $DB->delete_records('saipa_sessions', ['courseid' => $context->instanceid]);
        $DB->delete_records('saipa_risk_scores', ['courseid' => $context->instanceid]);
    }

    public static function delete_data_for_user(approved_contextlist $contextlist): void {
        global $DB;
        $userid = $contextlist->get_user()->id;
        foreach ($contextlist->get_contexts() as $context) {
            if ($context->contextlevel !== CONTEXT_COURSE) {
                continue;
            }
            $sessions = $DB->get_records('saipa_sessions', [
                'userid'   => $userid,
                'courseid' => $context->instanceid,
            ]);
            foreach ($sessions as $session) {
                $DB->delete_records('saipa_messages', ['sessionid' => $session->id]);
            }
            $DB->delete_records('saipa_sessions', [
                'userid'   => $userid,
                'courseid' => $context->instanceid,
            ]);
            $DB->delete_records('saipa_risk_scores', [
                'userid'   => $userid,
                'courseid' => $context->instanceid,
            ]);
        }
    }

    public static function delete_data_for_users(approved_userlist $userlist): void {
        global $DB;
        $context = $userlist->get_context();
        if ($context->contextlevel !== CONTEXT_COURSE) {
            return;
        }
        foreach ($userlist->get_userids() as $userid) {
            $sessions = $DB->get_records('saipa_sessions', [
                'userid'   => $userid,
                'courseid' => $context->instanceid,
            ]);
            foreach ($sessions as $session) {
                $DB->delete_records('saipa_messages', ['sessionid' => $session->id]);
            }
            $DB->delete_records('saipa_sessions', [
                'userid'   => $userid,
                'courseid' => $context->instanceid,
            ]);
            $DB->delete_records('saipa_risk_scores', [
                'userid'   => $userid,
                'courseid' => $context->instanceid,
            ]);
        }
    }
}
