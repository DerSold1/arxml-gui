# Entwicklung

Setup, Konventionen, Tests sowie der aktuelle Stand bekannter Einschränkungen und die Roadmap.

[← zurück zur README](../README.md)

---

## Inhalt

- [Entwicklungsumgebung](#entwicklungsumgebung)
- [Code-Stil](#code-stil)
- [Tests](#tests)
- [GUI ohne Bildschirm starten](#gui-ohne-bildschirm-starten)
- [Abhängigkeiten](#abhängigkeiten)
- [Bekannte Einschränkungen](#bekannte-einschränkungen)
- [Roadmap](#roadmap)
- [Beiträge](#beiträge)

---

## Entwicklungsumgebung

```bash
git clone https://github.com/DerSold1/arxml-gui.git
cd arxml-gui
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Empfohlen für VS Code: Python-Extension, als Interpreter `.venv` wählen, `black` als Formatter.
`.venv/` und `logs/` sind in `.gitignore` eingetragen.

## Code-Stil

- **Formatierung:** `black .`
- **Linting:** `pylint arxml models utils gui`
- **Typ-Hinweise** an allen öffentlichen Methoden (bestehender Stil: `typing.Dict`, `List`, `Optional`)
- **Docstrings** einzeilig in Englisch, wie im bestehenden Code
- **Datenmodell** als `@dataclass`, Aufzählungen als `Enum` mit sprechenden String-Werten
- **Keine GUI-Imports** in `models/`, `arxml/` und `utils/` – diese Schichten müssen ohne Tkinter laufen

## Tests

Das Verzeichnis `tests/` ist angelegt, enthält aber noch keine Tests (`pytest` meldet
„no tests ran“). Vorschlag für den Einstieg – Generator, Validator und Konverter lassen sich
ohne GUI testen:

```python
# tests/test_generator.py
import xml.etree.ElementTree as ET

from models.interface import InterfaceCollection
from models.types import InterfaceElement, InterfaceType
from arxml.generator import ARXMLGenerator
from arxml.validators import ARXMLValidator

NS = {"ar": "http://autosar.org/schema/r4.0"}


def _projekt():
    c = InterfaceCollection(project_name="Test", vendor_name="Vendor")
    c.add_interface(InterfaceElement(
        element_type=InterfaceType.PORT, name="P1",
        content={"port_type": "provide",
                 "signals": [{"name": "S1", "data_type": "uint8", "unit": "", "description": ""}]},
    ))
    return c


def test_generate_ist_wohlgeformt_und_enthaelt_paket():
    root = ET.fromstring(ARXMLGenerator().generate(_projekt()))
    assert root.find("ar:AR-PACKAGES/ar:AR-PACKAGE/ar:SHORT-NAME", NS).text == "Test"


def test_port_signal_wird_ausgegeben():
    root = ET.fromstring(ARXMLGenerator().generate(_projekt()))
    namen = [e.text for e in root.iterfind(".//ar:ELEMENT-DATA-PROTOTYPE/ar:SHORT-NAME", NS)]
    assert namen == ["S1"]


def test_validator_meldet_ungueltigen_namen():
    c = _projekt()
    c.add_interface(InterfaceElement(element_type=InterfaceType.SIGNAL, name="1abc"))
    ok, befunde = ARXMLValidator().validate_collection(c)
    assert not ok
    assert any(b.element == "1abc" for b in befunde)
```

Ausführen:

```bash
pytest                         # alle Tests
pytest --cov=arxml --cov=models --cov=utils   # mit Abdeckung
```

`pytest` aus dem Projektverzeichnis starten. Da `tests/` ein Paket ist (`__init__.py`),
nimmt pytest das Projektverzeichnis automatisch in den Suchpfad auf – die obigen Tests laufen
so ohne weitere Konfiguration und ohne Tkinter.

## GUI ohne Bildschirm starten

Für CI oder Bildschirmfotos unter Linux:

```bash
sudo apt install xvfb python3-tk
xvfb-run -a python main.py
```

## Abhängigkeiten

Zur Laufzeit nutzt die Anwendung **ausschließlich die Python-Standardbibliothek**
(`tkinter`, `xml.etree`, `xml.dom.minidom`, `json`, `csv`, `pickle`, `logging`, `dataclasses`).

`requirements.txt` enthält zusätzlich Pakete, die derzeit **nicht importiert** werden:

| Paket | vorgesehen für |
|---|---|
| `lxml` | XSD-Validierung der ARXML |
| `xmltodict` | einfacher ARXML-Import |
| `pandas`, `numpy`, `openpyxl` | Parameter-Import/-Export aus Excel |
| `pydantic`, `jsonschema` | typisiertes Modell, Prüfung der Projektdatei |
| `python-dotenv`, `colorama` | Konfiguration, farbige Konsolenausgabe |
| `pytest`, `pytest-cov`, `black`, `pylint` | Entwicklung |

Mittelfristig sinnvoll: Aufteilung in `requirements.txt` (Laufzeit) und
`requirements-dev.txt` (Entwicklung).

## Bekannte Einschränkungen

Stand: Commit `998a9fc`. Alle Punkte wurden am Code bzw. durch Ausführen nachvollzogen.

### GUI

| # | Bereich | Verhalten |
|---|---|---|
| G1 | Reiter *Interfaces*, Menü *Edit → Add Interface* | Schaltflächen sind Platzhalter (`MainWindow._add_interface` usw.). `InterfaceEditor` aus `gui/interface_editor.py` ist fertig, wird aber nicht verwendet. Die Liste im Reiter wird nie befüllt. |
| G2 | `InterfaceDialog` | Wechsel des Typs auf `PORT` oder `SERVICE` wirft `IndexError` in `_on_type_changed()` (die Suche nach der „+ Add“-Schaltfläche über `winfo_children()` geht eine Ebene zu tief). Nach Wechsel auf `SIGNAL` wird der Bereich *Operations/Signals* ausgeblendet und beim Zurückwechseln nicht wieder eingeblendet. |
| G3 | `OperationDialog` → `ParameterDialog` | liefert Parameter als `dict`; der Generator erwartet `Parameter`-Objekte ⇒ `AttributeError` beim Generieren. Beim Bearbeiten einer Operation werden vorhandene Ein-/Ausgabeparameter nicht geladen. |
| G4 | *File → Open Project* | liest JSON, übernimmt es aber nicht ins Projekt; meldet trotzdem „Project loaded successfully“. |
| G5 | *File → Import ARXML* | ruft den Parser nicht auf, meldet trotzdem Erfolg. |
| G6 | *Create/Update Project* | legt immer ein neues, leeres Projekt an – vorhandene Interfaces gehen verloren. |
| G7 | Reiter *Parameters*, *Tools → Export Parameters* | Platzhalter; *Load Template* zeigt nur die Namen der Vorlagen. |
| G8 | Fehler beim Speichern/Exportieren | kein Fehlerdialog, nur Konsolenausgabe. |
| G9 | Validierung | bei reinen Warnungen wird „Project is valid!“ ohne die Warnungen angezeigt. |

### ARXML / Parser

| # | Bereich | Verhalten |
|---|---|---|
| A1 | Generator | Ausgabe ist nicht AUTOSAR-schemakonform, siehe [ARXML-Ausgabe](arxml-ausgabe.md#abweichungen-zu-autosar-r4-und-zielbild). |
| A2 | Generator | gewählte AUTOSAR-Version und *Namespace* haben keinen Einfluss auf die Ausgabe. |
| A3 | Generator | `init_value` von Port-Signalen und Parameter an System-Signalen werden nicht ausgegeben; `CONSTRAINTS` wird immer geschrieben, auch leer. |
| A4 | Parser | findet keine Elemente in Dateien mit `xmlns` (also weder echte AUTOSAR-Dateien noch die eigene Ausgabe). Übernimmt nur Namen und Beschreibungen. |

### Modell / Dateien

| # | Bereich | Verhalten |
|---|---|---|
| M1 | Projekt-JSON | Interface-Parameter, globale Parameter und Version werden nicht gespeichert; `Parameter`-Objekte in Operationen sind nicht serialisierbar. |
| M2 | Parameter-JSON | beim Einlesen gehen `value_type` und `metadata` verloren. |
| M3 | Validator | prüft keine Namen von Operationen/Signalen und keine Parameter in Operationen. |
| M4 | Logger | schreibt nach `logs/` im jeweiligen Arbeitsverzeichnis, nicht im Programmverzeichnis. |

## Roadmap

Reihenfolge nach Nutzen für den GUI-Workflow:

1. **Interface-Editor einbinden** (G1, G2, G6)
   `InterfaceEditor` im Reiter *Interfaces* verwenden, `_on_type_changed()` reparieren,
   *Create/Update Project* nur Stammdaten aktualisieren lassen.
2. **Parameter durchgängig als Objekte** (G3, M1)
   `ParameterDialog` liefert `Parameter`; Converter serialisiert/deserialisiert `Parameter`
   und `ParameterConstraint`.
3. **Projekt laden** (G4)
   `Converters.dict_to_interface_collection()` ergänzen und in *Open Project* nutzen.
4. **Parameter-Reiter und Export** (G7, M2)
5. **Fehlerdialoge und Logging** (G8, G9, M4)
   Ausnahmen loggen statt `print()`, Warnungen bei gültigem Projekt anzeigen.
6. **Schemakonforme ARXML** (A1–A3)
   Umstellung gemäß [Zielbild](arxml-ausgabe.md#abweichungen-zu-autosar-r4-und-zielbild),
   XSD-Prüfung mit `lxml` in den Tests.
7. **ARXML-Import** (A4, G5)
   Namespace-fähiger Parser, Round-Trip-Test Generator → Parser.
8. **Tests und CI**
   pytest-Suite, GitHub Actions mit `black --check`, `pylint`, `pytest` und `xvfb` für GUI-Smoke-Tests.

## Beiträge

1. Issue anlegen oder bestehendes kommentieren
2. Branch `feature/<kurzname>` bzw. `fix/<kurzname>`
3. Änderungen mit Tests, `black` und `pylint` sauber
4. Pull Request mit Bezug auf die Nummer aus [Bekannte Einschränkungen](#bekannte-einschränkungen), falls zutreffend
5. Dokumentation in `docs/` mitpflegen – insbesondere Statustabelle in der README und diese Liste
