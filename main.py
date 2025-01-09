from database import engine
import models
from fastapi import FastAPI
from routers import auth,tasks,admin,users


models.Base.metadata.create_all(engine)

app = FastAPI()

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(admin.router)
app.include_router(users.router)

@app.get("/")
def say_hello():
    return "Hello there. Go to /docs for a better view"