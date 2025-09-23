from peewee import (
    Model, CharField, TextField,
    DateTimeField, ForeignKeyField, UUIDField, AutoField
)
from playhouse.pool import PooledPostgresqlDatabase
from datetime import datetime
import os


# ✅ Database connectie (Supabase via .env DATABASE_URL of losse PG-variabelen)
db = PooledPostgresqlDatabase(
    os.getenv("PGDATABASE", "postgres"),
    user=os.getenv("PGUSER", "postgres"),
    password=os.getenv("PGPASSWORD", ""),
    host=os.getenv("PGHOST", "localhost"),
    port=int(os.getenv("PGPORT", 5432)),
    max_connections=8,
    stale_timeout=300,
)


class BaseModel(Model):
    class Meta:
        database = db


# 🔑 Link met Supabase auth.users (UUID als primary key)
class Profile(BaseModel):
    id = UUIDField(primary_key=True)   # zelfde id als auth.users.id (UUID in Supabase)
    email = CharField(unique=True)
    display_name = CharField(null=True)
    role = CharField(default="TRAINEE")  # ADMIN of TRAINEE
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)


class Topic(BaseModel):
    id = AutoField()
    title = CharField()
    description = TextField(null=True)
    created_at = DateTimeField(default=datetime.utcnow)


class Subtopic(BaseModel):
    id = AutoField()
    topic = ForeignKeyField(Topic, backref="subtopics", on_delete="CASCADE")
    title = CharField()
    description = TextField(null=True)
    created_at = DateTimeField(default=datetime.utcnow)


# ✅ Create tables functie
def create_tables():
    with db:
        db.create_tables([Profile, Topic, Subtopic])
