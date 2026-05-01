import tkinter as tk
import requests
import time

# 这里改成你想看的三个币
SYMBOLS = ["PIEVERSEUSDT", "币安人生USDT", "GENIUSUSDT"]

REFRESH_MS = 3000
BG_COLOR = "#111111"
FG_COLOR = "white"
UP_COLOR = "#00ff99"
DOWN_COLOR = "#ff5555"
SUB_COLOR = "#aaaaaa"
WARN_COLOR = "#ffcc00"

class SymbolPanel:
    def __init__(self, parent, symbol):
        self.symbol = symbol

        self.frame = tk.Frame(parent, bg=BG_COLOR, bd=0, highlightthickness=0)
        self.frame.pack(fill="x", padx=8, pady=3)

        self.symbol_label = tk.Label(
            self.frame, text=symbol, font=("Arial", 13, "bold"),
            fg=FG_COLOR, bg=BG_COLOR, anchor="w"
        )
        self.symbol_label.pack(anchor="w")

        self.price_label = tk.Label(
            self.frame, text="--", font=("Arial", 17, "bold"),
            fg=UP_COLOR, bg=BG_COLOR, anchor="w"
        )
        self.price_label.pack(anchor="w")

        self.info_label = tk.Label(
            self.frame, text="24h: --    资金费率: --",
            font=("Arial", 10), fg=FG_COLOR, bg=BG_COLOR, anchor="w"
        )
        self.info_label.pack(anchor="w")

        self.sep = tk.Frame(parent, height=1, bg="#222222")
        self.sep.pack(fill="x", padx=6, pady=1)

    def update_view(self, price, change_percent, funding_rate):
        if change_percent >= 0:
            price_color = UP_COLOR
            info_color = UP_COLOR
            change_text = f"+{change_percent:.2f}%"
        else:
            price_color = DOWN_COLOR
            info_color = DOWN_COLOR
            change_text = f"{change_percent:.2f}%"

        funding_text = f"{funding_rate * 100:.4f}%"

        self.price_label.config(text=f"{price:,.4f}", fg=price_color)
        self.info_label.config(
            text=f"24h: {change_text}    资金费率: {funding_text}",
            fg=info_color
        )

    def show_error(self, msg="网络错误"):
        self.price_label.config(text=msg, fg=WARN_COLOR)
        self.info_label.config(text="24h: --    资金费率: --", fg=WARN_COLOR)


class MultiPriceWidget:
    def __init__(self, root):
        self.root = root
        self.root.title("Binance Futures Widget")
        self.root.geometry("300x270+1500+100")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.93)
        self.root.configure(bg=BG_COLOR)

        self.offset_x = 0
        self.offset_y = 0

        # self.title_label = tk.Label(
        #     root, text="Binance Futures",
        #     font=("Arial", 13, "bold"),
        #     fg=FG_COLOR, bg=BG_COLOR
        # )
        # self.title_label.pack(pady=(8, 4))

        self.panels = []
        for symbol in SYMBOLS:
            panel = SymbolPanel(root, symbol)
            self.panels.append(panel)

        # self.time_label = tk.Label(
        #     root, text="更新时间: --",
        #     font=("Arial", 9), fg=SUB_COLOR, bg=BG_COLOR
        # )
        # self.time_label.pack(pady=(4, 8))

        self.tip_label = tk.Label(
            root, text="左键拖动 | 右键关闭",
            font=("Arial", 8), fg=SUB_COLOR, bg=BG_COLOR
        )
        self.tip_label.pack(pady=(0, 8))

        self.root.bind("<ButtonPress-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.on_move)
        self.root.bind("<Button-3>", lambda e: self.root.destroy())

        self.update_all()

    def start_move(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def on_move(self, event):
        x = self.root.winfo_x() + event.x - self.offset_x
        y = self.root.winfo_y() + event.y - self.offset_y
        self.root.geometry(f"+{x}+{y}")
        

    def fetch_symbol_data(self, symbol):
        price_url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
        stat_url = f"https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={symbol}"
        premium_url = f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}"

        price_resp = requests.get(price_url, timeout=5)
        stat_resp = requests.get(stat_url, timeout=5)
        premium_resp = requests.get(premium_url, timeout=5)

        price_resp.raise_for_status()
        stat_resp.raise_for_status()
        premium_resp.raise_for_status()

        price_data = price_resp.json()
        stat_data = stat_resp.json()
        premium_data = premium_resp.json()

        # 有些异常返回会带 code/msg，这里顺手拦一下
        if isinstance(price_data, dict) and "code" in price_data:
            raise ValueError(f"{symbol}: {price_data.get('msg', 'price接口错误')}")
        if isinstance(stat_data, dict) and "code" in stat_data:
            raise ValueError(f"{symbol}: {stat_data.get('msg', '24h接口错误')}")
        if isinstance(premium_data, dict) and "code" in premium_data:
            raise ValueError(f"{symbol}: {premium_data.get('msg', 'premium接口错误')}")

        price = float(price_data["price"])
        change_percent = float(stat_data["priceChangePercent"])
        funding_rate = float(premium_data["lastFundingRate"])

        return price, change_percent, funding_rate

    def update_all(self):
        for panel in self.panels:
            try:
                price, change_percent, funding_rate = self.fetch_symbol_data(panel.symbol)
                panel.update_view(price, change_percent, funding_rate)
            except Exception as e:
                print(f"[ERROR] {panel.symbol}: {e}")
                panel.show_error("读取失败")

        #now_str = time.strftime("%H:%M:%S")
        # self.time_label.config(text=f"更新时间: {now_str}")
        self.root.after(REFRESH_MS, self.update_all)


if __name__ == "__main__":
    root = tk.Tk()
    app = MultiPriceWidget(root)
    root.mainloop()