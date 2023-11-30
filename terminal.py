import tkinter as tk
from PIL import Image, ImageTk
from pyfiglet import Figlet
import os


class CustomTerminal:
    def __init__(self, master):
        self.master = master
        master.title("Custom Terminal")
        master.geometry("800x600")
        master.configure(bg="black")

        self.setup_text_widget()
        self.setup_commands()

        self.current_folder = "[iVanced]-[~]"  # Initial folder set to home

        # Add the Figlet header with the new ASCII art and horizontal line
        figlet_header = self.generate_figlet_header("iShell", font="small")
        self.print_to_terminal(figlet_header, tag="header")

        # Add a welcome message and disclaimer with text wrapping
        welcome_message = (
            " ----------- Your Interactive Shell ------------------\n"
            "This tool is for educational and testing purposes only. "
            "Usage for malicious or illegal activities is prohibited. "
            "You are solely responsible for your actions. "
            "The author is not liable for any damage. \n\n"
        )
        self.print_to_terminal(welcome_message, tag="header")

        self.input_prompt()
        self.text_widget.bind("<BackSpace>", self.handle_backspace)


    def setup_text_widget(self):
        self.text_widget = tk.Text(self.master, wrap=tk.WORD, font=("Courier", 12), bg="black", fg="white")
        self.text_widget.pack(expand=True, fill="both")

    def setup_commands(self):
        self.commands = {
            "pwd": self.show_current_folder,
            "ls": self.list_commands,
            "cd": self.change_directory
            # Add other commands as needed
        }

    def input_prompt(self):
     current_folder_name = os.path.basename(self.current_folder)
     prompt_text = f"\n{current_folder_name} > "
     self.text_widget.insert(tk.END, prompt_text, "input_prompt")
     self.text_widget.tag_configure("input_prompt", foreground="#00FF00")  # Set color for the input prompt
     self.text_widget.see(tk.END)
     self.text_widget.bind("<Return>", self.process_user_input)


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
        command_parts = user_input.split(" ")
        command_name = command_parts[0]

        if command_name in self.commands:
            self.commands[command_name](command_parts[1:])
        else:
            self.print_to_terminal(f" {command_name}\nCommand not found:", tag="output")
            self.list_commands([])  # Display available commands

    def show_current_folder(self, args):
     command_output = self.current_folder
     self.print_to_terminal("pwd", command_output, tag="output")

    def list_commands(self, args):
     available_commands = ", ".join(self.commands.keys())
     self.print_to_terminal("ls", f"Available commands: {available_commands}", tag="output")

    def change_directory(self, args):
        if not args:
            self.print_to_terminal("Usage: cd [folder]", tag="output")
            return

        new_folder = args[0]

        if new_folder in ["home", "script", "ramdisk", "device"]:
            self.current_folder = os.path.join("/", new_folder)
            self.input_prompt()
            self.print_to_terminal(f"Changed directory to: {self.current_folder}", tag="output")
        else:
            self.print_to_terminal("Invalid folder", tag="output")

    def print_to_terminal(self, command_name, message="", tag="output"):
     if message:
         self.text_widget.insert(tk.END, f"{command_name}\n{message}\n", tag)
     else:
         self.text_widget.insert(tk.END, f"{command_name}\n", tag)



    def generate_figlet_header(self, text, font="Courier New"):
        figlet = Figlet(font=font)
        return figlet.renderText(text)

if __name__ == "__main__":
    root = tk.Tk()
    terminal = CustomTerminal(root)
    root.mainloop()