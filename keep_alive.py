from flask import Flask             
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///phew.db'
db = SQLAlchemy(app)

class data(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    date = db.Column(db.Integer)
    month = db.Column(db.Integer)
    year = db.Column(db.Integer)
    time = db.Column(db.Integer)
    ping = db.Column(db.Boolean)

@app.route('/')
def index():
    return """woah-o, woah-o <br> wait a minute, i think i left my consciousness in the sixth dimension"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)