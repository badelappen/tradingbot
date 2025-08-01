"""Abstrakte Strategie‑Klasse für den Trading‑Bot.

Strategien implementieren die Methode `generate_signal`, die anhand der
übergebenen Preisdaten entscheidet, ob eine Position eröffnet, geschlossen
oder gehalten werden soll. Signale werden als Strings 'BUY', 'SELL' oder
'HOLD' repräsentiert.
"""

from __future__ import annotations

from typing import List


class Strategy:
    """Basisklasse für eine Handelsstrategie."""

    def __init__(self, **params: float) -> None:
        self.params = params

    def generate_signal(self, prices: List[float]) -> str:
        """Erzeugt ein Handelssignal.

        :param prices: Liste historischer Schlusskurse (jüngster Preis am Ende)
        :return: 'BUY', 'SELL' oder 'HOLD'
        """
        raise NotImplementedError("generate_signal muss in Unterklassen implementiert werden")