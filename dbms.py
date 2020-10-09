import random
import smtplib
from flask import redirect, render_template, request, session

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
