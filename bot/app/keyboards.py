from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

import app.database.requests as rq

main = InlineKeyboardMarkup(inline_keyboard =[
    [InlineKeyboardButton(text = 'Мой профиль', callback_data= 'my_profile'), InlineKeyboardButton(text = 'О нас', callback_data= 'get_information')],
    [InlineKeyboardButton(text = 'Новый пост', callback_data= 'new_post')]
])

profile = InlineKeyboardMarkup(inline_keyboard= [
    [InlineKeyboardButton(text = 'Пополнить баланс', callback_data= 'top_up_balance'), InlineKeyboardButton(text = 'Назад', callback_data= 'start' )],
    [InlineKeyboardButton(text = 'Приобрести привилегию', callback_data= 'acquire_a_privilege')]
    ])

confirm_user = InlineKeyboardMarkup(inline_keyboard= [
    [InlineKeyboardButton(text = 'Подтвердить', callback_data= 'confirm_post_user' ), InlineKeyboardButton(text = 'Заполнить заново', callback_data= 'refill_post' )]
    ])

enter_photo_confirm = InlineKeyboardMarkup(inline_keyboard= [
    [InlineKeyboardButton(text = 'Завершить', callback_data= 'enter_photo_confirm' )]
    ])

main_admin = InlineKeyboardMarkup(inline_keyboard =[
    [InlineKeyboardButton(text = 'Посмотреть неподтвержденные посты', callback_data= 'next_post')],
    [InlineKeyboardButton(text = 'Перейти в главное меню пользователя', callback_data= 'start')]
])

prev_confirm = InlineKeyboardMarkup(inline_keyboard= [
    [InlineKeyboardButton(text = 'Подтвердить', callback_data= 'prev_confirm_post' ), InlineKeyboardButton(text = 'Отказать', callback_data= 'prev_remove_post')]
    ])

confirm = InlineKeyboardMarkup(inline_keyboard= [
    [InlineKeyboardButton(text = 'Подтвердить', callback_data= 'confirm_post'), InlineKeyboardButton(text = 'Назад', callback_data= 'next_post')]
])

remove_post = InlineKeyboardMarkup(inline_keyboard= [
    [InlineKeyboardButton(text = 'Удалить с комментарием', callback_data= 'remove_post'), InlineKeyboardButton(text = 'Назад', callback_data= 'next_post')]
])

async def inline_privileges():
    keyboard = InlineKeyboardBuilder()
    privileges = await rq.get_all_privileges()
    for privilege in privileges:
        keyboard.add(InlineKeyboardButton(text = f"{privilege.name_privilege}",callback_data= f'buy_privilege_{privilege.id}'))
    keyboard.add(InlineKeyboardButton(text = 'Назад', callback_data= 'my_profile'))
    return keyboard.adjust(2).as_markup()

go_to_get_privilege = InlineKeyboardMarkup(inline_keyboard= [
    [InlineKeyboardButton(text = 'Приобрести', callback_data= 'get_of_privilege'), InlineKeyboardButton(text = 'Назад', callback_data= 'acquire_a_privilege')]
])

new_post_or_main_menu = InlineKeyboardMarkup(inline_keyboard= [
    [InlineKeyboardButton(text = 'Главное меню', callback_data= 'start'), InlineKeyboardButton(text = 'Новый пост', callback_data= 'new_post')]
])