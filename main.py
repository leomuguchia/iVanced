import tkinter as tk
from PIL import Image, ImageTk
from pyfiglet import Figlet
import os
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
from ansi2html import Ansi2HTMLConverter

class GuiApp:
    def __init__(self, master):
        self.master = master
        master.title('iVanced by lio')
        master.geometry("1200x700")  # Set the width to 1200 pixels
        master.resizable(False, False)  # Allow resizing
        self.current_folder = "[iVanced]-[~]"

        # Create frames
        self.frame = tk.Frame(master, bg="#0a0a0a")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Create and place widgets
        self.create_header()
        self.create_widgets()
        
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
        header_container.pack(side="top", fill="x", pady=(10, 0))
        logo_path = "profile.png"
        logo_img = Image.open(logo_path)
        logo_img = logo_img.resize((80, 80), Image.NEAREST)
        self.logo_img = ImageTk.PhotoImage(logo_img)

        # Software name and version labels
        software_label = tk.Label(header_container, text="iVanced", font=("Arial", 14, "bold"), fg="#00FF00", bg="#111111")
        version_label = tk.Label(header_container, text="Version 1.1", font=("Arial", 10), fg="#00FF00", bg="#111111")

        # Logo, software name, and version placement
        logo_label = tk.Label(header_container, bg="#111111")
        logo_label.image = self.logo_img  # Retain a reference to the image to prevent garbage collection
        logo_label.config(image=self.logo_img)
        logo_label.pack(side="left", padx=10)
        software_label.pack(side="left", padx=(10, 10))
        version_label.pack(side="left")

    def create_left_column(self, width):
        container1 = tk.Frame(self.frame, width=width, bg="#0a0a0a")
        container1.pack(side="left", fill=tk.BOTH, expand=False)

        buttons_info = [
            ("iOS Activation", self.show_activation_popup),
            ("Ramdisk (iOS 14-16)", self.ramdisk),
            ("Jailbreak iOS", self.jail_break),
            ("Advanced Flash", self.smart_flash),
            ("Exit Recovery Mode", self.exit_recovery_mode),
            ("My Device (All phones!)", self.check_imei),
            ("FMI Unlock (All iphones!)", self.fmi_unlock),
        ]

        for text, command in buttons_info:
            button = tk.Button(
                container1,
                text=text,
                command=command,  # Remove the lambda function
                width=25,
                height=2,
                bg="#0a0a0a",
                fg="#4CAF50",
                relief=tk.FLAT,
                borderwidth=2,
                pady=6,
                padx=20,
                bd=0,
                anchor="e",
            )
            button.pack(pady=(5, 5), padx=10, anchor="e")


    def run_terminal_command(self, command_function, *command_args, callback=None):
     try:
         process = subprocess.Popen(
             command_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True, preexec_fn=os.setsid
         )
 
         def update_terminal():
             nonlocal process
             try:
                 line = process.stdout.readline()
                 if line:
                     # Check for subprocess request for user input
                     if self.is_user_input_required:
                         self.terminal.print_to_terminal(f"Subprocess requires user input: \n{line}")
                     else:
                         self.terminal.print_to_terminal(f"\n{line}", tag="output")
                         self.master.update_idletasks()  # Update the Tkinter GUI
 
                     self.master.after(10, update_terminal)  # Schedule the next update
                 elif process.poll() is not None:
                     # Command has finished
                     remaining_output = process.communicate()[0]
                     if remaining_output:
                         self.terminal.print_to_terminal(f"\n{remaining_output}", tag="output")
                         self.master.update_idletasks()  # Update the Tkinter GUI
 
                     if callback:
                         # Schedule the callback to be executed after a short delay
                         self.master.after(100, callback)
             except Exception as e:
                 # Handle exceptions during update
                 print(f"Error during terminal update: {e}")
 
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
         self.terminal.print_to_terminal("Command interrupted.")
         process.terminate()
         os.killpg(process.pid, signal.SIGTERM)  # Send signal to the whole process group
         process.wait()
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
             self.run_terminal_command(self.start_checkra1n, "sudo", "./checkra1n", "-c", "-V", "-E", callback=self.terminal.input_prompt)
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
             bg="#111111",
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

     # Form subprocess commands
     command_args_clean = ["bash", "./sshrd.sh", "clean"]
     command_args_load = ["bash", "./sshrd.sh", str(iOSVer)]
     command_args_boot = ["bash", "./sshrd.sh", "boot"]

     # Execute subprocess commands
     self.terminal.print_to_terminal("▌║█║▌│║▌│║▌║▌█║🇷​​🇦​​🇲​​🇩​​🇮​​🇸​​🇰​▌│║▌║▌│║║▌█║▌║█\n")
     self.run_terminal_command(*command_args_clean,callback=self.terminal.input_prompt)
     self.run_terminal_command(*command_args_load,callback=self.terminal.input_prompt)
     self.run_terminal_command(*command_args_boot,callback=self.terminal.input_prompt)

    
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


    def save_activation_files(self):
     command_function = self.save_activation_files
     command_args = ["bash", "./save.sh"]
     self.run_terminal_command(command_function, *command_args, callback=self.terminal.input_prompt)

     folder_path = "./files"
     file_name = "activation_record.plist"
     file_path = os.path.join(folder_path, file_name)


    def restore_activation_files(self):
     command_function = self.restore_activation_files
     command_args = ["bash", "./restore.sh"]
     self.run_terminal_command(command_function, *command_args, callback=self.terminal.input_prompt)

     folder_path = "./files"
     file_name = "activation_record.plist"
     file_path = os.path.join(folder_path, file_name)


    def delete_activation_files(self):
     command_function = self.delete_activation_files
     command_args = ["bash", "./delete.sh"]
     self.run_terminal_command(command_function, *command_args, callback=self.terminal.input_prompt)

     #sshrd script commands
    def smart_flash(self):
        # Show a warning message before proceeding
        result = messagebox.askquestion(
            "Warning",
            "This is a low-level iOS firmware reset, recommended only for iOS firmware developers and technicians as it offers advanced control. We recommend iTunes if you are not any of the above to avoid bricking your device.\n\nProceed?",
        )

        if result == "yes":
            # Define command_args_clean
            command_args_clean = ["bash", "./sshrd.sh", "reset"]
            self.terminal.print_to_terminal("\nresetting device..\n")
            self.run_terminal_command(*command_args_clean, callback=self.terminal.input_prompt)

    def sshrd_reboot(self,args=None):
        command_args = ["bash", "./sshrd.sh", "reboot"]
        self.run_terminal_command(*command_args, callback=self.terminal.input_prompt)

    def sshrd_reset(self,args=None):
        command_args = ["bash", "./sshrd.sh", "reset"]
        self.run_terminal_command(*command_args, callback=self.terminal.input_prompt)

    def sshrd_dump_blobs(self,args=None):
        command_args = ["bash", "./sshrd.sh", "dump-blobs"]
        self.run_terminal_command(*command_args, callback=self.terminal.input_prompt)

    def sshrd_clean(self,args=None):
        command_args = ["bash", "./sshrd.sh", "clean"]
        self.run_terminal_command(*command_args, callback=self.terminal.input_prompt)

    def sshrd_ssh(self,args=None):
        command_args = ["bash", "./sshrd.sh", "ssh"]
        self.run_terminal_command(*command_args, callback=self.terminal.input_prompt)

    def sshrd_mount_file_systems(self,args=None):
        command_args = ["bash", "./sshrd.sh", "mount_filesystems"]
        self.run_terminal_command(*command_args, callback=self.terminal.input_prompt)

    def sshrd_boot(self,args=None):
        command_args = ["bash", "./sshrd.sh", "boot"]
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
     command_args = ["./device/irecovery", "-s"]
     self.run_terminal_command(command_function, *command_args)
         
    def upload_file(self, file_path):
     command_function = self.upload_file
     file_path = filedialog.askopenfilename(title="Select a file")
     command_args = ["./device/irecovery", "-f", file_path]
     self.run_terminal_command(command_function, *command_args)

    def two_way_shell(self, args=None):
     command_function = self.two_way_shell
     command_args = ["./device/irecovery", "-s"]
     self.run_terminal_command(command_function, *command_args)

    def single_command(self, custom_command):
     command_function = self.single_command
     command_args = ["./device/irecovery", "-c", custom_command]
     self.run_terminal_command(command_function, *command_args)

    def exploit_command(self, args=None):
     command_function = self.exploit_command
     command_args = ["./device/irecovery", "-e"]
     self.run_terminal_command(command_function, *command_args)

    def apple_support(self, args=None):
     command_function = self.apple_support
     command_args = ["./device/irecovery", "-a"]
     self.run_terminal_command(command_function, *command_args)
     self.terminal.input_prompt()
 
    def usb_reset(self, args=None):
     command_function = self.usb_reset
     command_args = ["./device/irecovery", "-r"]
     self.run_terminal_command(command_function, *command_args)

    def batch_scripting(self, script_file):
     command_function = self.batch_scripting
     command_args = ["./device/irecovery", "-b", script_file]
     self.run_terminal_command(command_function, *command_args)
 
    def raw_commands(self, raw_command):
     command_function = self.raw_commands
     command_args = ["./device/irecovery", "-x21", "-x40", "-xA1", raw_command]
     self.run_terminal_command(command_function, *command_args)
  
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
        container3 = tk.Frame(self.frame, width=width, bg="#0a0a0a")
        container3.pack(side="left", fill=tk.BOTH, expand=True)

        # Buttons Frame
        buttons_frame = tk.Frame(container3, bg="#0a0a0a")
        buttons_frame.pack(pady=(5, 5), side="top")  # Set side to "top"

        # Instructions Frame
        instructions_frame = tk.Frame(container3, bg="#0a0a0a")
        instructions_frame.pack(side="top", pady=(5, 5), fill=tk.BOTH, expand=True)  # Set fill and expand

        # Create a frame for each tab
        tabs = {
            "Quick usage": self.create_tab(instructions_frame, [
                "**********Quick Flash*********\n\n"
                "Step 1: Connect your iPhone",
                "Step 2: Enter recovery mode then DFU ",
                "set up more instructions here....",
                "set up more instructions here....",
                "set up more instructions here...."
            ]),
            "Supported": self.create_tab(instructions_frame, ["Supported content"]),
            "Jailbreaks": self.create_tab(instructions_frame, ["Jailbreaks content"]),
            "Manual": self.create_tab(instructions_frame, ["Manual content"]),
        }

        # Create buttons dynamically
        for text, tab in tabs.items():
            button = tk.Button(
                buttons_frame,
                text=text,
                command=lambda t=tab: self.show_tab(t),
                width=10,
                height=2,
                bg="#111111",
                fg="white",
                relief=tk.FLAT,
                borderwidth=2,
                pady=2,
                padx=2,
                bd=0,
                anchor="center",
            )
            button.pack(side="left", padx=5)  # Set side to "left"

    def create_tab(self, parent, content):
        tab = tk.Frame(parent, bg="#0a0a0a")
        for instruction in content:
            label = tk.Label(tab, text=instruction, fg="#FFA500", bg="#0a0a0a", justify="left", padx=20,
                             pady=5, wraplength=350)
            label.pack(anchor="w")
        return tab

    def show_tab(self, tab):
        # Hide all tabs
        for child in tab.master.winfo_children():
            child.pack_forget()
        # Show the selected tab
        tab.pack(fill=tk.BOTH, expand=True)

        
class CustomTerminal:
    def __init__(self, master,gui):
        self.master = master
        master.pack(side="left", fill=tk.BOTH, expand=True)
        self.setup_text_widget()
        self.gui=gui
        self.setup_commands()

        self.initial_working_directory = os.getcwd()
        self.current_folder = self.initial_working_directory

        # Add the Figlet header with the new ASCII art and horizontal line
        figlet_header = self.generate_figlet_header("iShell", font="small")
        self.print_to_terminal(figlet_header, tag="header")

        # Add a welcome message and disclaimer with text wrapping
        welcome_message = (
            "\nWelcome to iTerm - Your Interactive Shell\n\n"
            "This tool is for educational and testing purposes only. "
            "Usage for malicious or illegal activities is prohibited. "
            "You are solely responsible for your actions. "
            "The author is not liable for any damage. \n"
        )
        self.print_to_terminal(welcome_message, tag="header")

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
            width=55,
            height=total_height,  # Set the total height
            highlightthickness=0,  # Set highlightthickness to 0 to remove the border
        )
        self.text_widget.pack(expand=True, fill="both", pady=(0, 20))
        self.text_widget.tag_config("header", foreground="yellow")
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
            "exitrec": self.gui.exit_recovery_mode,
            "ufile": self.gui.upload_file,
            "2wayshell": self.gui.two_way_shell,
            "sincomm": self.gui.single_command,
            "excomm": self.gui.exploit_command,
            "applesupport": self.gui.apple_support,
            "usbres": self.gui.usb_reset,
            "batscript": self.gui.batch_scripting,
            "rawcomm": self.gui.raw_commands,
            "rchelp": self.gui.irecovery_help,
        }

    def input_prompt(self):
     current_folder_name = os.path.basename(self.current_folder)
     prompt_text = f"\n[{current_folder_name}] > "
     self.text_widget.insert(tk.END, prompt_text, "input_prompt")
     self.text_widget.tag_configure("input_prompt", foreground="#00FF00")  # Set color for the input prompt
     self.text_widget.see(tk.END)
     self.text_widget.bind("<Return>", self.process_user_input)
     # Set the focus on the text widget
     self.text_widget.focus_set()


    def process_user_input(self, event):
     user_input = self.text_widget.get("end-2l lineend", tk.END).strip()

     # Handle backspace key press
     if not user_input:
         self.handle_backspace(event)
         return

     self.text_widget.delete("end-1l linestart", tk.END)  # Remove input prompt
     self.execute_command(user_input)
     self.input_prompt()


    def handle_backspace(self, event):
     # Get the current cursor position
     current_position = self.text_widget.index(tk.INSERT)

     # Get the start position of user input (end of the previous line)
     user_input_start = self.text_widget.index("end-2l lineend +1c")

     # If the cursor is before the user input, do nothing
     if current_position < user_input_start:
         return "break"
 
     # If there is user input, delete the character before the cursor
     if current_position > user_input_start:
         self.text_widget.delete(current_position + "1c", current_position)

     return "break"


    def execute_command(self, user_input):
     command_parts = user_input.split()
     command_name = command_parts[0]

     if command_name in self.commands:
         self.commands[command_name](command_parts[1:])
     else:
         self.print_to_terminal(f"Command not found: {command_name}\nRun -list for available commands", tag="output")


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
         "2wayshell": "Start a two-way shell",
         "sincomm": "Execute a single command",
         "excomm": "Exploit a command",
         "applesupport": "Apple devices developer details",
         "usbres": "Reset USB connection",
         "batscript": "Execute batch scripting",
         "rawcomm": "Execute raw commands",
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
            terminal_width = os.get_terminal_size().columns

            colored_items = []

            for item in contents:
                full_path = os.path.join(folder, item)
                if os.path.isdir(full_path):
                    colored_items.append(f"\033[1;34m{item}\033[0m  ")  # Blue color for directories
                else:
                    colored_items.append(f"{item}  ")

            formatted_items = "".join(colored_items)
            lines = self.wrap_text(formatted_items, terminal_width)

            for line in lines:
                self.print_to_terminal(line.rstrip())

        except FileNotFoundError:
            self.print_to_terminal(f"Directory not found: {folder}", tag="output")

    def wrap_text(self, text, width):
        lines = []
        current_line = ""

        for word in text.split():
            if len(current_line) + len(word) <= width:
                current_line += word + " "
            else:
                lines.append(current_line)
                current_line = word + " "

        if current_line:
            lines.append(current_line)

        return lines
        
        
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
    root = tk.Tk()
    app = GuiApp(root)
    root.mainloop()
