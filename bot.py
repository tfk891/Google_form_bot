import json
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Load your data
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Google Form URL
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeq13VdWxYiCpreEznyKxY2NQQmantZM3ft83CY7bM6uoIvjg/viewform"

# Setup Chrome
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Mapping form labels to JSON keys
label_map = {
    "Name": "q1", 
    "Email": "q2", 
    "Phone number": "q3", 
    "Which category of books would you like to suggest?": "q4", 
    "Book's Name": "q5", 
    "Writers Name": "q6", 
    "Your opinion or details about the book": "q7"
}

def normalize_label(text):
    return text.lower().replace("*", "").strip()

def fill_form():
    driver.get(FORM_URL)
    time.sleep(7)

    filled_count = 0
    question_divs = driver.find_elements(By.CSS_SELECTOR, 'div[role="listitem"]')

    for q in question_divs:
        try:
            label = q.find_element(By.CSS_SELECTOR, 'div[role="heading"]').text
            label_key = normalize_label(label)

            matched = None
            for expected_label in label_map:
                if normalize_label(expected_label) == label_key:
                    matched = label_map[expected_label]
                    break

            if matched:
                value = random.choice(data[matched])
                input_box = q.find_element(By.CSS_SELECTOR, 'input, textarea')
                input_box.send_keys(value)
                filled_count += 1
        except Exception as e:
            print(f"[!] Error filling a field: {e}")
            continue

    if filled_count < len(label_map):
        print(f"[!] Only filled {filled_count}/{len(label_map)} fields.")
        return False

    # Submit the form
    try:
        wait = WebDriverWait(driver, 10)
        submit_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            '//div[@role="button" and (contains(., "Submit") or contains(., "জমা দিন"))]'
        )))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_btn)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", submit_btn)
        time.sleep(2)
        print("[✓] Submitted successfully.")
        return True
    except Exception as e:
        print("[!] Submit button error:", e)
        return False

# Main loop
for i in range(101):
    print(f"[+] Submitting form {i+1}/101")
    success = fill_form()
    if not success:
        print("[!] Skipping due to failure.")
    time.sleep(12)

driver.quit()
print("[✓] All done.")
