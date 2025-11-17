# ResetPassword_Ex.py
import bcrypt
from datetime import datetime
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QLineEdit
from Final_HocMay.UI.ResetPassword import Ui_ResetPassword
from Final_HocMay.connector.connector import Connector

class ResetPasswordWindow(QMainWindow, Ui_ResetPassword):
    def __init__(self, email: str, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.parent_window = parent
        self.labelBack.mousePressEvent = self.goback
        self.pushButtonReset.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        self.db = Connector(database="data")
        self.email = email
        self.le_new = getattr(self, "lineEditPassword", None)
        self.le_confirm = getattr(self, "lineEditConfirmPass", None)
        self.le_otp = getattr(self, "lineEditOTP", None)
        self.btn_reset = getattr(self, "pushButtonReset", None)
        self.eye_new = getattr(self, "label_9", None)
        self.eye_confirm = getattr(self, "label_10", None)
        self.label_7.setMask(QtGui.QRegion(0, 0, self.label_7.width(), self.label_7.height()))
        path = QtGui.QPainterPath()
        path.moveTo(55, 0)
        path.quadTo(0, 0, 0, 55)
        path.lineTo(0, self.label_7.height())
        path.lineTo(self.label_7.width(), self.label_7.height())
        path.lineTo(self.label_7.width(), 0)
        path.closeSubpath()
        self.label_7.setMask(QtGui.QRegion(path.toFillPolygon().toPolygon()))
        if self.le_new:
            self.le_new.clear()
            self.le_new.setPlaceholderText("New password")
            self.le_new.setEchoMode(QLineEdit.EchoMode.Password)
        if self.le_confirm:
            self.le_confirm.clear()
            self.le_confirm.setPlaceholderText("Confirm new password")
            self.le_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        if self.le_otp:
            self.le_otp.clear()
            self.le_otp.setPlaceholderText("OTP")
        style = "QLineEdit::placeholder{ color: rgba(185,110,127,0.6); }"
        for w in (self.le_new, self.le_confirm, self.le_otp):
            if w:
                w.setStyleSheet(w.styleSheet() + style)
        self._show_new = False
        self._show_confirm = False
        if self.eye_new:
            self.eye_new.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            self.eye_new.installEventFilter(self)
        if self.eye_confirm:
            self.eye_confirm.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            self.eye_confirm.installEventFilter(self)
        self.apply_echo_mode_new()
        self.apply_echo_mode_confirm()
        if self.btn_reset:
            self.btn_reset.clicked.connect(self.reset_password)
        for w in (self.le_new, self.le_confirm, self.le_otp):
            if w:
                w.returnPressed.connect(self.reset_password)

    def apply_echo_mode_new(self):
        if self.le_new:
            self.le_new.setEchoMode(
                QLineEdit.EchoMode.Normal if self._show_new else QLineEdit.EchoMode.Password
            )

    def apply_echo_mode_confirm(self):
        if self.le_confirm:
            self.le_confirm.setEchoMode(
                QLineEdit.EchoMode.Normal if self._show_confirm else QLineEdit.EchoMode.Password
            )

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Type.MouseButtonPress:
            if obj is self.eye_new and self.le_new:
                self._show_new = not self._show_new
                self.apply_echo_mode_new()
                return True
            if obj is self.eye_confirm and self.le_confirm:
                self._show_confirm = not self._show_confirm
                self.apply_echo_mode_confirm()
                return True
        return super().eventFilter(obj, event)

    def reset_password(self):
        new = (self.le_new.text() if self.le_new else "").strip()
        confirm = (self.le_confirm.text() if self.le_confirm else "").strip()
        otp_input = (self.le_otp.text() if self.le_otp else "").strip()
        if not new or not confirm or not otp_input:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return
        if new != confirm:
            QMessageBox.warning(self, "Error", "Password and confirmation do not match.")
            return
        conn = None
        cursor = None
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT otp_code, otp_expire
                  FROM users
                 WHERE Email = %s
                 LIMIT 1
                """,
                (self.email,)
            )
            row = cursor.fetchone()
            if not row or row[0] is None:
                QMessageBox.warning(self, "Error", "No valid OTP request found for this account.")
                return
            otp_db, expires_at = row[0], row[1]
            if otp_input != otp_db:
                QMessageBox.warning(self, "Error", "Invalid OTP.")
                return
            from datetime import datetime
            now = datetime.now()
            if expires_at is not None and now > expires_at:
                QMessageBox.warning(self, "Error", "OTP has expired.")
                return
            import bcrypt
            hashed = bcrypt.hashpw(new.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            cursor.execute(
                """
                UPDATE users
                   SET Password = %s,
                       otp_code = NULL,
                       otp_expire = NULL
                 WHERE Email = %s
                """,
                (hashed, self.email)
            )
            if cursor.rowcount != 1:
                QMessageBox.warning(self, "Error", "Failed to update password.")
                conn.rollback()
                return
            conn.commit()
            QMessageBox.information(self, "Success", "Password has been reset successfully.")
            from Final_HocMay.UI.Login_Ex import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            QMessageBox.critical(self, "Error", f"System error:\n{e}")
        finally:
            try:
                if cursor:
                    cursor.close()
            except:
                pass
            try:
                self.db.disConnect()
            except:
                pass

    def goback(self, event):
        self.close()
        if self.parent_window:
            self.parent_window.show()

