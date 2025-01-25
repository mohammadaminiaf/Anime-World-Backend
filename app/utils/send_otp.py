import os
import random
import re
from datetime import datetime, timedelta
from email.message import EmailMessage
from dotenv import load_dotenv
import aiosmtplib
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.otp import OTP

# Load environment variables from .env file
load_dotenv()

# In-memory storage for OTPs (replace with Redis in production)
otp_storage = {}


def generate_otp(user_id: str, db: Session) -> str:
    """
    Generates a random 6-digit OTP and stores it in memory with an expiration time.
    """
    otp = str(random.randint(100000, 999999))
    expiration_time = datetime.now() + timedelta(minutes=10)
    otp_hash = generate_password_hash(otp, method="pbkdf2:sha256", salt_length=8)

    # Create a new OTP record
    otp_record = OTP(
        user_id=user_id,
        otp_hash=otp_hash,
        expires_at=expiration_time,
    )
    db.add(otp_record)
    db.commit()

    return otp


def verify_otp_code(user_id: str, otp: str, db: Session) -> str:
    """
    Verifies if the provided OTP is valid and has not expired.
    """
    # Fetch the latest OTP for the user
    otp_record = (
        db.query(OTP)
        .filter(
            OTP.user_id == user_id,
            OTP.is_used == False,
            OTP.expires_at > datetime.now(),
        )
        .order_by(OTP.created_at.desc())
        .first()
    )

    if not otp_record:
        return 'OTP was not found or has expired.' 
    
    print(f"OTP Record: {otp_record.otp_hash}")
    print(f"Hashed OTP: {generate_password_hash(otp, method='pbkdf2:sha256', salt_length=8)}")

    if check_password_hash(otp_record.otp_hash, otp):
        print("OTP verified successfully.")
        otp_record.is_used = True
        db.commit()
        return ''

    return 'Invalid OTP code.'


#! Verify used otp (verify if an otp has already been used)
def check_used_otp(user_id: str, otp: str, db: Session) -> str:
    """
    Verifies if otp exists and is verified by the user
    """
    # Fetch the latest OTP for the user
    otp_record = (
        db.query(OTP)
        .filter(
            OTP.user_id == user_id,
            OTP.is_used == True,
            OTP.expires_at > datetime.now(),
        )
        .order_by(OTP.created_at.desc())
        .first()
    )

    if not otp_record:
        return 'OTP was not found or has expired.' 
    

    # Check if OTP's match by hasing the new otp and comparing it with the stored otp
    if check_password_hash(otp_record.otp_hash, otp):
        print("OTP verified successfully.")
        # Delete otp from db
        db.delete(otp_record)
        db.commit()
        return ''
    
    print('Invalid OTP code.')

    return 'Invalid OTP code.'

#! Check if Email is valid
def validate_email(email: str) -> bool:
    """Validates the email format."""
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(email_regex, email) is not None


#! Send OTP method
async def send_otp_email(to_email: str, otp: str) -> bool:
    """
    Sends an email with the OTP to the provided email address.
    """
    if not validate_email(to_email):
        print("Invalid email address.")
        return False

    email = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")

    with open("app/templates/otp.html", "r") as file:
        otp_template = file.read()
    html_content = otp_template.replace("{{ otp }}", otp)

    msg = EmailMessage()
    msg["From"] = email
    msg["To"] = to_email
    msg["Subject"] = "Your OTP for Password Reset"
    msg.set_content(
        f"Your OTP for password reset is: {otp}. It will expire in 10 minutes."
    )
    msg.add_alternative(html_content, subtype="html")

    try:
        await aiosmtplib.send(
            msg,
            hostname="smtp.gmail.com",
            port=587,
            username=email,
            password=password,
            start_tls=True,
        )
        return True

    except aiosmtplib.SMTPException as e:
        print(f"Failed to send email: {e}")
        return False
