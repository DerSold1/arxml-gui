"""Parameter models and management"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import re


class ParameterValueType(Enum):
    """Parameter value types"""
    STATIC = "static"
    DYNAMIC = "dynamic"
    COMPUTED = "computed"
    REFERENCE = "reference"


@dataclass
class ParameterValue:
    """Parameter with value and validation"""
    name: str
    value: Any
    value_type: ParameterValueType = ParameterValueType.STATIC
    unit: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "value_type": self.value_type.value,
            "unit": self.unit,
            "metadata": self.metadata
        }


class ParameterValidator:
    """Validates parameter values"""

    @staticmethod
    def validate_int(value: Any, min_val: Optional[int] = None, max_val: Optional[int] = None) -> bool:
        """Validate integer parameter"""
        try:
            val = int(value)
            if min_val is not None and val < min_val:
                return False
            if max_val is not None and val > max_val:
                return False
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_float(value: Any, min_val: Optional[float] = None, max_val: Optional[float] = None) -> bool:
        """Validate float parameter"""
        try:
            val = float(value)
            if min_val is not None and val < min_val:
                return False
            if max_val is not None and val > max_val:
                return False
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_string(value: Any, pattern: Optional[str] = None, max_length: Optional[int] = None) -> bool:
        """Validate string parameter"""
        try:
            val = str(value)
            if pattern and not re.match(pattern, val):
                return False
            if max_length and len(val) > max_length:
                return False
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_boolean(value: Any) -> bool:
        """Validate boolean parameter"""
        if isinstance(value, bool):
            return True
        if isinstance(value, str):
            return value.lower() in ["true", "false", "yes", "no", "1", "0"]
        if isinstance(value, (int, float)):
            return value in [0, 1, 0.0, 1.0]
        return False

    @staticmethod
    def validate_enum(value: Any, allowed_values: List[Any]) -> bool:
        """Validate enum parameter"""
        return value in allowed_values

    @staticmethod
    def validate_regex(value: str, pattern: str) -> bool:
        """Validate parameter against regex pattern"""
        try:
            return bool(re.match(pattern, value))
        except re.error:
            return False


@dataclass
class ParameterGroup:
    """Group of related parameters"""
    name: str
    description: str = ""
    parameters: Dict[str, ParameterValue] = field(default_factory=dict)
    parent_group: Optional[str] = None

    def add_parameter(self, param: ParameterValue) -> None:
        """Add parameter to group"""
        self.parameters[param.name] = param

    def remove_parameter(self, param_name: str) -> bool:
        """Remove parameter from group"""
        if param_name in self.parameters:
            del self.parameters[param_name]
            return True
        return False

    def get_parameter(self, param_name: str) -> Optional[ParameterValue]:
        """Get parameter by name"""
        return self.parameters.get(param_name)

    def list_parameters(self) -> List[str]:
        """List all parameter names in group"""
        return list(self.parameters.keys())

    def to_dict(self) -> Dict[str, Any]:
        """Convert group to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {k: v.to_dict() for k, v in self.parameters.items()},
            "parent_group": self.parent_group
        }


class ParameterManager:
    """Manages parameter groups and validation"""

    def __init__(self):
        self.groups: Dict[str, ParameterGroup] = {}
        self.validators: Dict[str, Callable] = {
            "int": ParameterValidator.validate_int,
            "float": ParameterValidator.validate_float,
            "string": ParameterValidator.validate_string,
            "boolean": ParameterValidator.validate_boolean,
            "enum": ParameterValidator.validate_enum,
            "regex": ParameterValidator.validate_regex,
        }

    def add_group(self, group: ParameterGroup) -> None:
        """Add parameter group"""
        self.groups[group.name] = group

    def remove_group(self, group_name: str) -> bool:
        """Remove parameter group"""
        if group_name in self.groups:
            del self.groups[group_name]
            return True
        return False

    def get_group(self, group_name: str) -> Optional[ParameterGroup]:
        """Get parameter group by name"""
        return self.groups.get(group_name)

    def list_groups(self) -> List[str]:
        """List all group names"""
        return list(self.groups.keys())

    def add_parameter_to_group(self, group_name: str, param: ParameterValue) -> bool:
        """Add parameter to specific group"""
        if group_name in self.groups:
            self.groups[group_name].add_parameter(param)
            return True
        return False

    def get_all_parameters(self) -> Dict[str, List[ParameterValue]]:
        """Get all parameters organized by group"""
        return {k: list(v.parameters.values()) for k, v in self.groups.items()}

    def export_to_dict(self) -> Dict[str, Any]:
        """Export all parameters to dictionary"""
        return {k: v.to_dict() for k, v in self.groups.items()}
