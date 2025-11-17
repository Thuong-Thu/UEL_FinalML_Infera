import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd
from Final_HocMay.connector.connector import Connector
pd.set_option('display.float_format', '{:,.0f}'.format)

class Statistic:
    def __init__(self):
        self.db = Connector(database="data")
        self.db.connect()
    def getHighestAndLowestSalesByYear(self):
        sql = """
            SELECT 
                Year,
                MAX(CASE WHEN rn_max = 1 THEN `date` END) AS Highest_Sales_Date,
                MAX(CASE WHEN rn_max = 1 THEN sales END) AS Highest_Sales,
                MAX(CASE WHEN rn_min = 1 THEN `date` END) AS Lowest_Sales_Date,
                MAX(CASE WHEN rn_min = 1 THEN sales END) AS Lowest_Sales
            FROM (
                SELECT 
                    YEAR(`date`) AS Year,
                    `date`,
                    sales,
                    ROW_NUMBER() OVER (PARTITION BY YEAR(`date`) ORDER BY sales DESC, `date` DESC) AS rn_max,
                    ROW_NUMBER() OVER (PARTITION BY YEAR(`date`) ORDER BY sales ASC,  `date` ASC ) AS rn_min
                FROM data.train
                WHERE sales > 0
            ) ranked
            GROUP BY Year
            ORDER BY Year;"""
        df = self.db.queryDataset(sql)
        df['Highest_Sales'] = df['Highest_Sales'].apply(lambda x: f"{x:,.0f}")
        df['Lowest_Sales'] = df['Lowest_Sales'].apply(lambda x: f"{x:,.3f}")
        return df
    def showHighestAndLowestSalesByYear(self):
        df=self.getHighestAndLowestSalesByYear()
        plt.figure(figsize=(12, 6))
        plt.scatter(df['Highest_Sales_Date'], df['Highest_Sales'], color='green', label='Highest Sales',marker='o')
        plt.scatter(df['Lowest_Sales_Date'], df['Lowest_Sales'], color='red', label='Lowest Sales',marker='o')
        plt.xlabel('Date')
        plt.ylabel('Sales')
        plt.legend()
        plt.title('Dates With The Highest And Lowest Sales For Each Year')
        plt.show()

    def getSalesTrendBeforeAfterEarthquake(self):
        sql = """
        SELECT 
            date,
            sales
        FROM data.train
        WHERE sales > 0
        ORDER BY date;
        """

        df = self.db.queryDataset(sql)
        df["date"] = pd.to_datetime(df["date"])
        earthquake_date = pd.to_datetime("2016-04-16")
        return df, earthquake_date

    def showSalesTrendBeforeAfterEarthquake(self):
        df, earthquake_date = self.getSalesTrendBeforeAfterEarthquake()

        before_df = df[df["date"] < earthquake_date]
        after_df = df[df["date"] >= earthquake_date]
        plt.figure(figsize=(10, 6))
        plt.plot(before_df["date"], before_df["sales"], color="purple", label="Before Earthquake")
        plt.plot(after_df["date"], after_df["sales"], color="orange", label="After Earthquake")
        plt.xlabel('Date')
        plt.ylabel('Sales')
        plt.title('Sales Trend Before and After the Earthquake')
        plt.legend()
        plt.show()

    def getSalesHolidayByStoretype(self):
        sql = """SELECT 
                    s.type AS store_type,
                    CASE WHEN h.hdate IS NULL THEN 'No holiday' ELSE 'Holiday' END AS holiday_status,
                    AVG(t.sales) AS avg_sales
                FROM data.train t
                JOIN data.stores s ON t.store_nbr = s.store_nbr
                LEFT JOIN (
                    SELECT STR_TO_DATE(date, '%c/%e/%Y') AS hdate
                    FROM data.holidays_events
                    WHERE type = 'Holiday' AND transferred = 'FALSE'
                ) h ON t.date = h.hdate
                GROUP BY s.type, holiday_status
                ORDER BY s.type, holiday_status;"""
        df = self.db.queryDataset(sql)
        return df

    def showSalesHolidayByStoretype(self):
        df = self.getSalesHolidayByStoretype()
        plt.figure(figsize=(10, 5))
        sns.barplot(
            x='store_type',
            y='avg_sales',
            hue='holiday_status',
            data=df,
            palette=['#4C72B0', '#55A868'],
            ci=None
        )
        plt.title('Sales On Holidays Vs Non-holidays For Each Store Type')
        plt.ylabel('Sales')
        plt.xlabel('Store Type')
        plt.legend(title='Holiday Type')
        plt.show()

    def getSalesByDayofweek(self):
        sql = """
          SELECT dayname,AVG(sales) AS avg_sales
        FROM (SELECT DATE_FORMAT(date, '%W') AS dayname, sales
        FROM data.train) t
        GROUP BY dayname
        ORDER BY CASE dayname
            WHEN 'Monday' THEN 1
            WHEN 'Tuesday' THEN 2
            WHEN 'Wednesday' THEN 3
            WHEN 'Thursday' THEN 4
            WHEN 'Friday' THEN 5
            WHEN 'Saturday' THEN 6
            WHEN 'Sunday' THEN 7
        END;
        """
        df = self.db.queryDataset(sql)
        return df

    def showSalesByDayOfWeek(self):
        df = self.getSalesByDayofweek()
        days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        plt.figure(figsize=(10, 5))
        sns.barplot(x='dayname',y='avg_sales',data=df,order=days,palette='pastel',ci=None)
        plt.title('Sales On Different Days Of The Week')
        plt.xlabel('Days Of The Week')
        plt.ylabel('Average Sales')
        plt.show()

    def getTotalSalesPerYear(self):
        sql = """
        SELECT 
            YEAR(date) AS year,
            SUM(sales) AS total_sales
        FROM data.train
        GROUP BY YEAR(date)
        ORDER BY YEAR(date);
        """
        df = self.db.queryDataset(sql)
        return df

    def showTotalSalesPerYear(self):
        df = self.getTotalSalesPerYear()
        plt.figure(figsize=(10, 5))
        plt.bar(df['year'], df['total_sales'], color='#4C72B0')
        plt.title('Sales Per Year', fontsize=14)
        plt.xlabel('Year', fontsize=14)
        plt.ylabel('Sales', fontsize=14)
        plt.show()

    def getPreserved_duplicate_structure(self):
        sql = """
            SELECT date, store_nbr, transactions
            FROM data.cleaned_train
            ORDER BY date, store_nbr;
        """
        df = self.db.queryDataset(sql)
        df['date'] = pd.to_datetime(df['date'])
        df = df.dropna(subset=['transactions'])
        sampled = (df.groupby(['date', 'store_nbr']).apply(
            lambda x: x.sample(min(5, len(x)), random_state=42)).reset_index(drop=True))
        return sampled

    def showPreserved_duplicate_structure(self, lag=1):
        df = self.getPreserved_duplicate_structure()

        plt.style.use('seaborn-v0_8-whitegrid')
        plt.figure(figsize=(10, 5))
        pd.plotting.lag_plot(df['transactions'], lag=lag)
        plt.title(f"Lag Plot (Preserved Duplicate Structure) — lag={lag}")
        plt.xlabel("y(t)")
        plt.ylabel(f"y(t + {lag})")
        plt.tight_layout()
        plt.show()

    def getCorrelationHeatmap(self):
        sql = """
            SELECT 
                sales, onpromotion, transactions, oil_price,
                is_weekend, month_sin, month_cos,
                dayofweek_sin, dayofweek_cos
            FROM data.cleaned_train
            WHERE sales IS NOT NULL
            ORDER BY RAND()
            LIMIT 30000
        """
        df = self.db.queryDataset(sql)
        if df is None or df.empty:
            return pd.DataFrame()
        return df.corr()
    def getData_train(self):
        sql = """
            SELECT date, store_nbr, family, sales
            FROM data.cleaned_train;
        """
        df = self.db.queryDataset(sql)
        return df
    def getData_Hodidayevent(self):
        sql = """
            SELECT date, store_nbr, family, sales
            FROM data.cleaned_train;
        """
        df = self.db.queryDataset(sql)
        return df
    def getStores(self):
        sql = """
            SELECT date, store_nbr, family, sales
            FROM data.cleaned_train;
        """
        df = self.db.queryDataset(sql)
        return df
    def showCorrelationHeatmap(self):
        df = self.getCorrelationHeatmap()
        df_num = df.select_dtypes(include=['float64', 'int64'])
        corr_matrix = df_num.corr()
        sns.heatmap(corr_matrix, annot=True)
        plt.title('Correlation Heatmap of Numerical Features')
        plt.show()

