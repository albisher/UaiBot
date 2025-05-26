To control Safari sequentially from the Terminal—including opening tabs, searching, and interacting with page elements—combine shell scripting with AppleScript/JavaScript injections. Here’s how to achieve this:

---

### 1. **Open a New Tab with a URL**
Use a custom Zsh/Bash function or the `open` command with AppleScript to ensure new tabs open reliably:
```zsh
function new_safari_tab() {
  osascript -e "tell application \"Safari\"
    activate
    tell front window
      set current tab to (make new tab with properties {URL:\"$1\"})
    end tell
  end tell"
}
```
Call it with:
```zsh
new_safari_tab "https://www.google.com"  # Opens Google in a new tab [1][7]
```

---

### 2. **Search for a Query**
Convert the search term into a URL-encoded string and open it:
```zsh
search_term="your query here"
encoded_term=$(printf "%s" "$search_term" | jq -sRr @uri)  # Requires `jq`
new_safari_tab "https://www.google.com/search?q=$encoded_term" [2]
```

---

### 3. **Click Elements on the Page**
Use AppleScript to inject JavaScript into the active tab. For example, to click a button with ID `#searchButton`:
```zsh
osascript <<EOF
tell application "Safari"
  activate
  tell front document
    do JavaScript "document.getElementById('searchButton').click();"
  end tell
end tell
EOF
```
- **Target elements by**:  
  - **ID**: `document.getElementById('id')` [4]  
  - **Class**: `document.getElementsByClassName('class')`  
  - **Tag**: `document.getElementsByTagName('button')` [5][6]  

---

### 4. **Track Tabs**
AppleScript can reference specific windows/tabs. To ensure actions target the correct tab:
```applescript
tell application "Safari"
  set myWindow to front window
  set myTab to current tab of myWindow
  -- Perform actions on myTab
end tell
```

---

### Full Example Script
```bash
#!/bin/zsh

# Function to open a new tab
new_safari_tab() {
  osascript -e "tell application \"Safari\"
    activate
    tell front window
      set current tab to (make new tab with properties {URL:\"$1\"})
    end tell
  end tell"
}

# Open Google in a new tab
new_safari_tab "https://www.google.com"

# Search for "example query"
search_term="example query"
encoded_term=$(printf "%s" "$search_term" | jq -sRr @uri)
new_safari_tab "https://www.google.com/search?q=$encoded_term"

# Click the first search result (adjust selector as needed)
sleep 2  # Wait for page to load
osascript <<EOF
tell application "Safari"
  activate
  tell front document
    do JavaScript "document.querySelector('h3').click();"
  end tell
end tell
EOF
```

---

### Key Considerations:
- **Timing**: Add `sleep` commands to allow pages to load before interacting [5][6].  
- **Error Handling**: Use JavaScript checks (e.g., `if (elementExists) { ... }`) to avoid failures [4].  
- **Browser Path**: Modify scripts for Chrome/Firefox by updating the application path [2].  

For complex workflows, consider wrapping logic in an [Automator workflow](https://discussions.apple.com/thread/250959248) [3] or a dedicated shell script [2][7].

Citations:
[1] https://discussions.apple.com/thread/253127889
[2] https://github.com/antoniolanza1996/openSafariFromTerminal
[3] https://discussions.apple.com/thread/250959248
[4] https://www.cubemg.com/how-to-click-a-button-on-a-web-page-with-applescript/
[5] https://www.macscripter.net/t/clicking-search-button-in-safari/75461
[6] https://www.macscripter.net/t/click-on-a-button-of-a-web-site-with-javascript/76386
[7] https://apple.stackexchange.com/questions/427188/terminal-command-to-force-open-new-tab-in-safari
[8] https://github.com/kssfilo/safari-ctl
[9] https://stackoverflow.com/questions/5721528/terminal-command-to-open-safari
[10] https://superuser.com/questions/1856865/how-can-i-open-a-new-safari-window-with-bash
[11] https://discussions.apple.com/thread/253026968
[12] https://support.apple.com/guide/terminal/execute-commands-and-run-tools-apdb66b5242-0d18-49fc-9c47-a2498b7c91d5/mac
[13] https://apple.stackexchange.com/questions/374585/how-can-i-automate-repeat-mouse-clicks-with-delay-from-fixed-coordinates-withi
[14] https://discussions.apple.com/thread/255581931
[15] https://discussions.apple.com/thread/4326977
[16] https://stackoverflow.com/questions/5270134/how-do-you-achieve-a-click-on-the-screen-in-safari-using-applescript
[17] https://apple.stackexchange.com/questions/119324/using-javascript-applescript-to-click-button-in-safari
[18] https://stackoverflow.com/questions/41629592/macos-sierra-how-to-enable-allow-remote-automation-using-command-line
[19] https://blog.bytesguy.com/enabling-remote-automation-in-safari-14
[20] https://www.lambdatest.com/blog/selenium-safaridriver-macos/
[21] https://apple.stackexchange.com/questions/305895/how-to-open-google-chrome-or-safari-from-terminal
[22] https://superuser.com/questions/331129/script-to-search-for-highlighted-text
[23] https://discussions.apple.com/thread/254913756
[24] https://superuser.com/questions/67442/open-multiple-safari-tabs-from-the-command-line-on-mac-os-x
[25] https://www.reddit.com/r/shortcuts/comments/1cip2ug/open_url_in_safari_click_a_button_using_15_pro_max/
[26] https://apple.stackexchange.com/questions/374099/where-does-safari-store-the-open-tabs
[27] https://support.apple.com/en-kw/guide/safari/ibrwbb6e21e4/mac
[28] https://www.reddit.com/r/MacOS/comments/zhyiyu/how_can_i_use_command_tab_to_choose_any_open_tab/
[29] https://apple.stackexchange.com/questions/206427/can-you-see-a-list-of-all-open-tabs-in-safari
[30] https://github.com/zhuhanming/safari-tabs-saver
[31] https://www.idownloadblog.com/2015/08/24/10-safari-keyboard-shortcuts-that-everyone-should-know/
[32] https://www.youtube.com/watch?v=RR-bDwtTaNs
[33] https://www.theverge.com/23803135/safari-tab-groups-how-to
[34] https://www.macscripter.net/t/use-applescript-in-a-safari-search/71125

---
Answer from Perplexity: pplx.ai/share




====================
====================

To automate browser actions (open browser, search, click, track tabs) across Firefox, Chrome, Safari, and others in a generic, command-line-controlled way, the most robust and cross-browser solution is to use a browser automation framework like Selenium, Playwright, or Cypress. These tools provide a unified API for controlling multiple browsers, supporting scripting from the terminal, and tracking browser state.

## Generic Cross-Browser Automation Approaches

**Selenium WebDriver**

- Supports Chrome, Firefox, Safari, Edge, and more.
- Lets you write scripts (Python, JavaScript, etc.) to:
  - Open browsers and tabs
  - Navigate to URLs
  - Interact with page elements (click, type, etc.)
  - Keep track of windows/tabs via handles[1][6].

**Example (Python):**
```python
from selenium import webdriver
from selenium.webdriver.common.by import By

# Choose your browser driver
driver = webdriver.Chrome()  # Or webdriver.Firefox(), webdriver.Safari(), etc.

# Open a URL
driver.get("https://www.google.com")

# Search for something
search_box = driver.find_element(By.NAME, "q")
search_box.send_keys("example search")
search_box.submit()

# Click on the first result
first_result = driver.find_element(By.CSS_SELECTOR, "h3")
first_result.click()

# Track tabs/windows
print(driver.window_handles)
```
- Run this script from the terminal:  
  `python your_script.py`  
- Change the driver to switch browsers[1][6].

---

**Playwright**

- Supports Chromium (Chrome/Edge), Firefox, and WebKit (Safari engine).
- Unified API for all supported browsers.
- Can be scripted in JavaScript, Python, etc.[7].

**Example (Node.js):**
```javascript
const { chromium, firefox, webkit } = require('playwright');

(async () => {
  const browser = await chromium.launch(); // or firefox.launch(), webkit.launch()
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto('https://www.google.com');
  await page.fill('input[name="q"]', 'example search');
  await page.press('input[name="q"]', 'Enter');
  await page.click('h3'); // Click first result
  console.log(await context.pages()); // Track open tabs
  await browser.close();
})();
```
- Run with:  
  `node your_script.js`  
- Swap `chromium`, `firefox`, or `webkit` for different browsers[7].

---

**Cypress**

- Supports Chrome, Firefox, Edge, and Electron.
- Tests are written in JavaScript.
- Specify browser at runtime via CLI[4].

**Example CLI:**
```bash
npx cypress run --browser chrome
npx cypress run --browser firefox
```
- Use Cypress commands in your test files to automate search, click, etc.[4].

---

## Summary Table

| Framework   | Browsers Supported                | Language(s)      | Tab/Window Tracking | CLI Control |
|-------------|-----------------------------------|------------------|--------------------|-------------|
| Selenium    | Chrome, Firefox, Safari, Edge, IE | Python, JS, etc. | Yes                | Yes         |
| Playwright  | Chrome, Firefox, Safari (WebKit)  | JS, Python, etc. | Yes                | Yes         |
| Cypress     | Chrome, Firefox, Edge, Electron   | JavaScript       | Limited            | Yes         |

---

## Key Points

- **No built-in, generic CLI-only solution** exists for all browsers; scripting with automation frameworks is the standard and most reliable approach[1][4][6][7].
- **Selenium and Playwright** are the most flexible for tracking tabs and supporting all major browsers.
- **All actions** (open, search, click, track tabs) can be scripted and run from the terminal.
- **Browser drivers** (e.g., chromedriver, geckodriver) must be installed and accessible.

For most use cases, Selenium or Playwright will provide the cross-browser, command-line-controlled automation you need.

Citations:
[1] https://www.browserstack.com/guide/cross-browser-testing-in-selenium
[2] https://www.qafox.com/new-selenium-ide-cross-browser-testing-using-command-line-runner/
[3] https://hackmd.io/@sideex/webdriver
[4] https://www.lambdatest.com/learning-hub/cross-browser-testing-with-cypress
[5] https://blog.pixelfreestudio.com/best-practices-for-cross-browser-testing-automation/
[6] https://saucelabs.com/resources/blog/cross-browser-testing-with-selenium
[7] https://codoid.com/automation-testing/playwright-cross-browser-testing-tutorial/
[8] https://philipwalton.com/articles/learning-how-to-set-up-automated-cross-browser-javascript-unit-testing/

---
Answer from Perplexity: pplx.ai/share