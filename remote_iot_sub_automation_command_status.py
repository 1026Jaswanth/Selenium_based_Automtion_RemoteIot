import os
import time
import pandas as pd
import logging
import json
import ast
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

# Define log directory (log_folder_3 in same directory as script)
script_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(script_dir, "log_folder_3")

# Create the log directory if it doesn't exist
os.makedirs(log_dir, exist_ok=True)

# Generate a timestamped log filename inside the log folder
log_filename = datetime.now().strftime("%Y%m%d_%H%M%S_script3.log")
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
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Load configuration
try:
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
    logging.info("Configuration file loaded successfully.")
except Exception as e:
    logging.error(f"Failed to load config.json: {e}")
    exit(1)

EXPECTED_VERSIONS = {
    "Expected_output": "1.0.0"
}


def load_credentials(file_path="credentials.conf"):
    credentials = {}
    try:
        with open(file_path, "r") as cred_file:
            for line in cred_file:
                key, value = line.strip().split("=")
                credentials[key] = value
        logging.info("Credentials loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading credentials: {e}")
        exit(1)
    return credentials


def get_latest_downloaded_file(download_dir):
    try:
        files = [os.path.join(download_dir, f) for f in os.listdir(download_dir) if
                 os.path.isfile(os.path.join(download_dir, f))]
        latest_file = max(files, key=os.path.getctime) if files else None
        if latest_file:
            logging.info(f"Latest downloaded file found: {latest_file}")
        else:
            logging.warning("No downloaded files found.")
        return latest_file
    except Exception as e:
        logging.error(f"Error finding latest file: {e}")
        return None


def wait_for_file_download_complete(download_dir, timeout=60):
    """Waits until the file starting with `base_filename` is fully downloaded."""
    end_time = time.time() + timeout
    logging.info("Waiting for jobs CSV to be fully downloaded...")

    while time.time() < end_time:
        all_files = os.listdir(download_dir)
        # Filter files: containing 'jobs', ends with .csv, and no .crdownload
        jobs_files = [
            os.path.join(download_dir, f)
            for f in all_files
            if "jobs" in f.lower() and f.lower().endswith(".csv") and not f.endswith(".crdownload")
        ]

        if jobs_files:
            latest_file = max(jobs_files, key=os.path.getctime)
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    f.read(10)  # Try to read few bytes
                logging.info(f"Job file download completed: {latest_file}")
                return latest_file
            except Exception as e:
                logging.debug(f"File not ready yet: {e}")

        time.sleep(1)

    logging.error("Timeout: jobs.csv not downloaded completely within expected time.")
    return None


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
        else:
            logging.error("Error: Password field is empty!")
            return False

        time.sleep(5)
        logging.info("Login successful.")
        return True
    except Exception as e:
        logging.error(f"Login failed: {e}")
        return False


def create_batch_job(driver, device_list):
    try:
        logging.info("Creating batch job...")
        wait = WebDriverWait(driver, 10)

        batch_jobs = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='dashboard-menu']/div/div[4]/div[3]/span/span[2]")))
        batch_jobs.click()
        time.sleep(2)

        dropdown = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                          "//*[@id='portal-982480788']/div/div[2]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div[5]/div/span")))
        dropdown.click()
        time.sleep(2)

        new_job = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='portal-982480788-overlays']/div[2]/div/div/span[1]/span")))
        new_job.click()
        time.sleep(5)

        job_name_field = wait.until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[2]/div[3]/div/div/div[3]/div/div/div[1]/div/table/tbody/tr[1]/td[3]/input")))
        job_name_field.send_keys("IotSecurity")
        time.sleep(4)

        search_text = f'"{"|".join(device_list)}"'
        search_box = wait.until(EC.presence_of_element_located((By.XPATH,
                                                                "/html/body/div[2]/div[3]/div/div/div[3]/div/div/div[1]/div/table/tbody/tr[5]/td[3]/div/div/div[3]/div/div[1]/div/input")))
        search_box.send_keys(search_text)
        time.sleep(3)
        search_icon = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                             "/html/body/div[2]/div[3]/div/div/div[3]/div/div/div[1]/div/table/tbody/tr[5]/td[3]/div/div/div[3]/div/div[1]/div/div/span")))
        search_icon.click()
        time.sleep(3)

        # Select all listed devices
        select_devices = wait.until(
            EC.presence_of_element_located((By.XPATH,
                                            "/html/body/div[2]/div[3]/div/div/div[3]/div/div/div[1]/div/table/tbody/tr[5]/td[3]/div/div/div[1]/div/select[1]")))
        select_devices.send_keys(Keys.CONTROL + "a")
        time.sleep(2)
        # Click Wrap Button
        wrap_button = wait.until(
            EC.element_to_be_clickable((By.XPATH,
                                        "/html/body/div[2]/div[3]/div/div/div[3]/div/div/div[1]/div/table/tbody/tr[5]/td[3]/div/div/div[1]/div/div[2]/div[1]")))
        wrap_button.click()

        time.sleep(2)

        # Verify Selected Devices
        wait.until(EC.presence_of_element_located((By.XPATH,
                                                   "/html/body/div[2]/div[3]/div/div/div[3]/div/div/div[1]/div/table/tbody/tr[5]/td[3]/div/div/div[1]/div/select[2]")))

        # Enter command Name
        script_field = wait.until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[2]/div[3]/div/div/div[3]/div/div/div[1]/div/table/tbody/tr[8]/td[3]/textarea")))
        script_field.send_keys(
            "grep -oP 'IoTSecurity_\\K[0-9]+\\.[0-9]+\\.[0-9]+' /home/pi/IoTSecurity/security-release.version | head -1 || echo 0.0.0")
        time.sleep(2)  # Wait for the dropdown to appear

        # Scroll down to make the submit button visible
        submit_button = wait.until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[2]/div[3]/div/div/div[3]/div/div/div[3]/div/div/div/div/div[3]/div")))

        # Method 1: Scroll using JavaScript
        driver.execute_script("arguments[0].scrollIntoView();", submit_button)
        time.sleep(2)  # Allow time for scrolling

        # Method 2: Scroll using ActionChains (Alternative)
        actions = ActionChains(driver)
        actions.move_to_element(submit_button).perform()
        time.sleep(3)

        # Click Submit
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div[2]/div[3]/div/div/div[3]/div/div/div[3]/div/div/div/div/div[3]/div"))).click()

        time.sleep(300)  # 300 -- 5 minutes

        menu_tab = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div[1]/div/div[2]/div/div[2]/div/div/div/div[1]/div/div/div[2]/div/div[5]/div")))
        menu_tab.click()
        time.sleep(2)

        export_table = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[2]/div/div/span[5]")))
        export_table.click()
        time.sleep(5)

        logging.info("Batch job successfully created.")
    except Exception as e:
        logging.error(f"Error creating batch job: {e}")


def update_output_file(output_path, new_file_path):
    try:
        df = pd.read_csv(output_path)

        def parse_result(result):
            try:
                if not isinstance(result, str):
                    result = str(result)
                result = result.strip()

                if not result:  # Empty result
                    return "Failed"
                if result == EXPECTED_VERSIONS.get("Expected_output"):
                    return "Successful"
                else:
                    return "Failed"
            except Exception as e:
                logging.error(f"Error parsing result: {e}")
                return "Failed"

        def determine_status(row):
            if row.get("Status", "").lower() != "executed":
                return "Failed"
            return parse_result(row.get("Result", ""))

        df["Command Status"] = df.apply(determine_status, axis=1)
        df.to_excel(new_file_path, index=False)
        logging.info(f"Updated output file saved at: {new_file_path}")
    except Exception as e:
        logging.error(f"Error updating output file: {e}")


def main():
    logging.info("Starting script execution...")

    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--force-device-scale-factor=1")  # Forces 100% scale
    options.add_argument("--high-dpi-support=1")  # Ensures high DPI support
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    creds = load_credentials()
    username = creds["username"]
    password = creds["password"]

    if not login(driver, username, password):
        logging.error("Login failed!")
        driver.quit()
        return

    try:
        input_path = config["script_3"]["input_path"]
        download_dir = os.path.expanduser(config["script_3"]["download_dir"])
        new_output_path = config["script_3"]["new_output_path"]

        df = pd.read_excel(input_path)
        device_list = df['Device Name'].tolist()

        create_batch_job(driver, device_list)
        time.sleep(10)

        # latest_file = get_latest_downloaded_file(download_dir)
        latest_file = wait_for_file_download_complete(download_dir)
        if latest_file:
            logging.info(f"Processing latest file: {latest_file}")
            update_output_file(latest_file, new_output_path)
            filtered_df = df[df['Job Name'].str.contains('IotSecurity', na=False)]
            filtered_df.to_excel(new_output_path, index=False)

            # Now reload and get processed devices
            output_df = pd.read_excel(new_output_path)
            processed_devices = output_df['Device Name'].dropna().unique().tolist()

            # Now safely log
            logging.info(f"Removed {len(processed_devices)} devices from tracking file.")
            # Remove processed devices from Tracking_online_Devices.xlsx
            try:
                tracking_file = os.path.join(config["script_1"]["save_path"], "Tracking_online_Devices.xlsx")
                if os.path.exists(tracking_file):
                    tracking_df = pd.read_excel(tracking_file)
                    output_df = pd.read_excel(new_output_path)

                    processed_devices = output_df['Device Name'].dropna().unique().tolist()
                    updated_tracking_df = tracking_df[~tracking_df['Device Name'].isin(processed_devices)]

                    # Save the updated tracking sheet
                    updated_tracking_df.to_excel(tracking_file, index=False)
                    logging.info("Processed devices removed from Tracking_online_Devices.xlsx")
                else:
                    logging.warning(f"Tracking file not found: {tracking_file}")
            except Exception as e:
                logging.error(f"Error updating Tracking file: {e}")
        else:
            logging.warning("No valid result file found!")

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        driver.quit()
        logging.info("Script execution completed.")
        print("3rd_script_completed")


if __name__ == "__main__":
    main()
