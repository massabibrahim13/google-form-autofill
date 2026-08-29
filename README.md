# Google Form Auto-Fill

Fills out a Google Form automatically using rows from a CSV file.

## Files

| File | What it's for |
|---|---|
| `main.py` | The main script — fills and submits the form |
| `debug_form.py` | Run this only if `main.py` times out or fails |
| `selenium_google_form_sample_data.csv` | Your data — one row per person |

## Setup (one time)

1. **Install Python packages:**
   ```
   pip install selenium pandas
   ```
2. **Make sure Google Chrome is installed** on your computer. Selenium will find and drive it automatically — no separate driver download needed.

## How to run it

### Step 1 — Prepare your data file
Create a CSV with these exact column headers: `Name`, `Phone Number`, `Email Address`. One row per person you want to submit.

### Step 2 — Point the script at your data file
Open `main.py` and find this line near the top:
```python
df = pd.read_csv(
    "selenium_google_form_sample_data.csv",
    dtype={"Phone Number": str},
)
```
Replace `"selenium_google_form_sample_data.csv"` with the path to your own CSV (e.g. `"my_contacts.csv"`).

### Step 3 — Point the script at your form
Find this line:
```python
form_url = "https://docs.google.com/forms/d/e/1FAIpQLSeqVr5L6-SmgOAAX5ddk-qAT2z8NzHKzSLtXMavN6wNizMAJA/viewform?usp=dialog"
```
Replace the link with your own Google Form's URL.

> Your form must have three text questions titled **Name**, **Phone Number**, and **Email Address** (capitalization doesn't matter). If your questions are worded differently, update the matching text in this line further down the script:
> ```python
> name_box = get_input_by_question(driver, wait, "Name")
> phone_box = get_input_by_question(driver, wait, "Phone number")
> email_box = get_input_by_question(driver, wait, "Email address")
> ```

### Step 4 — Choose how many rows to submit
By default the script only submits the first 3 rows, for safe testing:
```python
for index, row in df.head(3).iterrows():
```
- To submit more, change `3` to any number, e.g. `df.head(20)`.
- To submit every row in the file, remove `.head(3)` entirely: `for index, row in df.iterrows():`

### Step 5 — Run it
```
python main.py
```
A Chrome window will open by itself and submit one form response per row. Progress prints to the console as it goes.

## After it runs

Check `submission_log.csv` — it lists every row with a `success` or `failed` status, and why, so you can see at a glance if anything needs a retry.

## If something times out

Run:
```
python debug_form.py
```
It opens your form and prints out its real field names and button labels, so you can see exactly what to match in Step 3 above.
