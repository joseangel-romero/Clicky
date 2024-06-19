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

        # Frame to organize related controls - Interval Configuration
        control_frame = tk.LabelFrame(master, text="Interval Configuration")
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")  # Expand frame horizontally

        tk.Label(control_frame, text="Minutes:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        tk.Entry(control_frame, textvariable=self.interval_minutes, width=5).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(control_frame, text="Seconds:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        tk.Entry(control_frame, textvariable=self.interval_seconds, width=5).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        tk.Label(control_frame, text="Milliseconds:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.E)
        tk.Entry(control_frame, textvariable=self.interval_milliseconds, width=5).grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)

        # Frame for Click Options
        click_options_frame = tk.LabelFrame(master, text="Click Options")
        click_options_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # Variables for click options
        self.click_type = tk.StringVar(value="Single")
        self.click_button = tk.StringVar(value="Left")

        # Drop-downs for click options
        tk.Label(click_options_frame, text="Click Type:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        click_type_dropdown = tk.OptionMenu(click_options_frame, self.click_type, "Single", "Double")
        click_type_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(click_options_frame, text="Click Button:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        click_button_dropdown = tk.OptionMenu(click_options_frame, self.click_button, "Left", "Right")
        click_button_dropdown.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        # Frame for Click Repeat Options
        repeat_frame = tk.LabelFrame(master, text="Click Repeat")
        repeat_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.repeat_enabled = tk.BooleanVar(value=False)
        self.repeat_count = tk.IntVar(value=10)

        repeat_check = tk.Checkbutton(repeat_frame, text="Enable Click Repeat", variable=self.repeat_enabled, command=self.toggle_repeat)
        repeat_check.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        tk.Label(repeat_frame, text="Click Count:").grid(row=0, column=1, padx=5, pady=5, sticky=tk.E)
        self.click_count_entry = tk.Entry(repeat_frame, textvariable=self.repeat_count, width=5)
        self.click_count_entry.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)

        # Frame for Cursor Position Options
        cursor_frame = tk.LabelFrame(master, text="Cursor Position")
        cursor_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        self.cursor_position = tk.StringVar(value="current")
        self.cursor_x = tk.IntVar(value=0)
        self.cursor_y = tk.IntVar(value=0)

        tk.Radiobutton(cursor_frame, text="Current location", variable=self.cursor_position, value="current").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        pick_button = tk.Radiobutton(cursor_frame, text="Pick location", variable=self.cursor_position, value="pick")
        pick_button.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        pick_button.config(command=self.pick_location)

        tk.Label(cursor_frame, text="X").grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        self.cursor_x_entry = tk.Entry(cursor_frame, textvariable=self.cursor_x, width=5)
        self.cursor_x_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        tk.Label(cursor_frame, text="Y").grid(row=0, column=4, padx=5, pady=5, sticky=tk.E)
        self.cursor_y_entry = tk.Entry(cursor_frame, textvariable=self.cursor_y, width=5)
        self.cursor_y_entry.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)

        # Start and Stop buttons
        button_frame = tk.Frame(master)
        button_frame.grid(row=4, column=0, pady=10)

        self.start_button = tk.Button(button_frame, text="Start (F8)", command=self.start_clicking)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = tk.Button(button_frame, text="Stop (F8)", state="disabled", command=self.stop_clicking)
        self.stop_button.grid(row=0, column=1, padx=5)

        # Window resizing configuration
        master.grid_rowconfigure(0, weight=1)  # Row 0 will expand vertically
        master.grid_columnconfigure(0, weight=1)  # Column 0 will expand horizontally

        # Register F8 key globally
        keyboard.on_press_key("f8", self.toggle_clicking)

        # Initialize the repeat toggle state
        self.toggle_repeat()

    def toggle_repeat(self):
        """
        Toggle the repeat settings based on user input.
        """
        if self.repeat_enabled.get():
            self.click_count_entry.config(state='normal')
        else:
            self.click_count_entry.config(state='disabled')

    def pick_location(self):
        """
        Enable the user to pick a location on the screen.
        """
        self.master.withdraw()
        messagebox.showinfo("Pick Location", "Move your mouse to the desired location and press 'P'.")
        keyboard.wait('p')
        x, y = pyautogui.position()
        self.cursor_x.set(x)
        self.cursor_y.set(y)
        self.master.deiconify()

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
        if self.repeat_enabled.get():
            repeat_count = self.repeat_count.get()
            for _ in range(repeat_count):
                if self.running:
                    self.perform_click_action()
                    pyautogui.sleep(interval / 1000.0)
                else:
                    break
            self.stop_clicking()
        else:
            while self.running:
                self.perform_click_action()
                pyautogui.sleep(interval / 1000.0)

    def perform_click_action(self):
        """
        Perform the appropriate click action based on user settings.
        """
        if self.cursor_position.get() == "pick":
            x, y = self.cursor_x.get(), self.cursor_y.get()
            pyautogui.moveTo(x, y)

        if self.click_type.get() == "Single":
            button = self.click_button.get().lower()
            if button == "left":
                pyautogui.click(button='left')
            elif button == "right":
                pyautogui.click(button='right')
        elif self.click_type.get() == "Double":
            button = self.click_button.get().lower()
            if button == "left":
                pyautogui.doubleClick(button='left')
            elif button == "right":
                pyautogui.doubleClick(button='right')

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
