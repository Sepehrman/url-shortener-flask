import datetime

import requests
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from pyshorteners import Shortener

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:Sep123@localhost/somedb"
app.config["TEMPLATES_AUTO_RELOAD"] = True
db = SQLAlchemy(app)

DEFAULT_EXPIRY = datetime.date.today() + datetime.timedelta(days=1)
TOKEN = "NtXtTUvuU51NQjXCqpUy8LUmVrJutb7z6gh96RBnsPyLQup8XlDtQoPvsha5"


class Url(db.Model):
    """
    A URL DB model
    """
    __tablename__ = 'urls'
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String(255))
    short_url = db.Column(db.String(255))
    redirects = db.Column(db.String(12), default=0)
    expiration_date = db.Column(db.Date)

    def __init__(self, long_url: str, short_url, alias: str = "", expiration_date: str = DEFAULT_EXPIRY) -> None:
        """
        A Url initializer of a Model Class Url
        :param long_url: a String
        :param alias: a String
        :param expiry_date: a datetime object
        """
        self.long_url = long_url
        self.short_url = short_url
        self.alias = alias
        self.redirects = 0
        self.expiration_date = expiration_date


@app.route('/')
def index():
    """
    Our index route for the start of the application
    :return: index.html template
    """
    dates = Url.query.filter_by(expiration_date=datetime.date.today()).delete()
    db.session.commit()


    details = {
        "date_today": DEFAULT_EXPIRY
        }

    return render_template('index.html', **details)


@app.route('/redirect/<id>/<path:url>')
def redirect_to(id, url):
    """
    A redirect method responsible for incrementing the redirect counts
    :param id: an Integer
    :param url: a String
    :return: a redirect to the link path
    """

    update = Url.query.filter_by(id=id).first()
    update.redirects = int(update.redirects) + 1
    db.session.commit()
    redirect(request.headers.get("Referer"))
    return redirect(url)


@app.route("/urls", methods=['GET'])
def urls():
    all_urls = Url.query.all()

    return render_template("existing_urls.html", all_urls=all_urls)


@app.route('/submit', methods=['POST'])
def submit():
    """
    A submission route, responsible for rendering success.html upon a POST request
    :return: success.html template
    """
    long_url = request.form['url']
    expiry = request.form['date']
    alias = request.form['alias']
    url = f"https://api.tinyurl.com/create?api_token={TOKEN}&url={long_url}&alias={alias}"

    response = requests.request("POST", url).json()
    print(response)
    error = response.get("errors")

    if len(error) != 0:
        return render_template("errors.html", error= error)

    print(response.get("data"))
    print(response.get("errors"))

    short_url = response.get("data").get("tiny_url")

    some_url = Url(long_url, short_url, expiration_date=expiry, alias=alias)

    db.session.add(some_url)
    db.session.commit()
    data = {
        'long': long_url,
        'short': some_url.short_url,
        'id': some_url.id,
        'expiry': some_url.expiration_date,
    }
    return render_template('success.html', **data)


if __name__ == '__main__':
    app.run()
