import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import subprocess
import re
import os

load_dotenv()
imei_array = []

with open('imei.txt', 'r') as imei_file:
    for line in imei_file:
        imei = line.strip()
        imei_array.append(imei)

for imei in imei_array:
    while True:
        try:
            # Create a new Chrome browser instance
            driver = webdriver.Chrome()

            driver.implicitly_wait(10)

            url = "https://sickw.com"
            driver.get(url)

            # Find the IMEI input field
            imei_input = driver.find_element(By.ID, "imei")
            imei_input.clear()
            imei_input.send_keys(imei)

            # Wait for the service dropdown to be ready
            service_select = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "service"))
            )

            # Select the service
            service_dropdown = Select(service_select)
            service_dropdown.select_by_value("30")  # Replace with the desired option value

            # Click the submit button
            submit_button = driver.find_element(By.ID, "submit")
            submit_button.click()

            # Wait for the result
            time.sleep(10)  # Increase the wait time if needed

            # Get the result image link
            result_div = driver.find_element(By.ID, "result")
            result_image = result_div.find_element(By.CLASS_NAME, "class-2").find_element(By.TAG_NAME, "img")
            result_image_link = result_image.get_attribute("src")

            print("Result Image Link:", result_image_link)

        except Exception as e:
            print(f"Error for IMEI {imei}: {e}")
        finally:
            # Close the browser regardless of success or failure
            driver.quit()
            break  # Break out of the while loop after processing one IMEI
