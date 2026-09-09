import json
from datetime import datetime
import pandas as pd
import yfinance as yf

# Daftar saham IHSG (Tambahkan ticker lainnya)
TICKERS = [
    "BBCA.JK",
    "BBRI.JK",
    "BMRI.JK",
    "TLKM.JK",
    "ASII.JK",
    "AMRT.JK",
    "ICBP.JK",
    "BRIS.JK",
    "PGAS.JK",
    "MEDC.JK",
  ".JK",
]


def calculate_indicators(df):
    # Exponential Moving Average (EMA)
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()

    # Relative Strength Index (RSI 14)
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["RSI14"] = 100 - (100 / (1 + rs))

    # Average Volume 20
    df["Vol_MA20"] = df["Volume"].rolling(window=20).mean()

    # Average True Range (ATR 14)
    high_low = df["High"] - df["Low"]
    high_cp = (df["High"] - df["Close"].shift(1)).abs()
    low_cp = (df["Low"] - df["Close"].shift(1)).abs()
    tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
    df["ATR14"] = tr.rolling(window=14).mean()

    return df


def run_screener():
    results = []

    for ticker in TICKERS:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="6mo")

            if len(df) < 50:
                continue

            df = calculate_indicators(df)
            latest = df.iloc[-1]

            # Logika Algoritma Swing Trader (Buy on Pullback)
            is_uptrend = (latest["Close"] > latest["EMA50"]) and (
                latest["EMA20"] > latest["EMA50"]
            )
            is_pullback = (latest["Close"] >= latest["EMA20"] * 0.985) and (
                latest["Close"] <= latest["EMA20"] * 1.015
            )
            is_rsi_ok = (latest["RSI14"] >= 45) and (latest["RSI14"] <= 65)
            is_vol_ok = latest["Volume"] > latest["Vol_MA20"]

            if is_uptrend and is_pullback and is_rsi_ok and is_vol_ok:
                entry_price = float(round(latest["Close"], 2))
                atr = float(latest["ATR14"])
                stop_loss = round(entry_price - (1.5 * atr), 2)
                take_profit = round(entry_price + (3.0 * atr), 2)

                results.append({
                    "ticker": ticker.replace(".JK", ""),
                    "close": entry_price,
                    "ema20": round(float(latest["EMA20"]), 2),
                    "ema50": round(float(latest["EMA50"]), 2),
                    "rsi": round(float(latest["RSI14"]), 2),
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "risk_reward": "1:2",
                })
        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    output_data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB"),
        "total_matches": len(results),
        "data": results,
    }

    with open("data.json", "w") as f:
        json.dump(output_data, f, indent=2)


if __name__ == "__main__":
    run_screener()
