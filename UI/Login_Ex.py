import sys
import bcrypt
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QLineEdit
from PyQt6 import QtGui, QtCore
from PyQt6.QtCore import Qt
from Final_HocMay.UI.Login import Ui_Login
from Final_HocMay.connector.connector import Connector
from Final_HocMay.UI.SendOTP_Ex import SendOTPWindow
from Final_HocMay.UI.UserHomepage_Ex import UserHomepageWindow
from Final_HocMay.UI.Register_Ex import RegisterWindow

class LoginWindow(QMainWindow, Ui_Login):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButtonLogin.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        self.pushButtonRegisterNow.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        self.db = Connector(database="data")
        self.current_user = None
        self.user_homepage = None
        self.settings = QtCore.QSettings("SmartRetail", "LoginApp")
        self.check_save = getattr(self, "checkBoxSave", None)
        self.label_forgot = getattr(self, "labelForgot", None)
        if self.label_forgot is not None:
            self.label_forgot.setCursor(
                QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            )
            self.label_forgot.mousePressEvent = self.on_forgot_clicked
        self.label_forgot = getattr(self, "labelForgot", None)
        if self.label_forgot is not None:
            self.label_forgot.setCursor(
                QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            )
            self.label_forgot.mousePressEvent = self.on_forgot_clicked
        # Placeholder text
        self.lineEditUserName.clear()
        self.lineEditPassword.clear()
        self.lineEditUserName.setPlaceholderText("UserName")
        self.lineEditPassword.setPlaceholderText("Password")
        style = """
        QLineEdit::placeholder {
            color: rgba(185, 110, 127, 0.6);
        }
        """
        self.lineEditUserName.setStyleSheet(self.lineEditUserName.styleSheet() + style)
        self.lineEditPassword.setStyleSheet(self.lineEditPassword.styleSheet() + style)
        self.pushButtonLogin.clicked.connect(self.login)
        self.pushButtonRegisterNow.clicked.connect(self.open_register)
        self.label_2.setMask(QtGui.QRegion(0, 0, self.label_2.width(), self.label_2.height()))
        path = QtGui.QPainterPath()
        path.moveTo(55, 0)
        path.quadTo(0, 0, 0, 55)
        path.lineTo(0, self.label_2.height())
        path.lineTo(self.label_2.width(), self.label_2.height())
        path.lineTo(self.label_2.width(), 0)
        path.closeSubpath()
        self.label_2.setMask(QtGui.QRegion(path.toFillPolygon().toPolygon()))
        self._show_password = False
        self.label_6.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.label_6.installEventFilter(self)
        self.apply_echo_mode()
        self.load_saved_login()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Type.MouseButtonPress:
            if obj is self.label_6:
                self._show_password = not self._show_password
                self.apply_echo_mode()
                return True
        return super().eventFilter(obj, event)

    def apply_echo_mode(self):
        self.lineEditPassword.setEchoMode(
            QLineEdit.EchoMode.Normal if self._show_password else QLineEdit.EchoMode.Password
        )

    def load_saved_login(self):
        try:
            username = self.settings.value("login/username", "", type=str)
            password = self.settings.value("login/password", "", type=str)
            if username:
                self.lineEditUserName.setText(username)
            if password:
                self.lineEditPassword.setText(password)
            if self.check_save is not None and (username or password):
                self.check_save.setChecked(True)
        except Exception:
            pass

    def save_login_if_needed(self, username: str, password: str):
        try:
            if self.check_save is not None and self.check_save.isChecked():
                self.settings.setValue("login/username", username)
                self.settings.setValue("login/password", password)
            else:
                self.settings.remove("login/username")
                self.settings.remove("login/password")
        except Exception as e:
            print("Cannot save login info:", e)

    def login(self):
        username = self.lineEditUserName.text().strip()
        password = self.lineEditPassword.text()
        if not username and not password:
            QMessageBox.warning(self, "Error", "Please enter your username and password.")
            return
        elif not username:
            QMessageBox.warning(self, "Error", "Please enter your username.")
            return
        elif not password:
            QMessageBox.warning(self, "Error", "Please enter your password.")
            return
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT UserName, Email, Password, Role FROM users WHERE UserName = %s",
                (username,),
            )
            row = cursor.fetchone()
            cursor.close()
            self.db.disConnect()
            if row and bcrypt.checkpw(password.encode("utf-8"), row[2].encode("utf-8")):
                self.current_user = {
                    "username": row[0],
                    "email": row[1],
                    "role": row[3],
                }
                self.save_login_if_needed(username, password)
                self.open_user_homepage()
            else:
                QMessageBox.warning(
                    self,
                    "Invalid Login",
                    "Incorrect username or password. Please try again."
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Database error:\n{e}")

    def on_forgot_clicked(self, event):
        self.open_send_otp()

    def on_register(self, event):
        self.open_register()

    def open_register(self):
        self.register_window = RegisterWindow(login_window=self)
        self.register_window.show()
        self.hide()

    def open_user_homepage(self):
        try:
            self.user_homepage = UserHomepageWindow(user_data=self.current_user)
            self.user_homepage.show()
            self.close()
        except ImportError:
            QMessageBox.warning(
                self,
                "Error",
                "Unable to load the User Homepage. Please check the file name."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open the User Homepage:\n{e}"
            )

    def open_send_otp(self):
        self.otp_window = SendOTPWindow(parent=self)
        self.otp_window.show()
        self.hide()