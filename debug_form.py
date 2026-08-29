import time
from selenium import webdriver
from selenium.webdriver.common.by import By

form_url = "https://docs.google.com/forms/d/e/1FAIpQLSeqVr5L6-SmgOAAX5ddk-qAT2z8NzHKzSLtXMavN6wNizMAJA/viewform?usp=dialog"

driver = webdriver.Chrome()
driver.get(form_url)
time.sleep(3)  # let it fully render before inspecting

print("\n=== INPUTS ===")
inputs = driver.find_elements(By.TAG_NAME, "input")
print(f"Found {len(inputs)} <input> elements")
for i, inp in enumerate(inputs):
    print(f"[{i}] type={inp.get_attribute('type')!r} "
          f"aria-label={inp.get_attribute('aria-label')!r} "
          f"aria-labelledby={inp.get_attribute('aria-labelledby')!r}")

print("\n=== LISTITEMS (question containers) ===")
items = driver.find_elements(By.XPATH, '//div[@role="listitem"]')
print(f"Found {len(items)} listitem elements")
for i, item in enumerate(items):
    print(f"[{i}] text={item.text[:80]!r}")

print("\n=== BUTTON-ROLE ELEMENTS ===")
buttons = driver.find_elements(By.XPATH, '//div[@role="button"]')
print(f"Found {len(buttons)} button-role elements")
for i, b in enumerate(buttons):
    print(f"[{i}] text={b.text[:40]!r} aria-label={b.get_attribute('aria-label')!r}")

print("\n=== PAGE TITLE / URL (sanity check it's the real form, not a login wall) ===")
print("title:", driver.title)
print("url:", driver.current_url)

input("\nPress Enter to close the browser...")
driver.quit()
