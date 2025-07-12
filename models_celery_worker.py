from models_celery_config import celery_app
from celery import Task
import threading
import os
import joblib
import numpy as np
import yfinance as yf
import pandas_ta as ta
from tensorflow.keras.models import load_model

class ModelManager:
    _instances = {}
    _lock = threading.Lock()

    @classmethod
    def get_model(cls, ticker):
        if ticker not in cls._instances:
            with cls._lock:
                if ticker not in cls._instances:
                    print(f"Cargando modelo para {ticker}...")
                    model_path = f"models/{ticker}_modelo.h5"
                    scaler_path = f"models/{ticker}_scaler.save"
                    features_path = f"models/{ticker}_features.save"

                    if not all(os.path.exists(p) for p in [model_path, scaler_path, features_path]):
                        raise FileNotFoundError(f"No se encontraron archivos de modelo para {ticker}")

                    cls._instances[ticker] = {
                        'model': load_model(model_path),
                        'scaler': joblib.load(scaler_path),
                        'features': joblib.load(features_path)
                    }
                    print(f"Modelo {ticker} cargado correctamente")
        return cls._instances[ticker]

class PredictionTask(Task):
    def __init__(self):
        super().__init__()
        self.model_manager = ModelManager()

@celery_app.task(base=PredictionTask, bind=True)
def process_prediction(self, ticker):
    try:
        print(f"\nProcesando predicción para {ticker}")
        
        # Obtener modelo y recursos
        model_resources = self.model_manager.get_model(ticker)
        model = model_resources['model']
        scaler = model_resources['scaler']
        features = model_resources['features']

        # Descargar y procesar datos
        window_size = 60
        df = yf.download(ticker, period="1y", interval="1d", multi_level_index=False)
        
        if df is None or df.empty:
            return {'error': f"No se pudieron obtener datos del ticker {ticker}"}

        # Calcular indicadores
        df["rsi"] = ta.rsi(df["Close"], length=14)
        df["ema_20"] = ta.ema(df["Close"], length=20)
        df["ema_50"] = ta.ema(df["Close"], length=50)
        df["ema_100"] = ta.ema(df["Close"], length=100)

        macd = ta.macd(df["Close"])
        df["macd"] = macd["MACD_12_26_9"]
        df["macd_signal"] = macd["MACDs_12_26_9"]
        df["macd_hist"] = macd["MACDh_12_26_9"]

        stochrsi = ta.stochrsi(df["Close"])
        df["stochrsi_k"] = stochrsi["STOCHRSIk_14_14_3_3"]
        df["stochrsi_d"] = stochrsi["STOCHRSId_14_14_3_3"]

        df["adx"] = ta.adx(df["High"], df["Low"], df["Close"])["ADX_14"]

        bbands = ta.bbands(df["Close"], length=20, std=2)
        # Imprimir las columnas disponibles para debug
        print("Columnas en bbands:", bbands.columns)
        # Usar los nombres correctos
        df["bbands_upper"] = bbands.iloc[:, 0]  # Primera columna (Upper)
        df["bbands_middle"] = bbands.iloc[:, 1]  # Segunda columna (Middle)
        df["bbands_lower"] = bbands.iloc[:, 2]   # Tercera columna (Lower)

        df["obv"] = ta.obv(df["Close"], df["Volume"])
        df["volume_20sma"] = df["Volume"].rolling(window=20).mean()

        df.dropna(inplace=True)

        if len(df) < window_size:
            return {'error': f"No hay suficientes datos para {ticker}"}

        recent_data = df[features].tail(window_size)
        scaled_recent = scaler.transform(recent_data)
        X_pred = np.expand_dims(scaled_recent, axis=0)

        pred_scaled = model.predict(X_pred)
        dummy = np.zeros((1, len(features)))
        dummy[0, 0] = pred_scaled[0, 0]
        inv_pred = scaler.inverse_transform(dummy)
        pred_price = float(inv_pred[0, 0])

        print(f"Predicción completada para {ticker}: {pred_price}")
        return {
            'ticker': ticker,
            'predicted_price': pred_price
        }

    except Exception as e:
        print(f"Error en predicción: {str(e)}")
        return {'error': str(e)}