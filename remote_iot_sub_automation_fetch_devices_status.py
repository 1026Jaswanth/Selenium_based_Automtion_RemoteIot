import os
import time
import logging
import glob
import json
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Define log directory (log_folder_1 in same directory as script)
script_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(script_dir, "log_folder_1")

# Create the log directory if it doesn't exist
os.makedirs(log_dir, exist_ok=True)

# Generate a timestamped log filename inside the log folder
log_filename = datetime.now().strftime("%Y%m%d_%H%M%S_script1.log")
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
try:
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
        logging.info("Configuration loaded successfully.")
except Exception as e:
    logging.error(f"Error loading configuration: {e}")
    exit(1)


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


def login(driver, username, password):
    try:
        wait = WebDriverWait(driver, 10)
        driver.get("https://remoteiot.com/portal/?link=login")
        logging.info("Navigated to login page.")

        username_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text']")))
        username_field.send_keys(username)
        logging.debug("Entered username.")

        password_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password']")))
        password_field.send_keys(password)
        logging.debug("Entered password.")

        if password_field.get_attribute("value"):
            password_field.send_keys(Keys.RETURN)
            logging.info("Submitted login form.")
        else:
            logging.error("Password field is empty!")
            return False

        time.sleep(5)
        logging.info("Login successful.")
        return True
    except Exception as e:
        logging.error(f"Login failed: {e}")
        return False


def download_device_list(driver, download_path):
    try:
        wait = WebDriverWait(driver, 10)
        menu_button = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                             "/html/body/div[1]/div/div[2]/div/div[2]/div/div/div/div[1]/div/div[1]/div/div/div[2]/div/div[5]/div")))
        menu_button.click()
        logging.info("Navigated to device menu.")

        time.sleep(5)
        export_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[2]/div/div/span[14]/span")))
        export_button.click()
        logging.info("Clicked export button.")

        time.sleep(10)  # Wait for download to complete
        downloaded_files = sorted(glob.glob(os.path.join(download_path, "Devices*.csv")), key=os.path.getmtime,
                                  reverse=True)

        if downloaded_files:
            logging.info("Device list download completed.")
            return downloaded_files[0]
        else:
            logging.warning("Download failed. No file found.")
            return None
    except Exception as e:
        logging.error(f"Error downloading device list: {e}")
        return None


def filter_offline_devices(file_path, save_path):
    try:
        df = pd.read_csv(file_path)  # Load CSV instead of XLSX
        logging.info("Device list loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading file: {e}")
        return

    if "Status" not in df.columns:
        logging.warning("Column 'Status' not found in downloaded file.")
        return

    df_offline = df[df["Status"].str.lower() == "online"]
    offline_path = os.path.join(save_path, "Tracking_online_Devices.xlsx")

    try:
        df_offline.to_excel(offline_path, index=False)
        logging.info(f"Offline devices saved to: {offline_path}")
    except Exception as e:
        logging.error(f"Error saving offline devices: {e}")


def main():
    download_path = os.path.expanduser(config["script_1"]["download_path"])  # Path to downloads folder
    save_path = config["script_1"]["save_path"]

    logging.info("Starting script execution.")
    try:
        options = webdriver.ChromeOptions()
        #options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--start-maximized")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--force-device-scale-factor=1")  # Forces 100% scale
        options.add_argument("--high-dpi-support=1")  # Ensures high DPI support
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        logging.info("WebDriver initialized.")
    except Exception as e:
        logging.error(f"Error initializing WebDriver: {e}")
        return

    creds = load_credentials()
    username = creds.get("username", "")
    password = creds.get("password", "")

    if login(driver, username, password):
        file_path = download_device_list(driver, download_path)
        if file_path:
            filter_offline_devices(file_path, save_path)

    driver.quit()
    logging.info("Script execution completed.")
    print("1st_script_completed")


if __name__ == "__main__":
    main()
