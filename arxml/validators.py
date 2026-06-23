"""ARXML Validators for data integrity and AUTOSAR compliance"""

from typing import Dict, List, Tuple, Optional
from models.interface import InterfaceCollection
from models.types import InterfaceElement, Parameter
import re


class ValidationError:
    """Represents a validation error"""

    def __init__(self, error_type: str, element: str, message: str, severity: str = "ERROR"):
        self.error_type = error_type
        self.element = element
        self.message = message
        self.severity = severity  # ERROR, WARNING, INFO

    def __str__(self) -> str:
        return f"[{self.severity}] {self.error_type} on '{self.element}': {self.message}"


class ARXMLValidator:
    """Validates ARXML content and AUTOSAR compliance"""

    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []

    def validate_collection(self, collection: InterfaceCollection) -> Tuple[bool, List[ValidationError]]:
        """Validate entire interface collection"""
        self.errors = []
        self.warnings = []

        # Validate project metadata
        self._validate_metadata(collection)

        # Validate interfaces
        for interface_name, interface in collection.interfaces.items():
            self._validate_interface(interface)

        # Validate global parameters
        for param in collection.global_parameters:
            self._validate_parameter(param, "GlobalParameter")

        all_issues = self.errors + self.warnings
        return len(self.errors) == 0, all_issues

    def _validate_metadata(self, collection: InterfaceCollection) -> None:
        """Validate project metadata"""
        if not collection.project_name:
            self.errors.append(ValidationError(
                "METADATA", "ProjectName",
                "Project name is required"
            ))

        if not collection.vendor_name:
            self.warnings.append(ValidationError(
                "METADATA", "VendorName",
                "Vendor name is not set",
                "WARNING"
            ))

        if collection.autosar_version not in ["4.2", "4.3", "4.4"]:
            self.errors.append(ValidationError(
                "METADATA", "AutosarVersion",
                f"Unsupported AUTOSAR version: {collection.autosar_version}"
            ))

    def _validate_interface(self, interface: InterfaceElement) -> None:
        """Validate interface element"""
        # Check name validity (AUTOSAR naming rules)
        if not self._is_valid_identifier(interface.name):
            self.errors.append(ValidationError(
                "INTERFACE", interface.name,
                "Invalid interface name format (must start with letter, contain only alphanumeric and underscore)"
            ))

        # Check for duplicate names (warning)
        if " " in interface.name:
            self.warnings.append(ValidationError(
                "INTERFACE", interface.name,
                "Interface name contains spaces",
                "WARNING"
            ))

        # Validate parameters
        for param in interface.parameters:
            self._validate_parameter(param, interface.name)

    def _validate_parameter(self, param: Parameter, parent_name: str) -> None:
        """Validate parameter definition"""
        # Check parameter name
        if not self._is_valid_identifier(param.name):
            self.errors.append(ValidationError(
                "PARAMETER", f"{parent_name}.{param.name}",
                "Invalid parameter name format"
            ))

        # Check constraint consistency
        if param.constraint:
            if (param.constraint.min_value is not None and
                    param.constraint.max_value is not None and
                    param.constraint.min_value > param.constraint.max_value):
                self.errors.append(ValidationError(
                    "CONSTRAINT", f"{parent_name}.{param.name}",
                    "Min value is greater than max value"
                ))

            # Validate default value against constraints
            if param.constraint.default_value is not None:
                if not self._is_value_in_constraints(param.constraint.default_value, param.constraint):
                    self.errors.append(ValidationError(
                        "CONSTRAINT", f"{parent_name}.{param.name}",
                        "Default value violates constraints"
                    ))

    def _is_valid_identifier(self, name: str) -> bool:
        """Check if name follows AUTOSAR identifier rules"""
        # Must start with letter or underscore, contain only alphanumeric and underscore
        pattern = r"^[a-zA-Z_][a-zA-Z0-9_]*$"
        return bool(re.match(pattern, name)) and len(name) <= 128

    def _is_value_in_constraints(self, value, constraint) -> bool:
        """Check if value satisfies constraints"""
        try:
            if constraint.min_value is not None and value < constraint.min_value:
                return False
            if constraint.max_value is not None and value > constraint.max_value:
                return False
            if constraint.allowed_values and value not in constraint.allowed_values:
                return False
            return True
        except (TypeError, ValueError):
            return False

    def get_errors(self) -> List[ValidationError]:
        """Get all validation errors"""
        return self.errors

    def get_warnings(self) -> List[ValidationError]:
        """Get all validation warnings"""
        return self.warnings

    def clear(self) -> None:
        """Clear all validation issues"""
        self.errors = []
        self.warnings = []
