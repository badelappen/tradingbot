"""Datenbeschaffung für den Trading‑Bot.

Dieses Modul kapselt die Kommunikation mit der Binance API. Für einfaches
Testing ohne echten API‑Key kann der DataHandler im `paper`‑Modus
initialisiert werden; in diesem Fall werden zufällige Daten generiert.
"""

from __future__ import annotations

import os
import random
from datetime import datetime
from typing import List, Dict, Any

try:
    from binance.client import Client  # type: ignore[import]
except ImportError:
    Client = None  # type: ignore


class DataHandler:
    """Beschafft Marktdaten von Binance oder generiert Testdaten."""

    def __init__(self, api_key: str | None = None, api_secret: str | None = None) -> None:
        self.api_key = api_key or os.getenv("BINANCE_API_KEY")
        self.api_secret = api_secret or os.getenv("BINANCE_API_SECRET")
        self.client: Any | None = None
        if self.api_key and self.api_secret and Client is not None:
            # Initialisiere echten Binance Client
            self.client = Client(self.api_key, self.api_secret)

    def get_recent_prices(self, symbol: str, interval: str, limit: int = 50) -> List[float]:
        """Ruft die letzten Schlusskurse für ein Symbol ab.

        Falls kein API‑Key gesetzt ist, werden zufällige Preise generiert.

        :param symbol: Handels­paar (z. B. 'BTCUSDT')
        :param interval: Zeitintervall (z. B. '1m', '5m', '1h')
        :param limit: Anzahl der zurückzugebenden Kerzen
        :return: Liste von Schlusskursen
        """
        if self.client:
            # hole Klines via Binance API
            try:
                klines = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
                closes = [float(candle[4]) for candle in klines]
                return closes
            except Exception as err:
                # Fallback: generiere Zufallsdaten
                print(f"Fehler beim Abrufen der Binance-Daten: {err}. Verwende Zufallsdaten.")
        # Generiere Pseudodaten für Tests
        base_price = random.uniform(10000, 40000)
        return [base_price + random.gauss(0, base_price * 0.01) for _ in range(limit)]

    def get_current_price(self, symbol: str) -> float:
        """Gibt den aktuellen Preis für das Symbol zurück (letzter Schlusskurs)."""
        prices = self.get_recent_prices(symbol, interval="1m", limit=1)
        return prices[-1] if prices else 0.0