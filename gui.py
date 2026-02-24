import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QTextEdit, QLineEdit, QLabel
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import main
import file


class TerminalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VoidNovelEngine Launcher")
        self.setFixedSize(960, 530)

        self.set_background()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setAttribute(Qt.WA_StyledBackground, True)
        central_widget.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # 输出区域
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Consolas", 10))
        self.output.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                border: none;
            }
        """)
        layout.addWidget(self.output, 1)

        # 输入区域
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)

        prompt = QLabel(">>> ")
        prompt.setFont(QFont("Consolas", 10))
        prompt.setStyleSheet("background: transparent; color: white;")
        input_layout.addWidget(prompt)

        self.entry = QLineEdit()
        self.entry.setFont(QFont("Consolas", 10))
        self.entry.setStyleSheet("""
            QLineEdit {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                border: none;
            }
        """)
        self.entry.returnPressed.connect(self.on_enter)
        input_layout.addWidget(self.entry)

        layout.addLayout(input_layout)

        # 注入输出和清屏函数
        main.gui_print = self.gui_print
        main.clear_screen = self.clear_output

        # 显示初始菜单
        main.menu()

    def set_background(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(script_dir, "background.png")
        if os.path.exists(bg_path):
            self.setStyleSheet(f"""
                QMainWindow {{
                    border-image: url({bg_path.replace('\\', '/')});
                }}
            """)
        else:
            self.setStyleSheet("QMainWindow { background-color: black; }")

    def gui_print(self, text):
        self.output.append(text)
        self.output.moveCursor(self.output.textCursor().End)

    def clear_output(self):
        self.output.clear()

    def on_enter(self):
        user_input = self.entry.text().strip()
        if user_input:
            self.gui_print(f">>>> {user_input}")
            self.entry.clear()
            main.Translate_user_input(user_input)
        else:
            self.entry.clear()


def run_gui():
    app = QApplication(sys.argv)
    window = TerminalApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_gui()