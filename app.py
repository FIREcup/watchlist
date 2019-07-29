from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
import os, sys
import click


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 关闭读模型修改的监控
db = SQLAlchemy(app)


@app.route("/index")
@app.route("/home")
@app.route("/")
def index():
    return render_template('index.html', name=name, movies=movies)


@app.route("/user/<name>")
def user_page(name):
    return 'User: {}'.format(name)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop')
def initdb(drop):
    """
    Initialize the database
    """
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.') #输出提示信息


@app.cli.command()
def forge():
    """
    Generate fake data.
    """
    db.create_all()
    name = "Jack Yang"
    movies = [
            {'title': 'My Neighbor Totoro', 'year': '1988'},
            {'title': 'Dead Poets Society', 'year': '1989'},
            {'title': 'A Perfect World', 'year': '1993'},
            {'title': 'Leon', 'year': '1994'},
            {'title': 'Mahjong', 'year': '1996'},
            {'title': 'Swallowtail Butterfly', 'year': '1996'},
            {'title': 'King of Comedy', 'year': '1999'},
            {'title': 'Devils on the Doorstep', 'year': '1999'},
            {'title': 'WALL-E', 'year': '2008'},
            {'title': 'The Pork of Music', 'year': '2012'}
    ]
    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)

    db.session.commit()
    click.echo('Done.')
