import pytest
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


def test_request():
    # initialize driver
    driver = webdriver.Chrome()

    try:
        # Open the website
        driver.get("http://localhost:8000/")

        # Wait for the page to load
        time.sleep(5)

        # click on map and wait for load
        map_button = driver.find_element(By.ID, "map")
        map_button.click()
        time.sleep(5)

        # button is <button id="requestPMI">Request PMI</button>
        end_test_button = driver.find_element(By.ID, "requestPMI")
        end_test_button.click()

        # give time for API to fetch results from NASA API and load results table
        time.sleep(20)
        results_table = driver.find_element(By.ID, "results")
        assert results_table.is_displayed()
        
    finally:
        # Close the WebDriver
        driver.quit()

def test_upload():
    # initialize driver
    driver = webdriver.Chrome()

    try:
        # Open the website
        driver.get("http://localhost:8000/")

        # Wait for the page to load
        time.sleep(5)

        # click on map and wait for load
        map_button = driver.find_element(By.ID, "map")
        map_button.click()
        time.sleep(5)

        # button is <button id="upload">Upload</button>
        upload_button = driver.find_element(By.ID, "reportMildew")
        upload_button.click()

        submit_button = driver.find_element(By.ID, "submitDate")
        assert submit_button.is_displayed()
        # click on submit button
        time.sleep(2)
        submit_button.click()

        # give time for API to fetch results from NASA API and load results table
        time.sleep(5)
        # alert will pop up
        alert = driver.switch_to.alert
        alert_text = alert.text
        assert alert_text == "Report submitted successfully."
        
    finally:
        # Close the WebDriver
        driver.quit()