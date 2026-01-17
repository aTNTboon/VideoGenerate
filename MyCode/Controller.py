from MyCode.util.SceneParserService import SecenePaser
import flask
import json
import os

app = flask.Flask(__name__)

@app.route('/')
def index(uid):
    return 'Hello World!'


