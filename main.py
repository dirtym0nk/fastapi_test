from fastapi import Body, Depends, FastAPI, HTTPException, Path, Query
from typing import Optional, List, Dict, Annotated
from fastapi.middleware.cors import CORSMiddleware  # для работы локал хоста фронта и бэка
from sqlalchemy.orm import Session
from models import Base, User, Post
from database import engine, session_local
from schemas import UserCreate, PostCreate, PostResponse, User as DbUser


app = FastAPI()

origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=DbUser)
async def create_user(user: UserCreate, db: Session = Depends(get_db)) -> DbUser:
    db_user = User(name=user.name, age=user.age)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@app.post("/posts/", response_model=PostResponse)
async def create_post(post: PostCreate, db: Session = Depends(get_db)) -> PostResponse:
    """Создавет пост. Отправляет title, body, author_id. Где author_id связывает пост с автором."""
    db_user = db.query(User).filter(User.id == post.author_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')
 
    db_post = Post(title=post.title, body=post.body, author_id=post.author_id)

    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return db_post


@app.get("/post/", response_model=List[PostResponse])
async def post(db: Session = Depends(get_db)):
    """Возвращает все существующие посты"""
    return db.query(Post).all()


@app.get("/users/{name}", response_model=DbUser)
async def post(name: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.name == name).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return db_user


# Новый метод для удаления поста
@app.delete("/posts/{post_id}")
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail='Post not found')
    db.delete(db_post)
    db.commit()
    return {"message": f"Post with id {post_id} has been deleted."}


# Новый метод для удаления пользователя
@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')

    # Проверка на наличие связанных постов
    user_posts = db.query(Post).filter(Post.author_id == user_id).all()
    if user_posts:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete user with id {user_id} because they have associated posts."
        )

    db.delete(db_user)
    db.commit()
    return {"message": f"User with id {user_id} has been deleted."}


# функции без базы данных


# @app.get("/items")
# async def items() -> List[Post]:
#     '''Возвращаем массив обьектов класса Post. Каждый элемент которого
#     должен содержать все поля, иначе будет ошибка'''
#     return [Post(**post) for post in posts]


# @app.post("/items/add")
# async def add_item(post: PostCreate) -> Post:
#     # next находит первое совпадение и принимает два параметра. Пепрвым параметром пытаемся найти автора. Вторым параметром указывается что возвращать, если ничего не найдено в нашем случае None.  
#     author = next(
#         (user for user in users if user['id'] == post.author_id),
#         None)
#     # Если автор не найден (проверяется переменная author),
#     #  вызываем исключение
#     if not author: 
#         raise HTTPException(status_code=404, detail='User not found')
#     new_post_id = len(posts) + 1

#     new_post = {
#         'id': new_post_id,
#         'title': post.title,
#         'body': post.body,
#         'author': author
#         }
#     posts.append(new_post)
#     return Post(**new_post)


# @app.post("/user/add")
# async def user_add(user: Annotated[
#     UserCreate,
#     Body(..., example={
#         "name": "UserName",
#         "age": 1
#     })
# ]) -> User:
#     new_user_id = len(users) + 1

#     new_user = {
#         'id': new_user_id,
#         'name': user.name,
#         'age': user.age
#         }
#     users.append(**new_user)
#     return User(**new_user)


# @app.get("/items/{id}")
# # параметры lt и re обозначают диапазон граничных значений которые можно передать. Где lt-максимальная граница, а ge-минимальная.
# async def items(id: Annotated[int, Path(..., title='тут указывается id поста',
#                                         ge=1, lt=100)]) -> Post:
#     '''Возвращает dict item по указанному id. Если указанного id нет,
#     возвращает ошибку''' 
#     for post in posts:
#         if post['id'] == id:
#             return Post(**post)

#     raise HTTPException(status_code=404, detail='Post not foud') 


# @app.get("/search")
# async def search(post_id: Annotated[
#     Optional[int],
#     Query(title='id of post to search', ge=1, le=100)
# ]) -> Dict[str, Optional[Post]]:
#     if post_id: 
#         for post in posts:
#             if post['id'] == post_id:
#                 return {"data": Post(**post)}
#         raise HTTPException(status_code=404, detail='Post not foud')
#     else:
#         return {"data": None}
