# FileConverter
A versatile desktop utility for converting files between various formats. Supports images, videos, audio, documents, and archives with a clean, user-friendly interface
## ✨ Core Features

-   **Comprehensive Format Support:**
    -   **Video:** Convert between `MP4`, `AVI`, `MKV`, `MOV`, and create animated `GIF`s.
    -   **Audio:** Convert between `MP3`, `WAV`, `FLAC`, `OGG`.
    -   **Image:** Convert `PNG`, `JPG`, `WEBP`, `TIFF`, with support for professional **RAW** camera formats.
    -   **Document:** Convert `.docx` to `.pdf`, or `.pdf` to `.docx` and `.txt`.
    -   **Archive:** Convert between `ZIP`, `7z`, `TAR` archives.

-   **Powerful Tools:**
    -   **File Merging** for both videos and PDFs.
    -   **Detailed Settings** to control quality, bitrate, resolution, and more.
    -   **Preset Manager** to save and load your favorite conversion settings.

-   **User-Friendly Interface:**
    -   Drag-and-drop support for files and folders.
    -   Customizable **Light & Dark themes**.
    -   Built-in **Setup Guide** and **Dependency Checker** to help new users.

---

## 🚀 Getting Started

Follow these instructions to get the application running on your Windows machine.

### 📋 Prerequisites

This application relies on a few powerful, free external programs. Please install the following on your system:

1.  **Python 3.12:**
    -   **Why?** The core language the application runs on.
    -   **Download:** [python.org (v3.12.4)](https://www.python.org/downloads/release/python-3124/)
    -   **✅ Important:** During installation, you **must** check the box that says **"Add python.exe to PATH"**.

2.  **FFmpeg (for Video & Audio):**
    -   **Why?** The engine for all multimedia conversions.
    -   **Download:** We recommend the "essentials" build from [Gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
    -   **Setup:** Unzip the file to a permanent location (like `C:\ffmpeg`) and add its `bin` subfolder to the system PATH.

3.  **LibreOffice (for Documents):**
    -   **Why?** Used to convert Microsoft Office documents and other text formats.
    -   **Download:** [libreoffice.org](httpss://www.libreoffice.org/download/download-libreoffice/)
    -   **Setup:** Add its `program` subfolder (e.g., `C:\Program Files\LibreOffice\program`) to the system PATH.

4.  **7-Zip (for Archives):**
    -   **Why?** Handles all archive-related conversions.
    -   **Download:** [7-zip.org](https://www.7-zip.org/)
    -   **Setup:** Add its installation directory (e.g., `C:\Program Files\7-Zip`) to the system PATH.

> **Tip:** The application has a built-in `Help > Setup Guide` with detailed instructions for adding programs to the system PATH. Use the `Help > Dependency Checker` to verify your setup.

### 💻 Installation & Launch

The application is launched via a script that handles all Python-related setup automatically.

#### Step 1: First-Time Setup
You only need to do this once.

1.  Download the project source code by clicking `Code > Download ZIP` on this GitHub page.
2.  Extract the ZIP file to a permanent folder on your computer.
3.  Double-click the file named **`install_requirements.bat`**.

This script will create a private Python environment for the app and download all necessary libraries. This may take a few minutes.

#### Step 2: Running the Application
After the one-time setup is complete, you can launch the program at any time.

1.  Double-click the **`run.bat`** file.
