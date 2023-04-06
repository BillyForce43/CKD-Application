import numpy as np
import pickle
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_session import Session
import sqlite3
from decimal import Decimal


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ckdprediction.db'
app.config['SESSION_TYPE'] = 'filesystem'
login_manager = LoginManager()
login_manager.init_app(app)
session = Session(app)
db = SQLAlchemy(app)
model = pickle.load(open('model.pkl', 'rb')) # doctor_model version
model2 = pickle.load(open('model2.pkl', 'rb')) # general_person_model version

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(2), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.String(10), nullable=True)

    ## Attribute ALL For Predict
    blood_pressure = db.Column(db.String(20), nullable=True)
    albumin = db.Column(db.String(10), nullable=True)
    sugar = db.Column(db.String(10), nullable=True)
    blood_glucose_random = db.Column(db.String(10), nullable=True)
    blood_urea = db.Column(db.String(10), nullable=True)
    serum_creatinine = db.Column(db.String(10), nullable=True)
    haemoglobin = db.Column(db.String(10), nullable=True)
    packed_cell_volume = db.Column(db.String(10), nullable=True)
    red_blood_cell_count = db.Column(db.String(10), nullable=True)
    hypertension = db.Column(db.String(10), nullable=True)
    diabetes_mellitus = db.Column(db.String(10), nullable=True)
    coronaru_artery_disease = db.Column(db.String(10), nullable=True)
    appetite = db.Column(db.String(10), nullable=True)
    anemia = db.Column(db.String(10), nullable=True)
    hypertension = db.Column(db.String(10), nullable=True)
    diabetes_mellitus = db.Column(db.String(10), nullable=True)
    appetite = db.Column(db.String(10), nullable=True)
    anemia = db.Column(db.String(10), nullable=True)
    peda_edema = db.Column(db.String(10), nullable=True)
    result = db.Column(db.String(10), nullable=True)

    ##
    history_type = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    user = db.relationship('User', backref='history_user')
    patient = db.relationship('Patient', backref='history_patient')

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.String(10), nullable=True)
    firstname = db.Column(db.String(80), nullable=True)
    lastname = db.Column(db.String(80), nullable=True)
    tel = db.Column(db.String(120), nullable=True)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='patient')

db.create_all()

@login_manager.user_loader
def load_user(user_id):
    # Load and return a user object from the database
    # based on the user_id
    return User.query.get(int(user_id))


@app.route('/')
def index():
    login_now = 0
    if current_user.is_authenticated:
        # User is logged in
        login_now = 1
        return render_template('index.html',login_now=login_now)
    else:
        # User is not logged in
        return render_template('index.html',login_now=login_now)

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         user = User.query.filter_by(username=username).first()
#         if user and check_password_hash(user.password, password):
#             login_user(user)
#             return redirect(url_for('welcome'))
#         flash('Invalid username or password')
#     return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        
        if user:
            login_user(user)
            return redirect(url_for('welcome'))
        else:
            flash('Invalid username or password', 'error')
            return redirect('/login')

         # Check if the username and password are correct
        # if username != 'correct_username' or password != 'correct_password':
        #     flash('Invalid username or password', 'error')
        #     return redirect('/login')
        # else:
        #     login_user(user)
        #     return redirect(url_for('welcome'))
        
        # If the username and password are correct, redirect to the home page
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        role = request.form['user_role']

        user = User(username=username, firstname=firstname, lastname=lastname, password=password, email=email, role=role)
        db.session.add(user)
        db.session.commit()

        return redirect('/login')
    return render_template('register.html')

@app.route('/checkrole')
def checkrole():
    if current_user.is_authenticated:
        user_id = current_user.id
        conn = sqlite3.connect('ckdprediction.db')
        cur = conn.cursor()
        cur.execute("SELECT role FROM user WHERE id=?", (user_id,))
        users = cur.fetchone()
        conn.close()
        if users[0] == '1':
            return redirect(url_for('prediction_doctor'))
        elif users[0] == '2':
            return redirect(url_for('prediction_guest'))
    return redirect(url_for('login'))


# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     user_id = current_user.id
#     print(user_id)
#     return redirect(url_for('index'))
@app.route('/logout')
@login_required
def logout():
    user_id = None
    if current_user.is_authenticated:
        user_id = current_user.id
        logout_user()
    print(user_id)
    return redirect(url_for('index'))

@app.route('/result')
def reslult():
    return render_template('result.html')

@app.route('/welcome')
def welcome():
    # prepare data for show history of prediction

    history_guest = History.query.filter_by(user_id=current_user.id,history_type=2).order_by(History.timestamp.desc()).all()
    user_data = User.query.filter(User.id == current_user.id).first()

    # history_med = db.session.query(History,Patient).join(Patient).filter(History.user_id == Patient.user_id).order_by(History.timestamp.desc()).all()
    history_med = History.query.filter_by(user_id = current_user.id, history_type = '1').order_by(History.timestamp.desc()).all()
    

    # prepare data for show history of prediction

    med_role = 0
    guest_role = 0
    admin_role = 0
    # check role to show history
    if current_user.is_authenticated:
        user_id = current_user.id
        conn = sqlite3.connect('ckdprediction.db')
        cur = conn.cursor()
        cur.execute("SELECT role FROM user WHERE id=?", (user_id,))
        users = cur.fetchone()
        conn.close()
        if users[0] == '1':
            med_role = 1
        elif users[0] == '2':
            guest_role = 1
        elif users[0] == '3':
            admin_role = 1
    # check role to show history

    return render_template('welcome.html', history_med=history_med, user_data=user_data, history_guest=history_guest, 
                           med_role=med_role, guest_role=guest_role,admin_role=admin_role)

@app.route('/add_patient',methods=['POST'])
def add_patient():
    if request.method == 'POST':
        fname=request.form['firstname'],
        lname=request.form['lastname'],
        tel=request.form['tel'],
        age=request.form['age']
        patient = Patient(
            age = age[0],
            firstname = fname[0],
            lastname = lname[0],
            tel = tel[0],
            user=current_user
        )
        db.session.add(patient)
        db.session.commit()
        return redirect('/prediction_doctor')
        
    return render_template('prediction-doctor.html')


@app.route('/admin_history_med')
def admin_history():
    users = User.query.all()
    medhistory = History.query.fillter_by(history_type = 1).order_by(History.timestamp.desc()).all()
    return render_template('admin-history-med.html', users=users,medhistory=medhistory)

@app.route('/admin_history_guest')
def admin_guest():
    users = User.query.all()
    guesthistory = History.query.fillter_by(history_type = 2).order_by(History.timestamp.desc()).all()
    return render_template('admin-history-guest.html', users=users,guesthistory=guesthistory)

@app.route('/contact')
def contact():
    login_now = 0
    if current_user.is_authenticated:
        # User is logged in
        login_now = 1
        return render_template('contact.html',login_now=login_now)
    else:
        # User is not logged in
        return render_template('contact.html',login_now=login_now)
    

@app.route('/prediction_doctor')
def prediction_doctor():
    # users = User.query.all()
    patient = Patient.query.filter_by(user_id=current_user.id).order_by(Patient.timestamp.desc()).all()
    return render_template('prediction-doctor.html',patient=patient)

@app.route('/prediction_guest')
def prediction_guest(): 
    return render_template('prediction-guest.html')

@app.route('/predict_doctor',methods=['POST'])
def predict_doctor():
    #For rendering results on HTML GUI
    if request.method == 'POST':  
        int_features = [float(x) for x in request.form.values()]
        int_features.pop(0)
        final_features = [np.array(int_features)]
        prediction = model.predict(final_features)
        output = round(prediction[0], 2)

        #convert output to decimal
        int_output = int(output)
        decimal_output = Decimal(int_output)
        string_output = str(decimal_output)

        age=request.form['age'],
        blood_pressure=request.form['blood_pressure'],
        albumin=request.form['albumin'],
        sugar=request.form['sugar'],
        blood_glucose_random=request.form['blood_glucose_random'],
        blood_urea=request.form['blood_urea'],
        serum_creatinine=request.form['serum_creatinine'],
        haemoglobin=request.form['haemoglobin'],
        packed_cell_volume=request.form['packed_cell_volume'],
        red_blood_cell_count=request.form['red_blood_cell_count'],
        hypertension=request.form['hypertension'],
        diabetes_mellitus=request.form['diabetes_mellitus'],
        coronaru_artery_disease=request.form['coronaru_artery_disease'],
        appetite=request.form['appetite'],
        anemia=request.form['anemia'],
        history_type = 1,
        patient_id = int(request.form['patient_list'])


        history = History(
            age=age[0],
            blood_pressure = blood_pressure[0],
            albumin=albumin[0],
            sugar=sugar[0],
            blood_glucose_random=blood_glucose_random[0],
            blood_urea=blood_urea[0],
            serum_creatinine=serum_creatinine[0],
            haemoglobin=haemoglobin[0],
            packed_cell_volume=packed_cell_volume[0],
            red_blood_cell_count=red_blood_cell_count[0],
            hypertension=hypertension[0],
            diabetes_mellitus=diabetes_mellitus[0],
            coronaru_artery_disease=coronaru_artery_disease[0],
            appetite=appetite[0],
            anemia=anemia[0],
            result=string_output,
            history_type=history_type[0],
            patient_id = patient_id,
            user=current_user
        )
        db.session.add(history)
        db.session.commit()

    return render_template('result.html', prediction_text='Your Result :{}'.format(output),output=output)

@app.route('/predict_guest',methods=['POST'])
def predict_guest():
    #For rendering results on HTML GUI
    if request.method == 'POST':
        int_features = [float(x) for x in request.form.values()]
        final_features = [np.array(int_features)]
        prediction = model2.predict(final_features)
        output = round(prediction[0], 2)
        
        #convert output to decimal
        int_output = int(output)
        decimal_output = Decimal(int_output)
        string_output = str(decimal_output)

        age = request.form['age']
        hypertension = request.form['hypertension']
        diabetes_mellitus = request.form['diabetes_mellitus']
        appetite = request.form['appetite']
        anemia = request.form['anemia']
        peda_edema = request.form['peda_edema']
        history_type = 2
        history = History(age=age, hypertension=hypertension, diabetes_mellitus=diabetes_mellitus, appetite=appetite,
                               anemia=anemia, peda_edema=peda_edema,result=string_output,history_type=history_type,patient_id = 0,user=current_user)
        db.session.add(history)
        db.session.commit()
    return render_template('result.html',output=output)
# prediction_text='Your Result :{}'.format(output),output=output

if __name__ == '__main__':
    app.run(debug=True)
