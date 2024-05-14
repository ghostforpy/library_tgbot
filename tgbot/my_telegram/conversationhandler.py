#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2022
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
# pylint: disable=R0201
"""This module contains the ConversationHandler."""

# import logging
# import warnings
# import functools
# import datetime
# from threading import Lock
from typing import TYPE_CHECKING, Dict, List, NoReturn, Optional, Union, Tuple, cast, ClassVar
import warnings

from telegram import Update
from telegram.ext import (
    # BasePersistence,
    # CallbackContext,
    # CallbackQueryHandler,
    # ChosenInlineResultHandler,
    # DispatcherHandlerStop,
    Handler,
    # InlineQueryHandler,
    ConversationHandler
)
from telegram.ext.utils.promise import Promise
# from telegram.ext.utils.types import ConversationDict
# from telegram.ext.utils.types import CCT

from django.core.cache import caches

conv_cache = caches['conversations']
# if TYPE_CHECKING:
#     from telegram.ext import Dispatcher, Job
CheckUpdateType = Optional[Tuple[Tuple[int, ...], Handler, object]]


class MyConversationHandler(ConversationHandler):
    __slots__ = set()

######3
    def _get_key(self, update: Update) -> Tuple[int, ...]:
        chat = update.effective_chat
        user = update.effective_user

        key = []

        if self.per_chat:
            #key.append(chat.id)  # type: ignore[union-attr]
            key.append(user.id)

        if self.per_user and user is not None:
            key.append(user.id)

        if self.per_message:
            key.append(
                update.callback_query.inline_message_id  # type: ignore[union-attr]
                or update.callback_query.message.message_id  # type: ignore[union-attr]
            )

        return tuple(key)

##########
    def check_update(self, update: object) -> CheckUpdateType:  # pylint: disable=R0911
        """
        Determines whether an update should be handled by this conversationhandler, and if so in
        which state the conversation currently is.

        Args:
            update (:class:`telegram.Update` | :obj:`object`): Incoming update.

        Returns:
            :obj:`bool`

        """
        if not isinstance(update, Update):
            return None
        # Ignore messages in channels
        if update.channel_post or update.edited_channel_post:
            return None
        if self.per_chat and not update.effective_user:
            return None
        if self.per_message and not update.callback_query:
            return None
        if update.callback_query and self.per_chat and (not update.callback_query.message and not update.callback_query.data):
            return None

        key = self._get_key(update)
        with self._conversations_lock:
            # state = self.conversations.get(key)
            state = conv_cache.get(key)

        # Resolve promises
        if isinstance(state, tuple) and len(state) == 2 and isinstance(state[1], Promise):
            self.logger.debug('waiting for promise...')

            # check if promise is finished or not
            if state[1].done.wait(0):
                res = self._resolve_promise(state)
                self._update_state(res, key)
                with self._conversations_lock:
                    # state = self.conversations.get(key)
                    state = conv_cache.get(key)

            # if not then handle WAITING state instead
            else:
                hdlrs = self.states.get(self.WAITING, [])
                for hdlr in hdlrs:
                    check = hdlr.check_update(update)
                    if check is not None and check is not False:
                        return key, hdlr, check
                return None

        self.logger.debug('selecting conversation %s with state %s', str(key), str(state))

        handler = None

        # Search entry points for a match
        if state is None or self.allow_reentry:
            for entry_point in self.entry_points:
                check = entry_point.check_update(update)
                if check is not None and check is not False:
                    handler = entry_point
                    break

            else:
                if state is None:
                    return None

        # Get the handler list for current state, if we didn't find one yet and we're still here
        if state is not None and not handler:
            handlers = self.states.get(state)

            for candidate in handlers or []:
                check = candidate.check_update(update)
                if check is not None and check is not False:
                    handler = candidate
                    break

            # Find a fallback handler if all other handlers fail
            else:
                for fallback in self.fallbacks:
                    check = fallback.check_update(update)
                    if check is not None and check is not False:
                        handler = fallback
                        break

                else:
                    return None

        return key, handler, check  # type: ignore[return-value]

    def _update_state(self, new_state: object, key: Tuple[int, ...]) -> None:
        if new_state == self.END:
            with self._conversations_lock:
                if conv_cache.get(key):
                    conv_cache.delete(key)
                    if self.persistent and self.persistence and self.name:
                        self.persistence.update_conversation(self.name, key, None)


                # if key in self.conversations:
                #     # If there is no key in conversations, nothing is done.
                #     del self.conversations[key]
                #     if self.persistent and self.persistence and self.name:
                #         self.persistence.update_conversation(self.name, key, None)

        elif isinstance(new_state, Promise):
            with self._conversations_lock:
                # self.conversations[key] = (self.conversations.get(key), new_state)
                conv_cache.set(key, (conv_cache.get(key), new_state))
                if self.persistent and self.persistence and self.name:
                    self.persistence.update_conversation(
                        self.name, key, (self.conversations.get(key), new_state)
                    )

        elif new_state is not None:
            if new_state not in self.states:
                warnings.warn(
                    f"Handler returned state {new_state} which is unknown to the "
                    f"ConversationHandler{' ' + self.name if self.name is not None else ''}."
                )
            with self._conversations_lock:
                # self.conversations[key] = new_state
                conv_cache.set(key, new_state)

                if self.persistent and self.persistence and self.name:
                    self.persistence.update_conversation(self.name, key, new_state)