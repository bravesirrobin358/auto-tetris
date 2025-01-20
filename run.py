import os
import multiprocessing
import subprocess

current_directory = os.getcwd()  # Get the current directory

def frontend_thread():
    frontend_dir = os.path.join(current_directory, "frontend")
    os.chdir(frontend_dir)
    subprocess.run(["streamlit", "run", "main.py"])

if __name__ == "__main__":
    # Start the frontend as a separate process
    frontend_process = multiprocessing.Process(target=frontend_thread, daemon=True)
    frontend_process.start()

    # Run the backend (Flask)
    backend_dir = os.path.join(current_directory, "backend")
    os.chdir(backend_dir)
    subprocess.run(["flask", "run"])
