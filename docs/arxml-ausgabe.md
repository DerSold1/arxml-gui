# ARXML-Ausgabe

Beschreibt, wie der Generator (`arxml/generator.py`) das Projekt in XML übersetzt, welche
Elemente entstehen und wo die Ausgabe heute vom AUTOSAR-Standard abweicht.

[← zurück zur README](../README.md)

---

## Inhalt

- [Wichtiger Hinweis zur Konformität](#wichtiger-hinweis-zur-konformität)
- [Gesamtaufbau](#gesamtaufbau)
- [Element-Zuordnung](#element-zuordnung)
- [Vollständiges Beispiel](#vollständiges-beispiel)
- [Technische Details](#technische-details)
- [Abweichungen zu AUTOSAR R4 und Zielbild](#abweichungen-zu-autosar-r4-und-zielbild)

---

## Wichtiger Hinweis zur Konformität

> ⚠️ Die erzeugte Datei ist **wohlgeformtes XML mit AUTOSAR-Namespace**, aber **kein
> schemagültiges AUTOSAR-ARXML**. Mehrere Tags sind projekteigene Namen
> (z. B. `PORT-INTERFACE`, `SERVICE-TYPE`, `PORT-TYPE`, `AR-INFO-SECTION`, `CONSTRAINTS`),
> Typen werden als Text statt als Referenz geschrieben, und die Datei wurde nicht gegen das
> AUTOSAR-XSD validiert.
>
> Werkzeuge wie DaVinci Developer, SystemDesk, EB tresos oder `autosar`/`armodel` (Python)
> werden die Datei daher voraussichtlich nicht oder nur teilweise importieren.
> Die Umstellung auf R4-Elemente ist Teil der [Roadmap](entwicklung.md#roadmap); das
> [Zielbild](#abweichungen-zu-autosar-r4-und-zielbild) steht unten.

Für Konzeptarbeit, Schulungen, Reviews und als lesbare Schnittstellenbeschreibung ist die
Ausgabe gut nutzbar.

## Gesamtaufbau

```
AUTOSAR                              xmlns = http://autosar.org/schema/r4.0
├── AR-INFO-SECTION
│   └── DESCRIPTION
│       └── L-2 (L="en")             "<Projektname> - <Vendor>"
└── AR-PACKAGES
    └── AR-PACKAGE
        ├── SHORT-NAME               Projektname
        └── ELEMENTS
            ├── SERVICE-INTERFACE    je Interface vom Typ SERVICE
            ├── PORT-INTERFACE       je Interface vom Typ PORT
            └── SYSTEM-SIGNAL        je Interface vom Typ SIGNAL
```

- Es gibt genau **ein** `AR-PACKAGE` pro Projekt, benannt nach dem Projektnamen.
- Interfaces erscheinen in der Reihenfolge, in der sie hinzugefügt wurden.
- Interfaces vom Typ `OPERATION` oder `EVENT` werden nicht ausgegeben.
- Ein leeres Projekt erzeugt `<ELEMENTS/>`.

## Element-Zuordnung

### Service-Interface

| Modell | XML |
|---|---|
| `InterfaceElement.name` | `SERVICE-INTERFACE/SHORT-NAME` |
| `InterfaceElement.description` | `SERVICE-INTERFACE/DESC` |
| `content["service_type"]` | `SERVICE-TYPE` (Standard `request-response`) |
| `content["operations"][i]` | `OPERATIONS/OPERATION` |
| ↳ `name`, `description` | `SHORT-NAME`, `DESC` |
| ↳ `input_parameters` | `INPUT-PARAMETERS/PARAMETER-DATA-PROTOTYPE` (nur wenn nicht leer) |
| ↳ `output_parameters` | `OUTPUT-PARAMETERS/PARAMETER-DATA-PROTOTYPE` (nur wenn nicht leer) |
| `InterfaceElement.parameters` | `PARAMETERS/PARAMETER-DATA-PROTOTYPE` (nur wenn nicht leer) |

### Port-Interface

| Modell | XML |
|---|---|
| `name`, `description` | `PORT-INTERFACE/SHORT-NAME`, `DESC` |
| `content["port_type"]` | `PORT-TYPE` (Standard `provide`) |
| `content["signals"][i]` | `DATA-ELEMENTS/ELEMENT-DATA-PROTOTYPE` |
| ↳ `name`, `description` | `SHORT-NAME`, `DESC` |
| ↳ `data_type` | `DATA-TYPE` (nur wenn Schlüssel vorhanden) |
| ↳ `unit` | `UNIT` (nur wenn Schlüssel vorhanden, auch leer) |
| ↳ `init_value` | – (wird nicht ausgegeben) |
| `InterfaceElement.parameters` | `PARAMETERS/PARAMETER-DATA-PROTOTYPE` |

### System-Signal

| Modell | XML |
|---|---|
| `name`, `description` | `SYSTEM-SIGNAL/SHORT-NAME`, `DESC` |
| `content["data_type"]` | `DATA-TYPE` |
| `content["init_value"]` | `INIT-VALUE` (als Text) |
| `InterfaceElement.parameters` | – (wird nicht ausgegeben) |

### Parameter (`PARAMETER-DATA-PROTOTYPE`)

| Modell | XML |
|---|---|
| `name` | `SHORT-NAME` |
| `description` | `DESC` (leer ⇒ `<DESC/>`) |
| `param_type` | `TYPE-REFERENCE`: `int→uint32`, `float→float32`, `string`, `boolean`, `enum`, `complex`; Unbekanntes ⇒ `uint32` |
| `constraint` | `CONSTRAINTS` – wird **immer** geschrieben, ggf. leer (`<CONSTRAINTS/>`) |
| ↳ `min_value`, `max_value`, `default_value` | `MIN-VALUE`, `MAX-VALUE`, `DEFAULT-VALUE` (nur wenn gesetzt) |
| `metadata` | `METADATA/PROPERTY/KEY` + `VALUE` je Eintrag (nur wenn nicht leer) |

## Vollständiges Beispiel

Ausgabe des [kompletten Beispiels aus der Python-API](python-api.md#komplettes-beispiel),
unverändert übernommen:

```xml
<?xml version="1.0" ?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://autosar.org/schema/r4.0">
  <AR-INFO-SECTION>
    <DESCRIPTION>
      <L-2 L="en">BmsDemo - MHP</L-2>
    </DESCRIPTION>
  </AR-INFO-SECTION>
  <AR-PACKAGES>
    <AR-PACKAGE>
      <SHORT-NAME>BmsDemo</SHORT-NAME>
      <ELEMENTS>
        <SERVICE-INTERFACE>
          <SHORT-NAME>DiagService</SHORT-NAME>
          <DESC>Diagnosedienste</DESC>
          <SERVICE-TYPE>request-response</SERVICE-TYPE>
          <OPERATIONS>
            <OPERATION>
              <SHORT-NAME>ReadDtc</SHORT-NAME>
              <DESC>Fehlerspeicher lesen</DESC>
              <INPUT-PARAMETERS>
                <PARAMETER-DATA-PROTOTYPE>
                  <SHORT-NAME>dtc_mask</SHORT-NAME>
                  <DESC/>
                  <TYPE-REFERENCE>uint32</TYPE-REFERENCE>
                  <CONSTRAINTS/>
                </PARAMETER-DATA-PROTOTYPE>
              </INPUT-PARAMETERS>
              <OUTPUT-PARAMETERS>
                <PARAMETER-DATA-PROTOTYPE>
                  <SHORT-NAME>dtc_count</SHORT-NAME>
                  <DESC/>
                  <TYPE-REFERENCE>uint32</TYPE-REFERENCE>
                  <CONSTRAINTS/>
                </PARAMETER-DATA-PROTOTYPE>
              </OUTPUT-PARAMETERS>
            </OPERATION>
          </OPERATIONS>
          <PARAMETERS>
            <PARAMETER-DATA-PROTOTYPE>
              <SHORT-NAME>timeout</SHORT-NAME>
              <DESC>Timeout in ms</DESC>
              <TYPE-REFERENCE>uint32</TYPE-REFERENCE>
              <CONSTRAINTS>
                <MIN-VALUE>0</MIN-VALUE>
                <MAX-VALUE>1000</MAX-VALUE>
                <DEFAULT-VALUE>100</DEFAULT-VALUE>
              </CONSTRAINTS>
            </PARAMETER-DATA-PROTOTYPE>
          </PARAMETERS>
        </SERVICE-INTERFACE>
        <PORT-INTERFACE>
          <SHORT-NAME>BatteryTemp</SHORT-NAME>
          <DESC>Batterietemperatur</DESC>
          <PORT-TYPE>provide</PORT-TYPE>
          <DATA-ELEMENTS>
            <ELEMENT-DATA-PROTOTYPE>
              <SHORT-NAME>CellTemp</SHORT-NAME>
              <DESC>Zelltemperatur</DESC>
              <DATA-TYPE>int16</DATA-TYPE>
              <UNIT>degC</UNIT>
            </ELEMENT-DATA-PROTOTYPE>
          </DATA-ELEMENTS>
        </PORT-INTERFACE>
        <SYSTEM-SIGNAL>
          <SHORT-NAME>VehicleSpeed</SHORT-NAME>
          <DESC>Fahrzeuggeschwindigkeit</DESC>
          <DATA-TYPE>uint16</DATA-TYPE>
          <INIT-VALUE>0</INIT-VALUE>
        </SYSTEM-SIGNAL>
      </ELEMENTS>
    </AR-PACKAGE>
  </AR-PACKAGES>
</AUTOSAR>
```

## Technische Details

- Aufbau mit `xml.etree.ElementTree`, Formatierung mit `xml.dom.minidom` (2 Leerzeichen Einrückung).
- Die XML-Deklaration lautet `<?xml version="1.0" ?>` ohne `encoding`-Angabe; die Datei wird
  trotzdem als **UTF-8** geschrieben (XML-Standard bei fehlender Angabe).
- Für **alle** Versionen 4.2, 4.3, 4.4 wird der Namespace `http://autosar.org/schema/r4.0`
  geschrieben. Das ist für R4.x korrekt – die Version selbst steht in AUTOSAR üblicherweise im
  Dateinamen des Schemas in `xsi:schemaLocation`, der hier noch fehlt.
- `ARXMLGenerator` wird im Hauptfenster einmalig mit Version `4.3` erzeugt; die im Reiter
  *Project* gewählte Version hat keinen Einfluss auf den Generator.
- Das Feld *Namespace* des Projekts wird nicht ausgegeben.
- Sonderzeichen (`<`, `&`, Umlaute) werden von ElementTree korrekt maskiert bzw. als UTF-8 geschrieben.

## Abweichungen zu AUTOSAR R4 und Zielbild

Die folgende Tabelle ist die Orientierung für die Umstellung auf schemakonforme Ausgabe
(Classic Platform). Vor der Umsetzung sollte jede Zeile gegen das XSD der Zielversion
(z. B. `AUTOSAR_4-3-0.xsd`) geprüft werden.

| Heute | Problem | Ziel (AUTOSAR R4, Classic) |
|---|---|---|
| `xsi:schemaLocation="http://autosar.org/schema/r4.0"` | Schema-Datei fehlt (Paar aus Namespace und Datei erwartet) | `"http://autosar.org/schema/r4.0 AUTOSAR_4-3-0.xsd"` |
| `AR-INFO-SECTION/DESCRIPTION` | kein AUTOSAR-Element | entfällt bzw. `ADMIN-DATA` / `DESC` am Paket |
| `<DESC>Text</DESC>` | `DESC` erwartet mehrsprachigen Inhalt | `<DESC><L-2 L="EN">Text</L-2></DESC>` |
| `L="en"` | Sprachcodes sind Großbuchstaben | `L="EN"` |
| `SERVICE-INTERFACE` + `SERVICE-TYPE` + `OPERATION` | in Classic nicht vorhanden; `SERVICE-INTERFACE` ist ein Element der Adaptive Platform mit anderem Aufbau | `CLIENT-SERVER-INTERFACE` mit `IS-SERVICE`, `OPERATIONS/CLIENT-SERVER-OPERATION/ARGUMENTS/ARGUMENT-DATA-PROTOTYPE` (`DIRECTION` IN/OUT) |
| `PORT-INTERFACE` + `DATA-ELEMENTS/ELEMENT-DATA-PROTOTYPE` | kein AUTOSAR-Element | `SENDER-RECEIVER-INTERFACE/DATA-ELEMENTS/VARIABLE-DATA-PROTOTYPE` |
| `PORT-TYPE` (provide/require) | Richtung gehört nicht ans Interface, sondern an den Port einer SWC | `P-PORT-PROTOTYPE` / `R-PORT-PROTOTYPE` / `PR-PORT-PROTOTYPE` in einer `APPLICATION-SW-COMPONENT-TYPE` |
| `DATA-TYPE` / `TYPE-REFERENCE` als Text | Typen werden referenziert | `TYPE-TREF DEST="IMPLEMENTATION-DATA-TYPE">/AUTOSAR_Platform/ImplementationDataTypes/uint16</TYPE-TREF>` plus Paket mit den Datentypen |
| `PARAMETERS` am Interface | kein AUTOSAR-Element | eigenes `PARAMETER-INTERFACE/PARAMETERS/PARAMETER-DATA-PROTOTYPE` |
| `CONSTRAINTS/MIN-VALUE/MAX-VALUE` | kein AUTOSAR-Element | `DATA-CONSTR` mit `LOWER-LIMIT`/`UPPER-LIMIT`, referenziert vom Datentyp |
| `DEFAULT-VALUE`, `INIT-VALUE` als Text | Werte sind strukturiert | `INIT-VALUE` mit `NUMERICAL-VALUE-SPECIFICATION` (an ComSpec bzw. I-Signal) |
| `UNIT` als Text | Einheiten werden referenziert | `UNIT` im Einheiten-Paket, Referenz über `COMPU-METHOD` |
| `METADATA/PROPERTY` | kein AUTOSAR-Element | `ADMIN-DATA/SDGS/SDG/SD` (Special Data) |
| `SYSTEM-SIGNAL/DATA-TYPE`, `INIT-VALUE` | gehören nicht ans System-Signal | `SYSTEM-SIGNAL` mit `PHYSICAL-PROPS`; Init-Wert am `I-SIGNAL` |
| fehlende `UUID`-Attribute | optional, von vielen Werkzeugen erwartet | `UUID` je Element |

Empfohlenes Vorgehen für die Umstellung:

1. Datentyp-Paket (`ImplementationDataTypes`, ggf. `BaseTypes`) erzeugen, damit Referenzen auflösbar sind.
2. Interfaces auf `SENDER-RECEIVER-INTERFACE` und `CLIENT-SERVER-INTERFACE` umstellen.
3. Paketstruktur nach Namespace-Feld aufbauen (z. B. `/Interfaces`, `/DataTypes`).
4. Ausgabe in den Tests mit `lxml` gegen das XSD validieren (`lxml` ist bereits in `requirements.txt`).
5. Parser auf Namespace-Unterstützung umstellen, damit ein Round-Trip möglich wird.
