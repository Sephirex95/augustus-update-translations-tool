# -*- coding: utf-8 -*-
"""
Created on Fri Jul 18 13:47:45 2025

@author: sephirex95
"""

import sys
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QScrollArea, QMessageBox, QLineEdit,QFileDialog,
    QApplication,QSizePolicy, QComboBox
)
from PyQt6.QtCore import Qt, QSettings
import encodings

import os
os.environ["QT_OPENGL"] = "desktop"  # or "angle", but "desktop" skips software fallback


def extract_all_strings(content):
    match = re.search(
        r'static\s+translation_string\s+all_strings\s*\[\s*\]\s*=\s*\{(.*?)\};',
        content,
        re.DOTALL
    )
    if not match:
        return {}

    body = match.group(1)

    # Matches: {TR_KEY, "string" \n "string" \n ...}
    entry_pattern = re.compile(
        r'\{\s*([A-Z0-9_]+)\s*,\s*((?:"(?:[^"\\]|\\.)*"\s*)+)\s*\},?',
        re.DOTALL
    )

    string_literal_pattern = re.compile(r'"((?:[^"\\]|\\.)*)"')

    results = {}

    for m in entry_pattern.finditer(body):
        key = m.group(1)
        raw_value = m.group(2)

        # Extract and concatenate string literals without altering content
        parts = string_literal_pattern.findall(raw_value)
        full_string = ''.join(parts)
        results[key] = full_string

    return results



class CompareStringsWidget(QWidget):
    def __init__(self, missing_keys, original_strings, file2_path):
        super().__init__()
        self.setWindowTitle("Missing Translations")
        self.resize(1300, 600)
        self.file2_path = file2_path
        # Header row
        header_layout = QHBoxLayout()
        layout = QVBoxLayout(self)
        self.input_fields = {}
        key_width = 400
        input_width = 400
        original_width = 400
        
        key_header = QLabel("Key")
        key_header.setMinimumWidth(key_width)
        key_header.setStyleSheet("font-weight: bold")
        header_layout.addWidget(key_header)
        
        input_header = QLabel("Translation")
        input_header.setMinimumWidth(input_width)
        input_header.setStyleSheet("font-weight: bold")
        header_layout.addWidget(input_header)
        
        original_header = QLabel("Original")
        original_header.setMinimumWidth(original_width)
        original_header.setStyleSheet("font-weight: bold")
        header_layout.addWidget(original_header)
        
        layout.addLayout(header_layout)



        scroll = QScrollArea(self)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)



        for key in missing_keys:
            row = QHBoxLayout()

            # Fixed-width key label
            key_label = QLabel(key)
            key_label.setFixedWidth(key_width)
            key_label.setAlignment(Qt.AlignmentFlag.AlignTop)
            row.addWidget(key_label)

            # Multiline input field
            input_field = QTextEdit()
            input_field.setFixedHeight(30)
            
            def make_resizer(text_edit):
                min_height = 30
                max_height = 200
                def auto_resize():
                    doc_height = text_edit.document().size().height() + 10
                    new_height = max(min_height, min(int(doc_height), max_height))
                    text_edit.setFixedHeight(new_height)
                return auto_resize
            
            input_field.textChanged.connect(make_resizer(input_field))
            
            row.addWidget(input_field)
            self.input_fields[key] = input_field


            # Word-wrapped original string
            original_label = QLabel(original_strings[key])
            original_label.setWordWrap(True)
            original_label.setFixedWidth(original_width)
            original_label.setAlignment(Qt.AlignmentFlag.AlignTop)
            row.addWidget(original_label)

            scroll_layout.addLayout(row)
        
        key_label.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        input_field.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        original_label.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)

        key_label.setMinimumWidth(key_width)
        input_field.setMinimumWidth(input_width)
        original_label.setMinimumWidth(original_width)

        scroll_widget.setLayout(scroll_layout)
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_widget)

        layout.addWidget(scroll)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.ok_clicked)
        layout.addWidget(ok_button)

    def ok_clicked(self):
        try:
            with open(self.file2_path, 'r', encoding='utf-8') as f:
                content = f.read()
    
            # Collect non-empty input translations
            new_entries = []
            for key, field in self.input_fields.items():
                value = field.toPlainText().strip()
                if not value:
                    continue
                escaped_value = value.replace('\\', '\\\\').replace('"', '\\"')
                entry = f'    {{{key}, "{escaped_value}"}},'
                new_entries.append(entry)
    
            if not new_entries:
                QMessageBox.information(self, "Nothing to Insert", "No translation entries were filled in.")
                return
    
            # Find the position of the last occurrence of '};'
            insert_pos = content.rfind('};')
            if insert_pos == -1:
                raise ValueError("Could not find end of all_strings array ('};') in file.")
    
            # Walk backwards to find } or ,
            i = insert_pos - 1
            while i >= 0 and content[i].isspace():
                i -= 1
                if i < 0:
                    raise ValueError("Reached start of file before finding any content before '};'.")
    
            last_char = content[i]
            insert_comma = False
            if last_char == '}':
                insert_comma = True
            elif last_char == ',':
                insert_comma = False
            else:
                raise ValueError(f"Unexpected character before '}};': '{last_char}'")
    
            # Prepare insert string
            insertion = ""
            if insert_comma:
                insertion += ","
            insertion += "\n".join(new_entries)
            insertion += "\n"
    
            # Insert it just before '};'
            updated_content = content[:insert_pos] + insertion + content[insert_pos:]
    
            with open(self.file2_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
    
            QMessageBox.information(self, "Success", f"Inserted {len(new_entries)} translations into file.")
            self.close()
    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to insert translations:\n{e}")
    
    


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("C Translation String Comparator")
        self.setGeometry(100, 100, 600, 200)

        self.settings = QSettings("YourCompany", "TranslationComparator")
        
        # Restore previous file paths
        self.file1_path = self.settings.value("file1_path", "", type=str)
        self.file2_path = self.settings.value("file2_path", "", type=str)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
    
        # File 1
        file1_layout = QHBoxLayout()
        self.file1_line = QLineEdit()
        self.file1_line.setReadOnly(True)
        self.file1_line.setText(self.file1_path)
        
        browse1_btn = QPushButton("Browse...")
        browse1_btn.clicked.connect(self.browse_file1)
        
        self.file1_encoding_box = QComboBox()
        self.file1_encoding_box.addItems(sorted(set(encodings.aliases.aliases.values())))
        self.file1_encoding_box.setCurrentText("utf_8")
    
        file1_layout.addWidget(QLabel("Translate from:"))
        file1_layout.addWidget(self.file1_line)
        file1_layout.addWidget(browse1_btn)
        file1_layout.addWidget(QLabel("Encoding:"))
        file1_layout.addWidget(self.file1_encoding_box)
        layout.addLayout(file1_layout)
    
        # File 2
        file2_layout = QHBoxLayout()
        self.file2_line = QLineEdit()
        self.file2_line.setReadOnly(True)
        self.file2_line.setText(self.file2_path)
        browse2_btn = QPushButton("Browse...")
        browse2_btn.clicked.connect(self.browse_file2)
        self.file2_encoding_box = QComboBox()
        self.file2_encoding_box.addItems(sorted(set(encodings.aliases.aliases.values())))
        self.file2_encoding_box.setCurrentText("utf_8")
    
        file2_layout.addWidget(QLabel("Translate to:"))
        file2_layout.addWidget(self.file2_line)
        file2_layout.addWidget(browse2_btn)
        file2_layout.addWidget(QLabel("Encoding:"))
        file2_layout.addWidget(self.file2_encoding_box)
        layout.addLayout(file2_layout)
    
        # Button row
        button_layout = QHBoxLayout()
        compare_btn = QPushButton("Translate with UI")
        compare_btn.clicked.connect(self.compare_files)
        button_layout.addWidget(compare_btn)
    
        export_btn = QPushButton("Generate .txt with Missing Keys")
        export_btn.clicked.connect(self.export_missing_keys)
        button_layout.addWidget(export_btn)
    
        layout.addLayout(button_layout)
    
        self.setLayout(layout)

    def browse_file1(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select first .c file", "", "C Files (*.c)")
        if file:
            self.file1_path = file
            self.file1_line.setText(file)
            self.settings.setValue("file1_path", file)


    def browse_file2(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select second .c file", "", "C Files (*.c)")
        if file:
            self.file2_path = file
            self.file2_line.setText(file)
            self.settings.setValue("file2_path", file)
            
    def compare_files(self):
        if not self.file1_path or not self.file2_path:
            QMessageBox.warning(self, "Error", "Please select both files.")
            return
    
        try:
            encoding1 = self.file1_encoding_box.currentText()
            encoding2 = self.file2_encoding_box.currentText()
    
            with open(self.file1_path, 'r', encoding=encoding1) as f1:
                content1 = f1.read()
            with open(self.file2_path, 'r', encoding=encoding2) as f2:
                content2 = f2.read()
    
            strings1 = extract_all_strings(content1)
            strings2 = extract_all_strings(content2)
    
            missing_keys = [k for k in strings1 if k not in strings2]
    
            if not missing_keys:
                QMessageBox.information(self, "Done", "No missing keys found.")
                return
    
            self.result_window = CompareStringsWidget(missing_keys, strings1, self.file2_path)
            self.result_window.show()
    
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            
    def export_missing_keys(self):
        if not hasattr(self, 'file1_path') or not hasattr(self, 'file2_path'):
            QMessageBox.warning(self, "Error", "Please compare files first.")
            return
    
        try:
            encoding1 = self.file1_encoding_box.currentText()
            encoding2 = self.file2_encoding_box.currentText()
    
            with open(self.file1_path, 'r', encoding=encoding1) as f1:
                content1 = f1.read()
            with open(self.file2_path, 'r', encoding=encoding2) as f2:
                content2 = f2.read()
    
            strings1 = extract_all_strings(content1)  # should return {KEY: VALUE}
            strings2 = extract_all_strings(content2)
    
            missing_keys = [k for k in strings1 if k not in strings2]
    
            if not missing_keys:
                QMessageBox.information(self, "Done", "No missing keys to export.")
                return
    
            export_path, _ = QFileDialog.getSaveFileName(
                self, "Save Missing Keys As", "missing_keys.txt", "Text Files (*.txt)"
            )
            if not export_path:
                return  # User canceled
    
            with open(export_path, 'w', encoding='utf-8') as out_file:
                for key in missing_keys:
                    value = strings1[key].replace('"', r'\"')  # Escape quotes
                    out_file.write(f'{{{key}, "{value}"}},\n')
    
            QMessageBox.information(self, "Exported", f"Missing keys exported to:\n{export_path}")
    
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

