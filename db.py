# http://flask.pocoo.org/docs/1.0/tutorial/database/

from flask import current_app, g
from flask.cli import with_appcontext
import psycopg2
from psycopg2 import Error
from psycopg2 import pool
import uuid


def get_db():
    if "db" not in g:

        g.db  = psycopg2.pool.SimpleConnectionPool(
            1, 20,user = "skhbjyhkckrmya",
            password = "1a02de740eb5a2e8cb0b87808b491f4e3e9e4296f6e8691c50faa5897b94c893",
            host = "ec2-46-137-188-105.eu-west-1.compute.amazonaws.com",
            port = "5432",
            database = "do6ogi8lq70ki").getconn()

        g.db.autocommit = True

    return g.db

def close_conn(e):
    print('CLOSING CONN')
    db = g.pop('db', None)
    if db is not None:
        app.config['postgreSQL_pool'].putconn(db)

def init_db():
    db = get_db()
    cursor = db.cursor()
    #with db.connection as cursor:
    cursor.execute(open("schema.sql", "r").read())
 

#@click.command("init-db")
@with_appcontext
def init_db_command():
    try:
        init_db()
    except Exception as e:
        print("error init db:" + str(e))
  
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def delete(userid):
    print("deleting data for userid:", (userid))
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE from Subs where id=%s", (userid,))
    #autocommit
    

def insert(userid, subreddit, frequence):

    print("inserting", userid, subreddit, frequence)
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO Subs (subid, id, subreddit,frequency) VALUES(%s, %s, %s, %s)", (str(uuid.uuid4()), str(userid), subreddit,frequence))
    #autocommit

def select(userid):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("select subreddit, frequency from Subs where id=%s" ,(str(userid),))
    records = cursor.fetchall() 
    return records
