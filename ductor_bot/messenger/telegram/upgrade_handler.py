"""Upgrade flow: notifications, callback handling, changelog display. DISABLED."""

# DISABLED: All upgrade notification and changelog network calls have been
# commented out. on_update_available() is a no-op. handle_upgrade_callback()
# and handle_changelog_callback() return immediately without contacting GitHub.

from __future__ import annotations

import contextlib
import logging
from typing import TYPE_CHECKING

from aiogram.exceptions import TelegramBadRequest

# from ductor_bot.i18n import t
# from ductor_bot.infra.restart import EXIT_RESTART
# from ductor_bot.infra.updater import perform_upgrade_pipeline, write_upgrade_sentinel
from ductor_bot.infra.version import VersionInfo  # noqa: F401
# from ductor_bot.messenger.telegram.sender import SendRichOpts, send_rich
# from ductor_bot.text.response_format import SEP, fmt

if TYPE_CHECKING:
    from ductor_bot.messenger.telegram.app import TelegramBot

logger = logging.getLogger(__name__)


async def on_update_available(bot: TelegramBot, info: VersionInfo) -> None:  # noqa: ARG001
    """Disabled: previously notified users about a new version via Telegram."""
    # DISABLED: update notification removed.
    # from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    # keyboard = InlineKeyboardMarkup(inline_keyboard=[[
    #     InlineKeyboardButton(text=t("upgrade_handler.btn_changelog", version=info.latest),
    #                          callback_data=f"upg:cl:{info.latest}"),
    # ], [
    #     InlineKeyboardButton(text=t("upgrade_handler.btn_upgrade_now"),
    #                          callback_data=f"upg:yes:{info.latest}"),
    #     InlineKeyboardButton(text=t("upgrade_handler.btn_later"), callback_data="upg:no"),
    # ]])
    # text = fmt(t("upgrade.available_header"), SEP,
    #            f"Installed: `{info.current}`\nNew:       `{info.latest}`")
    # await bot.notify_upgrade(text, SendRichOpts(reply_markup=keyboard))


async def handle_upgrade_callback(
    bot: TelegramBot,
    chat_id: int,
    message_id: int,
    data: str,
    *,
    thread_id: int | None = None,
) -> None:
    """Disabled: previously handled upg:yes/no/cl callbacks."""
    # DISABLED: upgrade execution and changelog fetch removed.
    # if data.startswith("upg:cl:"):
    #     await handle_changelog_callback(bot, chat_id, message_id, data, thread_id=thread_id)
    #     return
    with contextlib.suppress(TelegramBadRequest):
        await bot.bot_instance.edit_message_reply_markup(
            chat_id=chat_id, message_id=message_id, reply_markup=None
        )
    if data == "upg:no":
        with contextlib.suppress(TelegramBadRequest):
            await bot.bot_instance.edit_message_text(
                text="Self-update is disabled in this build.",
                chat_id=chat_id,
                message_id=message_id,
            )
        return
    # upg:yes or upg:cl — both disabled
    # DISABLED:
    # target_version = data.split(":", 2)[2] if data.count(":") >= 2 else "latest"
    # current_version = get_current_version()
    # ... perform_upgrade_pipeline / fetch_changelog ...
    await bot.bot_instance.send_message(
        chat_id,
        "Self-update is disabled in this build.",
        parse_mode=None,
        message_thread_id=thread_id,
    )


async def handle_changelog_callback(
    bot: TelegramBot,
    chat_id: int,
    message_id: int,
    data: str,  # noqa: ARG001
    *,
    thread_id: int | None = None,
) -> None:
    """Disabled: previously fetched changelog from GitHub Releases."""
    # DISABLED: GitHub Releases contact removed.
    # from ductor_bot.infra.version import _parse_version, fetch_changelog
    # version = data.split(":", 2)[2] if data.count(":") >= 2 else ""
    # body = await fetch_changelog(version)
    # ...
    with contextlib.suppress(TelegramBadRequest):
        await bot.bot_instance.edit_message_reply_markup(
            chat_id=chat_id, message_id=message_id, reply_markup=None
        )
    await bot.bot_instance.send_message(
        chat_id,
        "Changelog fetch is disabled in this build.",
        parse_mode=None,
        message_thread_id=thread_id,
    )
