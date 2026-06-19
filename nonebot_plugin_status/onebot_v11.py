"""
@Author         : yanyongyu
@Date           : 2022-09-02 11:35:48
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-30 18:25:12
@Description    : OneBot v11 matchers for status plugin
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from nonebot.rule import to_me
from nonebot import on_type, on_message
from nonebot.adapters.onebot.v11 import PokeNotifyEvent, PrivateMessageEvent

from . import server_status, status_config, status_permission
from . import render_template


async def _group_poke(event: PokeNotifyEvent) -> bool:
    """Only match pokes in group chats (not private pokes)."""
    return event.group_id is not None


if status_config.server_status_enabled:
    group_poke = on_type(
        (PokeNotifyEvent,),
        rule=to_me() & _group_poke,
        permission=status_permission,
        priority=10,
        block=True,
        handlers=[server_status],
    )
    """Poke notify matcher for group chats.

    双击头像拍一拍
    """


async def _private_poke(event: PokeNotifyEvent) -> bool:
    """Match pokes in private chats directed at the bot."""
    return event.group_id is None and event.target_id == event.self_id


async def private_server_status(bot, event: PokeNotifyEvent):
    """Server status handler for private poke events.

    PokeNotifyEvent lacks message context, so matcher.send() fails.
    We call send_msg explicitly with message_type=private.
    """
    from nonebot.adapters.onebot.v11 import Message

    message = Message(await render_template())
    await bot.send_msg(message_type="private", user_id=event.user_id, message=message)


if status_config.server_status_enabled:
    private_poke = on_type(
        (PokeNotifyEvent,),
        rule=_private_poke,
        permission=status_permission,
        priority=10,
        block=True,
        handlers=[private_server_status],
    )
    """Poke notify matcher for private chats.

    私聊戳一戳
    """


async def _poke(event: PrivateMessageEvent) -> bool:
    return event.sub_type == "friend" and event.message[0].type == "poke"


if status_config.server_status_enabled:
    poke = on_message(
        _poke,
        permission=status_permission,
        priority=10,
        block=True,
        handlers=[server_status],
    )
    """Poke message matcher.

    私聊发送戳一戳
    """
