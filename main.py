import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# dtype=str on Phone Number stops pandas from reading it as an int and
# silently dropping the leading 0 (e.g. 03001234567 -> 3001234567).
df = pd.read_csv(
    "selenium_google_form_sample_data.csv",
    dtype={"Phone Number": str},
)

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 15)

form_url = "https://docs.google.com/forms/d/e/1FAIpQLSeqVr5L6-SmgOAAX5ddk-qAT2z8NzHKzSLtXMavN6wNizMAJA/viewform?usp=dialog"


def get_input_by_question(driver, wait, question_text):
    """
    Find a text input by walking up to the question's container (the
    div[role="listitem"] that holds the question title) and grabbing the
    input inside it. This is more reliable than input[@aria-label=...]
    because Google Forms often does NOT set aria-label to the plain
    question text -- it frequently uses aria-labelledby pointing at a
    hidden span instead, which is why the original selectors were
    timing out silently.

    The match is case-insensitive (via XPath 1.0's translate() trick,
    since this engine has no lower-case() function) because Google
    renders question titles with its own capitalization -- e.g. "Phone
    Number", not "Phone number" -- and a case-sensitive contains() will
    time out on a mismatch exactly like this one did.
    """
    q = question_text.lower()
    xpath = (
        '//div[@role="listitem"]'
        '[.//*[contains(translate(text(), '
        '"ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), '
        f'"{q}")]]//input'
    )
    return wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))


results = []

for index, row in df.head(3).iterrows():
    name = str(row["Name"])
    number = str(row["Phone Number"])
    email = str(row["Email Address"])

    try:
        driver.get(form_url)

        name_box = get_input_by_question(driver, wait, "Name")
        phone_box = get_input_by_question(driver, wait, "Phone number")
        email_box = get_input_by_question(driver, wait, "Email address")

        name_box.clear()
        name_box.send_keys(name)
        phone_box.clear()
        phone_box.send_keys(number)
        email_box.clear()
        email_box.send_keys(email)

        # Fail loudly here rather than submitting blank/wrong fields.
        assert name_box.get_attribute("value") == name
        assert phone_box.get_attribute("value") == number
        assert email_box.get_attribute("value") == email

        # The clickable target is the div[role="button"] wrapper, not
        # the inner <span> that just holds the label text.
        submit_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//div[@role="button"][.//span[text()="Submit"]]')
            )
        )
        submit_button.click()

        wait.until(
            EC.text_to_be_present_in_element(
                (By.TAG_NAME, "body"), "Your response has been recorded"
            )
        )

        print(f"Submitted: {name}")
        results.append((name, "success", None))

    except TimeoutException as e:
        print(f"Failed (timeout): {name} -- a field or the confirmation "
              f"text was never found. Run the debug snippet at the "
              f"bottom of this file to see the form's real structure.")
        results.append((name, "failed", "timeout"))

    except AssertionError:
        print(f"Failed (value mismatch): {name} -- a field didn't hold "
              f"the value we typed into it.")
        results.append((name, "failed", "value_mismatch"))

    except Exception as e:
        print(f"Failed: {name} -- {e}")
        results.append((name, "failed", str(e)))

    time.sleep(1)  # small buffer between submissions

driver.quit()

pd.DataFrame(results, columns=["Name", "Status", "Error"]).to_csv(
    "submission_log.csv", index=False
)

# ---------------------------------------------------------------------------
# DEBUG: if every row still times out, uncomment this block, run it on its
# own, and read the console output. It prints every input's real
# aria-label/aria-labelledby and every listitem's visible question text, so
# you can see exactly what Google is rendering for THIS form and adjust the
# question_text strings above to match.
# ---------------------------------------------------------------------------
# debug_driver = webdriver.Chrome()
# debug_driver.get(form_url)
# time.sleep(2)
# for inp in debug_driver.find_elements(By.TAG_NAME, "input"):
#     print("input:", repr(inp.get_attribute("aria-label")),
#           repr(inp.get_attribute("aria-labelledby")))
# for item in debug_driver.find_elements(By.XPATH, '//div[@role="listitem"]'):
#     print("listitem text:", repr(item.text[:60]))
# debug_driver.quit()
