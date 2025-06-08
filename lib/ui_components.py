"""
Reusable UI components for SolsScope PyQt6 interface
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QCheckBox, QPushButton, QTextEdit,
    QScrollArea, QFrame, QListWidget, QListWidgetItem,
    QSizePolicy, QSpacerItem, QMessageBox, QProgressBar,
    QComboBox, QSpinBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor

class ModernCard(QFrame):
    """A modern card-style container widget"""
    
    def __init__(self, title=None, parent=None):
        super().__init__(parent)
        self.setProperty("class", "info-card")
        self.setFrameStyle(QFrame.Shape.Box)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        if title:
            title_label = QLabel(title)
            title_font = title_label.font()
            title_font.setPointSize(11)
            title_font.setBold(True)
            title_label.setFont(title_font)
            layout.addWidget(title_label)
        
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)
    
    def add_widget(self, widget):
        """Add a widget to the card content"""
        self.content_layout.addWidget(widget)
    
    def add_layout(self, layout):
        """Add a layout to the card content"""
        self.content_layout.addLayout(layout)

class StatusIndicator(QLabel):
    """A status indicator with colored text and background"""
    
    def __init__(self, text="", status="neutral", parent=None):
        super().__init__(text, parent)
        self.set_status(status)
    
    def set_status(self, status):
        """Set the status type: running, stopped, warning, neutral"""
        status_classes = {
            'running': 'status-running',
            'stopped': 'status-stopped', 
            'warning': 'status-warning',
            'neutral': ''
        }
        
        class_name = status_classes.get(status, '')
        if class_name:
            self.setProperty("class", class_name)
        else:
            self.setProperty("class", None)
        
        # Force style refresh
        self.style().unpolish(self)
        self.style().polish(self)

class CollapsibleSection(QWidget):
    """A collapsible section widget"""
    
    def __init__(self, title="", parent=None, collapsed=True):
        super().__init__(parent)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Store the original title
        self.title = title
        self.is_collapsed = collapsed

        # Header
        self.header = QPushButton()
        self.header.setProperty("class", "secondary")
        self.header.setCheckable(True)
        self.header.setChecked(not collapsed)  # Inverted logic: checked = expanded
        self.header.clicked.connect(self.toggle_content)
        self.main_layout.addWidget(self.header)

        # Content container
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(16, 8, 16, 16)
        self.main_layout.addWidget(self.content_widget)

        # Set initial state
        if collapsed:
            self.content_widget.setVisible(False)
            self.header.setText(f"▶ {title}")
        else:
            self.content_widget.setVisible(True)
            self.header.setText(f"▼ {title}")
    
    def toggle_content(self):
        """Toggle the visibility of the content"""
        if self.header.isChecked():
            self.expand()
        else:
            self.collapse()

    def collapse(self):
        """Collapse the section"""
        self.is_collapsed = True
        self.content_widget.setVisible(False)
        self.header.setText(f"▶ {self.title}")

    def expand(self):
        """Expand the section"""
        self.is_collapsed = False
        self.content_widget.setVisible(True)
        self.header.setText(f"▼ {self.title}")
    
    def add_widget(self, widget):
        """Add a widget to the content area"""
        self.content_layout.addWidget(widget)
    
    def add_layout(self, layout):
        """Add a layout to the content area"""
        self.content_layout.addLayout(layout)

class ModernFormField(QWidget):
    """A modern form field with label and input"""
    
    valueChanged = pyqtSignal()
    
    def __init__(self, label_text, field_type="text", options=None, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(4)
        
        # Label
        self.label = QLabel(label_text)
        self.label.setStyleSheet("font-weight: 500; margin-bottom: 4px;")
        layout.addWidget(self.label)
        
        # Input field based on type
        if field_type == "text":
            self.input = QLineEdit()
            self.input.textChanged.connect(self.valueChanged.emit)
        elif field_type == "password":
            self.input = QLineEdit()
            self.input.setEchoMode(QLineEdit.EchoMode.Password)
            self.input.textChanged.connect(self.valueChanged.emit)
        elif field_type == "checkbox":
            self.input = QCheckBox()
            self.input.stateChanged.connect(self.valueChanged.emit)
        elif field_type == "number":
            self.input = QSpinBox()
            self.input.setRange(-999999, 999999)
            self.input.valueChanged.connect(self.valueChanged.emit)
        elif field_type == "decimal":
            self.input = QDoubleSpinBox()
            self.input.setRange(-999999.0, 999999.0)
            self.input.setDecimals(2)
            self.input.valueChanged.connect(self.valueChanged.emit)
        elif field_type == "combo":
            self.input = QComboBox()
            if options:
                self.input.addItems(options)
            self.input.currentTextChanged.connect(self.valueChanged.emit)
        else:
            self.input = QLineEdit()
            self.input.textChanged.connect(self.valueChanged.emit)
        
        layout.addWidget(self.input)
    
    def get_value(self):
        """Get the current value of the input field"""
        if isinstance(self.input, QLineEdit):
            return self.input.text()
        elif isinstance(self.input, QCheckBox):
            return self.input.isChecked()
        elif isinstance(self.input, (QSpinBox, QDoubleSpinBox)):
            return self.input.value()
        elif isinstance(self.input, QComboBox):
            return self.input.currentText()
        return None
    
    def set_value(self, value):
        """Set the value of the input field"""
        if isinstance(self.input, QLineEdit):
            self.input.setText(str(value))
        elif isinstance(self.input, QCheckBox):
            self.input.setChecked(bool(value))
        elif isinstance(self.input, (QSpinBox, QDoubleSpinBox)):
            self.input.setValue(value)
        elif isinstance(self.input, QComboBox):
            index = self.input.findText(str(value))
            if index >= 0:
                self.input.setCurrentIndex(index)
    
    def set_tooltip(self, tooltip):
        """Set tooltip for both label and input"""
        self.label.setToolTip(tooltip)
        self.input.setToolTip(tooltip)

class ModernListWidget(QWidget):
    """A modern list widget with add/remove functionality"""
    
    itemsChanged = pyqtSignal()
    
    def __init__(self, title="Items", parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: 500;")
        layout.addWidget(title_label)
        
        # List widget
        self.list_widget = QListWidget()
        self.list_widget.setMaximumHeight(120)
        layout.addWidget(self.list_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)
        
        self.add_input = QLineEdit()
        self.add_input.setPlaceholderText("Enter item to add...")
        self.add_input.returnPressed.connect(self.add_item)
        controls_layout.addWidget(self.add_input)
        
        self.add_button = QPushButton("Add")
        self.add_button.setProperty("class", "secondary")
        self.add_button.setMaximumWidth(60)
        self.add_button.clicked.connect(self.add_item)
        controls_layout.addWidget(self.add_button)
        
        self.remove_button = QPushButton("Remove")
        self.remove_button.setProperty("class", "error")
        self.remove_button.setMaximumWidth(80)
        self.remove_button.clicked.connect(self.remove_item)
        controls_layout.addWidget(self.remove_button)
        
        layout.addLayout(controls_layout)
    
    def add_item(self):
        """Add an item to the list"""
        text = self.add_input.text().strip()
        if text and not self.has_item(text):
            self.list_widget.addItem(text)
            self.add_input.clear()
            self.itemsChanged.emit()
    
    def remove_item(self):
        """Remove selected item from the list"""
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            self.list_widget.takeItem(current_row)
            self.itemsChanged.emit()
    
    def has_item(self, text):
        """Check if item already exists in the list"""
        for i in range(self.list_widget.count()):
            if self.list_widget.item(i).text() == text:
                return True
        return False
    
    def get_items(self):
        """Get all items in the list"""
        return [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
    
    def set_items(self, items):
        """Set the items in the list"""
        self.list_widget.clear()
        for item in items:
            self.list_widget.addItem(str(item))
        self.itemsChanged.emit()

class AutocraftPotionSelector(QWidget):
    """A modern selector for autocraft potions with individual toggle buttons"""

    valueChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Title and description
        title_label = QLabel("Potions to Auto Craft")
        title_label.setStyleSheet("font-weight: 600; font-size: 12px; margin-bottom: 4px;")
        layout.addWidget(title_label)

        desc_label = QLabel("Select which potions to automatically craft when Auto Craft Mode is enabled. You must be near the cauldron.")
        desc_label.setStyleSheet("color: #888; font-size: 10px; margin-bottom: 12px; font-style: italic;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Create a grid layout for potion buttons
        self.grid_widget = QWidget()
        self.grid_layout = QVBoxLayout(self.grid_widget)
        self.grid_layout.setSpacing(8)

        # Dictionary to store checkbox references
        self.potion_checkboxes = {}

        # Import the accepted potions list from constants
        from constants import ACCEPTEDPOTIONS

        # Group potions by category for better organization
        potion_groups = {
            "🧪 Basic Potions": [
                ("Potion of Bound", "Potion of Bound"),
                ("Heavenly Potion", "Heavenly Potion"),
                ("Warp Potion", "Warp Potion")
            ],
            "⚡ Godly Potions": [
                ("Godly Potion (Zeus)", "Godly Potion (Zeus)"),
                ("Godly Potion (Poseidon)", "Godly Potion (Poseidon)"),
                ("Godly Potion (Hades)", "Godly Potion (Hades)")
            ],
            "✨ Special Potions": [
                ("Godlike Potion", "Godlike Potion"),
                ("Jewelry Potion", "Jewelry Potion"),
                ("Zombie Potion", "Zombie Potion"),
                ("Rage Potion", "Rage Potion"),
                ("Diver Potion", "Diver Potion")
            ]
        }

        # Ensure all potions from ACCEPTEDPOTIONS are included
        all_grouped_potions = set()
        for group_potions in potion_groups.values():
            for _, potion_key in group_potions:
                all_grouped_potions.add(potion_key)

        # Add any missing potions to the Special Potions group
        missing_potions = set(ACCEPTEDPOTIONS) - all_grouped_potions
        if missing_potions:
            for potion in missing_potions:
                potion_groups["✨ Special Potions"].append((potion, potion))

        for group_name, potions in potion_groups.items():
            # Group header
            group_label = QLabel(group_name)
            group_label.setStyleSheet("font-weight: 500; color: #888; margin-top: 8px;")
            self.grid_layout.addWidget(group_label)

            # Create checkboxes for this group
            group_layout = QVBoxLayout()
            group_layout.setSpacing(4)

            for display_name, key in potions:
                checkbox = QCheckBox(display_name)
                checkbox.setStyleSheet("""
                    QCheckBox {
                        padding: 6px 12px;
                        margin-left: 16px;
                        margin: 2px;
                        border: 1px solid #555;
                        border-radius: 4px;
                        background-color: #2a2a2a;
                        color: #ffffff;
                    }
                    QCheckBox:hover {
                        background-color: #3a3a3a;
                        border-color: #777;
                    }
                    QCheckBox:checked {
                        background-color: #0d7377;
                        border-color: #14a085;
                        font-weight: bold;
                    }
                    QCheckBox::indicator {
                        width: 0px;
                        height: 0px;
                    }
                """)
                checkbox.stateChanged.connect(self.valueChanged.emit)
                self.potion_checkboxes[key] = checkbox
                group_layout.addWidget(checkbox)

            self.grid_layout.addLayout(group_layout)

        layout.addWidget(self.grid_widget)

    def get_value(self):
        """Get the current autocraft settings as a dictionary"""
        return {key: checkbox.isChecked() for key, checkbox in self.potion_checkboxes.items()}

    def set_value(self, value_dict):
        """Set the autocraft settings from a dictionary"""
        if isinstance(value_dict, dict):
            for key, checkbox in self.potion_checkboxes.items():
                checkbox.setChecked(value_dict.get(key, False))

class ProgressCard(ModernCard):
    """A card with progress indication"""

    def __init__(self, title="Progress", parent=None):
        super().__init__(title, parent)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.add_widget(self.progress_bar)

        self.status_label = QLabel("Ready")
        self.add_widget(self.status_label)

    def set_progress(self, value, status_text=""):
        """Set progress value and optional status text"""
        self.progress_bar.setValue(value)
        if status_text:
            self.status_label.setText(status_text)
