import sys
import threading
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, 
    QLineEdit, QPushButton, QHBoxLayout, QLabel,
    QScrollArea, QGraphicsOpacityEffect, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QFont, QIcon, QCursor, QColor

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from agent_tools import all_tools

class AgentWorker(QObject):
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, agent):
        super().__init__()
        self.agent = agent
        self.messages = []

    def handle_request(self, user_text):
        try:
            self.messages.append(HumanMessage(content=user_text))
            response_state = self.agent.invoke({"messages": self.messages})
            self.messages = response_state["messages"]
            result_text = self.messages[-1].content
            self.response_ready.emit(result_text)
        except Exception as e:
            self.error_occurred.emit(str(e))

class MessageWidget(QWidget):
    def __init__(self, text, is_bot=False):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        sender_lbl = QLabel("🤖 OpenClaw" if is_bot else "You")
        sender_lbl.setStyleSheet("color: #9CA3AF; font-size: 11px; font-weight: bold;")
        
        msg_lbl = QLabel(text)
        msg_lbl.setWordWrap(True)
        msg_lbl.setFont(QFont("Segoe UI", 11))
        msg_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        if is_bot:
            sender_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
            msg_lbl.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    color: #374151;
                    padding: 5px 0px 15px 0px;
                }
            """)
            layout.addWidget(sender_lbl)
            layout.addWidget(msg_lbl)
        else:
            sender_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            msg_lbl.setStyleSheet("""
                QLabel {
                    background-color: #B282EA;
                    color: white;
                    border-radius: 18px;
                    border-bottom-right-radius: 4px;
                    padding: 12px 18px;
                }
            """)
            layout.addWidget(sender_lbl)
            layout.addWidget(msg_lbl, alignment=Qt.AlignmentFlag.AlignRight)
            
        # Add smooth fade-in animation
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.anim.start()

class HeaderBar(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.setFixedHeight(80)
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #9333EA, stop:1 #C084FC);
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                border-bottom: none;
            }
            QLabel {
                background: transparent;
                color: white;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # Titles
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        title_layout.setSpacing(2)
        
        main_title = QLabel("OpenClaw")
        main_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        
        sub_title = QLabel("🟢 Online Now")
        sub_title.setFont(QFont("Segoe UI", 10))
        sub_title.setStyleSheet("color: #E9D5FF;")
        
        title_layout.addWidget(main_title)
        title_layout.addWidget(sub_title)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                color: #F3E8FF;
            }
        """)
        close_btn.clicked.connect(self.parent_window.close)
        layout.addWidget(close_btn)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.parent_window.dragPos = event.globalPosition().toPoint()
            
    def mouseMoveEvent(self, event):
        if hasattr(self.parent_window, 'dragPos') and self.parent_window.dragPos is not None:
            delta = event.globalPosition().toPoint() - self.parent_window.dragPos
            self.parent_window.move(self.parent_window.pos() + delta)
            self.parent_window.dragPos = event.globalPosition().toPoint()
            
    def mouseReleaseEvent(self, event):
        self.parent_window.dragPos = None

class TypingIndicator(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.lbl = QLabel("OpenClaw is thinking...")
        self.lbl.setStyleSheet("color: #9CA3AF; font-style: italic;")
        self.lbl.setFont(QFont("Segoe UI", 10))
        layout.addWidget(self.lbl)
        
        self.opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)
        self.anim = QPropertyAnimation(self.opacity, b"opacity")
        self.anim.setDuration(600)
        self.anim.setStartValue(0.4)
        self.anim.setEndValue(1.0)
        self.anim.setLoopCount(-1) # Loop forever
        self.anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.hide()
        
    def start(self):
        self.show()
        self.anim.start()
        
    def stop(self):
        self.anim.stop()
        self.hide()

class OpenClawApp(QMainWindow):
    def __init__(self, agent):
        super().__init__()
        
        self.agent = agent
        self.dragPos = None
        
        self.init_ui()
        
        self.worker = AgentWorker(self.agent)
        self.worker.response_ready.connect(self.on_response_received)
        self.worker.error_occurred.connect(self.on_error_received)
        
    def init_ui(self):
        # Apply frameless window styling and transparent background
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Define dimensions
        screen = QApplication.primaryScreen().geometry()
        app_width = 400
        app_height = int(screen.height() * 0.85)
        
        x_pos = screen.width() - app_width - 30
        y_pos = int((screen.height() - app_height) / 2)
        
        self.setGeometry(x_pos, y_pos, app_width, app_height)
        
        # Main background widget holding everything together securely
        bg_widget = QFrame()
        bg_widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
            }
        """)
        self.setCentralWidget(bg_widget)
        
        main_layout = QVBoxLayout(bg_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. Custom Purple Header
        self.header = HeaderBar(self)
        main_layout.addWidget(self.header)
        
        # 2. Scroll Area for dynamic message chatting
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
            QScrollBar:vertical {
                border: none;
                background: #F3F4F6;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #D1D5DB;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9CA3AF;
            }
        """)
        
        self.chat_container = QWidget()
        self.chat_container.setStyleSheet("background-color: white;")
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setContentsMargins(15, 15, 15, 15)
        self.chat_layout.setSpacing(10)
        self.scroll_area.setWidget(self.chat_container)
        
        main_layout.addWidget(self.scroll_area)
        
        # 3. Animated typing indicator
        self.typing_indicator = TypingIndicator()
        main_layout.addWidget(self.typing_indicator)
        
        # 4. Input Area aligned with your image concept
        input_container = QFrame()
        input_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-top: 1px solid #E5E7EB;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }
        """)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(15, 15, 15, 15)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Reply to OpenClaw...")
        self.input_field.setFont(QFont("Segoe UI", 11))
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #F3F4F6;
                border: none;
                border-radius: 20px;
                padding: 10px 15px;
                color: #374151;
            }
            QLineEdit:focus {
                background-color: #E5E7EB;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        
        self.send_button = QPushButton("Send")
        self.send_button.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.send_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #9333EA;
                color: white;
                border-radius: 20px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #A855F7;
            }
            QPushButton:disabled {
                background-color: #D8B4FE;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        main_layout.addWidget(input_container)
        
        # Initial boot up visual
        self.append_message("Hello! I am ready to assist you. I can open apps, create folders, search files, and browse the web. How can I help?", is_bot=True)

    def append_message(self, text, is_bot=False):
        msg_widget = MessageWidget(text, is_bot)
        self.chat_layout.addWidget(msg_widget)
        
        # Quick timeout required so the layout processes the new widget geometry before scrolling
        QTimer.singleShot(50, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def send_message(self):
        user_text = self.input_field.text().strip()
        if not user_text:
            return
            
        self.append_message(user_text, is_bot=False)
        self.input_field.clear()
        
        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)
        
        self.typing_indicator.start()
        QTimer.singleShot(50, self.scroll_to_bottom)
        
        threading.Thread(target=self.worker.handle_request, args=(user_text,)).start()

    def on_response_received(self, response_text):
        self.typing_indicator.stop()
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.input_field.setFocus()
        self.append_message(response_text, is_bot=True)

    def on_error_received(self, error_msg):
        self.typing_indicator.stop()
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.append_message(f"An error occurred: {error_msg}", is_bot=True)

def main():
    print("Initializing OpenClaw Agent backend...")
    
    # Initialize the LLM
    try:
        model = ChatOllama(model="qwen2.5:7b")
    except Exception as e:
        print(f"Failed to load model: {e}")
        sys.exit(1)

    system_prompt = '''You are OpenClaw, an intelligent desktop assistant running on a Windows PC.
Your job is to help the user perform tasks on their computer using the available tools.

IMPORTANT RULES:
1. If the user asks for ANY real-world action on the computer, you MUST use the appropriate tool.
2. NEVER pretend to perform an action. Always call a tool.
3. If the request is informational, respond normally without using tools.
4. After a tool executes, explain the result clearly and briefly.
5. Be concise, helpful, and behave like a professional desktop assistant.
'''

    agent = create_agent(
        model=model,
        tools=all_tools,
        system_prompt=system_prompt,
        debug=False
    )

    app = QApplication(sys.argv)
    window = OpenClawApp(agent)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
