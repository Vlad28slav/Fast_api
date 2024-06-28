from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from models import SessionLocal, engine
from utils import AuthMiddleware, exchange_code_for_token
from config import get_settings

settings = get_settings()

AUTH0_DOMAIN = settings.auth0_domain
SECRET_KEY = settings.secret_key
AUTH0_TOKEN_URL = f"https://{AUTH0_DOMAIN}/oauth/token"
AUTH0_JWKS_URL = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.add_middleware(
    AuthMiddleware,
    auth0_domain=AUTH0_DOMAIN,
    client_id=settings.auth0_client_id,
    audience=settings.auth0_api_audience,
    algorithms=settings.auth0_algorithms

)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.name = user.name
    db_user.email = user.email
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return db_user

@app.post("/posts/", response_model=schemas.Post)
def create_post(request: Request, post: schemas.PostCreate, db: Session = Depends(get_db)):
    print(request.session)
    db_post = models.Post(title=post.title, content=post.content, owners_id=request.session.get("id"))
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.get("/posts/", response_model=List[schemas.Post])
def read_posts(request: Request, skip: int = 0, limit: int=10, db: Session= Depends(get_db)):
    user_id = request.session.get("id")
    print(user_id)
    posts = db.query(models.Post).filter(models.Post.owners_id == user_id).offset(skip).limit(limit)
    return posts

@app.get("/posts/{post_id}", response_model=schemas.Post)
def read_post(request: Request, post_id: int, db : Session = Depends(get_db)):
    user_id = request.session.get("id")
    post = db.query(models.Post).filter(models.Post.id == post_id, models.Post.owners_id == user_id ).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.delete("/posts/{post_id}")
def delete_post(request: Request, post_id: int, db : Session = Depends(get_db)):
    user_id = request.session.get("id")
    db_post= db.query(models.Post).filter(models.Post.id == post_id, models.Post.owners_id == user_id ).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(db_post)
    db.commit()
    return {"Complete": "Post was deleted successfully"}

@app.get("/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    code = request.query_params.get("code")
    if not code:
        return {"error": "Authorization code not provided"}
    token_response = await exchange_code_for_token(code)
    if "error" in token_response:
        return token_response
    id_token = token_response["id_token"]
    auth = AuthMiddleware(
        app,
        auth0_domain=AUTH0_DOMAIN,
        client_id=settings.auth0_client_id,
        audience=settings.auth0_api_audience,
        algorithms=settings.auth0_algorithms
    )
    payload = await auth.decode_token(id_token, id_token=True)
    user = db.query(models.User).filter(models.User.email == payload.get("email")).first()
    if user is None:
        user = models.User(name=payload.get("given_name"), email=payload.get("email"))
        db.add(user)
        db.commit()
        db.refresh(user)
    request.session.update({
        "id": user.id,
        "name": payload.get("given_name"),
        "email": payload.get("email"),
    })
    print(request.session)
    return token_response


@app.get('/logout')
async def logout(request: Request):
    redirect_url = f"https://{AUTH0_DOMAIN}/v2/logout?client_id={settings.auth0_client_id}&returnTo=http://localhost:8000"
    return RedirectResponse(url=redirect_url)
