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
        Initializes the AutoClicker application with language support.
        """
        self.master = master
        self.current_language = 'en'  # Default language

        # Load translations from dictionary.json
        self.translations = self.load_translations()

        self.master.title(self.translations[self.current_language]['title'])
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
        self.interval_minutes = tk.StringVar(value='0')
        self.interval_seconds = tk.StringVar(value='0')
        self.interval_milliseconds = tk.StringVar(value='100')
        self.randomize_interval = tk.BooleanVar(value=False)
        self.random_range = tk.StringVar(value='0')
        self.running = False

        # Additional variables
        # Removed countdown_seconds as per user request

        self.start_hotkey = tk.StringVar(value="F8")
        self.stop_hotkey = tk.StringVar(value="F9")  # Changed from "F8" to "F9"

        # Initialize the list of hotkey handlers
        self.hotkey_handlers = []

        # Initialize UI elements references for dynamic updates
        self.ui_elements = {}

        # Interface setup
        self.setup_interface()

        # Register hotkeys
        self.register_hotkeys()

        # Initialize toggle states
        self.toggle_repeat()
        self.toggle_randomize()

    def load_translations(self):
        """
        Loads translations from the dictionary.json file.
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dictionary_path = os.path.join(script_dir, 'dictionary.json')
        try:
            with open(dictionary_path, 'r', encoding='utf-8') as f:
                translations = json.load(f)
            return translations
        except FileNotFoundError:
            messagebox.showerror("Error", f"Translation file not found at {dictionary_path}.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Error decoding JSON from {dictionary_path}:\n{e}")
            sys.exit(1)
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while loading translations:\n{e}")
            sys.exit(1)

    def setup_interface(self):
        """
        Sets up the graphical user interface elements with language support.
        """
        lang = self.current_language
        # Language selection frame
        language_frame = ttk.LabelFrame(self.master, text="Language")
        language_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.ui_elements['language_frame'] = language_frame

        self.language_var = tk.StringVar(value=self.current_language)
        en_radio = ttk.Radiobutton(language_frame, text="English", variable=self.language_var, value='en', command=self.change_language)
        es_radio = ttk.Radiobutton(language_frame, text="Español", variable=self.language_var, value='es', command=self.change_language)
        en_radio.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        es_radio.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.ui_elements['radio_en'] = en_radio
        self.ui_elements['radio_es'] = es_radio

        # Frame of interval configuration
        control_frame = ttk.LabelFrame(self.master, text=self.translations[lang]['interval_config'])
        control_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.ui_elements['control_frame'] = control_frame

        # Minutes
        self.ui_elements['label_minutes'] = ttk.Label(control_frame, text=self.translations[lang]['minutes'])
        self.ui_elements['label_minutes'].grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        vcmd = (self.master.register(self.validate_integer), '%P')
        self.ui_elements['entry_minutes'] = ttk.Entry(control_frame, textvariable=self.interval_minutes, width=5, validate='key', validatecommand=vcmd)
        self.ui_elements['entry_minutes'].grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Seconds
        self.ui_elements['label_seconds'] = ttk.Label(control_frame, text=self.translations[lang]['seconds'])
        self.ui_elements['label_seconds'].grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        self.ui_elements['entry_seconds'] = ttk.Entry(control_frame, textvariable=self.interval_seconds, width=5, validate='key', validatecommand=vcmd)
        self.ui_elements['entry_seconds'].grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        # Milliseconds
        self.ui_elements['label_milliseconds'] = ttk.Label(control_frame, text=self.translations[lang]['milliseconds'])
        self.ui_elements['label_milliseconds'].grid(row=0, column=4, padx=5, pady=5, sticky=tk.E)
        self.ui_elements['entry_milliseconds'] = ttk.Entry(control_frame, textvariable=self.interval_milliseconds, width=5, validate='key', validatecommand=vcmd)
        self.ui_elements['entry_milliseconds'].grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)

        # Randomize interval
        self.randomize_check = ttk.Checkbutton(control_frame, text=self.translations[lang]['randomize_interval'], variable=self.randomize_interval, command=self.toggle_randomize)
        self.randomize_check.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W, columnspan=2)
        ToolTip(self.randomize_check, text=self.translations[lang]['tooltip_randomize_interval'])
        self.ui_elements['randomize_check'] = self.randomize_check

        # Random Range
        self.ui_elements['label_random_range'] = ttk.Label(control_frame, text=self.translations[lang]['random_range'])
        self.ui_elements['label_random_range'].grid(row=1, column=2, padx=5, pady=5, sticky=tk.E)
        self.random_range_entry = ttk.Entry(control_frame, textvariable=self.random_range, width=5, state='disabled', validate='key', validatecommand=vcmd)
        self.random_range_entry.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)
        ToolTip(self.random_range_entry, text=self.translations[lang]['tooltip_random_range'])
        self.ui_elements['random_range_entry'] = self.random_range_entry

        # Frame of click options
        click_options_frame = ttk.LabelFrame(self.master, text=self.translations[lang]['click_options'])
        click_options_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.ui_elements['click_options_frame'] = click_options_frame

        self.click_type = tk.StringVar(value=self.translations[lang]['single'])
        self.click_button = tk.StringVar(value=self.translations[lang]['left'])

        # Click Type
        self.ui_elements['label_click_type'] = ttk.Label(click_options_frame, text=self.translations[lang]['click_type'])
        self.ui_elements['label_click_type'].grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        click_type_dropdown = ttk.Combobox(click_options_frame, textvariable=self.click_type, values=[self.translations[lang]['single'], self.translations[lang]['double']], state='readonly')
        click_type_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        ToolTip(click_type_dropdown, text=self.translations[lang]['tooltip_click_type'])
        self.ui_elements['dropdown_click_type'] = click_type_dropdown

        # Click Button
        self.ui_elements['label_click_button'] = ttk.Label(click_options_frame, text=self.translations[lang]['click_button'])
        self.ui_elements['label_click_button'].grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        click_button_dropdown = ttk.Combobox(click_options_frame, textvariable=self.click_button, values=[self.translations[lang]['left'], self.translations[lang]['right']], state='readonly')
        click_button_dropdown.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        ToolTip(click_button_dropdown, text=self.translations[lang]['tooltip_click_button'])
        self.ui_elements['dropdown_click_button'] = click_button_dropdown

        # Frame of click repetition
        repeat_frame = ttk.LabelFrame(self.master, text=self.translations[lang]['click_repetition'])
        repeat_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        self.ui_elements['repeat_frame'] = repeat_frame

        self.repeat_enabled = tk.BooleanVar(value=False)
        self.repeat_count = tk.StringVar(value='10')

        repeat_check = ttk.Checkbutton(repeat_frame, text=self.translations[lang]['enable_click_repetition'], variable=self.repeat_enabled, command=self.toggle_repeat)
        repeat_check.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W, columnspan=2)
        ToolTip(repeat_check, text=self.translations[lang]['tooltip_enable_click_repetition'])
        self.ui_elements['repeat_check'] = repeat_check

        # Number of Clicks
        self.ui_elements['label_number_of_clicks'] = ttk.Label(repeat_frame, text=self.translations[lang]['number_of_clicks'])
        self.ui_elements['label_number_of_clicks'].grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        self.click_count_entry = ttk.Entry(repeat_frame, textvariable=self.repeat_count, width=5, state='disabled', validate='key', validatecommand=vcmd)
        self.click_count_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        ToolTip(self.click_count_entry, text=self.translations[lang]['tooltip_number_of_clicks'])
        self.ui_elements['click_count_entry'] = self.click_count_entry

        # Frame of cursor position
        cursor_frame = ttk.LabelFrame(self.master, text=self.translations[lang]['cursor_position'])
        cursor_frame.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        self.ui_elements['cursor_frame'] = cursor_frame

        self.cursor_position = tk.StringVar(value="current")
        self.cursor_x = tk.StringVar(value='0')
        self.cursor_y = tk.StringVar(value='0')

        # Current Position Radio Button
        current_radio = ttk.Radiobutton(cursor_frame, text=self.translations[lang]['current_position'], variable=self.cursor_position, value="current")
        current_radio.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ToolTip(current_radio, text=self.translations[lang]['tooltip_current_position'])
        self.ui_elements['radio_current'] = current_radio

        # Select Position Radio Button
        pick_button = ttk.Radiobutton(cursor_frame, text=self.translations[lang]['select_position'], variable=self.cursor_position, value="pick", command=self.pick_location)
        pick_button.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        ToolTip(pick_button, text=self.translations[lang]['tooltip_select_position'])
        self.ui_elements['radio_pick'] = pick_button

        # X Coordinate
        self.ui_elements['label_x'] = ttk.Label(cursor_frame, text=self.translations[lang]['x'])
        self.ui_elements['label_x'].grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        self.cursor_x_entry = ttk.Entry(cursor_frame, textvariable=self.cursor_x, width=5, validate='key', validatecommand=vcmd)
        self.cursor_x_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        ToolTip(self.cursor_x_entry, text=self.translations[lang]['tooltip_x'])
        self.ui_elements['cursor_x_entry'] = self.cursor_x_entry

        # Y Coordinate
        self.ui_elements['label_y'] = ttk.Label(cursor_frame, text=self.translations[lang]['y'])
        self.ui_elements['label_y'].grid(row=0, column=4, padx=5, pady=5, sticky=tk.E)
        self.cursor_y_entry = ttk.Entry(cursor_frame, textvariable=self.cursor_y, width=5, validate='key', validatecommand=vcmd)
        self.cursor_y_entry.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
        ToolTip(self.cursor_y_entry, text=self.translations[lang]['tooltip_y'])
        self.ui_elements['cursor_y_entry'] = self.cursor_y_entry

        # Frame of hotkey configuration
        hotkey_frame = ttk.LabelFrame(self.master, text=self.translations[lang]['hotkey_config'])
        hotkey_frame.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        self.ui_elements['hotkey_frame'] = hotkey_frame

        # Start Hotkey
        self.ui_elements['label_start_hotkey'] = ttk.Label(hotkey_frame, text=self.translations[lang]['start_hotkey'])
        self.ui_elements['label_start_hotkey'].grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.start_hotkey_entry = ttk.Entry(hotkey_frame, textvariable=self.start_hotkey, width=10)
        self.start_hotkey_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        ToolTip(self.start_hotkey_entry, text=self.translations[lang]['save_config_message'])
        self.ui_elements['start_hotkey_entry'] = self.start_hotkey_entry

        # Stop Hotkey
        self.ui_elements['label_stop_hotkey'] = ttk.Label(hotkey_frame, text=self.translations[lang]['stop_hotkey'])
        self.ui_elements['label_stop_hotkey'].grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        self.stop_hotkey_entry = ttk.Entry(hotkey_frame, textvariable=self.stop_hotkey, width=10)
        self.stop_hotkey_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        ToolTip(self.stop_hotkey_entry, text=self.translations[lang]['save_config_message'])
        self.ui_elements['stop_hotkey_entry'] = self.stop_hotkey_entry

        # Buttons to save/load configurations
        settings_frame = ttk.Frame(self.master)
        settings_frame.grid(row=6, column=0, padx=10, pady=5, sticky="ew")
        self.ui_elements['settings_frame'] = settings_frame

        save_button = ttk.Button(settings_frame, text=self.translations[lang]['save_config'], command=self.save_settings, bootstyle="info-outline")
        save_button.grid(row=0, column=0, padx=5, pady=5)
        ToolTip(save_button, text=self.translations[lang]['save_config_message'])
        self.ui_elements['button_save'] = save_button

        load_button = ttk.Button(settings_frame, text=self.translations[lang]['load_config'], command=self.load_settings, bootstyle="info-outline")
        load_button.grid(row=0, column=1, padx=5, pady=5)
        ToolTip(load_button, text=self.translations[lang]['load_config_message'])
        self.ui_elements['button_load'] = load_button

        # Start and stop buttons
        button_frame = ttk.Frame(self.master)
        button_frame.grid(row=7, column=0, pady=5)
        self.ui_elements['button_frame'] = button_frame

        self.start_button = ttk.Button(button_frame, text=self.translations[lang]['start'], command=self.start_clicking, bootstyle="success-outline")
        self.start_button.grid(row=0, column=0, padx=5)
        ToolTip(self.start_button, text=self.translations[lang]['tooltip_start'])
        self.ui_elements['button_start'] = self.start_button

        self.stop_button = ttk.Button(button_frame, text=self.translations[lang]['stop'], state="disabled", command=self.stop_clicking, bootstyle="danger-outline")
        self.stop_button.grid(row=0, column=1, padx=5)
        ToolTip(self.stop_button, text=self.translations[lang]['tooltip_stop'])
        self.ui_elements['button_stop'] = self.stop_button

        # Status bar
        self.status_label = ttk.Label(self.master, text=self.translations[lang]['status_inactive'], anchor='w')
        self.status_label.grid(row=8, column=0, padx=10, pady=5, sticky='ew')
        self.ui_elements['status_label'] = self.status_label

        # Window resizing configuration
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

    def change_language(self):
        """
        Changes the application's language and updates the UI.
        """
        self.current_language = self.language_var.get()
        self.update_ui_language()

    def update_ui_language(self):
        """
        Updates all UI elements to match the selected language.
        """
        lang = self.current_language
        # Update window title
        self.master.title(self.translations[lang]['title'])

        # Update all labels and texts

        # Interval Configuration
        self.ui_elements['control_frame'].config(text=self.translations[lang]['interval_config'])
        self.ui_elements['label_minutes'].config(text=self.translations[lang]['minutes'])
        self.ui_elements['label_seconds'].config(text=self.translations[lang]['seconds'])
        self.ui_elements['label_milliseconds'].config(text=self.translations[lang]['milliseconds'])
        self.randomize_check.config(text=self.translations[lang]['randomize_interval'])
        self.ui_elements['label_random_range'].config(text=self.translations[lang]['random_range'])
        self.ui_elements['dropdown_click_type']['values'] = [self.translations[lang]['single'], self.translations[lang]['double']]
        self.ui_elements['dropdown_click_button']['values'] = [self.translations[lang]['left'], self.translations[lang]['right']]
        self.ui_elements['click_options_frame'].config(text=self.translations[lang]['click_options'])
        self.ui_elements['label_click_type'].config(text=self.translations[lang]['click_type'])
        self.ui_elements['label_click_button'].config(text=self.translations[lang]['click_button'])

        # Click Repetition
        self.ui_elements['repeat_frame'].config(text=self.translations[lang]['click_repetition'])
        for child in self.ui_elements['repeat_frame'].winfo_children():
            if isinstance(child, ttk.Checkbutton):
                child.config(text=self.translations[lang]['enable_click_repetition'])
            elif isinstance(child, ttk.Label):
                child.config(text=self.translations[lang]['number_of_clicks'])

        # Cursor Position
        self.ui_elements['cursor_frame'].config(text=self.translations[lang]['cursor_position'])
        self.ui_elements['radio_current'].config(text=self.translations[lang]['current_position'])
        self.ui_elements['radio_pick'].config(text=self.translations[lang]['select_position'])
        self.ui_elements['label_x'].config(text=self.translations[lang]['x'])
        self.ui_elements['label_y'].config(text=self.translations[lang]['y'])

        # Hotkey Configuration
        self.ui_elements['hotkey_frame'].config(text=self.translations[lang]['hotkey_config'])
        self.ui_elements['label_start_hotkey'].config(text=self.translations[lang]['start_hotkey'])
        self.ui_elements['label_stop_hotkey'].config(text=self.translations[lang]['stop_hotkey'])

        # Save and Load Buttons
        self.ui_elements['button_save'].config(text=self.translations[lang]['save_config'])
        self.ui_elements['button_load'].config(text=self.translations[lang]['load_config'])

        # Start and Stop Buttons
        self.ui_elements['button_start'].config(text=self.translations[lang]['start'])
        self.ui_elements['button_stop'].config(text=self.translations[lang]['stop'])

        # Status Label
        if self.running:
            self.status_label.config(text=self.translations[lang]['status_running'])
        else:
            self.status_label.config(text=self.translations[lang]['status_inactive'])

        # Update tooltips
        ToolTip(self.randomize_check, text=self.translations[lang]['tooltip_randomize_interval'])
        ToolTip(self.random_range_entry, text=self.translations[lang]['tooltip_random_range'])
        ToolTip(self.ui_elements['dropdown_click_type'], text=self.translations[lang]['tooltip_click_type'])
        ToolTip(self.ui_elements['dropdown_click_button'], text=self.translations[lang]['tooltip_click_button'])
        ToolTip(self.ui_elements['button_save'], text=self.translations[lang]['save_config_message'])
        ToolTip(self.ui_elements['button_load'], text=self.translations[lang]['load_config_message'])
        ToolTip(self.start_button, text=self.translations[lang]['tooltip_start'])
        ToolTip(self.stop_button, text=self.translations[lang]['tooltip_stop'])
        ToolTip(self.ui_elements['repeat_frame'], text=self.translations[lang]['tooltip_enable_click_repetition'])
        ToolTip(self.click_count_entry, text=self.translations[lang]['tooltip_number_of_clicks'])
        ToolTip(self.ui_elements['radio_current'], text=self.translations[lang]['tooltip_current_position'])
        ToolTip(self.ui_elements['radio_pick'], text=self.translations[lang]['tooltip_select_position'])
        ToolTip(self.cursor_x_entry, text=self.translations[lang]['tooltip_x'])
        ToolTip(self.cursor_y_entry, text=self.translations[lang]['tooltip_y'])

    def validate_integer(self, P):
        if P == '':
            return True
        try:
            int(P)
            return True
        except ValueError:
            return False

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
        # Fetch the translated message
        message = self.translations[self.current_language]['select_position_info']
        self.show_info(self.translations[self.current_language]['select_position_title'], message)

        # Create a full-screen transparent window
        self.capture_window = tk.Toplevel()
        self.capture_window.title(self.translations[self.current_language]['select_position_title'])
        self.capture_window.attributes('-fullscreen', True)
        self.capture_window.attributes('-alpha', 0.01)  # Make it almost transparent
        self.capture_window.attributes('-topmost', True)
        self.capture_window.bind('<Button-1>', self.get_click_position)

    def get_click_position(self, event):
        """
        Gets the click position and stores it.
        """
        x, y = event.x_root, event.y_root
        self.cursor_x.set(str(x))
        self.cursor_y.set(str(y))
        self.capture_window.destroy()
        self.master.deiconify()

    def start_clicking(self):
        """
        Starts the autoclicking process without delay.
        """
        if not self.running:
            try:
                minutes = int(self.interval_minutes.get() or 0)
                seconds = int(self.interval_seconds.get() or 0)
                milliseconds = int(self.interval_milliseconds.get() or 0)

                total_interval = (minutes * 60 + seconds) * 1000 + milliseconds

                if total_interval <= 0:
                    raise ValueError(self.translations[self.current_language]['error_invalid_interval_message'])

                if self.randomize_interval.get():
                    random_range = int(self.random_range.get() or 0)
                    if random_range < 0 or random_range > total_interval:
                        raise ValueError(self.translations[self.current_language]['error_invalid_interval_message'])

                self.running = True
                self.start_button.config(state="disabled")
                self.stop_button.config(state="normal")
                self.status_label.config(text=self.translations[self.current_language]['status_running'])

                # Removed countdown delay as per user request

                self.click_thread = threading.Thread(target=self.click_mouse, args=(total_interval,), daemon=True)
                self.click_thread.start()
            except ValueError as e:
                self.show_error(self.translations[self.current_language]['error_invalid_interval_title'], str(e))
            except Exception as e:
                self.show_error("Error", str(e))

    def click_mouse(self, interval):
        """
        Performs the click action repeatedly with a given interval.
        """
        try:
            if self.repeat_enabled.get():
                repeat_count = int(self.repeat_count.get() or 0)
                for _ in range(repeat_count):
                    if self.running:
                        self.perform_click_action()
                        actual_interval = interval
                        if self.randomize_interval.get():
                            variation = random.randint(0, int(self.random_range.get() or 0))
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
                        variation = random.randint(0, int(self.random_range.get() or 0))
                        actual_interval += variation
                    pyautogui.sleep(actual_interval / 1000.0)
        except Exception as e:
            self.show_error("Error", str(e))
            self.stop_clicking()

    def perform_click_action(self):
        """
        Performs the appropriate click action based on user configuration.
        """
        if self.cursor_position.get() == "pick":
            x = int(self.cursor_x.get() or 0)
            y = int(self.cursor_y.get() or 0)
            pyautogui.moveTo(x, y)

        button = self.click_button.get().lower()
        if self.click_type.get() == self.translations[self.current_language]['single']:
            pyautogui.click(button=button)
        elif self.click_type.get() == self.translations[self.current_language]['double']:
            pyautogui.doubleClick(button=button)

    def stop_clicking(self):
        """
        Stops the autoclicking process.
        """
        if self.running:
            self.running = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.status_label.config(text=self.translations[self.current_language]['status_inactive'])

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
        Registers the start and stop hotkeys with language support.
        """
        # Unbind previous hotkeys
        for handler in self.hotkey_handlers:
            keyboard.remove_hotkey(handler)
        self.hotkey_handlers.clear()

        # Validate that the hotkeys are not the same
        if self.start_hotkey.get() == self.stop_hotkey.get():
            self.show_error(self.translations[self.current_language]['error_hotkey_title'], self.translations[self.current_language]['error_hotkey_same'])
            return

        # Register new hotkeys
        start_hotkey = self.start_hotkey.get()
        stop_hotkey = self.stop_hotkey.get()
        try:
            start_handler = keyboard.add_hotkey(start_hotkey, self.start_clicking)
            self.hotkey_handlers.append(start_handler)
        except Exception as e:
            error_message = self.translations[self.current_language]['error_hotkey_register'].format(action='start', key=start_hotkey, error=str(e))
            self.show_error(self.translations[self.current_language]['error_hotkey_title'], error_message)

        try:
            stop_handler = keyboard.add_hotkey(stop_hotkey, self.stop_clicking)
            self.hotkey_handlers.append(stop_handler)
        except Exception as e:
            error_message = self.translations[self.current_language]['error_hotkey_register'].format(action='stop', key=stop_hotkey, error=str(e))
            self.show_error(self.translations[self.current_language]['error_hotkey_title'], error_message)

    def save_settings(self):
        """
        Saves the current configuration to a file selected by the user.
        """
        # Validate that the hotkeys are not the same before saving
        if self.start_hotkey.get() == self.stop_hotkey.get():
            self.show_error(self.translations[self.current_language]['error_hotkey_title'], self.translations[self.current_language]['error_save_hotkey_same'])
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON Files", "*.json")],
                                                 title=self.translations[self.current_language]['save_config_title'])
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
                "language": self.current_language
            }
            try:
                with open(file_path, "w", encoding='utf-8') as f:
                    json.dump(settings, f, indent=4)
                self.show_info(self.translations[self.current_language]['info_config_saved_title'], self.translations[self.current_language]['info_config_saved_message'])
            except Exception as e:
                error_message = self.translations[self.current_language]['error_save_config_message'].format(error=str(e))
                self.show_error(self.translations[self.current_language]['error_save_config_title'], error_message)

    def load_settings(self):
        """
        Loads the configuration from a file selected by the user.
        """
        file_path = filedialog.askopenfilename(defaultextension=".json",
                                               filetypes=[("JSON Files", "*.json")],
                                               title=self.translations[self.current_language]['load_config_title'])
        if file_path:
            try:
                with open(file_path, "r", encoding='utf-8') as f:
                    settings = json.load(f)
                self.interval_minutes.set(settings.get("interval_minutes", '0'))
                self.interval_seconds.set(settings.get("interval_seconds", '0'))
                self.interval_milliseconds.set(settings.get("interval_milliseconds", '100'))
                self.randomize_interval.set(settings.get("randomize_interval", False))
                self.random_range.set(settings.get("random_range", '0'))
                self.click_type.set(settings.get("click_type", self.translations[self.current_language]['single']))
                self.click_button.set(settings.get("click_button", self.translations[self.current_language]['left']))
                self.repeat_enabled.set(settings.get("repeat_enabled", False))
                self.repeat_count.set(settings.get("repeat_count", '10'))
                self.cursor_position.set(settings.get("cursor_position", "current"))
                self.cursor_x.set(settings.get("cursor_x", '0'))
                self.cursor_y.set(settings.get("cursor_y", '0'))
                self.start_hotkey.set(settings.get("start_hotkey", "F8"))
                self.stop_hotkey.set(settings.get("stop_hotkey", "F9"))  # Changed default to "F9"
                self.current_language = settings.get("language", 'en')
                self.language_var.set(self.current_language)

                # Re-register the hotkeys
                self.register_hotkeys()

                # Update interface elements
                self.update_ui_language()
                self.toggle_repeat()
                self.toggle_randomize()

                self.show_info(self.translations[self.current_language]['info_config_loaded_title'], self.translations[self.current_language]['info_config_loaded_message'])
            except FileNotFoundError:
                self.show_error(self.translations[self.current_language]['error_load_config_title'], self.translations[self.current_language]['error_load_config_not_found'])
            except Exception as e:
                error_message = self.translations[self.current_language]['error_load_config_message'].format(error=str(e))
                self.show_error(self.translations[self.current_language]['error_load_config_title'], error_message)

    def show_info(self, title, message):
        """
        Shows an informational message box with translated text.
        """
        messagebox.showinfo(title, message)

    def show_error(self, title, message):
        """
        Shows an error message box with translated text.
        """
        messagebox.showerror(title, message)

# Main function to start the application
def main():
    """
    Main function to create and run the Tkinter application with language support.
    """
    # Use a window with ttkbootstrap theme
    root = ttk.Window(themename="superhero")
    app = AutoClicker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
