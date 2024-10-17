from flask import Flask, render_template, redirect, url_for, session, request, jsonify, make_response, send_from_directory
from flask_restful import Api, Resource
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_dance.contrib.google import make_google_blueprint, google
import matplotlib.backends
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
from requests.models import Response


from dotenv import load_dotenv


from os import environ
from datetime import datetime
import json

load_dotenv()
app = Flask(__name__)
api = Api(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/community')
def community():
    return render_template('community.html')

@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)

