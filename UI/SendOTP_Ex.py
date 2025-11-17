# SendOTP_Ex.py
import sys
import random
import smtplib
from datetime import datetime, timedelta
from PyQt6 import QtWidgets, QtGui, QtCore
from Final_HocMay.UI.SendOTP import Ui_OTP
from Final_HocMay.connector.connector import Connector
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from Final_HocMay.UI.ResetPassword_Ex import ResetPasswordWindow


ADMIN_EMAIL = "codera8386@gmail.com"
ADMIN_APP_PASSWORD = "tjej arst nwfd vbsc"

OTP_LIFETIME_SECONDS = 120


class SendOTPWindow(QtWidgets.QMainWindow, Ui_OTP):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.parent_window = parent
        self.labelBack.mousePressEvent = self.goback
        self.pushButtonSend.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        self.setWindowTitle("Smart Retail - Reset Password with OTP")
        self.db = Connector()
        self.db.connect()
        self.lineEditEmail.clear()
        self.lineEditEmail.setPlaceholderText("Enter your registered email")
        self.label_2.setMask(QtGui.QRegion(0, 0, self.label_2.width(), self.label_2.height()))
        path = QtGui.QPainterPath()
        path.moveTo(55, 0)
        path.quadTo(0, 0, 0, 55)
        path.lineTo(0, self.label_2.height())
        path.lineTo(self.label_2.width(), self.label_2.height())
        path.lineTo(self.label_2.width(), 0)
        path.closeSubpath()
        self.label_2.setMask(QtGui.QRegion(path.toFillPolygon().toPolygon()))
        self.pushButtonSend.clicked.connect(self.send_otp)
        if hasattr(self, "label_7"):
            self.label_7.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            self.label_7.mousePressEvent = self.go_home

    def go_home(self, event):
        self.close()

    def send_otp(self):
        try:
            email = self.lineEditEmail.text().strip()
            if not email:
                QtWidgets.QMessageBox.warning(self, "Warning", "Please enter your email address.")
                return
            if not self.email_exists(email):
                QtWidgets.QMessageBox.warning(self, "Error", "Email address is not registered.")
                return
            otp = f"{random.randint(0, 999999):06d}"
            expires_at = datetime.now() + timedelta(seconds=OTP_LIFETIME_SECONDS)
            if not self.update_otp_for_email(email, otp, expires_at):
                QtWidgets.QMessageBox.critical(self, "Error", "Failed to save OTP to database.")
                return

            self.send_otp_email(email, otp)
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
            msg.setWindowTitle("OTP Sent")
            msg.setText(f"An OTP has been sent to {email}.")
            msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
            result = msg.exec()

            if result == QtWidgets.QMessageBox.StandardButton.Ok:
                from Final_HocMay.UI.ResetPassword_Ex import ResetPasswordWindow
                self.reset_window = ResetPasswordWindow(email=email, parent=self)
                self.reset_window.show()
                self.hide()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QtWidgets.QMessageBox.critical(self, "FATAL ERROR", str(e))

    def email_exists(self, email: str) -> bool:
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE Email = %s LIMIT 1", (email,))
        row = cursor.fetchone()
        conn.close()
        return row is not None

    def update_otp_for_email(self, email: str, otp: str, expires_at: datetime) -> bool:
        conn = self.db.connect()
        cursor = conn.cursor()
        sql = """
            UPDATE users
               SET otp_code = %s,
                   otp_expire = %s
             WHERE Email = %s
        """
        cursor.execute(sql, (otp, expires_at, email))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected == 1

    def send_otp_email(self, to_email: str, otp: str):
        subject = "Smart Retail - OTP Reset Password"
        body = (
            f"Your OTP to reset the password is: {otp}\n\n"
            f"This OTP is valid for {OTP_LIFETIME_SECONDS} seconds and can be used only once."
        )
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = Header(subject, "utf-8")
        msg["From"] = formataddr(("Smart Retail", ADMIN_EMAIL))
        msg["To"] = to_email
        try:
            with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as smtp:
                smtp.set_debuglevel(1)  # <<< BẬT DEBUG
                smtp.starttls()
                smtp.login(ADMIN_EMAIL, ADMIN_APP_PASSWORD)
                smtp.sendmail(ADMIN_EMAIL, [to_email], msg.as_string())
            print("OTP sent successfully!")
        except Exception as e:
            print(f"[EMAIL ERROR] {e}")
            raise
    def goback(self, event):
        self.close()
        if self.parent_window:
            self.parent_window.show()
