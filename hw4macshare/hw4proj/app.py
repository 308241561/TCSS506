from flask import Flask, render_template, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,SubmitField, DateField,IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, Email, NumberRange
from yelp import find_coffee
from wiki import findBirths
from flask_login import current_user, login_user, login_required, logout_user
from models import db, login, UserModel

class loginForm(FlaskForm):
    email=StringField(label="Enter email", validators=[DataRequired(),Email()])
    password=PasswordField(label="Enter password",validators=[DataRequired(), Length(min=6,max=16)])
    submit=SubmitField(label="Login")

class searchForm(FlaskForm):
    date=DateField(label="Enter birthday", validators=[DataRequired()])
    searchNum=IntegerField(label="Enter number of results",validators=[DataRequired(), NumberRange(min=1, max=20, message=None)])
    submit=SubmitField(label="Search")

#passwords={}
#passwords['lhhung@uw.edu']='qwerty'

app = Flask(__name__)
app.secret_key="a secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/login.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login.init_app(app)

def addUser(email, password):
    #check if email or username exits
    user=UserModel()
    user.set_password(password)
    user.email=email
    db.session.add(user)
    db.session.commit()

@app.before_first_request
def create_table():
    db.create_all()
    user = UserModel.query.filter_by(email = "lhhung@uw.edu").first()
    if user is None:
        addUser("lhhung@uw.edu","qwerty")    
    
# @app.route("/home")
# @login_required
# def findCoffee():
#     return render_template("home.html", myData=find_coffee())

@app.route("/home", methods=['GET','POST'])
@login_required
def findBirthDay():
    form=searchForm()
    if form.validate_on_submit():
        if request.method == "POST":
            date=request.form["date"]
            # 2018-12-19
            month_day = date[-5:-3]+'/'+date[-2:]
            year = date[:4]
            searchNum=request.form["searchNum"]
            return render_template("home.html", myData=findBirths(month_day, year, searchNum), form=form)

    # return render_template("home.html", myData=findBirths('01/01', "1998", 1), form=form)
    return render_template("home.html", form=form)

@app.route("/")
def redirectToLogin():
    return redirect("/login")


@app.route("/login",methods=['GET','POST'])
def login():
    form=loginForm()
    if form.validate_on_submit():
        if request.method == "POST":
            email=request.form["email"]
            pw=request.form["password"]
            user = UserModel.query.filter_by(email = email).first()
            if user is not None and user.check_password(pw) :
                login_user(user)
                return redirect('/home')
    return render_template("login.html",form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/login')

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
