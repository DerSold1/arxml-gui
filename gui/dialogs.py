"""Dialog windows for user input"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Any
from models.types import (
    InterfaceElement, InterfaceType, ServiceType, PortType, DataType,
    Operation, Signal, Parameter, ParameterType, ParameterConstraint
)


class InterfaceDialog(tk.Toplevel):
    """Dialog for creating/editing interfaces"""

    def __init__(self, parent, interface: Optional[InterfaceElement] = None):
        super().__init__(parent)
        self.title("Interface Editor")
        self.geometry("600x500")
        self.result = None
        self.interface = interface
        self._create_widgets()
        if interface:
            self._load_interface()
        self.transient(parent)
        self.grab_set()

    def _create_widgets(self) -> None:
        """Create dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Interface Type
        ttk.Label(main_frame, text="Interface Type:").grid(row=0, column=0, sticky="w", pady=5)
        self.type_var = tk.StringVar(value="SERVICE")
        type_combo = ttk.Combobox(
            main_frame,
            textvariable=self.type_var,
            values=["SERVICE", "PORT", "SIGNAL"],
            width=40,
            state="readonly"
        )
        type_combo.grid(row=0, column=1, sticky="w", pady=5)
        type_combo.bind("<<ComboboxSelected>>", lambda e: self._on_type_changed())

        # Interface Name
        ttk.Label(main_frame, text="Interface Name:").grid(row=1, column=0, sticky="w", pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=40).grid(row=1, column=1, sticky="w", pady=5)

        # Description
        ttk.Label(main_frame, text="Description:").grid(row=2, column=0, sticky="nw", pady=5)
        self.desc_text = tk.Text(main_frame, height=4, width=40)
        self.desc_text.grid(row=2, column=1, sticky="w", pady=5)

        # Service-specific options
        self.service_frame = ttk.LabelFrame(main_frame, text="Service Options")
        self.service_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)

        ttk.Label(self.service_frame, text="Service Type:").pack(side=tk.LEFT, padx=5)
        self.service_type_var = tk.StringVar(value="REQUEST_RESPONSE")
        service_combo = ttk.Combobox(
            self.service_frame,
            textvariable=self.service_type_var,
            values=["REQUEST_RESPONSE", "FIRE_AND_FORGET", "PUBLISH_SUBSCRIBE"],
            width=25,
            state="readonly"
        )
        service_combo.pack(side=tk.LEFT, padx=5)

        # Port-specific options
        self.port_frame = ttk.LabelFrame(main_frame, text="Port Options")
        self.port_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)

        ttk.Label(self.port_frame, text="Port Type:").pack(side=tk.LEFT, padx=5)
        self.port_type_var = tk.StringVar(value="PROVIDE")
        port_combo = ttk.Combobox(
            self.port_frame,
            textvariable=self.port_type_var,
            values=["PROVIDE", "REQUIRE", "PROVIDE_REQUIRE"],
            width=25,
            state="readonly"
        )
        port_combo.pack(side=tk.LEFT, padx=5)

        # Hide port frame initially
        self.port_frame.grid_remove()

        # Operations/Signals listbox (for SERVICE/PORT)
        self.items_frame = ttk.LabelFrame(main_frame, text="Operations/Signals")
        self.items_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=10)

        btn_frame = ttk.Frame(self.items_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(btn_frame, text="+ Add", command=self._add_item).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="- Remove", command=self._remove_item).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Edit", command=self._edit_item).pack(side=tk.LEFT, padx=2)

        self.items_listbox = tk.Listbox(self.items_frame, height=5)
        self.items_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.items = []

        # Buttons
        btn_frame2 = ttk.Frame(main_frame)
        btn_frame2.grid(row=6, column=0, columnspan=2, sticky="ew", pady=20)
        ttk.Button(btn_frame2, text="Save", command=self._save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame2, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=5)

    def _on_type_changed(self) -> None:
        """Handle interface type change"""
        interface_type = self.type_var.get()
        if interface_type == "SERVICE":
            self.service_frame.grid()
            self.port_frame.grid_remove()
            self.items_frame.winfo_children()[0].winfo_children()[0].winfo_children()[0].config(text="+ Add Operation")
        elif interface_type == "PORT":
            self.service_frame.grid_remove()
            self.port_frame.grid()
            self.items_frame.winfo_children()[0].winfo_children()[0].winfo_children()[0].config(text="+ Add Signal")
        else:  # SIGNAL
            self.service_frame.grid_remove()
            self.port_frame.grid_remove()
            self.items_frame.grid_remove()

    def _add_item(self) -> None:
        """Add operation or signal"""
        interface_type = self.type_var.get()
        if interface_type == "SERVICE":
            dialog = OperationDialog(self)
            self.wait_window(dialog)
            if dialog.result:
                self.items.append(dialog.result)
                self.items_listbox.insert(tk.END, dialog.result["name"])
        elif interface_type == "PORT":
            dialog = SignalDialog(self)
            self.wait_window(dialog)
            if dialog.result:
                self.items.append(dialog.result)
                self.items_listbox.insert(tk.END, dialog.result["name"])

    def _remove_item(self) -> None:
        """Remove selected operation or signal"""
        selection = self.items_listbox.curselection()
        if selection:
            idx = selection[0]
            self.items_listbox.delete(idx)
            del self.items[idx]

    def _edit_item(self) -> None:
        """Edit selected operation or signal"""
        selection = self.items_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to edit")
            return

        idx = selection[0]
        item = self.items[idx]
        interface_type = self.type_var.get()

        if interface_type == "SERVICE":
            dialog = OperationDialog(self, item)
        else:
            dialog = SignalDialog(self, item)

        self.wait_window(dialog)
        if dialog.result:
            self.items[idx] = dialog.result
            self.items_listbox.delete(idx)
            self.items_listbox.insert(idx, dialog.result["name"])

    def _load_interface(self) -> None:
        """Load existing interface data"""
        if not self.interface:
            return

        self.name_var.set(self.interface.name)
        self.desc_text.insert(1.0, self.interface.description)
        self.type_var.set(self.interface.element_type.value.upper())
        self._on_type_changed()

        if self.interface.element_type == InterfaceType.SERVICE:
            if "service_type" in self.interface.content:
                self.service_type_var.set(self.interface.content["service_type"].upper())
            if "operations" in self.interface.content:
                for op in self.interface.content["operations"]:
                    self.items.append(op)
                    self.items_listbox.insert(tk.END, op["name"])

        elif self.interface.element_type == InterfaceType.PORT:
            if "port_type" in self.interface.content:
                self.port_type_var.set(self.interface.content["port_type"].upper())
            if "signals" in self.interface.content:
                for sig in self.interface.content["signals"]:
                    self.items.append(sig)
                    self.items_listbox.insert(tk.END, sig["name"])

    def _save(self) -> None:
        """Save interface"""
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter an interface name")
            return

        interface_type_str = self.type_var.get()
        interface_type = InterfaceType[interface_type_str]
        description = self.desc_text.get(1.0, tk.END).strip()

        interface = InterfaceElement(
            element_type=interface_type,
            name=name,
            description=description
        )

        if interface_type == InterfaceType.SERVICE:
            interface.content["service_type"] = self.service_type_var.get().lower()
            interface.content["operations"] = self.items
        elif interface_type == InterfaceType.PORT:
            interface.content["port_type"] = self.port_type_var.get().lower()
            interface.content["signals"] = self.items

        self.result = interface
        self.destroy()


class OperationDialog(tk.Toplevel):
    """Dialog for creating/editing operations"""

    def __init__(self, parent, operation: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.title("Operation Editor")
        self.geometry("500x400")
        self.result = None
        self.operation = operation or {}
        self._create_widgets()
        if operation:
            self._load_operation()
        self.transient(parent)
        self.grab_set()

    def _create_widgets(self) -> None:
        """Create dialog widgets"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Operation Name
        ttk.Label(main_frame, text="Operation Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, sticky="w", pady=5)

        # Description
        ttk.Label(main_frame, text="Description:").grid(row=1, column=0, sticky="nw", pady=5)
        self.desc_text = tk.Text(main_frame, height=3, width=40)
        self.desc_text.grid(row=1, column=1, sticky="w", pady=5)

        # Input Parameters
        ttk.Label(main_frame, text="Input Parameters:").grid(row=2, column=0, sticky="w", pady=5)
        self.input_listbox = tk.Listbox(main_frame, height=3)
        self.input_listbox.grid(row=2, column=1, sticky="ew", pady=5)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=1, sticky="w", pady=5)
        ttk.Button(btn_frame, text="+ Add Input", command=self._add_input).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="- Remove Input", command=self._remove_input).pack(side=tk.LEFT, padx=2)

        self.input_params = []

        # Output Parameters
        ttk.Label(main_frame, text="Output Parameters:").grid(row=4, column=0, sticky="w", pady=5)
        self.output_listbox = tk.Listbox(main_frame, height=3)
        self.output_listbox.grid(row=4, column=1, sticky="ew", pady=5)

        btn_frame2 = ttk.Frame(main_frame)
        btn_frame2.grid(row=5, column=1, sticky="w", pady=5)
        ttk.Button(btn_frame2, text="+ Add Output", command=self._add_output).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame2, text="- Remove Output", command=self._remove_output).pack(side=tk.LEFT, padx=2)

        self.output_params = []

        # Buttons
        btn_frame3 = ttk.Frame(main_frame)
        btn_frame3.grid(row=6, column=0, columnspan=2, sticky="ew", pady=20)
        ttk.Button(btn_frame3, text="Save", command=self._save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame3, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=5)

    def _add_input(self) -> None:
        """Add input parameter"""
        param_dialog = ParameterDialog(self)
        self.wait_window(param_dialog)
        if param_dialog.result:
            self.input_params.append(param_dialog.result)
            self.input_listbox.insert(tk.END, param_dialog.result["name"])

    def _remove_input(self) -> None:
        """Remove input parameter"""
        selection = self.input_listbox.curselection()
        if selection:
            idx = selection[0]
            self.input_listbox.delete(idx)
            del self.input_params[idx]

    def _add_output(self) -> None:
        """Add output parameter"""
        param_dialog = ParameterDialog(self)
        self.wait_window(param_dialog)
        if param_dialog.result:
            self.output_params.append(param_dialog.result)
            self.output_listbox.insert(tk.END, param_dialog.result["name"])

    def _remove_output(self) -> None:
        """Remove output parameter"""
        selection = self.output_listbox.curselection()
        if selection:
            idx = selection[0]
            self.output_listbox.delete(idx)
            del self.output_params[idx]

    def _load_operation(self) -> None:
        """Load existing operation data"""
        if "name" in self.operation:
            self.name_var.set(self.operation["name"])
        if "description" in self.operation:
            self.desc_text.insert(1.0, self.operation["description"])

    def _save(self) -> None:
        """Save operation"""
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter an operation name")
            return

        self.result = {
            "name": name,
            "description": self.desc_text.get(1.0, tk.END).strip(),
            "input_parameters": self.input_params,
            "output_parameters": self.output_params,
        }
        self.destroy()


class SignalDialog(tk.Toplevel):
    """Dialog for creating/editing signals"""

    def __init__(self, parent, signal: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.title("Signal Editor")
        self.geometry("500x350")
        self.result = None
        self.signal = signal or {}
        self._create_widgets()
        if signal:
            self._load_signal()
        self.transient(parent)
        self.grab_set()

    def _create_widgets(self) -> None:
        """Create dialog widgets"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Signal Name
        ttk.Label(main_frame, text="Signal Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, sticky="w", pady=5)

        # Data Type
        ttk.Label(main_frame, text="Data Type:").grid(row=1, column=0, sticky="w", pady=5)
        self.datatype_var = tk.StringVar(value="uint32")
        datatype_combo = ttk.Combobox(
            main_frame,
            textvariable=self.datatype_var,
            values=["uint8", "uint16", "uint32", "uint64", "int8", "int16", "int32", "int64", "float32", "float64", "boolean", "string"],
            width=37,
            state="readonly"
        )
        datatype_combo.grid(row=1, column=1, sticky="w", pady=5)

        # Unit
        ttk.Label(main_frame, text="Unit:").grid(row=2, column=0, sticky="w", pady=5)
        self.unit_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.unit_var, width=40).grid(row=2, column=1, sticky="w", pady=5)

        # Description
        ttk.Label(main_frame, text="Description:").grid(row=3, column=0, sticky="nw", pady=5)
        self.desc_text = tk.Text(main_frame, height=3, width=40)
        self.desc_text.grid(row=3, column=1, sticky="w", pady=5)

        # Initial Value
        ttk.Label(main_frame, text="Initial Value:").grid(row=4, column=0, sticky="w", pady=5)
        self.init_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.init_var, width=40).grid(row=4, column=1, sticky="w", pady=5)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=20)
        ttk.Button(btn_frame, text="Save", command=self._save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=5)

    def _load_signal(self) -> None:
        """Load existing signal data"""
        if "name" in self.signal:
            self.name_var.set(self.signal["name"])
        if "data_type" in self.signal:
            self.datatype_var.set(self.signal["data_type"])
        if "unit" in self.signal:
            self.unit_var.set(self.signal["unit"])
        if "description" in self.signal:
            self.desc_text.insert(1.0, self.signal["description"])
        if "init_value" in self.signal:
            self.init_var.set(str(self.signal["init_value"]))

    def _save(self) -> None:
        """Save signal"""
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a signal name")
            return

        self.result = {
            "name": name,
            "data_type": self.datatype_var.get(),
            "unit": self.unit_var.get(),
            "description": self.desc_text.get(1.0, tk.END).strip(),
            "init_value": self.init_var.get() or None,
        }
        self.destroy()


class ParameterDialog(tk.Toplevel):
    """Dialog for creating/editing parameters"""

    def __init__(self, parent, parameter: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.title("Parameter Editor")
        self.geometry("500x400")
        self.result = None
        self.parameter = parameter or {}
        self._create_widgets()
        if parameter:
            self._load_parameter()
        self.transient(parent)
        self.grab_set()

    def _create_widgets(self) -> None:
        """Create dialog widgets"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Parameter Name
        ttk.Label(main_frame, text="Parameter Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, sticky="w", pady=5)

        # Parameter Type
        ttk.Label(main_frame, text="Type:").grid(row=1, column=0, sticky="w", pady=5)
        self.type_var = tk.StringVar(value="int")
        type_combo = ttk.Combobox(
            main_frame,
            textvariable=self.type_var,
            values=["int", "float", "string", "boolean", "enum"],
            width=37,
            state="readonly"
        )
        type_combo.grid(row=1, column=1, sticky="w", pady=5)

        # Description
        ttk.Label(main_frame, text="Description:").grid(row=2, column=0, sticky="nw", pady=5)
        self.desc_text = tk.Text(main_frame, height=3, width=40)
        self.desc_text.grid(row=2, column=1, sticky="w", pady=5)

        # Min Value
        ttk.Label(main_frame, text="Min Value:").grid(row=3, column=0, sticky="w", pady=5)
        self.min_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.min_var, width=40).grid(row=3, column=1, sticky="w", pady=5)

        # Max Value
        ttk.Label(main_frame, text="Max Value:").grid(row=4, column=0, sticky="w", pady=5)
        self.max_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.max_var, width=40).grid(row=4, column=1, sticky="w", pady=5)

        # Default Value
        ttk.Label(main_frame, text="Default Value:").grid(row=5, column=0, sticky="w", pady=5)
        self.default_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.default_var, width=40).grid(row=5, column=1, sticky="w", pady=5)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=20)
        ttk.Button(btn_frame, text="Save", command=self._save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=5)

    def _load_parameter(self) -> None:
        """Load existing parameter data"""
        if "name" in self.parameter:
            self.name_var.set(self.parameter["name"])
        if "type" in self.parameter:
            self.type_var.set(self.parameter["type"])
        if "description" in self.parameter:
            self.desc_text.insert(1.0, self.parameter["description"])

    def _save(self) -> None:
        """Save parameter"""
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a parameter name")
            return

        # Convert empty strings to None
        min_val = self.min_var.get() or None
        max_val = self.max_var.get() or None
        default_val = self.default_var.get() or None

        self.result = {
            "name": name,
            "type": self.type_var.get(),
            "description": self.desc_text.get(1.0, tk.END).strip(),
            "min_value": min_val,
            "max_value": max_val,
            "default_value": default_val,
        }
        self.destroy()
