import json
from datetime import datetime
import pandas as pd
import yfinance as yf

# Daftar 100 Emiten IDX Terpopuler
TICKERS = [
    # Bluechip / Big Cap
    {"ticker": "BBCA", "category": "Bluechip"}, {"ticker": "BBRI", "category": "Bluechip"},
    {"ticker": "BMRI", "category": "Bluechip"}, {"ticker": "BBNI", "category": "Bluechip"},
    {"ticker": "TLKM", "category": "Bluechip"}, {"ticker": "ASII", "category": "Bluechip"},
    {"ticker": "UNVR", "category": "Bluechip"}, {"ticker": "ICBP", "category": "Bluechip"},
    {"ticker": "INDF", "category": "Bluechip"}, {"ticker": "AMRT", "category": "Bluechip"},
    {"ticker": "TPIA", "category": "Bluechip"}, {"ticker": "BREN", "category": "Bluechip"},
    {"ticker": "BYAN", "category": "Bluechip"}, {"ticker": "CPIN", "category": "Bluechip"},
    {"ticker": "GOTO", "category": "Bluechip"}, {"ticker": "KLBF", "category": "Bluechip"},

    # Mining, Energy & Resources (IDX Liquid)
    {"ticker": "ADRO", "category": "IDX Liquid"}, {"ticker": "PTBA", "category": "IDX Liquid"},
    {"ticker": "ITMG", "category": "IDX Liquid"}, {"ticker": "MEDC", "category": "IDX Liquid"},
    {"ticker": "ANTM", "category": "IDX Liquid"}, {"ticker": "INCO", "category": "IDX Liquid"},
    {"ticker": "PGAS", "category": "IDX Liquid"}, {"ticker": "AKRA", "category": "IDX Liquid"},
    {"ticker": "HRUM", "category": "IDX Liquid"}, {"ticker": "MBMA", "category": "IDX Liquid"},
    {"ticker": "NCKL", "category": "IDX Liquid"}, {"ticker": "AMMN", "category": "IDX Liquid"},
    {"ticker": "CUAN", "category": "IDX Liquid"}, {"ticker": "DOOID", "category": "IDX Liquid"},
    {"ticker": "INDY", "category": "IDX Liquid"}, {"ticker": "ELSA", "category": "IDX Liquid"},
    {"ticker": "ENRG", "category": "IDX Liquid"},

    # Banking & Financial Services
    {"ticker": "BRIS", "category": "IDX Liquid"}, {"ticker": "BBTN", "category": "IDX Liquid"},
    {"ticker": "BDMN", "category": "IDX Liquid"}, {"ticker": "BNGA", "category": "IDX Liquid"},
    {"ticker": "NISP", "category": "IDX Liquid"}, {"ticker": "PNBN", "category": "IDX Liquid"},
    {"ticker": "ARTO", "category": "IDX Liquid"}, {"ticker": "BBYB", "category": "IDX Liquid"},
    {"ticker": "BANK", "category": "IDX Liquid"}, {"ticker": "AGRO", "category": "IDX Liquid"},

    # Telecom, Tech & Infrastructure
    {"ticker": "EXCL", "category": "IDX Liquid"}, {"ticker": "ISAT", "category": "IDX Liquid"},
    {"ticker": "TOWR", "category": "IDX Liquid"}, {"ticker": "TBIG", "category": "IDX Liquid"},
    {"ticker": "MTEL", "category": "IDX Liquid"}, {"ticker": "EMTK", "category": "IDX Liquid"},
    {"ticker": "SCMA", "category": "IDX Liquid"}, {"ticker": "BUKA", "category": "IDX Liquid"},
    {"ticker": "WIFI", "category": "IDX Liquid"}, {"ticker": "CENT", "category": "IDX Liquid"},

    # Consumer, Retail & Healthcare
    {"ticker": "MYOR", "category": "IDX Liquid"}, {"ticker": "CMRY", "category": "IDX Liquid"},
    {"ticker": "ACES", "category": "IDX Liquid"}, {"ticker": "MAPI", "category": "IDX Liquid"},
    {"ticker": "MAPA", "category": "IDX Liquid"}, {"ticker": "RALS", "category": "IDX Liquid"},
    {"ticker": "LPPF", "category": "IDX Liquid"}, {"ticker": "ERAA", "category": "IDX Liquid"},
    {"ticker": "MIKA", "category": "IDX Liquid"}, {"ticker": "HEAL", "category": "IDX Liquid"},
    {"ticker": "SILO", "category": "IDX Liquid"}, {"ticker": "SIDO", "category": "IDX Liquid"},
    {"ticker": "TSPC", "category": "IDX Liquid"}, {"ticker": "KAEF", "category": "IDX Liquid"},

    # Property, Real Estate & Construction
    {"ticker": "BSDE", "category": "IDX Liquid"}, {"ticker": "CTRA", "category": "IDX Liquid"},
    {"ticker": "PWON", "category": "IDX Liquid"}, {"ticker": "SMRA", "category": "IDX Liquid"},
    {"ticker": "ASRI", "category": "IDX Liquid"}, {"ticker": "ADHI", "category": "IDX Liquid"},
    {"ticker": "PTPP", "category": "IDX Liquid"}, {"ticker": "WIKA", "category": "IDX Liquid"},
    {"ticker": "WEGE", "category": "IDX Liquid"}, {"ticker": "TOTL", "category": "IDX Liquid"},

    # Industrial, Automotive & Logistics
    {"ticker": "SMGR", "category": "IDX Liquid"}, {"ticker": "INTP", "category": "IDX Liquid"},
    {"ticker": "UNTR", "category": "IDX Liquid"}, {"ticker": "AUTO", "category": "IDX Liquid"},
    {"ticker": "GJTL", "category": "IDX Liquid"}, {"ticker": "SMSM", "category": "IDX Liquid"},
    {"ticker": "IMAS", "category": "IDX Liquid"}, {"ticker": "BIRD", "category": "IDX Liquid"},
    {"ticker": "ASSA", "category": "IDX Liquid"}, {"ticker": "SMDR", "category": "IDX Liquid"},
    {"ticker": "TEMAS", "category": "IDX Liquid"}, {"ticker": "TINS", "category": "IDX Liquid"},
    {"ticker": "WOOD", "category": "IDX Liquid"}, {"ticker": "MAIN", "category": "IDX Liquid"},
    {"ticker": "JPFA", "category": "IDX Liquid"}, {"ticker": "TAPG", "category": "IDX Liquid"},
    {"ticker": "DSNG", "category": "IDX Liquid"}, {"ticker": "SSMS", "category": "IDX Liquid"}
]

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_swing_strategy(close, ema20, ema50, rsi):
    score = 0
    
    # Evaluasi EMA 20 terhadap Harga
    if close > ema20:
        ema20_status = "strong_buy" if close >= ema20 * 1.02 else "buy"
        score += 2 if ema20_status == "strong_buy" else 1
    elif close < ema20:
        ema20_status = "strong_sell" if close <= ema20 * 0.98 else "sell"
        score -= 2 if ema20_status == "strong_sell" else 1
    else:
        ema20_status = "neutral"

    # Evaluasi Trend EMA 20 vs EMA 50
    if ema20 > ema50:
        ema50_status = "strong_buy" if close > ema50 else "buy"
        score += 2 if ema50_status == "strong_buy" else 1
    elif ema20 < ema50:
        ema50_status = "strong_sell" if close < ema50 else "sell"
        score -= 2 if ema50_status == "strong_sell" else 1
    else:
        ema50_status = "neutral"

    # Evaluasi Momentum RSI
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

    # Sinyal Gabungan
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

def fetch_real_data():
    all_stocks = []
    print("Mengambil data riil dari Bursa Saham Indonesia (IDX)...")

    for stock in TICKERS:
        ticker_symbol = f"{stock['ticker']}.JK"
        try:
            # Unduh riwayat 100 hari untuk kalkulasi indikator teknis
            df = yf.download(ticker_symbol, period="100d", interval="1d", progress=False)

            if df.empty or len(df) < 50:
                print(f"⚠️ Data tidak cukup untuk: {stock['ticker']}")
                continue

            # Hitung Indikator
            df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
            df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
            df['RSI'] = calculate_rsi(df['Close'], 14)

            latest = df.iloc[-1]
            previous = df.iloc[-2]

            # MURNI HARGA ASLI PASAR (Tanpa dikali/diacak)
            close = float(latest['Close'])
            prev_close = float(previous['Close'])
            
            # Hitung Perubahan Persentase Riil
            change_pct = round(((close - prev_close) / prev_close) * 100, 2) if prev_close > 0 else 0.0
            
            ema20 = float(latest['EMA20'])
            ema50 = float(latest['EMA50'])
            rsi = round(float(latest['RSI']), 1) if not pd.isna(latest['RSI']) else 50.0

            # Kalkulasi sinyal tanpa mengubah nilai 'close' asli
            swing_res = calculate_swing_strategy(close, ema20, ema50, rsi)

            item = {
                "ticker": stock["ticker"],
                "close": round(close, 2), # Harga asli
                "change_pct": change_pct,
                "category": stock["category"],
                "ema20": round(ema20, 2),
                "ema20_status": swing_res["ema20_status"],
                "ema50": round(ema50, 2),
                "ema50_status": swing_res["ema50_status"],
                "rsi": rsi,
                "rsi_status": swing_res["rsi_status"],
                "signal": swing_res["signal"],
                "power_score": swing_res["power_score"],
                "stop_loss": round(close * 0.95, 2),
                "take_profit": round(close * 1.10, 2)
            }
            all_stocks.append(item)
            print(f"✅ {stock['ticker']}: Rp{close:,.0f} ({change_pct}%)")

        except Exception as e:
            print(f"❌ Error mengunduh {stock['ticker']}: {e}")

    # Pengelompokan Tab Secara Dinamis dan Presisi
    swing_setup = [s for s in all_stocks if s["signal"] in ["BULLISH", "STRONG_BULLISH"]]
    top_gainers = sorted(all_stocks, key=lambda x: x["change_pct"], reverse=True)[:20]
    top_movers = sorted(all_stocks, key=lambda x: abs(x["change_pct"]), reverse=True)[:20]
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

    print(f"\n🚀 Selesai! {len(all_stocks)} emiten berhasil diproses ke data.json")

if __name__ == "__main__":
    fetch_real_data()
