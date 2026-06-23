"""ARXML Generator for creating AUTOSAR XML files"""

from typing import Dict, List, Any, Optional
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from models.interface import InterfaceCollection
from models.types import (
    InterfaceType, ServiceType, PortType, DataType,
    InterfaceElement, ServiceInterface, PortInterface, Signal, Operation, Parameter
)


class ARXMLGenerator:
    """Generates ARXML files from interface definitions"""

    def __init__(self, autosar_version: str = "4.3"):
        self.autosar_version = autosar_version
        self.namespaces = {
            "4.2": "http://autosar.org/schema/r4.0",
            "4.3": "http://autosar.org/schema/r4.0",
            "4.4": "http://autosar.org/schema/r4.0",
        }
        self.ns = self.namespaces.get(autosar_version, self.namespaces["4.3"])

    def generate(self, collection: InterfaceCollection) -> str:
        """Generate ARXML content from interface collection"""
        root = Element("AUTOSAR")
        root.set("xmlns", self.ns)
        root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.set("xsi:schemaLocation", self.ns)

        # Add metadata
        self._add_metadata(root, collection)

        # Add interfaces
        interfaces_elem = SubElement(root, "AR-PACKAGES")
        pkg = SubElement(interfaces_elem, "AR-PACKAGE")
        SubElement(pkg, "SHORT-NAME").text = collection.project_name

        elements = SubElement(pkg, "ELEMENTS")

        # Generate each interface
        for interface in collection.interfaces.values():
            if interface.element_type == InterfaceType.SERVICE:
                self._add_service_interface(elements, interface)
            elif interface.element_type == InterfaceType.PORT:
                self._add_port_interface(elements, interface)
            elif interface.element_type == InterfaceType.SIGNAL:
                self._add_signal_interface(elements, interface)

        return self._prettify_xml(root)

    def _add_metadata(self, root: Element, collection: InterfaceCollection) -> None:
        """Add AUTOSAR metadata"""
        metadata = SubElement(root, "AR-INFO-SECTION")
        desc = SubElement(metadata, "DESCRIPTION")
        l2_elem = SubElement(desc, "L-2")
        l2_elem.set("L", "en")
        l2_elem.text = f"{collection.project_name} - {collection.vendor_name}"

    def _add_service_interface(self, parent: Element, interface: InterfaceElement) -> None:
        """Add service interface to ARXML"""
        service_elem = SubElement(parent, "SERVICE-INTERFACE")
        SubElement(service_elem, "SHORT-NAME").text = interface.name
        SubElement(service_elem, "DESC").text = interface.description

        # Add service type
        service_type = interface.content.get("service_type", ServiceType.REQUEST_RESPONSE.value)
        SubElement(service_elem, "SERVICE-TYPE").text = service_type

        # Add operations
        if "operations" in interface.content:
            operations_elem = SubElement(service_elem, "OPERATIONS")
            for operation in interface.content["operations"]:
                self._add_operation(operations_elem, operation)

        # Add parameters
        if interface.parameters:
            params_elem = SubElement(service_elem, "PARAMETERS")
            for param in interface.parameters:
                self._add_parameter_element(params_elem, param)

    def _add_port_interface(self, parent: Element, interface: InterfaceElement) -> None:
        """Add port interface to ARXML"""
        port_elem = SubElement(parent, "PORT-INTERFACE")
        SubElement(port_elem, "SHORT-NAME").text = interface.name
        SubElement(port_elem, "DESC").text = interface.description

        # Add port type
        port_type = interface.content.get("port_type", PortType.PROVIDE.value)
        SubElement(port_elem, "PORT-TYPE").text = port_type

        # Add signals/data elements
        if "signals" in interface.content:
            data_elem = SubElement(port_elem, "DATA-ELEMENTS")
            for signal in interface.content["signals"]:
                self._add_signal_element(data_elem, signal)

        # Add parameters
        if interface.parameters:
            params_elem = SubElement(port_elem, "PARAMETERS")
            for param in interface.parameters:
                self._add_parameter_element(params_elem, param)

    def _add_signal_interface(self, parent: Element, interface: InterfaceElement) -> None:
        """Add signal interface to ARXML"""
        signal_elem = SubElement(parent, "SYSTEM-SIGNAL")
        SubElement(signal_elem, "SHORT-NAME").text = interface.name
        SubElement(signal_elem, "DESC").text = interface.description

        # Add signal properties
        if "data_type" in interface.content:
            SubElement(signal_elem, "DATA-TYPE").text = interface.content["data_type"]

        if "init_value" in interface.content:
            SubElement(signal_elem, "INIT-VALUE").text = str(interface.content["init_value"])

    def _add_operation(self, parent: Element, operation: Dict[str, Any]) -> None:
        """Add operation to service interface"""
        op_elem = SubElement(parent, "OPERATION")
        SubElement(op_elem, "SHORT-NAME").text = operation.get("name", "Operation")
        SubElement(op_elem, "DESC").text = operation.get("description", "")

        # Add input parameters
        if operation.get("input_parameters"):
            in_params = SubElement(op_elem, "INPUT-PARAMETERS")
            for param in operation["input_parameters"]:
                self._add_parameter_element(in_params, param)

        # Add output parameters
        if operation.get("output_parameters"):
            out_params = SubElement(op_elem, "OUTPUT-PARAMETERS")
            for param in operation["output_parameters"]:
                self._add_parameter_element(out_params, param)

    def _add_signal_element(self, parent: Element, signal: Dict[str, Any]) -> None:
        """Add signal element to port interface"""
        sig_elem = SubElement(parent, "ELEMENT-DATA-PROTOTYPE")
        SubElement(sig_elem, "SHORT-NAME").text = signal.get("name", "Signal")
        SubElement(sig_elem, "DESC").text = signal.get("description", "")

        if "data_type" in signal:
            SubElement(sig_elem, "DATA-TYPE").text = signal["data_type"]

        if "unit" in signal:
            SubElement(sig_elem, "UNIT").text = signal["unit"]

    def _add_parameter_element(self, parent: Element, param: Parameter) -> None:
        """Add parameter element to ARXML"""
        param_elem = SubElement(parent, "PARAMETER-DATA-PROTOTYPE")
        SubElement(param_elem, "SHORT-NAME").text = param.name
        SubElement(param_elem, "DESC").text = param.description

        # Add type reference
        type_elem = SubElement(param_elem, "TYPE-REFERENCE")
        type_elem.text = self._map_param_type(param.param_type)

        # Add constraints if present
        if param.constraint:
            constraint_elem = SubElement(param_elem, "CONSTRAINTS")
            if param.constraint.min_value is not None:
                SubElement(constraint_elem, "MIN-VALUE").text = str(param.constraint.min_value)
            if param.constraint.max_value is not None:
                SubElement(constraint_elem, "MAX-VALUE").text = str(param.constraint.max_value)
            if param.constraint.default_value is not None:
                SubElement(constraint_elem, "DEFAULT-VALUE").text = str(param.constraint.default_value)

        # Add metadata
        if param.metadata:
            meta_elem = SubElement(param_elem, "METADATA")
            for key, value in param.metadata.items():
                prop = SubElement(meta_elem, "PROPERTY")
                SubElement(prop, "KEY").text = key
                SubElement(prop, "VALUE").text = str(value)

    def _map_param_type(self, param_type) -> str:
        """Map parameter type to AUTOSAR type reference"""
        type_map = {
            "int": "uint32",
            "float": "float32",
            "string": "string",
            "boolean": "boolean",
            "enum": "enum",
            "complex": "complex"
        }
        return type_map.get(param_type.value if hasattr(param_type, 'value') else param_type, "uint32")

    def _prettify_xml(self, elem: Element) -> str:
        """Return prettified XML string"""
        rough_string = tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    def save_to_file(self, collection: InterfaceCollection, filepath: str) -> bool:
        """Generate and save ARXML to file"""
        try:
            content = self.generate(collection)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error saving ARXML: {e}")
            return False
