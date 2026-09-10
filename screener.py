import json
import os
import pandas as pd
import yfinance as yf

# Daftar 180+ Emiten Terlikuid & Populer di BEI (IDX)
TICKERS = [
    # Perbankan & Keuangan
    "BBCA.JK",
    "BBRI.JK",
    "BMRI.JK",
    "BBNI.JK",
    "BBTN.JK",
    "BRIS.JK",
    "ARTO.JK",
    "BDMN.JK",
    "BNGA.JK",
    "PNBN.JK",
    "MEGA.JK",
    "AGRO.JK",
    "BJBR.JK",
    "BJTM.JK",
    "BFIN.JK",
    "PNLF.JK",
    # Energi, Batubara & Minyak
    "ADRO.JK",
    "PTBA.JK",
    "ITMG.JK",
    "HRUM.JK",
    "INDY.JK",
    "MEDC.JK",
    "PGAS.JK",
    "AKRA.JK",
    "ELSA.JK",
    "DOID.JK",
    "MBAP.JK",
    "TOBA.JK",
    "BUMI.JK",
    "ENRG.JK",
    "KKGI.JK",
    "ABMM.JK",
    "GEMS.JK",
    "CUAN.JK",
    "BREN.JK",
    # Mineral, Logam & Logam Mulia
    "ANTM.JK",
    "INCO.JK",
    "TINS.JK",
    "MDKA.JK",
    "MBMA.JK",
    "NCKL.JK",
    "AMMN.JK",
    "PSAB.JK",
    "DKFT.JK",
    "CITA.JK",
    # Telekomunikasi & Teknologi
    "TLKM.JK",
    "ISAT.JK",
    "EXCL.JK",
    "GOTO.JK",
    "BUKA.JK",
    "MTDL.JK",
    "EMTK.JK",
    "SCMA.JK",
    "WIFI.JK",
    "BELI.JK",
    # Otomotif, Infrastruktur & Menara
    "ASII.JK",
    "AUTO.JK",
    "SMSM.JK",
    "GJTL.JK",
    "IMAS.JK",
    "TOWR.JK",
    "TBIG.JK",
    "CENT.JK",
    "JSMR.JK",
    "WIKA.JK",
    "PTPP.JK",
    "ADHI.JK",
    "WEGE.JK",
    "TOTL.JK",
    # Konsumsi, Makanan, Minuman & Farmasi
    "UNVR.JK",
    "INDF.JK",
    "ICBP.JK",
    "MYOR.JK",
    "KLBF.JK",
    "SIDO.JK",
    "CPIN.JK",
    "JPFA.JK",
    "MAIN.JK",
    "AMRT.JK",
    "MIDI.JK",
    "CMRY.JK",
    "GOOD.JK",
    "ROTI.JK",
    "STTP.JK",
    "ULTJ.JK",
    "TSPC.JK",
    "KAEF.JK",
    "INAF.JK",
    "MIKA.JK",
    "HEAL.JK",
    "SILO.JK",
    "SAME.JK",
    # Ritel, Properti & Konstruksi
    "ACES.JK",
    "MAPI.JK",
    "MAPA.JK",
    "LPPF.JK",
    "RALS.JK",
    "BSDE.JK",
    "CTRA.JK",
    "PWON.JK",
    "SMRA.JK",
    "ASRI.JK",
    "APLN.JK",
    "DILD.JK",
    "MDLN.JK",
    "MKPI.JK",
    # Semen, Kimia & Industri
    "SMGR.JK",
    "INTP.JK",
    "SMBR.JK",
    "TPIA.JK",
    "BRPT.JK",
    "ESSA.JK",
    "AVIA.JK",
    "APEX.JK",
    "INKP.JK",
    "TKIM.JK",
    "SPMA.JK",
    # Perkebunan & CPO
    "AALI.JK",
    "LSIP.JK",
    "DSNG.JK",
    "TAPG.JK",
    "SSMS.JK",
    "BWPT.JK",
    "SGRO.JK",
    # Transportasi, Logistik & Alat Berat
    "UNTR.JK",
    "HEXA.JK",
    "BIRD.JK",
    "ASSA.JK",
    "SMDR.JK",
    "TMAS.JK",
    "IPCC.JK",
    "GIAA.JK",
    # Media, Hiburan & Lainnya
    "MNCN.JK",
    "BMTR.JK",
    "FILM.JK",
    "VONE.JK",
    "ACES.JK",
    "CLEO.JK",
]


def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    for i in range(period, len(series)):
        avg_gain.iloc[i] = (avg_gain.iloc[i - 1] * 13 + gain.iloc[i]) / 14
        avg_loss.iloc[i] = (avg_loss.iloc[i - 1] * 13 + loss.iloc[i]) / 14

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def get_ihsg_data():
    try:
        ihsg = yf.Ticker("^JKSE")
        hist = ihsg.history(period="5d")
        if len(hist) >= 2:
            latest = hist.iloc[-1]
            prev = hist.iloc[-2]
            open_p = float(latest["Open"])
            high_p = float(latest["High"])
            low_p = float(latest["Low"])
            close_p = float(latest["Close"])
            prev_p = float(prev["Close"])
            change_p = float(((close_p - prev_p) / prev_p) * 100)

            return {
                "open": round(open_p, 2),
                "high": round(high_p, 2),
                "low": round(low_p, 2),
                "close": round(close_p, 2),
                "prev": round(prev_p, 2),
                "change": round(change_p, 2),
            }
    except Exception as e:
        print(f"Error fetching IHSG: {e}")

    return {
        "open": 0,
        "high": 0,
        "low": 0,
        "close": 0,
        "prev": 0,
        "change": 0,
    }


def analyze_stock(ticker):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="6mo")
        if len(df) < 50:
            return None

        df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
        df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
        df["RSI"] = calculate_rsi(df["Close"], 14)

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        close = float(latest["Close"])
        prev_close = float(prev["Close"])
        change_pct = float(((close - prev_close) / prev_close) * 100)

        ema20 = float(latest["EMA20"])
        ema50 = float(latest["EMA50"])
        rsi = float(latest["RSI"])

        # Perhitungan Signal Power Score (Skala 1 - 10)
        power_score = 5

        # Trend EMA
        if close > ema20:
            power_score += 1
        else:
            power_score -= 1

        if close > ema50:
            power_score += 1
        else:
            power_score -= 1

        if ema20 > ema50:
            power_score += 1
        else:
            power_score -= 1

        # Kondisi RSI
        if 40 <= rsi <= 65:
            power_score += 1
        elif rsi > 70:
            power_score -= 1
        elif rsi < 30:
            power_score += 1

        # Pembatasan Skala 1 - 10
        power_score = max(1, min(10, power_score))

        # Pengelompokan Kategori
        category = "Netral"
        if power_score >= 8:
            category = "Strong Bullish"
        elif power_score >= 6:
            category = "Bullish"
        elif power_score <= 3:
            category = "Strong Bearish"
        elif power_score <= 4:
            category = "Bearish"

        # Kalkulasi Stop Loss & Take Profit (TP1 +5%, TP2 +10%)
        stop_loss = round(min(ema20, close * 0.96), 0)
        tp1 = round(close * 1.05, 0)
        tp2 = round(close * 1.10, 0)

        clean_symbol = ticker.replace(".JK", "")

        return {
            "symbol": clean_symbol,
            "close": round(close, 0),
            "change": round(change_pct, 2),
            "ema20": round(ema20, 0),
            "ema50": round(ema50, 0),
            "rsi": round(rsi, 2),
            "power_score": power_score,
            "category": category,
            "stop_loss": stop_loss,
            "tp1": tp1,
            "tp2": tp2,
        }
    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")
        return None


def main():
    print("Memulai pemindaian saham...")
    stocks_data = []

    for idx, ticker in enumerate(TICKERS):
        print(f"[{idx+1}/{len(TICKERS)}] Analyzing {ticker}...")
        data = analyze_stock(ticker)
        if data:
            stocks_data.append(data)

    # Sort berdasarkan Power Score tertinggi (10 ke 1)
    stocks_data.sort(
        key=lambda x: (x["power_score"], x["change"]), reverse=True
    )

    ihsg_data = get_ihsg_data()

    output_data = {"ihsg": ihsg_data, "stocks": stocks_data}

    with open("data.json", "w") as f:
        json.dump(output_data, f, indent=2)

    print("Selesai! Data berhasil disimpan ke data.json")


if __name__ == "__main__":
    main()
