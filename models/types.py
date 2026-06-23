"""Type definitions for ARXML Generator"""

from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


class ParameterType(Enum):
    """Supported parameter types"""
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"
    ENUM = "enum"
    COMPLEX = "complex"


class InterfaceType(Enum):
    """AUTOSAR interface types"""
    SERVICE = "service"
    PORT = "port"
    SIGNAL = "signal"
    OPERATION = "operation"
    EVENT = "event"


class ServiceType(Enum):
    """Service interface types"""
    REQUEST_RESPONSE = "request-response"
    FIRE_AND_FORGET = "fire-and-forget"
    PUBLISH_SUBSCRIBE = "publish-subscribe"


class PortType(Enum):
    """Port types in AUTOSAR"""
    PROVIDE = "provide"
    REQUIRE = "require"
    PROVIDE_REQUIRE = "provide-require"


class DataType(Enum):
    """AUTOSAR data types"""
    UINT8 = "uint8"
    UINT16 = "uint16"
    UINT32 = "uint32"
    UINT64 = "uint64"
    INT8 = "int8"
    INT16 = "int16"
    INT32 = "int32"
    INT64 = "int64"
    FLOAT32 = "float32"
    FLOAT64 = "float64"
    BOOLEAN = "boolean"
    STRING = "string"


@dataclass
class ParameterConstraint:
    """Constraints for parameter validation"""
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    allowed_values: Optional[List[Any]] = None
    regex_pattern: Optional[str] = None
    required: bool = True
    default_value: Optional[Any] = None


@dataclass
class Parameter:
    """Parameter definition"""
    name: str
    param_type: ParameterType
    description: str = ""
    constraint: ParameterConstraint = field(default_factory=ParameterConstraint)
    metadata: Dict[str, Any] = field(default_factory=dict)
    category: str = "general"


@dataclass
class Signal:
    """Signal definition in AUTOSAR"""
    name: str
    data_type: DataType
    length: int = 1
    unit: str = ""
    description: str = ""
    parameters: List[Parameter] = field(default_factory=list)
    init_value: Optional[Any] = None


@dataclass
class Operation:
    """Operation/Method definition"""
    name: str
    description: str = ""
    input_parameters: List[Parameter] = field(default_factory=list)
    output_parameters: List[Parameter] = field(default_factory=list)
    error_codes: Dict[int, str] = field(default_factory=dict)


@dataclass
class ServiceInterface:
    """Service interface definition"""
    name: str
    service_type: ServiceType
    description: str = ""
    operations: List[Operation] = field(default_factory=list)
    parameters: List[Parameter] = field(default_factory=list)
    events: List[str] = field(default_factory=list)


@dataclass
class PortInterface:
    """Port interface definition"""
    name: str
    port_type: PortType
    description: str = ""
    signals: List[Signal] = field(default_factory=list)
    parameters: List[Parameter] = field(default_factory=list)
    data_elements: Dict[str, DataType] = field(default_factory=dict)


@dataclass
class InterfaceElement:
    """Generic interface element"""
    element_type: InterfaceType
    name: str
    description: str = ""
    version: str = "1.0.0"
    parameters: List[Parameter] = field(default_factory=list)
    content: Dict[str, Any] = field(default_factory=dict)
