"""
Simple Tkinter GUI for XAUUSD Analysis System
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from src.data_fetcher import DataFetcher
from src.technical_indicators import TechnicalIndicators
from src.visualizer import Visualizer
from src.candlestick_analysis import CandlestickAnalyzer


class XAUUSDApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("XAUUSD Analysis GUI")
        self.geometry("600x400")

        # configuration placeholders
        self.config = {
            'fetcher': {'symbol': 'XAUUSD=X', 'interval': '1d'},
            'visualization': {'theme': 'dark', 'plot_dir': 'results/plots'}
        }

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill='both', expand=True)

        # symbol
        ttk.Label(frame, text="Symbol:").grid(row=0, column=0, sticky='w')
        self.symbol_var = tk.StringVar(value="XAUUSD=X")
        ttk.Entry(frame, textvariable=self.symbol_var, width=20).grid(row=0, column=1)

        # start date
        ttk.Label(frame, text="Start Date (YYYY-MM-DD):").grid(row=1, column=0, sticky='w')
        self.start_var = tk.StringVar(value=(datetime.now().date().isoformat()))
        ttk.Entry(frame, textvariable=self.start_var, width=20).grid(row=1, column=1)

        # end date
        ttk.Label(frame, text="End Date (YYYY-MM-DD):").grid(row=2, column=0, sticky='w')
        self.end_var = tk.StringVar(value=(datetime.now().date().isoformat()))
        ttk.Entry(frame, textvariable=self.end_var, width=20).grid(row=2, column=1)

        # buttons
        ttk.Button(frame, text="Fetch & Analyze", command=self.fetch_and_analyze).grid(row=3, column=0, columnspan=2, pady=10)

        # log area
        self.log = tk.Text(frame, height=10)
        self.log.grid(row=4, column=0, columnspan=2, sticky='nsew')
        frame.rowconfigure(4, weight=1)
        frame.columnconfigure(1, weight=1)

    def log_message(self, msg: str):
        self.log.insert('end', msg + "\n")
        self.log.see('end')

    def fetch_and_analyze(self):
        symbol = self.symbol_var.get().strip()
        start = self.start_var.get().strip()
        end = self.end_var.get().strip()
        try:
            self.log_message(f"Fetching data for {symbol} from {start} to {end}...")
            fetcher = DataFetcher(self.config['fetcher'])
            data = fetcher.fetch(symbol, start=start, end=end)
            self.log_message("Data fetched successfully")

            self.log_message("Calculating technical indicators...")
            ti = TechnicalIndicators()
            data = ti.apply_all(data)
            self.log_message("Indicators calculated")

            self.log_message("Analyzing candlestick patterns...")
            ca = CandlestickAnalyzer()
            patterns = ca.detect_patterns(data)
            self.log_message(f"Patterns found: {patterns}")

            self.log_message("Generating visualization...")
            viz = Visualizer(self.config)
            viz.plot_candlestick_with_indicators(data)
            self.log_message("Chart created and saved")

            messagebox.showinfo("Success", "Analysis complete and chart saved!")
        except Exception as e:
            self.log_message(f"Error: {e}")
            messagebox.showerror("Error", str(e))


if __name__ == '__main__':
    app = XAUUSDApp()
    app.mainloop()
