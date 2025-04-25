import sys
import os
from pathlib import Path

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QIcon

import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.backends.backend_qtagg import (
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure


matplotlib.use("QtAgg")

import novo_toolbox as nt

matplotlib.rcParams['savefig.format'] = 'svg'

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Plot Explorer")

        self.folder_icon = QIcon("./icons/folder.png")
        self.folder_open_icon = QIcon("./icons/folder_open.png")  # New icon for opened folders
        self.file_icon = QIcon("./icons/file.png")

        self.selected_measurement = None
        self.parameter_to_plot = "|Eps|" # TODO init otherwise
        self.x_axis = "Freq."
        self.comboempty = True
        self.stored_selection = []  # New attribute to store the selection

        # Main layout
        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout(main_widget)

        # Left column: Filetree and Plot button
        self.open_folder_button = QtWidgets.QPushButton("Open Folder")
        self.open_folder_button.clicked.connect(self.open_folder)
        self.file_tree = QtWidgets.QTreeWidget()
        self.file_tree.setHeaderHidden(True)  # Hide header
        self.file_tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.file_tree.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        init_dir = Path("./tests/testdata")
        init_dir = Path("../../03_Messergebnisse/032_Messergebnisse/Novocontrol")
        self.folder_path = init_dir  # Set the initial folder path
        self.load_folder(init_dir or Path.cwd())  # Load the current working directory

        self.plot_button = QtWidgets.QPushButton("Plot")
        self.plot_button.clicked.connect(self.plot_all)

        self.clear_selection_button = QtWidgets.QPushButton("Restore Selection")  # Repurpose button
        self.clear_selection_button.clicked.connect(self.restore_selection)  # Connect to new method

        self.copy_filepaths_button = QtWidgets.QPushButton("Copy Filepaths")  # New button
        self.copy_filepaths_button.clicked.connect(self.copy_filepaths_to_clipboard)  # Connect to new method

        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(self.open_folder_button)        
        left_layout.addWidget(self.file_tree)
        left_layout.addWidget(self.plot_button)
        left_layout.addWidget(self.clear_selection_button)  # Add the repurposed button
        left_layout.addWidget(self.copy_filepaths_button)  # Add the new button

        # Middle column: Matplotlib Canvas
        self.canvas = MplCanvas(self, width=10, height=6, dpi=100)
        toolbar = NavigationToolbar(self.canvas, self)
        middle_layout = QtWidgets.QVBoxLayout()
        middle_layout.addWidget(self.canvas)
        middle_layout.addWidget(toolbar)

        # Right column: Plot options and metadata
        right_layout = QtWidgets.QVBoxLayout()
        self.x_axis_dropdown = QtWidgets.QComboBox()
        self.x_axis_dropdown.currentTextChanged.connect(self.update_plot)  # Update plot when x-axis changes
        self.y_axis_dropdown = QtWidgets.QComboBox()
        self.y_axis_dropdown.currentTextChanged.connect(self.update_plot)  # Update plot when y-axis changes
        self.log_x_checkbox = QtWidgets.QCheckBox("Logarithmic X")
        self.log_x_checkbox.setChecked(True)  # Set default to checked
        self.log_x_checkbox.stateChanged.connect(self.update_plot)
        self.log_y_checkbox = QtWidgets.QCheckBox("Logarithmic Y")
        self.log_y_checkbox.stateChanged.connect(self.update_plot)
        self.sample_name_field = QtWidgets.QLineEdit()
        self.sample_name_field.editingFinished.connect(self.update_plot)  # Update plot when sample name changes
        self.sample_name_field.returnPressed.connect(self.update_plot)  # Update plot when Enter is pressed
        self.time_label = QtWidgets.QLabel()
        self.meanbounds_checkbox = QtWidgets.QCheckBox("Mean and Bounds")
        self.meanbounds_checkbox.stateChanged.connect(self.update_plot)

        right_layout.addWidget(QtWidgets.QLabel("X Axis:"))
        right_layout.addWidget(self.x_axis_dropdown)
        right_layout.addWidget(QtWidgets.QLabel("Y Axis:"))
        right_layout.addWidget(self.y_axis_dropdown)
        right_layout.addWidget(self.log_x_checkbox)
        right_layout.addWidget(self.log_y_checkbox)
        right_layout.addWidget(self.meanbounds_checkbox)
        right_layout.addWidget(QtWidgets.QLabel("Sample Name:"))
        right_layout.addWidget(self.sample_name_field)
        right_layout.addWidget(QtWidgets.QLabel("Time:"))
        right_layout.addWidget(self.time_label)
        right_layout.addStretch()

        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        left_container = QtWidgets.QWidget()
        left_container.setLayout(left_layout)

        middle_container = QtWidgets.QWidget()
        middle_container.setLayout(middle_layout)

        right_container = QtWidgets.QWidget()
        right_container.setLayout(right_layout)

        splitter.addWidget(left_container)
        splitter.addWidget(middle_container)
        splitter.addWidget(right_container)
        splitter.setSizes([200, 400, 200])  # Set initial sizes for the splitter


        # Add columns to main layout
        # main_layout.addLayout(left_layout)
        # main_layout.addLayout(middle_layout)
        # main_layout.addLayout(right_layout)
        main_layout.addWidget(splitter)

        # Set main widget
        self.setCentralWidget(main_widget)


    def open_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            try:
                folder_path = Path(folder)
                self.folder_path = folder_path  # Update the folder path
                # Set the header to the selected folder name
                self.file_tree.setHeaderLabel(folder_path.name)
                self.file_tree.setHeaderHidden(False)  # Show header
                self.load_folder(folder_path)
            except Exception as e:
                print(f"Failed to load the folder: {e}")

    def load_folder(self, folder, parent_item=None):
        folder = Path(folder)  # Ensure folder is a Path object
        dirs = []
        files = []

        for entry in folder.iterdir():
            if entry.name.startswith('.'):
                continue
            if entry.is_dir():
                dirs.append(entry)
            else:
                if entry.suffix.lower() == ".txt":
                    files.append(entry)

        dirs.sort(key=lambda e: e.name.lower())
        files.sort(key=lambda e: e.name.lower())

        if parent_item is None:
            self.file_tree.clear()
            add_item = self.file_tree
        else:
            parent_item.takeChildren()
            add_item = parent_item
            parent_item.setIcon(0, self.folder_open_icon)

        for entries in [dirs, files]:
            for entry in entries:
                icon = self.folder_icon if entry.is_dir() else self.file_icon
                item = QtWidgets.QTreeWidgetItem(add_item)
                item.setIcon(0, icon)
                item.setText(0, entry.name)
                item.setData(0, QtCore.Qt.ItemDataRole.UserRole, str(entry))

        if parent_item:
            QtCore.QTimer.singleShot(100, lambda: parent_item.setExpanded(True))

        if parent_item is None:
            self.file_tree.expandAll()

    def on_item_double_clicked(self, item, column):
        path = Path(item.data(column, QtCore.Qt.ItemDataRole.UserRole))
        if path.is_file():
            self.handle_open(path)
        elif path.is_dir():
            item_to_change = self.file_tree.selectedItems()[0]
            self.load_folder(path, item_to_change)

    def handle_open(self, file_item):
        print(f"Opening file: {file_item}")
        self.selected_measurement = nt.Measurement(filepath=str(file_item))
        self.update_metadata()
        self.update_plot()


    def update_plot(self):
        self.canvas.axes.cla()
        self.parameter_to_plot = self.y_axis_dropdown.currentText() or self.parameter_to_plot
        self.x_axis = self.x_axis_dropdown.currentText() or self.x_axis
        if self.comboempty:
            return
        try:
            if isinstance(self.selected_measurement, nt.MeasurementGroup):
                if self.meanbounds_checkbox.isChecked():
                    self.selected_measurement.plot_mean_bounds(self.parameter_to_plot, ax=self.canvas.axes, label=self.sample_name_field.text(), x=self.x_axis)
                else:
                    self.selected_measurement.plot_singles(self.parameter_to_plot, ax=self.canvas.axes, x=self.x_axis)
            else:
                self.selected_measurement.plot(self.parameter_to_plot, ax=self.canvas.axes, label=self.sample_name_field.text(), x=self.x_axis)
        except KeyError as e:
            QtWidgets.QMessageBox.warning(self, "Key Error", f"Key '{self.parameter_to_plot}' or '{self.x_axis}' not found.")
            print(e)
        self.canvas.axes.grid(True)
        self.canvas.axes.set_xscale(self.log_x_checkbox.isChecked() and "log" or "linear")
        self.canvas.axes.set_yscale(self.log_y_checkbox.isChecked() and "log" or "linear")
        self.canvas.axes.set_ylabel(f"{self.parameter_to_plot}  [{self.selected_measurement.einheiten[self.parameter_to_plot]}]" if self.selected_measurement.einheiten[self.parameter_to_plot] else self.parameter_to_plot)


        self.canvas.draw()

    def update_metadata(self):
        if isinstance(self.selected_measurement, nt.MeasurementGroup):
            m  = self.selected_measurement.mean()
        else:
            m = self.selected_measurement
        if m:
            self.sample_name_field.setText(m.metadata['Sample'])
            self.time_label.setText(m.metadata['Date'] + '  ' + m.metadata['Time'])
            curr_x = self.x_axis
            curr_y = self.parameter_to_plot
            self.x_axis_dropdown.clear()
            self.y_axis_dropdown.clear()
            self.comboempty = True
            self.x_axis_dropdown.addItems(m.einheiten.keys())
            self.y_axis_dropdown.addItems(m.einheiten.keys())
            if curr_y in m.einheiten.keys():
                self.y_axis_dropdown.setCurrentText(curr_y)
            if curr_x in m.einheiten.keys():
                self.x_axis_dropdown.setCurrentText(curr_x)
            self.comboempty = False

        else:
            self.sample_name_field.clear()
            self.time_label.clear()
            self.x_axis_dropdown.clear()
            self.y_axis_dropdown.clear()
            self.comboempty = True

    def plot_all(self):
        """Store the current selection and plot the selected measurements."""
        self.stored_selection = self.file_tree.selectedItems()  # Store the current selection
        if not self.stored_selection:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a measurement to plot.")
            return

        self.selected_measurement = nt.MeasurementGroup()
        for item in self.stored_selection:
            path = Path(item.data(0, QtCore.Qt.ItemDataRole.UserRole))
            if path.is_file():
                measurement = nt.Measurement(filepath=str(path))
                self.selected_measurement.append_measurement(measurement)

        self.update_metadata()
        self.update_plot()

    def restore_selection(self):
        """Restore the previously stored selection."""
        if not self.stored_selection:
            QtWidgets.QMessageBox.information(self, "No Stored Selection", "There is no stored selection to restore.")
            return

        # Clear current selection
        for item in self.file_tree.selectedItems():
            item.setSelected(False)

        # Restore the stored selection
        for item in self.stored_selection:
            item.setSelected(True)

    def copy_filepaths_to_clipboard(self):
        """Copy the filepaths of selected items to the clipboard."""
        selected_items = self.file_tree.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select at least one item.")
            return

        base_dir = Path(self.folder_path.resolve()) # Get the base directory from the header
        print(f"Base directory: {base_dir}")
        filepaths = [
            str(Path(item.data(0, QtCore.Qt.ItemDataRole.UserRole)).resolve().relative_to(base_dir))
            for item in selected_items
        ]

        if len(filepaths) == 1:
            clipboard_content = f'"{filepaths[0].replace("\\", "\\\\")}"'
        else:
            clipboard_content = str(filepaths)

        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(clipboard_content)
        QtWidgets.QMessageBox.information(self, "Copied to Clipboard", "Filepaths copied to clipboard.")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
