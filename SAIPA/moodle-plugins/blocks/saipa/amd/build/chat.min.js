// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// block_saipa/chat AMD module
// Fase 1: calls local_saipa_chat web service via core/ajax.

/**
 * @module    block_saipa/chat
 * @copyright 2026 Schaller & Ponce <dev@schaller-ponce.com.ar>
 * @license   http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */
define(['core/ajax', 'core/log'], function(Ajax, Log) {

    'use strict';

    function appendMessage(role, text, container) {
        var div = document.createElement('div');
        div.className = 'saipa-msg saipa-msg-' + role + ' mb-1 p-1 rounded';
        div.style.background = (role === 'user') ? '#d1ecf1' : '#fff3cd';
        div.style.maxWidth = '90%';
        div.style.marginLeft = (role === 'user') ? 'auto' : '0';
        div.textContent = text;
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
    }

    function init(courseId, wwwroot) {
        var sendBtn      = document.getElementById('saipa-send-' + courseId);
        var inputEl      = document.getElementById('saipa-input-' + courseId);
        var msgContainer = document.getElementById('saipa-messages-' + courseId);

        if (!sendBtn || !inputEl || !msgContainer) {
            Log.error('SAIPA: widget elements not found for course ' + courseId);
            return;
        }

        var hasMessages = false;
        var sessionId   = 0;

        function sendMessage() {
            var text = inputEl.value.trim();
            if (!text) {
                return;
            }
            if (!hasMessages) {
                msgContainer.innerHTML = '';
                hasMessages = true;
            }
            inputEl.value = '';
            inputEl.disabled = true;
            sendBtn.disabled = true;

            appendMessage('user', text, msgContainer);

            // Show typing indicator
            var typingDiv = document.createElement('div');
            typingDiv.id = 'saipa-typing-' + courseId;
            typingDiv.className = 'saipa-msg saipa-msg-assistant mb-1 p-1 rounded';
            typingDiv.style.background = '#fff3cd';
            typingDiv.style.maxWidth = '90%';
            typingDiv.style.fontStyle = 'italic';
            typingDiv.textContent = '...';
            msgContainer.appendChild(typingDiv);
            msgContainer.scrollTop = msgContainer.scrollHeight;

            Ajax.call([{
                methodname: 'local_saipa_chat',
                args: {
                    course_id:  courseId,
                    message:    text,
                    session_id: sessionId
                }
            }])[0].then(function(result) {
                // Remove typing indicator
                var typing = document.getElementById('saipa-typing-' + courseId);
                if (typing) {
                    typing.remove();
                }

                sessionId = result.session_id || 0;
                appendMessage('assistant', result.reply, msgContainer);

            }).fail(function(err) {
                var typing = document.getElementById('saipa-typing-' + courseId);
                if (typing) {
                    typing.remove();
                }
                Log.error('SAIPA chat error: ' + JSON.stringify(err));
                appendMessage('assistant', 'Error al conectar con SAIPA. Por favor intentá de nuevo.', msgContainer);

            }).always(function() {
                inputEl.disabled = false;
                sendBtn.disabled = false;
                inputEl.focus();
            });
        }

        sendBtn.addEventListener('click', sendMessage);
        inputEl.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !inputEl.disabled) {
                sendMessage();
            }
        });

        Log.debug('SAIPA: chat widget initialised for course ' + courseId);
    }

    return { init: init };
});
