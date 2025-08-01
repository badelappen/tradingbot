# TradingBot Web GUI

Dieses Repository enthält eine einfache FastAPI‑basierte Weboberfläche für einen
Trading‑Bot. Die Kernlogik des Bots ist modular aufgebaut und kann mit
verschiedenen Strategien erweitert werden. Die Anwendung bietet Endpunkte zum
Starten und Stoppen des Bots sowie zum Abrufen des aktuellen Status und zum
Durchführen eines Backtests. Die gesamte Anwendung läuft in einem Docker
Container und kann daher schnell auf jeder Infrastruktur bereitgestellt
werden.

## Aufbau

```
tradingbot_project/
├── app/                # FastAPI‑Webserver
│   └── main.py         # Startpunkt für die API
├── bot/                # Kernlogik des Trading‑Bots
│   ├── __init__.py
│   ├── bot.py          # TradingBot-Klasse zum Starten/Stoppen des Bots
│   ├── data_handler.py # Datenbeschaffung via Binance API
│   ├── strategy.py     # Basisklasse für Strategien
│   └── strategies/     # Konkrete Strategien
│       └── simple_sma.py
├── config/
│   └── config.yaml     # Beispielkonfiguration
├── requirements.txt    # Python-Abhängigkeiten
├── Dockerfile          # Docker-Build-Datei
└── README.md           # Dieses Dokument
```

## Schnellstart

1. **Konfiguration anpassen** – Ersetze in `config/config.yaml` die Platzhalter
   `YOUR_BINANCE_API_KEY` und `YOUR_BINANCE_API_SECRET` durch deine persönlichen
   API‑Schlüssel. Passe bei Bedarf die Handelsgröße und Strategieparameter an.
2. **Container bauen** – Führe folgenden Befehl im Wurzelverzeichnis aus:

   ```bash
   docker build -t tradingbot .
   ```

3. **Container starten** – Starte den Bot via Docker, wobei du die Konfigurationsdatei
   und ggf. Umgebungsvariablen einbindest:

   ```bash
   docker run -e BINANCE_API_KEY=<dein_key> -e BINANCE_API_SECRET=<dein_secret> -p 8000:8000 tradingbot
   ```

   Die API ist anschließend unter `http://localhost:8000` erreichbar.

4. **Interaktion** – Verwende ein Tool wie `curl` oder einen Browser, um
   folgende Endpunkte aufzurufen:

   - `POST /start` – Startet den Trading‑Bot.
   - `POST /stop` – Stoppt den Trading‑Bot.
   - `GET /status` – Gibt den aktuellen Status des Bots zurück.
   - `POST /backtest` – Führt einen Backtest auf historischen Daten durch (nur
     exemplarisch implementiert).

Die Implementierung ist als Grundlage gedacht und soll auf deine eigenen
Trading‑Strategien angepasst werden. Beachte, dass der Handel mit
Kryptowährungen mit erheblichen Risiken verbunden ist – setze nur Kapital ein,
dessen Verlust du verkraften kannst.