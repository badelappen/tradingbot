"""FastAPI-Webserver für den Trading‑Bot.

Dieser Service stellt eine einfache REST-API bereit, mit der der Bot gestartet
und gestoppt werden kann. Außerdem lässt sich ein Backtest auslösen und der
aktuelle Status abfragen. Die API nutzt den `TradingBot` aus dem
``bot``-Modul.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from bot.bot import TradingBot


app = FastAPI(title="Crypto Trading Bot API", version="0.1.0")

# Initialisiere den Trading‑Bot beim Start der API
bot_instance = TradingBot(config_path="config/config.yaml")


class BacktestRequest(BaseModel):
    num_candles: int = 500


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "TradingBot API running"}


@app.get("/status")
def get_status() -> dict:
    return bot_instance.status()


@app.post("/start")
def start_bot() -> dict[str, str]:
    if bot_instance.status().get("running"):
        raise HTTPException(status_code=400, detail="Bot already running")
    bot_instance.start()
    return {"message": "Bot started"}


@app.post("/stop")
def stop_bot() -> dict[str, str]:
    if not bot_instance.status().get("running"):
        raise HTTPException(status_code=400, detail="Bot not running")
    bot_instance.stop()
    return {"message": "Bot stopped"}


@app.post("/backtest")
def run_backtest(request: BacktestRequest) -> dict:
    result = bot_instance.backtest(num_candles=request.num_candles)
    return result