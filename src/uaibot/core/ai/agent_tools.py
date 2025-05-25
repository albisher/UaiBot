from typing import Any, Dict
from uaibot.core.file_operations import FileOperations, FileOperation
import psutil
import datetime
import math
from uaibot.core.awareness.system_awareness import SystemAwarenessManager
from uaibot.core.input.mouse import MouseController
from uaibot.core.browser_handler import BrowserHandler
import requests
from uaibot.core.config_manager import ConfigManager
from playwright.sync_api import sync_playwright
import os
import shutil
import ast
import re
import matplotlib.pyplot as plt
from uaibot.core.ai.agents.information_collector import InformationCollectorAgent

class Tool:
    name: str
    def execute(self, action: str, params: dict) -> any:
        raise NotImplementedError

class FileTool(Tool):
    """
    Agent tool for file operations (create, read, write, append, delete, search, list, rename, copy, info).
    Wraps the FileOperations class and exposes it as a tool for agents.
    """
    name = "file"

    def __init__(self):
        self.ops = FileOperations()

    def execute(self, action: str, params: Dict[str, Any]) -> Any:
        """
        Execute a file operation. Action is the operation name (e.g., 'create', 'read', ...).
        Params should include filename, content, directory, pattern, etc. as needed.
        """
        op = FileOperation(
            operation=action,
            filename=params.get("filename"),
            content=params.get("content"),
            directory=params.get("directory"),
            pattern=params.get("pattern"),
        )
        return self.ops.execute(op)

class SystemResourceTool(Tool):
    name = "system"
    def execute(self, action: str, params: dict) -> any:
        if action == "info":
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            return (
                f"CPU: {cpu}%\n"
                f"Memory: {mem.percent}% used ({mem.used // (1024**2)}MB/{mem.total // (1024**2)}MB)\n"
                f"Disk: {disk.percent}% used ({disk.used // (1024**3)}GB/{disk.total // (1024**3)}GB)"
            )
        return "Unknown system resource action"

class DateTimeTool(Tool):
    name = "datetime"
    def execute(self, action: str, params: dict) -> any:
        if action == "now":
            now = datetime.datetime.now()
            return now.strftime("%Y-%m-%d %H:%M:%S")
        return "Unknown datetime action"

class WeatherTool(Tool):
    name = "weather"
    def execute(self, action: str, params: dict) -> any:
        if action == "current":
            location = params.get("location", "Kuwait")
            config = ConfigManager()
            api_key = config.get("openweathermap_api_key", "")
            if not api_key:
                return "Weather API key not set. Please add your OpenWeatherMap API key to config."
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
                resp = requests.get(url, timeout=5)
                if resp.ok:
                    data = resp.json()
                    desc = data['weather'][0]['description'].capitalize()
                    temp = data['main']['temp']
                    city = data['name']
                    country = data['sys']['country']
                    return f"Weather in {city}, {country}: {temp}°C, {desc}"
                else:
                    return f"Weather API error: {resp.status_code} {resp.text}"
            except Exception as e:
                return f"Weather API error: {e}"
        return "Unknown weather action"

class CalculatorTool(Tool):
    name = "calculator"
    def execute(self, action: str, params: dict) -> any:
        if action == "eval":
            expr = params.get("expression", "")
            try:
                # Safe eval: only allow math functions and numbers
                allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
                allowed_names["abs"] = abs
                result = eval(expr, {"__builtins__": {}}, allowed_names)
                return f"Result: {result}"
            except Exception as e:
                return f"Error: {e}"
        return "Unknown calculator action"

class SystemAwarenessTool(Tool):
    name = "system_awareness"
    def __init__(self):
        self.manager = SystemAwarenessManager()
    def execute(self, action: str, params: dict) -> any:
        if action == "info":
            return self.manager.get_mouse_info()
        if action == "screen":
            return self.manager.get_screen_size()
        if action == "windows":
            return self.manager.get_open_windows()
        return "Unknown system awareness action"

class MouseControlTool(Tool):
    name = "mouse"
    def __init__(self):
        self.controller = MouseController()
    def execute(self, action: str, params: dict) -> any:
        if action == "move":
            x, y = params.get("x"), params.get("y")
            return self.controller.move_to(x, y)
        if action == "click":
            button = params.get("button", "left")
            return self.controller.click(button=button)
        return "Unknown mouse action"

class KeyboardInputTool(Tool):
    name = "keyboard"
    def execute(self, action: str, params: dict) -> any:
        try:
            from uaibot.platform_uai.platform_utils import get_input_handler
            handler = get_input_handler()
            if action == "type":
                text = params.get("text", "")
                return handler.type_text(text)
            if action == "press":
                key = params.get("key", "enter")
                return handler.press_key(key)
            return "Unknown keyboard action"
        except Exception as e:
            return f"Keyboard error: {e}"

class BrowserAutomationTool(Tool):
    name = "browser"
    def __init__(self):
        self.handler = BrowserHandler()
    def execute(self, action: str, params: dict) -> any:
        if action == "open":
            url = params.get("url", "https://www.google.com")
            return self.handler.open_browser(url)
        if action == "type":
            text = params.get("text", "")
            return self.handler.type_in_browser(text)
        if action == "click":
            x, y = params.get("x"), params.get("y")
            return self.handler.click_in_browser(x, y)
        return "Unknown browser action"

class WebSurfingTool(Tool):
    name = "web_surfing"
    def execute(self, action: str, params: dict) -> any:
        """Automates browsing, clicking, typing, and navigation using Playwright."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                if action == "open_url":
                    url = params.get("url", "https://www.google.com")
                    page.goto(url)
                    title = page.title()
                    browser.close()
                    return f"Opened URL: {url} (title: {title})"
                elif action == "click":
                    selector = params.get("selector")
                    if not selector:
                        browser.close()
                        return "No selector provided for click."
                    page.goto(params.get("url", "https://www.google.com"))
                    page.click(selector)
                    browser.close()
                    return f"Clicked {selector} on {params.get('url', '')}"
                elif action == "type":
                    selector = params.get("selector")
                    text = params.get("text", "")
                    if not selector or not text:
                        browser.close()
                        return "Selector and text required for typing."
                    page.goto(params.get("url", "https://www.google.com"))
                    page.fill(selector, text)
                    browser.close()
                    return f"Typed '{text}' in {selector} on {params.get('url', '')}"
                elif action == "screenshot":
                    url = params.get("url", "https://www.google.com")
                    page.goto(url)
                    path = params.get("path", "screenshot.png")
                    page.screenshot(path=path)
                    browser.close()
                    return f"Screenshot saved to {path}"
                else:
                    browser.close()
                    return f"Unknown web surfing action: {action}"
        except Exception as e:
            return f"WebSurfingTool error: {e}"

class WebSearchingTool(Tool):
    name = "web_searching"
    def execute(self, action: str, params: dict) -> any:
        """Performs web searches and returns results using DuckDuckGo."""
        if action == "search":
            query = params.get("query", "")
            if not query:
                return "No search query provided."
            try:
                url = f"https://api.duckduckgo.com/?q={query}&format=json&no_redirect=1&no_html=1"
                resp = requests.get(url, timeout=5)
                if resp.ok:
                    data = resp.json()
                    results = []
                    # Related topics (DuckDuckGo's way of returning results)
                    for topic in data.get("RelatedTopics", []):
                        if "Text" in topic and "FirstURL" in topic:
                            results.append({
                                "title": topic["Text"],
                                "url": topic["FirstURL"]
                            })
                    # Abstract as snippet
                    snippet = data.get("AbstractText", "")
                    answer = {
                        "results": results[:5],
                        "snippet": snippet
                    }
                    return answer
                else:
                    return f"DuckDuckGo API error: {resp.status_code} {resp.text}"
            except Exception as e:
                return f"Web search error: {e}"
        return "Unknown web search action"

class FileAndDocumentOrganizerTool(Tool):
    name = "file_document_organizer"
    def execute(self, action: str, params: dict) -> any:
        """Organizes files and documents by rules/tags using real file operations."""
        try:
            if action == "move":
                src = params.get("src")
                dst = params.get("dst")
                if not src or not dst:
                    return "Source and destination required."
                shutil.move(src, dst)
                return f"Moved {src} to {dst}"
            elif action == "rename":
                src = params.get("src")
                dst = params.get("dst")
                if not src or not dst:
                    return "Source and destination required."
                os.rename(src, dst)
                return f"Renamed {src} to {dst}"
            elif action == "list":
                directory = params.get("directory", ".")
                files = os.listdir(directory)
                return files
            elif action == "organize_by_type":
                directory = params.get("directory", ".")
                for fname in os.listdir(directory):
                    fpath = os.path.join(directory, fname)
                    if os.path.isfile(fpath):
                        ext = os.path.splitext(fname)[1][1:] or "no_ext"
                        target_dir = os.path.join(directory, ext)
                        os.makedirs(target_dir, exist_ok=True)
                        shutil.move(fpath, os.path.join(target_dir, fname))
                return f"Organized files in {directory} by type."
            elif action == "organize_by_date":
                directory = params.get("directory", ".")
                for fname in os.listdir(directory):
                    fpath = os.path.join(directory, fname)
                    if os.path.isfile(fpath):
                        mtime = os.path.getmtime(fpath)
                        date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
                        target_dir = os.path.join(directory, date_str)
                        os.makedirs(target_dir, exist_ok=True)
                        shutil.move(fpath, os.path.join(target_dir, fname))
                return f"Organized files in {directory} by date."
            else:
                return f"Unknown file/document organizer action: {action}"
        except Exception as e:
            return f"FileAndDocumentOrganizerTool error: {e}"

class CodePathUpdaterTool(Tool):
    name = "code_path_updater"
    def execute(self, action: str, params: dict) -> any:
        """Updates code import paths and references in Python files using AST and regex."""
        try:
            if action == "update_imports":
                old_path = params.get("old_path")
                new_path = params.get("new_path")
                directory = params.get("directory", ".")
                if not old_path or not new_path:
                    return "old_path and new_path required."
                updated_files = []
                for root, _, files in os.walk(directory):
                    for fname in files:
                        if fname.endswith(".py"):
                            fpath = os.path.join(root, fname)
                            with open(fpath, "r", encoding="utf-8") as f:
                                code = f.read()
                            # Use regex to replace import paths
                            new_code = re.sub(rf'(from|import)\s+{re.escape(old_path)}', lambda m: m.group(0).replace(old_path, new_path), code)
                            if new_code != code:
                                with open(fpath, "w", encoding="utf-8") as f:
                                    f.write(new_code)
                                updated_files.append(fpath)
                return f"Updated imports in {len(updated_files)} files: {updated_files}"
            else:
                return f"Unknown code path updater action: {action}"
        except Exception as e:
            return f"CodePathUpdaterTool error: {e}"

class GraphMakerTool(Tool):
    name = "graph_maker"
    def __init__(self, work_dir="work/graph_maker"):
        self.work_dir = work_dir
        os.makedirs(self.work_dir, exist_ok=True)
        self.collector = InformationCollectorAgent()

    def execute(self, action: str, params: dict) -> any:
        """Generates graphs from collected data in a folder."""
        try:
            if action == "analyze_folder":
                folder = params.get("folder", ".")
                # Collect file info
                files = self.collector.file_tool.execute("list", {"directory": folder})
                # File type distribution
                ext_counts = {}
                for fname in files:
                    ext = os.path.splitext(fname)[1][1:] or "no_ext"
                    ext_counts[ext] = ext_counts.get(ext, 0) + 1
                # Plot
                fig, ax = plt.subplots()
                ax.bar(ext_counts.keys(), ext_counts.values())
                ax.set_title("File Type Distribution")
                ax.set_xlabel("Extension")
                ax.set_ylabel("Count")
                graph_path = os.path.join(self.work_dir, "file_type_distribution.png")
                plt.savefig(graph_path)
                plt.close(fig)
                return {"graph": graph_path, "summary": ext_counts}
            else:
                return f"Unknown graph maker action: {action}"
        except Exception as e:
            return f"GraphMakerTool error: {e}" 