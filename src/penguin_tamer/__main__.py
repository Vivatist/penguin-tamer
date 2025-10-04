#!/usr/bin/env python3
"""
Entry point for running Penguin Tamer as a module.

This allows running the application with: python -m penguin_tamer
"""
import sys
from penguin_tamer.cli import main

if __name__ == "__main__":
    sys.exit(main())
