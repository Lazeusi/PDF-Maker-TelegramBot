from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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

