from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# Website login credentials
username = "sprl_superadmin"
password = "Pass@123"
login_url = "https://sprl.digineous.com/#/login"

# Path to your WebDriver (adjust as necessary for your browser)
driver_path = "C:\\Users\\rohan\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"

service = Service(driver_path)
driver = webdriver.Chrome(service=service)

try:
    # Open the login page
    driver.get(login_url)
    time.sleep(3)  # Wait for the page to load

    # Enter username
    username_field = driver.find_element(By.XPATH, "//input[@placeholder='Enter Username']")
    username_field.send_keys(username)

    # Enter password
    password_field = driver.find_element(By.XPATH, "//input[@placeholder='Enter your password']")
    password_field.send_keys(password)

    # Click login button
    login_button = driver.find_element(By.XPATH, "//button[text()='Login']")
    login_button.click()
    time.sleep(5)  # Wait for login and redirection

    # Navigate to the device status page
    driver.get("https://sprl.digineous.com/#/plant_architecture/device_status")

    # Debugging: Get the page source to check if the table is loaded
    page_source = driver.page_source
    with open("page_source.html", "w", encoding="utf-8") as file:
        file.write(page_source)

    print("Page source saved to 'page_source.html'. Please inspect this file for the table content.")

    # Loop indefinitely until rows are loaded
    while True:
        try:
            # Execute JavaScript to check if rows are loaded in the table
            rows = driver.execute_script('return document.querySelectorAll(".MuiTableRow-root").length')

            if rows > 0:
                print("Table rows are loaded!")
                # Try again to get rows after they are loaded
                rows_elements = driver.find_elements(By.CSS_SELECTOR, ".MuiTableRow-root")
                print(f"Found {len(rows_elements)} rows in the table.")

                # Extracting the data from each row
                for row in rows_elements:
                    columns = row.find_elements(By.TAG_NAME, "td")  # Find all columns in the row
                    if columns:
                        plant_name = columns[0].text
                        machine_id = columns[1].text
                        machine_name = columns[2].text
                        date_time = columns[3].text
                        status_column = columns[4]

                        # Check if there is any content in the Device Status column
                        status_text = status_column.text
                        if status_text:
                            print(f"Plant: {plant_name}, Machine ID: {machine_id}, Machine_name: {machine_name}, Last_Data_Recived_on: {date_time}, Status: {status_text}")
                        else:
                            # Check if there's a div or other indication of status (if applicable)
                            try:
                                svg_icon = status_column.find_element(By.TAG_NAME, "svg")
                                svg_color = svg_icon.get_attribute("style")
                                if "red" in svg_color:
                                    print(f"Plant: {plant_name}, Machine ID: {machine_id}, Machine_name: {machine_name}, Last_Data_Recived_on: {date_time}, Status: Disconnected")
                                elif "green" in svg_color:
                                    # print(f"Plant: {plant_name}, Machine ID: {machine_id}, Machine_name: {machine_name}, Last_Data_Recived_on: {date_time}, Status: Connected")
                                    pass
                            except:
                                print("NO DATA FOUND")
                break  # Exit the loop once rows are found
        except Exception as e:
            print(f"Error: {e}. Retrying...")
            time.sleep(2)  # Sleep briefly before trying again

finally:
    # Close the WebDriver
    driver.quit()
