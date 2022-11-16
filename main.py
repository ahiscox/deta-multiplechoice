from deta import Deta
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import jinja2
import random
from fastapi.staticfiles import StaticFiles
import os

env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
tmpl_home = env.get_template("index.html")
tmpl_results = env.get_template("results.html")


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
deta = Deta(os.getenv("PROJECT_KEY", None))
db = deta.Base(os.getenv("UNIQUE_ID"))

# Check if database exists, if not create it with a default template.
data = db.get("data")

if not data:
    db.insert({
        "questions": {}
    }, "data")


@app.get("/")
async def root():
    data = db.get("data")

    # Randomize answers
    for q in data['questions']:
        random.shuffle(data['questions'][q])

    info = os.getenv("HEADLINE", "Select the answers to the questions below to get the coordinates!")

    return HTMLResponse(tmpl_home.render({'questions': data['questions'], 'info': info}))


@app.post("/answer")
async def answer(request: Request):
    data = db.get("data")

    total = len(data['questions'])
    correct = 0

    form = await request.form()

    for question in form:
        user_answer = form[question]
        correct_answer = data['questions'][question][0]

        if user_answer == correct_answer:
            correct += 1

    return HTMLResponse(tmpl_results.render({'correct': correct, 'total': total, 'coords': os.getenv("COORDS")}))

