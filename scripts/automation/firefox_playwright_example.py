from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.firefox.launch()
    page = browser.new_page()
    # Open Google
    page.goto("https://www.google.com")
    # Fill the search box and submit
    page.fill('input[name="q"]', "example search")
    page.press('input[name="q"]', 'Enter')
    page.wait_for_selector('h3')
    # Click the first result
    page.click('h3')
    # Print all open pages
    print(page.context.pages)
    browser.close() 