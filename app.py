from flask import Flask


app = Flask(__name__)


@app.route("/index")
@app.route("/home")
@app.route("/")
def index():
    return '<h1>Hello, Tororo!</h1><img src="static/longmao.gif">'


@app.route("/user/<name>")
def user_page(name):
    return 'User: {}'.format(name)
