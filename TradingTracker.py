import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import time
from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates

class Trade:
    def __init__(self, timestamp, symbol, price, volume, original_price, trade_type):
        self.timestamp = timestamp
        self.symbol = symbol
        self.price = price
        self.volume = volume
        self.original_price = original_price
        self.trade_type = trade_type

    def performance_metric(self):
        return (self.price - self.original_price) * self.volume

    def reduce_volume(self, amount):
        self.volume -= amount
        if self.volume < 0:
            self.volume = 0

    def __str__(self):
        return (f"Trade(Symbol: {self.symbol}, Type: {self.trade_type}, Price: {self.price:.2f}, "
                f"Volume: {self.volume}, Orig.Price: {self.original_price:.2f}, Time: {self.timestamp:.2f})")

class Heap:
    def __init__(self, comparator):
        self.data = []
        self.comparator = comparator

    def push(self, item):
        self.data.append(item)
        self._sift_up(len(self.data) - 1)

    def pop(self):
        if not self.data:
            return None
        top_item = self.data[0]
        self.data[0] = self.data[-1]
        self.data.pop()
        self._sift_down(0)
        return top_item

    def peek(self):
        if not self.data:
            return None
        return self.data[0]

    def _sift_up(self, index):
        parent_index = (index - 1) // 2
        while index > 0 and self.comparator(self.data[index], self.data[parent_index]):
            self.data[index], self.data[parent_index] = self.data[parent_index], self.data[index]
            index = parent_index
            parent_index = (index - 1) // 2

    def _sift_down(self, index):
        total_items = len(self.data)
        while True:
            left_index = 2 * index + 1
            right_index = 2 * index + 2
            best_index = index
            if left_index < total_items and self.comparator(self.data[left_index], self.data[best_index]):
                best_index = left_index
            if right_index < total_items and self.comparator(self.data[right_index], self.data[best_index]):
                best_index = right_index
            if best_index == index:
                break
            self.data[index], self.data[best_index] = self.data[best_index], self.data[index]
            index = best_index

class TransactionTracker:
    def __init__(self):
        self.trades = []
        self.best_heap = Heap(lambda first_trade, second_trade: first_trade.performance_metric() > second_trade.performance_metric())
        self.worst_heap = Heap(lambda first_trade, second_trade: first_trade.performance_metric() < second_trade.performance_metric())

    def add_trade(self, trade):
        self.trades.append(trade)
        self.best_heap.push(trade)
        self.worst_heap.push(trade)

    def get_best_trade(self):
        return self.best_heap.peek()

    def get_worst_trade(self):
        return self.worst_heap.peek()

class AVLNode:
    def __init__(self, key, trade):
        self.key = key
        self.trade = trade
        self.height = 1
        self.left = None
        self.right = None

class PortfolioManager:
    def __init__(self):
        self.root = None

    def get_height(self, node):
        return node.height if node else 0

    def get_balance(self, node):
        return self.get_height(node.left) - self.get_height(node.right) if node else 0

    def right_rotate(self, node_y):
        node_x = node_y.left
        subtree_T2 = node_x.right
        node_x.right = node_y
        node_y.left = subtree_T2
        node_y.height = 1 + max(self.get_height(node_y.left), self.get_height(node_y.right))
        node_x.height = 1 + max(self.get_height(node_x.left), self.get_height(node_x.right))
        return node_x

    def left_rotate(self, node_x):
        node_y = node_x.right
        subtree_T2 = node_y.left
        node_y.left = node_x
        node_x.right = subtree_T2
        node_x.height = 1 + max(self.get_height(node_x.left), self.get_height(node_x.right))
        node_y.height = 1 + max(self.get_height(node_y.left), self.get_height(node_y.right))
        return node_y

    def insert_node(self, current_node, key, trade):
        if not current_node:
            return AVLNode(key, trade)
        if key < current_node.key:
            current_node.left = self.insert_node(current_node.left, key, trade)
        else:
            current_node.right = self.insert_node(current_node.right, key, trade)
        current_node.height = 1 + max(self.get_height(current_node.left), self.get_height(current_node.right))
        balance_factor = self.get_balance(current_node)
        if balance_factor > 1 and key < current_node.left.key:
            return self.right_rotate(current_node)
        if balance_factor < -1 and key > current_node.right.key:
            return self.left_rotate(current_node)
        if balance_factor > 1 and key > current_node.left.key:
            current_node.left = self.left_rotate(current_node.left)
            return self.right_rotate(current_node)
        if balance_factor < -1 and key < current_node.right.key:
            current_node.right = self.right_rotate(current_node.right)
            return self.left_rotate(current_node)
        return current_node

    def add_trade(self, trade):
        self.root = self.insert_node(self.root, trade.timestamp, trade)

    def inorder_traversal(self, node, result):
        if node:
            self.inorder_traversal(node.left, result)
            result.append(node.trade)
            self.inorder_traversal(node.right, result)

    def get_inorder(self):
        result = []
        self.inorder_traversal(self.root, result)
        return result

class TradingTracker(tk.Tk):
    CANDLE_PERIOD = 10

    def __init__(self):
        super().__init__()
        self.attributes("-fullscreen", True)
        self.transaction_tracker = TransactionTracker()
        self.portfolio_manager = PortfolioManager()
        self.all_trades = []
        self.random_generator = random.Random()
        self.wallet = 10000.0
        self.stock_history = {}
        self.current_symbol = None
        main_panel = tk.Frame(self, padx=10, pady=10)
        main_panel.pack(fill=tk.BOTH, expand=True)
        top_panel = tk.Frame(main_panel)
        top_panel.pack(side=tk.TOP, fill=tk.X)
        details_panel = tk.LabelFrame(top_panel, text="Trade Details", padx=5, pady=5)
        details_panel.pack(fill=tk.X, pady=(0, 5))
        tk.Label(details_panel, text="Stock Symbol:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.symbol_field = tk.Entry(details_panel)
        self.symbol_field.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        tk.Label(details_panel, text="Price:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.price_field = tk.Entry(details_panel)
        self.price_field.insert(0, "100")
        self.price_field.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        tk.Label(details_panel, text="Volume:").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.volume_field = tk.Entry(details_panel)
        self.volume_field.insert(0, "10")
        self.volume_field.grid(row=0, column=5, padx=5, pady=5, sticky="w")
        button_panel = tk.Frame(top_panel)
        button_panel.pack(fill=tk.X, pady=(5, 5))
        button_options = {'bd': 2, 'relief': 'groove', 'font': ("Helvetica", 10, "bold"), 'width': 16, 'padx': 5, 'pady': 5}
        self.add_button = tk.Button(button_panel, text="Add Trade", command=self.add_trade, bg="lightgreen", **button_options)
        self.sell_button = tk.Button(button_panel, text="Sell Stock", command=self.sell_trade, bg="tomato", **button_options)
        self.update_all_button = tk.Button(button_panel, text="Update All Prices", command=self.update_all_prices, bg="lightblue", **button_options)
        self.update_selected_button = tk.Button(button_panel, text="Update Selected Stock", command=self.update_selected_stock, bg="orange", **button_options)
        self.add_button.pack(side=tk.LEFT, expand=True, padx=15, pady=5)
        self.sell_button.pack(side=tk.LEFT, expand=True, padx=15, pady=5)
        self.update_all_button.pack(side=tk.LEFT, expand=True, padx=15, pady=5)
        self.update_selected_button.pack(side=tk.LEFT, expand=True, padx=15, pady=5)
        center_pane = ttk.PanedWindow(main_panel, orient=tk.HORIZONTAL)
        center_pane.pack(fill=tk.BOTH, expand=True)
        left_frame = tk.Frame(center_pane)
        center_pane.add(left_frame, weight=1)
        table_frame = tk.LabelFrame(left_frame, text="Trades", padx=5, pady=5)
        table_frame.pack(fill=tk.BOTH, expand=True)
        columns = ("Timestamp", "Symbol", "Type", "Price", "Volume", "Orig. Price", "Performance")
        self.trade_table = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        for column in columns:
            self.trade_table.heading(column, text=column)
            self.trade_table.column(column, anchor="center")
        self.trade_table.pack(fill=tk.BOTH, expand=True)
        vertical_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.trade_table.yview)
        self.trade_table.configure(yscrollcommand=vertical_scrollbar.set)
        vertical_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        right_frame = tk.Frame(center_pane)
        center_pane.add(right_frame, weight=1)
        stock_list_frame = tk.LabelFrame(right_frame, text="Stocks", padx=5, pady=5)
        stock_list_frame.pack(fill=tk.X)
        self.stock_listbox = tk.Listbox(stock_list_frame, height=4)
        self.stock_listbox.pack(fill=tk.X, padx=5, pady=5)
        self.stock_listbox.bind("<<ListboxSelect>>", self.on_stock_select)
        self.selected_stock_label = tk.Label(stock_list_frame, text="Selected Stock: None", font=("Helvetica", 10, "bold"))
        self.selected_stock_label.pack(pady=(0, 5))
        graph_frame = tk.LabelFrame(right_frame, text="Price vs Time", padx=5, pady=5)
        graph_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        self.figure = Figure(figsize=(4, 3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Stock Price vs Time")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Price")
        self.canvas = FigureCanvasTkAgg(self.figure, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        summary_panel = tk.Frame(main_panel)
        summary_panel.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        self.best_trade_label = tk.Label(summary_panel, text="Best Trade: N/A")
        self.worst_trade_label = tk.Label(summary_panel, text="Worst Trade: N/A")
        self.wallet_label = tk.Label(summary_panel, text="Wallet: $10000.00")
        self.best_trade_label.pack(side=tk.LEFT, padx=10)
        self.worst_trade_label.pack(side=tk.LEFT, padx=10)
        self.wallet_label.pack(side=tk.LEFT, padx=10)
        self.price_update_timer()
        self.update_summary()
        self.update_stock_list()

    def price_update_timer(self):
        self.update_all_prices()
        if self.current_symbol:
            self.plot_stock_history(self.current_symbol)
        self.after(5000, self.price_update_timer)

    def add_trade(self):
        symbol = self.symbol_field.get().strip()
        if not symbol:
            messagebox.showerror("Input Error", "Please enter a stock symbol.")
            return
        try:
            price = float(self.price_field.get())
            volume = int(self.volume_field.get())
        except ValueError:
            messagebox.showerror("Input Error", "Price must be a number and volume must be an integer.")
            return
        trade_timestamp = time.time()
        new_trade = Trade(trade_timestamp, symbol, price, volume, price, "Buy")
        self.transaction_tracker.add_trade(new_trade)
        self.portfolio_manager.add_trade(new_trade)
        self.all_trades.append(new_trade)
        cost_of_purchase = price * volume
        self.wallet -= cost_of_purchase
        self.update_stock_history(symbol, price, trade_timestamp)
        self.symbol_field.delete(0, tk.END)
        self.refresh_table()
        self.update_summary()
        self.update_stock_list()

    def sell_trade(self):
        symbol = simpledialog.askstring("Sell Stock", "Enter the stock symbol to sell:")
        if symbol is None or not symbol.strip():
            return
        symbol = symbol.strip()
        buy_trade = None
        for trade in self.all_trades:
            if trade.symbol.lower() == symbol.lower() and trade.trade_type == "Buy" and trade.volume > 0:
                buy_trade = trade
                break
        if buy_trade is None:
            messagebox.showerror("Sell Error", f"No available buy trade found for symbol: {symbol}")
            return
        volume_string = simpledialog.askstring("Sell Stock", f"Enter number of shares to sell (Available: {buy_trade.volume}):")
        if volume_string is None or not volume_string.strip():
            return
        try:
            sell_volume = int(volume_string)
        except ValueError:
            messagebox.showerror("Input Error", "Volume must be an integer.")
            return
        if sell_volume <= 0 or sell_volume > buy_trade.volume:
            messagebox.showerror("Sell Error", f"Invalid sell volume. Must be between 1 and {buy_trade.volume}")
            return
        current_price = buy_trade.price
        trade_timestamp = time.time()
        sell_trade = Trade(trade_timestamp, symbol, current_price, sell_volume, buy_trade.original_price, "Sell")
        self.transaction_tracker.add_trade(sell_trade)
        self.portfolio_manager.add_trade(sell_trade)
        self.all_trades.append(sell_trade)
        buy_trade.reduce_volume(sell_volume)
        revenue = current_price * sell_volume
        self.wallet += revenue
        self.update_stock_history(symbol, current_price, trade_timestamp)
        self.refresh_table()
        self.update_summary()
        self.update_stock_list()

    def simulate_price_update(self, trade, max_fluctuation):
        fluctuation_factor = 1 + (self.random_generator.random() * 2 * max_fluctuation - max_fluctuation)
        return trade.price * fluctuation_factor

    def update_all_prices(self):
        for trade in self.all_trades:
            if trade.trade_type == "Buy" and trade.volume > 0:
                new_price = self.simulate_price_update(trade, 0.05)
                trade.price = new_price
        self.transaction_tracker = TransactionTracker()
        self.portfolio_manager = PortfolioManager()
        latest_prices = {}
        for trade in self.all_trades:
            self.transaction_tracker.add_trade(trade)
            self.portfolio_manager.add_trade(trade)
            if trade.trade_type == "Buy" and trade.volume > 0:
                latest_prices[trade.symbol] = trade.price
        current_time = time.time()
        for symbol, price in latest_prices.items():
            self.update_stock_history(symbol, price, current_time)
        self.refresh_table()
        self.update_summary()
        self.update_stock_list()

    def update_selected_stock(self):
        selected_items = self.trade_table.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a trade to update.")
            return
        selected_item = selected_items[0]
        table_children = self.trade_table.get_children()
        selected_index = table_children.index(selected_item)
        selected_trade = self.all_trades[selected_index]
        if selected_trade.trade_type != "Buy" or selected_trade.volume <= 0:
            messagebox.showerror("Update Error", "Selected trade is not an active buy trade.")
            return
        new_price = self.simulate_price_update(selected_trade, 0.05)
        selected_trade.price = new_price
        current_time = time.time()
        self.update_stock_history(selected_trade.symbol, new_price, current_time)
        self.transaction_tracker = TransactionTracker()
        self.portfolio_manager = PortfolioManager()
        for trade in self.all_trades:
            self.transaction_tracker.add_trade(trade)
            self.portfolio_manager.add_trade(trade)
        self.refresh_table()
        self.update_summary()
        self.update_stock_list()

    def update_summary(self):
        best_trade = self.transaction_tracker.get_best_trade()
        worst_trade = self.transaction_tracker.get_worst_trade()
        if best_trade:
            self.best_trade_label.config(text=f"Best Trade: {best_trade.symbol} | Profit: {best_trade.performance_metric():.2f}")
        else:
            self.best_trade_label.config(text="Best Trade: N/A")
        if worst_trade:
            self.worst_trade_label.config(text=f"Worst Trade: {worst_trade.symbol} | Profit: {worst_trade.performance_metric():.2f}")
        else:
            self.worst_trade_label.config(text="Worst Trade: N/A")
        self.wallet_label.config(text=f"Wallet: ${self.wallet:.2f}")

    def refresh_table(self):
        for row in self.trade_table.get_children():
            self.trade_table.delete(row)
        for trade in self.all_trades:
            self.trade_table.insert("", "end", values=(
                f"{trade.timestamp:.2f}",
                trade.symbol,
                trade.trade_type,
                f"{trade.price:.2f}",
                trade.volume,
                f"{trade.original_price:.2f}",
                f"{trade.performance_metric():.2f}"
            ))

    def update_stock_history(self, symbol, new_price, timestamp):
        period = self.CANDLE_PERIOD
        if symbol not in self.stock_history:
            self.stock_history[symbol] = [{
                "start": timestamp,
                "open": new_price,
                "high": new_price,
                "low": new_price,
                "close": new_price
            }]
        else:
            candles = self.stock_history[symbol]
            latest_candle = candles[-1]
            if timestamp < latest_candle["start"] + period:
                latest_candle["high"] = max(latest_candle["high"], new_price)
                latest_candle["low"] = min(latest_candle["low"], new_price)
                latest_candle["close"] = new_price
            else:
                candles.append({
                    "start": timestamp,
                    "open": new_price,
                    "high": new_price,
                    "low": new_price,
                    "close": new_price
                })
        if len(self.stock_history[symbol]) > 50:
            self.stock_history[symbol] = self.stock_history[symbol][-50:]

    def update_stock_list(self):
        unique_symbols = sorted({trade.symbol for trade in self.all_trades})
        self.stock_listbox.delete(0, tk.END)
        for symbol in unique_symbols:
            self.stock_listbox.insert(tk.END, symbol)

    def on_stock_select(self, event):
        selected_indices = event.widget.curselection()
        if selected_indices:
            selected_index = selected_indices[0]
            symbol = event.widget.get(selected_index)
            self.current_symbol = symbol
            self.plot_stock_history(symbol)
            if symbol in self.stock_history and self.stock_history[symbol]:
                latest_price = self.stock_history[symbol][-1]["close"]
                self.selected_stock_label.config(text=f"Selected Stock: {symbol} | Price: {latest_price:.2f}")
            else:
                self.selected_stock_label.config(text=f"Selected Stock: {symbol} | Price: N/A")

    def plot_stock_history(self, symbol):
        self.ax.clear()
        self.ax.set_title(f"{symbol} Price vs Time")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Price")
        if symbol not in self.stock_history or len(self.stock_history[symbol]) == 0:
            self.canvas.draw()
            return
        times = []
        prices = []
        for candle in self.stock_history[symbol]:
            time_point = datetime.fromtimestamp(candle["start"])
            times.append(time_point)
            prices.append(candle["close"])
        self.ax.plot(times, prices, marker='o', linestyle='-')
        self.figure.autofmt_xdate()
        self.canvas.draw()

if __name__ == "__main__":
    app = TradingTracker()
    app.mainloop()
