# Architektur

Überblick über Schichten, Module und Datenfluss des ARXML GUI Generators.

[← zurück zur README](../README.md)

---

## Schichten

```mermaid
flowchart TB
    subgraph GUI["gui/ – Präsentation (Tkinter)"]
        MW[MainWindow]
        IE[InterfaceEditor]
        DLG[InterfaceDialog · OperationDialog · SignalDialog · ParameterDialog]
    end
    subgraph CORE["arxml/ – Verarbeitung"]
        GEN[ARXMLGenerator]
        PAR[ARXMLParser]
        VAL[ARXMLValidator]
    end
    subgraph MODEL["models/ – Datenmodell"]
        COL[InterfaceCollection]
        TYP[types.py: Enums & Dataclasses]
        TM[TemplateManager]
        PM[ParameterManager]
    end
    subgraph UTIL["utils/ – Infrastruktur"]
        FH[FileHandler]
        CV[Converters]
        LOG[Logger]
    end

    MW --> GEN & VAL & COL & TM & PM & FH & CV & LOG
    MW -.noch nicht eingebunden.-> IE
    IE --> DLG
    IE --> COL
    GEN & PAR & VAL --> COL
    COL --> TYP
    CV --> COL & PM
```

Abhängigkeiten zeigen nur nach unten: `models/` kennt weder GUI noch ARXML, `arxml/` kennt
keine GUI. Dadurch lassen sich Generator, Validator und Modell ohne Tkinter verwenden und
testen (siehe [Python-API](python-api.md)).

## Module

| Modul | Verantwortung | Wichtige Klassen |
|---|---|---|
| `main.py` | Start, Tk-Root, Hauptschleife, Logging bei Start/Ende | `main()` |
| `gui/main_window.py` | Menüs, Reiter, Statusleiste, verbindet GUI mit Modell und Generator | `MainWindow` |
| `gui/interface_editor.py` | Interface-Liste als `ttk.Frame` mit Hinzufügen/Bearbeiten/Löschen | `InterfaceEditor` |
| `gui/dialogs.py` | modale Eingabedialoge | `InterfaceDialog`, `OperationDialog`, `SignalDialog`, `ParameterDialog` |
| `arxml/generator.py` | Modell → XML-Text bzw. Datei | `ARXMLGenerator` |
| `arxml/parser.py` | XML → Modell | `ARXMLParser` |
| `arxml/validators.py` | Regeln für Namen, Metadaten, Constraints | `ARXMLValidator`, `ValidationError` |
| `models/types.py` | Enums und Basis-Dataclasses | `InterfaceElement`, `Parameter`, `ParameterConstraint`, … |
| `models/interface.py` | Projektcontainer und Vorlagen | `InterfaceCollection`, `TemplateManager`, `ParameterTemplate`, `InterfaceTemplate` |
| `models/parameter.py` | Parameterwerte in Gruppen, Einzelwert-Prüfungen | `ParameterManager`, `ParameterGroup`, `ParameterValue`, `ParameterValidator` |
| `utils/file_handler.py` | JSON/CSV/Pickle-I/O, Dateihelfer | `FileHandler` (statisch) |
| `utils/converters.py` | Modell ↔ dict/JSON/CSV-Zeilen | `Converters` (statisch) |
| `utils/logger.py` | Singleton-Logger (Konsole + Datei) | `Logger`, `get_logger()` |

## Datenmodell

```mermaid
classDiagram
    class InterfaceCollection {
        project_name: str
        vendor_name: str
        autosar_version: str
        namespace: str
        interfaces: Dict
        global_parameters: List
        data_type_definitions: Dict
        add_interface()
        remove_interface()
        get_interface()
        list_interfaces()
    }
    class InterfaceElement {
        element_type: InterfaceType
        name: str
        description: str
        version: str
        parameters: List
        content: Dict
    }
    class Parameter {
        name: str
        param_type: ParameterType
        description: str
        constraint: ParameterConstraint
        metadata: Dict
        category: str
    }
    class ParameterConstraint {
        min_value
        max_value
        allowed_values
        regex_pattern
        required: bool
        default_value
    }
    InterfaceCollection "1" o-- "*" InterfaceElement
    InterfaceCollection "1" o-- "*" Parameter : global_parameters
    InterfaceElement "1" o-- "*" Parameter
    Parameter "1" *-- "1" ParameterConstraint
```

### Bewusste Designentscheidung: generisches `content`

`InterfaceElement` ist für alle Interface-Typen gleich; typspezifische Daten (Service-Typ,
Operationen, Port-Typ, Signale, Datentyp) liegen als Dictionary in `content`. Vorteile:
einfache JSON-Serialisierung und ein einziger Code-Pfad in Dialogen und Konvertern.
Nachteil: keine Typprüfung durch Python – Tippfehler in Schlüsseln (z. B. `"signal"` statt
`"signals"`) werden still ignoriert.

Die spezifischeren Dataclasses `ServiceInterface`, `PortInterface`, `Signal` und `Operation`
in `types.py` sind definiert, werden aktuell aber nirgends verwendet. Bei der Umstellung auf
schemakonforme ARXML bietet es sich an, auf diese (oder pydantic-Modelle) umzusteigen.

### Zwei Parametermodelle

| Modell | Zweck | Verwendet von |
|---|---|---|
| `models.types.Parameter` | **Definition** eines Parameters (Typ, Grenzen, Default) | Interfaces, Operationen, Vorlagen, Generator, Validator |
| `models.parameter.ParameterValue` | konkreter **Wert** eines Parameters in einer Gruppe | `ParameterManager`, Konverter für CSV/JSON |

Beide sind derzeit nicht miteinander verknüpft.

## Ablauf: ARXML exportieren

```mermaid
sequenceDiagram
    actor U as Nutzer
    participant MW as MainWindow
    participant COL as InterfaceCollection
    participant GEN as ARXMLGenerator
    participant FS as Dateisystem

    U->>MW: Project → Create/Update Project
    MW->>COL: neue InterfaceCollection(Name, Vendor, Version, Namespace)
    U->>MW: File → Export as ARXML
    MW->>U: Dateidialog (.arxml)
    U-->>MW: Pfad
    MW->>GEN: save_to_file(collection, pfad)
    GEN->>GEN: generate() → ElementTree → minidom
    GEN->>FS: schreiben (UTF-8)
    GEN-->>MW: True / False
    MW->>U: Statusleiste + „ARXML file exported successfully“
```

## Fehlerbehandlung und Logging

- `FileHandler`, `ARXMLGenerator.save_to_file` und `ARXMLParser` fangen Ausnahmen ab, geben
  sie mit `print()` auf der Konsole aus und liefern `False`/`None`. Die GUI prüft den
  Rückgabewert, zeigt im Fehlerfall aber (noch) keinen Dialog.
- Der `Logger` ist ein Singleton um das Standard-`logging`. Er legt beim ersten Aufruf
  `logs/` im Arbeitsverzeichnis an. Ausnahmen in den Modulen werden bisher nicht über den
  Logger, sondern per `print()` gemeldet.

## Erweiterungspunkte

| Vorhaben | Ansatzpunkt |
|---|---|
| neuer Interface-Typ | `InterfaceType` erweitern, `ARXMLGenerator.generate()` + eigene `_add_…`-Methode, Parser `_parse_element()`, Typauswahl in `InterfaceDialog` |
| neue Validierungsregel | Methode in `ARXMLValidator`, Aufruf in `_validate_interface()` bzw. `_validate_parameter()` |
| neue Parameter-Vorlage | `TemplateManager._initialize_builtin_templates()` oder zur Laufzeit `add_parameter_template()` |
| neues Exportformat | statische Methode in `Converters`, Schreiben über `FileHandler`, Menüeintrag in `MainWindow._create_menu()` |
| Mehrsprachige GUI | Beschriftungen in `gui/` zentralisieren (derzeit fest auf Englisch) |
