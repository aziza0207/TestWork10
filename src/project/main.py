from fastapi import FastAPI, Depends, HTTPException
from .database import Base
from . import models, schemas
from .database import SessionLocal, engine, get_db
from .routers import task, auth

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(task.router)
app.include_router(auth.router)
