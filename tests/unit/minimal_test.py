#!/usr/bin/env python3
"""
Minimal test for terminal output
"""
import time

# Test plain text output
print("Plain text output test")
print("-" * 40)

# Test emoji
print("Emoji test:")
print("✅ Success")
print("⚠️ Warning")
print("❌ Error")
print("🤖 Robot")

# Test box drawing characters
print("\nBox drawing test:")
print("╭" + "─" * 20 + "╮")
print("│" + " " * 20 + "│")
print("╰" + "─" * 20 + "╯")

print("\nTest completed")

