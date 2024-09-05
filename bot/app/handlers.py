from aiogram import F, Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from pathlib import Path
from dotenv import load_dotenv
import os
from app.payment import create
import app.keyboards as kb
import app.database.requests as rq
from rich.text import Text

load_dotenv()
router = Router()
bot = Bot(token=os.getenv('TOKEN'))
parent_directory = Path.cwd().parent
photos_directory = f'{parent_directory}/photos'
CHANNEL_ID = '@sale_channel_71'

class CreatePost(StatesGroup):
    title = State()
    compound = State()
    size = State()
    additionally = State()
    price = State()
    photos = State(list)
    
class Privilege(StatesGroup):
    id_privilege = State()

@router.message(CommandStart())
async def cmd_start(message: Message, flag: bool = False, first_name: str = None):
    await rq.set_user(message.from_user.id, message.from_user.username)
    if not first_name: first_name = message.from_user.first_name
    if flag:
        await message.edit_text(f"Привет, {first_name}. Выберите то, что вас интересует.",
                            reply_markup = kb.main)
    else:
        await message.answer(f"Привет, {first_name}. Выберите то, что вас интересует.",
                            reply_markup = kb.main)
    
@router.callback_query(F.data == 'start')
async def go_to_start(callback: CallbackQuery):
    await cmd_start(callback.message, True, callback.from_user.first_name)   

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    user = await rq.get_user_profile(message.from_user.id)
    if user:
        flagAdmin = user.admin
        if flagAdmin:
            await message.answer(f"Привет, {message.from_user.first_name}",
                            reply_markup = kb.main_admin)

@router.callback_query(F.data == "my_profile")
async def get_profile(callback: CallbackQuery):
    user = await rq.get_user_profile(callback.from_user.id)
    privilege = await rq.get_privilege_for_this_user(user.id_privilege)
    await callback.message.edit_text(f'      Мой профиль\nМой ID: {user.id}\nПривилегия: {privilege.name_privilege}\nОсталось запостить {privilege.numb_create_posts_of_month - user.numb_of_posts} публикаций\nБаланс: {user.balance} рублей',
                         reply_markup = kb.profile)
    
@router.callback_query(F.data == 'acquire_a_privilege')
async def acquire_a_privilege(callback: CallbackQuery):
    privileges = await rq.get_all_privileges()
    answer = 'Привилегия предоставляет Вам возможность подачи определенного количества объявлений за месяц.\nСписок привилегий представлен ниже:👇\n'
    for privilege in privileges:
        answer += f'{privilege.name_privilege} - {privilege.numb_create_posts_of_month} объявлений/месяц - {privilege.price} рублей\n'
    await callback.message.edit_text(answer,
                                  reply_markup= await kb.inline_privileges())
    
@router.callback_query(F.data and F.data.startswith('buy_privilege_'))
async def process_callback_buy_privilege(callback: CallbackQuery, state: FSMContext):
    privilege_id = int(callback.data.split('_')[-1])
    privilege = await rq.get_privilege_by_id(privilege_id)
    await state.clear()
    await state.set_state(Privilege.id_privilege)
    await state.update_data(id_privilege = privilege_id)
    await callback.message.edit_text(f'Вы выбрали привилегию {privilege.name_privilege}. Хотите приобрести её?',
                                     reply_markup= kb.go_to_get_privilege)

@router.callback_query(F.data == 'get_of_privilege')
async def get_of_privilege(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    privilege_id = data["id_privilege"]
    privilege = await rq.get_privilege_by_id(privilege_id)
    user = await rq.get_user_profile(callback.from_user.id)
    if user.balance >= privilege.price:
        pass
    else:
        await callback.message.answer("На вашем счете недостаточно средств. Пополните баланс и выберите привилегию снова.")
        await state.clear()
        #await go_to_start(callback)
@router.callback_query(F.data == 'buy')
async def buy_privilege(callback: CallbackQuery):
    price = 1.00
    payment_url, payment_id = create(price, callback.message.chat.id)
    await callback.message.answer(f"{payment_url} {payment_id}")
@router.callback_query(F.data == "new_post")
async def create_new_post(callback: CallbackQuery, state: FSMContext):
    await callback.answer("")
    user = await rq.get_user_profile(callback.from_user.id)
    privilege = await rq.get_privilege_for_this_user(user.id_privilege)
    if user.numb_of_posts < privilege.numb_create_posts_of_month:
        await state.set_state(CreatePost.title)
        await callback.message.answer('Введите заголовок Вашего объявления.')
    else:
        await callback.message.answer('У Вас не приобретена привилегия либо Вы выложили достаточное количество объявлений.')

@router.message(CreatePost.title)
async def enter_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(CreatePost.compound)
    await message.answer('Введите состав Вашей вещи.')

@router.message(CreatePost.compound)
async def enter_compound(message: Message, state: FSMContext):
    await state.update_data(compound=message.text)
    await state.set_state(CreatePost.size)
    await message.answer('Введите размер Вашей вещи.')
    
@router.message(CreatePost.size)
async def enter_size(message: Message, state: FSMContext):
    await state.update_data(size=message.text)
    await state.set_state(CreatePost.additionally)
    await message.answer('Введите описание Вашей вещи.')

@router.message(CreatePost.additionally)
async def enter_additionally(message: Message, state: FSMContext):
    await state.update_data(additionally=message.text)
    await state.set_state(CreatePost.price)
    await message.answer('Введите цену Вашей вещи.')
    
@router.message(CreatePost.price)
async def enter_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(CreatePost.photos)
    await message.answer('Пришлите фотографии Вашей вещи, не присылая в одном сообщении.')
    
@router.message(CreatePost.photos, F.photo)
async def enter_photos(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    file_id = message.photo[-1].file_id
    photos.append(file_id)
    await state.update_data(photos = photos)
    await message.answer("Отправьте ещё фото или нажмите 'Завершить', когда закончите.",
                        reply_markup= kb.enter_photo_confirm)

@router.callback_query(F.data == 'enter_photo_confirm')
async def enter_photo_confirm(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await callback.message.answer('Отлично. Ваш пост будет выглядеть следующим образом:')
    data = await state.get_data()
    user = await rq.get_user_profile(callback.from_user.id)
    media = []
    flag3 = True
    caption_text = (f'{data["title"]}\n'
                                  '\n'
                                              f'состав: {data["compound"]}\n'
                                              f'размер: {data["size"]}\n'
                                              f'{data["additionally"]}\n'
                                              '\n'
                                              '\n'
                                              f'{data["price"]} ₽\n'
                                              '\n'
                                              '\n'
                                              f'✍️@{user.name_user} 🔎#{user.name_user}')
    for photo in data["photos"]:
        if flag3:
            media.append(InputMediaPhoto(media=photo, caption= caption_text))
            flag3 = False
        else:
            media.append(InputMediaPhoto(media=photo))
        
    await bot.send_media_group(chat_id= callback.message.chat.id, media= media)
    await callback.message.answer('Проверьте Ваш пост и подтвердите его публикацию, нажав на кнопку "Подтвердить".',
                         reply_markup = kb.confirm_user)
    
@router.callback_query(F.data == 'confirm_post_user')
async def confirm_post1(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await callback.message.answer('Ваш пост отправлен на проверку. Ожидайте подтверждения Вашего поста.',
                                  reply_markup= kb.new_post_or_main_menu)
    data = await state.get_data()
    user = await rq.get_user_profile(callback.from_user.id)
    photos = data.get("photos", [])
    photos_path = []
    for photo in photos:
        file = await bot.get_file(photo)
        file_path = file.file_path
        new_file_path = f'{photos_directory}/{photo}.jpg'
        await bot.download_file(file_path, new_file_path)
        photos_path.append(new_file_path)
    await rq.push_new_post_in_basedata(user.id, data["title"], data["compound"], data["size"], data["additionally"], data["price"], photos_path)
    users_admin = await rq.get_users_admin()
    for user_admin in users_admin:
        await bot.send_message(chat_id= user_admin.id_tg, text="Вам пришел новый пост на проверку!")
        numb = await rq.get_number_of_unconfirmed()
        await bot.send_message(chat_id= user_admin.id_tg, text= f"Непроверенных постов {numb}")
    await state.clear()

@router.callback_query(F.data == 'refill_post')
async def confirm_post(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.clear()
    await state.set_state(CreatePost.title)
    await callback.message.answer('Введите заголовок Вашего объявления.')
#----------------------------------------------------------------HandlersForAdmin-----------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------
class RemovePost(StatesGroup):
    comment = State()

@router.callback_query(F.data == "next_post")
async def get_post(callback: CallbackQuery):
    await callback.answer('')
    current_user = await rq.get_user_profile(callback.from_user.id)
    if current_user.admin:
        posts = await rq.get_all_posts_which_not_confirm()
        if not posts:
            await callback.message.answer("Неподтвержденных постов нет.",
                                        reply_markup= kb.main_admin)
        else:
            photos = []
            post = posts[0]
            photos_path = await rq.get_photos_path_for_post(post.id)
            for photo_path in photos_path:
                photo_bytes = FSInputFile(photo_path)
                photos.append(photo_bytes)
            media = []
            flag3 = True
            user = await rq.get_user_for_current_post(post.id_user)
            caption_text = (f'{post.title}\n'
                                    '\n'
                                        f'состав: {post.compound}\n'
                                        f'размер: {post.size}\n'
                                        f'{post.additionally}\n'
                                        '\n'
                                        '\n'
                                        f'{post.price} ₽\n'
                                        '\n'
                                        '\n'
                                        f'✍️@{user.name_user} 🔎#{user.name_user}')
            for photo in photos:
                if flag3:
                    media.append(InputMediaPhoto(media=photo, caption= caption_text))
                    flag3 = False
                else:
                    media.append(InputMediaPhoto(media=photo))
            await bot.send_media_group(chat_id= callback.message.chat.id, media= media)
            await callback.message.answer('Что будем делать с постом?', reply_markup= kb.prev_confirm)
        
@router.callback_query(F.data == 'confirm_post')
async def confirm_and_posted_Post(callback: CallbackQuery):
    current_user = await rq.get_user_profile(callback.from_user.id)
    if current_user.admin:
        await callback.answer('Пост подтвержден')
        posts = await rq.get_all_posts_which_not_confirm()
        post = posts[0]
        await rq.confirm_this_post(post.id)
        photos = []
        photos_path = await rq.get_photos_path_for_post(post.id)
        for photo_path in photos_path:
            photo_bytes = FSInputFile(photo_path)
            photos.append(photo_bytes)
        media = []
        flag3 = True
        user = await rq.get_user_for_current_post(post.id_user)
        caption_text = (f'{post.title}\n'
                        '\n'
                        f'состав: {post.compound}\n'
                        f'размер: {post.size}\n'
                        f'{post.additionally}\n'
                        '\n'
                        '\n'
                        f'{post.price} ₽\n'
                        '\n'
                        '\n'
                        f'✍️@{user.name_user} 🔎#{user.name_user}')
        for photo in photos:
            if flag3:
                media.append(InputMediaPhoto(media=photo, caption= caption_text))
                flag3 = False
            else:
                media.append(InputMediaPhoto(media=photo))
        await bot.send_media_group(chat_id=CHANNEL_ID, media = media)
        await rq.update_number_posts_for_user(post.id)
        await rq.posted_this_post(post.id)
        await get_post(callback)

@router.callback_query(F.data == 'prev_confirm_post')
async def prev_confirm_post(callback: CallbackQuery):
    await callback.answer('')
    current_user = await rq.get_user_profile(callback.from_user.id)
    if current_user.admin:
        await callback.message.edit_text('Вы точно хотите подтвердить?',
                                    reply_markup= kb.confirm)
    
@router.callback_query(F.data == 'prev_remove_post')
async def prev_remove_post(callback: CallbackQuery):
    current_user = await rq.get_user_profile(callback.from_user.id)
    if current_user.admin:
        await callback.answer('')
        await callback.message.edit_text('Вы точно хотите удалить пост?',
                                  reply_markup= kb.remove_post)
    
@router.callback_query(F.data == 'remove_post')
async def remove_post(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    current_user = await rq.get_user_profile(callback.from_user.id)
    if current_user.admin:
        await callback.message.answer('Пост будет удален. Напишите комментарий (Причина отказа).')
        await state.set_state(RemovePost.comment)
    
@router.message(RemovePost.comment)
async def get_comment(message: Message, state: FSMContext):
    current_user = await rq.get_user_profile(message.from_user.id)
    if current_user.admin:
        await state.update_data(comment= message.text)
        await message.answer('Комментарий будет отправлен владельцу поста.')
        posts = await rq.get_all_posts_which_not_confirm()
        post = posts[0]
        photos = []
        photos_path = await rq.get_photos_path_for_post(post.id)
        for photo_path in photos_path:
            photo_bytes = FSInputFile(photo_path)
            photos.append(photo_bytes)
        media = []
        flag3 = True
        user = await rq.get_user_for_current_post(post.id_user)
        caption_text = (f'{post.title}\n'
                        '\n'
                        f'состав: {post.compound}\n'
                        f'размер: {post.size}\n'
                        f'{post.additionally}\n'
                        '\n'
                        '\n'
                        f'{post.price} ₽\n'
                        '\n'
                        '\n'
                        f'✍️@{user.name_user} 🔎#{user.name_user}')
        for photo in photos:
            if flag3:
                media.append(InputMediaPhoto(media=photo, caption= caption_text))
                flag3 = False
            else:
                media.append(InputMediaPhoto(media=photo))
        await bot.send_media_group(chat_id=message.from_user.id, media = media)
        data = await state.get_data()
        await bot.send_message(chat_id = user.id_tg, text = f"Ваш пост, находящийся выше, не прошел модерацию по причине: {data['comment']}")
        await state.clear()
        photos_path = await rq.get_photos_path_for_post(post.id)
        for photo_path in photos_path:
            os.remove(photo_path)
        await rq.remove_path_photos_for_current_post(post.id)
        await rq.remove_post(post.id)

