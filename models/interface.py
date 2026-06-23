"""Interface models for ARXML generation"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from models.types import (
    InterfaceElement, Parameter, Signal, Operation,
    ServiceInterface, PortInterface, DataType
)


@dataclass
class InterfaceCollection:
    """Collection of interfaces for a project"""
    project_name: str
    vendor_name: str = "VendorName"
    autosar_version: str = "4.3"
    interfaces: Dict[str, InterfaceElement] = field(default_factory=dict)
    global_parameters: List[Parameter] = field(default_factory=list)
    data_type_definitions: Dict[str, str] = field(default_factory=dict)
    namespace: str = "/Interfaces"

    def add_interface(self, interface: InterfaceElement) -> None:
        """Add interface to collection"""
        self.interfaces[interface.name] = interface

    def remove_interface(self, interface_name: str) -> bool:
        """Remove interface from collection"""
        if interface_name in self.interfaces:
            del self.interfaces[interface_name]
            return True
        return False

    def get_interface(self, interface_name: str) -> Optional[InterfaceElement]:
        """Get interface by name"""
        return self.interfaces.get(interface_name)

    def list_interfaces(self) -> List[str]:
        """List all interface names"""
        return list(self.interfaces.keys())

    def add_global_parameter(self, parameter: Parameter) -> None:
        """Add global parameter"""
        self.global_parameters.append(parameter)

    def add_data_type(self, name: str, definition: str) -> None:
        """Add custom data type definition"""
        self.data_type_definitions[name] = definition


@dataclass
class ParameterTemplate:
    """Template for commonly used parameters"""
    name: str
    category: str
    parameters: List[Parameter] = field(default_factory=list)
    description: str = ""

    def get_parameters(self) -> List[Parameter]:
        """Get all parameters from template"""
        return self.parameters.copy()


@dataclass
class InterfaceTemplate:
    """Template for interface creation"""
    name: str
    interface_type: str  # "service", "port", "signal"
    description: str = ""
    sample_parameters: List[Parameter] = field(default_factory=list)
    sample_signals: List[Signal] = field(default_factory=list)
    sample_operations: List[Operation] = field(default_factory=list)


class TemplateManager:
    """Manages parameter and interface templates"""

    def __init__(self):
        self.parameter_templates: Dict[str, ParameterTemplate] = {}
        self.interface_templates: Dict[str, InterfaceTemplate] = {}
        self._initialize_builtin_templates()

    def _initialize_builtin_templates(self) -> None:
        """Initialize built-in templates"""
        # Common parameter templates
        self._add_timing_template()
        self._add_communication_template()
        self._add_safety_template()

    def _add_timing_template(self) -> None:
        """Add timing-related parameter template"""
        params = [
            Parameter(name="timeout", param_type="int", description="Timeout in ms"),
            Parameter(name="cycle_time", param_type="int", description="Cycle time in ms"),
            Parameter(name="delay", param_type="int", description="Delay in ms"),
        ]
        template = ParameterTemplate(
            name="Timing",
            category="timing",
            parameters=params,
            description="Common timing parameters"
        )
        self.parameter_templates["timing"] = template

    def _add_communication_template(self) -> None:
        """Add communication-related parameter template"""
        params = [
            Parameter(name="baudrate", param_type="int", description="Baud rate"),
            Parameter(name="data_bits", param_type="int", description="Data bits (7-8)"),
            Parameter(name="stop_bits", param_type="int", description="Stop bits (1-2)"),
            Parameter(name="parity", param_type="string", description="Parity (none/odd/even)"),
        ]
        template = ParameterTemplate(
            name="Communication",
            category="communication",
            parameters=params,
            description="Common communication parameters"
        )
        self.parameter_templates["communication"] = template

    def _add_safety_template(self) -> None:
        """Add safety-related parameter template"""
        params = [
            Parameter(name="asil_level", param_type="string", description="ASIL level (A-D)"),
            Parameter(name="fault_tolerance", param_type="boolean", description="Fault tolerance enabled"),
            Parameter(name="error_recovery", param_type="boolean", description="Error recovery enabled"),
        ]
        template = ParameterTemplate(
            name="Safety",
            category="safety",
            parameters=params,
            description="Common safety parameters"
        )
        self.parameter_templates["safety"] = template

    def add_parameter_template(self, template: ParameterTemplate) -> None:
        """Add custom parameter template"""
        self.parameter_templates[template.name.lower()] = template

    def get_parameter_template(self, name: str) -> Optional[ParameterTemplate]:
        """Get parameter template by name"""
        return self.parameter_templates.get(name.lower())

    def list_parameter_templates(self) -> List[str]:
        """List all parameter template names"""
        return list(self.parameter_templates.keys())

    def add_interface_template(self, template: InterfaceTemplate) -> None:
        """Add custom interface template"""
        self.interface_templates[template.name.lower()] = template

    def get_interface_template(self, name: str) -> Optional[InterfaceTemplate]:
        """Get interface template by name"""
        return self.interface_templates.get(name.lower())

    def list_interface_templates(self) -> List[str]:
        """List all interface template names"""
        return list(self.interface_templates.keys())
