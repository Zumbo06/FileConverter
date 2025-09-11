# FileConverter
A versatile desktop utility for converting files between various formats. Supports images, videos, audio, documents, and archives with a clean, user-friendly interface

These programs are required for file conversion and must be added to your system's PATH so the application can find them.
Python (Version 3.12 recommended)
Why: This is the programming language the application is written in.
Download: python.org (v3.12.4)
Important: During installation, you must check the box that says "Add python.exe to PATH".
FFmpeg (for Video & Audio)
Why: The world's leading multimedia framework, used for all video and audio conversions, including creating animated GIFs.
Download: We recommend the "essentials" build from Gyan.dev.
Setup: Unzip the downloaded file to a permanent location (e.g., C:\ffmpeg) and add its bin subfolder to the system PATH.
LibreOffice (for Documents)
Why: A powerful, free office suite used to convert document formats like .docx, .odt, .pptx, etc.
Download: libreoffice.org
Setup: Install the program and add its program subfolder (e.g., C:\Program Files\LibreOffice\program) to the system PATH.
7-Zip (for Archives)
Why: A high-performance file archiver used for all archive conversions (.zip, .7z, .rar).
Download: 7-zip.org
Setup: Install the program and add its installation directory (e.g., C:\Program Files\7-Zip) to the system PATH.
Note: The application includes a built-in Setup Guide (Help > Setup Guide) and Dependency Checker (Help > Dependency Checker) to assist you with this process.
2. Python Libraries (Handled by the installer script)
These are the Python packages the application depends on. You do not need to install these manually; the provided setup script will handle it for you.
PyQt6 (for the user interface)
Pillow, rawpy, pillow-heif, pillow-avif (for image processing)
pdf2docx, PyMuPDF, pypdf (for PDF conversion and merging)
qt-material (for UI theming)
Installation & Launch
This application uses a virtual environment to keep its Python libraries separate from your main system, ensuring a clean and reliable setup.
First-Time Setup
On your first run, you must run the requirements installer.
Download the Project: Download the project files as a ZIP from GitHub and extract them to a folder on your computer.
Run the Installer Script: Double-click the file named install_requirements.bat.
This will create a private Python environment inside a new venv folder.
It will then automatically download and install all the necessary Python libraries. This may take a few minutes.
You only need to do this once.
Running the Application
After the first-time setup is complete, you can start the application at any time.
Double-click the run.bat file.
This script will quickly check for the required external software (FFmpeg, etc.) and launch the main application window.
