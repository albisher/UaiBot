# Cross-Browser Automation: Selenium, Playwright, Cypress

## Overview
Modern browser automation frameworks allow you to control Chrome, Firefox, Safari, Edge, and more from scripts. The most robust solutions are Selenium, Playwright, and Cypress.

## Selenium Example (Python)
```python
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()  # Or Firefox(), Safari(), etc.
driver.get("https://www.google.com")
search_box = driver.find_element(By.NAME, "q")
search_box.send_keys("example search")
search_box.submit()
first_result = driver.find_element(By.CSS_SELECTOR, "h3")
first_result.click()
print(driver.window_handles)
```

## Playwright Example (Node.js)
```javascript
const { chromium, firefox, webkit } = require('playwright');
(async () => {
  const browser = await chromium.launch(); // or firefox.launch(), webkit.launch()
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto('https://www.google.com');
  await page.fill('input[name="q"]', 'example search');
  await page.press('input[name="q"]', 'Enter');
  await page.click('h3');
  console.log(await context.pages());
  await browser.close();
})();
```

## Cypress Example (CLI)
```bash
npx cypress run --browser chrome
npx cypress run --browser firefox
```

## Example Scripts
- [Firefox Selenium Example (Python)](../../scripts/automation/firefox_selenium_example.py)
- [Firefox Playwright Example (Python)](../../scripts/automation/firefox_playwright_example.py)

## Comparison Table
| Framework   | Browsers Supported                | Language(s)      | Tab/Window Tracking | CLI Control |
|-------------|-----------------------------------|------------------|--------------------|-------------|
| Selenium    | Chrome, Firefox, Safari, Edge, IE | Python, JS, etc. | Yes                | Yes         |
| Playwright  | Chrome, Firefox, Safari (WebKit)  | JS, Python, etc. | Yes                | Yes         |
| Cypress     | Chrome, Firefox, Edge, Electron   | JavaScript       | Limited            | Yes         |

## Best Practices
- Use Selenium or Playwright for maximum flexibility and browser support.
- Install the correct browser drivers (chromedriver, geckodriver, etc.).
- Use scripting to automate navigation, search, clicks, and tab management.
- Run scripts from the terminal for automation and testing. 