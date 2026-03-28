from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
from collections import deque
import itertools
import time
import random
import os
import pickle

# Portföy bilgileri (Tarih, Alış Fiyatı)
portfolio = {

    # ========== 🔥 GÜÇLÜ HACİMLİ GİRİŞ (52 hisse) ==========
    "DMSAS": ["03-12-2025", 10.81],  # GÜÇLÜ_HACİMLİ
    "EFORC": ["04-12-2025", 25.76],  # GÜÇLÜ_HACİMLİ
    "EKIZ": ["04-12-2025", 96.0],  # GÜÇLÜ_HACİMLİ
    "KTSKR": ["05-12-2025", 78.83],  # GÜÇLÜ_HACİMLİ
    "ULKER": ["09-12-2025", 117.66],  # GÜÇLÜ_HACİMLİ
    "ISYAT": ["10-12-2025", 9.01],  # GÜÇLÜ_HACİMLİ
    "EDIP": ["11-12-2025", 38.54],  # GÜÇLÜ_HACİMLİ
    "OTTO": ["12-12-2025", 500.2],  # GÜÇLÜ_HACİMLİ
    "SARKY": ["12-12-2025", 16.58],  # GÜÇLÜ_HACİMLİ
    "ARASE": ["17-12-2025", 66.86],  # GÜÇLÜ_HACİMLİ
    "MTRYO": ["18-12-2025", 9.21],  # GÜÇLÜ_HACİMLİ
    "GARFA": ["22-12-2025", 26.48],  # GÜÇLÜ_HACİMLİ
    "BSOKE": ["22-12-2025", 17.37],  # GÜÇLÜ_HACİMLİ
    "NUGYO": ["24-12-2025", 9.95],  # GÜÇLÜ_HACİMLİ
    "FORTE": ["25-12-2025", 85.04],  # GÜÇLÜ_HACİMLİ
    "AYDEM": ["26-12-2025", 20.91],  # GÜÇLÜ_HACİMLİ
    "RALYH": ["26-12-2025", 226.04],  # GÜÇLÜ_HACİMLİ
    "BEYAZ": ["08-01-2026", 31.49],  # GÜÇLÜ_HACİMLİ
    "KLGYO": ["09-01-2026", 6.94],  # GÜÇLÜ_HACİMLİ
    "ALKIM": ["09-01-2026", 19.19],  # GÜÇLÜ_HACİMLİ
    "ISGYO": ["14-01-2026", 22.22],  # GÜÇLÜ_HACİMLİ
    "KGYO": ["14-01-2026", 5.59],  # GÜÇLÜ_HACİMLİ
    "LIDFA": ["15-01-2026", 2.46],  # GÜÇLÜ_HACİMLİ
    "HLGYO": ["15-01-2026", 4.27],  # GÜÇLÜ_HACİMLİ
    "YYLGD": ["16-01-2026", 11.15],  # GÜÇLÜ_HACİMLİ
    "TABGD": ["16-01-2026", 252.75],  # GÜÇLÜ_HACİMLİ
    "ENTRA": ["19-01-2026", 11.04],  # GÜÇLÜ_HACİMLİ
    "AGYO": ["19-01-2026", 7.59],  # GÜÇLÜ_HACİMLİ
    "MZHLD": ["20-01-2026", 7.16],  # GÜÇLÜ_HACİMLİ
    "OYYAT": ["22-01-2026", 44.48],  # GÜÇLÜ_HACİMLİ
    "LOGO": ["23-01-2026", 170.08],  # GÜÇLÜ_HACİMLİ
    "YUNSA": ["23-01-2026", 8.62],  # GÜÇLÜ_HACİMLİ
    "DURDO": ["23-01-2026", 4.05],  # GÜÇLÜ_HACİMLİ
    "CONSE": ["26-01-2026", 3.32],  # GÜÇLÜ_HACİMLİ
    "BAKAB": ["26-01-2026", 42.32],  # GÜÇLÜ_HACİMLİ
    "HUBVC": ["26-01-2026", 2.91],  # GÜÇLÜ_HACİMLİ
    "BASCM": ["27-01-2026", 14.63],  # GÜÇLÜ_HACİMLİ
    "DOKTA": ["28-01-2026", 25.86],  # GÜÇLÜ_HACİMLİ
    "PNSUT": ["02-02-2026", 12.22],  # GÜÇLÜ_HACİMLİ
    "AKFYE": ["02-02-2026", 19.03],  # GÜÇLÜ_HACİMLİ
    "OZYSR": ["02-02-2026", 46.56],  # GÜÇLÜ_HACİMLİ
    "SEKFK": ["04-02-2026", 9.45],  # GÜÇLÜ_HACİMLİ
    "FLAP": ["10-02-2026", 9.54],  # GÜÇLÜ_HACİMLİ
    "KOPOL": ["12-02-2026", 6.17],  # GÜÇLÜ_HACİMLİ
    "ASUZU": ["16-02-2026", 67.82],  # GÜÇLÜ_HACİMLİ
    "BOBET": ["16-02-2026", 22.04],  # GÜÇLÜ_HACİMLİ
    "AFYON": ["16-02-2026", 15.25],  # GÜÇLÜ_HACİMLİ
    "AKENR": ["17-02-2026", 11.89],  # GÜÇLÜ_HACİMLİ
    "BASGZ": ["19-02-2026", 48.76],  # GÜÇLÜ_HACİMLİ
    "IEYHO": ["05-03-2026", 82.77],  # GÜÇLÜ_HACİMLİ
    "KRONT": ["05-03-2026", 17.0],  # GÜÇLÜ_HACİMLİ
    "ULAS": ["27-03-2026", 36.86],  # GÜÇLÜ_HACİMLİ

    # ========== ✅ HACİMLİ GİRİŞ SİNYALİ (18 hisse) ==========
    "AYES": ["01-12-2025", 16.77],  # HACİMLİ
    "GLCVY": ["01-12-2025", 80.19],  # HACİMLİ
    "YKBNK": ["02-12-2025", 35.79],  # HACİMLİ
    "ALARK": ["22-12-2025", 102.41],  # HACİMLİ
    "EUYO": ["26-12-2025", 14.34],  # HACİMLİ
    "GLBMD": ["30-12-2025", 13.54],  # HACİMLİ
    "EGPRO": ["06-01-2026", 26.08],  # HACİMLİ
    "FZLGY": ["07-01-2026", 14.15],  # HACİMLİ
    "KRPLS": ["14-01-2026", 8.79],  # HACİMLİ
    "BIZIM": ["15-01-2026", 29.41],  # HACİMLİ
    "CASA": ["16-01-2026", 117.16],  # HACİMLİ
    "GSDDE": ["19-01-2026", 10.69],  # HACİMLİ
    "AKFGY": ["19-01-2026", 2.95],  # HACİMLİ
    "DGATE": ["22-01-2026", 76.0],  # HACİMLİ
    "DMRGD": ["05-02-2026", 3.85],  # HACİMLİ
    "BINHO": ["09-02-2026", 9.89],  # HACİMLİ
    "MRGYO": ["17-02-2026", 2.91],  # HACİMLİ
    "ZEDUR": ["17-02-2026", 9.19],  # HACİMLİ

    # ========== ✅ GİRİŞ SİNYALİ (95 hisse) ==========
    "VKFYO": ["27-11-2025", 23.71],  # GİRİŞ
    "GARAN": ["01-12-2025", 141.7],  # GİRİŞ
    "OTKAR": ["08-12-2025", 509.54],  # GİRİŞ
    "TAVHL": ["10-12-2025", 293.15],  # GİRİŞ
    "IZENR": ["11-12-2025", 10.79],  # GİRİŞ
    "ENJSA": ["12-12-2025", 87.62],  # GİRİŞ
    "NIBAS": ["12-12-2025", 26.6],  # GİRİŞ
    "ASELS": ["15-12-2025", 212.0],  # GİRİŞ
    "ATLAS": ["18-12-2025", 6.63],  # GİRİŞ
    "EUKYO": ["19-12-2025", 17.12],  # GİRİŞ
    "SAFKR": ["22-12-2025", 27.43],  # GİRİŞ
    "YATAS": ["23-12-2025", 38.34],  # GİRİŞ
    "KOZAA": ["24-12-2025", 108.47],  # GİRİŞ
    "GUBRF": ["24-12-2025", 346.18],  # GİRİŞ
    "IPEKE": ["25-12-2025", 90.4],  # GİRİŞ
    "MRSHL": ["25-12-2025", 1826.08],  # GİRİŞ
    "KLKIM": ["25-12-2025", 34.58],  # GİRİŞ
    "KLMSN": ["25-12-2025", 33.27],  # GİRİŞ
    "ANHYT": ["26-12-2025", 107.56],  # GİRİŞ
    "ESCOM": ["29-12-2025", 3.59],  # GİRİŞ
    "EGEPO": ["30-12-2025", 8.31],  # GİRİŞ
    "EDATA": ["30-12-2025", 5.83],  # GİRİŞ
    "PARSN": ["30-12-2025", 97.87],  # GİRİŞ
    "ARSAN": ["31-12-2025", 3.58],  # GİRİŞ
    "KRVGD": ["31-12-2025", 2.76],  # GİRİŞ
    "SELEC": ["31-12-2025", 82.32],  # GİRİŞ
    "BRSAN": ["03-01-2026", 567.12],  # GİRİŞ
    "TOASO": ["05-01-2026", 258.31],  # GİRİŞ
    "KCHOL": ["05-01-2026", 179.88],  # GİRİŞ
    "SOKM": ["06-01-2026", 52.37],  # GİRİŞ
    "DOAS": ["07-01-2026", 197.76],  # GİRİŞ
    "GMTAS": ["08-01-2026", 48.06],  # GİRİŞ
    "ADGYO": ["09-01-2026", 53.53],  # GİRİŞ
    "LUKSK": ["09-01-2026", 115.24],  # GİRİŞ
    "EUPWR": ["12-01-2026", 35.13],  # GİRİŞ
    "PRKAB": ["14-01-2026", 35.23],  # GİRİŞ
    "ATAKP": ["14-01-2026", 56.26],  # GİRİŞ
    "AVTUR": ["14-01-2026", 17.22],  # GİRİŞ
    "RGYAS": ["14-01-2026", 145.67],  # GİRİŞ
    "ADEL": ["15-01-2026", 37.88],  # GİRİŞ
    "ERBOS": ["15-01-2026", 200.18],  # GİRİŞ
    "TTKOM": ["15-01-2026", 60.25],  # GİRİŞ
    "KZGYO": ["15-01-2026", 25.82],  # GİRİŞ
    "GENTS": ["16-01-2026", 11.53],  # GİRİŞ
    "EKGYO": ["16-01-2026", 22.22],  # GİRİŞ
    "KIMMR": ["16-01-2026", 14.54],  # GİRİŞ
    "ENKAI": ["17-01-2026", 83.07],  # GİRİŞ
    "AKGRT": ["17-01-2026", 7.89],  # GİRİŞ
    "OBASE": ["20-01-2026", 38.2],  # GİRİŞ
    "DZGYO": ["21-01-2026", 8.76],  # GİRİŞ
    "CRFSA": ["21-01-2026", 135.14],  # GİRİŞ
    "KRSTL": ["22-01-2026", 11.07],  # GİRİŞ
    "A1CAP": ["23-01-2026", 13.6],  # GİRİŞ
    "ISMEN": ["23-01-2026", 44.14],  # GİRİŞ
    "AGESA": ["23-01-2026", 231.59],  # GİRİŞ
    "GLYHO": ["23-01-2026", 13.75],  # GİRİŞ
    "RTALB": ["26-01-2026", 3.85],  # GİRİŞ
    "TATGD": ["26-01-2026", 13.94],  # GİRİŞ
    "MNDRS": ["26-01-2026", 15.09],  # GİRİŞ
    "HRKET": ["26-01-2026", 79.54],  # GİRİŞ
    "SILVR": ["27-01-2026", 3.05],  # GİRİŞ
    "MEGMT": ["27-01-2026", 63.98],  # GİRİŞ
    "BRISA": ["27-01-2026", 90.95],  # GİRİŞ
    "LMKDC": ["27-01-2026", 33.23],  # GİRİŞ
    "BORSK": ["27-01-2026", 7.24],  # GİRİŞ
    "INDES": ["30-01-2026", 8.63],  # GİRİŞ
    "ISGSY": ["02-02-2026", 76.46],  # GİRİŞ
    "MEKAG": ["02-02-2026", 4.84],  # GİRİŞ
    "ULUFA": ["02-02-2026", 4.13],  # GİRİŞ
    "AZTEK": ["02-02-2026", 4.79],  # GİRİŞ
    "IZMDC": ["02-02-2026", 7.48],  # GİRİŞ
    "DEVA": ["03-02-2026", 70.3],  # GİRİŞ
    "FONET": ["03-02-2026", 3.37],  # GİRİŞ
    "GLRYH": ["04-02-2026", 4.53],  # GİRİŞ
    "SEKUR": ["05-02-2026", 4.01],  # GİRİŞ
    "BERA": ["09-02-2026", 20.0],  # GİRİŞ
    "LYDHO": ["09-02-2026", 190.99],  # GİRİŞ
    "ISDMR": ["09-02-2026", 43.94],  # GİRİŞ
    "PENGD": ["10-02-2026", 9.26],  # GİRİŞ
    "ULUUN": ["10-02-2026", 7.58],  # GİRİŞ
    "KRDMD": ["11-02-2026", 31.01],  # GİRİŞ
    "VAKBN": ["12-02-2026", 38.5],  # GİRİŞ
    "NTHOL": ["13-02-2026", 50.4],  # GİRİŞ
    "UNLU": ["16-02-2026", 18.18],  # GİRİŞ
    "AYEN": ["16-02-2026", 30.18],  # GİRİŞ
    "GOZDE": ["16-02-2026", 28.08],  # GİRİŞ
    "TSGYO": ["16-02-2026", 8.08],  # GİRİŞ
    "KRTEK": ["17-02-2026", 29.8],  # GİRİŞ
    "PKART": ["18-02-2026", 75.9],  # GİRİŞ
    "MOGAN": ["18-02-2026", 9.94],  # GİRİŞ
    "ODAS": ["18-02-2026", 6.54],  # GİRİŞ
    "VAKFN": ["18-02-2026", 2.32],  # GİRİŞ
    "KOCMT": ["18-02-2026", 2.88],  # GİRİŞ
    "EKOS": ["19-02-2026", 6.63],  # GİRİŞ
    "TUPRS": ["06-03-2026", 250.88],  # GİRİŞ

} 

# Sinyal kategorileri: telegram_to_portfolio.py tarafından otomatik doldurulur.
# Kategori değerleri: "GÜÇLÜ_HACİMLİ" | "HACİMLİ" | "GİRİŞ"
signal_categories = {
    "A1CAP": "GİRİŞ",
    "ADEL": "GİRİŞ",
    "ADGYO": "GİRİŞ",
    "AFYON": "GÜÇLÜ_HACİMLİ",
    "AGESA": "GİRİŞ",
    "AGYO": "GÜÇLÜ_HACİMLİ",
    "AKENR": "GÜÇLÜ_HACİMLİ",
    "AKFGY": "HACİMLİ",
    "AKFYE": "GÜÇLÜ_HACİMLİ",
    "AKGRT": "GİRİŞ",
    "ALARK": "HACİMLİ",
    "ALKIM": "GÜÇLÜ_HACİMLİ",
    "ANHYT": "GİRİŞ",
    "ARASE": "GÜÇLÜ_HACİMLİ",
    "ARSAN": "GİRİŞ",
    "ASELS": "GİRİŞ",
    "ASUZU": "GÜÇLÜ_HACİMLİ",
    "ATAKP": "GİRİŞ",
    "ATLAS": "GİRİŞ",
    "AVTUR": "GİRİŞ",
    "AYDEM": "GÜÇLÜ_HACİMLİ",
    "AYEN": "GİRİŞ",
    "AYES": "HACİMLİ",
    "AZTEK": "GİRİŞ",
    "BAKAB": "GÜÇLÜ_HACİMLİ",
    "BASCM": "GÜÇLÜ_HACİMLİ",
    "BASGZ": "GÜÇLÜ_HACİMLİ",
    "BERA": "GİRİŞ",
    "BEYAZ": "GÜÇLÜ_HACİMLİ",
    "BINHO": "HACİMLİ",
    "BIZIM": "HACİMLİ",
    "BOBET": "GÜÇLÜ_HACİMLİ",
    "BORSK": "GİRİŞ",
    "BRISA": "GİRİŞ",
    "BRSAN": "GİRİŞ",
    "BSOKE": "GÜÇLÜ_HACİMLİ",
    "CASA": "HACİMLİ",
    "CONSE": "GÜÇLÜ_HACİMLİ",
    "CRFSA": "GİRİŞ",
    "DEVA": "GİRİŞ",
    "DGATE": "HACİMLİ",
    "DMRGD": "HACİMLİ",
    "DMSAS": "GÜÇLÜ_HACİMLİ",
    "DOAS": "GİRİŞ",
    "DOKTA": "GÜÇLÜ_HACİMLİ",
    "DURDO": "GÜÇLÜ_HACİMLİ",
    "DZGYO": "GİRİŞ",
    "EDATA": "GİRİŞ",
    "EDIP": "GÜÇLÜ_HACİMLİ",
    "EFORC": "GÜÇLÜ_HACİMLİ",
    "EGEPO": "GİRİŞ",
    "EGPRO": "HACİMLİ",
    "EKGYO": "GİRİŞ",
    "EKIZ": "GÜÇLÜ_HACİMLİ",
    "EKOS": "GİRİŞ",
    "ENJSA": "GİRİŞ",
    "ENKAI": "GİRİŞ",
    "ENTRA": "GÜÇLÜ_HACİMLİ",
    "ERBOS": "GİRİŞ",
    "ESCOM": "GİRİŞ",
    "EUKYO": "GİRİŞ",
    "EUPWR": "GİRİŞ",
    "EUYO": "HACİMLİ",
    "FLAP": "GÜÇLÜ_HACİMLİ",
    "FONET": "GİRİŞ",
    "FORTE": "GÜÇLÜ_HACİMLİ",
    "FZLGY": "HACİMLİ",
    "GARAN": "GİRİŞ",
    "GARFA": "GÜÇLÜ_HACİMLİ",
    "GENTS": "GİRİŞ",
    "GLBMD": "HACİMLİ",
    "GLCVY": "HACİMLİ",
    "GLRYH": "GİRİŞ",
    "GLYHO": "GİRİŞ",
    "GMTAS": "GİRİŞ",
    "GOZDE": "GİRİŞ",
    "GSDDE": "HACİMLİ",
    "GUBRF": "GİRİŞ",
    "HLGYO": "GÜÇLÜ_HACİMLİ",
    "HRKET": "GİRİŞ",
    "HUBVC": "GÜÇLÜ_HACİMLİ",
    "IEYHO": "GÜÇLÜ_HACİMLİ",
    "INDES": "GİRİŞ",
    "IPEKE": "GİRİŞ",
    "ISDMR": "GİRİŞ",
    "ISGSY": "GİRİŞ",
    "ISGYO": "GÜÇLÜ_HACİMLİ",
    "ISMEN": "GİRİŞ",
    "ISYAT": "GÜÇLÜ_HACİMLİ",
    "IZENR": "GİRİŞ",
    "IZMDC": "GİRİŞ",
    "KCHOL": "GİRİŞ",
    "KGYO": "GÜÇLÜ_HACİMLİ",
    "KIMMR": "GİRİŞ",
    "KLGYO": "GÜÇLÜ_HACİMLİ",
    "KLKIM": "GİRİŞ",
    "KLMSN": "GİRİŞ",
    "KOCMT": "GİRİŞ",
    "KOPOL": "GÜÇLÜ_HACİMLİ",
    "KOZAA": "GİRİŞ",
    "KRDMD": "GİRİŞ",
    "KRONT": "GÜÇLÜ_HACİMLİ",
    "KRPLS": "HACİMLİ",
    "KRSTL": "GİRİŞ",
    "KRTEK": "GİRİŞ",
    "KRVGD": "GİRİŞ",
    "KTSKR": "GÜÇLÜ_HACİMLİ",
    "KZGYO": "GİRİŞ",
    "LIDFA": "GÜÇLÜ_HACİMLİ",
    "LMKDC": "GİRİŞ",
    "LOGO": "GÜÇLÜ_HACİMLİ",
    "LUKSK": "GİRİŞ",
    "LYDHO": "GİRİŞ",
    "MEGMT": "GİRİŞ",
    "MEKAG": "GİRİŞ",
    "MNDRS": "GİRİŞ",
    "MOGAN": "GİRİŞ",
    "MRGYO": "HACİMLİ",
    "MRSHL": "GİRİŞ",
    "MTRYO": "GÜÇLÜ_HACİMLİ",
    "MZHLD": "GÜÇLÜ_HACİMLİ",
    "NIBAS": "GİRİŞ",
    "NTHOL": "GİRİŞ",
    "NUGYO": "GÜÇLÜ_HACİMLİ",
    "OBASE": "GİRİŞ",
    "ODAS": "GİRİŞ",
    "OTKAR": "GİRİŞ",
    "OTTO": "GÜÇLÜ_HACİMLİ",
    "OYYAT": "GÜÇLÜ_HACİMLİ",
    "OZYSR": "GÜÇLÜ_HACİMLİ",
    "PARSN": "GİRİŞ",
    "PENGD": "GİRİŞ",
    "PKART": "GİRİŞ",
    "PNSUT": "GÜÇLÜ_HACİMLİ",
    "PRKAB": "GİRİŞ",
    "RALYH": "GÜÇLÜ_HACİMLİ",
    "RGYAS": "GİRİŞ",
    "RTALB": "GİRİŞ",
    "SAFKR": "GİRİŞ",
    "SARKY": "GÜÇLÜ_HACİMLİ",
    "SEKFK": "GÜÇLÜ_HACİMLİ",
    "SEKUR": "GİRİŞ",
    "SELEC": "GİRİŞ",
    "SILVR": "GİRİŞ",
    "SOKM": "GİRİŞ",
    "TABGD": "GÜÇLÜ_HACİMLİ",
    "TATGD": "GİRİŞ",
    "TAVHL": "GİRİŞ",
    "TOASO": "GİRİŞ",
    "TSGYO": "GİRİŞ",
    "TTKOM": "GİRİŞ",
    "TUPRS": "GİRİŞ",
    "ULAS": "GÜÇLÜ_HACİMLİ",
    "ULKER": "GÜÇLÜ_HACİMLİ",
    "ULUFA": "GİRİŞ",
    "ULUUN": "GİRİŞ",
    "UNLU": "GİRİŞ",
    "VAKBN": "GİRİŞ",
    "VAKFN": "GİRİŞ",
    "VKFYO": "GİRİŞ",
    "YATAS": "GİRİŞ",
    "YKBNK": "HACİMLİ",
    "YUNSA": "GÜÇLÜ_HACİMLİ",
    "YYLGD": "GÜÇLÜ_HACİMLİ",
    "ZEDUR": "HACİMLİ",
}

CATEGORY_LABELS = {
    "GÜÇLÜ_HACİMLİ": "🔥 GÜÇLÜ HACİMLİ GİRİŞ",
    "HACİMLİ":       "✅ HACİMLİ GİRİŞ SİNYALİ",
    "GİRİŞ":         "✅ GİRİŞ SİNYALİ",
    "BİLİNMEYEN":    "❓ Kategorisiz",
    "TÜM_HİSSELER":  "🌍 TÜM SİNYALLER BİR ARADA (Genel)",
    "GUCLU_VE_GIRIS": "🏆 GÜÇLÜ HACİMLİ + GİRİŞ SİNYALLERİ (İkili Kombinasyon)"
}

class UltimateOptimizedSimulator:
    def __init__(self, baslangic_bakiye=100000):
        self.baslangic_bakiye = baslangic_bakiye
        self.all_stock_data = {}
        self.baslangic_filtresi = None
        self.bitis_filtresi = None
        self.data_loaded = False
      
    def load_all_stock_data_once(self):
      """TÜM HİSSE VERİLERİNİ SADECE BİR KEZ ÇEK - BAŞTA!"""
      if self.data_loaded:
          print("📁 Veriler zaten yüklü - tekrar çekilmiyor!")
          return
          
      cache_file = "market_cache.pkl"
      today_str = datetime.now().strftime("%Y-%m-%d")
      
      # 1) Ön bellek kontrolü
      if os.path.exists(cache_file):
          # Dosyanın değiştirilme tarihi (gün bazında)
          mtime = os.path.getmtime(cache_file)
          file_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
          
          if file_date == today_str:
              print("⚡ BUGÜNÜN VERİLERİ ÖNBELLEKTEN (CACHE) YÜKLENİYOR! (Beklemeyeceksin!)")
              try:
                  with open(cache_file, "rb") as f:
                      self.all_stock_data = pickle.load(f)
                  self.data_loaded = True
                  print(f"✅ {len(self.all_stock_data)} hisse verisi 1 saniyede yüklendi.")
                  return
              except Exception as e:
                  print(f"⚠️ Önbellek okuma hatası: {e}. Yeniden çekilecek.")
                  
      print("🌐 TÜM HİSSE VERİLERİ ÇEKİLİYOR - SADECE BİR KEZ!")
      print("=" * 60)
      
      basarili_sayac = 0
      basarisiz_sayac = 0
      
      for hisse_kodu, detaylar in portfolio.items():
          try:
              # Ticker sembolü düzelt
              ticker_symbol = hisse_kodu + ".IS"
              ticker = yf.Ticker(ticker_symbol)
              
              # Tarih parse et
              alis_tarihi = datetime.strptime(detaylar[0], '%d-%m-%Y')
              alis_fiyati = detaylar[1]
              
              # Geniş tarih aralığı ile veri çek
              baslangic = alis_tarihi - timedelta(days=10)
              bitis = datetime.now() + timedelta(days=1)
              
              # Veri çekme işlemi
              history = ticker.history(
                  start=baslangic,
                  end=bitis,
                  interval='1d',
                  auto_adjust=True,
                  prepost=False,
                  actions=False
              )
              
              # Veri kontrolü
              if not history.empty and len(history) >= 2:
                  # NaN değerleri temizle
                  history = history.dropna()
                  
                  if len(history) >= 2:
                      # VERİYİ SAKLA - TEKRAR ÇEKİLMEYECEK!
                      self.all_stock_data[hisse_kodu] = {
                          'alis_tarihi': alis_tarihi,
                          'alis_fiyati': alis_fiyati,
                          'history': history,
                          'ticker': ticker_symbol
                      }
                      basarili_sayac += 1
                      print(f"✅ {hisse_kodu}: {len(history)} günlük veri")
                  else:
                      print(f"❌ {hisse_kodu}: NaN temizleme sonrası yetersiz veri")
                      basarisiz_sayac += 1
              else:
                  print(f"❌ {hisse_kodu}: Boş veya yetersiz veri")
                  basarisiz_sayac += 1
                  
              # Rate limiting
              time.sleep(0.1)
              
          except Exception as e:
              print(f"❌ {hisse_kodu}: Hata - {str(e)[:50]}")
              basarisiz_sayac += 1
              continue
      
      self.data_loaded = True
      
      # Veriyi diske kaydet
      try:
          with open("market_cache.pkl", "wb") as f:
              pickle.dump(self.all_stock_data, f)
          print("💾 Veriler bugüne özel diske (market_cache.pkl) kaydedildi!")
      except Exception as e:
          print(f"⚠️ Cache kaydetme hatası: {e}")
          
      print("=" * 60)
      print(f"🎉 VERİ ÇEKME TAMAMLANDI!")
      print(f"✅ Başarılı: {basarili_sayac} hisse")
      print(f"❌ Başarısız: {basarisiz_sayac} hisse")
      print(f"💾 Veriler bellekte saklandı - bugün bir daha çekilmeyecek!")
      print("=" * 60)

    def reset_simulator(self):
      """Simülatörü sıfırla"""
      self.aktif_pozisyonlar = {}
      self.bekleme_listesi = deque()
      self.kacirilan_hisseler = []
      self.tamamlanan_islemler = []
      self.slot_sayisi = 0
      self.sabit_slot_tutari = 0  # SABİT SLOT TUTARI - DEĞİŞMEZ!
      self.kenarda_duran_para = 0  # KAZANILAN PARA BURADA DURUR
      self.gunluk_log = []
      
    def gunluk_cikis_kontrol(self, hisse_kodu, gun_verisi, alis_fiyati, pozisyon, strateji):
    
        gun_yuksek = gun_verisi['High'] 
        gun_dusuk = gun_verisi['Low']
        gun_kapanis = gun_verisi['Close']
        
        # Kar oranları
        yuksek_kar = ((gun_yuksek - alis_fiyati) / alis_fiyati) * 100
        dusuk_kar = ((gun_dusuk - alis_fiyati) / alis_fiyati) * 100
        kapanis_kar = ((gun_kapanis - alis_fiyati) / alis_fiyati) * 100
        
        # 1. SABİT STOP LOSS (HER ZAMAN AKTİF - EN ÖNCELİKLİ)
        if dusuk_kar <= -strateji['stop_loss']:
            return True, -strateji['stop_loss'], "Stop Loss"
        
        # 2. AKILLI TRAİLİNG STOP SİSTEMİ
        if 'trailing_aktif' not in pozisyon:
            pozisyon['trailing_aktif'] = False
            pozisyon['en_yuksek_kapanis'] = alis_fiyati
            pozisyon['trailing_aktif_gun'] = None  # Hangi gün aktif oldu
        
        # 3. TRAİLİNG STOP KONTROLÜ (Önceki günden aktifse)
        if pozisyon.get('trailing_aktif', False):
            # Trailing stop önceki gün aktif olduysa kontrol et
            if pozisyon['trailing_aktif_gun'] != gun_verisi.name.date():
                trailing_stop_fiyati = pozisyon['en_yuksek_kapanis'] * (1 - strateji['trailing_stop'] / 100)
                
                if gun_dusuk <= trailing_stop_fiyati:
                    trailing_kar_orani = ((trailing_stop_fiyati - alis_fiyati) / alis_fiyati) * 100
                    return True, trailing_kar_orani, "Trailing Stop"
        
        # 4. TRAİLİNG STOP AKTİVASYON KONTROLÜ (Günün sonunda)
        if not pozisyon['trailing_aktif']:
            # Henüz trailing aktif değil - kapanış alış fiyatından yüksek mi?
            if gun_kapanis > alis_fiyati:
                # İLK KEZ ALIŞ FİYATININ ÜSTÜNDEKİ KAPANIŞ!
                pozisyon['trailing_aktif'] = True
                pozisyon['en_yuksek_kapanis'] = gun_kapanis
                pozisyon['trailing_aktif_gun'] = gun_verisi.name.date()  # Bu gün aktif oldu
                
                
        else:
            # Trailing stop aktif - en yüksek kapanışı güncelle
            if gun_kapanis > pozisyon['en_yuksek_kapanis']:
                pozisyon['en_yuksek_kapanis'] = gun_kapanis
                
            
        
        # 5. KAR HEDEFİ
        if yuksek_kar >= strateji['kar_hedefi']:
            return True, strateji['kar_hedefi'], "Kar Hedefi"
        
        # 6. ZAMAN LİMİTİ
        gun_sayisi = (gun_verisi.name.date() - pozisyon['alis_tarihi'].date()).days
        if gun_sayisi >= strateji['max_gun']:
            return True, kapanis_kar, "Zaman Limiti"
        
        return False, 0, ""

    def _apply_date_filter(self, date_str):
        # Tarih filtrelemesini simülasyon başlangıcında değerlendirmek için yardımcı if checks
        dt = datetime.strptime(date_str, "%d-%m-%Y")
        if self.baslangic_filtresi:
            b_dt = datetime.strptime(self.baslangic_filtresi, "%Y-%m-%d")
            if dt < b_dt: return False
        if self.bitis_filtresi:
            bit_dt = datetime.strptime(self.bitis_filtresi, "%Y-%m-%d")
            if dt > bit_dt: return False
        return True

    def simulasyon_calistir(self, slot_sayisi, strateji, hedef_kategori=None, kacirma_orani=0.0, seed=42):
      """Ana simülasyon - SADECE ÖNBELLEKTEN VERİ KULLAN!
      Eğer hedef_kategori verilirse SADECE o kategorideki hisseleri işleme alır."""
      
      if seed is not None:
          random.seed(seed)
          
      self.reset_simulator()
      self.slot_sayisi = slot_sayisi
      self.sabit_slot_tutari = self.baslangic_bakiye / slot_sayisi  # SABİT TUTAR!
      
      # VERİ ÇEKME YOK! - Önceden çekilmiş verileri kullan
      if not self.data_loaded:
          print("❌ Önce veriler yüklenmelidir!")
          return None
          
      # Sadece hedef kategoriye ait hisseleri ayıkla
      hisse_verileri = {}
      for k, v in self.all_stock_data.items():
          hisse_kat = signal_categories.get(k, "BİLİNMEYEN")
          tarih_str = v['alis_tarihi'].strftime('%d-%m-%Y')
          
          # Tarih aralığında mı?
          if tarih_str and not self._apply_date_filter(tarih_str):
               continue

          # Eğer hedef kategori belirtilmişse ona göre filtrele
          if hedef_kategori == "TÜM_HİSSELER":
              pass # Hepsini kabul et
          elif hedef_kategori == "GUCLU_VE_GIRIS":
              if hisse_kat not in ["GÜÇLÜ_HACİMLİ", "GİRİŞ"]:
                  continue
          elif hedef_kategori and hisse_kat != hedef_kategori:
              continue
              
          hisse_verileri[k] = v
      
      if not hisse_verileri:
          # Bu kategoride hiç hisse yoksa simülasyon yapma
          return None
      
      # Hisseleri tarihe göre sırala ve bekleme listesine ekle
      sirali_hisseler = sorted(hisse_verileri.items(), 
                             key=lambda x: x[1]['alis_tarihi'])
      
      for hisse_kodu, veri in sirali_hisseler:
          self.bekleme_listesi.append((hisse_kodu, veri))
      
      # Simülasyon tarihleri
      baslangic_tarihi = min([v['alis_tarihi'] for v in hisse_verileri.values()])
      bitis_tarihi = datetime.now()
      
      guncel_tarih = baslangic_tarihi
      
      while guncel_tarih <= bitis_tarihi:
          gunluk_durum = {
              'tarih': guncel_tarih,
              'aktif_pozisyonlar': len(self.aktif_pozisyonlar),
              'bekleme_listesi': len(self.bekleme_listesi),
              'gunun_olaylari': []
          }
          
          # 1. ÇIKIŞ KONTROLLARI (Alış gününden sonraki günden başlasın)
          cikilacak_hisseler = []
          
          for hisse_kodu, pozisyon in list(self.aktif_pozisyonlar.items()):
              if hisse_kodu in hisse_verileri:
                  veri = hisse_verileri[hisse_kodu]
                  history = veri['history']
                  
                  # Alış gününden sonraki günde kontrol başlasın
                  gun_sayisi = (guncel_tarih.date() - pozisyon['alis_tarihi'].date()).days
                  if gun_sayisi < 1:  # Alış günü kontrol yapma
                      continue
                  
                  # O günün verisini bul
                  gun_verisi = None
                  for tarih, gun_data in history.iterrows():
                      if tarih.date() == guncel_tarih.date():
                          gun_verisi = gun_data
                          gun_verisi.name = tarih
                          break
                  
                  if gun_verisi is not None:
                      cikis, kar_orani, sebep = self.gunluk_cikis_kontrol(
                          hisse_kodu, gun_verisi, pozisyon['alis_fiyati'], 
                          pozisyon, strateji)
                      
                      if cikis:
                          cikilacak_hisseler.append((hisse_kodu, kar_orani, guncel_tarih, sebep))
                          gunluk_durum['gunun_olaylari'].append(
                              f"ÇIKIŞ: {hisse_kodu} - {sebep} (%{kar_orani:+.1f})")
          
          # Çıkış işlemlerini gerçekleştir
          for hisse_kodu, kar_orani, cikis_tarihi, sebep in cikilacak_hisseler:
              self.pozisyon_kapat(hisse_kodu, kar_orani, cikis_tarihi, sebep)
          
          # 2. YENİ GİRİŞ KONTROLLARI
          while (len(self.aktif_pozisyonlar) < self.slot_sayisi and 
                 self.bekleme_listesi):
              
              hisse_kodu, veri = self.bekleme_listesi[0]
              
              if veri['alis_tarihi'].date() <= guncel_tarih.date():
                  self.bekleme_listesi.popleft()
                  
                  # 🎯 GERÇEK HAYAT SİMÜLASYONU: Sinyalleri Kaçırma Olasılığı
                  if kacirma_orani > 0 and random.random() < kacirma_orani:
                      self.kacirilan_hisseler.append((hisse_kodu, veri, guncel_tarih))
                      gunluk_durum['gunun_olaylari'].append(
                          f"KAÇIRILDI (STRES TESTİ): {hisse_kodu} - İşleme geç kalındı!")
                      continue
                      
                  self.pozisyon_ac(hisse_kodu, veri)
                  gunluk_durum['gunun_olaylari'].append(
                      f"GİRİŞ: {hisse_kodu} - {veri['alis_fiyati']} TL")
              else:
                  break
          
          # 3. KAÇIRILAN HİSSE KONTROLÜ
          while self.bekleme_listesi:
              hisse_kodu, veri = self.bekleme_listesi[0]
              
              if veri['alis_tarihi'].date() <= guncel_tarih.date():
                  if len(self.aktif_pozisyonlar) >= self.slot_sayisi:
                      self.bekleme_listesi.popleft()
                      self.kacirilan_hisseler.append((hisse_kodu, veri, guncel_tarih))
                      gunluk_durum['gunun_olaylari'].append(
                          f"KAÇIRILDI: {hisse_kodu} - Slot dolu!")
                  else:
                      break
              else:
                  break
          
          if gunluk_durum['gunun_olaylari']:
              self.gunluk_log.append(gunluk_durum)
          
          guncel_tarih += timedelta(days=1)
      
      # Kalan pozisyonları kapat
      for hisse_kodu in list(self.aktif_pozisyonlar.keys()):
          if hisse_kodu in hisse_verileri:
              son_fiyat = hisse_verileri[hisse_kodu]['history'].iloc[-1]['Close']
              alis_fiyati = self.aktif_pozisyonlar[hisse_kodu]['alis_fiyati']
              kar_orani = ((son_fiyat - alis_fiyati) / alis_fiyati) * 100
              self.pozisyon_kapat(hisse_kodu, kar_orani, datetime.now(), "Simülasyon Sonu")
      
      return self.analiz_sonuclari()
  
    def pozisyon_ac(self, hisse_kodu, veri):
      """Yeni pozisyon aç - SABİT TUTAR KULLAN!"""
      if len(self.aktif_pozisyonlar) >= self.slot_sayisi:
          return False
          
      self.aktif_pozisyonlar[hisse_kodu] = {
          'tutar': self.sabit_slot_tutari,  # SABİT TUTAR!
          'alis_tarihi': veri['alis_tarihi'],
          'alis_fiyati': veri['alis_fiyati'],
          'en_yuksek_kar': 0
      }
      return True
  
    def pozisyon_kapat(self, hisse_kodu, kar_orani, cikis_tarihi, sebep):
      """Pozisyon kapat - KAZANCI KENARDA TUT!"""
      if hisse_kodu not in self.aktif_pozisyonlar:
          return
          
      pozisyon = self.aktif_pozisyonlar[hisse_kodu]
      eski_tutar = pozisyon['tutar']
      yeni_tutar = eski_tutar * (1 + kar_orani / 100)
      kar_tl = yeni_tutar - eski_tutar
      
      # KAZANCI KENARDA TUT - SLOT TUTARINA EKLEMEYİN!
      self.kenarda_duran_para += kar_tl
      
      gun_sayisi = (cikis_tarihi - pozisyon['alis_tarihi']).days
      
      # Çıkış fiyatını hesapla
      cikis_fiyati = pozisyon['alis_fiyati'] * (1 + kar_orani / 100)
      
      self.tamamlanan_islemler.append({
          'hisse': hisse_kodu,
          'alis_tarihi': pozisyon['alis_tarihi'],
          'cikis_tarihi': cikis_tarihi,
          'gun_sayisi': gun_sayisi,
          'alis_fiyati': pozisyon['alis_fiyati'],
          'cikis_fiyati': cikis_fiyati,
          'kar_orani': kar_orani,
          'eski_tutar': eski_tutar,
          'yeni_tutar': yeni_tutar,
          'kar_tl': kar_tl,
          'cikis_sebebi': sebep,
          'en_yuksek_kar': pozisyon.get('en_yuksek_kar', 0)
      })
      
      del self.aktif_pozisyonlar[hisse_kodu]
  
    def analiz_sonuclari(self):
      """Detaylı sonuç analizi"""
      # Final sermaye = Aktif pozisyonlardaki para + Kenarda duran para
      aktif_pozisyon_degeri = len(self.aktif_pozisyonlar) * self.sabit_slot_tutari
      bos_slot_degeri = (self.slot_sayisi - len(self.aktif_pozisyonlar)) * self.sabit_slot_tutari
      
      final_sermaye = aktif_pozisyon_degeri + bos_slot_degeri + self.kenarda_duran_para
      toplam_getiri = ((final_sermaye - self.baslangic_bakiye) / self.baslangic_bakiye) * 100
      
      basarili_islem = len([i for i in self.tamamlanan_islemler if i['kar_orani'] > 0])
      toplam_islem = len(self.tamamlanan_islemler)
      
      # Çıkış sebepleri analizi
      cikis_sebepleri = {}
      for islem in self.tamamlanan_islemler:
          sebep = islem['cikis_sebebi']
          if sebep not in cikis_sebepleri:
              cikis_sebepleri[sebep] = {'sayi': 0, 'kar_toplam': 0}
          cikis_sebepleri[sebep]['sayi'] += 1
          cikis_sebepleri[sebep]['kar_toplam'] += islem['kar_tl']
      
      kacirilan_sayisi = len(self.kacirilan_hisseler)
      toplam_hisse = len(portfolio)
      alinan_hisse = toplam_islem
      
      # ── Kategori bazlı analiz ─────────────────────────────────────────────
      kategori_analiz = {}
      for cat_key in list(CATEGORY_LABELS.keys()) + ["BİLİNMEYEN"]:
          cat_islemler = [
              i for i in self.tamamlanan_islemler
              if signal_categories.get(i['hisse'], "BİLİNMEYEN") == cat_key
          ]
          cat_hisseler = [
              h for h in portfolio.keys()
              if signal_categories.get(h, "BİLİNMEYEN") == cat_key
          ]
          cat_basarili = len([i for i in cat_islemler if i['kar_orani'] > 0])
          cat_toplam   = len(cat_islemler)
          cat_kar_tl   = sum(i['kar_tl'] for i in cat_islemler)
          kategori_analiz[cat_key] = {
              'hisse_sayisi': len(cat_hisseler),
              'islem_sayisi': cat_toplam,
              'basarili':     cat_basarili,
              'basari_orani': (cat_basarili / cat_toplam * 100) if cat_toplam > 0 else 0,
              'toplam_kar_tl': cat_kar_tl,
              'ort_kar_orani': (
                  sum(i['kar_orani'] for i in cat_islemler) / cat_toplam
                  if cat_toplam > 0 else 0
              ),
          }
      # ─────────────────────────────────────────────────────────────────────

      return {
          'final_sermaye': final_sermaye,
          'toplam_getiri': toplam_getiri,
          'basarili_islem': basarili_islem,
          'toplam_islem': toplam_islem,
          'toplam_kar_tl': self.kenarda_duran_para,  # TOPLAM KAR = KENARDA DURAN PARA
          'ortalama_kar': self.kenarda_duran_para / toplam_islem if toplam_islem > 0 else 0,
          'basari_orani': (basarili_islem / toplam_islem * 100) if toplam_islem > 0 else 0,
          'islemler': self.tamamlanan_islemler,
          'sabit_slot_tutari': self.sabit_slot_tutari,
          'kenarda_duran_para': self.kenarda_duran_para,
          'cikis_sebepleri': cikis_sebepleri,
          'kacirilan_hisseler': self.kacirilan_hisseler,
          'kacirilan_sayisi': kacirilan_sayisi,
          'toplam_hisse': toplam_hisse,
          'alinan_hisse': alinan_hisse,
          'hisse_yakalama_orani': (alinan_hisse / toplam_hisse * 100) if toplam_hisse > 0 else 0,
          'gunluk_log': self.gunluk_log,
          'kategori_analiz': kategori_analiz,
      }

    def detayli_islem_raporu_yazdir(self, sonuc, strateji, slot_sayisi):
      """Optimal stratejiyle yapılan tüm işlemlerin detaylı raporunu yazdır"""
      print("\n" + "=" * 100)
      print("📊 DETAYLI İŞLEM RAPORU - OPTİMAL STRATEJİ İLE YAPILAN TÜM İŞLEMLER")
      print("=" * 100)
      
      print(f"🎯 Kullanılan Strateji:")
      print(f"   • Kar Hedefi: %{strateji['kar_hedefi']}")
      print(f"   • Stop Loss: %{strateji['stop_loss']}")
      print(f"   • Trailing Stop: %{strateji['trailing_stop']}")
      print(f"   • Zaman Limiti: {strateji['max_gun']} gün")
      print(f"   • Slot Sayısı: {slot_sayisi}")  # DOĞRU SLOT SAYISI!
      print(f"   • Her Slot Tutarı: {self.baslangic_bakiye // slot_sayisi:,} TL")  # DOĞRU HESAPLAMA!
      
      print(f"\n📈 Genel Sonuçlar:")
      print(f"   • Final Sermaye: {sonuc['final_sermaye']:,.0f} TL")
      print(f"   • Toplam Getiri: %{sonuc['toplam_getiri']:+.1f}")
      print(f"   • Toplam İşlem: {sonuc['toplam_islem']}")
      print(f"   • Başarılı İşlem: {sonuc['basarili_islem']} (%{sonuc['basari_orani']:.1f})")
      print(f"   • Toplam Kar: {sonuc['toplam_kar_tl']:,.0f} TL")
      print(f"   • Kenarda Duran Para: {sonuc['kenarda_duran_para']:,.0f} TL")
      
      print("\n" + "=" * 100)
      print("💼 TÜM İŞLEMLERİN DETAYLI LİSTESİ")
      print("=" * 100)
      
      # İşlemleri tarihe göre sırala
      sirali_islemler = sorted(sonuc['islemler'], key=lambda x: x['alis_tarihi'])
      
      for i, islem in enumerate(sirali_islemler, 1):
          kar_emoji = "🟢" if islem['kar_orani'] > 0 else "🔴"
          
          print(f"\n{i:2d}. {kar_emoji} {islem['hisse']}")
          print(f"    📅 Alış: {islem['alis_tarihi'].strftime('%d.%m.%Y')} - "
                f"Satış: {islem['cikis_tarihi'].strftime('%d.%m.%Y')} ({islem['gun_sayisi']} gün)")
          print(f"    💰 Fiyat: {islem['alis_fiyati']:.2f} TL → {islem['cikis_fiyati']:.2f} TL")
          print(f"    📊 Getiri: %{islem['kar_orani']:+.1f} ({islem['kar_tl']:+,.0f} TL)")
          print(f"    🎯 Çıkış Sebebi: {islem['cikis_sebebi']}")
          
          if islem['en_yuksek_kar'] > 0:
              print(f"    📈 En Yüksek Kar: %{islem['en_yuksek_kar']:.1f}")
      
      # Çıkış sebepleri analizi
      print("\n" + "=" * 100)
      print("📊 ÇIKIŞ SEBEPLERİ ANALİZİ")
      print("=" * 100)
      
      for sebep, veri in sonuc['cikis_sebepleri'].items():
          oran = (veri['sayi'] / sonuc['toplam_islem'] * 100) if sonuc['toplam_islem'] > 0 else 0
          print(f"🎯 {sebep}: {veri['sayi']} işlem (%{oran:.1f}) - "
                f"Toplam Kar: {veri['kar_toplam']:+,.0f} TL")
      
      # Kaçırılan hisseler
      if sonuc['kacirilan_hisseler']:
          print("\n" + "=" * 100)
          print("❌ KAÇIRILAN HİSSELER (Slot Dolu Olduğu İçin)")
          print("=" * 100)
          
          for hisse_kodu, veri, tarih in sonuc['kacirilan_hisseler']:
              print(f"• {hisse_kodu}: {veri['alis_tarihi'].strftime('%d.%m.%Y')} - "
                    f"{veri['alis_fiyati']:.2f} TL (Kaçırıldığı tarih: {tarih.strftime('%d.%m.%Y')})")
      
      print("\n" + "=" * 100)
      print("🎯 ÖZET İSTATİSTİKLER")
      print("=" * 100)
      print(f"📊 Toplam Hisse: {sonuc['toplam_hisse']}")
      print(f"✅ Alınan Hisse: {sonuc['alinan_hisse']}")
      print(f"❌ Kaçırılan Hisse: {sonuc['kacirilan_sayisi']}")
      print(f"🎪 Hisse Yakalama Oranı: %{sonuc['hisse_yakalama_orani']:.1f}")
      
      if sonuc['toplam_islem'] > 0:
          ortalama_gun = sum([i['gun_sayisi'] for i in sonuc['islemler']]) / sonuc['toplam_islem']
          print(f"⏱️ Ortalama Elde Tutma Süresi: {ortalama_gun:.1f} gün")
          print(f"💰 Ortalama İşlem Karı: {sonuc['ortalama_kar']:,.0f} TL")

      # ─── KATEGORİ BAZLI ANALİZ ───────────────────────────────────────────
      if signal_categories and 'kategori_analiz' in sonuc:
          print("\n" + "=" * 100)
          print("📊 KATEGORİ BAZLI ANALİZ (Sinyal Tipine Göre Performans)")
          print("=" * 100)
          print(f"{'Kategori':<30} {'Hisse':>6} {'İşlem':>6} {'Başarı%':>8} {'Ort.Kar%':>9} {'Toplam Kar':>14}")
          print("-" * 80)
          for cat_key, label in CATEGORY_LABELS.items():
              d = sonuc['kategori_analiz'].get(cat_key, {})
              if d and d['hisse_sayisi'] > 0:
                  print(
                      f"{label:<30} "
                      f"{d['hisse_sayisi']:>6} "
                      f"{d['islem_sayisi']:>6} "
                      f"{d['basari_orani']:>7.1f}% "
                      f"{d['ort_kar_orani']:>+8.1f}% "
                      f"{d['toplam_kar_tl']:>+14,.0f} TL"
                  )
          print("=" * 100)

def hizli_test():
  """Hızlı test - VERİYİ SADECE BİR KEZ ÇEK!"""
  print("🚀 SÜPER OPTİMİZE HIZLI TEST")
  print("=" * 50)
  
  # Simülatörü oluştur
  simulator = UltimateOptimizedSimulator()
  
  # 1. TÜM VERİLERİ SADECE BİR KEZ ÇEK!
  simulator.load_all_stock_data_once()
  
    # Test edilecek parametreler
  test_kombinasyonlari = [
      {'slot': 5, 'kar': 15, 'stop': 7, 'trail': 5, 'gun': 14},
      {'slot': 6, 'kar': 12, 'stop': 6, 'trail': 4, 'gun': 10},
      {'slot': 7, 'kar': 18, 'stop': 8, 'trail': 6, 'gun': 21},
      {'slot': 8, 'kar': 20, 'stop': 7, 'trail': 5, 'gun': 14},
      {'slot': 10, 'kar': 15, 'stop': 6, 'trail': 4, 'gun': 10}
  ]
  
  sonuclar = []
  
  print(f"\n⚡ SÜPER HIZLI TEST - VERİ İNTERNETTEN ÇEKİLMEYECEK!")
  print("=" * 60)
  
  for i, params in enumerate(test_kombinasyonlari, 1):
      print(f"\n{i}/5 - {params['slot']} slot testi...")
      
      strateji = {
            'kar_hedefi': params['kar'],
            'stop_loss': params['stop'],
            'trailing_stop': params['trail'],
            'max_gun': params['gun']
        }
        
      try:
            # SADECE ÖNBELLEKTEN HESAPLA - İNTERNET YOK!
            sonuc = simulator.simulasyon_calistir(params['slot'], strateji)
            
            if sonuc and sonuc['toplam_islem'] > 0:
                sonuc_detay = {
                    'slot_sayisi': params['slot'],
                    'parametreler': params,
                    'strateji': strateji,
                    'final_sermaye': sonuc['final_sermaye'],
                    'toplam_getiri': sonuc['toplam_getiri'],
                    'basari_orani': sonuc['basari_orani'],
                    'toplam_islem': sonuc['toplam_islem'],
                    'hisse_yakalama_orani': sonuc['hisse_yakalama_orani'],
                    'detay': sonuc
                }
                
                sonuclar.append(sonuc_detay)
                
                print(f"✅ {sonuc['final_sermaye']:,.0f} TL (%{sonuc['toplam_getiri']:+.1f}) - "
                      f"{sonuc['toplam_islem']} işlem")
            else:
                print("❌ Test başarısız")
                
      except Exception as e:
            print(f"❌ Hata: {e}")
            continue
    
  if sonuclar:
        en_iyi = max(sonuclar, key=lambda x: x['final_sermaye'])
        
        print("\n" + "=" * 50)
        print("🏆 EN İYİ SONUÇ")
        print("=" * 50)
        print(f"💰 Final Sermaye: {en_iyi['final_sermaye']:,.0f} TL")
        print(f"📈 Toplam Getiri: %{en_iyi['toplam_getiri']:+.1f}")
        print(f"🎯 Başarı Oranı: %{en_iyi['basari_orani']:.1f}")
        print(f"📊 Toplam İşlem: {en_iyi['toplam_islem']}")
        print(f"🎪 Hisse Yakalama: %{en_iyi['hisse_yakalama_orani']:.1f}")
        
        # Detaylı işlem raporunu yazdır - DOĞRU SLOT SAYISI İLE!
        simulator.detayli_islem_raporu_yazdir(en_iyi['detay'], en_iyi['strateji'], en_iyi['slot_sayisi'])
        
        return en_iyi
  else:
        print("❌ Hiçbir test başarılı olmadı!")
        return None

def optimize_for_category(simulator, kategori, slot_sayilari, kar_hedefleri, stop_losslar, trailing_stops, zaman_limitleri):
    """Belirli bir kategori için tüm kombinasyonları dener ve en iyiyi döner"""
    print(f"\n" + "=" * 80)
    print(f"🔍 KATEGORİ OPTİMİZASYONU: {CATEGORY_LABELS.get(kategori, kategori)}")
    print("=" * 80)
    
    tum_sonuclar = []
    test_sayaci = 0
    
    # Hızlı kontrol: Bu kategoride hisse var mı?
    if kategori == "TÜM_HİSSELER":
        kategori_hisse_sayisi = len(simulator.all_stock_data)
    elif kategori == "GUCLU_VE_GIRIS":
        kategori_hisse_sayisi = sum(1 for k in simulator.all_stock_data.keys() if signal_categories.get(k, "BİLİNMEYEN") in ["GÜÇLÜ_HACİMLİ", "GİRİŞ"])
    else:
        kategori_hisse_sayisi = sum(1 for k in simulator.all_stock_data.keys() if signal_categories.get(k, "BİLİNMEYEN") == kategori)
        
    if kategori_hisse_sayisi == 0:
        print(f"⚠️ Bu kategoride ({kategori}) hiç hisse bulunamadığı için test atlanıyor.")
        return None
        
    print(f"📊 {kategori} kategorisinde {kategori_hisse_sayisi} hisse test ediliyor...")
    baslangic_zamani = time.time()
    
    for slot in slot_sayilari:
        for kar_hedefi in kar_hedefleri:
            for stop_loss in stop_losslar:
                for trailing_stop in trailing_stops:
                    for max_gun in zaman_limitleri:
                        # Mantıklı kombinasyon kontrolü
                        if trailing_stop >= stop_loss:
                            continue
                        if kar_hedefi <= stop_loss:
                            continue
                        
                        test_sayaci += 1
                        strateji = {
                            'kar_hedefi': kar_hedefi,
                            'stop_loss': stop_loss,
                            'trailing_stop': trailing_stop,
                            'max_gun': max_gun
                        }
                        
                        try:
                            # Sadece ilgili kategori için simüle et
                            sonuc = simulator.simulasyon_calistir(slot, strateji, hedef_kategori=kategori)
                            
                            if sonuc and sonuc['toplam_islem'] > 0:
                                sonuc_detay = {
                                    'kategori': kategori,
                                    'slot_sayisi': slot,
                                    'kar_hedefi': kar_hedefi,
                                    'stop_loss': stop_loss,
                                    'trailing_stop': trailing_stop,
                                    'max_gun': max_gun,
                                    'strateji': strateji,
                                    'final_sermaye': sonuc['final_sermaye'],
                                    'toplam_getiri': sonuc['toplam_getiri'],
                                    'basari_orani': sonuc['basari_orani'],
                                    'toplam_islem': sonuc['toplam_islem'],
                                    'basarili_islem': sonuc['basarili_islem'],
                                    'hisse_yakalama_orani': sonuc['hisse_yakalama_orani'],
                                    'alinan_hisse': sonuc['alinan_hisse'],
                                    'toplam_hisse': sonuc['toplam_hisse'],
                                    'kacirilan_sayisi': sonuc['kacirilan_sayisi'],
                                    'detay': sonuc
                                }
                                tum_sonuclar.append(sonuc_detay)
                                
                            if test_sayaci % 100 == 0:
                                gecen_sure = time.time() - baslangic_zamani
                                print(f"   ⚡ {kategori}: {test_sayaci:,} test tamamlandı...")
                                
                        except Exception as e:
                            continue
                            
    if not tum_sonuclar:
        print(f"❌ {kategori} kategorisi için hiçbir test başarılı olmadı!")
        return None
        
    # Kategori için en iyi sonucu bul
    en_iyi = max(tum_sonuclar, key=lambda x: x['final_sermaye'])
    toplam_sure = time.time() - baslangic_zamani
    
    print(f"\n🏆 {CATEGORY_LABELS.get(kategori, kategori)} İÇİN OPTİMAL STRATEJİ!")
    print(f"⚡ {test_sayaci:,} test {toplam_sure:.1f} saniyede tamamlandı.")
    print(f"💰 {kategori} Final Sermaye: {en_iyi['final_sermaye']:,.0f} TL (%{en_iyi['toplam_getiri']:+.1f})")
    print(f"🎯 Parametreler: {en_iyi['slot_sayisi']} Slot | %{en_iyi['kar_hedefi']} Kar | %{en_iyi['stop_loss']} Stop | %{en_iyi['trailing_stop']} Trail | {en_iyi['max_gun']} Gün")
    print(f"📊 İşlem İstatistiği: {en_iyi['basarili_islem']}/{en_iyi['toplam_islem']} Başarılı İşlem (%{en_iyi['basari_orani']:.1f} Başarı)")
    print(f"🎪 Hisse Alma Oranı: Kategoriye ait toplam {en_iyi['toplam_hisse']} hisseden {en_iyi['alinan_hisse']} tanesi işleme girebildi (%{en_iyi['hisse_yakalama_orani']:.1f})")
    
    # GERÇEK HAYAT STRES TESTLERİ
    print("\n" + "-" * 80)
    print("🌪️ GERÇEK HAYAT STRES TESTLERİ (10 Farklı Rastgele Kaçırma Senaryosu)")
    print("-" * 80)
    stres_sonuclari = []
    
    # 10 Farklı Senaryo, rastgele oranlar (%15 ile %45 arası) ve rastgele seedler
    senaryolar = []
    for s_idx in range(1, 11):
        oran = random.uniform(0.15, 0.45) # %15 ile %45 arası rastgele kaçırma
        rnd_seed = random.randint(1, 999999)
        senaryolar.append((oran, rnd_seed))
    
    for i, (oran, rnd_seed) in enumerate(senaryolar, 1):
        stres_sonuc = simulator.simulasyon_calistir(
            en_iyi['slot_sayisi'], en_iyi['strateji'], 
            hedef_kategori=kategori, kacirma_orani=oran, seed=rnd_seed
        )
        if stres_sonuc:
            print(f"📉 Senaryo {i:2d} (Sinyallerin ~%{int(oran*100):2d}'si Kaçırıldı): "
                  f"💰 Final Sermaye: {stres_sonuc['final_sermaye']:,.0f} TL (%{stres_sonuc['toplam_getiri']:+.1f}) "
                  f"| 🎯 İşlem Sayısı: {stres_sonuc['toplam_islem']}")
            stres_sonuclari.append(stres_sonuc)
            
    en_iyi['stres_sonuclari'] = stres_sonuclari
    
    return en_iyi

def ultimate_strateji_optimizasyonu(custom_param_grid=None, start_date=None, end_date=None):
    """SÜPER OPTİMİZE - Kategori bazlı parametreleri test et"""
    
    print("🚀 ULTIMATE KATEGORİ BAZLI STRATEJİ TESTI")
    print("=" * 80)
    print("⚡ VERİ SADECE BİR KEZ ÇEKİLECEK - SONRA KATEGORİLER İÇİN SÜPER HIZLI!")
    print("=" * 80)
    
    # Simülatörü oluştur
    simulator = UltimateOptimizedSimulator()
    if start_date: simulator.baslangic_filtresi = start_date
    if end_date: simulator.bitis_filtresi = end_date
    
    # 1. TÜM VERİLERİ SADECE BİR KEZ ÇEK!
    print("📊 1. AŞAMA: TÜM HİSSE VERİLERİNİ ÇEK")
    simulator.load_all_stock_data_once()
    
    print("\n📊 2. AŞAMA: KATEGORİ BAZLI OPTİMİZASYON")
    print("=" * 60)
    
    if custom_param_grid:
        slot_sayilari = custom_param_grid.get('slots', [6, 7])
        kar_hedefleri = custom_param_grid.get('targets', [10, 12, 14, 24, 34, 39])
        stop_losslar = custom_param_grid.get('stops', [8, 10, 15])
        trailing_stops = custom_param_grid.get('trails', [5, 6, 8])
        zaman_limitleri = custom_param_grid.get('days', [5, 7, 9, 10, 14])
    else:
        # Çok daha geniş test kombinasyonları (On binlerce ihtimali dener)
        slot_sayilari = [6, 7]
        kar_hedefleri = [10, 12, 14, 24 ,34 ,39]
        stop_losslar = [ 8, 10, 15]
        trailing_stops = [ 5, 6, 8]
        zaman_limitleri = [5, 7, 9, 10, 14]
    
    # Tüm kategorileri tespit et (Mevcut hisselerin ait olduğu eşsiz kategoriler)
    aktif_kategoriler = set()
    for hisse in simulator.all_stock_data.keys():
        kat = signal_categories.get(hisse, "BİLİNMEYEN")
        aktif_kategoriler.add(kat)
        
    en_iyi_kategori_sonuclari = {}
    
    aktif_kategoriler_listesi = sorted(list(aktif_kategoriler))
    aktif_kategoriler_listesi.append("GUCLU_VE_GIRIS") # Güçlü ve Giriş İkilisi
    aktif_kategoriler_listesi.append("TÜM_HİSSELER") # En sona Genel Kategoriyi Ekle
    
    # Her aktif kategori için ayrı ayrı optimizasyon çalıştır
    for kategori in aktif_kategoriler_listesi:
        en_iyi_kat = optimize_for_category(
            simulator, kategori, 
            slot_sayilari, kar_hedefleri, stop_losslar, trailing_stops, zaman_limitleri
        )
        if en_iyi_kat:
            en_iyi_kategori_sonuclari[kategori] = en_iyi_kat
            
    # Tüm işlemler bitince genel tabloyu/raporu bas
    print("\n\n" + "*" * 100)
    print("🌟🌟🌟 KATEGORİ BAZLI OPTİMİZASYON SONUÇLARI (ÖZET) 🌟🌟🌟")
    print("*" * 100)
    
    if not en_iyi_kategori_sonuclari:
         print("❌ Hiçbir kategori için başarılı strateji bulunamadı.")
         return None
         
    for kategori, sonuc in en_iyi_kategori_sonuclari.items():
         label = CATEGORY_LABELS.get(kategori, kategori)
         print(f"\n👉 {label}")
         print(f"   🦄 İdeal Sermaye (Hiç kaçırmadan): {sonuc['final_sermaye']:,.0f} TL (%{sonuc['toplam_getiri']:+.1f}) | 🎯 Başarı: %{sonuc['basari_orani']:.1f} ({sonuc['basarili_islem']}/{sonuc['toplam_islem']})")
         
         if "stres_sonuclari" in sonuc and sonuc["stres_sonuclari"]:
             stres = sonuc['stres_sonuclari']
             min_stres = min([s['final_sermaye'] for s in stres])
             avg_stres = sum([s['final_sermaye'] for s in stres]) / len(stres)
             print(f"   🌪️ GERÇEK HAYAT (10 Stresli Senaryo Ortalaması): {avg_stres:,.0f} TL")
             print(f"   🛑 EN KÖTÜ İHTİMAL (En şanssız olunan senaryo): {min_stres:,.0f} TL")
             
         print(f"   🎪 Yakalanan: {sonuc['alinan_hisse']}/{sonuc['toplam_hisse']} Hisse (%{sonuc['hisse_yakalama_orani']:.1f})")
         print(f"   ⚙️ Strateji: {sonuc['slot_sayisi']} Slot | %{sonuc['kar_hedefi']} Kar | %{sonuc['stop_loss']} Stop | %{sonuc['trailing_stop']} Trail | {sonuc['max_gun']} Gün")
         
    # =========================================================================
    # 🤖 YAPAY ZEKA SİSTEM KARARI VE TAVSİYESİ 🤖
    # =========================================================================
    print("\n" + "=" * 100)
    print("🤖 YAPAY ZEKA SİSTEM KARARI VE KESİN TAVSİYESİ 🤖")
    print("=" * 100)
    
    # En kârlı kategoriyi Senaryo Testlerindeki "EN KÖTÜ İHTİMAL"e (Minimax) göre bul
    def en_kotu_senaryo_getirisi(kategori_sonuc):
        stres_list = kategori_sonuc.get("stres_sonuclari", [])
        if not stres_list:
            return kategori_sonuc['final_sermaye']
        return min(s['final_sermaye'] for s in stres_list)
        
    en_karlisi = max(en_iyi_kategori_sonuclari.items(), key=lambda x: en_kotu_senaryo_getirisi(x[1]))
    sanpiyon_kategori = en_karlisi[0]
    sampiyon_sonuc = en_karlisi[1]
    
    tavsiye_baslik = CATEGORY_LABELS.get(sanpiyon_kategori, sanpiyon_kategori)
    
    print(f"💡 EN MANTIKLI KARAR:")
    if sanpiyon_kategori == "TÜM_HİSSELER":
        print(f"Bütün ihtimaller hesaplandı. Sinyal başlığı (Güçlü Hacimli, Giriş vb.) FARK ETMEKSİZİN")
        print(f"Telegram'dan gelen TÜM HİSSELERE ayrım yapmadan girmek en yüksek kârı getiriyor.")
    elif sanpiyon_kategori == "GUCLU_VE_GIRIS":
        print(f"Bütün ihtimaller hesaplandı. Programımız SADECE 'Güçlü Hacimli' ve 'Giriş Sinyali'")
        print(f"olan ikiliye girmeyi, diğer düşük hacimli vs. sinyalleri pas geçmeyi tavsiye ediyor.")
    else:
        print(f"Bütün ihtimaller hesaplandı. Diğer tüm sinyalleri görmezden gelip")
        print(f"SADECE '{tavsiye_baslik}' sinyali gelen hisselere yatırım yapmak matematiğe göre en yüksek kârı garanti ediyor.")
        
    print(f"\n⚙️ UYGULANACAK KESİN STRATEJİ KURALI:")
    print(f"   • Portföy Bakiyeni {sampiyon_sonuc['slot_sayisi']} eşit parçaya (slota) böl.")
    print(f"   • Hedef Kar: %{sampiyon_sonuc['kar_hedefi']}")
    print(f"   • Stop Loss (Zarar Kes): %{sampiyon_sonuc['stop_loss']}")
    print(f"   • Trailing Stop (Takip Eden): %{sampiyon_sonuc['trailing_stop']}")
    print(f"   • Maksimum Bekleme Süresi: {sampiyon_sonuc['max_gun']} Gün")
    
    print(f"\n💴 İZLEYECEĞİN YOL VE BEKLENTİ (100.000 TL Sermaye İçin):")
    print(f"   🌟 İdeal Durum (Hiçbir Sinyali Kaçırmazsan): {sampiyon_sonuc['final_sermaye']:,.0f} TL (%{sampiyon_sonuc['toplam_getiri']:+.1f})")
    
    if "stres_sonuclari" in sampiyon_sonuc and sampiyon_sonuc["stres_sonuclari"]:
        stres = sampiyon_sonuc['stres_sonuclari']
        min_stres = min([s['final_sermaye'] for s in stres])
        avg_stres = sum([s['final_sermaye'] for s in stres]) / len(stres)
        print(f"   🌪️ Gerçek Hayat (10 Farklı Paralel Evren Ortalaması): {avg_stres:,.0f} TL")
        print(f"   🛑 En Kötü İhtimal (En çok yanlış hissenin denk geldiği talihsiz senaryo): {min_stres:,.0f} TL")
        
    print("=" * 100 + "\n")
    
    return en_iyi_kategori_sonuclari

# Ana fonksiyon
if __name__ == "__main__":
    print("Hangi testi çalıştırmak istiyorsunuz?")
    print("1. Hızlı Test (5 kombinasyon)")
    print("2. Tam Optimizasyon (Tüm kombinasyonlar)")
    
    secim = input("Seçiminizi yapın (1 veya 2): ")
    
    if secim == "1":
        en_optimal = hizli_test()
    else:
        en_optimal = ultimate_strateji_optimizasyonu()
    
    if en_optimal:
        if secim == "1":
            print(f"\n🎯 SONUÇ ÖZET:")
            print(f"💰 100.000 TL → {en_optimal['final_sermaye']:,.0f} TL")
            print(f"📈 Getiri: %{en_optimal['toplam_getiri']:+.1f}")
            print(f"🎪 {en_optimal['slot_sayisi']} slot ile {en_optimal['toplam_islem']} işlem")
            print(f"✅ %{en_optimal['basari_orani']:.1f} başarı oranı")
            print(f"🚀 SÜPER OPTİMİZE - Veriler sadece bir kez çekildi!")
        else:
            print(f"\n✅ Kategori bazlı optimizasyon tamamlandı!")
            print(f"Yukarıdaki tabloda hangi sinyal grubu için hangi stratejinin en kârlı olduğunu inceleyebilirsiniz.")
