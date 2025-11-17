from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QSizePolicy
import seaborn as sns


class ChartHandle:
    def __init__(self):
        self.canvas = None
        self.toolbar = None

    def clearLayout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.canvas = None
        self.toolbar = None

    def drawHighestLowest(self, df, layout):
        self.clearLayout(layout)
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        ax.scatter(df['Highest_Sales_Date'], df['Highest_Sales'], color='green', label='Highest Sales')
        ax.scatter(df['Lowest_Sales_Date'], df['Lowest_Sales'], color='red', label='Lowest Sales')
        ax.set_title("Dates With Highest And Lowest Sales")
        ax.set_xlabel("Date")
        ax.set_ylabel("Sales")
        ax.legend()
        fig.subplots_adjust(bottom=0.25)
        self.canvas = Canvas(fig)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.canvas.updateGeometry()
        self.toolbar = NavigationToolbar(self.canvas, layout.parentWidget())
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    def drawEarthquakeTrend(self, before_df, after_df, layout):
        self.clearLayout(layout)
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(before_df["date"], before_df["sales"], color="purple", label="Before Earthquake")
        ax.plot(after_df["date"], after_df["sales"], color="orange", label="After Earthquake")
        ax.set_title("Sales Trend Before & After Earthquake")
        ax.set_xlabel("Date")
        ax.set_ylabel("Sales")
        ax.legend()
        fig.tight_layout()
        self.canvas = Canvas(fig)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.canvas.updateGeometry()
        self.toolbar = NavigationToolbar(self.canvas, layout.parentWidget())
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    def drawHolidaySales(self, df, layout):
        self.clearLayout(layout)
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        store_types = df["store_type"].unique()
        holiday_groups = df["holiday_status"].unique()
        bar_width = 0.35
        x = range(len(store_types))

        for i, h in enumerate(holiday_groups):
            values = []
            for st in store_types:
                tmp = df[(df["store_type"] == st) & (df["holiday_status"] == h)]
                if len(tmp) > 0:
                    values.append(tmp["avg_sales"].iloc[0])
                else:
                    values.append(0)

            ax.bar(
                [p + i * bar_width for p in x],
                values,
                bar_width,
                label=h
            )

        ax.set_xticks([p + bar_width / 2 for p in x])
        ax.set_xticklabels(store_types)
        ax.set_title("Sales On Holidays Vs Non-holidays For Each Store Type")
        ax.set_xlabel("Store Type")
        ax.set_ylabel("Average Sales")
        ax.legend(title="Holiday Type")
        fig.tight_layout()
        self.canvas = Canvas(fig)
        self.toolbar = NavigationToolbar(self.canvas, layout.parentWidget())
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.canvas.draw()

    def drawSalesByDay(self, df, layout):
        self.clearLayout(layout)
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(df["dayname"], df["avg_sales"])
        ax.set_title("Sales By Day Of Week")
        ax.set_xlabel("Day")
        ax.set_ylabel("Avg Sales")
        fig.tight_layout()
        self.canvas = Canvas(fig)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.canvas.updateGeometry()
        self.toolbar = NavigationToolbar(self.canvas, layout.parentWidget())
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    def drawTotalSalesPerYear(self, df, layout):
        self.clearLayout(layout)
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(df['year'], df['total_sales'])
        ax.set_title("Total Sales Per Year")
        ax.set_xlabel("Year")
        ax.set_ylabel("Total Sales")
        fig.tight_layout()
        self.canvas = Canvas(fig)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.canvas.updateGeometry()
        self.toolbar = NavigationToolbar(self.canvas, layout.parentWidget())
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    def drawPreserved_duplicate_structure(self, df, layout, lag=1):
        self.clearLayout(layout)
        # tạo figure
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.scatter(df['transactions'][:-lag], df['transactions'][lag:], s=10)
        ax.set_title(f"Preserved_duplicate_structure (lag={lag})")
        ax.set_xlabel("y(t)")
        ax.set_ylabel(f"y(t+{lag})")
        fig.tight_layout()
        canvas = Canvas(fig)
        toolbar = NavigationToolbar(canvas, layout.parentWidget())
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        canvas.draw()

    def drawCorrelationHeatmap(self, corr, layout):
        self.clearLayout(layout)
        fig = Figure(figsize=(10, 8), dpi=100)
        ax = fig.add_subplot(111)
        import seaborn as sns
        sns.heatmap(
            corr,
            ax=ax,
            cmap='coolwarm',
            annot=True,
            fmt='.2f',
            square=True,
            linewidths=0.5,
            cbar_kws={'shrink': 0.8},
            vmin=-1,
            vmax=1
        )
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
        fig.tight_layout(pad=2.0)
        self.canvas = Canvas(fig)
        self.toolbar = NavigationToolbar(self.canvas, layout.parentWidget())
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.canvas.draw()
