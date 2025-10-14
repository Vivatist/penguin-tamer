"""
Demo System - Independent recording and playback system.

This module provides isolated functionality for recording and playing back
console sessions without modifying existing code.

Uses Null Object Pattern - no need for if-checks in calling code.
"""

from .manager import DemoSystemManager, NullDemoManager, create_demo_manager

__all__ = ['DemoSystemManager', 'NullDemoManager', 'create_demo_manager']
