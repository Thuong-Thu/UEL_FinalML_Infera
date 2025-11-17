import pandas as pd

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHeaderView, QTableWidgetItem, QFileDialog, \
    QMessageBox
from Final_HocMay.UI.MainWindow import Ui_Admin
import mysql.connector
import sys
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QDate
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from Final_HocMay.Models.Statistic import Statistic
from Final_HocMay.connector.connector import Connector
from Final_HocMay.UI.ChartHandle import ChartHandle
from Final_HocMay.Models.Predictor import predict_any_date, predict_for_store_date
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.parent_window = parent
        self.ui = Ui_Admin()
        self.ui.setupUi(self)
        # self.conn = mysql.connector.connect(
        #     host="localhost",
        #     user="root",
        #     password="thuvt23406@",
        #     database="data"
        # )
        # self.cursor = self.conn.cursor()
        self.table_map = {
            "Holidays_Events": "holidays_events",
            "Items": "items",
            "Stores": "stores",
            "Oil": "oil",
            "Train": "train",
            "Test": "test",
            "Transaction": "transactions",
            "Users": "users"
        }
        self.db = Connector()
        self.db.connect()
        self.ui.comboBoxData.currentTextChanged.connect(self.load_table_data)
        self.load_table_data(self.ui.comboBoxData.currentText())
        self.ui.lineEditFilter.textChanged.connect(self.filter_table)
        self.loadStores()
        self.loadFamilies()
        self.statistic = Statistic()
        self.chartHandle = ChartHandle()
        self.ui.btnPredictP.clicked.connect(self.predict_one_product)
        self.ui.btnPredictD.clicked.connect(self.predict_by_day)
        self.ui.btnPeakLowSales.clicked.connect(self.showHighestLowest)
        self.ui.btnEarthquakeSales.clicked.connect(self.showEarthquakeTrend)
        self.ui.btnHolidayVsNormal.clicked.connect(self.showHolidaySales)
        self.ui.btnSalesByWeekday.clicked.connect(self.showSalesByDay)
        self.ui.btnCorrelationHeatmap.clicked.connect(self.showHeatmap)
        self.ui.btnLagPlot.clicked.connect(self.showPreserved_duplicate_structure)
        self.ui.btnYearlySales.clicked.connect(self.showTotalSales)
        self.ui.actionBack.triggered.connect(self.goBack)
    def load_table_data(self, ui_name):
        try:
            table_name = self.table_map.get(ui_name)
            if table_name is None:
                print("Không tìm thấy bảng trong mapping:", ui_name)
                return
            sql = f"SELECT * FROM {table_name}"
            print("RUN:", sql)
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            col_names = [desc[0] for desc in self.cursor.description]
            self.ui.tableWidget.setColumnCount(len(col_names))
            self.ui.tableWidget.setHorizontalHeaderLabels(col_names)
            self.ui.tableWidget.setRowCount(0)
            for row_data in result:
                row_index = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(row_index)
                for col, value in enumerate(row_data):
                    self.ui.tableWidget.setItem(row_index, col, QtWidgets.QTableWidgetItem(str(value)))
        except Exception as e:
            print("Lỗi:", e)

    def filter_table(self, text):
        text = text.lower()
        row_count = self.ui.tableWidget.rowCount()
        col_count = self.ui.tableWidget.columnCount()
        for row in range(row_count):
            row_visible = False
            for col in range(col_count):
                item = self.ui.tableWidget.item(row, col)
                if item is not None and text in item.text().lower():
                    row_visible = True
                    break
            self.ui.tableWidget.setRowHidden(row, not row_visible)

    def normalize_date(date_text):
        try:
            dt = pd.to_datetime(date_text)
            return dt.strftime("%Y-%m-%d")
        except:
            return None

    def showTable(self, df):
        self.ui.tableWidgetListofData.setRowCount(len(df))
        self.ui.tableWidgetListofData.setColumnCount(len(df.columns))
        self.ui.tableWidgetListofData.setHorizontalHeaderLabels(df.columns)
        for r in range(len(df)):
            for c in range(len(df.columns)):
                item = QTableWidgetItem(str(df.iloc[r, c]))
                self.ui.tableWidgetListofData.setItem(r, c, item)

    def showHighestLowest(self):
        df = self.statistic.getHighestAndLowestSalesByYear()
        self.showTable(df)
        self.chartHandle.drawHighestLowest(df, self.ui.verticalLayout)

    def showEarthquakeTrend(self):
        df, eq = self.statistic.getSalesTrendBeforeAfterEarthquake()
        before_df = df[df["date"] < eq]
        after_df = df[df["date"] >= eq]
        self.showTable(df)
        self.chartHandle.drawEarthquakeTrend(before_df, after_df, self.ui.verticalLayout)

    def showHolidaySales(self):
        df = self.statistic.getSalesHolidayByStoretype()
        self.showTable(df)
        self.chartHandle.drawHolidaySales(df, self.ui.verticalLayout)

    def showSalesByDay(self):
        df = self.statistic.getSalesByDayofweek()
        self.showTable(df)
        self.chartHandle.drawSalesByDay(df, self.ui.verticalLayout)

    def showTotalSales(self):
        df = self.statistic.getTotalSalesPerYear()
        self.showTable(df)
        self.chartHandle.drawTotalSalesPerYear(df, self.ui.verticalLayout)

    def showPreserved_duplicate_structure(self):
        df = self.statistic.getPreserved_duplicate_structure()
        self.showTable(df)
        self.chartHandle.drawPreserved_duplicate_structure(df, self.ui.verticalLayout, lag=1)

    def showHeatmap(self):
        df = self.statistic.getCorrelationHeatmap()
        df_num = df.select_dtypes(include=["float64", "int64"])
        corr = df_num.corr()
        self.showTable(df)
        self.chartHandle.drawCorrelationHeatmap(corr, self.ui.verticalLayout)

    def loadStores(self):
        sql = "SELECT DISTINCT store_nbr FROM cleaned_train ORDER BY store_nbr;"
        df = self.db.queryDataset(sql)
        if df is not None:
            for s in df["store_nbr"].tolist():
                self.ui.comboBoxStoreP.addItem(str(s))
                self.ui.comboBoxStoreD.addItem(str(s))

    def loadFamilies(self):
        sql = "SELECT DISTINCT family FROM cleaned_train ORDER BY family;"
        df = self.db.queryDataset(sql)
        self.ui.comboBoxFamily.clear()
        if df is not None:
            for s in df["family"].tolist():
                self.ui.comboBoxFamily.addItem(str(s))

    def predict_one_product(self):
        try:
            date_str = self.ui.dateEditDateP.date().toString("yyyy-MM-dd")
            store = self.ui.comboBoxStoreP.currentText().strip()
            if not store:
                raise ValueError("Vui lòng chọn cửa hàng.")
            store_nbr = int(store)
            family = self.ui.comboBoxFamily.currentText().strip()
            if not family:
                raise ValueError("Vui lòng chọn nhóm sản phẩm.")
            family = family.upper()
            onpromo_text = self.ui.lineEditOnpromotion.text().strip()
            onpromo = int(onpromo_text) if onpromo_text else 0
            print("=== INPUT DEBUG ===")
            print("date_str:", date_str)
            print("store_nbr:", store_nbr)
            print("family:", family)
            print("onpromotion:", onpromo)
            print("===================")
            sales = predict_any_date(
                date_str=date_str,
                store_nbr=store_nbr,
                family=family,
                onpromotion=onpromo
            )
            self.ui.lineEditSales.setText(f"{sales:,.2f}")
        except ValueError as ve:
            QMessageBox.warning(self, "Lỗi nhập liệu", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Lỗi hệ thống", f"Dự đoán thất bại:\n{e}")

    def predict_by_day(self):
        try:
            date_str = self.ui.dateEditDateP.date().toString("yyyy-MM-dd")
            store = self.ui.comboBoxStoreP.currentText().strip()
            if not date_str:
                raise ValueError("Vui lòng nhập ngày.")
            try:
                store_nbr = int(store)
            except:
                raise ValueError("Cửa hàng phải là số (1-54).")
            if not (1 <= store_nbr <= 54):
                raise ValueError("Cửa hàng phải từ 1 đến 54.")

            df = predict_for_store_date(date_str, store_nbr).head(5)

            self.ui.tableWidgetDate.setRowCount(0)
            self.ui.tableWidgetDate.setRowCount(len(df))
            self.ui.tableWidgetDate.setColumnCount(2)
            self.ui.tableWidgetDate.setHorizontalHeaderLabels(['Family', 'Sales'])

            for i, row in df.iterrows():
                self.ui.tableWidgetDate.setItem(i, 0, QTableWidgetItem(row['FAMILY']))
                self.ui.tableWidgetDate.setItem(i, 1, QTableWidgetItem(f"{row['SALES']:,.2f}"))
            self.ui.tableWidgetDate.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))

    def goBack(self):
        try:
            self.close()
            if self.parent_window is not None:
                self.parent_window.show()
        except Exception as e:
            print("BACK ERROR:", e)

