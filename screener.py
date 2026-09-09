import json
import random
from datetime import datetime

# Daftar emiten sampel
TICKERS = [
    {"ticker": "BBCA", "category": "Bluechip"},
    {"ticker": "BBRI", "category": "Bluechip"},
    {"ticker": "BMRI", "category": "Bluechip"},
    {"ticker": "TLKM", "category": "Bluechip"},
    {"ticker": "ASII", "category": "Bluechip"},
    {"ticker": "BRIS", "category": "IDX Liquid"},
    {"ticker": "MEDC", "category": "IDX Liquid"},
    {"ticker": "ANTM", "category": "IDX Liquid"},
    {"ticker": "PGAS", "category": "IDX Liquid"},
    {"ticker": "ADRO", "category": "IDX Liquid"}
]

def calculate_swing_strategy(close, ema20, ema50, rsi):
    score = 0
    
    if close > ema20:
        ema20_status = "strong_buy" if close >= ema20 * 1.03 else "buy"
        score += 2 if ema20_status == "strong_buy" else 1
    elif close < ema20:
        ema20_status = "strong_sell" if close <= ema20 * 0.97 else "sell"
        score -= 2 if ema20_status == "strong_sell" else 1
    else:
        ema20_status = "neutral"

    if ema20 > ema50:
        ema50_status = "strong_buy" if close > ema50 else "buy"
        score += 2 if ema50_status == "strong_buy" else 1
    elif ema20 < ema50:
        ema50_status = "strong_sell" if close < ema50 else "sell"
        score -= 2 if ema50_status == "strong_sell" else 1
    else:
        ema50_status = "neutral"

    if rsi >= 65:
        rsi_status = "strong_buy"
        score += 2
    elif 50 <= rsi < 65:
        rsi_status = "buy"
        score += 1
    elif 30 <= rsi <= 40:
        rsi_status = "sell"
        score -= 1
    elif rsi < 30:
        rsi_status = "strong_sell"
        score -= 2
    else:
        rsi_status = "neutral"

    if score >= 4:
        signal = "STRONG_BULLISH"
    elif score >= 1:
        signal = "BULLISH"
    elif score <= -4:
        signal = "STRONG_BEARISH"
    elif score <= -1:
        signal = "BEARISH"
    else:
        signal = "NEUTRAL"

    power_score = min(10, max(1, round(((score + 5) / 10) * 10)))

    return {
        "ema20_status": ema20_status,
        "ema50_status": ema50_status,
        "rsi_status": rsi_status,
        "signal": signal,
        "power_score": power_score
    }

def generate_screener_data():
    all_stocks = []

    for stock in TICKERS:
        close = random.randint(1000, 10000)
        change_pct = round(random.uniform(-4.0, 5.0), 2)
        ema20 = int(close * random.uniform(0.95, 1.05))
        ema50 = int(close * random.uniform(0.90, 1.10))
        rsi = round(random.uniform(25.0, 75.0), 1)

        swing_res = calculate_swing_strategy(close, ema20, ema50, rsi)

        item = {
            "ticker": stock["ticker"],
            "close": close,
            "change_pct": change_pct,
            "category": stock["category"],
            "ema20": ema20,
            "ema20_status": swing_res["ema20_status"],
            "ema50": ema50,
            "ema50_status": swing_res["ema50_status"],
            "rsi": rsi,
            "rsi_status": swing_res["rsi_status"],
            "signal": swing_res["signal"],
            "power_score": swing_res["power_score"],
            "stop_loss": round(close * 0.95, 1),
            "take_profit": round(close * 1.10, 1)
        }
        all_stocks.append(item)

    # Pastikan variabel penampung terisi penuh
    swing_setup = [s for s in all_stocks if s["signal"] in ["BULLISH", "STRONG_BULLISH"]]
    top_gainers = sorted(all_stocks, key=lambda x: x["change_pct"], reverse=True)[:5]
    top_movers = sorted(all_stocks, key=lambda x: abs(x["change_pct"]), reverse=True)[:5]
    bluechips = [s for s in all_stocks if s["category"] == "Bluechip"]

    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB"),
        "total_scanned": len(all_stocks),
        "swing_setup": swing_setup,
        "top_gainers": top_gainers,
        "top_movers": top_movers,
        "bluechips": bluechips,
        "all_stocks": all_stocks
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print("Data berhasil diperbarui di data.json")

if __name__ == "__main__":
    generate_screener_data()
