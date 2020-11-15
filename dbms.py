import random
import smtplib
from flask import redirect, render_template, request, session
from functools import wraps

def generate_otp(email, message = None):
    if not message:
        # Generating OTP & storing it's value and message
        OTP = str(random.randint(1000, 9999))
        session['my_var'] = f"{OTP}"
        message = "Your OTP for DEMS is " + OTP + "."

    # Sending Email
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login("rymaIITK@gmail.com", "a!1234IIT")
    server.sendmail("rymaIITK@gmail.com", email, message)

    return OTP

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/employee_login")
        return f(*args, **kwargs)
    return decorated_function

def admin_login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/admin_login")
        elif not session.get("admin_login"):
            return "You Don't Have permission to view this page"
        return f(*args, **kwargs)
    return decorated_function


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code
