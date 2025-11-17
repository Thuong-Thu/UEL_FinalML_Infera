from Final_HocMay.Models.Statistic import Statistic
from Final_HocMay.connector.connector import Connector

def main():
    connector = Connector(
        server="localhost",
        port=3306,
        database="data",
        username="root",
        password="thuvt23406@"
    )
    connector.connect()
    stat = Statistic()
    stat.db = connector

    print("\n=== 1. Highest & Lowest Sales by Year ===")
    print(stat.getHighestAndLowestSalesByYear())
    stat.showHighestAndLowestSalesByYear()

    print("\n=== 2. Sales Trend Before & After Earthquake ===")
    df, eq = stat.getSalesTrendBeforeAfterEarthquake()
    print(df.head())
    stat.showSalesTrendBeforeAfterEarthquake()

    print("\n=== 3. Sales on Holidays vs Non-Holidays ===")
    print(stat.getSalesHolidayByStoretype())
    stat.showSalesHolidayByStoretype()

    print("\n=== 4. Sales by Day of Week ===")
    print(stat.getSalesByDayofweek())
    stat.showSalesByDayOfWeek()

    print("\n=== 5. Total Sales per Year ===")
    print(stat.getTotalSalesPerYear())
    stat.showTotalSalesPerYear()

    print("\n=== 6. Lag Plot ===")
    stat.showPreserved_duplicate_structure(lag=1)

    print("\n=== 7. Correlation Heatmap ===")
    stat.showCorrelationHeatmap()

if __name__ == "__main__":
    main()
