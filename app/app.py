from flask import Flask
from peewee import SqliteDatabase

app = Flask(__name__)

db = SqliteDatabase('domaindash.db')