# Projektplan: Raspberry-Pi-Telemetriesystem

## 1. Ziel

Entwicklung eines modularen Telemetriesystems für einen **Raspberry Pi Zero 2 W**. Der Pi erfasst Sensordaten von:

* **Barometer** → Luftdruck
* **Temperatursensor** → Temperatur
* **IMU** → Beschleunigung und Gyroskopdaten
* **GPS** → zunächst nur als vorbereitetes, leeres Datenfeld; tatsächlicher Sensor wird später integriert

Die Daten werden:

1. **lokal auf dem Raspberry Pi gespeichert**
2. parallel über ein **eigenes WLAN des Pi** an einen Laptop übertragen
3. auf dem Laptop empfangen, gespeichert und live visualisiert.

Das System soll zunächst vollständig als **Labor-/Prüfstandssystem** entwickelt und mit simulierten Daten getestet werden.

---

## 2. Technologie

### Raspberry Pi

* Raspberry Pi Zero 2 W
* Raspberry Pi OS
* Python 3
* WLAN Access Point
* lokale Datenspeicherung

### Python

Verwendete Komponenten nach Bedarf:

* `numpy` – numerische Verarbeitung
* `matplotlib` – Visualisierung
* Sensorbibliotheken entsprechend der tatsächlich verwendeten Sensoren
* `socket` – Netzwerkkommunikation
* `csv` oder `sqlite3` – Speicherung
* `json` – Telemetrie-Datenformat

Keine unnötigen Frameworks verwenden.

---

## 3. Sensor-Datenmodell

Das gemeinsame Datenformat soll von Anfang an **GPS-Felder enthalten**, auch wenn noch kein GPS angeschlossen ist.

Beispiel:

```python
data = {
    "timestamp": ...,

    "pressure": ...,
    "temperature": ...,

    "ax": ...,
    "ay": ...,
    "az": ...,

    "gx": ...,
    "gy": ...,
    "gz": ...,

    "gps": {
        "latitude": None,
        "longitude": None,
        "altitude": None,
        "speed": None,
        "satellites": None
    }
}
```

Solange kein GPS vorhanden ist, bleiben die GPS-Werte beispielsweise `None`.

**Wichtig:** Die restliche Software soll dadurch nicht angepasst werden müssen. Sobald das GPS später integriert wird, soll lediglich das entsprechende Sensor-Modul die bisher leeren Felder mit echten Werten füllen.

---

# 4. Systemarchitektur

```text
                     ┌─────────────────┐
                     │    Sensoren     │
                     │                 │
                     │ Barometer       │
                     │ Temperatur      │
                     │ IMU             │
                     │ GPS (später)    │
                     └────────┬────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Raspberry Pi     │
                    │ Zero 2 W         │
                    │                  │
                    │ Sensorerfassung  │
                    │ Zeitstempel      │
                    │ lokale Speicherung│
                    └───────┬──────────┘
                            │
                 ┌──────────┴──────────┐
                 │                     │
                 ▼                     ▼
          lokale Speicherung       WLAN
                 │                     │
                 │                     ▼
                 │              ┌─────────────┐
                 │              │   Laptop    │
                 │              │             │
                 │              │ Empfang     │
                 │              │ Speicherung │
                 │              │ Visualisierung│
                 │              └─────────────┘
                 ▼
              CSV/SQLite
```

Der Pi soll **nicht vom WLAN abhängig sein**. Die lokale Speicherung läuft unabhängig von der Telemetrie weiter.

---

# 5. Aufteilung auf drei Personen

## Person 1 – Sensorik

Entwicklung des Raspberry-Pi-Programms für die Datenerfassung.

### Aufgaben

* Barometer initialisieren und auslesen
* Temperatursensor auslesen
* IMU initialisieren und auslesen
* Beschleunigung X/Y/Z
* Gyroskop X/Y/Z
* GPS-Schnittstelle als **leeres Modul vorbereiten**
* Messwerte in ein einheitliches Format bringen
* Zeitstempel erzeugen
* Messfrequenz kontrollieren
* fehlerhafte Sensorwerte erkennen
* lokale Speicherung implementieren

Das GPS-Modul soll beispielsweise bereits eine definierte Schnittstelle besitzen:

```python
def read_gps():
    return {
        "latitude": None,
        "longitude": None,
        "altitude": None,
        "speed": None,
        "satellites": None
    }
```

Später kann diese Funktion durch die tatsächliche GPS-Anbindung ersetzt werden.

---

## Person 2 – Netzwerk und Telemetrie

Entwicklung der Kommunikation zwischen Pi und Laptop.

### Aufgaben

* Pi als WLAN-Access-Point betreiben
* Server auf dem Pi
* Client auf dem Laptop
* Datenpakete übertragen
* Verbindungsabbrüche erkennen
* Wiederverbindung ermöglichen
* Übertragungsfehler behandeln
* Telemetrie von lokaler Datenspeicherung entkoppeln

Bevorzugt zunächst eine einfache **TCP-Verbindung**.

```text
Pi
 │
 │ JSON-Daten
 ▼
TCP-Verbindung
 │
 ▼
Laptop
```

Die GPS-Felder werden bereits mit übertragen, auch wenn sie zunächst `null` enthalten.

---

## Person 3 – Laptop und Visualisierung

Entwicklung der Anwendung auf dem Laptop.

### Aufgaben

* Telemetriedaten empfangen
* Daten validieren
* Live-Anzeige
* Live-Plots
* lokale Speicherung
* spätere Datenanalyse

Die Visualisierung soll bereits Platz für GPS-Daten vorsehen, beispielsweise:

```text
GPS
Latitude:   N/A
Longitude:  N/A
Altitude:   N/A
Speed:      N/A
Satellites: N/A
```

Nach Integration des GPS müssen keine grundlegenden Änderungen an der Laptop-Anwendung notwendig sein.

---

# 6. Gemeinsame Datenschnittstelle

Alle drei Teile müssen dasselbe Datenformat verwenden.

Beispiel:

```json
{
    "timestamp": 12.481,
    "pressure": 1008.3,
    "temperature": 27.4,
    "ax": 0.12,
    "ay": -0.04,
    "az": 9.71,
    "gx": 0.03,
    "gy": -0.01,
    "gz": 0.07,
    "gps": {
        "latitude": null,
        "longitude": null,
        "altitude": null,
        "speed": null,
        "satellites": null
    }
}
```

Die Schnittstelle soll zentral definiert werden, damit nicht jede Person eigene Feldnamen oder Einheiten verwendet.

---

# 7. Entwicklungsreihenfolge

### Phase 1 – Simulation

Noch keine echte Hardware voraussetzen.

```text
Simulierte Sensordaten
        ↓
Datenformat
        ↓
Netzwerk
        ↓
Laptop
        ↓
Visualisierung
```

GPS wird ebenfalls simuliert bzw. mit `None` dargestellt.

### Phase 2 – Sensoren

Simulierte Daten durch echte Sensordaten ersetzen:

* Barometer
* Temperatur
* IMU

Testen:

* korrekte Einheiten
* Zeitstempel
* Messfrequenz
* Ausreißer
* Speicherung

### Phase 3 – WLAN

Pi als eigener Access Point.

```text
Pi ───── WLAN ───── Laptop
```

Internet darf nicht erforderlich sein.

### Phase 4 – Integration

Alle Komponenten zusammenführen:

```text
Sensoren
   ↓
Raspberry Pi
   ├── lokale Speicherung
   └── Telemetrie
           ↓
         WLAN
           ↓
        Laptop
           ↓
      Visualisierung
```

### Phase 5 – GPS

GPS-Hardware anschließen und ausschließlich das vorbereitete GPS-Modul ersetzen bzw. erweitern.

Die vorhandene Datenstruktur, Telemetrie und Visualisierung sollen weiter funktionieren.

### Phase 6 – Robustheit

Gezielt testen:

* WLAN wird unterbrochen
* Laptop wird getrennt
* Sensor liefert ungültige Werte
* GPS ist nicht verfügbar
* Pi startet neu
* hohe Datenrate
* längere Messungen

Die lokale Speicherung auf dem Pi muss unabhängig von der Funkverbindung funktionieren.

---

# 8. Anforderungen an den Codex-Agenten

Der Code soll:

* modular aufgebaut sein
* klar zwischen Hardware, Datenmodell, Speicherung und Netzwerk trennen
* möglichst wenig externe Abhängigkeiten verwenden
* Logging statt unstrukturierter `print()`-Ausgaben verwenden
* Konfiguration nicht unnötig im Code verteilen
* mit simulierten Sensordaten testbar sein
* saubere Schnittstellen zwischen den drei Komponenten besitzen
* GPS von Anfang an im Datenmodell berücksichtigen
* GPS-Ausfall bzw. noch nicht vorhandene GPS-Hardware korrekt behandeln
* späteres Hinzufügen des GPS ohne grundlegenden Umbau ermöglichen
* zunächst **keine raketenspezifische Flugsteuerungs- oder Auslöseautomatik** implementieren

Priorität:

```text
Zuverlässige Datenerfassung
        >
Lokale Datenspeicherung
        >
Zuverlässige Telemetrie
        >
Live-Visualisierung
        >
GPS-Integration
        >
Komplexere Auswertung
```

Die Software soll zunächst als eigenständiges **Sensor- und Telemetriesystem** funktionieren.
