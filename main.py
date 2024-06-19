import pyautogui
import threading
import tkinter as tk
from tkinter import messagebox
import sys
import os
import keyboard

class AutoClicker:
    def __init__(self, master):
        """
        Initialize the AutoClicker application.

        Args:
        - master (tk.Tk): The root Tkinter window.
        """
        self.master = master
        self.master.title("Auto Clicker")  # Set the title of the window

        # Determine the path to the icon
        if hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, 'assets/logo.ico')
        else:
            icon_path = './assets/logo.ico'

        self.master.iconbitmap(icon_path)  # Set the window icon

        # Initialize variables for interval configuration
        self.interval_minutes = tk.IntVar(value=0)
        self.interval_seconds = tk.IntVar(value=10)
        self.interval_milliseconds = tk.IntVar(value=100)
        self.running = False  # Flag to indicate if autoclicking is running or not

        # Frame to organize related controls
        control_frame = tk.LabelFrame(master, text="Interval Configuration")
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")  # Expand frame horizontally

        # Labels and input fields for minutes, seconds, and milliseconds
        tk.Label(control_frame, text="Minutes:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        tk.Entry(control_frame, textvariable=self.interval_minutes, width=5).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(control_frame, text="Seconds:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        tk.Entry(control_frame, textvariable=self.interval_seconds, width=5).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        tk.Label(control_frame, text="Milliseconds:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.E)
        tk.Entry(control_frame, textvariable=self.interval_milliseconds, width=5).grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)

        # Start and Stop buttons
        button_frame = tk.Frame(master)
        button_frame.grid(row=1, column=0, pady=10)

        self.start_button = tk.Button(button_frame, text="Start (F8)", command=self.start_clicking)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = tk.Button(button_frame, text="Stop (F8)", state="disabled", command=self.stop_clicking)
        self.stop_button.grid(row=0, column=1, padx=5)

        # Window resizing configuration
        master.grid_rowconfigure(0, weight=1)  # Row 0 will expand vertically
        master.grid_columnconfigure(0, weight=1)  # Column 0 will expand horizontally

        # Register F8 key globally
        keyboard.on_press_key("f8", self.toggle_clicking)

    def start_clicking(self):
        """
        Start the autoclicking process.

        Raises:
        - ValueError: If the total interval is zero or negative.
        """
        if not self.running:
            try:
                minutes = self.interval_minutes.get()
                seconds = self.interval_seconds.get()
                milliseconds = self.interval_milliseconds.get()

                total_interval = (minutes * 60 + seconds) * 1000 + milliseconds

                if total_interval <= 0:
                    raise ValueError("The interval must be greater than zero.")

                self.running = True
                self.start_button.config(state="disabled")
                self.stop_button.config(state="normal")
                self.click_thread = threading.Thread(target=self.click_mouse, args=(total_interval,))
                self.click_thread.start()
            except ValueError as e:
                messagebox.showerror("Error: Interval not valid", str(e))

    def click_mouse(self, interval):
        """
        Perform the mouse click action repeatedly with a given interval.

        Args:
        - interval (float): The interval between clicks in milliseconds.
        """
        while self.running:
            pyautogui.click()
            pyautogui.sleep(interval / 1000.0)

    def stop_clicking(self):
        """
        Stop the autoclicking process.
        """
        if self.running:
            self.running = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")

    def toggle_clicking(self, event=None):
        """
        Toggle between starting and stopping the autoclicking process.
        """
        if self.running:
            self.stop_clicking()
        else:
            self.start_clicking()

# Main function to start the application
def main():
    """
    Main function to create and run the Tkinter application.
    """
    root = tk.Tk()
    root.title("Auto Clicker")
    app = AutoClicker(root)
    root.mainloop()

if __name__ == "__main__":
    main()