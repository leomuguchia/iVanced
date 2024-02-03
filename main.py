import tkinter as tk
from PIL import Image, ImageTk
from pyfiglet import Figlet
import os
import threading
import time
import subprocess
from tkinter import messagebox
from tkinter.simpledialog import askstring
import signal
from tkinter import filedialog
import requests
from bs4 import BeautifulSoup
from colorama import Fore, Style
import tkinter as tk
from tkinter import ttk
from tkinter import Tk, StringVar, OptionMenu, Label, Entry, Button, CENTER
import json
import re
import smtplib
from pyusb import USBMux
from pyusb import DeviceUnlocker

def clear_terminal_screen():
    # Clear the terminal screen
    os.system('clear' if os.name == 'posix' else 'cls')
    
class GuiApp:
    def __init__(self, master):
        self.master = master
        master.title('iVanced by lio')
        master.geometry("1200x700")  # Set the width to 1200 pixels
        master.resizable(False, False)  # Allow resizing
        self.current_folder = "[iVanced]-[~]"
        
        # Initialize USBMux in a separate thread
        usb_mux_thread = threading.Thread(target=self.initialize_usb_mux)
        usb_mux_thread.start()
        
        # Set the default active tab
        self.active_tab = "Quick usage"
        
        
        
        # Create frames
        self.frame = tk.Frame(master, bg="#111111")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Create and place widgets
        self.create_header()
        self.create_widgets()
        
        self.process = None  # Initialize process attribute
        self.is_user_input_required = False
        

    def set_user_input_required(self, value):
        self.is_user_input_required = value

    def create_widgets(self):
        lcw = self.master.winfo_screenwidth() * 0.2
        cw = self.master.winfo_screenwidth() * 0.2
        rcw = self.master.winfo_screenwidth() * 0.35
        self.create_left_column(lcw)
        self.create_center_column(cw)
        self.create_right_column(rcw)

    def create_header(self):
     header_container = tk.Frame(self.frame, height=80, bg="#111111")
     header_container.pack(side="top", fill="x")
 
     # Load and resize the logo image
     logo_path = "icons/profile.png"
     logo_img = Image.open(logo_path)
     logo_img = logo_img.resize((80, 80), Image.NEAREST)
     self.logo_img = ImageTk.PhotoImage(logo_img)
 
     # Software name and version labels
     software_label = tk.Label(header_container, text="iVanced", font=("Baskerville", 20, "bold"), fg="#00FF00", bg="#111111")
     version_label = tk.Label(header_container, text="Version 1.1", font=("Arial", 10), fg="#00FF00", bg="#111111")
 
     # Logo label
     logo_label = tk.Label(header_container, image=self.logo_img, bg="#111111")
     logo_label.image = self.logo_img  # Retain a reference to the image to prevent garbage collection
     logo_label.pack(side="left", padx=10)

     # Pack the labels
     software_label.pack(side="left", padx=(10, 10))
     version_label.pack(side="left")
 
     # Add a cold button
     cold_icon_path = "icons/cold.png"  # Use the correct path for the cold icon
     cold_icon_img = Image.open(cold_icon_path)
     cold_icon_img = cold_icon_img.resize((30, 30), Image.NEAREST)
     cold_icon = ImageTk.PhotoImage(cold_icon_img)
 
     cold_button = tk.Button(header_container, image=cold_icon, bg="#111111", bd=0, highlightthickness=0, command=self.cold_kill)
     cold_button.image = cold_icon
     cold_button.pack(side="right", padx=(5, 15), pady=5)
  
     # Add a warm button
     warm_icon_path = "icons/warm.png"
     warm_icon_img = Image.open(warm_icon_path)
     warm_icon_img = warm_icon_img.resize((31, 31), Image.NEAREST)
     warm_icon = ImageTk.PhotoImage(warm_icon_img)
 
     warm_button = tk.Button(header_container, image=warm_icon, bg="#111111", bd=0, highlightthickness=0, command=self.warm_kill)
     warm_button.image = warm_icon
     warm_button.pack(side="right", padx=(5, 5), pady=5)


    def warm_kill(self):
        self.terminate_processes(self)

    def cold_kill(self):
        self.close_window()
        
    def initialize_usb_mux(self):
        while True:
            try:
                self.usb_mux = USBMux()
                if self.usb_mux.devices:
                    break  # Exit the loop if devices are connected
            except Exception as e:
                print(f"Error initializing USBMux: {e}")
            time.sleep(5)  # Wait for 5 seconds before attempting again
            
    def terminate_processes(self):
        if self.process is not None and self.process.poll() is None:
            self.terminal.print_to_terminal("Processes terminated.")
            self.process.terminate()
            os.killpg(self.process.pid, signal.SIGTERM) 
            self.process.wait()
            self.terminal.input_prompt()

    def close_window(self):
        self.terminate_processes()
        if self.master is not None:
            self.master.destroy()

        
    def create_left_column(self, width):
        container1 = tk.Frame(self.frame, width=width, bg="#0a0a0a")
        container1.pack(side="left", fill=tk.BOTH, expand=False, padx=(0,3))

        buttons_info = [
            ("iOS Activation", self.show_activation_popup),
            ("Ramdisk (iOS 14-16)", self.ramdisk),
            ("Jailbreak iOS", self.jail_break),
            ("Advanced Flash", self.smart_flash),
            ("Recovery Mode", self.recovery_mode),
            ("My Device (All phones!)", self.check_imei),
            ("FMI Unlock", self.fmi_unlock),
        ]

        for text, command in buttons_info:
            button = tk.Button(
                container1,
                text=text,
                command=command,  # Remove the lambda function
                width=22,
                height=2,
                bg="#0a0a0a",
                fg="#4CAF50",
                relief=tk.FLAT,
                borderwidth=2,
                pady=6,
                padx=20,
                bd=0,
                anchor="center",
            )
            button.pack(pady=(5, 5), padx=10, anchor="e")


    def run_terminal_command(self, command_function, *command_args, callback=None):
        try:
            self.process = subprocess.Popen(
                command_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True, preexec_fn=os.setsid
            )

            def update_terminal():
                nonlocal self
                try:
                    line = self.process.stdout.readline()
                    if line:
                        # Check for subprocess request for user input
                        if self.is_user_input_required:
                            self.terminal.print_to_terminal(f"Subprocess requires user input: \n{line}")
                        else:
                            self.terminal.print_to_terminal(f"\n{line}", tag="output")
                            self.master.update_idletasks()  # Update the Tkinter GUI

                        self.master.after(10, update_terminal)  # Schedule the next update
                    elif self.process.poll() is not None:
                        # Command has finished
                        remaining_output = self.process.communicate()[0]
                        if remaining_output:
                            self.terminal.print_to_terminal(f"\n{remaining_output}", tag="output")
                            self.master.update_idletasks()  # Update the Tkinter GUI

                        if callback:
                            # Schedule the callback to be executed after a short delay
                            self.master.after(100, callback)
                except Exception as e:
                    # Handle exceptions during update
                    self.terminal.print_to_terminal(f"Error during terminal update: {e}")

            # Start the initial update
            update_terminal()

        except subprocess.CalledProcessError as e:
            error_message = f"Error:\n {e.stderr}"
            self.terminal.print_to_terminal(error_message, tag="error")

            # Ensure that the input prompt is called in case of an error
            self.terminal.input_prompt()

        except Exception as e:
            error_message = f"An unexpected error occurred:\n {e}"
            self.terminal.print_to_terminal(error_message, tag="error")

            # Ensure that the input prompt is called in case of an unexpected error
            self.terminal.input_prompt()
 
        def handle_interrupt(signum, frame):
         # Handle keyboard interrupt (Ctrl+C)
         self.terminal.print_to_terminal("Process interrupted.")
         self.process.terminate()
         os.killpg(self.process.pid, signal.SIGTERM)  # Send signal to the whole process group
         self.process.wait()
         self.terminal.input_prompt()
 
        # Register the signal handler for Ctrl+C
        signal.signal(signal.SIGINT, handle_interrupt)


    def jail_break(self):
     ios_version = askstring("Jailbreak", "Enter your iOS version (Supports IOS 12 - 16.1):")

     if ios_version is None:
         return

     try:
         ios_version = float(ios_version)
         if 12 <= ios_version <= 14:
             self.start_checkra1n()
         elif 15 <= ios_version <= 16.1:
             self.start_palera1n()
         else:
             self.terminal.print_to_terminal("Invalid iOS version. Please enter a value between 12 and 16.1.\n", tag="output")
             self.terminal.input_prompt()
     except ValueError:
         self.terminal.print_to_terminal("Invalid input. Please enter a numeric value.\n", tag="output")
         self.terminal.input_prompt()


    def start_checkra1n(self):
     # Define the necessary command arguments here
     command_args = ["sudo", "./checkra1n", "-c", "-V", "-E"]
     if not self.usb_mux.devices:
         self.terminal.print_to_terminal('Unable to connect to device!')
         self.terminal.input_prompt()
         return
     self.run_terminal_command(command_args, callback=self.terminal.input_prompt)

    def fmi_unlock(self):
     try:
         # Call the checkbox script
         self.terminal.print_to_terminal("web instanced opened in main terminal")
         self.terminal.print_to_terminal("happy hacking!@^_^@")
         command_args = ["python3", "FMI.py"]
         subprocess.run(command_args, check=True)
         self.terminal.input_prompt()  

     except Exception as e:
         print(f"Error during FMI Unlock: {e}")
     self.terminal.input_prompt()   
        
    def check_imei(self):
        # Initialize Tkinter top-level window
        self.top_level = Tk()
        self.top_level.title("IMEI Check")

        # Set the size and position of the top-level window
        window_width = 400
        window_height = 250
        screen_width = self.top_level.winfo_screenwidth()
        screen_height = self.top_level.winfo_screenheight()
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        self.top_level.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        # Bind the window close event to a function
        self.top_level.protocol("WM_DELETE_WINDOW", self.on_close)

        # Create labels, input field, submit button
        Label(self.top_level, text="Enter IMEI:", pady=5).pack(pady=10)
        self.imei_var = StringVar(self.top_level)
        imei_entry = Entry(self.top_level, bd=3, relief="groove", width=20, textvariable=self.imei_var)
        imei_entry.pack(pady=5)

        Label(self.top_level, text="Enter API Key:", pady=5).pack(pady=10)
        self.api_var = StringVar(self.top_level)
        api_entry = Entry(self.top_level, bd=3, relief="groove", width=20, textvariable=self.api_var)
        api_entry.pack(pady=5)

        submit_button = Button(self.top_level, text="Submit", command=self.submit)
        submit_button.pack(pady=10)
        
    def on_close(self):
     # Function to be called when the window is closed
     self.terminal.input_prompt()
     self.top_level.destroy()    

    def is_valid_imei(self, imei):
        # Implement your IMEI validation logic here
        return len(imei) == 15 and imei.isdigit()

    def submit(self):
        entered_imei = self.imei_var.get()
        entered_api = self.api_var.get()

        # Validate IMEI
        if not self.is_valid_imei(entered_imei):
            self.terminal.print_to_terminal("Invalid IMEI number", tag="error")
            return

        # Call the method to check IMEI and display the result
        self.process_imei(entered_imei, entered_api)
        # Close the top-level window after processing the IMEI
        self.top_level.destroy()
        self.terminal.input_prompt()
    
    def process_imei(self, imei, api):
     api_url = "https://sickw.com/api.php"
     service_id = "30"
 
     curl_command = f'curl "{api_url}?format=json&key={api}&imei={imei}&service={service_id}"'
 
     try:
         result = subprocess.check_output(curl_command, shell=True, text=True)
         json_result = json.loads(result)
 
         if json_result["status"] == "success":
             imei_details = json_result["result"]
 
             # Extract relevant information from the string
             formatted_output = f"IMEI Details for {imei}:\n"
             details_pattern = re.compile(r'<br>(.*?)<br>', re.DOTALL)
             details_matches = details_pattern.findall(imei_details)
 
             for detail in details_matches:
                 # Remove <font> tags and print each detail in its own line
                 clean_detail = re.sub(r'<font color="red">|</font>', '', detail).strip()
                 formatted_output += clean_detail + "\n"
 
             self.terminal.print_to_terminal(formatted_output, tag="output")
         else:
             self.terminal.print_to_terminal(f"Error: {json_result['status']}", tag="error")
         
         self.terminal.input_prompt()
 
     except subprocess.CalledProcessError as e:
         self.terminal.print_to_terminal(f"Error: {e}", tag="error")
         self.terminal.input_prompt()
 
 
    def start_palera1n(self):
     # Display the initial message in the custom terminal
     initial_message = "Choose an option: ['build', 'boot']\n"
     initial_message += "Tip 1: Build fake fs while in DFU mode\n"
     initial_message += "Tip 2: Wait for the device to boot\n"
     initial_message += "Tip 3: Boot the fake fs on the device"
     self.terminal.print_to_terminal(initial_message, tag="output")

     # Create a new Toplevel widget
     choices = ["build", "boot"]
     option_widget = tk.Toplevel(self.master)
     option_widget.title("Choose an option")
     option_widget.geometry("300x50")  # Set the desired width and height
     self.center_on_screen(option_widget)  # Center the widget on the screen

     button_frame = tk.Frame(option_widget, bg="white")
     button_frame.pack(expand=True)

     for choice in choices:
         btn = tk.Button(
             button_frame,
             text=choice,
             command=lambda c=choice: self.handle_palera1n_choice(option_widget, c),
             width=15,
             height=2,
             bg="#0a0a0a",
             fg="green",
             relief=tk.FLAT,
             borderwidth=1,  # Border width set to 1
             pady=6,
             padx=20,
             bd=0,
             activebackground="white",  # Background color on button press
             activeforeground="green",  # Text color on button press
             highlightthickness=0,  # Remove focus border
         )
         btn.pack(side=tk.LEFT, padx=10, pady=10)

    def center_on_screen(self, widget):
     width = widget.winfo_reqwidth()
     height = widget.winfo_reqheight()
     x = (widget.winfo_screenwidth() // 2) - (width // 2)
     y = (widget.winfo_screenheight() // 2) - (height // 2)
     widget.geometry("+{}+{}".format(x, y))


    def handle_palera1n_choice(self, option_widget, user_choice):
     self.terminal.print_to_terminal(f"[-]{user_choice}ing...")
     if not self.usb_mux.devices:
         option_widget.destroy()  # Close the widget after making a choice
         self.terminal.print_to_terminal('Unable to connect to device!')
         self.terminal.input_prompt()
         return
     if user_choice == "boot":
         command_args = ["sudo", "./palera1n-linux-x86_64", "-f"]
         self.run_terminal_command(*command_args, callback=self.terminal.input_prompt)
     elif user_choice == "build":
         command_args = ["sudo", "./palera1n-linux-x86_64", "-cf"]
         self.run_terminal_command(*command_args, callback=self.terminal.input_prompt)

     option_widget.destroy()  # Close the widget after making a choice

    def boot_fakefs(self):
     # Define the necessary command arguments here
     command_args = ["sudo", "./palera1n-linux-x86_64", "-f"]
     self.run_terminal_command(*command_args, callback=self.terminal.input_prompt)

    def build_fakefs(self):
     # Define the necessary command arguments here
     command_args = ["sudo", "./palera1n-linux-x86_64", "-cf"]
     self.run_terminal_command(*command_args, callback=self.terminal.input_prompt)


    def ramdisk(self):
     # Ask for iOS Version
     iOSVer = askstring('Device iOS?', 'On what iOS version are you?')
 
     # Check if iOS Version is provided
     if iOSVer is None:
         return

     # Check if iOS Version is a valid number between 12 and 16
     try:
         iOSVer = int(iOSVer)
         if iOSVer < 12 or iOSVer > 16:
             self.terminal.print_to_terminal("Only supports iOS 12 - 16")
             self.terminal.input_prompt()
             return  
     except ValueError:
         # Invalid iOS version, prompt the user to enter a valid number
         self.terminal.print_to_terminal("Only supports iOS 12 - 16")
         self.terminal.input_prompt()
         return

     # Start the sequence by calling the first command
     self.terminal.print_to_terminal("▌║█║▌│║▌│║▌║▌█║🇷​​🇦​​🇲​​🇩​​🇮​​🇸​​🇰​▌│║▌║▌│║║▌█║▌║█\n")

     # Define the commands
     command_args_clean = ["bash", "./sshrd.sh", "clean"]
     command_args_load = ["bash", "./sshrd.sh", str(iOSVer)]
     command_args_boot = ["bash", "./sshrd.sh", "boot"]
     command_args_ssh = ["bash", "./sshrd.sh", "ssh"]
     command_args_mount = ["bash", "./sshrd.sh", "mount_filesystems"]
     
     if not self.usb_mux.devices:
         self.terminal.print_to_terminal('Unable to connect to device!')
         self.terminal.input_prompt()
         return

     # Execute the commands sequentially using callbacks
     self.run_terminal_command(*command_args_clean, 
                               callback=lambda: self.run_terminal_command(*command_args_load, 
                                                                          callback=lambda: self.run_terminal_command(*command_args_boot, 
                                                                                                                     callback=lambda: self.run_terminal_command(*command_args_ssh, 
                                                                                                                                                                # callback=lambda: self.run_terminal_command(*command_args_mount, 
                                                                                                                                                                                                           callback=self.terminal.input_prompt))))

    
    def show_activation_popup(self):
        # Create a pop-up window
        activation_popup = tk.Toplevel(self.master)
        activation_popup.title("Activation Menu")

        # Center the pop-up window
        self.center_window(activation_popup)

        # Styling for the pop-up window
        activation_popup.configure(bg="#f0f0f0")
        activation_popup.attributes('-alpha', 0.9)

        # Define the commands for the buttons
        commands = {
            "Save Activation Files": self.save_activation_files,
            "Restore Activation Files": self.restore_activation_files,
            "Delete Activation Files": self.delete_activation_files,
        }

        # Create and layout buttons in the pop-up window
        for button_text, command in commands.items():
            button = tk.Button(activation_popup, text=button_text, command=lambda cmd=command: self.execute_and_close(activation_popup, cmd))
            button.pack(pady=10, padx=20, fill=tk.X)

    def execute_and_close(self, popup, command):
        # Close the pop-up window
        popup.destroy()

        # Execute the specified command
        command()
        
    def center_window(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def recovery_mode(self):
     # Display the initial message in the custom terminal
     initial_message = "Choose an option: ['enter recovery mode', 'exit recovery mode']\n"
     self.terminal.print_to_terminal(initial_message, tag="output")

     # Create a new Toplevel widget
     choices = ["enter", "exit"]
     option_widget = tk.Toplevel(self.master)
     option_widget.title("Choose an option")
     option_widget.geometry("300x50")  # Set the desired width and height
     self.center_on_screen(option_widget)  # Center the widget on the screen

     button_frame = tk.Frame(option_widget, bg="white")
     button_frame.pack(expand=True)

     for choice in choices:
         btn = tk.Button(
             button_frame,
             text=choice,
             command=lambda c=choice: self.handle_recovery_choice(option_widget, c),
             width=15,
             height=2,
             bg="#0a0a0a",
             fg="green",
             relief=tk.FLAT,
             borderwidth=1,  
             pady=6,
             padx=20,
             bd=0,
             activebackground="white",  
             activeforeground="green",  
             highlightthickness=0,  
         )
         btn.pack(side=tk.LEFT, padx=10, pady=10)

    def handle_recovery_choice(self, option_widget, user_choice):
     self.terminal.print_to_terminal(f"[-]{user_choice}ing...")
     if user_choice == "enter":
         self.enter_recovery_mode()
     elif user_choice == "exit":
         self.exit_recovery_mode()
         
     option_widget.destroy()  # Close the widget after making a choice
     
     
    def save_activation_files(self):
     command_function = self.save_activation_files
     command_args = ["bash", "./save.sh"]
     
     if not self.usb_mux.devices:
         self.terminal.print_to_terminal('Unable to connect to device!')
         self.terminal.input_prompt()
         return
     
     self.run_terminal_command(command_function, *command_args, callback=self.terminal.input_prompt)

     folder_path = "./files"
     file_name = "activation_record.plist"
     file_path = os.path.join(folder_path, file_name)


    def restore_activation_files(self):
     command_function = self.restore_activation_files
     command_args = ["bash", "./restore.sh"]
     
     if not self.usb_mux.devices:
         self.terminal.print_to_terminal('Unable to connect to device!')
         self.terminal.input_prompt()
         return
     
     self.run_terminal_command(command_function, *command_args, callback=self.terminal.input_prompt)

     folder_path = "./files"
     file_name = "activation_record.plist"
     file_path = os.path.join(folder_path, file_name)


    def delete_activation_files(self):
     command_function = self.delete_activation_files
     command_args = ["bash", "./delete.sh"]
     self.run_terminal_command(command_function, *command_args, callback=self.terminal.input_prompt)


    def get_device_info(self):
     try:
         # Run ideviceinfo to get device information
         ideviceinfo_output = subprocess.check_output(["ideviceinfo"], stderr=subprocess.STDOUT, text=True)

         # Extract specific details into the device_info dictionary
         device_info = {
             'DeviceName': None, 'ProductType': None, 'ProductVersion': None, 'FirmwareVersion': None,
             'ActivationState': None, 'BasebandVersion': None, 'BrickState': None,
             'FirmwareVersion': None, 'HardwareModel': None, 'MobileEquipmentIdentifier:': None, 'TimeZone': None,
             'SerialNumber': None, 'MLBSerialNumber': None, 'UniqueDeviceID': None, 'BuildVersion': None,
             'TrustedHostAttached': None, 'PartitionType': None, 'BasebandSerialNumber': None, 'BasebandStatus': None,
             'SIMStatus': None, 'SIMTrayStatus': None, 'DieID:': None, 'DeviceClass': None,
             'InternationalMobileEquipmentIdentity': None, 'UniqueChipID': None, 'UntrustedHostBUID': None,
             'TelephonyCapability': None, 'PasswordProtected':None, 'ProductName': None, 'TimeIntervalSince1970': None,
         }
 
         for line in ideviceinfo_output.splitlines():
             # Check if the line contains the expected separator ":"
             if ":" not in line:
                 continue
 
              # Extract additional details
             for key in device_info.keys():
                 if key in line:
                     value = line.split(":")[1].strip()
                     device_info[key] = value
                     
         return device_info
 
     except subprocess.CalledProcessError as e:
         print(f"Error running ideviceinfo: {e}")
         return None
  
    # Method to enter the connected Apple device into recovery mode using ideviceenterrecovery
    def get_recovery_mode(self, UniqueDeviceID):
        try:
            # Run ideviceenterrecovery to send the device into recovery mode
            subprocess.run(["./device/ideviceenterrecovery", UniqueDeviceID])

            return True

        except subprocess.CalledProcessError as e:
            print(f"Error running ideviceenterrecovery: {e.output}")
            return False
        
    def enter_recovery_mode(self):
        # Get the device UniqueDeviceID
        device_info = self.get_device_info()
        if device_info == None:
            self.terminal.print_to_terminal('[-]Unable to connect to device')
            self.terminal.input_prompt()
            return
        
        device_UniqueDeviceID = device_info['UniqueDeviceID']
        if device_UniqueDeviceID:
            self.terminal.print_to_terminal(f"Device UniqueDeviceID: {device_UniqueDeviceID}")
            # Enter the device into recovery mode
            success = self.get_recovery_mode(device_UniqueDeviceID)

            if success:
                self.terminal.print_to_terminal("Device entered into recovery mode successfully.")
            else:
                self.terminal.print_to_terminal("Failed to enter the device into recovery mode.")
        else:
            self.terminal.print_to_terminal("Failed to get device UniqueDeviceID.")
        
        self.terminal.input_prompt()   
            
             
     #sshrd script commands
    def smart_flash(self):
        # Show a warning message before proceeding
        result = messagebox.askquestion(
            "Warning",
            "This is a low-level iOS firmware reset, recommended only for iOS firmware developers and technicians as it offers advanced control. We recommend iTunes if you are not any of the above to avoid bricking your device.\n\nProceed?",
        )
        
        if not self.usb_mux.devices:
            self.terminal.print_to_terminal('Unable to connect to device!')
            self.terminal.input_prompt()
            return
        
        if result == "yes":
            # Define command_args_clean
            command_args_clean = ["bash", "./sshrd.sh", "reset"]
            self.terminal.print_to_terminal("\nresetting device..")
            self.run_terminal_command(*command_args_clean, callback=self.terminal.input_prompt)

    def sshrd_reboot(self,args=None):
        command_args = ["bash", "./sshrd.sh", "reboot"]
        if not self.usb_mux.devices:
         self.terminal.print_to_terminal('Unable to connect to device!')
         self.terminal.input_prompt()
         return
        self.run_terminal_command(*command_args, callback=self.terminal.input_prompt)

    def sshrd_reset(self,args=None):
        command_args = ["bash", "./sshrd.sh", "reset"]
        if not self.usb_mux.devices:
         self.terminal.print_to_terminal('Unable to connect to device!')
         self.terminal.input_prompt()
         return
        self.run_terminal_command(*command_args, callback=self.terminal.input_prompt)

    def sshrd_dump_blobs(self,args=None):
        command_args = ["bash", "./sshrd.sh", "dump-blobs"]
        if not self.usb_mux.devices:
         self.terminal.print_to_terminal('Unable to connect to device!')
         self.terminal.input_prompt()
         return
        self.run_terminal_command(*command_args, callback=self.terminal.input_prompt)

    def sshrd_clean(self,args=None):
        command_args = ["bash", "./sshrd.sh", "clean"]
        self.run_terminal_command(*command_args, callback=self.terminal.input_prompt)

    def sshrd_ssh(self,args=None):
        command_args = ["bash", "./sshrd.sh", "ssh"]
        if not self.usb_mux.devices:
         self.terminal.print_to_terminal('Unable to connect to device!')
         self.terminal.input_prompt()
         return
        self.run_terminal_command(*command_args, callback=self.terminal.input_prompt)

    def sshrd_mount_file_systems(self,args=None):
        command_args = ["bash", "./sshrd.sh", "mount_filesystems"]
        if not self.usb_mux.devices:
         self.terminal.print_to_terminal('Unable to connect to device!')
         self.terminal.input_prompt()
         return
        self.run_terminal_command(*command_args, callback=self.terminal.input_prompt)

    def sshrd_boot(self,args=None):
        command_args = ["bash", "./sshrd.sh", "boot"]
        if not self.usb_mux.devices:
         self.terminal.print_to_terminal('Unable to connect to device!')
         self.terminal.input_prompt()
         return
        self.run_terminal_command(*command_args, callback=self.terminal.input_prompt)

    def sshrd_sshelp(self, args=None):
     help_message = """
     \nHelp for SSH commands:
     - To reboot the device: reboot
     - To erase all data: reset
     - To dump onboard SHSH blobs: dump-blobs
     - To delete old SSH ramdisk: clean
     - To connect to SSH on your device: ssh
     - To mount filesystems: mount-file-systems
     - To boot the ramdisk: boot
     - For SSH help: sshelp
     """
     self.terminal.print_to_terminal(help_message)
   
        
    #iRecovery tool commands
    def exit_recovery_mode(self, args=None):
     command_function = self.exit_recovery_mode
     command_args = ["./device/irecovery", "-n"]
     if not self.usb_mux.devices:
         self.terminal.print_to_terminal('Unable to connect to device!')
         self.terminal.input_prompt()
         return
     self.run_terminal_command(command_function, *command_args)
     self.terminal.input_prompt()
         
    def upload_file(self, file_path):
     command_function = self.upload_file
     file_path = filedialog.askopenfilename(title="Select a file")
     command_args = ["./device/irecovery", "-f", file_path]
     if not self.usb_mux.devices:
         self.terminal.print_to_terminal('Unable to connect to device!')
         self.terminal.input_prompt()
         return
     self.run_terminal_command(command_function, *command_args)
     self.terminal.input_prompt()

    def shell(self, args=None):
     command_function = self.shell
     command_args = ["./device/irecovery", "-s"]
     if not self.usb_mux.devices:
         self.terminal.print_to_terminal('Unable to connect to device!')
         self.terminal.input_prompt()
         return
     self.run_terminal_command(command_function, *command_args)
     self.terminal.input_prompt()

    def single_command(self, custom_command):
     command_function = self.single_command
     command_args = ["./device/irecovery", "-c", custom_command]
     if not self.usb_mux.devices:
         self.terminal.print_to_terminal('Unable to connect to device!')
         self.terminal.input_prompt()
         return
     self.run_terminal_command(command_function, *command_args)
     self.terminal.input_prompt()

    def query_device(self, args=None):
     command_function = self.query_device
     command_args = ["./device/irecovery", "-q"]
     if not self.usb_mux.devices:
         self.terminal.print_to_terminal('Unable to connect to device!')
         self.terminal.input_prompt()
         return
     self.run_terminal_command(command_function, *command_args)
     self.terminal.input_prompt()

    def apple_support(self, args=None):
     command_function = self.apple_support
     command_args = ["./device/irecovery", "-a"]
     self.run_terminal_command(command_function, *command_args)
     self.terminal.input_prompt()
 
    def usb_reset(self, args=None):
     command_function = self.usb_reset
     command_args = ["./device/irecovery", "-r"]
     if not self.usb_mux.devices:
         self.terminal.print_to_terminal('Unable to connect to device!')
         self.terminal.input_prompt()
         return
     self.run_terminal_command(command_function, *command_args)
     self.terminal.input_prompt()

    def batch_scripting(self, script_file):
     command_function = self.batch_scripting
     command_args = ["./device/irecovery", "-e", script_file]
     if not self.usb_mux.devices:
         self.terminal.print_to_terminal('Unable to connect to device!')
         self.terminal.input_prompt()
         return
     self.run_terminal_command(command_function, *command_args)
     self.terminal.input_prompt()
 
    def raw_commands(self, raw_command):
        flag = input("Choose flag: [-x21, -x40, -xA1] ")
        command_args = ["./device/irecovery", flag, raw_command]
        if not self.usb_mux.devices:
         self.terminal.print_to_terminal('Unable to connect to device!')
         self.terminal.input_prompt()
         return
        self.run_terminal_command(*command_args)
        self.terminal.input_prompt()
  
    def irecovery_help(self, args=None):
     help_message = """
     \nHelp for recovery commands:
     ufile - You can upload a file to 0x9000000
     2wayshell - You can spawn a shell to do all sorts of neat things Once it has spawned, you can type 'help' and iBoot will respond with its built-in command list
     sincomm - Sends a single command to the device *without* spawning a shell.
     excomm - Sends Chronic Dev's + Geohot's latest usb exploit.
     applesupport - Get all apples devices manufacturer's details
     usbres - Reset USB
     batscript - this allows you to send commands to iBoot from a pre written list of commands, this also supports scripting such as /auto-boot and /upload <file>
     rawcomm - You can now send raw commands via the -x21 -x40 or -xA1 flags. type rawhelp to view supported raw commands
     rchelp - see a list of available recovery commands and their functionality
     rawhelp - see a list of available raw recoverycommands
     """
     self.terminal.print_to_terminal(help_message)
     self.terminal.input_prompt()
       
     
    def create_center_column(self, width):
        container2 = tk.Frame(self.frame, width=width, bg="#0a0a0a")
        container2.pack(side="left", fill=tk.BOTH, expand=False)

        # Center column contains the custom terminal
        self.terminal_frame = tk.Frame(container2, bg="#0a0a0a")
        self.terminal_frame.pack(side="left", fill=tk.BOTH, expand=True)

        # Create the custom terminal inside the new frame
        self.terminal = CustomTerminal(self.terminal_frame, self)

    def create_right_column(self, width):
        container3 = tk.Frame(self.frame, width=width, bg="#111111")
        container3.pack(side="left", fill=tk.BOTH, expand=True, padx=(3,0))

        # Buttons Frame
        buttons_frame = tk.Frame(container3, bg="#111111")
        buttons_frame.pack(pady=(0, 3), side="top")  # Set side to "top"

        # Instructions Frame
        instructions_frame = tk.Frame(container3, bg="#0a0a0a")
        instructions_frame.pack(side="top", fill=tk.BOTH, expand=True)  # Set fill and expand

        # Create a frame for each tab
        tabs = {
         "Quick usage": self.create_tab(instructions_frame, [
         "**********Quick Flash*********\n\n"
         "Buy usage instructions only for $50",
         tk.Button(
             buttons_frame,
             text='Buy for $50',
             command=lambda: self.payment(),  # Corrected the lambda function
             width=10,
             height=2,
             relief=tk.FLAT,
             pady=2,
             padx=1,
             bd=0,
             anchor="center",
         ),
         "Or else you can figure it alone for free\n\n"
         "Happy@hacking!"
         "\n\n\n\n\n\n",
         ]),

            "Device": self.create_tab(instructions_frame, ["Connected device details"]),
            "Supported": self.create_tab(instructions_frame, ["Supported content","set up more instructions here....\n\n\n\n\n\n",]),
            "Jailbreaks": self.create_tab(instructions_frame, ["Jailbreaks content","set up more instructions here....\n\n\n\n\n\n",],),
        }

        # Create buttons dynamically
        self.tab_buttons = {}  # Dictionary to store button references

        for text, tab in tabs.items():
            button = tk.Button(
                buttons_frame,
                text=text,
                command=lambda t=tab, b=text: self.show_tab(t, b),
                width=10,
                height=2,
                relief=tk.FLAT,
                pady=2,
                padx=1,
                bd=0,
                anchor="center",
            )
            button.pack(side="left", padx=5)  # Set side to "left"
            self.tab_buttons[text] = button  # Store button reference

        # Show the default active tab
        self.show_tab(tabs[self.active_tab], self.active_tab)
        
        # Create a frame for device details with a border
        self.right_device_details_container = tk.Frame(container3, bg="#0a0a0a")
        self.right_device_details_container.pack(side="bottom", pady=(5, 0), fill=tk.BOTH, expand=True)
 
        # Create a smaller smartphone icon
        self.smartphone_icon = tk.PhotoImage(file="icons/iphone.png").subsample(3)  
        smartphone_label = tk.Label(self.right_device_details_container, image=self.smartphone_icon, bg="#0a0a0a")
        smartphone_label.image = self.smartphone_icon
        smartphone_label.grid(row=0, column=0, padx=5, pady=(10, 0))  # Added pady for spacing

        # Display the number of devices below the smartphone icon
        device_count_label = tk.Label(self.right_device_details_container, text=f" {len(self.usb_mux.devices)} ", fg="black", bg="white")
        device_count_label.grid(row=0, column=0)
        
        # Display device details vertically
        self.device_details_label = tk.Label(self.right_device_details_container, text="", font=("Helvetica", 12),
                                             fg="gray", bg="#0a0a0a", justify="left", padx=20, pady=5, wraplength=200)
        self.device_details_label.grid(row=0, column=1)
        
        # Add a refresh button
        refresh_icon = Image.open("icons/refresh.png") 
        refresh_icon = refresh_icon.resize((20, 18))
        refresh_icon = ImageTk.PhotoImage(refresh_icon)

        refresh_button = tk.Button(self.right_device_details_container, image=refresh_icon, bg="#0a0a0a", bd=0, highlightthickness=0, command=self.display_device_info)
        refresh_button.image = refresh_icon
        refresh_button.grid(row=1, column=0)
        
        # Show the default message
        self.display_device_info()
        
    def is_valid_email(self, email):
        email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        return bool(email_regex.match(email))

    def send_email(self, email_content):
        recipient_email = 'muguchialio@gmail.com'
        smtp_server = 'smtp.mailtrap.io'  
        smtp_port = 25  
        smtp_username = ''  
        smtp_password = '' 

        # Check if the email content has a correct format
        if not self.is_valid_email(recipient_email):
            self.terminal.print_to_terminal('Invalid recipient email format. Please enter a valid email address.')
            return

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)

                # Construct and send email
                server.sendmail(smtp_username, recipient_email, f'Subject: User wants to buy instructions for iVanced\n\n{email_content}')

            self.terminal.print_to_terminal('Email sent successfully!')
        except Exception as e:
            self.terminal.print_to_terminal(f'Error sending email: {e}')

    def payment(self):
        email_content = askstring("Checkout $50. Enter content to send via email")

        if email_content:
            self.send_email(email_content)
        else:
            self.terminal.print_to_terminal('Invalid email content. Please enter some text.')

    def create_tab(self, parent, content):
        tab = tk.Frame(parent, bg="#0a0a0a")
        for instruction in content:
            label = tk.Label(tab, text=instruction, fg="#FFA500", bg="#0a0a0a", justify="left", padx=10,
                             pady=5, wraplength=350)
            label.pack(anchor="w")
        return tab

    def show_tab(self, tab, button_text):
        # Hide all tabs
        for child in tab.master.winfo_children():
            child.pack_forget()

        # Show the selected tab
        tab.pack(fill=tk.BOTH, expand=True)

        # Highlight the active button
        for text, button in self.tab_buttons.items():
            if text == button_text:
                button.configure(bg="#333333")  # Change the background color of the active button
            else:
                button.configure(bg="#0a0a0a")  # Reset background color for other buttons               
     
    def display_device_info(self, args=None):
     # Check if there are devices
     if not self.usb_mux.devices:
         # No devices connected
         self.device_details_label.config(text="No device connected")
     else:
         # Devices connected
         device_info = self.get_device_info()
         device = self.usb_mux.devices[0]  # Display details of the first connected device
         details_text = f"Device ID: {device.devid}\n" \
                        f"DeviceName: {device_info['DeviceName']}\n" \
                        f"ProductType {device_info['ProductType']}\n" \
                        f"Serial Number: {device.serial}\n" \
                        f"Product ID: {device.usbprod}\n" \
                        f"Location ID: {device.location}\n"\
                        f"ProductVersion: {device_info['iOSVersion']}"

         device_state = self.get_device_state(device)  # Replace with actual method
         details_text += f"\nDevice State: {device_state}"
 
         self.device_details_label.config(text=details_text)
 
    def get_device_state(self, device):
     # Replace this with the actual method to get the device state
     # For example, you might use device properties like device.serial or device.usbprod
     # to determine the state, or use additional methods from the USBMux class.
     return "Unknown"
    
    def create_tab(self, parent, content):
         tab = tk.Frame(parent, bg="#0a0a0a")
         for instruction in content:
             label = tk.Label(tab, text=instruction, fg="#FFA500", bg="#0a0a0a", justify="left", padx=20,
                              pady=5, wraplength=350)
             label.pack(anchor="w")
         return tab

    def show_tab(self, tab, button_text):
         # Hide all tabs
         for child in tab.master.winfo_children():
             child.pack_forget()
 
         # Show the selected tab
         tab.pack(fill=tk.BOTH, expand=True)
 
         # Highlight the active button
         for text, button in self.tab_buttons.items():
             if text == button_text:
                 button.configure(bg="#333333")  # Change the background color of the active button
             else:
                 button.configure(bg="#0a0a0a")  # Reset background color for other buttons
    
                
class CustomTerminal:
    def __init__(self, master,gui):
        self.master = master
        master.pack(side="left", fill=tk.BOTH, expand=True)
        self.setup_text_widget()
        self.gui=gui
        self.usb_mux = USBMux()
        self.device_unlocker = DeviceUnlocker()
        self.setup_commands()

        self.initial_working_directory = os.getcwd()
        self.current_folder = self.initial_working_directory
        self.text_widget.bind("<BackSpace>", self.handle_backspace)

        # Add the Figlet header with the new ASCII art and horizontal line
        figlet_header = self.generate_figlet_header("iShell", font="small")
        self.print_to_terminal(figlet_header, tag="header")

        # Add a welcome message and disclaimer with text wrapping
        welcome_message = (
            "\nWelcome to iTerm - Your Interactive Shell\n\n"
            "This tool is for educational and testing purposes only. "
            "Usage for malicious or illegal activities is prohibited. "
            "You are solely responsible for your actions. "
            "The author is not liable for any damage."
        )
        self.print_to_terminal(f"{welcome_message}\n", tag="header")

        self.input_prompt()

    def setup_text_widget(self):
     visible_lines = 20  # Adjust this based on your preference
     extra_lines_at_bottom = 5  # Adjust this based on how many extra lines you want at the bottom
     total_height = visible_lines + extra_lines_at_bottom

     self.text_widget = tk.Text(
         self.master,
         wrap=tk.WORD,
         font=("Courier", 12),
         bg="black",
         fg="white",
         insertbackground="white",
         insertwidth=4,
         width=58,
         height=total_height,  # Set the total height
         bd=0,  
         highlightthickness=0,
        )
     self.text_widget.pack(expand=True, fill="both", pady=(5, 0))
     self.text_widget.tag_config("header", foreground="grey")
     self.text_widget.tag_config("input", foreground="green")
    

    def setup_commands(self):
        self.commands = {
            #general terminal commands
            "pwd": self.show_current_folder,
            "list": self.list_commands,
            "cd": self.change_directory,
            "ls": self.ls_command,
            
            #sshrd script commands
            "reboot": self.gui.sshrd_reboot,
            "reset": self.gui.sshrd_reset,
            "dumpblobs": self.gui.sshrd_dump_blobs,
            "clean": self.gui.sshrd_clean,
            "sshd": self.gui.sshrd_ssh,
            "mofisys": self.gui.sshrd_mount_file_systems,
            "boot": self.gui.sshrd_boot,
            "sshelp": self.gui.sshrd_sshelp,
            
            # Commands for iRecovery
            "exitrecovery": self.gui.exit_recovery_mode,
            "uploadfile": self.gui.upload_file,
            "shell": self.gui.shell,
            "sincomm": self.gui.single_command,
            "device?": self.gui.query_device,
            "applesupport": self.gui.apple_support,
            "usbres": self.gui.usb_reset,
            "batscript": self.gui.batch_scripting,
            "rawcomm": self.gui.raw_commands,
            "rchelp": self.gui.irecovery_help,
            "enterecovery": self.gui.get_recovery_mode,
            "refresh": self.gui.display_device_info,
            
            #commands for pyusb
            "passlimit": self.fetch_passcode_limit_plist,
            "install": self.usbmux_install,
            "usbssh": self.usbmux_ssh,
            "portforward": self.usbmux_port_forward,
        }

    def input_prompt(self):
     current_folder_name = os.path.basename(self.current_folder)
     prompt_text = f"[{current_folder_name}] > "
     self.text_widget.insert(tk.END, f"\n{prompt_text}\n", "input_prompt")
     self.text_widget.tag_configure("input_prompt", foreground="#00FF00")  # Set color for the input prompt
     self.text_widget.tag_config("folder", foreground="white")
     self.text_widget.tag_config("file", foreground="grey")
     self.text_widget.see(tk.END)
     self.text_widget.bind("<Return>", lambda event: self.process_user_input(event, prompt_text))

     # Set the focus on the text widget
     self.text_widget.focus_set()
     
    def handle_backspace(self, event):
     # Get the current cursor position
     cursor_position = self.text_widget.index(tk.CURRENT)

     # Check if the cursor is not at the start of the current line
     if not cursor_position.endswith(".0"):
         # Delete the character to the left of the cursor
         self.text_widget.delete(tk.CURRENT + "-1c", tk.CURRENT)


    def process_user_input(self, event, prompt_text):
     user_input = self.text_widget.get("end-2l lineend", tk.END).strip()
     
     # Remove input prompt from the user input
     command = user_input.replace(prompt_text, "").strip()

     if not command:
         self.input_prompt()
         return
 
     # Clear the current line (input prompt and user command)
     self.text_widget.delete("end-2l lineend", tk.END)
 
     # Process the user's command
     self.execute_command(command)
 
     # Reinsert the input prompt
     self.input_prompt()


    def execute_command(self, command):
     command_parts = command.split()
     command_name = command_parts[0]

     if command_name in self.commands:
         self.commands[command_name](command_parts[1:])
     else:
         self.print_to_terminal(f"Command not found: {command_name}\nRun list for available commands", tag="output")


    def show_current_folder(self, args):
     command_output = self.current_folder
     self.print_to_terminal("pwd", command_output, tag="output")

    def list_commands(self, args):
     command_info = {
         "pwd": "Check the current directory",
         "list": "List available commands",
         "cd": "Change current directory",
         "ls": "List contents of current folder",
         "reboot": "Reboot the system",
         "reset": "Reset the system",
         "dumpblobs": "Dump system blobs",
         "clean": "Clean the system",
         "sshd": "Start SSH daemon",
         "mofisys": "Mount file systems",
         "boot": "Boot the system",
         "sshelp": "Display SSH help",
         "ufile": "Upload a file",
         "shell": "Start a two-way shell",
         "sincomm": "Execute a single command",
         "device?": "query device info",
         "applesupport": "Apple devices developer details",
         "usbres": "Reset USB connection",
         "batscript": "Execute batch scripting",
         "rawcomm": "Execute raw commands",
         "passlimit":"",
         "usbssh":"",
         "install":"",
         "portforward":"",
     }

     output_lines = [f"{command} - {info}" for command, info in command_info.items()]
     self.print_to_terminal("ls", "\n".join(output_lines), tag="output")


    def change_directory(self, args):
     if not args:
         self.print_to_terminal("Usage: cd [folder]", tag="output")
         return

     new_folder = args[0]

     if new_folder == "return":
         # Go back to the previous top directory
         parent_directory = os.path.dirname(self.current_folder)
         if os.path.commonpath([parent_directory, self.initial_working_directory]) == self.initial_working_directory:
             self.current_folder = parent_directory
         else:
             self.print_to_terminal("You are in the root folder!", tag="output")
             return
     else:
         new_path = os.path.join(self.current_folder, new_folder)
 
         if os.path.exists(new_path) and os.path.isdir(new_path):
             self.current_folder = new_path
         else:
             self.print_to_terminal("Invalid folder", tag="output")
             return

     relative_path = os.path.relpath(self.current_folder, self.initial_working_directory)
     self.input_prompt()
     self.print_to_terminal(f"Changed directory to: {os.path.join('iVanced', relative_path)}", tag="output")


    def ls_command(self, args):
     folder = args[0] if args else self.current_folder
 
     try:
         contents = sorted(os.listdir(folder))
 
         # Separate folders and files
         folders = [item for item in contents if os.path.isdir(os.path.join(folder, item))]
         files = [item for item in contents if os.path.isfile(os.path.join(folder, item))]
 
         # Print folders at the top
         for folder_name in folders:
             self.print_to_terminal(f"{folder_name}/", tag="folder")
 
         # Print files at the bottom
         for file_name in files:
              self.print_to_terminal(file_name, tag="file")
 
     except FileNotFoundError:
          self.print_to_terminal(f"Directory not found: {folder}", tag="output")

    #pyusb functions
    def usbmux_port_forward(self, args):
     if not self.usb_mux.devices:
         self.print_to_terminal("No connected devices.")
         return

     device_to_connect = self.usb_mux.devices[0]  
     device_port_to_forward = args[1] if args[1] else "22"
     host_port_to_forward = args[0] if args[0] else "localhost"
 
     forwarded_socket = self.usb_mux.forward_port(device_to_connect, device_port_to_forward, host_port_to_forward)
     self.print_to_terminal(f"Port forwarded. You can now connect to localhost:{host_port_to_forward}")
 
    def usbmux_ssh(self, command_args):
        if not self.usb_mux.devices:
         self.print_to_terminal("No connected devices.")
         return

        success = self.usb_mux.run_ssh(command_args)
        if success:
         self.print_to_terminal(f"SSH command executed successfully.")
        else:
         self.print_to_terminal("Failed to execute SSH command.")
        
    def fetch_passcode_limit_plist(self, args=None):
        if not self.usb_mux.devices:
         self.print_to_terminal("No connected devices.")
         return
    
        success = self.device_unlocker.check_lock_files()
        if success:
         self.print_to_terminal(f"Passcode limit file  found! Test successful")
        else:
         self.print_to_terminal("File not found in specified location")
         
    def usbmux_install(self, args):
    #  if not self.usb_mux.devices:
    #      self.print_to_terminal("No connected devices.")
    #      return

     app_path = command_args[0] if command_args else "/"
     device_to_connect = self.usb_mux.devices[0] 
     success = self.usb_mux.installation_service(app_path)
     if success:
         self.print_to_terminal("Installation service completed.")
     else:
         self.print_to_terminal("Failed!")

        

    def print_to_terminal(self, command_name, message="", tag="output"):
     if message:
         self.text_widget.insert(tk.END, f"{command_name}\n{message}\n", tag)
     else:
         self.text_widget.insert(tk.END, f"{command_name}\n", tag)
    
     # Scroll to the end
     self.text_widget.see(tk.END)
     self.master.update_idletasks()  # Update the Tkinter GUI


    def generate_figlet_header(self, text, font="Courier New"):
        figlet = Figlet(font=font)
        return figlet.renderText(text)


if __name__ == "__main__":
    clear_terminal_screen()
    print("iVanced\nStarted...\n\npress ctrl + C to quit!")
    root = tk.Tk()
    app = GuiApp(root)
    root.mainloop()
