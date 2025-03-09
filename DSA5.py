import tkinter as tk
from tkinter import messagebox
import time
import random

class DynamicArray:
    def __init__(self, capacity=2):
        self.capacity = capacity
        self.count = 0
        self.array = [None] * capacity

    def append(self, item):
        if self.count == self.capacity:
            self.resize(2 * self.capacity)
        self.array[self.count] = item
        self.count += 1

    def resize(self, new_capacity):
        new_array = [None] * new_capacity
        for i in range(self.count):
            new_array[i] = self.array[i]
        self.array = new_array
        self.capacity = new_capacity

    def __iter__(self):
        for i in range(self.count):
            yield self.array[i]

    def __getitem__(self, index):
        if index < 0 or index >= self.count:
            raise IndexError("Index out of range")
        return self.array[index]

    def __len__(self):
        return self.count

class Trade:
    def __init__(self, timestamp, symbol, price, volume):
        self.timestamp = timestamp
        self.symbol = symbol
        self.price = price
        self.volume = volume

    def performance_metric(self):
        return self.price * self.volume

    def __str__(self):
        return f"Trade(Symbol: {self.symbol}, Price: {self.price:.2f}, Volume: {self.volume}, Time: {self.timestamp:.2f})"

class TransactionTracker:
    def __init__(self):
        self.trades = DynamicArray()

    def add_trade(self, trade):
        self.trades.append(trade)

    def get_best_trade(self):
        best = None
        for trade in self.trades:
            if best is None or trade.performance_metric() > best.performance_metric():
                best = trade
        return best

    def get_worst_trade(self):
        worst = None
        for trade in self.trades:
            if worst is None or trade.performance_metric() < worst.performance_metric():
                worst = trade
        return worst

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

    def right_rotate(self, y):
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))
        return x

    def left_rotate(self, x):
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        return y

    def insert_node(self, node, key, trade):
        if node is None:
            return AVLNode(key, trade)
        if key < node.key:
            node.left = self.insert_node(node.left, key, trade)
        else:
            node.right = self.insert_node(node.right, key, trade)
        node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
        balance = self.get_balance(node)
        if balance > 1 and key < node.left.key:
            return self.right_rotate(node)
        if balance < -1 and key > node.right.key:
            return self.left_rotate(node)
        if balance > 1 and key > node.left.key:
            node.left = self.left_rotate(node.left)
            return self.right_rotate(node)
        if balance < -1 and key < node.right.key:
            node.right = self.right_rotate(node.right)
            return self.left_rotate(node)
        return node

    def add_trade(self, trade):
        self.root = self.insert_node(self.root, trade.timestamp, trade)

    def inorder_traversal(self, node, result):
        if node:
            self.inorder_traversal(node.left, result)
            result.append(node.trade)
            self.inorder_traversal(node.right, result)

    def get_inorder(self):
        result = DynamicArray()
        self.inorder_traversal(self.root, result)
        return result

def simulate_price_update(trade, max_fluctuation=0.05):
    factor = 1 + random.uniform(-max_fluctuation, max_fluctuation)
    return trade.price * factor

def update_all_trades():
    global all_trades, tracker, portfolio
    for trade in all_trades:
        new_price = simulate_price_update(trade)
        trade.price = new_price
    tracker = TransactionTracker()
    portfolio = PortfolioManager()
    for trade in all_trades:
        tracker.add_trade(trade)
        portfolio.add_trade(trade)
    update_display("Prices updated for all trades.")

tracker = TransactionTracker()
portfolio = PortfolioManager()
all_trades = DynamicArray()

root = tk.Tk()
root.title("Stock Market Trading Tracker")
root.geometry("600x500")
root.configure(bg="#f5f5f5")

input_frame = tk.Frame(root, bg="#fff", bd=1, relief=tk.SOLID, padx=10, pady=10)
input_frame.pack(pady=20, padx=20, fill=tk.X)

output_frame = tk.Frame(root, bg="#fafafa", bd=1, relief=tk.SOLID, padx=10, pady=10)
output_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

tk.Label(input_frame, text="Stock Symbol:", font=("Arial", 10), bg="#fff").grid(row=0, column=0, sticky="w")
symbol_entry = tk.Entry(input_frame, font=("Arial", 10))
symbol_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Price:", font=("Arial", 10), bg="#fff").grid(row=1, column=0, sticky="w")
price_entry = tk.Entry(input_frame, font=("Arial", 10))
price_entry.grid(row=1, column=1, padx=5, pady=5)
price_entry.insert(0, "100")

tk.Label(input_frame, text="Volume:", font=("Arial", 10), bg="#fff").grid(row=2, column=0, sticky="w")
volume_entry = tk.Entry(input_frame, font=("Arial", 10))
volume_entry.grid(row=2, column=1, padx=5, pady=5)
volume_entry.insert(0, "10")

output_text = tk.Text(output_frame, wrap=tk.WORD, font=("Arial", 10))
output_text.pack(fill=tk.BOTH, expand=True)

def update_display(message=""):
    output_text.delete(1.0, tk.END)
    if message:
        output_text.insert(tk.END, message + "\n\n")
    best = tracker.get_best_trade()
    worst = tracker.get_worst_trade()
    if best:
        output_text.insert(tk.END, f"Best Trade: {best.symbol} | Profit: {best.performance_metric():.2f}\n")
    else:
        output_text.insert(tk.END, "Best Trade: N/A\n")
    if worst:
        output_text.insert(tk.END, f"Worst Trade: {worst.symbol} | Profit: {worst.performance_metric():.2f}\n")
    else:
        output_text.insert(tk.END, "Worst Trade: N/A\n")
    output_text.insert(tk.END, "\nPortfolio (Inorder Traversal):\n")
    for trade in portfolio.get_inorder():
        output_text.insert(tk.END, str(trade) + " | Performance: " + f"{trade.performance_metric():.2f}\n")

def add_trade():
    symbol = symbol_entry.get().strip()
    if not symbol:
        messagebox.showerror("Input Error", "Please enter a stock symbol.")
        return
    try:
        price = float(price_entry.get())
        volume = int(volume_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "Price must be a number and volume must be an integer.")
        return
    timestamp = time.time()
    trade = Trade(timestamp, symbol, price, volume)
    tracker.add_trade(trade)
    portfolio.add_trade(trade)
    all_trades.append(trade)
    symbol_entry.delete(0, tk.END)
    update_display("Trade added: " + str(trade))

def update_prices():
    update_all_trades()

def view_all_trades():
    update_display("Viewing all trades:")

button_frame = tk.Frame(input_frame, bg="#fff")
button_frame.grid(row=3, column=0, columnspan=2, pady=10)

add_button = tk.Button(button_frame, text="Add Trade", bg="#4CAF50", fg="#fff", padx=10, command=add_trade)
add_button.pack(side=tk.LEFT, padx=5)

update_button = tk.Button(button_frame, text="Update Prices", bg="#FF9800", fg="#fff", padx=10, command=update_prices)
update_button.pack(side=tk.LEFT, padx=5)

view_button = tk.Button(button_frame, text="View All Trades", bg="#2196F3", fg="#fff", padx=10, command=view_all_trades)
view_button.pack(side=tk.LEFT, padx=5)

root.mainloop()
