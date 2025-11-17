from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout
from PyQt6 import QtWidgets
from Final_HocMay.UI.UserHomepage import Ui_UserHomepage
from Final_HocMay.UI.AboutUs import AboutUs
from Final_HocMay.connector.connector import Connector
from Final_HocMay.UI.MainWindow_Ex import MainWindow
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import QMessageBox
from Final_HocMay.Models.Predictor import predict_for_store_date

class UserHomepageWindow(QMainWindow):

    def __init__(self, user_data=None):
        super().__init__()
        self.user_data = user_data
        self.ui = Ui_UserHomepage()
        self.ui.setupUi(self)
        self.loadHello()
        self.loadHomepage()
        self.ui.labelHello_2.mousePressEvent = self.openAdmin
        self.db = Connector()
        self.db.connect()
        self.loadStores()
        self.ui.btnPredictRecomendation.clicked.connect(self.predictRecommendation)
        self.ui.labelLogout.mousePressEvent = self.logout
        if self.user_data.get("role") != "Admin":
            self.ui.labelHello_2.setEnabled(False)
            self.ui.labelHello_2.setStyleSheet("opacity: 0.3;")
        else:
            self.ui.labelHello_2.setEnabled(True)

    def loadHello(self):
        if self.user_data and "username" in self.user_data:
            username = self.user_data["username"]
            self.ui.labelHello.setText(f"Hello, {username}")
        else:
            self.ui.labelHello.setText("Hello")

    def logout(self, event):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle("Logout Confirmation")
        msg.setText("Are you sure you want to logout?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        result = msg.exec()
        if result == QMessageBox.StandardButton.Yes:
            from Final_HocMay.UI.Login_Ex import LoginWindow  # import TẠI ĐÂY
            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()

    def loadHomepage(self):
        about_widget = AboutUs()
        if self.ui.scrollAreaWidgetContents.layout() is None:
            layout = QVBoxLayout(self.ui.scrollAreaWidgetContents)
        else:
            layout = self.ui.scrollAreaWidgetContents.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        layout.addWidget(about_widget)

    def loadStores(self):
        sql = "SELECT DISTINCT store_nbr FROM cleaned_train ORDER BY store_nbr;"
        df = self.db.queryDataset(sql)
        if df is not None:
            for s in df["store_nbr"].tolist():
                self.ui.comboBoxStore.addItem(str(s))

    def loadDates(self):
        sql = "SELECT DISTINCT date FROM cleaned_train ORDER BY date;"
        df = self.db.queryDataset(sql)
        if df is not None and len(df) > 0:
            dates = sorted(df["date"].tolist())
            min_date = QDate.QDate.fromString(str(dates[0]), "yyyy-MM-dd")
            max_date = QDate.QDate.fromString(str(dates[-1]), "yyyy-MM-dd")
            self.ui.dateEditDate.setMinimumDate(min_date)
            self.ui.dateEditDate.setMaximumDate(max_date)
            self.ui.dateEditDate.setDate(min_date)
    def predictRecommendation(self):
        try:
            date_str = self.ui.dateEditDate.text().strip()
            store_str = self.ui.comboBoxStore.currentText().strip()
            if not date_str or not store_str:
                raise ValueError("Vui lòng nhập đầy đủ Date và Store.")
            store_nbr = int(store_str)
            if not (1 <= store_nbr <= 54):
                raise ValueError("Store phải từ 1 đến 54.")
            df = predict_for_store_date(date_str, store_nbr)
            df = df.head(5)
            model = QStandardItemModel()
            for i, row in df.iterrows():
                text = f"{i + 1}. {row['FAMILY']}"
                item = QStandardItem(text)
                model.appendRow(item)
            self.ui.listView.setModel(model)
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))

    def openAdmin(self, event):
        if self.user_data.get("role") != "Admin":
            QMessageBox.warning(self, "No permission", "Only Admin can access this page.")
            return
        self.admin_window = MainWindow(parent=self)
        self.admin_window.show()
        self.hide()


