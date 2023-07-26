from flask import Flask, session, render_template, url_for, request, flash, redirect
from flask_mysqldb import MySQL
import yaml
from passlib.hash import sha256_crypt
from flask_bootstrap import Bootstrap


app = Flask(__name__)
app.secret_key = 'Pr0gr4m1r4nj3'
bootstrap = Bootstrap(app)


db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
mysql = MySQL(app)


@app.route('/')
def home():
    if session.get('username') is None:
        return render_template("inde.html")
    else:
        cur = mysql.connection.cursor()
        result_value = cur.execute("SELECT * from Users")
        if result_value > 0:
            user = cur.fetchall()
            return render_template("home.html", user = user)
        return render_template("home.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if session.get('username') is None:
            cur = mysql.connection.cursor()
            username = request.form.get('username')
            password = request.form.get('password')
            if cur.execute("SELECT * from User where 'username' = %s and password = %s", [username, password]) > 0:
                user = cur.fetchone()
                session['login'] = True
                session['username'] = user[0]
                session['Ime'] = user[1]
                session['Prezime'] = user[2]
                mysql.connection.commit()
                flash("Uspjesno ste se prijavili.", 'success')
                return render_template('home.html')
            else:
                flash('Pogresno username ili password !', 'danger')
                return render_template('login.html')
        else:
            cur = mysql.connection.cursor()
            razredi = cur.execute("SELECT * from 'Razred i odjeljenje'")
            if razredi>0:
                razred = cur.fetchall()
                return render_template('home.html', razred=razred)
            return render_template('home.html')
    else:
        if session.get('username') is not None:
            cur = mysql.connection.cursor()
            razredi = cur.execute("SELECT * from 'Razred i odjeljenje'")
            if razredi > 0:
                razred = cur.fetchall()
                return render_template('home.html', razred=razred)
        else:
            return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    if session.get('username') is not None:
        session.pop('loggedin', None)
        session.pop('username', None)
        flash("Uspjesno ste se odjavili", 'success')
        return render_template('inde.hml')
    else:
        return render_template('inde.html')



@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        username = request.form.get('username')
        ime = request.form.get('Ime')
        prezime = request.form.get('Prezime')
        email = request.form.get('E mail')
        password = request.form.get('password')
        potrda_loz = request.form.get('Potvrda lozinke')
        if password == potrda_loz:
            if (cur.execute('SELECT * FROM Users WHERE email = %s', [email]) == 0):
                cur.execute(
                    'INSERT INTO Users(username, Ime, Prezime, E mail, password) VALUES (%s, %s, %s, %s, %s)',
                    [username, ime, prezime, email, sha256_crypt.hash(password)])
                mysql.connection.commit()
                cur.close()
                flash('Uspješna registracija. Molimo prijavite se.', 'success')
                return redirect(url_for('/login'))
            else:
                flash('Email postoji', 'danger')
                return render_template('registration.html')
        else:
            flash('Pogrešna šifra', 'danger')
            return render_template('registration.html')
    return render_template('registration.html')

@app.errorhandler(404)
def invalid_route(e):
    return render_template("404.html")

@app.errorhandler(500)
def internal_error(e):
    return render_template("500.html")
