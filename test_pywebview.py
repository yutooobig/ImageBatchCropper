#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    import webview
    print("pywebview imported successfully")
    print(f"pywebview version: {webview.__version__}")
except ImportError as e:
    print(f"Failed to import pywebview: {e}")
    print("Please install pywebview with: pip install pywebview")
except Exception as e:
    print(f"Unexpected error: {e}")
