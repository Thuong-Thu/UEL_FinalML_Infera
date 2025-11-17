from PyQt6.QtWidgets import QApplication
from Final_HocMay.UI.Login_Ex import LoginWindow
import sys

app = QApplication(sys.argv)
login = LoginWindow()
login.show()
sys.exit(app.exec())