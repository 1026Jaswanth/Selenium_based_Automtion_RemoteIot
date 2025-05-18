import time
import subprocess

# Define script paths
script1 = r"C:\Users\jyarrams\PycharmProjects\IoT_Security_RemoteIoT_Automation\remote_iot_sub_automation_fetch_devices_status.py"
script2 = r"C:\Users\jyarrams\PycharmProjects\IoT_Security_RemoteIoT_Automation\remote_iot_sub_automation_Script_execution.py"
script3 = r"C:\Users\jyarrams\PycharmProjects\IoT_Security_RemoteIoT_Automation\remote_iot_sub_automation_command_status.py"

# Function to execute each script sequentially
def run_script(script_path):
    print(f"Running script: {script_path}")
    result = subprocess.run(["python", script_path], capture_output=True, text=True)
    output = result.stdout.strip()
    print(f"Output: {output}")
    return output

def run_scripts_sequentially():
    output1 = run_script(script1)
    if "1st_script_completed" in output1:
        time.sleep(5)
        output2 = run_script(script2)
        if "2nd_script_completed" in output2:
            time.sleep(5)
            output3 = run_script(script3)
            if "3rd_script_completed" in output3:
                print("All scripts executed successfully!")

# Execute scripts sequentially
run_scripts_sequentially()

