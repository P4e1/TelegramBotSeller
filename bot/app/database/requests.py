from app.database.models import async_session
from app.database.models import User, Post, Photo, Privilege
from sqlalchemy import select, func, update, delete


async def set_user(tg_id, nameUser):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.id_tg == tg_id))
        
        if not user:
            session.add(User(id_tg = tg_id, name_user = nameUser, id_privilege = 1, numb_of_posts = 0, balance = 0, admin = False))
            await session.commit()

async def get_user_profile(tg_id):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.id_tg == tg_id))
    
async def get_all_privileges():
    async with async_session() as session:
        return await session.scalars(select(Privilege))
    
async def get_privilege_by_id(privilege_id):
    async with async_session() as session:
        return await session.scalar(select(Privilege).where(Privilege.id == privilege_id))
    
async def get_user_for_current_post(id):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.id == id))
    
async def get_users_admin():
    async with async_session() as session:
        return await session.scalars(select(User).where(User.admin == True))

async def get_privilege_for_this_user(id_privilege):
    async with async_session() as session:
        return await session.scalar(select(Privilege).where(Privilege.id == id_privilege))
    
async def push_new_post_in_basedata(id_user, title, compound, size, additionally, price, photos_path):
    async with async_session() as session:
         # Добавление нового поста
        new_post = Post(
            id_user=id_user,
            title=title,
            compound=compound,
            size=size,
            additionally=additionally,
            price=price,
            confirmation=False,
            posted=False
        )
        session.add(new_post)
        await session.commit()  # Коммит для получения нового id

        # Получение максимального id поста
        max_id_subquery = select(func.max(Post.id)).scalar_subquery()
        id_post = await session.scalar(select(Post.id).where(Post.id == max_id_subquery))

        # Добавление фотографий
        photos_path_to_add = [Photo(id_post=id_post, photo_path = path) for path in photos_path]
        session.add_all(photos_path_to_add)
        await session.commit()
        
async def get_posts_for_user(id_user):
    async with async_session() as session:
        return await session.scalars(select(Post).where(Post.id_user == id_user))

async def get_photos_path_for_post(id_post):
    async with async_session() as session:
        return await session.scalars(select(Photo.photo_path).where(Photo.id_post == id_post))
    
async def get_all_posts_which_not_confirm():
    async with async_session() as session:
        result = await session.scalars(select(Post).where(Post.confirmation == False))
        return result.all()
    
async def confirm_this_post(id_post):
    async with async_session() as session:
        await session.execute(update(Post).where(Post.id == id_post).values(confirmation=True))
        await session.commit()

async def posted_this_post(id_post):
    async with async_session() as session:
        await session.execute(update(Post).where(Post.id == id_post).values(posted=True))
        await session.commit()

async def remove_path_photos_for_current_post(id_post):
    async with async_session() as session:
        await session.execute(delete(Photo).where(Photo.id_post == id_post))
        await session.commit()
async def remove_post(id_post):
    async with async_session() as session:
        await session.execute(delete(Post).where(Post.id == id_post))
        await session.commit()

async def get_number_of_unconfirmed():
    async with async_session() as session:
        return await session.scalar(select(func.count()).select_from(Post).where(Post.confirmation == False))
    
async def update_number_posts_for_user(post_id):
    async with async_session() as session:
        # Получаем пользователя, который создал пост с указанным post_id
        stmt = select(User).where(User.id == select(Post.id_user).where(Post.id == post_id).scalar_subquery())
        user = await session.scalar(stmt)
        
        # Убеждаемся, что пользователь найден
        if user:
            # Обновляем количество постов у пользователя
            await session.execute(
                update(User)
                .where(User.id == user.id)
                .values(numb_of_posts=user.numb_of_posts + 1)
            )
            await session.commit()