import sys
import base64
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QTextEdit, QLineEdit, QLabel
)
from PyQt5.QtGui import QFont, QPixmap, QBrush, QPalette
from PyQt5.QtCore import Qt, QByteArray
import main
import file
import background


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
        """将硬编码的 Base64 图片解码、缩放到窗口大小并设为背景"""
        # 请将以下字符串替换为你的 background.png 的 Base64 编码
        BACKGROUND_BASE64 = background.bg()
        b64_data = BACKGROUND_BASE64.strip().replace('\n', '').replace(' ', '')

        try:
            img_data = QByteArray.fromBase64(b64_data.encode())
            pixmap = QPixmap()
            if pixmap.loadFromData(img_data):
                # 缩放到窗口大小
                scaled_pix = pixmap.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                palette = self.palette()
                palette.setBrush(self.backgroundRole(), QBrush(scaled_pix))
                self.setPalette(palette)
                self.setAutoFillBackground(True)
            else:
                self.setStyleSheet("QMainWindow { background-color: black; }")
        except Exception as e:
            print(f"背景加载失败: {e}")
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