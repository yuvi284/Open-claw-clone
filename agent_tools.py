import os
import datetime
import subprocess
import webbrowser
from langchain_core.tools import tool

# ==========================================
# FILE TOOLS
# ==========================================

def _resolve_path(path: str) -> str:
    """Helper to resolve paths like 'Desktop/folder' or '~/Desktop' to absolute paths."""
    # If the AI just passes "Desktop/myfolder"
    if path.lower().startswith("desktop"):
        path = os.path.join(os.path.expanduser("~"), "Desktop", path[7:].lstrip("\\/"))
    elif path.lower().startswith("documents"):
        path = os.path.join(os.path.expanduser("~"), "Documents", path[9:].lstrip("\\/"))
    elif path.lower().startswith("downloads"):
        path = os.path.join(os.path.expanduser("~"), "Downloads", path[9:].lstrip("\\/"))
    
    return os.path.expanduser(path)

@tool
def create_folder(folder_path: str) -> str:
    """Creates a new folder at the specified path. If the user asks for 'Desktop', prefix the path with 'Desktop/' or '~/Desktop/'."""
    try:
        folder_path = _resolve_path(folder_path)
        os.makedirs(folder_path, exist_ok=True)
        return f"Folder successfully created at {folder_path}"
    except Exception as e:
        return f"Error creating folder: {e}"

@tool
def delete_file(file_path: str) -> str:
    """Deletes a file at the specified path. BE CAREFUL. Input should be the absolute path, or prefixed with 'Desktop/' etc."""
    try:
        file_path = _resolve_path(file_path)
        if os.path.exists(file_path):
            if os.path.isdir(file_path):
                import shutil
                shutil.rmtree(file_path)
                return f"Folder {file_path} successfully deleted."
            else:
                os.remove(file_path)
                return f"File {file_path} successfully deleted."
        else:
            return f"File or folder {file_path} does not exist."
    except Exception as e:
        return f"Error deleting file/folder: {e}"

@tool
def rename_file(old_path: str, new_path: str) -> str:
    """Renames a file or folder from old_path to new_path. Inputs are the original path and the new intended path."""
    try:
        old_path = _resolve_path(old_path)
        new_path = _resolve_path(new_path)
        
        if not os.path.exists(old_path):
             return f"File {old_path} does not exist."
             
        os.rename(old_path, new_path)
        return f"File renamed from {old_path} to {new_path}."
    except Exception as e:
        return f"Error renaming file: {e}"

@tool
def search_files(directory: str, file_name: str) -> str:
    """Searches for files or folders with a specific exact name within a directory. Looks in subdirectories. If you want to check the whole system, use 'C:\\' or 'F:\\' as the directory."""
    results = []
    import time
    start_time = time.time()
    
    try:
        directory = _resolve_path(directory)
        if not os.path.exists(directory):
            return f"Directory '{directory}' does not exist to search in."

        for root, dirs, files in os.walk(directory):
            # Check timeout (stop after 15 seconds to avoid freezing the AI forever)
            if time.time() - start_time > 15:
                return f"Search timed out after 15 seconds. Found so far: {', '.join(results) if results else 'Nothing'}"

            # Check if it's a file
            if file_name in files:
                results.append(os.path.join(root, file_name))
            
            # Check if it's a directory
            if file_name in dirs:
                results.append(os.path.join(root, file_name))
                
            # If we found at least 5 matches, stop early
            if len(results) >= 5:
                break
        
        if results:
            return f"Found at: {', '.join(results)}"
        return f"File/Folder '{file_name}' not found in '{directory}'."
    except Exception as e:
         return f"Error searching files: {e}"

@tool
def list_files(folder_path: str) -> str:
    """Lists files and folders inside a directory. Useful to see what is currently inside a folder."""
    try:
        folder_path = _resolve_path(folder_path)

        if not os.path.exists(folder_path):
            return f"Folder {folder_path} does not exist."

        items = os.listdir(folder_path)

        if not items:
            return "Folder is empty."

        return "Contents:\n" + "\n".join(items)
    except Exception as e:
        return f"Error listing files: {e}"

@tool
def open_folder(folder_path: str) -> str:
    """Opens a folder in Windows File Explorer so the user can see it."""
    try:
        folder_path = _resolve_path(folder_path)

        if not os.path.exists(folder_path):
            return f"Folder {folder_path} does not exist."

        subprocess.Popen(f'explorer "{folder_path}"')
        return f"Opened folder {folder_path}"
    except Exception as e:
        return f"Error opening folder: {e}"

# ==========================================
# SYSTEM TOOLS
# ==========================================
@tool
def get_time() -> str:
    """Returns the current system time."""
    return datetime.datetime.now().strftime("%I:%M:%S %p")

@tool
def get_date() -> str:
    """Returns the current system date."""
    return datetime.date.today().strftime("%Y-%m-%d")

@tool
def shutdown_pc() -> str:
    """Shuts down the PC."""
    try:
        # Note: Added /t 60 so user has time to abort with 'shutdown /a' if tested accidentally.
        os.system("shutdown /s /t 60")
        return "PC will shut down in 60 seconds. (User can abort via terminal: shutdown /a)"
    except Exception as e:
        return f"Error shutting down: {e}"

@tool
def lock_pc() -> str:
    """Locks the PC currently in use."""
    try:
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return "PC locked successfully."
    except Exception as e:
        return f"Error locking PC: {e}"

# ==========================================
# APPS TOOLS
# ==========================================
@tool
def open_chrome() -> str:
    """Opens Google Chrome browser."""
    try:
        webbrowser.open("https://www.google.com")
        return "Chrome opened."
    except Exception as e:
        return f"Error opening Chrome: {e}"

@tool
def open_application(app_name: str) -> str:
    """Opens an installed application by name (e.g., 'notepad', 'calc', 'code', 'spotify')."""
    try:
        subprocess.Popen(app_name, shell=True)
        return f"{app_name} launched successfully."
    except Exception as e:
        return f"Error launching {app_name}: {e}"

@tool
def close_application(process_name: str) -> str:
    """Force closes a running application by its process name (e.g., 'chrome.exe', 'Ld9BoxHeadless.exe'). Usually used when an app is locking a folder."""
    try:
        # Ensures .exe is appended so taskkill can work
        if not process_name.lower().endswith(".exe"):
            process_name += ".exe"
            
        result = subprocess.run(f'taskkill /F /IM "{process_name}" /T', capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            return f"{process_name} has been forcefully closed."
        else:
            return f"Failed to close {process_name}. It might not be running or requires admin privileges. Result: {result.stderr or result.stdout}"
    except Exception as e:
        return f"Error closing application: {e}"

# ==========================================
# BROWSER TOOLS
# ==========================================
@tool
def open_website(url: str, browser_name: str = "") -> str:
    """Opens a specific URL. If browser_name is specified (e.g., 'chrome'), it attempts to open it in that specific browser, otherwise it uses the default system browser."""
    try:
        if not url.startswith("http"):
            url = "https://" + url
            
        # If the user specifically asked for Chrome
        if browser_name.lower() == "chrome":
            subprocess.Popen(f'start chrome "{url}"', shell=True)
            return f"Website {url} opened successfully in Google Chrome."
            
        # Fallback to the system's default browser
        webbrowser.open(url)
        return f"Website {url} opened successfully in default browser."
    except Exception as e:
        return f"Error opening website: {e}"

@tool
def google_search(query: str) -> str:
    """Performs a Google search for the specified query in the default browser."""
    try:
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        return f"Google search for '{query}' opened successfully."
    except Exception as e:
        return f"Error performing search: {e}"

# ==========================================
# Export all tools
# ==========================================
all_tools = [
    create_folder, delete_file, rename_file, search_files,
    list_files, open_folder,
    get_time, get_date, shutdown_pc, lock_pc,
    open_chrome, open_application, close_application,
    open_website, google_search
]
