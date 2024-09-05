from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from pathlib import Path

# Получаем текущий рабочий каталог
current_directory = Path.cwd()
# Переходим к родительскому каталогу
parent_directory = current_directory.parent
# Указываем путь к базе данных в родительском каталоге
db_path = parent_directory / 'db.sqlite3'
engine = create_async_engine(url=f'sqlite+aiosqlite:///{db_path}')

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key = True)
    id_tg = mapped_column(BigInteger)
    name_user: Mapped[str] = mapped_column(String(32))
    id_privilege: Mapped[int] = mapped_column(ForeignKey('privileges.id'))
    numb_of_posts: Mapped[int] = mapped_column()
    balance: Mapped[int] = mapped_column()
    admin: Mapped[bool] = mapped_column()

class Post(Base):
    __tablename__ = 'posts'
    
    id: Mapped[int] = mapped_column(primary_key = True)
    id_user: Mapped[int] = mapped_column(ForeignKey('users.id'))
    title: Mapped[str] = mapped_column(String(64))
    compound: Mapped[str] = mapped_column(String(32))
    size: Mapped[str] = mapped_column(String(16))
    additionally: Mapped[str] = mapped_column(String(255))
    price: Mapped[int] = mapped_column()
    confirmation: Mapped[bool] = mapped_column()
    posted: Mapped[bool] = mapped_column()
    
class Photo(Base):
    __tablename__ = 'photos'
    
    id: Mapped[int] = mapped_column(primary_key = True)
    id_post: Mapped[int] = mapped_column(ForeignKey('posts.id'))
    photo_path: Mapped[str] =  mapped_column(String(128))
    
class Privilege(Base):
    __tablename__ = 'privileges'
    
    id: Mapped[int] = mapped_column(primary_key = True)
    name_privilege: Mapped[str] = mapped_column(String(16))
    price: Mapped[int] = mapped_column()
    numb_create_posts_of_month: Mapped[int] = mapped_column()
    
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)