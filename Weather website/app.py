import os

from flask import Flask, render_template, redirect, url_for, flash, request, session
import pymysql
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "dev-only-secret")

def get_db():
    return pymysql.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "flaskuser"),
        password=os.environ.get("DB_PASSWORD", "flaskpass"),
        database=os.environ.get("DB_NAME", "prototype"),
        cursorclass=pymysql.cursors.DictCursor,
    )


@app.route("/")
def index():
    return render_template("Home_Page.html")


@app.route('/Sign_up', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["Username"].strip()
        Email = request.form["Email"].strip().lower()
        Password = request.form["Password"]

        if not username or not Email or len(Password) < 8:
            flash("please fill every box")
            return render_template('Sign_up.html')

        connection = get_db()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO Users (Username, Email, Password) "
                    "VALUES (%s, %s, %s)",
                    (username, Email, generate_password_hash(Password)),
                )
                user_id = cursor.lastrowid
                cursor.execute(
                    "INSERT INTO Profiles (User_id, Dark_Mode) "
                    "VALUES (%s, %s)",
                    (user_id, 0,),
                )
            connection.commit()
        except pymysql.err.IntegrityError:
            flash("this email or username is already in use.", "error")
            return render_template('Sign_up.html')
        finally:
            connection.close()
   
        flash("register complete! proceed to login.", "success")
        return render_template('Sign_up.html')
    else:
        return render_template('Sign_up.html')





@app.route('/Log_in', methods=["GET", "POST"])
def Login():
    if request.method == "POST":
        Email = request.form["Email"].strip().lower()
        Password = request.form["Password"]
        connection = get_db()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM Users WHERE Email = %s",
                (Email,)
            )
            user = cursor.fetchone()
        connection.close()
        
        if user and check_password_hash(user["Password"], Password):
            session["User_id"] = user["id"]
            session["Username"] = user["Username"]
            flash(f"welcome {session['Username']}", "success")
            print("user found")
            return redirect(url_for('weather_hub'))
        else:
            print("invalid creds")
            flash("Incorrect username or password.", "error")
            return render_template('Log_in.html')
    else:
        return render_template('Log_in.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("you have been logged out.", "success")
    return redirect(url_for("Home_Page"))


@app.route('/Weather_hub')
def weather_hub():
    return render_template('Weather_hub.html')


if __name__ == '__main__':
    app.run(port=5000)