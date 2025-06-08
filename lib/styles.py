"""
Modern styling and themes for SolsScope PyQt6 UI
"""

# Color palette for modern design
COLORS = {
    # Light theme
    'light': {
        'primary': '#2563eb',      # Blue
        'primary_hover': '#1d4ed8',
        'secondary': '#64748b',    # Slate
        'success': '#059669',      # Green
        'warning': '#d97706',      # Orange
        'error': '#dc2626',        # Red
        'background': '#ffffff',
        'surface': '#f8fafc',
        'surface_hover': '#f1f5f9',
        'border': '#e2e8f0',
        'text_primary': '#0f172a',
        'text_secondary': '#475569',
        'text_muted': '#94a3b8',
    },
    # Dark theme
    'dark': {
        'primary': '#4f9eff',      # Brighter blue
        'primary_hover': '#3b82f6',
        'secondary': '#8b9dc3',    # Lighter slate
        'success': '#22c55e',      # Brighter green
        'warning': '#fbbf24',      # Brighter orange
        'error': '#f87171',        # Brighter red
        'background': '#121212',   # Very dark background
        'surface': '#1e1e1e',      # Dark surface
        'surface_hover': '#2a2a2a', # Hover state
        'border': '#404040',       # Visible borders
        'text_primary': '#ffffff', # Pure white text
        'text_secondary': '#e5e5e5', # Very light gray text
        'text_muted': '#b0b0b0',   # Muted but visible text
    }
}

def get_main_style(theme='light'):
    """Get the main application stylesheet"""
    colors = COLORS[theme]
    
    return f"""
    /* Main Application */
    QMainWindow {{
        background-color: {colors['background']};
        color: {colors['text_primary']};
        font-family: 'Segoe UI', 'Arial', sans-serif;
        font-size: 9pt;
    }}
    
    /* Tab Widget */
    QTabWidget::pane {{
        border: 1px solid {colors['border']};
        background-color: {colors['background']};
        border-radius: 8px;
        margin-top: 2px;
    }}

    QTabWidget > QWidget {{
        background-color: {colors['background']};
    }}
    
    QTabWidget::tab-bar {{
        alignment: left;
    }}
    
    QTabBar::tab {{
        background-color: {colors['surface']};
        color: {colors['text_secondary']};
        border: 1px solid {colors['border']};
        border-bottom: none;
        padding: 8px 16px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        min-width: 80px;
    }}
    
    QTabBar::tab:selected {{
        background-color: {colors['primary']};
        color: white;
        border-color: {colors['primary']};
    }}
    
    QTabBar::tab:hover:!selected {{
        background-color: {colors['surface_hover']};
        color: {colors['text_primary']};
    }}
    
    /* Group Boxes */
    QGroupBox {{
        font-weight: 600;
        color: {colors['text_primary']};
        border: 2px solid {colors['border']};
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 8px;
        background-color: {colors['surface']};
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 8px 0 8px;
        background-color: {colors['surface']};
        color: {colors['primary']};
    }}
    """

def get_form_style(theme='light'):
    """Get form controls stylesheet"""
    colors = COLORS[theme]
    
    return f"""
    /* Labels */
    QLabel {{
        color: {colors['text_primary']};
        font-weight: 500;
    }}
    
    /* Line Edits */
    QLineEdit {{
        border: 2px solid {colors['border']};
        border-radius: 6px;
        padding: 8px 12px;
        background-color: {colors['background']};
        color: {colors['text_primary']};
        font-size: 9pt;
    }}
    
    QLineEdit:focus {{
        border-color: {colors['primary']};
        outline: none;
    }}
    
    QLineEdit:hover {{
        border-color: {colors['secondary']};
    }}
    
    /* Check Boxes */
    QCheckBox {{
        color: {colors['text_primary']};
        spacing: 8px;
    }}
    
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {colors['border']};
        border-radius: 4px;
        background-color: {colors['background']};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {colors['primary']};
        border-color: {colors['primary']};
    }}
    
    QCheckBox::indicator:hover {{
        border-color: {colors['primary']};
    }}
    """

def get_button_style(theme='light'):
    """Get button stylesheet"""
    colors = COLORS[theme]
    
    return f"""
    /* Primary Buttons */
    QPushButton {{
        background-color: {colors['primary']};
        color: white;
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: 600;
        font-size: 9pt;
        min-height: 16px;
    }}
    
    QPushButton:hover {{
        background-color: {colors['primary_hover']};
    }}
    
    QPushButton:pressed {{
        background-color: {colors['primary_hover']};
    }}
    
    QPushButton:disabled {{
        background-color: {colors['border']};
        color: {colors['text_muted']};
    }}
    
    /* Secondary Buttons */
    QPushButton[class="secondary"] {{
        background-color: {colors['surface']};
        color: {colors['text_primary']};
        border: 2px solid {colors['border']};
    }}
    
    QPushButton[class="secondary"]:hover {{
        background-color: {colors['surface_hover']};
        border-color: {colors['secondary']};
    }}
    
    /* Success Buttons */
    QPushButton[class="success"] {{
        background-color: {colors['success']};
    }}
    
    QPushButton[class="success"]:hover {{
        background-color: #047857;
    }}
    
    /* Warning Buttons */
    QPushButton[class="warning"] {{
        background-color: {colors['warning']};
    }}
    
    QPushButton[class="warning"]:hover {{
        background-color: #b45309;
    }}
    
    /* Error Buttons */
    QPushButton[class="error"] {{
        background-color: {colors['error']};
    }}
    
    QPushButton[class="error"]:hover {{
        background-color: #b91c1c;
    }}
    """

def get_list_style(theme='light'):
    """Get list widget stylesheet"""
    colors = COLORS[theme]

    return f"""
    /* List Widgets */
    QListWidget {{
        border: 2px solid {colors['border']};
        border-radius: 6px;
        background-color: {colors['background']};
        color: {colors['text_primary']};
        padding: 4px;
        outline: none;
    }}

    QListWidget:focus {{
        border-color: {colors['primary']};
    }}

    QListWidget::item {{
        padding: 6px 8px;
        border-radius: 4px;
        margin: 1px;
    }}

    QListWidget::item:selected {{
        background-color: {colors['primary']};
        color: white;
    }}

    QListWidget::item:hover:!selected {{
        background-color: {colors['surface_hover']};
    }}
    """

def get_text_edit_style(theme='light'):
    """Get text edit stylesheet"""
    colors = COLORS[theme]

    return f"""
    /* Text Edit */
    QTextEdit {{
        border: 2px solid {colors['border']};
        border-radius: 6px;
        background-color: {colors['background']};
        color: {colors['text_primary']};
        padding: 8px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 8pt;
        line-height: 1.4;
    }}

    QTextEdit:focus {{
        border-color: {colors['primary']};
    }}
    """

def get_scroll_area_style(theme='light'):
    """Get scroll area stylesheet"""
    colors = COLORS[theme]

    return f"""
    /* Scroll Areas */
    QScrollArea {{
        border: 1px solid {colors['border']};
        background-color: {colors['background']};
        border-radius: 6px;
    }}

    QScrollArea > QWidget > QWidget {{
        background-color: {colors['background']};
    }}

    QScrollBar:vertical {{
        background-color: {colors['surface']};
        width: 12px;
        border-radius: 6px;
        margin: 0;
    }}

    QScrollBar::handle:vertical {{
        background-color: {colors['border']};
        border-radius: 6px;
        min-height: 20px;
        margin: 2px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: {colors['secondary']};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
        width: 0;
    }}

    QScrollBar:horizontal {{
        background-color: {colors['surface']};
        height: 12px;
        border-radius: 6px;
        margin: 0;
    }}

    QScrollBar::handle:horizontal {{
        background-color: {colors['border']};
        border-radius: 6px;
        min-width: 20px;
        margin: 2px;
    }}

    QScrollBar::handle:horizontal:hover {{
        background-color: {colors['secondary']};
    }}

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        height: 0;
        width: 0;
    }}
    """

def get_status_style(theme='light'):
    """Get status indicator stylesheet"""
    colors = COLORS[theme]

    return f"""
    /* Status Indicators */
    QLabel[class="status-running"] {{
        color: {colors['success']};
        font-weight: 600;
        padding: 4px 8px;
        border-radius: 4px;
        background-color: rgba(5, 150, 105, 0.1);
    }}

    QLabel[class="status-stopped"] {{
        color: {colors['error']};
        font-weight: 600;
        padding: 4px 8px;
        border-radius: 4px;
        background-color: rgba(220, 38, 38, 0.1);
    }}

    QLabel[class="status-warning"] {{
        color: {colors['warning']};
        font-weight: 600;
        padding: 4px 8px;
        border-radius: 4px;
        background-color: rgba(217, 119, 6, 0.1);
    }}

    QLabel[class="info-card"] {{
        background-color: {colors['surface']};
        border: 1px solid {colors['border']};
        border-radius: 8px;
        padding: 12px;
        margin: 4px;
    }}
    """

def get_widget_style(theme='light'):
    """Get additional widget styling"""
    colors = COLORS[theme]

    return f"""
    /* Splitter */
    QSplitter {{
        background-color: {colors['background']};
    }}

    QSplitter::handle {{
        background-color: {colors['border']};
    }}

    QSplitter::handle:horizontal {{
        width: 2px;
    }}

    QSplitter::handle:vertical {{
        height: 2px;
    }}

    /* Widget backgrounds */
    QWidget {{
        background-color: {colors['background']};
        color: {colors['text_primary']};
    }}

    /* Menu Bar */
    QMenuBar {{
        background-color: {colors['surface']};
        color: {colors['text_primary']};
        border-bottom: 1px solid {colors['border']};
    }}

    QMenuBar::item {{
        background-color: transparent;
        padding: 4px 8px;
    }}

    QMenuBar::item:selected {{
        background-color: {colors['primary']};
        color: white;
    }}

    /* Tool Bar */
    QToolBar {{
        background-color: {colors['surface']};
        border: 1px solid {colors['border']};
        spacing: 4px;
        padding: 4px;
    }}

    /* Status Bar */
    QStatusBar {{
        background-color: {colors['surface']};
        color: {colors['text_primary']};
        border-top: 1px solid {colors['border']};
    }}
    """

def get_complete_stylesheet(theme='light'):
    """Get the complete application stylesheet"""
    return (
        get_main_style(theme) +
        get_form_style(theme) +
        get_button_style(theme) +
        get_list_style(theme) +
        get_text_edit_style(theme) +
        get_scroll_area_style(theme) +
        get_status_style(theme) +
        get_widget_style(theme)
    )
