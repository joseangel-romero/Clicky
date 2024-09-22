# 🖱️ Clicky AutoClicker

![GitHub release (latest by date)](https://img.shields.io/github/v/release/joseangel-romero/AutoClicker?style=plastic) ![GitHub all releases](https://img.shields.io/github/downloads/joseangel-romero/AutoClicker/total?style=plastic) ![GitHub](https://img.shields.io/github/license/joseangel-romero/AutoClicker?style=plastic)

## 🌟 Introduction

Welcome to **Clicky**, a versatile and user-friendly Python-based application designed to automate mouse clicks on your desktop. Whether you're gaming, performing repetitive tasks, or testing software, AutoClicker streamlines your workflow by handling mouse clicks with precision and flexibility.

## 📝 Features

- **Customizable Click Intervals:**  
  Set precise intervals for mouse clicks using minutes, seconds, and milliseconds.

- **Randomized Click Intervals:**  
  Introduce variability in click intervals to mimic natural clicking patterns, preventing detection in gaming or automated testing environments.

- **Multiple Click Types:**  
  Choose between single-click and double-click actions to suit your needs.

- **Selectable Mouse Buttons:**  
  Perform clicks using the left or right mouse buttons.

- **Click Repetition Options:**  
  - **Infinite Clicks:** Enable continuous clicking until manually stopped.
  - **Limited Clicks:** Specify an exact number of clicks to perform.

- **Flexible Click Positioning:**  
  - **Current Cursor Position:** Click exactly where your mouse cursor is located.
  - **Custom Position Selection:** Easily choose a specific screen location by selecting it directly within the application.

- **Hotkey Configuration:**  
  Assign custom hotkeys to start and stop the autoclicking process, enabling seamless control without switching windows.

- **Language Support:**  
  Switch between **English** and **Spanish** dynamically to cater to your language preference.

- **Save and Load Configurations:**  
  Preserve your settings by saving them to a file and loading them later, ensuring consistency across sessions.

- **User-Friendly Interface:**  
  An intuitive GUI built with `ttkbootstrap` ensures ease of use, even for those unfamiliar with automation tools.

- **Robust Error Handling:**  
  Comprehensive validation and error messages guide you through correct configuration and usage.

## 🚀 Getting Started

AutoClicker is a Python-based application that automates mouse clicks on your desktop. Follow the instructions below to install and run the application.

### ⚙️ Prerequisites

- **Python 3.7 or higher**  
  Ensure you have Python installed on your system. You can download it from the [official website](https://www.python.org/downloads/).

### 📥 Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/joseangel-romero/AutoClicker.git
   cd AutoClicker
  
2. **Install dependencies:**

    ```bash
    pip install -r requirements.txt

3. **Build*:*

    ```bash
    pyinstaller autoclicker.spec
