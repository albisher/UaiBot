from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Start Firefox browser
with webdriver.Firefox() as driver:
    # Open Google
    driver.get("https://www.google.com")
    # Find the search box, enter query, and submit
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys("example search")
    search_box.submit()
    # Wait for results to load
    time.sleep(2)
    # Click the first result
    first_result = driver.find_element(By.CSS_SELECTOR, "h3")
    first_result.click()
    # Print all window handles
    print(driver.window_handles) 