from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.database.models.channel import Channel

admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Force Join", callback_data="force_join")],
    [InlineKeyboardButton(text="Admin Panel", callback_data="admin_panel")]                                     
])   

force_join_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Add channel", callback_data="add_channel") , InlineKeyboardButton(text="Remove channel", callback_data="remove_channel")],
    [InlineKeyboardButton(text="List channels", callback_data="list_channels")],
    [InlineKeyboardButton(text="Back🔙", callback_data="back_to_admin_panel")]

])

check_channel_type_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Public", callback_data="channel_type_public") , InlineKeyboardButton(text="Private", callback_data="channel_type_private")],
    [InlineKeyboardButton(text="Back🔙", callback_data="back_to_admin_panel")]
])

async def channel_list():
    channels = await Channel.get_all_channels()
    if not channels:
        builder = InlineKeyboardBuilder()
        builder.button(text="No channels available.", callback_data="no_channels")
        builder.button(text="Back🔙", callback_data="back_to_channel_menu")
        builder.adjust(1)
        return builder.as_markup()
    builder = InlineKeyboardBuilder()
    for ch in channels:
        builder.button(text=ch["title"], callback_data=f"channel_{ch['chat_id']}")

    builder.button(text="Back🔙", callback_data="back_to_channel_menu")
    builder.adjust(1)
    return builder.as_markup()

async def channel_list_show():
    channels = await Channel.get_all_channels()
    builder = InlineKeyboardBuilder()
    if not channels:
        builder.button(text="No channels available.", callback_data="no_channels")
        builder.button(text="Back🔙", callback_data="back_to_channel_menu")
        builder.adjust(1)
        return builder.as_markup()
    for ch in channels:
        builder.button(text=ch["title"], callback_data=f"show_channel_{ch['chat_id']}")
    builder.button(text="Back🔙", callback_data="back_to_channel_menu")
    builder.adjust(1)
    return builder.as_markup()

back_to_channel_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Back🔙", callback_data="back_to_channel_menu")]
])
