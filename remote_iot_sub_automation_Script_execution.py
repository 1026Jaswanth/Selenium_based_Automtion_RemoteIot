# Execute the script in RemoteIoT for the selected devices
import os
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
import json

# Define log directory (log_folder_2 in same directory as script)
script_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(script_dir, "log_folder_2")

# Create the log directory if it doesn't exist
os.makedirs(log_dir, exist_ok=True)

# Generate a timestamped log filename inside the log folder
log_filename = datetime.now().strftime("%Y%m%d_%H%M%S_script2.log")
log_file = os.path.join(log_dir, log_filename)
# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logging.info("Logging initialized. Log file: %s", log_filename)

# Load configuration
with open("config.json", "r") as config_file:
    config = json.load(config_file)

batch_delay = config["script_2"]["batch_delay"]
def load_credentials(file_path="credentials.conf"):
    credentials = {}
    try:
        with open(file_path, "r") as cred_file:
            for line in cred_file:
                key, value = line.strip().split("=")
                credentials[key] = value
        logging.info("Credentials loaded successfully.")
    except Exception as e:
        logging.error("Failed to load credentials: %s", e)
    return credentials


def login(driver, username, password):
    try:
        wait = WebDriverWait(driver, 10)
        driver.get("https://remoteiot.com/portal/?link=login")

        username_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text']")))
        username_field.send_keys(username)
        time.sleep(1)

        password_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password']")))
        password_field.send_keys(password)
        time.sleep(1)

        if password_field.get_attribute("value"):
            password_field.send_keys(Keys.RETURN)
            logging.info("Login submitted.")
        else:
            logging.error("Password field is empty!")
            return False

        time.sleep(5)
        logging.info("Login successful.")
        return True
    except Exception as e:
        logging.error("Login failed: %s", e)
        return False


def create_batch_job(driver, device_list, executed_devices, output_path):
    try:
        logging.info("Creating batch job for devices: %s", device_list)
        wait = WebDriverWait(driver, 10)
        batch_jobs = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='dashboard-menu']/div/div[4]/div[3]/span/span[2]")))
        batch_jobs.click()
        time.sleep(2)

        # Select New Job
        dropdown = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                          "//*[@id='portal-982480788']/div/div[2]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div[5]/div/span")))
        dropdown.click()
        time.sleep(2)

        new_job = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='portal-982480788-overlays']/div[2]/div/div/span[1]/span")))
        new_job.click()
        time.sleep(5)

        # Enter Job Name
        job_name_field = wait.until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[2]/div[3]/div/div/div[3]/div/div/div[1]/div/table/tbody/tr[1]/td[3]/input")))
        job_name_field.send_keys("IotSecurity batch job_automation_execution")
        time.sleep(4)

        # Execute the script
        search_text = f'"{"|".join(device_list)}"'
        search_box = wait.until(EC.presence_of_element_located((By.XPATH,
                                                                "/html/body/div[2]/div[3]/div/div/div[3]/div/div/div[1]/div/table/tbody/tr[5]/td[3]/div/div/div[3]/div/div[1]/div/input")))
        search_box.send_keys(search_text)
        time.sleep(3)
        search_icon = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                             "/html/body/div[2]/div[3]/div/div/div[3]/div/div/div[1]/div/table/tbody/tr[5]/td[3]/div/div/div[3]/div/div[1]/div/div/span")))
        search_icon.click()
        time.sleep(3)

        select_devices = wait.until(
            EC.presence_of_element_located((By.XPATH,
                                            "/html/body/div[2]/div[3]/div/div/div[3]/div/div/div[1]/div/table/tbody/tr[5]/td[3]/div/div/div[1]/div/select[1]")))
        select_devices.send_keys(Keys.CONTROL + "a")
        time.sleep(5)
        wrap_button = wait.until(
            EC.element_to_be_clickable((By.XPATH,
                                        "/html/body/div[2]/div[3]/div/div/div[3]/div/div/div[1]/div/table/tbody/tr[5]/td[3]/div/div/div[1]/div/div[2]/div[1]")))
        wrap_button.click()
        time.sleep(3)

        execute_script = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                "/html/body/div[2]/div[3]/div/div/div[3]/div/div/div[1]/div/table/tbody/tr[7]/td[3]/div/span[1]/label")))
        execute_script.click()

        script_field = wait.until(EC.presence_of_element_located((By.XPATH,
                                                                  "/html/body/div[2]/div[3]/div/div/div[3]/div/div/div[1]/div/table/tbody/tr[8]/td[3]/div/div/div/div/input")))  # "//*[@id='gwt-uid-41']/div/div/div/input")))
        script_field.send_keys("eru_misc.sh")
        time.sleep(2)
        script_field.send_keys(Keys.DOWN)
        script_field.send_keys(Keys.RETURN)
        time.sleep(2)

        maxim_windw = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                "/html/body/div[2]/div[3]/div/div/div[2]/div[1]")))
        maxim_windw.click()
        time.sleep(2)

        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                               "/html/body/div[2]/div[3]/div/div/div[3]/div/div/div[3]/div/div/div/div/div[3]/div")))
        submit_button.click()
        time.sleep(5)
        driver.refresh()

        executed_devices.extend(device_list)
        pd.DataFrame({'Executed Devices': executed_devices}).to_excel(output_path, index=False)
        logging.info("Batch job executed successfully.")
    except Exception as e:
        logging.error("Failed to execute batch job: %s", e)


def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--force-device-scale-factor=1")  # Forces 100% scale
    options.add_argument("--high-dpi-support=1")  # Ensures high DPI support
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    creds = load_credentials()
    username = creds.get("username")
    password = creds.get("password")

    if not username or not password:
        logging.critical("Missing credentials. Terminating script.")
        return

    if not login(driver, username, password):
        logging.critical("Login failed! Terminating script.")
        driver.quit()
        return

    input_path = config["script_2"]["input_path"]
    output_path = config["script_2"]["output_path"]
    device_count = config["script_2"]["device_count"]

    df = pd.read_excel(input_path)
    device_list = df['Device Name'].tolist()
    executed_devices = []
    batch_size = 10 if device_count >= 100 else 5
    total_devices = len(device_list)

    # Execute batches
    for i in range(0, min(device_count, total_devices), batch_size):
        batch = device_list[i:i + batch_size]
        create_batch_job(driver, batch, executed_devices, output_path)
        logging.info(f"Batch {i // batch_size + 1} executed.")
        time.sleep(batch_delay)
    driver.quit()
    logging.info("Script execution completed successfully.")
    print("2nd_script_completed")


if __name__ == "__main__":
    main()
