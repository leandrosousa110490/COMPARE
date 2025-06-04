from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QTextEdit, QFrame,
                             QFileDialog, QMenu, QAction, QToolBar, QMessageBox,
                             QStyle)
from PyQt5.QtGui import QTextCharFormat, QColor, QSyntaxHighlighter, QFont, QIcon, QDragEnterEvent, QDropEvent, QPainter
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSettings, QUrl, QMimeData, QSize, QRect
from difflib import SequenceMatcher
import sys
import os
import json

class DiffHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for showing differences between texts.
    
    This highlighter compares the current text with another text and highlights
    insertions, deletions, and modifications with different colors.
    
    Attributes:
        other_text (str): The text to compare against
        enabled (bool): Whether highlighting is enabled
        is_left (bool): Whether this is the left (first) text area
    """
    
    def __init__(self, parent, other_text="", is_left=True):
        """Initialize the DiffHighlighter.
        
        Args:
            parent (QTextDocument): The text document to highlight
            other_text (str): The text to compare against
            is_left (bool): Whether this is the left (first) text area
        """
        super().__init__(parent)
        self.other_text = other_text
        self.enabled = True
        self.is_left = is_left
        
        # Create formats for different types of differences
        self.deletion_format = QTextCharFormat()
        self.deletion_format.setBackground(QColor("#ffebee"))  # Light red
        self.deletion_format.setForeground(QColor("#d32f2f"))  # Dark red
        
        self.insertion_format = QTextCharFormat()
        self.insertion_format.setBackground(QColor("#e8f5e9"))  # Light green
        self.insertion_format.setForeground(QColor("#2e7d32"))  # Dark green
        
        self.modification_format = QTextCharFormat()
        self.modification_format.setBackground(QColor("#fff3e0"))  # Light orange
        self.modification_format.setForeground(QColor("#ef6c00"))  # Dark orange
        
        self.equal_format = QTextCharFormat()
        self.equal_format.setBackground(QColor("#ffffff"))  # White background
        self.equal_format.setForeground(QColor("#000000"))  # Black text

    def set_other_text(self, text):
        if self.enabled:
            self.other_text = text
            self.rehighlight()

    def highlightBlock(self, text):
        if not self.enabled or not text:
            return
            
        if not self.other_text:
            # No comparison text, show normal formatting
            self.setFormat(0, len(text), self.equal_format)
            return

        # Get the current block's position in the document
        block = self.currentBlock()
        block_start = block.position()
        
        # Get the full document text up to this block
        document = self.document()
        full_text = document.toPlainText()
        
        # Find the position of current block in full text
        current_block_start = 0
        current_block = document.firstBlock()
        while current_block.isValid() and current_block != block:
            current_block_start += len(current_block.text()) + 1  # +1 for newline
            current_block = current_block.next()
        
        # Compare character by character for this block
        matcher = SequenceMatcher(None, text, self.other_text[current_block_start:current_block_start + len(text)] if current_block_start < len(self.other_text) else "")
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'delete':
                # Show deletions in red
                fmt = self.deletion_format
                if self.is_left:
                    fmt.setFontStrikeOut(True)
                self.setFormat(i1, i2 - i1, fmt)
            elif tag == 'insert':
                # Show insertions in green
                fmt = self.insertion_format
                if not self.is_left:
                    fmt.setFontUnderline(True)
                self.setFormat(i1, i2 - i1, fmt)
            elif tag == 'replace':
                # Show modifications in orange
                self.setFormat(i1, i2 - i1, self.modification_format)
            elif tag == 'equal':
                # Show matching text normally
                self.setFormat(i1, i2 - i1, self.equal_format)




class DragDropTextEdit(QTextEdit):
    """Custom QTextEdit widget with enhanced drag and drop support.
    
    This widget handles both file drops (loading file content) and text drops
    (inserting text directly). It provides visual feedback through status updates.
    
    Attributes:
        text_area_id (int): Identifier for the text area (1 or 2)
        parent_app (ModernTextCompareApp): Reference to parent application
    """
    
    def __init__(self, parent=None, text_area_id=0):
        """Initialize the DragDropTextEdit widget.
        
        Args:
            parent (QWidget): Parent widget, should be ModernTextCompareApp
            text_area_id (int): Identifier for this text area (1 or 2)
        """
        super().__init__(parent)
        self.text_area_id = text_area_id
        self.parent_app = parent
        self.setAcceptDrops(True)
        
        # Line number area

        

        
    def dragEnterEvent(self, event):
        """Handle drag enter events for drag and drop functionality.
        
        Accepts the proposed action if the dragged data contains URLs or text.
        
        Args:
            event (QDragEnterEvent): The drag enter event
        """
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()
            
    def dropEvent(self, event):
        """Handle drop events for drag and drop functionality.
        
        Processes dropped files by loading their content, or dropped text
        by inserting it directly into the text edit.
        
        Args:
            event (QDropEvent): The drop event
        """
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                if os.path.isfile(file_path):
                    self.parent_app.load_file_content(file_path, self.text_area_id)
                    self.parent_app.add_to_recent_files(file_path)
        elif event.mimeData().hasText():
            self.insertPlainText(event.mimeData().text())
            self.parent_app.status_label.setText(f"Text dropped into Text {self.text_area_id}")
        event.acceptProposedAction()


class ModernTextCompareApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize settings for recent files
        self.settings = QSettings("TextCompare", "ModernTextCompareApp")
        self.recent_files = self.load_recent_files()
        self.max_recent_files = 5
        
        # Create standard icons for actions
        self.file_open_icon = self.style().standardIcon(QStyle.SP_FileDialogStart)
        self.file_save_icon = self.style().standardIcon(QStyle.SP_DialogSaveButton)
        self.recent_files_icon = self.style().standardIcon(QStyle.SP_FileDialogDetailedView)
        
        self.init_ui()
        self.setup_connections()
        
    def load_recent_files(self):
        """Load recent files from settings"""
        if self.settings.contains("recentFiles"):
            value = self.settings.value("recentFiles")
            # Check if value is already a list (happens in some Qt versions)
            if isinstance(value, list):
                return value
            # Otherwise, try to parse it as JSON
            try:
                return json.loads(value)
            except (TypeError, json.JSONDecodeError):
                return []
        return []
        
    def init_ui(self):
        self.setWindowTitle("Modern Text Comparison Tool - PyQt5")
        self.setGeometry(100, 100, 1200, 800)
        self.setAcceptDrops(True)  # Enable drag and drop for the main window
        
        # Create toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(self.toolbar)
        
        # File operations actions with keyboard shortcuts and icons
        self.action_open_file1 = QAction(self.file_open_icon, "Open File 1 (Ctrl+1)", self)
        self.action_open_file1.setShortcut("Ctrl+1")
        self.action_open_file1.setStatusTip("Open a file into Text 1")
        self.action_open_file1.triggered.connect(lambda: self.open_file(1))
        
        self.action_open_file2 = QAction(self.file_open_icon, "Open File 2 (Ctrl+2)", self)
        self.action_open_file2.setShortcut("Ctrl+2")
        self.action_open_file2.setStatusTip("Open a file into Text 2")
        self.action_open_file2.triggered.connect(lambda: self.open_file(2))
        
        self.action_save_results = QAction(self.file_save_icon, "Save Results (Ctrl+S)", self)
        self.action_save_results.setShortcut("Ctrl+S")
        self.action_save_results.setStatusTip("Save comparison results to a file")
        self.action_save_results.triggered.connect(self.save_results)
        
        # Recent files menu
        self.recent_files_menu = QMenu("Recent Files", self)
        self.update_recent_files_menu()
        
        # Add actions to toolbar
        self.toolbar.addAction(self.action_open_file1)
        self.toolbar.addAction(self.action_open_file2)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.action_save_results)
        self.toolbar.addSeparator()
        
        # Add recent files menu to toolbar with icon
        self.recent_files_action = QAction(self.recent_files_icon, "Recent Files", self)
        self.recent_files_action.setStatusTip("Access recently opened files")
        self.recent_files_action.setMenu(self.recent_files_menu)
        self.toolbar.addAction(self.recent_files_action)
        
        # Add separator and line numbers toggle
        self.toolbar.addSeparator()
        

        
        # Add separator and undo/redo actions
        self.toolbar.addSeparator()
        
        # Undo action
        self.action_undo = QAction(self.style().standardIcon(QStyle.SP_ArrowLeft), "Undo (Ctrl+Z)", self)
        self.action_undo.setShortcut("Ctrl+Z")
        self.action_undo.setStatusTip("Undo the last action")
        self.action_undo.triggered.connect(self.undo_action)
        self.action_undo.setEnabled(False)  # Initially disabled
        
        # Redo action
        self.action_redo = QAction(self.style().standardIcon(QStyle.SP_ArrowRight), "Redo (Ctrl+Y)", self)
        self.action_redo.setShortcut("Ctrl+Y")
        self.action_redo.setStatusTip("Redo the last undone action")
        self.action_redo.triggered.connect(self.redo_action)
        self.action_redo.setEnabled(False)  # Initially disabled
        
        # Add undo/redo actions to toolbar
        self.toolbar.addAction(self.action_undo)
        self.toolbar.addAction(self.action_redo)
        
        # Set dark theme
        self.setStyleSheet("""            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #404040;
                border-radius: 5px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                padding: 10px;
            }
            QTextEdit:focus {
                border-color: #0078d4;
            }
            QFrame {
                background-color: #2b2b2b;
            }
            /* Context menu hover effects */
            QMenu {
                background-color: #2D2D30;
                color: #E0E0E0;
                border: 1px solid #3F3F46;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 20px 5px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background-color: #3F3F46;
                margin: 5px 0px 5px 0px;
            }
        """)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Modern Text Comparison Tool")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        main_layout.addWidget(title_label)
        
        # Input section
        input_layout = QHBoxLayout()
        
        # Text 1 input
        text1_layout = QVBoxLayout()
        text1_header = QHBoxLayout()
        text1_label = QLabel("Text 1:")
        text1_label.setStyleSheet("font-weight: bold; color: #E0E0E0;")
        

        
        text1_clear_btn = QPushButton("Clear")
        text1_clear_btn.setStyleSheet("background-color: #3F3F46; color: #E0E0E0; padding: 3px 8px;")
        text1_clear_btn.clicked.connect(lambda: self.text1_edit.clear())
        
        text1_header.addWidget(text1_label)
        text1_header.addStretch()
        text1_header.addWidget(text1_clear_btn)
        
        # Statistics for Text 1
        self.text1_stats = QLabel("Lines: 0 | Words: 0 | Characters: 0")
        self.text1_stats.setStyleSheet("color: #B0B0B0; font-size: 11px; padding: 2px;")
        
        # Create text edit with drag and drop support
        self.text1_edit = DragDropTextEdit(self, 1)
        self.text1_edit.setPlaceholderText("Enter or drop first text here...")
        self.text1_edit.setAcceptRichText(False)  # Accept only plain text
        self.text1_edit.setStyleSheet("background-color: #2D2D30; color: #E0E0E0; border: 1px solid #3F3F46;")
        self.text1_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        
        text1_layout.addLayout(text1_header)
        text1_layout.addWidget(self.text1_stats)
        text1_layout.addWidget(self.text1_edit)
        
        # Text 2 input
        text2_layout = QVBoxLayout()
        text2_header = QHBoxLayout()
        text2_label = QLabel("Text 2:")
        text2_label.setStyleSheet("font-weight: bold; color: #E0E0E0;")
        

        
        text2_clear_btn = QPushButton("Clear")
        text2_clear_btn.setStyleSheet("background-color: #3F3F46; color: #E0E0E0; padding: 3px 8px;")
        text2_clear_btn.setCursor(Qt.PointingHandCursor)
        text2_clear_btn.clicked.connect(lambda: self.text2_edit.clear())
        
        text2_header.addWidget(text2_label)
        text2_header.addStretch()
        text2_header.addWidget(text2_clear_btn)
        
        # Statistics for Text 2
        self.text2_stats = QLabel("Lines: 0 | Words: 0 | Characters: 0")
        self.text2_stats.setStyleSheet("color: #B0B0B0; font-size: 11px; padding: 2px;")
        
        # Create text edit with drag and drop support
        self.text2_edit = DragDropTextEdit(self, 2)
        self.text2_edit.setPlaceholderText("Enter or drop second text here...")
        self.text2_edit.setAcceptRichText(False)  # Accept only plain text
        self.text2_edit.setStyleSheet("background-color: #2D2D30; color: #E0E0E0; border: 1px solid #3F3F46;")
        self.text2_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        
        text2_layout.addLayout(text2_header)
        text2_layout.addWidget(self.text2_stats)
        text2_layout.addWidget(self.text2_edit)
        
        input_layout.addLayout(text1_layout)
        input_layout.addLayout(text2_layout)
        main_layout.addLayout(input_layout)
        
        # Comparison Statistics section
        stats_layout = QVBoxLayout()
        stats_header = QLabel("Comparison Statistics:")
        stats_header.setStyleSheet("font-weight: bold; color: #E0E0E0; margin-top: 10px;")
        
        # Difference statistics
        self.diff_stats = QLabel("Similarity: 100% | Lines Diff: 0 | Words Diff: 0 | Characters Diff: 0")
        self.diff_stats.setStyleSheet("color: #4CAF50; font-size: 12px; padding: 5px; background-color: #2D2D30; border: 1px solid #3F3F46; border-radius: 3px;")
        
        stats_layout.addWidget(stats_header)
        stats_layout.addWidget(self.diff_stats)
        main_layout.addLayout(stats_layout)
        
        # Results section
        results_layout = QVBoxLayout()
        results_header = QHBoxLayout()
        results_label = QLabel("Comparison Results:")
        results_label.setStyleSheet("font-weight: bold; color: #E0E0E0;")
        results_clear_btn = QPushButton("Clear")
        results_clear_btn.setStyleSheet("background-color: #3F3F46; color: #E0E0E0;")
        results_clear_btn.clicked.connect(lambda: self.results_edit.clear())
        results_header.addWidget(results_label)
        results_header.addStretch()
        results_header.addWidget(results_clear_btn)
        
        self.results_edit = QTextEdit()
        self.results_edit.setReadOnly(True)
        self.results_edit.setMaximumHeight(250)
        self.results_edit.setPlaceholderText("Comparison results will appear here...")
        self.results_edit.setStyleSheet("background-color: #2D2D30; color: #E0E0E0; border: 1px solid #3F3F46;")
        results_layout.addLayout(results_header)
        results_layout.addWidget(self.results_edit)
        main_layout.addLayout(results_layout)
        
        # Status bar
        self.status_label = QLabel("Ready to compare texts")
        self.status_label.setStyleSheet("background-color: #404040; padding: 10px; border-radius: 5px;")
        main_layout.addWidget(self.status_label)
        
        # Setup syntax highlighters
        self.highlighter1 = DiffHighlighter(self.text1_edit.document(), "", True)
        self.highlighter2 = DiffHighlighter(self.text2_edit.document(), "", False)
        
        # Timer for delayed comparison (to avoid constant updates while typing)
        self.comparison_timer = QTimer()
        self.comparison_timer.setSingleShot(True)
        self.comparison_timer.timeout.connect(self.compare_texts)
        
    def setup_connections(self):
        """Setup signal connections"""
        self.text1_edit.textChanged.connect(self.on_text_changed)
        self.text2_edit.textChanged.connect(self.on_text_changed)
        
        # Connect text statistics updates
        self.text1_edit.textChanged.connect(lambda: self.update_text_statistics(1))
        self.text2_edit.textChanged.connect(lambda: self.update_text_statistics(2))
        
        # Connect undo/redo availability signals
        self.text1_edit.undoAvailable.connect(self.update_undo_redo_actions)
        self.text1_edit.redoAvailable.connect(self.update_undo_redo_actions)
        self.text2_edit.undoAvailable.connect(self.update_undo_redo_actions)
        self.text2_edit.redoAvailable.connect(self.update_undo_redo_actions)
    
    def update_recent_files_menu(self):
        """Update the recent files menu"""
        self.recent_files_menu.clear()
        
        for file_path in self.recent_files:
            action = QAction(os.path.basename(file_path), self)
            action.setStatusTip(file_path)
            action.triggered.connect(lambda checked, path=file_path: self.open_recent_file(path))
            self.recent_files_menu.addAction(action)
            
        if self.recent_files:
            self.recent_files_menu.addSeparator()
            clear_action = QAction("Clear Recent Files", self)
            clear_action.triggered.connect(self.clear_recent_files)
            self.recent_files_menu.addAction(clear_action)
    
    def add_to_recent_files(self, file_path):
        """Add a file to recent files list"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
            
        self.recent_files.insert(0, file_path)
        
        if len(self.recent_files) > self.max_recent_files:
            self.recent_files = self.recent_files[:self.max_recent_files]
            
        self.settings.setValue("recentFiles", json.dumps(self.recent_files))
        self.update_recent_files_menu()
    
    def clear_recent_files(self):
        """Clear the recent files list"""
        self.recent_files = []
        self.settings.setValue("recentFiles", json.dumps(self.recent_files))
        self.update_recent_files_menu()
    
    def get_focused_text_edit(self):
        """Get the currently focused text edit widget"""
        if self.text1_edit.hasFocus():
            return self.text1_edit
        elif self.text2_edit.hasFocus():
            return self.text2_edit
        return None
    
    def undo_action(self):
        """Perform undo on the focused text edit"""
        focused_edit = self.get_focused_text_edit()
        if focused_edit and focused_edit.document().isUndoAvailable():
            focused_edit.undo()
            self.status_label.setText("Undo performed")
        else:
            # If no text edit is focused, try both starting with text1
            if self.text1_edit.document().isUndoAvailable():
                self.text1_edit.undo()
                self.status_label.setText("Undo performed on Text 1")
            elif self.text2_edit.document().isUndoAvailable():
                self.text2_edit.undo()
                self.status_label.setText("Undo performed on Text 2")
    
    def redo_action(self):
        """Perform redo on the focused text edit"""
        focused_edit = self.get_focused_text_edit()
        if focused_edit and focused_edit.document().isRedoAvailable():
            focused_edit.redo()
            self.status_label.setText("Redo performed")
        else:
            # If no text edit is focused, try both starting with text1
            if self.text1_edit.document().isRedoAvailable():
                self.text1_edit.redo()
                self.status_label.setText("Redo performed on Text 1")
            elif self.text2_edit.document().isRedoAvailable():
                self.text2_edit.redo()
                self.status_label.setText("Redo performed on Text 2")
    
    def update_undo_redo_actions(self):
        """Update the enabled state of undo/redo actions based on availability"""
        # Enable undo if either text edit has undo available
        undo_available = (self.text1_edit.document().isUndoAvailable() or 
                         self.text2_edit.document().isUndoAvailable())
        self.action_undo.setEnabled(undo_available)
        
        # Enable redo if either text edit has redo available
        redo_available = (self.text1_edit.document().isRedoAvailable() or 
                         self.text2_edit.document().isRedoAvailable())
        self.action_redo.setEnabled(redo_available)
    

    
    def update_text_statistics(self, text_area_id):
        """Update text statistics for the specified text area"""
        if text_area_id == 1:
            text_edit = self.text1_edit
            stats_label = self.text1_stats
        else:
            text_edit = self.text2_edit
            stats_label = self.text2_stats
        
        text = text_edit.toPlainText()
        
        # Calculate statistics
        lines = len(text.splitlines()) if text.strip() else 0
        words = len(text.split()) if text.strip() else 0
        characters = len(text)
        
        # Update the statistics label
        stats_label.setText(f"Lines: {lines} | Words: {words} | Characters: {characters}")
        
        # Update comparison statistics
        self.update_comparison_statistics()
    
    def update_comparison_statistics(self):
        """Update the comparison statistics between both texts"""
        text1 = self.text1_edit.toPlainText()
        text2 = self.text2_edit.toPlainText()
        
        if not text1 and not text2:
            self.diff_stats.setText("Similarity: 100% | Lines Diff: 0 | Words Diff: 0 | Characters Diff: 0")
            self.diff_stats.setStyleSheet("color: #4CAF50; font-size: 12px; padding: 5px; background-color: #2D2D30; border: 1px solid #3F3F46; border-radius: 3px;")
            return
        
        # Calculate basic statistics
        lines1 = len(text1.splitlines()) if text1.strip() else 0
        lines2 = len(text2.splitlines()) if text2.strip() else 0
        words1 = len(text1.split()) if text1.strip() else 0
        words2 = len(text2.split()) if text2.strip() else 0
        chars1 = len(text1)
        chars2 = len(text2)
        
        # Calculate differences
        lines_diff = abs(lines1 - lines2)
        words_diff = abs(words1 - words2)
        chars_diff = abs(chars1 - chars2)
        
        # Calculate similarity using SequenceMatcher
        from difflib import SequenceMatcher
        similarity = SequenceMatcher(None, text1, text2).ratio() * 100
        
        # Update the display
        similarity_text = f"Similarity: {similarity:.1f}%"
        diff_text = f"Lines Diff: {lines_diff} | Words Diff: {words_diff} | Characters Diff: {chars_diff}"
        full_text = f"{similarity_text} | {diff_text}"
        
        self.diff_stats.setText(full_text)
        
        # Change color based on similarity
        if similarity >= 90:
            color = "#4CAF50"  # Green
        elif similarity >= 70:
            color = "#FF9800"  # Orange
        else:
            color = "#F44336"  # Red
        
        self.diff_stats.setStyleSheet(f"color: {color}; font-size: 12px; padding: 5px; background-color: #2D2D30; border: 1px solid #3F3F46; border-radius: 3px;")
    

    
    def open_recent_file(self, file_path):
        """Open a file from the recent files list"""
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "File Not Found", f"The file {file_path} no longer exists.")
            self.recent_files.remove(file_path)
            self.settings.setValue("recentFiles", json.dumps(self.recent_files))
            self.update_recent_files_menu()
            return
            
        # Ask which text area to load the file into
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Select Text Area")
        msg_box.setText(f"Load {os.path.basename(file_path)} into:")
        text1_button = msg_box.addButton("Text 1", QMessageBox.ActionRole)
        text2_button = msg_box.addButton("Text 2", QMessageBox.ActionRole)
        cancel_button = msg_box.addButton(QMessageBox.Cancel)
        
        msg_box.exec_()
        
        if msg_box.clickedButton() == text1_button:
            self.load_file_content(file_path, 1)
        elif msg_box.clickedButton() == text2_button:
            self.load_file_content(file_path, 2)
    
    def open_file(self, text_area):
        """Open a file dialog and load content into specified text area"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Open File for Text {text_area}",
            "",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            self.load_file_content(file_path, text_area)
            self.add_to_recent_files(file_path)
    
    def load_file_content(self, file_path, text_area):
        """Load file content into specified text area"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                if text_area == 1:
                    self.text1_edit.setPlainText(content)
                    self.status_label.setText(f"Loaded {os.path.basename(file_path)} into Text 1")
                else:
                    self.text2_edit.setPlainText(content)
                    self.status_label.setText(f"Loaded {os.path.basename(file_path)} into Text 2")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")
    
    def save_results(self):
        """Save comparison results to a file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Comparison Results",
            "",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.results_edit.toPlainText())
                self.status_label.setText(f"Results saved to {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save results: {str(e)}")
    
    # Drag and drop functionality is now handled by the DragDropTextEdit class
    
    def on_text_changed(self):
        """Handle text changes with delayed comparison"""
        self.comparison_timer.stop()
        self.comparison_timer.start(300)  # 300ms delay
        
    def compare_texts(self):
        """Compare the two texts and update highlighting"""
        text1 = self.text1_edit.toPlainText()
        text2 = self.text2_edit.toPlainText()
        
        if not text1 and not text2:
            self.results_edit.clear()
            self.status_label.setText("Ready to compare texts")
            return
            
        if not text1:
            self.results_edit.setText("Text 1 is empty")
            self.status_label.setText("Text 1 is empty")
            return
            
        if not text2:
            self.results_edit.setText("Text 2 is empty")
            self.status_label.setText("Text 2 is empty")
            return
        
        # Update highlighters
        self.highlighter1.set_other_text(text2)
        self.highlighter2.set_other_text(text1)
        
        # Calculate similarity
        matcher = SequenceMatcher(None, text1, text2)
        similarity = matcher.ratio() * 100
        
        # Generate detailed comparison
        self.generate_detailed_comparison(text1, text2, similarity)
        
    def generate_detailed_comparison(self, text1, text2, similarity):
        """Generate detailed character-by-character comparison with enhanced formatting"""
        matcher = SequenceMatcher(None, text1, text2)
        opcodes = list(matcher.get_opcodes())
        
        # Calculate statistics
        total_chars1 = len(text1)
        total_chars2 = len(text2)
        matching_chars = sum(i2 - i1 for tag, i1, i2, j1, j2 in opcodes if tag == 'equal')
        diff_count = len([op for op in opcodes if op[0] != 'equal'])
        
        # Store current scroll position
        scrollbar = self.results_edit.verticalScrollBar()
        current_scroll = scrollbar.value()
        
        # Build enhanced results
        results = []
        results.append(f"📊 COMPARISON RESULTS (Similarity: {similarity:.1f}%)")
        results.append(f"Text 1: {total_chars1} chars | Text 2: {total_chars2} chars | Matching: {matching_chars} chars")
        if diff_count > 0:
            results.append(f"🔍 Found {diff_count} differences")
        results.append("=" * 80)
        results.append("")
        results.append("📋 CHARACTER-BY-CHARACTER VIEW:")
        results.append("💡 Tip: Look for '✗' symbols and descriptions to identify differences")
        results.append("")
        results.append("Pos | Text 1 | Text 2 | Match | Description")
        results.append("-" * 70)
        
        # Show character-by-character comparison (limited to first 100 chars for performance)
        max_len = min(max(len(text1), len(text2)), 100)
        mismatch_count = 0
        
        for i in range(max_len):
            char1 = text1[i] if i < len(text1) else '(end)'
            char2 = text2[i] if i < len(text2) else '(end)'
            
            # Handle special characters for display
            display_char1 = self.get_display_char(char1)
            display_char2 = self.get_display_char(char2)
            
            is_match = char1 == char2
            match_status = "✓" if is_match else "✗"
            
            # Add description for mismatches
            if not is_match:
                mismatch_count += 1
                if char1 == '(end)':
                    description = f"INSERTION at pos {i}"
                elif char2 == '(end)':
                    description = f"DELETION at pos {i}"
                else:
                    description = f"CHANGE at pos {i}"
            else:
                description = "MATCH"
            
            line = f"{i:3d} | {display_char1:5s} | {display_char2:5s} | {match_status:5s} | {description}"
            results.append(line)
            
        if max_len < max(len(text1), len(text2)):
            results.append("...")
            results.append(f"(Showing first {max_len} characters for performance)")
        
        # Add summary
        if mismatch_count > 0:
            results.append("")
            results.append(f"🔍 SUMMARY: {mismatch_count} mismatches found.")
        
        self.results_edit.setText("\n".join(results))
        
        # Restore scroll position to prevent jumping to top
        scrollbar.setValue(current_scroll)
        
        # Update status with enhanced information
        if similarity == 100:
            self.status_label.setText("✅ Texts are identical!")
        else:
            self.status_label.setText(f"⚠️ Found {diff_count} differences - {similarity:.1f}% similarity")
    
    def get_display_char(self, char):
        """Get display representation of character"""
        if char == '(end)':
            return char
        elif char == ' ':
            return '(sp)'
        elif char == '\n':
            return '(nl)'
        elif char == '\t':
            return '(tab)'
        elif char == '\r':
            return '(cr)'
        elif ord(char) < 32:
            return f'(#{ord(char)})'
        else:
            return char
    


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = ModernTextCompareApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()