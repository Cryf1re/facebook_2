from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import json, os

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

POSTS_FILE = "PostData/posts.json"

# Создать файл и папку, если не существует
os.makedirs("PostData", exist_ok=True)
if not os.path.exists(POSTS_FILE):
    with open(POSTS_FILE, "w") as f:
        json.dump([], f)

# Загрузка и сохранение данных
def load_posts():
    with open(POSTS_FILE, "r") as f:
        return json.load(f)

def save_posts(posts):
    with open(POSTS_FILE, "w") as f:
        json.dump(posts, f, indent=4)

# Главная страница
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    posts = load_posts()
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})

# Страница создания поста
@app.get("/create", response_class=HTMLResponse)
def create_form(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})

@app.post("/create")
def create_post(username: str = Form(...), title: str = Form(...), content: str = Form(...)):
    posts = load_posts()
    post_id = max([p["id"] for p in posts], default=0) + 1
    posts.append({"id": post_id, "username": username, "title": title, "content": content})
    save_posts(posts)
    return RedirectResponse("/", status_code=303)

# Страница редактирования
@app.get("/edit/{post_id}", response_class=HTMLResponse)
def edit_form(post_id: int, request: Request):
    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("edit.html", {"request": request, "post": post})

@app.post("/edit/{post_id}")
def edit_post(post_id: int, username: str = Form(...), title: str = Form(...), content: str = Form(...)):
    posts = load_posts()
    for p in posts:
        if p["id"] == post_id:
            p["username"] = username
            p["title"] = title
            p["content"] = content
            break
    save_posts(posts)
    return RedirectResponse("/", status_code=303)

# Удаление поста
@app.get("/delete/{post_id}")
def delete_post(post_id: int):
    posts = load_posts()
    posts = [p for p in posts if p["id"] != post_id]
    save_posts(posts)
    return RedirectResponse("/", status_code=303)
