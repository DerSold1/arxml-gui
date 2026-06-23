"""Format conversion utilities"""

from typing import Dict, List, Any
from models.parameter import ParameterValue, ParameterGroup
from models.interface import InterfaceCollection
import json


class Converters:
    """Converts between different formats"""

    @staticmethod
    def parameters_to_dict(groups: Dict[str, ParameterGroup]) -> Dict[str, Any]:
        """Convert parameter groups to dictionary"""
        result = {}
        for group_name, group in groups.items():
            result[group_name] = group.to_dict()
        return result

    @staticmethod
    def parameters_to_json(groups: Dict[str, ParameterGroup]) -> str:
        """Convert parameter groups to JSON string"""
        data = Converters.parameters_to_dict(groups)
        return json.dumps(data, indent=2, ensure_ascii=False)

    @staticmethod
    def parameters_to_csv_rows(groups: Dict[str, ParameterGroup]) -> List[Dict[str, Any]]:
        """Convert parameter groups to CSV rows"""
        rows = []
        for group_name, group in groups.items():
            for param_name, param in group.parameters.items():
                rows.append({
                    "group": group_name,
                    "parameter_name": param_name,
                    "value": param.value,
                    "type": param.value_type.value,
                    "unit": param.unit,
                })
        return rows

    @staticmethod
    def dict_to_parameters(data: Dict[str, Any]) -> Dict[str, ParameterGroup]:
        """Convert dictionary to parameter groups"""
        groups = {}
        for group_name, group_data in data.items():
            if isinstance(group_data, dict):
                group = ParameterGroup(
                    name=group_data.get("name", group_name),
                    description=group_data.get("description", ""),
                    parent_group=group_data.get("parent_group")
                )
                if "parameters" in group_data:
                    for param_name, param_data in group_data["parameters"].items():
                        param = ParameterValue(
                            name=param_name,
                            value=param_data.get("value"),
                            unit=param_data.get("unit", "")
                        )
                        group.add_parameter(param)
                groups[group_name] = group
        return groups

    @staticmethod
    def json_string_to_parameters(json_str: str) -> Dict[str, ParameterGroup]:
        """Convert JSON string to parameter groups"""
        try:
            data = json.loads(json_str)
            return Converters.dict_to_parameters(data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return {}

    @staticmethod
    def interface_collection_to_dict(collection: InterfaceCollection) -> Dict[str, Any]:
        """Convert InterfaceCollection to dictionary"""
        return {
            "project_name": collection.project_name,
            "vendor_name": collection.vendor_name,
            "autosar_version": collection.autosar_version,
            "namespace": collection.namespace,
            "interfaces": {
                name: {
                    "type": interface.element_type.value,
                    "name": interface.name,
                    "description": interface.description,
                    "content": interface.content
                }
                for name, interface in collection.interfaces.items()
            }
        }

    @staticmethod
    def interface_collection_to_json(collection: InterfaceCollection) -> str:
        """Convert InterfaceCollection to JSON string"""
        data = Converters.interface_collection_to_dict(collection)
        return json.dumps(data, indent=2, ensure_ascii=False)
