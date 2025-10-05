import os
import webbrowser
import threading
import time
import subprocess

def run_streamlit():
    os.system("streamlit run streetmap.py --server.port 8501")

def open_browser():
    time.sleep(3)
    webbrowser.open("http://localhost:8501")

if __name__ == "__main__":
    threading.Thread(target=open_browser).start()
    run_streamlit()
