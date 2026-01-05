#!/usr/bin/env python3
"""
Launcher script for the Multimodal RAG Use Case Generator.
Starts both the FastAPI backend and Streamlit UI.
"""

import subprocess
import sys
import os
import time
import signal
import threading

def start_api_server():
    """Start the FastAPI server"""
    print("🚀 Starting FastAPI server...")
    try:
        process = subprocess.Popen([
            sys.executable, "main.py"
        ], cwd=os.path.join(os.path.dirname(__file__)))
        return process
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def start_streamlit_ui():
    """Start the Streamlit UI"""
    print("🎨 Starting Streamlit UI...")
    try:
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "ui.py",
            "--server.headless", "true",
            "--server.port", "8501"
        ], cwd=os.path.join(os.path.dirname(__file__)))
        return process
    except Exception as e:
        print(f"❌ Failed to start Streamlit UI: {e}")
        return None

def wait_for_api_ready(max_attempts=30):
    """Wait for API to be ready"""
    import requests
    for i in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/", timeout=2)
            if response.status_code == 200:
                print("✅ API server is ready!")
                return True
        except:
            pass
        print(f"⏳ Waiting for API server... ({i+1}/{max_attempts})")
        time.sleep(2)
    return False

def main():
    print("🤖 Multimodal RAG Use Case Generator Launcher")
    print("=" * 50)

    # Start API server
    api_process = start_api_server()
    if not api_process:
        sys.exit(1)

    # Wait for API to be ready
    if not wait_for_api_ready():
        print("❌ API server failed to start properly")
        api_process.terminate()
        sys.exit(1)

    # Start Streamlit UI
    ui_process = start_streamlit_ui()
    if not ui_process:
        api_process.terminate()
        sys.exit(1)

    print("\n🎉 Both services started successfully!")
    print("📱 Web UI: http://localhost:8501")
    print("🔌 API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop all services")

    def signal_handler(signum, frame):
        print("\n🛑 Shutting down services...")
        ui_process.terminate()
        api_process.terminate()
        print("✅ All services stopped")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Keep running
    try:
        while True:
            time.sleep(1)
            # Check if processes are still running
            if api_process.poll() is not None:
                print("❌ API server stopped unexpectedly")
                ui_process.terminate()
                break
            if ui_process.poll() is not None:
                print("❌ UI stopped unexpectedly")
                api_process.terminate()
                break
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()