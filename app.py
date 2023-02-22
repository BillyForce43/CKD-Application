import numpy as np
import pickle
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_sqlalchemy import SQLAlchemy
import datetime
from datetime import datetime
from flask import Flask, g


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
model = pickle.load(open('model.pkl', 'rb'))
model2 = pickle.load(open('model2.pkl', 'rb'))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reslut = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

db.create_all()



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        
        if user:
            return redirect(url_for('welcome'))
        else:
            return 'Invalid Login. Please try again.'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']

        user = User(username=username, firstname=firstname, lastname=lastname, password=password, email=email)
        db.session.add(user)
        db.session.commit()

        return redirect('/login')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('firstname', None)
    session.pop('lastname', None)
    return redirect('/login')
@app.route('/result')
def reslult():
    return render_template('result.html')

@app.route('/welcome')
def welcome():
    user_id = session.get('user_id')
    firstname = session.get('firstname')
    lastname = session.get('lastname')
    if user_id and firstname and lastname:
        return render_template('welcome.html', firstname=firstname, lastname=lastname)
    return render_template('welcome.html')
    
@app.route('/users')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/prediction-doctor')
def prediction_doctor():
    return render_template('prediction-doctor.html')

@app.route('/prediction-guest')
def prediction_guest():
    return render_template('prediction-guest.html')

@app.route('/predict_doctor',methods=['POST'])
def predict_doctor():
    #For rendering results on HTML GUI
    int_features = [float(x) for x in request.form.values()]
    final_features = [np.array(int_features)]
    prediction = model.predict(final_features)
    output = round(prediction[0], 2)
    # print(output)
    # if output == 0:
    #     output = "CKD"
    # else:
    #     output = "Not CKD" 
    return render_template('result.html', prediction_text='Your Result :{}'.format(output),output=output)

@app.route('/predict_guest',methods=['POST'])
def predict_guest():
    #For rendering results on HTML GUI
    int_features = [float(x) for x in request.form.values()]
    final_features = [np.array(int_features)]
    prediction = model2.predict(final_features)
    output = round(prediction[0], 2)
    # print(output)
    # if output == 0:
    #     output = "CKD"
    # else:
    #     output = "Not CKD" 
    return render_template('result.html', prediction_text='Your Result :{}'.format(output),output=output)


if __name__ == '__main__':
    app.run(debug=True)
