from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time

# Initialize WebDriver
driver = webdriver.Chrome()

# Login Details
login_url = "https://ems.digineous.com/#/login"
raw_data_url = "https://ems.digineous.com/#/common/rawdata"
user_id = "gayatree_polymers"
password = "Pass@123"

try:
    # Step 1: Log in
    driver.get(login_url)
    time.sleep(3)

    # Locate username and password fields and login button
    driver.find_element(By.XPATH, "//input[@placeholder='Enter Username']").send_keys(user_id)
    driver.find_element(By.XPATH, "//input[@placeholder='Enter your password']").send_keys(password)
    driver.find_element(By.XPATH, "//button[@class='btn signin signinpointer']").click()
    time.sleep(5)  # Allow login to process

    # Step 2: Navigate to the raw data page
    driver.get(raw_data_url)
    time.sleep(5)

    # Step 3: Select "Energy Meter" from the dropdown
    dropdown = driver.find_element(By.XPATH, "//div[@id='mui-component-select-deviceNo']")
    dropdown.click()  # Open the dropdown
    time.sleep(1)  # Allow dropdown options to load

    # Select the "Energy Meter" option
    energy_meter_option = driver.find_element(By.XPATH, "//li[contains(text(), 'Energy Meter')]")
    energy_meter_option.click()
    time.sleep(2)  # Allow selection to process

    # Step 4: Click the OK button
    ok_button = driver.find_element(By.XPATH, "//button[contains(text(), 'OK')]")
    ok_button.click()
    time.sleep(5)  # Allow time for data to load

    # Step 5: Check if data is displayed
    page_source = driver.page_source
    if "No Data" in page_source or "Data not available" in page_source:
        print("No data is being received.")
    else:
        print("Data is being received.")

        # Step 6: Check the Date Time column's first row
        try:
            # Locate the first row of the Date Time column
            date_time_cell_xpath = "//table[@class='MuiTable-root']//tr[1]/td[1]"

            # Debug: Print the page source to check if the table exists
            print("Page source snapshot:")
            print(driver.page_source)

            # Wait for the table to be visible
            date_time_element = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, date_time_cell_xpath))
            )
            date_time_text = date_time_element.text

            # Debugging: Print the Date Time text to verify
            print(f"Date Time text from table: {date_time_text}")

            # Parse and compare the Date Time
            try:
                table_date_time = datetime.strptime(date_time_text, "%d-%b-%Y %H:%M:%S")
                current_time = datetime.now()

                # Check if the table date time is within the last 10 minutes
                time_difference = current_time - table_date_time
                if timedelta(minutes=0) <= time_difference <= timedelta(minutes=10):
                    print("The Date Time column's first row matches the criteria.")
                else:
                    print("The Date Time column's first row does not match the criteria.")
            except ValueError as e:
                print(f"Error parsing Date Time: {e}")

        except Exception as e:
            print(f"Error while checking Date Time column: {e}")



finally:
    # Close the browser
    driver.quit()
