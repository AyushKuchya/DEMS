import random
import smtplib

def hello():
    return "Hello World"


def generate_otp(email, message = None):
    if not message:
        # Generating OTP & storing it's value and message
        OTP = str(random.randint(1000, 9999))
        message = "Your OTP for Rate Your Mate! is " + OTP + "."

    # Sending Email
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login("rymaIITK@gmail.com", "a!1234IIT")
    server.sendmail("rymaIITK@gmail.com", email, message)