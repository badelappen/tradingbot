"""Implementiert die TradingBot‑Klasse.

Der Bot verwaltet den gesamten Handelsprozess: er beschafft Daten über
``DataHandler``, wendet eine Strategie an, führt Trades aus (hier nur
simuliert) und bietet Methoden zum Starten/Stoppen. Die eigentliche
Orderausführung müsste im Produktiveinsatz mit der Binance API verbunden
werden; in diesem Beispiel wird sie als Backtest/Paper‑Trading simuliert.
"""

from __future__ import annotations

import asyncio
import threading
import time
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

import yaml  # type: ignore

from .data_handler import DataHandler
from .strategy import Strategy
from .strategies.simple_sma import SimpleSMAStrategy


@dataclass
class Trade:
    """Repräsentiert einen simulierten Trade für Backtests."""
    timestamp: float
    action: str  # 'BUY' oder 'SELL'
    price: float
    quantity: float


class TradingBot:
    def __init__(self, config_path: str = "config/config.yaml") -> None:
        # Lade Konfiguration
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        api_key = config.get("api_key")
        api_secret = config.get("api_secret")
        self.symbol: str = config.get("symbol", "BTCUSDT")
        self.interval: str = config.get("interval", "1m")
        self.base_asset_amount: float = float(config.get("base_asset_amount", 0.001))
        risk_cfg = config.get("risk", {})
        self.stop_loss_pct: float = float(risk_cfg.get("stop_loss_pct", 0.02))
        self.take_profit_pct: float = float(risk_cfg.get("take_profit_pct", 0.03))
        self.max_position_size: float = float(risk_cfg.get("max_position_size", 0.1))
        strategy_cfg = config.get("strategy", {})
        strategy_type = strategy_cfg.get("type", "sma")
        # Initialisiere Strategie
        if strategy_type == "sma":
            self.strategy: Strategy = SimpleSMAStrategy(
                short_window=int(strategy_cfg.get("short_window", 7)),
                long_window=int(strategy_cfg.get("long_window", 25)),
            )
        else:
            raise ValueError(f"Unbekannter Strategie-Typ: {strategy_type}")
        # Datenhandler initialisieren
        self.data_handler = DataHandler(api_key=api_key, api_secret=api_secret)
        # Laufstatus
        self._running = False
        self._thread: Optional[threading.Thread] = None
        # Aktueller Trade-Status
        self.position: Optional[Trade] = None
        self.trade_history: List[Trade] = []

    def start(self) -> None:
        """Startet den Bot in einem separaten Thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stoppt den Bot."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        self._thread = None

    def status(self) -> Dict[str, Any]:
        """Gibt den aktuellen Status des Bots zurück."""
        return {
            "running": self._running,
            "open_position": self.position.price if self.position else None,
            "trade_count": len(self.trade_history),
        }

    def _run_loop(self) -> None:
        """Interne Schleife für den Livebetrieb."""
        prices: List[float] = []
        while self._running:
            # Neue Daten abrufen
            price = self.data_handler.get_current_price(self.symbol)
            prices.append(price)
            # Limitieren der gespeicherten Preise für Ressourceneffizienz
            if len(prices) > max(1000, 2 * getattr(self.strategy, 'long_window', 25)):
                prices = prices[-max(1000, 2 * getattr(self.strategy, 'long_window', 25)) :]
            # Handelsentscheidung treffen
            signal = self.strategy.generate_signal(prices)
            # Simulierte Orderausführung
            if signal == "BUY" and self.position is None:
                # Eröffne Position
                quantity = self.base_asset_amount
                self.position = Trade(time.time(), "BUY", price, quantity)
                self.trade_history.append(self.position)
            elif signal == "SELL" and self.position is not None:
                # Schließe Position
                sell_trade = Trade(time.time(), "SELL", price, self.position.quantity)
                self.trade_history.append(sell_trade)
                self.position = None
            # Füge Stop-Loss/Take-Profit hinzu
            if self.position:
                entry_price = self.position.price
                if price <= entry_price * (1 - self.stop_loss_pct):
                    # Stop-Loss auslösen
                    sell_trade = Trade(time.time(), "SELL", price, self.position.quantity)
                    self.trade_history.append(sell_trade)
                    self.position = None
                elif price >= entry_price * (1 + self.take_profit_pct):
                    # Take-Profit auslösen
                    sell_trade = Trade(time.time(), "SELL", price, self.position.quantity)
                    self.trade_history.append(sell_trade)
                    self.position = None
            # Warte ein wenig, um API-Limitierung zu vermeiden
            time.sleep(5)

    def backtest(self, num_candles: int = 500) -> Dict[str, Any]:
        """Führt einen einfachen Backtest durch und gibt Performance-Kennzahlen aus."""
        prices = self.data_handler.get_recent_prices(self.symbol, self.interval, limit=num_candles)
        position: Optional[Trade] = None
        profit = 0.0
        trades = []
        for idx, price in enumerate(prices):
            window_prices = prices[: idx + 1]
            signal = self.strategy.generate_signal(window_prices)
            if signal == "BUY" and position is None:
                position = Trade(idx, "BUY", price, self.base_asset_amount)
                trades.append(position)
            elif signal == "SELL" and position is not None:
                # Realisiere Gewinn
                trade = Trade(idx, "SELL", price, position.quantity)
                trades.append(trade)
                profit += (price - position.price) * position.quantity
                position = None
            # Stop-Loss/Take-Profit
            if position:
                entry = position.price
                if price <= entry * (1 - self.stop_loss_pct):
                    trade = Trade(idx, "SELL", price, position.quantity)
                    trades.append(trade)
                    profit += (price - entry) * position.quantity
                    position = None
                elif price >= entry * (1 + self.take_profit_pct):
                    trade = Trade(idx, "SELL", price, position.quantity)
                    trades.append(trade)
                    profit += (price - entry) * position.quantity
                    position = None
        return {
            "profit": profit,
            "trade_count": len(trades),
            "trades": trades,
        }