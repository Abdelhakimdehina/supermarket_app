import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

class AppRestartHandler(FileSystemEventHandler):
    def __init__(self, app_process):
        self.app_process = app_process
        self.restart_pending = False
    
    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            print(f"\nPython file modified: {event.src_path}")
            self.schedule_restart()
    
    def schedule_restart(self):
        if not self.restart_pending:
            self.restart_pending = True
            print("Changes detected. Restarting app in 1 second...")
            time.sleep(1)  # Wait for all changes to be saved
            self.restart_app()
            self.restart_pending = False
    
    def restart_app(self):
        print("Stopping current instance...")
        self.app_process.terminate()
        self.app_process.wait()
        
        print("Starting new instance...")
        self.app_process = start_app()

def start_app():
    """Start the application process"""
    # Get the path to main.py relative to this script
    main_script = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'main.py')
    return subprocess.Popen([sys.executable, main_script])

def run_with_watchdog():
    """Run the application with file watching"""
    print("Starting application with auto-restart...")
    
    # Start the application
    app_process = start_app()
    
    # Set up the watchdog
    event_handler = AppRestartHandler(app_process)
    observer = Observer()
    
    # Get the workspace root directory
    workspace_dir = os.path.dirname(os.path.dirname(__file__))
    
    # Start watching
    observer.schedule(event_handler, workspace_dir, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping application...")
        observer.stop()
        app_process.terminate()
    
    observer.join()
    print("Application stopped.")

if __name__ == "__main__":
    run_with_watchdog() 