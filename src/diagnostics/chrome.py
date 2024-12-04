from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import sys
import traceback
import subprocess
import platform
import json
import datetime

class ChromeDiagnostics:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.chrome_options.add_argument("--verbose")
        self.chrome_options.add_argument("--log-level=3")
        self.driver = None

    def run_all_diagnostics(self):
        """Run all diagnostic checks"""
        print("=== Chrome Diagnostics Suite ===")
        print("-" * 50)
        
        # System Information
        print("System Information:")
        print(f"Python: {sys.version.split()[0]}")
        print(f"Selenium: {webdriver.__version__}")
        
        # Connection Diagnostics
        print("\nConnection Diagnostics:")
        port_active = self.verify_chrome_debug_port()
        if not port_active:
            print("ERROR: Debug port check failed")
            return
        
        connection_success = self.test_chrome_connection()
        if not connection_success:
            print("ERROR: Chrome connection failed")
            return
        
        # Page Analysis
        self.analyze_page_structure()
        self.cleanup() 