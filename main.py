from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime



app = Flask(__name__)
app.secret_key = 'SecterKeyforhack'
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

manager = LoginManager(app)

app.app_context().push()


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(32), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False)
    first_name = db.Column(db.String(32), nullable=False)
    last_name = db.Column(db.String(32), nullable=False, default=False)
    admin = db.Column(db.Boolean(), nullable=False, default=False)
    avatar = db.Column(db.String(400), default="")
    routes_id = db.Column(db.ForeignKey("routes.id"))
    id_routes_traveled = db.Column(db.ForeignKey("routes.id"))
    comments_id = db.Column(db.ForeignKey("comments.id"))
    description = db.Column(db.Text, default="")


class Routes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    objects_id = db.Column(db.ForeignKey("objects.id"))
    author_id = db.Column(db.ForeignKey("users.id"))
    comments_id = db.Column(db.ForeignKey("comments.id"))


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.ForeignKey("users.id"))
    photo_id = db.Column(db.ForeignKey("photo.id"))
    rating = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date)
    description = db.Column(db.Text, default="")
    routes_id = db.Column(db.ForeignKey("routes.id"))
    parent = db.Column(db.ForeignKey("comments.id"))


class Objects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coordinates = db.Column(db.Integer, nullable=False)
    photo_id = db.Column(db.ForeignKey("photo.id"))
    description = db.Column(db.Text, default="")


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    objects_id = db.Column(db.ForeignKey("objects.id"))
    comments_id = db.Column(db.ForeignKey("comments.id"))

db.create_all()


@manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


@app.route("/")
@app.route("/general")
def general():
    return render_template('index.html')


@app.route("/reg", methods=['GET','POST'])
def reg():
    #if current_user.is_authenticated:
        #return redirect(url_for('general'))
    #else:
        fname = ''
        lname = ''
        login = ''
        password = ''
        password2 = ''

        if request.method == 'POST':
            fname = request.form.get('fname')
            lname = request.form.get('lname')
            login = request.form.get('login')
            password = request.form.get('password')
            password2 = request.form.get('confirm_password')

            user = Users.query.filter_by(login=login).first()
            flash('этот логин уже зарегистрирован')
            #login = ''
            print(fname)
            if password == password2:
                print('password ok')
                password = generate_password_hash(password)
                user = Users(login = login, password = password, first_name =fname, last_name = lname, admin = 0)
                db.session.add(user)
                db.session.commit()
                login_user(user)
                return redirect(url_for('general'))
            else:
                flash('пароли не совпадают')
                password = ''
                password2 = ''

        return render_template('registration.html')


@app.route("/log", methods=['GET','POST'])
def log():
    # if current_user.is_authenticated:
    #     return redirect(url_for('general'))
    # else:
        login = ''
        password = ''
        if request.method == 'POST':
            login = request.form.get('login')
            password = request.form.get('password')
            if login and password:
                try:

                    user = Users.query.filter_by(login=login).first()
                    if check_password_hash(user.password, password):
                        login_user(user)

                        return redirect(url_for('general'))
                    else:

                        flash('Неверный пароль')
                        password = ''
                except:
                    flash('Пользователь не найден')
                    login = ''
                    password = ''
            else:
                flash('Введите логин и пароль')
        return render_template('auth.html',login=login)


@app.route("/out_akk")
def logout():
    logout_user()
    return redirect('general')


@app.route("/profile")
def profile():
    return render_template('profile.html')


if __name__ == "__main__":
    app.run(debug=True)