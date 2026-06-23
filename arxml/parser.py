"""ARXML Parser for reading and analyzing ARXML files"""

from typing import Dict, List, Optional, Any
from xml.etree import ElementTree as ET
from models.interface import InterfaceCollection
from models.types import InterfaceElement, InterfaceType, Parameter


class ARXMLParser:
    """Parses ARXML files into interface collections"""

    def __init__(self):
        self.namespaces = {
            "ar": "http://autosar.org/schema/r4.0",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance"
        }

    def parse_file(self, filepath: str) -> Optional[InterfaceCollection]:
        """Parse ARXML file and return InterfaceCollection"""
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            return self._parse_root(root)
        except Exception as e:
            print(f"Error parsing ARXML file: {e}")
            return None

    def parse_string(self, arxml_content: str) -> Optional[InterfaceCollection]:
        """Parse ARXML string and return InterfaceCollection"""
        try:
            root = ET.fromstring(arxml_content)
            return self._parse_root(root)
        except Exception as e:
            print(f"Error parsing ARXML content: {e}")
            return None

    def _parse_root(self, root: ET.Element) -> Optional[InterfaceCollection]:
        """Parse AUTOSAR root element"""
        # Extract metadata
        project_name = "ParsedProject"
        vendor_name = "VendorName"
        autosar_version = "4.3"

        collection = InterfaceCollection(
            project_name=project_name,
            vendor_name=vendor_name,
            autosar_version=autosar_version
        )

        # Parse AR-PACKAGES
        for pkg in root.findall(".//AR-PACKAGE", self.namespaces):
            self._parse_package(pkg, collection)

        return collection

    def _parse_package(self, pkg_elem: ET.Element, collection: InterfaceCollection) -> None:
        """Parse AR-PACKAGE element"""
        name_elem = pkg_elem.find("SHORT-NAME", self.namespaces)
        if name_elem is not None and name_elem.text:
            collection.project_name = name_elem.text

        # Parse elements in package
        elements = pkg_elem.find("ELEMENTS", self.namespaces)
        if elements is not None:
            for child in elements:
                self._parse_element(child, collection)

    def _parse_element(self, elem: ET.Element, collection: InterfaceCollection) -> None:
        """Parse interface element"""
        tag = elem.tag.replace("{", "").replace("}", "").split("}")[-1]

        if tag == "SERVICE-INTERFACE":
            self._parse_service_interface(elem, collection)
        elif tag == "PORT-INTERFACE":
            self._parse_port_interface(elem, collection)
        elif tag == "SYSTEM-SIGNAL":
            self._parse_system_signal(elem, collection)

    def _parse_service_interface(self, elem: ET.Element, collection: InterfaceCollection) -> None:
        """Parse SERVICE-INTERFACE element"""
        name = self._get_short_name(elem)
        desc = self._get_description(elem)

        interface = InterfaceElement(
            element_type=InterfaceType.SERVICE,
            name=name,
            description=desc
        )

        # Parse operations
        operations = []
        for op_elem in elem.findall(".//OPERATION", self.namespaces):
            op_name = self._get_short_name(op_elem)
            op_desc = self._get_description(op_elem)
            operations.append({"name": op_name, "description": op_desc})

        interface.content["operations"] = operations
        collection.add_interface(interface)

    def _parse_port_interface(self, elem: ET.Element, collection: InterfaceCollection) -> None:
        """Parse PORT-INTERFACE element"""
        name = self._get_short_name(elem)
        desc = self._get_description(elem)

        interface = InterfaceElement(
            element_type=InterfaceType.PORT,
            name=name,
            description=desc
        )

        # Parse data elements
        signals = []
        for sig_elem in elem.findall(".//ELEMENT-DATA-PROTOTYPE", self.namespaces):
            sig_name = self._get_short_name(sig_elem)
            sig_desc = self._get_description(sig_elem)
            signals.append({"name": sig_name, "description": sig_desc})

        interface.content["signals"] = signals
        collection.add_interface(interface)

    def _parse_system_signal(self, elem: ET.Element, collection: InterfaceCollection) -> None:
        """Parse SYSTEM-SIGNAL element"""
        name = self._get_short_name(elem)
        desc = self._get_description(elem)

        interface = InterfaceElement(
            element_type=InterfaceType.SIGNAL,
            name=name,
            description=desc
        )

        collection.add_interface(interface)

    def _get_short_name(self, elem: ET.Element) -> str:
        """Get SHORT-NAME from element"""
        name_elem = elem.find("SHORT-NAME", self.namespaces)
        return name_elem.text if name_elem is not None and name_elem.text else "Unknown"

    def _get_description(self, elem: ET.Element) -> str:
        """Get DESC from element"""
        desc_elem = elem.find("DESC", self.namespaces)
        return desc_elem.text if desc_elem is not None and desc_elem.text else ""
