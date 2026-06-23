"""Interface Editor for managing ARXML interfaces"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
from models.interface import InterfaceCollection
from models.types import InterfaceElement, InterfaceType
from gui.dialogs import InterfaceDialog


class InterfaceEditor(ttk.Frame):
    """Widget for editing interfaces"""

    def __init__(self, parent, collection: Optional[InterfaceCollection] = None):
        super().__init__(parent)
        self.collection = collection
        self.parent_window = parent
        self._create_widgets()
        self._refresh_list()

    def _create_widgets(self) -> None:
        """Create interface editor widgets"""
        # Button frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(btn_frame, text="+ Add Interface", command=self._add_interface).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="- Remove Interface", command=self._remove_interface).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit Interface", command=self._edit_interface).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self._refresh_list).pack(side=tk.RIGHT, padx=5)

        # Treeview for interfaces
        columns = ("Name", "Type", "Description")
        self.tree = ttk.Treeview(self, columns=columns, height=15, show="headings")

        self.tree.column("Name", width=150)
        self.tree.column("Type", width=100)
        self.tree.column("Description", width=300)

        self.tree.heading("Name", text="Name")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Description", text="Description")

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=scrollbar.set)

    def set_collection(self, collection: InterfaceCollection) -> None:
        """Set the interface collection"""
        self.collection = collection
        self._refresh_list()

    def _refresh_list(self) -> None:
        """Refresh the interfaces list"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add interfaces from collection
        if self.collection:
            for name, interface in self.collection.interfaces.items():
                self.tree.insert(
                    "",
                    tk.END,
                    text=name,
                    values=(
                        interface.name,
                        interface.element_type.value,
                        interface.description[:50] + "..." if len(interface.description) > 50 else interface.description
                    )
                )

    def _add_interface(self) -> None:
        """Add new interface"""
        if not self.collection:
            messagebox.showwarning("Warning", "Please create a project first")
            return

        dialog = InterfaceDialog(self.parent_window)
        self.parent_window.wait_window(dialog)

        if dialog.result:
            interface = dialog.result
            if interface.name in self.collection.interfaces:
                messagebox.showerror("Error", f"Interface '{interface.name}' already exists")
                return

            self.collection.add_interface(interface)
            self._refresh_list()
            messagebox.showinfo("Success", f"Interface '{interface.name}' added successfully")

    def _remove_interface(self) -> None:
        """Remove selected interface"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an interface to remove")
            return

        item = selection[0]
        interface_name = self.tree.item(item, "values")[0]

        if messagebox.askyesno("Confirm", f"Remove interface '{interface_name}'?"):
            if self.collection.remove_interface(interface_name):
                self._refresh_list()
                messagebox.showinfo("Success", f"Interface '{interface_name}' removed")
            else:
                messagebox.showerror("Error", "Could not remove interface")

    def _edit_interface(self) -> None:
        """Edit selected interface"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an interface to edit")
            return

        item = selection[0]
        interface_name = self.tree.item(item, "values")[0]
        interface = self.collection.get_interface(interface_name)

        if not interface:
            messagebox.showerror("Error", "Interface not found")
            return

        dialog = InterfaceDialog(self.parent_window, interface)
        self.parent_window.wait_window(dialog)

        if dialog.result:
            # Remove old interface and add updated one
            self.collection.remove_interface(interface_name)
            self.collection.add_interface(dialog.result)
            self._refresh_list()
            messagebox.showinfo("Success", "Interface updated successfully")
