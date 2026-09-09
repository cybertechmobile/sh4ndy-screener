import json
from datetime import datetime
import pandas as pd
import yfinance as yf

# Daftar Saham Bluechip / LQ45 / Kompas100 Pilihan
BLUECHIP_TICKERS = [
    "BBCA.JK",
    "BBRI.JK",
    "BMRI.JK",
    "BBNI.JK",
    "TLKM.JK",
    "ASII.JK",
    "ICBP.JK",
    "UNVR.JK",
    "AMRT.JK",
    "KLBF.JK",
    "CPIN.JK",
    "GOTO.JK",
]

# Daftar Saham Likuid / Mid-Cap / Growth (IDX Expansion)
IDX_EXPANDED_TICKERS = [
    "BRIS.JK",
    "PGAS.JK",
    "MEDC.JK",
    "ANTM.JK",
    "INCO.JK",
    "TPIA.JK",
    "AMMN.JK",
    "BREN.JK",
    "CUAN.JK",
    "ADRO.JK",
    "PTBA.JK",
    "AKRA.JK",
    "AUTO.JK",
    "MBMA.JK",
    "ACES.JK",
]

# Gabungkan seluruh daftar ticker tanpa duplikasi
ALL_TICKERS = list(set(BLUECHIP_TICKERS + IDX_EXPANDED_TICKERS))


def calculate_indicators(df):
    # Persentase Perubahan Hari Ini (% Change)
    df["Change_Pct"] = df["Close"].pct_change() * 100

    # Exponential Moving Average (EMA)
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()

    # RSI (14)
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["RSI14"] = 100 - (100 / (1 + rs))

    # Average Volume 20
    df["Vol_MA20"] = df["Volume"].rolling(window=20).mean()

    # ATR (14)
    high_low = df["High"] - df["Low"]
    high_cp = (df["High"] - df["Close"].shift(1)).abs()
    low_cp = (df["Low"] - df["Close"].shift(1)).abs()
    tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
    df["ATR14"] = tr.rolling(window=14).mean()

    return df


def run_screener():
    all_processed = []
    swing_candidates = []

    for ticker in ALL_TICKERS:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="6mo")

            if len(df) < 50:
                continue

            df = calculate_indicators(df)
            latest = df.iloc[-1]
            clean_ticker = ticker.replace(".JK", "")

            # Tag kategori
            category = "Bluechip" if ticker in BLUECHIP_TICKERS else "IDX Liquid"

            entry_price = float(round(latest["Close"], 2))
            atr = float(latest["ATR14"])
            change_pct = (
                float(round(latest["Change_Pct"], 2))
                if not pd.isna(latest["Change_Pct"])
                else 0.0
            )

            stock_info = {
                "ticker": clean_ticker,
                "close": entry_price,
                "change_pct": change_pct,
                "volume": int(latest["Volume"]),
                "vol_ma20": int(latest["Vol_MA20"]),
                "ema20": round(float(latest["EMA20"]), 2),
                "ema50": round(float(latest["EMA50"]), 2),
                "rsi": round(float(latest["RSI14"]), 2),
                "category": category,
                "stop_loss": round(entry_price - (1.5 * atr), 2),
                "take_profit": round(entry_price + (3.0 * atr), 2),
                "risk_reward": "1:2",
            }

            all_processed.append(stock_info)

            # Logika Filter Swing Trading (Pullback)
            is_uptrend = (latest["Close"] > latest["EMA50"]) and (
                latest["EMA20"] > latest["EMA50"]
            )
            is_pullback = (latest["Close"] >= latest["EMA20"] * 0.985) and (
                latest["Close"] <= latest["EMA20"] * 1.015
            )
            is_rsi_ok = (latest["RSI14"] >= 40) and (latest["RSI14"] <= 65)
            is_vol_ok = latest["Volume"] > (latest["Vol_MA20"] * 0.8)

            if is_uptrend and is_pullback and is_rsi_ok and is_vol_ok:
                swing_candidates.append(stock_info)

        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    # 1. Top Gainers (Urutkan berdasarkan kenaikan % tertinggi)
    top_gainers = sorted(
        all_processed, key=lambda x: x["change_pct"], reverse=True
    )[:5]

    # 2. Top Movers / Volume Spikes (Urutkan dari rasio volume terbesar dibanding rata-ratanya)
    top_movers = sorted(
        all_processed,
        key=lambda x: (x["volume"] / x["vol_ma20"]) if x["vol_ma20"] > 0 else 0,
        reverse=True,
    )[:5]

    # 3. Filter khusus Bluechip
    bluechips = [s for s in all_processed if s["category"] == "Bluechip"]

    output_data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB"),
        "total_scanned": len(all_processed),
        "swing_setup": swing_candidates,
        "top_gainers": top_gainers,
        "top_movers": top_movers,
        "bluechips": bluechips,
        "all_stocks": all_processed,
    }

    with open("data.json", "w") as f:
        json.dump(output_data, f, indent=2)


if __name__ == "__main__":
    run_screener()
