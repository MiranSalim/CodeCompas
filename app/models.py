from peewee import (
    Model, CharField, BooleanField,
    DateTimeField, TextField, ForeignKeyField
)
import datetime

from .db import db  # 👈 gebruik de gedeelde db uit app/db.py


class BaseModel(Model):
    class Meta:
        database = db


class Profile(BaseModel):
    email = CharField(unique=True, max_length=255)
    name = CharField(null=True, max_length=255)
    role = CharField(default="USER")  # USER of ADMIN
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.datetime.utcnow)


class Topic(BaseModel):
    title = CharField(max_length=255)
    description = TextField(null=True)
    created_at = DateTimeField(default=datetime.datetime.utcnow)


class Subtopic(BaseModel):
    topic = ForeignKeyField(Topic, backref="subtopics", on_delete="CASCADE")
    title = CharField(max_length=255)
    description = TextField(null=True)
    created_at = DateTimeField(default=datetime.datetime.utcnow)


def create_tables():
    with db:
        db.create_tables([Profile, Topic, Subtopic])
