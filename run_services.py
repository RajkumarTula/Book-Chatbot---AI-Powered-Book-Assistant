#!/usr/bin/env python3
"""
Service runner for the Book Chatbot application.
This script starts all required services in the correct order.
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

class ServiceManager:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def start_service(self, name, command, cwd=None, wait_for_ready=None):
        """Start a service and return the process."""
        print(f"Starting {name}...")
        
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes.append((name, process))
            
            if wait_for_ready:
                print(f"Waiting for {name} to be ready...")
                self.wait_for_ready(process, wait_for_ready)
            
            print(f"✅ {name} started (PID: {process.pid})")
            return process
            
        except Exception as e:
            print(f"❌ Failed to start {name}: {e}")
            return None
    
    def wait_for_ready(self, process, check_function, timeout=30):
        """Wait for a service to be ready."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if check_function():
                return True
            time.sleep(1)
        
        print(f"⚠️  Service may not be ready after {timeout} seconds")
        return False
    
    def check_redis_ready(self):
        """Check if Redis is ready."""
        try:
            result = subprocess.run(
                ["redis-cli", "ping"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            return result.returncode == 0 and "PONG" in result.stdout
        except:
            return False
    
    def check_api_ready(self):
        """Check if API is ready."""
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def stop_all_services(self):
        """Stop all running services."""
        print("\nStopping all services...")
        self.running = False
        
        for name, process in self.processes:
            try:
                print(f"Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                print(f"⚠️  {name} didn't stop gracefully, forcing...")
                process.kill()
            except Exception as e:
                print(f"❌ Error stopping {name}: {e}")
    
    def monitor_services(self):
        """Monitor services and restart if needed."""
        while self.running:
            time.sleep(10)
            
            for i, (name, process) in enumerate(self.processes):
                if process.poll() is not None:
                    print(f"⚠️  {name} stopped unexpectedly, restarting...")
                    
                    # Restart the service
                    if name == "Redis":
                        new_process = self.start_service(name, "redis-server")
                    elif name == "Rasa Actions":
                        new_process = self.start_service(
                            name, 
                            "rasa run actions", 
                            cwd="Booky"
                        )
                    elif name == "Rasa Server":
                        new_process = self.start_service(
                            name, 
                            "rasa run --enable-api --cors '*'", 
                            cwd="Booky"
                        )
                    elif name == "FastAPI Server":
                        new_process = self.start_service(
                            name, 
                            "python api_server.py"
                        )
                    elif name == "React Frontend":
                        new_process = self.start_service(
                            name, 
                            "npm start", 
                            cwd="react-frontend"
                        )
                    
                    if new_process:
                        self.processes[i] = (name, new_process)
                        print(f"✅ {name} restarted")
                    else:
                        print(f"❌ Failed to restart {name}")

def main():
    """Main function to start all services."""
    print("🚀 Book Chatbot Service Manager")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("api_server.py"):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Create service manager
    manager = ServiceManager()
    
    # Set up signal handlers
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}, shutting down...")
        manager.stop_all_services()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start Redis
        redis_process = manager.start_service(
            "Redis", 
            "redis-server",
            wait_for_ready=manager.check_redis_ready
        )
        
        if not redis_process:
            print("❌ Failed to start Redis. Please install and start Redis manually.")
            sys.exit(1)
        
        # Start Rasa Action Server
        manager.start_service(
            "Rasa Actions", 
            "rasa run actions", 
            cwd="Booky"
        )
        
        # Wait a bit for Rasa Actions to start
        time.sleep(5)
        
        # Start Rasa Server
        manager.start_service(
            "Rasa Server", 
            "rasa run --enable-api --cors '*'", 
            cwd="Booky"
        )
        
        # Wait a bit for Rasa Server to start
        time.sleep(5)
        
        # Start FastAPI Server
        api_process = manager.start_service(
            "FastAPI Server", 
            "python api_server.py",
            wait_for_ready=manager.check_api_ready
        )
        
        if not api_process:
            print("❌ Failed to start FastAPI Server")
            sys.exit(1)
        
        # Start React Frontend (optional)
        if os.path.exists("react-frontend"):
            manager.start_service(
                "React Frontend", 
                "npm start", 
                cwd="react-frontend"
            )
        
        print("\n" + "=" * 50)
        print("✅ All services started successfully!")
        print("\nAccess the application:")
        print("  - Vanilla frontend: http://localhost:8000")
        print("  - React frontend: http://localhost:3000")
        print("  - API documentation: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop all services")
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=manager.monitor_services)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Keep the main thread alive
        while manager.running:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt, shutting down...")
        manager.stop_all_services()
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        manager.stop_all_services()
        sys.exit(1)

if __name__ == "__main__":
    main()



