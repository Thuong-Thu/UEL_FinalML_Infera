#python -m pip install mysql-connector-python
import mysql.connector
import traceback
import pandas as pd

class Connector:
    def __init__(self,server="localhost", port=3306, database="data", username="root", password="thuvt23406@"):
        self.server=server
        self.port=port
        self.database=database
        self.username=username
        self.password=password
    def connect(self):
        try:
            self.conn = mysql.connector.connect(
                host=self.server,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password,
            use_pure=True)
            return self.conn
        except:
            self.conn=None
            traceback.print_exc()
        return None

    def disConnect(self):
        if self.conn and self.conn.is_connected():
            self.conn.close()
            self.conn = None
    def email_exists(self, email: str) -> bool:
        self.connect()
        cursor = self.conn.cursor()
        sql = "SELECT 1 FROM users WHERE Email = %s LIMIT 1"
        cursor.execute(sql, (email,))
        row = cursor.fetchone()
        cursor.close()
        return row is not None

    # Đăng ký khách hàng mới
    def register_customer(self, username: str, email: str,
                          password_hash: str, confirm_hash: str = None) -> int:

        self.connect()
        if confirm_hash is None:
            confirm_hash = password_hash

        sql = """
            INSERT INTO users (UserName, Email, Password, ConfirmPassword)
            VALUES (%s, %s, %s, %s)
        """
        val = (username, email, password_hash, confirm_hash)
        cursor = self.conn.cursor()
        cursor.execute(sql, val)
        self.conn.commit()
        affected = cursor.rowcount
        cursor.close()
        return affected

    def email_exists(self, email: str) -> bool:
        self.connect()
        cursor = self.conn.cursor()
        sql = "SELECT 1 FROM users WHERE Email = %s LIMIT 1"
        cursor.execute(sql, (email,))
        row = cursor.fetchone()
        cursor.close()
        return row is not None

    def register_user(self, username, email, password, role):
        sql = """
            INSERT INTO users (UserName, Email, Password, Role)
            VALUES (%s, %s, %s, %s)
        """
        cursor = self.conn.cursor()
        cursor.execute(sql, (username, email, password, role))
        self.conn.commit()
        return cursor.rowcount

    def queryDataset(self, sql):
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            df = pd.DataFrame(cursor.fetchall())
            if not df.empty:
                df.columns = cursor.column_names
            return df
        except:
            traceback.print_exc()
        return None

