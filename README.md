# OpenClaw Clone

OpenClaw Clone is an intelligent, locally-hosted Windows desktop assistant powered by **Langchain**, **Ollama**, and **PyQt6**. It leverages the `qwen2.5:7b` local LLM to understand natural language commands and autonomously perform real-world system tasks on your computer.

## ✨ Features

- **Local Processing**: Completely offline and private AI processing using Ollama.
- **System Automation**: Includes custom agent tools to manage files, create folders, open applications, search the web, and get system information.
- **Modern GUI (`desktop_app.py`)**: A sleek, frameless, and interactive chat interface built with PyQt6, featuring smooth animations and a responsive design.
- **Command Line Interface (`chatbot.py`)**: A lightweight, terminal-based alternative with dynamic loading animations.

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed on your Windows PC:

1. **Python 3.8+**
2. **[Ollama](https://ollama.com/)**: Must be installed and running on your system.

## 🚀 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/openclaw_clone.git
   cd openclaw_clone
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Ensure `PyQt6` is installed if you plan to use the desktop application. You can install it using `pip install PyQt6`)*

4. Pull the required language model via Ollama:
   ```bash
   ollama run qwen2.5:7b
   ```
   *(You can exit the ollama prompt once it finishes downloading)*

## 🎮 Usage

### Desktop Application (GUI)
To launch the modern desktop assistant interface, run:
```bash
python desktop_app.py
```
This will open the floating chat window where you can directly interact with OpenClaw.

### Command Line Interface (CLI)
If you prefer a terminal environment, you can run the CLI version:
```bash
python chatbot.py
```

## 🤖 Example Commands

Try asking OpenClaw to perform tasks like:
- *"Create a new folder called 'MyProjects' on the desktop."*
- *"Open Notepad."*
- *"What is the current time?"*
- *"Search my documents for 'invoice'."*

## 📁 Project Structure

- `desktop_app.py`: The main graphical user interface built with PyQt6.
- `chatbot.py`: The terminal-based chat interface.
- `agent_tools.py`: Contains the custom Langchain tool definitions used by the agent to interact with the Windows OS.
- `requirements.txt`: Python package dependencies.
