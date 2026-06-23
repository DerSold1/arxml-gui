# ARXML GUI Generator

Eine Python-GUI zum Erstellen von ARXML-Dateien (AUTOSAR) mit parametrisierbaren Schnittstellenbeschreibungen.

## Features

- 🎨 Benutzerfreundliche Tkinter-Oberfläche
- 📋 Schnittstellenbeschreibungen (Services, Ports, Signals, Operations)
- ⚙️ Parameter-Templates mit vollständiger Parametrisierung
- 📝 Live-ARXML-Vorschau
- 💾 Projekt-Verwaltung (Speichern/Laden)
- 📊 Import/Export von Parametern (CSV, JSON, XML)
- ✅ AUTOSAR 4.2/4.3 Compliance
- 🔍 Validierung und Fehlerprüfung

## Installation

```bash
git clone https://github.com/DerSold1/arxml-gui.git
cd arxml-gui
pip install -r requirements.txt
```

## Verwendung

```bash
python main.py
```

## Projektstruktur

```
arxml-gui/
├── main.py                    # Entry Point
├── gui/
│   ├── __init__.py
│   ├── main_window.py         # Hauptfenster
│   ├── interface_editor.py    # Interface-Editor
│   ├── parameter_panel.py     # Parameter-Management
│   └── dialogs.py             # Dialoge für Eingaben
├── arxml/
│   ├── __init__.py
│   ├── generator.py           # ARXML-Generator
│   ├── parser.py              # ARXML-Parser
│   └── validators.py          # Validierung
├── models/
│   ├── __init__.py
│   ├── interface.py           # Interface-Datenmodelle
│   ├── parameter.py           # Parameter-Datenmodelle
│   └── types.py               # Type-Definitionen
├── utils/
│   ├── __init__.py
│   ├── file_handler.py        # Datei-Operationen
│   ├── converters.py          # Format-Konvertierung
│   └── logger.py              # Logging
├── templates/                 # ARXML-Templates
├── requirements.txt
└── tests/
    └── test_generator.py
```

## AUTOSAR-Versionen

Unterstützte Versionen: AUTOSAR 4.2, 4.3, 4.4

## Lizenz

MIT
