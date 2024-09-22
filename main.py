import pyautogui
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
import sys
import os
import keyboard
import ttkbootstrap as ttk
from ttkbootstrap.tooltip import ToolTip
import json
import random

class AutoClicker:
    def __init__(self, master):
        """
        Initializes the AutoClicker application.
        """
        self.master = master
        self.master.title("Auto Clicker")
        self.master.resizable(False, False)  # Makes the window non-resizable

        # Attempt to set the window icon
        try:
            if hasattr(sys, '_MEIPASS'):
                icon_path = os.path.join(sys._MEIPASS, 'assets/logo.ico')
            else:
                icon_path = './assets/logo.ico'
            self.master.iconbitmap(icon_path)
        except:
            pass  # Ignore if the icon is not found

        # Configuration variables
        self.interval_minutes = tk.IntVar(value=0)
        self.interval_seconds = tk.IntVar(value=0)
        self.interval_milliseconds = tk.IntVar(value=100)
        self.randomize_interval = tk.BooleanVar(value=False)
        self.random_range = tk.IntVar(value=0)
        self.running = False

        # Additional variables
        self.countdown_seconds = tk.IntVar(value=3)
        self.start_hotkey = tk.StringVar(value="F8")
        self.stop_hotkey = tk.StringVar(value="F9")  # Changed from "F8" to "F9"

        # Initialize the list of hotkey handlers
        self.hotkey_handlers = []

        # Interface setup
        self.setup_interface()

        # Register hotkeys
        self.register_hotkeys()

        # Initialize toggle states
        self.toggle_repeat()
        self.toggle_randomize()

    def setup_interface(self):
        """
        Sets up the graphical user interface elements.
        """
        # Interval configuration frame
        control_frame = ttk.LabelFrame(self.master, text="Interval Configuration")
        control_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(control_frame, text="Minutes:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        ttk.Entry(control_frame, textvariable=self.interval_minutes, width=5).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(control_frame, text="Seconds:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        ttk.Entry(control_frame, textvariable=self.interval_seconds, width=5).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        ttk.Label(control_frame, text="Milliseconds:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.E)
        ttk.Entry(control_frame, textvariable=self.interval_milliseconds, width=5).grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)

        # Randomize interval
        self.randomize_check = ttk.Checkbutton(control_frame, text="Randomize Interval", variable=self.randomize_interval, command=self.toggle_randomize)
        self.randomize_check.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W, columnspan=2)
        ToolTip(self.randomize_check, text="Randomizes the interval between clicks within a specified range.")

        ttk.Label(control_frame, text="Random Range (ms):").grid(row=1, column=2, padx=5, pady=5, sticky=tk.E)
        self.random_range_entry = ttk.Entry(control_frame, textvariable=self.random_range, width=5, state='disabled')
        self.random_range_entry.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)
        ToolTip(self.random_range_entry, text="Specifies the maximum random variation in milliseconds.")

        # Click options frame
        click_options_frame = ttk.LabelFrame(self.master, text="Click Options")
        click_options_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.click_type = tk.StringVar(value="Single")
        self.click_button = tk.StringVar(value="Left")

        ttk.Label(click_options_frame, text="Click Type:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        click_type_dropdown = ttk.Combobox(click_options_frame, textvariable=self.click_type, values=["Single", "Double"], state='readonly')
        click_type_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        ToolTip(click_type_dropdown, text="Select between single or double click.")

        ttk.Label(click_options_frame, text="Click Button:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        click_button_dropdown = ttk.Combobox(click_options_frame, textvariable=self.click_button, values=["Left", "Right"], state='readonly')
        click_button_dropdown.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        ToolTip(click_button_dropdown, text="Select the mouse button to click.")

        # Click repetition frame
        repeat_frame = ttk.LabelFrame(self.master, text="Click Repetition")
        repeat_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.repeat_enabled = tk.BooleanVar(value=False)
        self.repeat_count = tk.IntVar(value=10)

        repeat_check = ttk.Checkbutton(repeat_frame, text="Enable Click Repetition", variable=self.repeat_enabled, command=self.toggle_repeat)
        repeat_check.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W, columnspan=2)
        ToolTip(repeat_check, text="Enable to repeat the click a specific number of times.")

        ttk.Label(repeat_frame, text="Number of Clicks:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        self.click_count_entry = ttk.Entry(repeat_frame, textvariable=self.repeat_count, width=5, state='disabled')
        self.click_count_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        ToolTip(self.click_count_entry, text="Specifies how many times to repeat the click.")

        # Cursor position frame
        cursor_frame = ttk.LabelFrame(self.master, text="Cursor Position")
        cursor_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        self.cursor_position = tk.StringVar(value="current")
        self.cursor_x = tk.IntVar(value=0)
        self.cursor_y = tk.IntVar(value=0)

        current_radio = ttk.Radiobutton(cursor_frame, text="Current Position", variable=self.cursor_position, value="current")
        current_radio.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ToolTip(current_radio, text="Clicks at the current cursor position.")

        pick_button = ttk.Radiobutton(cursor_frame, text="Select Position", variable=self.cursor_position, value="pick", command=self.pick_location)
        pick_button.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        ToolTip(pick_button, text="Select a specific position on the screen to click.")

        ttk.Label(cursor_frame, text="X:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        self.cursor_x_entry = ttk.Entry(cursor_frame, textvariable=self.cursor_x, width=5)
        self.cursor_x_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        ToolTip(self.cursor_x_entry, text="X coordinate for the click position.")

        ttk.Label(cursor_frame, text="Y:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.E)
        self.cursor_y_entry = ttk.Entry(cursor_frame, textvariable=self.cursor_y, width=5)
        self.cursor_y_entry.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
        ToolTip(self.cursor_y_entry, text="Y coordinate for the click position.")

        # Hotkey configuration frame
        hotkey_frame = ttk.LabelFrame(self.master, text="Hotkey Configuration")
        hotkey_frame.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(hotkey_frame, text="Start Hotkey:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.start_hotkey_entry = ttk.Entry(hotkey_frame, textvariable=self.start_hotkey, width=10)
        self.start_hotkey_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        ToolTip(self.start_hotkey_entry, text="Sets the hotkey to start the autoclicker.")

        ttk.Label(hotkey_frame, text="Stop Hotkey:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        self.stop_hotkey_entry = ttk.Entry(hotkey_frame, textvariable=self.stop_hotkey, width=10)
        self.stop_hotkey_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        ToolTip(self.stop_hotkey_entry, text="Sets the hotkey to stop the autoclicker.")

        # Buttons to save/load configurations
        settings_frame = ttk.Frame(self.master)
        settings_frame.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

        save_button = ttk.Button(settings_frame, text="Save Configuration", command=self.save_settings, bootstyle="info-outline")
        save_button.grid(row=0, column=0, padx=5, pady=5)
        ToolTip(save_button, text="Saves the current configuration to a file.")

        load_button = ttk.Button(settings_frame, text="Load Configuration", command=self.load_settings, bootstyle="info-outline")
        load_button.grid(row=0, column=1, padx=5, pady=5)
        ToolTip(load_button, text="Loads the configuration from a file.")

        # Start and stop buttons
        button_frame = ttk.Frame(self.master)
        button_frame.grid(row=6, column=0, pady=5)

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_clicking, bootstyle="success-outline")
        self.start_button.grid(row=0, column=0, padx=5)
        ToolTip(self.start_button, text="Starts the autoclicker.")

        self.stop_button = ttk.Button(button_frame, text="Stop", state="disabled", command=self.stop_clicking, bootstyle="danger-outline")
        self.stop_button.grid(row=0, column=1, padx=5)
        ToolTip(self.stop_button, text="Stops the autoclicker.")

        # Status bar
        self.status_label = ttk.Label(self.master, text="Status: Inactive", anchor='w')
        self.status_label.grid(row=7, column=0, padx=10, pady=5, sticky='ew')

        # Window resizing configuration
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

    def toggle_repeat(self):
        """
        Toggles the repetition configuration based on user input.
        """
        if self.repeat_enabled.get():
            self.click_count_entry.config(state='normal')
        else:
            self.click_count_entry.config(state='disabled')

    def toggle_randomize(self):
        """
        Toggles the random interval input based on user input.
        """
        if self.randomize_interval.get():
            self.random_range_entry.config(state='normal')
        else:
            self.random_range_entry.config(state='disabled')

    def pick_location(self):
        """
        Allows the user to select a location on the screen by clicking.
        """
        # Hide the main window
        self.master.withdraw()
        messagebox.showinfo("Select Position", "Move the mouse to the desired position and click to select it.")

        # Create a full-screen transparent window
        self.capture_window = tk.Toplevel()
        self.capture_window.attributes('-fullscreen', True)
        self.capture_window.attributes('-alpha', 0.01)  # Make it almost transparent
        self.capture_window.attributes('-topmost', True)
        self.capture_window.bind('<Button-1>', self.get_click_position)

    def get_click_position(self, event):
        """
        Gets the click position and stores it.
        """
        x, y = event.x_root, event.y_root
        self.cursor_x.set(x)
        self.cursor_y.set(y)
        self.capture_window.destroy()
        self.master.deiconify()

    def start_clicking(self):
        """
        Starts the autoclicking process.
        """
        if not self.running:
            try:
                minutes = self.interval_minutes.get()
                seconds = self.interval_seconds.get()
                milliseconds = self.interval_milliseconds.get()

                total_interval = (minutes * 60 + seconds) * 1000 + milliseconds

                if total_interval <= 0:
                    raise ValueError("The interval must be greater than zero.")

                if self.randomize_interval.get():
                    random_range = self.random_range.get()
                    if random_range < 0 or random_range > total_interval:
                        raise ValueError("The random range must be between 0 and the total interval.")

                self.running = True
                self.start_button.config(state="disabled")
                self.stop_button.config(state="normal")
                self.status_label.config(text="Status: Running")

                # Countdown before starting
                countdown = self.countdown_seconds.get()
                if countdown > 0:
                    for i in range(countdown, 0, -1):
                        self.status_label.config(text=f"Starting in {i}...")
                        self.master.update()
                        pyautogui.sleep(1)

                self.status_label.config(text="Status: Running")
                self.click_thread = threading.Thread(target=self.click_mouse, args=(total_interval,), daemon=True)
                self.click_thread.start()
            except ValueError as e:
                messagebox.showerror("Error: Invalid Interval", str(e))

    def click_mouse(self, interval):
        """
        Performs the click action repeatedly with a given interval.
        """
        if self.repeat_enabled.get():
            repeat_count = self.repeat_count.get()
            for _ in range(repeat_count):
                if self.running:
                    self.perform_click_action()
                    actual_interval = interval
                    if self.randomize_interval.get():
                        variation = random.randint(0, self.random_range.get())
                        actual_interval += variation
                    pyautogui.sleep(actual_interval / 1000.0)
                else:
                    break
            self.stop_clicking()
        else:
            while self.running:
                self.perform_click_action()
                actual_interval = interval
                if self.randomize_interval.get():
                    variation = random.randint(0, self.random_range.get())
                    actual_interval += variation
                pyautogui.sleep(actual_interval / 1000.0)

    def perform_click_action(self):
        """
        Performs the appropriate click action based on user configuration.
        """
        if self.cursor_position.get() == "pick":
            x, y = self.cursor_x.get(), self.cursor_y.get()
            pyautogui.moveTo(x, y)

        button = self.click_button.get().lower()
        if self.click_type.get() == "Single":
            pyautogui.click(button=button)
        elif self.click_type.get() == "Double":
            pyautogui.doubleClick(button=button)

    def stop_clicking(self):
        """
        Stops the autoclicking process.
        """
        if self.running:
            self.running = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.status_label.config(text="Status: Inactive")

    def toggle_clicking(self, event=None):
        """
        Toggles between starting and stopping the autoclicking process.
        """
        if self.running:
            self.stop_clicking()
        else:
            self.start_clicking()

    def register_hotkeys(self):
        """
        Registers the start and stop hotkeys.
        """
        # Unbind previous hotkeys
        for handler in self.hotkey_handlers:
            keyboard.remove_hotkey(handler)
        self.hotkey_handlers.clear()

        # Validate that the hotkeys are not the same
        if self.start_hotkey.get() == self.stop_hotkey.get():
            messagebox.showerror("Hotkey Error", "Start and stop hotkeys cannot be the same.")
            return

        # Register new hotkeys
        start_hotkey = self.start_hotkey.get()
        stop_hotkey = self.stop_hotkey.get()
        try:
            start_handler = keyboard.add_hotkey(start_hotkey, self.start_clicking)
            self.hotkey_handlers.append(start_handler)
        except Exception as e:
            messagebox.showerror("Hotkey Error", f"Could not register the start hotkey ({start_hotkey}):\n{e}")

        try:
            stop_handler = keyboard.add_hotkey(stop_hotkey, self.stop_clicking)
            self.hotkey_handlers.append(stop_handler)
        except Exception as e:
            messagebox.showerror("Hotkey Error", f"Could not register the stop hotkey ({stop_hotkey}):\n{e}")

    def save_settings(self):
        """
        Saves the current configuration to a file selected by the user.
        """
        # Validate that the hotkeys are not the same before saving
        if self.start_hotkey.get() == self.stop_hotkey.get():
            messagebox.showerror("Hotkey Error", "Cannot save the configuration because the start and stop hotkeys are the same.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON Files", "*.json")],
                                                 title="Save Configuration")
        if file_path:
            settings = {
                "interval_minutes": self.interval_minutes.get(),
                "interval_seconds": self.interval_seconds.get(),
                "interval_milliseconds": self.interval_milliseconds.get(),
                "randomize_interval": self.randomize_interval.get(),
                "random_range": self.random_range.get(),
                "click_type": self.click_type.get(),
                "click_button": self.click_button.get(),
                "repeat_enabled": self.repeat_enabled.get(),
                "repeat_count": self.repeat_count.get(),
                "cursor_position": self.cursor_position.get(),
                "cursor_x": self.cursor_x.get(),
                "cursor_y": self.cursor_y.get(),
                "start_hotkey": self.start_hotkey.get(),
                "stop_hotkey": self.stop_hotkey.get(),
                "countdown_seconds": self.countdown_seconds.get()
            }
            try:
                with open(file_path, "w") as f:
                    json.dump(settings, f, indent=4)
                messagebox.showinfo("Configuration Saved", "Your settings have been successfully saved.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save the configuration:\n{e}")

    def load_settings(self):
        """
        Loads the configuration from a file selected by the user.
        """
        file_path = filedialog.askopenfilename(defaultextension=".json",
                                               filetypes=[("JSON Files", "*.json")],
                                               title="Load Configuration")
        if file_path:
            try:
                with open(file_path, "r") as f:
                    settings = json.load(f)
                self.interval_minutes.set(settings.get("interval_minutes", 0))
                self.interval_seconds.set(settings.get("interval_seconds", 0))
                self.interval_milliseconds.set(settings.get("interval_milliseconds", 100))
                self.randomize_interval.set(settings.get("randomize_interval", False))
                self.random_range.set(settings.get("random_range", 0))
                self.click_type.set(settings.get("click_type", "Single"))
                self.click_button.set(settings.get("click_button", "Left"))
                self.repeat_enabled.set(settings.get("repeat_enabled", False))
                self.repeat_count.set(settings.get("repeat_count", 10))
                self.cursor_position.set(settings.get("cursor_position", "current"))
                self.cursor_x.set(settings.get("cursor_x", 0))
                self.cursor_y.set(settings.get("cursor_y", 0))
                self.start_hotkey.set(settings.get("start_hotkey", "F8"))
                self.stop_hotkey.set(settings.get("stop_hotkey", "F9"))  # Changed default to "F9"
                self.countdown_seconds.set(settings.get("countdown_seconds", 3))

                # Re-register the hotkeys
                self.register_hotkeys()

                # Update interface elements
                self.toggle_repeat()
                self.toggle_randomize()

                messagebox.showinfo("Configuration Loaded", "Your settings have been successfully loaded.")
            except FileNotFoundError:
                messagebox.showerror("Error", "Configuration file not found.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while loading the configuration:\n{e}")

# Main function to start the application
def main():
    """
    Main function to create and run the Tkinter application.
    """
    # Use a window with ttkbootstrap theme
    root = ttk.Window(themename="superhero")
    root.title("Auto Clicker")
    app = AutoClicker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
