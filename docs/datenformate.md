# Datenformate

Neben ARXML ([ARXML-Ausgabe](arxml-ausgabe.md)) verwendet das Tool JSON für Projektdateien
sowie JSON und CSV für Parameter. Alle Dateien werden in **UTF-8** geschrieben; JSON mit
2 Leerzeichen Einrückung und ohne ASCII-Maskierung (Umlaute bleiben lesbar).

[← zurück zur README](../README.md)

---

## Projektdatei

Erzeugt über **File → Save Project** bzw. `Converters.interface_collection_to_dict()`.

### Aufbau

```json
{
  "project_name": "BmsDemo",
  "vendor_name": "MHP",
  "autosar_version": "4.3",
  "namespace": "/Interfaces",
  "interfaces": {
    "BatteryTemp": {
      "type": "port",
      "name": "BatteryTemp",
      "description": "Batterietemperatur",
      "content": {
        "port_type": "provide",
        "signals": [
          {
            "name": "CellTemp",
            "data_type": "int16",
            "unit": "degC",
            "description": "Zelltemperatur"
          }
        ]
      }
    },
    "VehicleSpeed": {
      "type": "signal",
      "name": "VehicleSpeed",
      "description": "Fahrzeuggeschwindigkeit",
      "content": {
        "data_type": "uint16",
        "init_value": 0
      }
    }
  }
}
```

### Felder

| Feld | Typ | Beschreibung |
|---|---|---|
| `project_name` | string | Projektname |
| `vendor_name` | string | Hersteller/Vendor |
| `autosar_version` | string | `"4.2"`, `"4.3"` oder `"4.4"` |
| `namespace` | string | Paketpfad, z. B. `"/Interfaces"` |
| `interfaces` | object | Schlüssel = Interface-Name |
| `interfaces.*.type` | string | `"service"`, `"port"`, `"signal"` (Wert von `InterfaceType`) |
| `interfaces.*.name` | string | Interface-Name (identisch zum Schlüssel) |
| `interfaces.*.description` | string | Beschreibung |
| `interfaces.*.content` | object | typabhängiger Inhalt, 1:1 wie im Modell – siehe [Python-API](python-api.md#interfaces-anlegen) |

### Was nicht gespeichert wird

- `InterfaceElement.parameters` (Parameter am Interface)
- `InterfaceElement.version`
- `InterfaceCollection.global_parameters` und `data_type_definitions`

### Einschränkungen

- **Laden:** Es gibt noch keine Rückwandlung JSON → `InterfaceCollection`. *Open Project*
  liest die Datei, übernimmt den Inhalt aber nicht. Für eigene Skripte lässt sich die
  Rückwandlung einfach selbst schreiben:

  ```python
  from models.interface import InterfaceCollection
  from models.types import InterfaceElement, InterfaceType
  from utils.file_handler import FileHandler

  data = FileHandler.load_json("BmsDemo.json")
  projekt = InterfaceCollection(
      project_name=data["project_name"],
      vendor_name=data.get("vendor_name", "VendorName"),
      autosar_version=data.get("autosar_version", "4.3"),
      namespace=data.get("namespace", "/Interfaces"),
  )
  for i in data.get("interfaces", {}).values():
      projekt.add_interface(InterfaceElement(
          element_type=InterfaceType(i["type"]),
          name=i["name"],
          description=i.get("description", ""),
          content=i.get("content", {}),
      ))
  ```

- **Parameter-Objekte in Operationen:** Enthält `content["operations"]` Ein- oder
  Ausgabeparameter als `Parameter`-Objekte, schlägt das Speichern mit
  `Object of type Parameter is not JSON serializable` fehl. *Save Project* meldet in diesem
  Fall nichts in der GUI; die Fehlermeldung erscheint nur in der Konsole.

## Parameter-Export

Grundlage ist das Gruppenmodell aus `models/parameter.py`
(`ParameterManager` → `ParameterGroup` → `ParameterValue`).
Die Menüpunkte *Tools → Export Parameters (CSV/JSON)* sind noch Platzhalter; die Konverter
sind aber vorhanden und per Skript nutzbar.

### JSON

`Converters.parameters_to_json(manager.groups)`:

```json
{
  "Timing": {
    "name": "Timing",
    "description": "Zeitparameter",
    "parameters": {
      "cycle_time": {
        "name": "cycle_time",
        "value": 10,
        "value_type": "static",
        "unit": "ms",
        "metadata": {}
      },
      "timeout": {
        "name": "timeout",
        "value": "2*cycle_time",
        "value_type": "computed",
        "unit": "ms",
        "metadata": {"k": 1}
      }
    },
    "parent_group": null
  }
}
```

Einlesen mit `Converters.json_string_to_parameters(text)` bzw. `dict_to_parameters(data)`.
Dabei werden derzeit nur `name`, `value` und `unit` übernommen – `value_type` fällt auf
`static` zurück, `metadata` geht verloren.

### CSV

`Converters.parameters_to_csv_rows(manager.groups)` + `FileHandler.save_csv(...)`:

```csv
group,parameter_name,value,type,unit
Timing,cycle_time,10,static,ms
Timing,timeout,2*cycle_time,computed,ms
```

| Spalte | Inhalt |
|---|---|
| `group` | Gruppenname |
| `parameter_name` | Parametername |
| `value` | Wert (als Text) |
| `type` | `value_type` (`static`, `dynamic`, `computed`, `reference`) |
| `unit` | Einheit |

Trennzeichen ist das Komma. Für Excel mit deutscher Ländereinstellung die Datei über
*Daten → Aus Text/CSV* importieren, damit die Spalten korrekt erkannt werden.
Ein CSV-Import zurück ins Modell ist noch nicht vorhanden (`FileHandler.load_csv` liefert
nur eine Liste von Dictionaries).
