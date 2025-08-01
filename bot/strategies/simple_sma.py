"""Einfache SMA‑Strategie.

Diese Strategie vergleicht einen kurzen und einen langen gleitenden
Durchschnitt. Wenn der kurze Durchschnitt den langen von unten nach oben
kreuzt, wird ein Kaufsignal ('BUY') generiert. Wenn der kurze den langen von
oben nach unten kreuzt, wird ein Verkaufssignal ('SELL') generiert. Ansonsten
wird 'HOLD' zurückgegeben.
"""

from __future__ import annotations

from typing import List

from ..strategy import Strategy


class SimpleSMAStrategy(Strategy):
    def __init__(self, short_window: int = 7, long_window: int = 25) -> None:
        super().__init__(short_window=short_window, long_window=long_window)
        if long_window <= short_window:
            raise ValueError("long_window muss größer sein als short_window")
        self.short_window = short_window
        self.long_window = long_window
        # Speichern des letzten Zustands (ob kurz über lang war), um Kreuzungen zu erkennen
        self._last_cross_state: int | None = None

    def _moving_average(self, data: List[float], window: int) -> float:
        return sum(data[-window:]) / window

    def generate_signal(self, prices: List[float]) -> str:
        if len(prices) < self.long_window:
            # Nicht genügend Daten für beide Durchschnitte
            return "HOLD"

        short_ma = self._moving_average(prices, self.short_window)
        long_ma = self._moving_average(prices, self.long_window)

        # Setze aktuellen Zustand: 1 wenn kurz > lang, -1 wenn kurz < lang
        current_state = 1 if short_ma > long_ma else -1
        signal = "HOLD"
        if self._last_cross_state is not None:
            if current_state > self._last_cross_state:
                # Kreuzt von unten nach oben -> Kauf
                signal = "BUY"
            elif current_state < self._last_cross_state:
                # Kreuzt von oben nach unten -> Verkauf
                signal = "SELL"
        # Aktualisiere den Zustand für das nächste Mal
        self._last_cross_state = current_state
        return signal