# =========================
# 1. IMPORTS
# =========================

import sys
import json
import hashlib
import pandas as pd

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QLabel, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


# =========================
# 2. DATA HANDLING LOGIC
# =========================

class DataManager:
    def __init__(self):
        self.data = pd.DataFrame(
            columns=["Date", "Description", "Category", "Amount", "Hash"]
        )

    def load_files(self, paths):
        for path in paths:
            if path.endswith(".csv"):
                self._load_csv(path)
            elif path.endswith(".json"):
                self._load_json(path)
            elif path.endswith(".txt"):
                self._load_txt(path)

        self._deduplicate()

    def _load_csv(self, path):
        df = pd.read_csv(path)
        self._normalize(df)

    def _load_json(self, path):
        with open(path, "r") as f:
            raw = json.load(f)

        df = pd.DataFrame(raw).rename(columns={
            "date": "Date",
            "desc": "Description",
            "cat": "Category",
            "amt": "Amount"
        })
        self._normalize(df)

    def _load_txt(self, path):
        rows = []
        with open(path, "r") as f:
            for line in f:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) == 4:
                    rows.append({
                        "Date": parts[0],
                        "Description": parts[1],
                        "Amount": float(parts[2]),
                        "Category": parts[3]
                    })

        self._normalize(pd.DataFrame(rows))

    def _normalize(self, df):
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
        df["Category"] = df["Category"].fillna("Uncategorized")

        df["Hash"] = df.apply(
            lambda r: hashlib.md5(
                f"{r['Date']}{r['Description']}{r['Amount']}".encode()
            ).hexdigest(),
            axis=1
        )

        self.data = pd.concat([self.data, df], ignore_index=True)

    def _deduplicate(self):
        self.data = self.data.drop_duplicates(subset="Hash")

    def net_balance(self):
        return self.data["Amount"].sum()

    def expense_by_category(self):
        return (
            self.data[self.data["Amount"] < 0]
            .groupby("Category")["Amount"]
            .sum()
            .abs()
        )


# =========================
# 3. CHART WIDGET
# =========================

class ChartCanvas(FigureCanvas):
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        super().__init__(self.fig)


# =========================
# 4. MAIN APPLICATION UI
# =========================

class FinancialAnalyzer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Financial Analyzer")
        self.resize(1000, 700)

        self.manager = DataManager()

        # ----- Widgets -----
        self.upload_btn = QPushButton("Upload Financial Files")

        self.balance_label = QLabel("Net Balance: ₹0.00")
        self.balance_label.setAlignment(Qt.AlignCenter)
        self.balance_label.setStyleSheet(
            "font-size:18px; font-weight:bold"
        )

        self.chart = ChartCanvas()
        self.table = QTableWidget()

        # ----- Layout -----
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.upload_btn)
        self.layout.addWidget(self.balance_label)
        self.layout.addWidget(self.chart)
        self.layout.addWidget(self.table)

        # ----- Signal Connections -----
        self.upload_btn.clicked.connect(self.upload_files)

    # =========================
    # 5. FUNCTIONAL LOGIC
    # =========================

    def upload_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Financial Files",
            "",
            "Data Files (*.csv *.json *.txt)"
        )

        if paths:
            self.manager.load_files(paths)
            self.update_dashboard()

    def update_dashboard(self):
        # Net Balance
        balance = self.manager.net_balance()
        self.balance_label.setText(f"Net Balance: ₹{balance:,.2f}")

        # Expense Pie Chart
        self.chart.ax.clear()
        expenses = self.manager.expense_by_category()
        if not expenses.empty:
            self.chart.ax.pie(
                expenses,
                labels=expenses.index,
                autopct="%1.1f%%"
            )
            self.chart.ax.set_title("Expense Breakdown")
        self.chart.draw()

        # Transaction Table
        df = self.manager.data.drop(columns="Hash")
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels(df.columns)

        for row in range(len(df)):
            for col, value in enumerate(df.iloc[row]):
                self.table.setItem(
                    row, col,
                    QTableWidgetItem(str(value))
                )

        self.table.setSortingEnabled(True)


# =========================
# 6. APPLICATION ENTRY
# =========================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FinancialAnalyzer()
    window.show()
    sys.exit(app.exec_())
