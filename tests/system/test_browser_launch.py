import webbrowser
import subprocess
import time

url = "https://duckduckgo.com"
print("Trying webbrowser.open...")
webbrowser.open(url)
time.sleep(3)
print("Trying xdg-open...")
subprocess.Popen(["xdg-open", url])
print("Done! Check if browser opened.") 