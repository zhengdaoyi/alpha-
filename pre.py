import tkinter as tk
import requests
import time

SYMBOL = "RAVEUSDT"   # 改成你想看的合约，比如 RAVEUSDT
REFRESH_MS = 3000    # 3秒刷新一次

class PriceWidget:
    def __init__(self, root):
        self.root = root
        self.root.title("Binance Futures Widget")
        self.root.geometry("260x120+1600+100")   # 宽x高+X+Y，可自己改位置
        self.root.overrideredirect(True)         # 去掉边框
        self.root.attributes("-topmost", True)   # 置顶
        self.root.configure(bg="#111111")

        self.symbol_label = tk.Label(
            root, text=SYMBOL, font=("Arial", 16, "bold"),
            fg="white", bg="#111111"
        )
        self.symbol_label.pack(pady=(10, 2))

        self.price_label = tk.Label(
            root, text="--", font=("Arial", 22, "bold"),
            fg="#00ff99", bg="#111111"
        )
        self.price_label.pack()

        self.change_label = tk.Label(
            root, text="24h: --", font=("Arial", 12),
            fg="white", bg="#111111"
        )
        self.change_label.pack(pady=(2, 2))

        self.time_label = tk.Label(
            root, text="更新时间: --", font=("Arial", 9),
            fg="#aaaaaa", bg="#111111"
        )
        self.time_label.pack()

        self.root.bind("<ButtonPress-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.on_move)
        self.root.bind("<Button-3>", lambda e: self.root.destroy())

        self.offset_x = 0
        self.offset_y = 0

        self.update_price()

    def start_move(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def on_move(self, event):
        x = self.root.winfo_x() + event.x - self.offset_x
        y = self.root.winfo_y() + event.y - self.offset_y
        self.root.geometry(f"+{x}+{y}")

    def fetch_data(self):
        price_url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={SYMBOL}"
        stat_url = f"https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={SYMBOL}"

        price_data = requests.get(price_url, timeout=5).json()
        stat_data = requests.get(stat_url, timeout=5).json()

        price = float(price_data["price"])
        change_percent = float(stat_data["priceChangePercent"])
        return price, change_percent

    def update_price(self):
        try:
            price, change_percent = self.fetch_data()
            self.price_label.config(text=f"{price:,.4f}")

            if change_percent >= 0:
                self.change_label.config(
                    text=f"24h: +{change_percent:.2f}%",
                    fg="#00ff99"
                )
                self.price_label.config(fg="#00ff99")
            else:
                self.change_label.config(
                    text=f"24h: {change_percent:.2f}%",
                    fg="#ff5555"
                )
                self.price_label.config(fg="#ff5555")

            now_str = time.strftime("%H:%M:%S")
            self.time_label.config(text=f"更新时间: {now_str}")
        except Exception as e:
            self.price_label.config(text="网络错误")
            self.change_label.config(text=str(e)[:30], fg="#ffcc00")

        self.root.after(REFRESH_MS, self.update_price)

if __name__ == "__main__":
    root = tk.Tk()
    app = PriceWidget(root)
    root.mainloop()