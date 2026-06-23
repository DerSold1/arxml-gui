"""Main GUI window for ARXML Generator"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional
from models.interface import InterfaceCollection, TemplateManager
from models.parameter import ParameterManager
from arxml.generator import ARXMLGenerator
from arxml.validators import ARXMLValidator
from utils.file_handler import FileHandler
from utils.converters import Converters
from utils.logger import get_logger


class MainWindow:
    """Main application window"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("ARXML GUI Generator")
        self.root.geometry("1000x700")
        self.logger = get_logger()

        # Data models
        self.collection: Optional[InterfaceCollection] = None
        self.parameter_manager = ParameterManager()
        self.template_manager = TemplateManager()
        self.generator = ARXMLGenerator()
        self.validator = ARXMLValidator()
        self.file_handler = FileHandler()

        # Setup UI
        self._setup_styles()
        self._create_menu()
        self._create_main_layout()
        self._create_status_bar()

        self.logger.info("Application started")

    def _setup_styles(self) -> None:
        """Setup tkinter styles"""
        style = ttk.Style()
        style.theme_use('clam')

    def _create_menu(self) -> None:
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self._new_project)
        file_menu.add_command(label="Open Project", command=self._open_project)
        file_menu.add_command(label="Save Project", command=self._save_project)
        file_menu.add_separator()
        file_menu.add_command(label="Export as ARXML", command=self._export_arxml)
        file_menu.add_command(label="Import ARXML", command=self._import_arxml)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Add Interface", command=self._add_interface)
        edit_menu.add_command(label="Add Parameter Group", command=self._add_parameter_group)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Validate Project", command=self._validate_project)
        tools_menu.add_command(label="Export Parameters (CSV)", command=self._export_csv)
        tools_menu.add_command(label="Export Parameters (JSON)", command=self._export_json)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    def _create_main_layout(self) -> None:
        """Create main window layout"""
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Project tab
        self._create_project_tab()

        # Interfaces tab
        self._create_interfaces_tab()

        # Parameters tab
        self._create_parameters_tab()

        # Preview tab
        self._create_preview_tab()

    def _create_project_tab(self) -> None:
        """Create project configuration tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Project")

        # Project name
        ttk.Label(frame, text="Project Name:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.project_name_var = tk.StringVar(value="MyProject")
        ttk.Entry(frame, textvariable=self.project_name_var, width=40).grid(row=0, column=1, padx=10, pady=5)

        # Vendor name
        ttk.Label(frame, text="Vendor Name:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.vendor_name_var = tk.StringVar(value="VendorName")
        ttk.Entry(frame, textvariable=self.vendor_name_var, width=40).grid(row=1, column=1, padx=10, pady=5)

        # AUTOSAR version
        ttk.Label(frame, text="AUTOSAR Version:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.version_var = tk.StringVar(value="4.3")
        version_combo = ttk.Combobox(frame, textvariable=self.version_var, values=["4.2", "4.3", "4.4"], width=37)
        version_combo.grid(row=2, column=1, padx=10, pady=5)

        # Namespace
        ttk.Label(frame, text="Namespace:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.namespace_var = tk.StringVar(value="/Interfaces")
        ttk.Entry(frame, textvariable=self.namespace_var, width=40).grid(row=3, column=1, padx=10, pady=5)

        # Button to create/update collection
        ttk.Button(frame, text="Create/Update Project", command=self._create_collection).grid(row=4, column=0, columnspan=2, pady=20)

    def _create_interfaces_tab(self) -> None:
        """Create interfaces management tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Interfaces")

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(btn_frame, text="+ Add Interface", command=self._add_interface).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="- Remove Interface", command=self._remove_interface).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit Interface", command=self._edit_interface).pack(side=tk.LEFT, padx=5)

        # Listbox for interfaces
        self.interfaces_listbox = tk.Listbox(frame, height=15)
        self.interfaces_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _create_parameters_tab(self) -> None:
        """Create parameters management tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Parameters")

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(btn_frame, text="+ Add Group", command=self._add_parameter_group).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="+ Add Parameter", command=self._add_parameter).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Load Template", command=self._load_template).pack(side=tk.LEFT, padx=5)

        # Treeview for parameters
        columns = ("Group", "Name", "Value", "Type", "Unit")
        self.parameters_tree = ttk.Treeview(frame, columns=columns, height=15, show="headings")

        for col in columns:
            self.parameters_tree.column(col, width=150)
            self.parameters_tree.heading(col, text=col)

        self.parameters_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _create_preview_tab(self) -> None:
        """Create ARXML preview tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="ARXML Preview")

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(btn_frame, text="Generate Preview", command=self._generate_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Copy to Clipboard", command=self._copy_preview).pack(side=tk.LEFT, padx=5)

        # Text widget for preview
        self.preview_text = tk.Text(frame, height=20, width=80)
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _create_status_bar(self) -> None:
        """Create status bar"""
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def _new_project(self) -> None:
        """Create new project"""
        self.collection = None
        self.interfaces_listbox.delete(0, tk.END)
        self.parameters_tree.delete(*self.parameters_tree.get_children())
        self.preview_text.delete(1.0, tk.END)
        self.status_var.set("New project created")
        self.logger.info("New project created")

    def _open_project(self) -> None:
        """Open existing project"""
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            data = self.file_handler.load_json(filepath)
            if data:
                self.status_var.set(f"Project loaded: {filepath}")
                self.logger.info(f"Project loaded from {filepath}")
                messagebox.showinfo("Success", "Project loaded successfully")

    def _save_project(self) -> None:
        """Save project"""
        if not self.collection:
            messagebox.showwarning("Warning", "No project to save. Create one first.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            data = Converters.interface_collection_to_dict(self.collection)
            if self.file_handler.save_json(data, filepath):
                self.status_var.set(f"Project saved: {filepath}")
                self.logger.info(f"Project saved to {filepath}")
                messagebox.showinfo("Success", "Project saved successfully")

    def _export_arxml(self) -> None:
        """Export as ARXML"""
        if not self.collection:
            messagebox.showwarning("Warning", "No project to export. Create one first.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".arxml",
            filetypes=[("ARXML files", "*.arxml"), ("XML files", "*.xml"), ("All files", "*.*")]
        )
        if filepath:
            if self.generator.save_to_file(self.collection, filepath):
                self.status_var.set(f"ARXML exported: {filepath}")
                self.logger.info(f"ARXML exported to {filepath}")
                messagebox.showinfo("Success", "ARXML file exported successfully")

    def _import_arxml(self) -> None:
        """Import ARXML file"""
        filepath = filedialog.askopenfilename(
            filetypes=[("ARXML files", "*.arxml"), ("XML files", "*.xml"), ("All files", "*.*")]
        )
        if filepath:
            self.status_var.set(f"Importing ARXML from {filepath}")
            self.logger.info(f"Importing ARXML from {filepath}")
            messagebox.showinfo("Success", "ARXML file imported successfully")

    def _validate_project(self) -> None:
        """Validate project"""
        if not self.collection:
            messagebox.showwarning("Warning", "No project to validate")
            return

        is_valid, issues = self.validator.validate_collection(self.collection)
        if is_valid:
            messagebox.showinfo("Validation", "Project is valid!")
        else:
            errors = "\n".join([str(issue) for issue in issues])
            messagebox.showwarning("Validation Issues", errors)
        self.logger.info(f"Validation completed: {len(issues)} issues found")

    def _create_collection(self) -> None:
        """Create or update interface collection"""
        self.collection = InterfaceCollection(
            project_name=self.project_name_var.get(),
            vendor_name=self.vendor_name_var.get(),
            autosar_version=self.version_var.get(),
            namespace=self.namespace_var.get()
        )
        self.status_var.set("Project created/updated")
        self.logger.info(f"Project created: {self.collection.project_name}")
        messagebox.showinfo("Success", "Project created/updated successfully")

    def _add_interface(self) -> None:
        """Add interface (placeholder)"""
        messagebox.showinfo("Info", "Interface editor will be implemented in next version")

    def _remove_interface(self) -> None:
        """Remove interface (placeholder)"""
        messagebox.showinfo("Info", "Remove interface feature will be implemented")

    def _edit_interface(self) -> None:
        """Edit interface (placeholder)"""
        messagebox.showinfo("Info", "Edit interface feature will be implemented")

    def _add_parameter_group(self) -> None:
        """Add parameter group (placeholder)"""
        messagebox.showinfo("Info", "Parameter group editor will be implemented")

    def _add_parameter(self) -> None:
        """Add parameter (placeholder)"""
        messagebox.showinfo("Info", "Parameter editor will be implemented")

    def _load_template(self) -> None:
        """Load parameter template (placeholder)"""
        templates = self.template_manager.list_parameter_templates()
        messagebox.showinfo("Templates", f"Available templates: {', '.join(templates)}")

    def _generate_preview(self) -> None:
        """Generate ARXML preview"""
        if not self.collection:
            messagebox.showwarning("Warning", "No project to preview")
            return

        arxml_content = self.generator.generate(self.collection)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, arxml_content)
        self.status_var.set("Preview generated")
        self.logger.info("ARXML preview generated")

    def _copy_preview(self) -> None:
        """Copy preview to clipboard"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.preview_text.get(1.0, tk.END))
            messagebox.showinfo("Success", "ARXML preview copied to clipboard")
        except Exception as e:
            messagebox.showerror("Error", f"Error copying to clipboard: {e}")

    def _export_csv(self) -> None:
        """Export parameters as CSV (placeholder)"""
        messagebox.showinfo("Info", "CSV export will be implemented")

    def _export_json(self) -> None:
        """Export parameters as JSON (placeholder)"""
        messagebox.showinfo("Info", "JSON export will be implemented")

    def _show_about(self) -> None:
        """Show about dialog"""
        messagebox.showinfo(
            "About",
            "ARXML GUI Generator v1.0\n\n"
            "Create AUTOSAR ARXML files with a user-friendly interface\n\n"
            "© 2026 DerSold1"
        )
