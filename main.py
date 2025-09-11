# main.py

import sys
import os
import re
import subprocess
import shutil
import tempfile
import json
from functools import partial
import shutil
from ui.dependency_checker_ui import Ui_DependencyCheckerDialog # New Import
# Import third-party libraries
import rawpy
import pillow_heif
import pillow_avif
from pypdf import PdfWriter
from pdf2docx import Converter as PdfConverter
import fitz
from PyQt6.QtWidgets import (
    QApplication, QDialog, QMainWindow, QFileDialog, QTableWidgetItem,
    QComboBox, QProgressBar, QMessageBox, QPushButton, QWidget, QFormLayout,
    QSpinBox, QSlider, QLabel, QCheckBox, QGroupBox, QInputDialog, QAbstractItemView # Add QAbstractItemView
)
from PyQt6.QtCore import Qt, QThread, QObject, pyqtSignal
from PyQt6.QtGui import QPixmap
import qt_material
from ui.main_window_ui import Ui_MainWindow
from ui.preferences_dialog_ui import Ui_PreferencesDialog
from ui.guide_dialog_ui import Ui_SetupGuideDialog # New Import
from PIL import Image

pillow_heif.register_heif_opener()


class SetupGuideDialog(QDialog, Ui_SetupGuideDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("First-Time Setup Guide")
        
        guide_html = """
        <html>
        <body>
            <h4>Welcome to File Converter!</h4>
            <p>To enable all features, three free external programs are required:</p>
            <ul>
                <li><b>FFmpeg:</b> For all video and audio conversions. (Essential)</li>
                <li><b>LibreOffice:</b> For converting documents, spreadsheets, and presentations.</li>
                <li><b>7-Zip:</b> For handling archive files.</li>
            </ul>
            <p>These programs must be installed AND added to your system's PATH environment variable.</p>
            <hr>
            <h4>Step 1: Install Software</h4>
            <ol>
                <li>
                    <b>Download FFmpeg:</b> For Windows, a good source is 
                    <a href="https://www.gyan.dev/ffmpeg/builds/">gyan.dev</a>. Download the "essentials" build.
                    This will be a .zip file (e.g., <code>ffmpeg-essentials_build.zip</code>).
                </li>
                <li>Download and install <b>7-Zip</b> from <a href="https://www.7-zip.org/">www.7-zip.org</a>.</li>
                <li>Download and install <b>LibreOffice</b> from <a href="https://www.libreoffice.org/download/">www.libreoffice.org</a>.</li>
            </ol>
            <h4>Step 2: Add to Windows PATH</h4>
            <p>This allows the converter to find the programs from any command line.</p>
            <ol>
                <li>
                    <b>For FFmpeg:</b> Unzip the downloaded file to a permanent location on your computer,
                    for example: <code>C:\\ffmpeg</code>.
                </li>
                <li>Press the <b>Windows Key</b>, type <code>Edit the system environment variables</code>, and press Enter.</li>
                <li>In the window that opens, click the <b>"Environment Variables..."</b> button.</li>
                <li>In the bottom box ("System variables"), find and select the variable named <b>"Path"</b>, then click <b>"Edit..."</b>.</li>
                <li>Click <b>"New"</b> and add the path to the <b><code>bin</code></b> folder inside your FFmpeg directory. For example:<br><code>C:\\ffmpeg\\bin</code></li>
                <li>Click <b>"New"</b> again and add the installation directory for <b>7-Zip</b>. By default, this is:<br><code>C:\\Program Files\\7-Zip</code></li>
                <li>Click <b>"New"</b> again and add the installation directory for <b>LibreOffice</b>. By default, this is:<br><code>C:\\Program Files\\LibreOffice\\program</code></li>
                <li>Click OK on all windows to save the changes.</li>
            </ol>
            <p><b>Important:</b> You must <b>restart this application</b> (and possibly your computer) for the new PATH settings to take effect.</p>
        </body>
        </html>
        """
        self.textBrowser.setHtml(guide_html)

    def get_dont_remind_state(self):
        return self.dontRemindCheckBox.isChecked()

class DependencyCheckerDialog(QDialog, Ui_DependencyCheckerDialog):
    """A dialog to check for required external command-line tools."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.check_dependencies()

    def check_dependencies(self):
        dependencies = {
            "FFmpeg (Video/Audio)": "ffmpeg",
            "7-Zip (Archives)": "7z",
            "LibreOffice (Documents)": "soffice"
        }
        
        results_html = "<h4>Required Software Check</h4>"
        
        for name, exe in dependencies.items():
            path = shutil.which(exe)
            if path:
                results_html += f"<p><b>{name}:</b> <font color='green'>FOUND</font><br><small><i>{path}</i></small></p>"
            else:
                results_html += f"<p><b>{name}:</b> <font color='red'>NOT FOUND</font><br><small><i>Please install it and add it to your system's PATH. See the Setup Guide for help.</i></small></p>"
        
        self.textBrowser.setHtml(results_html)

# =============================================================================
# PREFERENCES DIALOG LOGIC
# =============================================================================

# In main.py, replace the existing PreferencesDialog class with this one

class PreferencesDialog(QDialog, Ui_PreferencesDialog):
    def __init__(self, current_settings, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.settings = current_settings
        self.defaultOutputDirLineEdit.setText(self.settings.get('default_output_dir', ''))
        self.clearListCheckBox.setChecked(self.settings.get('clear_list_on_complete', False))
        self.saveToSourceCheckBox.setChecked(self.settings.get('save_to_source_dir', False))
        
        # New: Populate and set the current theme
        self.themeComboBox.addItems(["System Default", "Light", "Dark"])
        self.themeComboBox.setCurrentText(self.settings.get('theme', 'System Default'))

        self.browseButton.clicked.connect(self.browse_for_directory)

    def browse_for_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Default Output Directory")
        if dir_path: self.defaultOutputDirLineEdit.setText(dir_path)

    def get_settings(self):
        return {
            'default_output_dir': self.defaultOutputDirLineEdit.text(),
            'clear_list_on_complete': self.clearListCheckBox.isChecked(),
            'save_to_source_dir': self.saveToSourceCheckBox.isChecked(),
            'theme': self.themeComboBox.currentText() # New: Get theme setting
        }
# =============================================================================
# SETTINGS PANELS
# =============================================================================

class BaseSettingsPanel(QWidget):
    settings_changed = pyqtSignal(dict)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QFormLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

    def load_settings(self, settings):
        raise NotImplementedError

    def get_settings(self):
        raise NotImplementedError

# In main.py, replace the existing settings panel classes with these corrected versions:

class ImageSettingsPanel(BaseSettingsPanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_label = QLabel()
        self.resize_combo = QComboBox()
        self.resize_combo.addItems(["None", "25%", "50%", "75%", "1920px (Full HD)", "1280px (HD)"])

        self.layout().addRow("JPEG/WEBP Quality:", self.quality_slider)
        self.layout().addRow("", self.quality_label)
        self.layout().addRow("Resize:", self.resize_combo)

        self.quality_slider.valueChanged.connect(lambda v: self.quality_label.setText(str(v)))
        self.quality_slider.valueChanged.connect(self.on_change)
        self.resize_combo.currentIndexChanged.connect(self.on_change)

    def on_change(self, _):
        self.settings_changed.emit(self.get_settings())

    def load_settings(self, settings):
        self.quality_slider.setValue(settings.get('quality', 95))
        self.resize_combo.setCurrentText(settings.get('resize', "None"))

    def get_settings(self):
        return {'quality': self.quality_slider.value(), 'resize': self.resize_combo.currentText()}

class VideoSettingsPanel(BaseSettingsPanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems(["Default", "500k", "1M", "2M", "5M", "10M"])
        self.resize_combo = QComboBox()
        self.resize_combo.addItems(["None", "1080p (1920x1080)", "720p (1280x720)", "480p (640x480)"])
        self.remove_audio_checkbox = QCheckBox("Remove audio track")
        
        self.layout().addRow("Video Bitrate:", self.bitrate_combo)
        self.layout().addRow("Resize:", self.resize_combo)
        self.layout().addRow(self.remove_audio_checkbox)

        self.bitrate_combo.currentIndexChanged.connect(self.on_change)
        self.resize_combo.currentIndexChanged.connect(self.on_change)
        self.remove_audio_checkbox.stateChanged.connect(self.on_change)

    def on_change(self, _):
        self.settings_changed.emit(self.get_settings())

    def load_settings(self, settings):
        self.bitrate_combo.setCurrentText(settings.get('video_bitrate', "Default"))
        self.resize_combo.setCurrentText(settings.get('resize', "None"))
        self.remove_audio_checkbox.setChecked(settings.get('remove_audio', False))

    def get_settings(self):
        return {
            'video_bitrate': self.bitrate_combo.currentText(),
            'resize': self.resize_combo.currentText(),
            'remove_audio': self.remove_audio_checkbox.isChecked()
        }
        
class AudioSettingsPanel(BaseSettingsPanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems(["Default", "96k", "128k", "192k", "256k", "320k"])
        self.layout().addRow("Audio Bitrate:", self.bitrate_combo)
        self.bitrate_combo.currentIndexChanged.connect(self.on_change)

    def on_change(self, _):
        self.settings_changed.emit(self.get_settings())

    def load_settings(self, settings):
        self.bitrate_combo.setCurrentText(settings.get('audio_bitrate', "Default"))

    def get_settings(self):
        return {'audio_bitrate': self.bitrate_combo.currentText()}

# =============================================================================
# CONFIGURATION AND WORKER CLASSES
# =============================================================================
RAW_EXTENSIONS = {".3fr",".arw",".cr2",".cr3",".crw",".dcr",".dng",".erf",".mos",".mrw",".orf",".pef",".raf",".raw",".rw2",".x3f"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".aac", ".wma", ".m4a"}
FLEXIBLE_CONVERSION_MAP = {
    ".7z": {"archive": ["zip", "tar"]}, ".zip": {"archive": ["7z", "tar"]}, ".rar": {"archive": ["7z", "zip", "tar"]}, ".iso": {"archive": ["7z", "zip", "tar"]}, ".dmg": {"archive": ["7z", "zip", "tar"]}, ".cab": {"archive": ["7z", "zip", "tar"]}, ".gz": {"archive": ["7z", "zip", "tar"]}, ".bz2": {"archive": ["7z", "zip", "tar"]}, ".tar": {"archive": ["7z", "zip"]}, ".jar": {"archive": ["7z", "zip", "tar"]}, ".deb": {"archive": ["7z", "zip", "tar"]}, ".ace": {"archive": ["7z", "zip", "tar"]}, ".alz": {"archive": ["7z", "zip", "tar"]}, ".arc": {"archive": ["7z", "zip", "tar"]}, ".arj": {"archive": ["7z", "zip", "tar"]}, ".cpio": {"archive": ["7z", "zip", "tar"]}, ".img": {"archive": ["7z", "zip", "tar"]}, ".lha": {"archive": ["7z", "zip", "tar"]}, ".lz": {"archive": ["7z", "zip", "tar"]}, ".lzma": {"archive": ["7z", "zip", "tar"]},
    **{ext: {"video": ["avi", "mkv", "mov"], "audio": ["mp3", "wav"], "image": ["png", "jpg", "gif"]} for ext in VIDEO_EXTENSIONS},
    **{ext: {"audio": ["wav", "ogg", "flac"] if ext!=".wav" else ["mp3","ogg","flac"]} for ext in AUDIO_EXTENSIONS},
    ".png": {"image": ["jpg", "webp", "bmp", "tiff"]}, ".jpg": {"image": ["png", "webp", "bmp", "tiff"]}, ".jpeg": {"image": ["png", "webp", "bmp", "tiff"]}, ".webp": {"image": ["png", "jpg", "bmp", "tiff"]}, ".bmp": {"image": ["png", "jpg", "webp", "tiff"]}, ".tiff": {"image": ["png", "jpg", "webp", "bmp"]}, ".tif": {"image": ["png", "jpg", "webp", "bmp"]}, ".heic": {"image": ["png", "jpg", "webp", "tiff"]}, ".heif": {"image": ["png", "jpg", "webp", "tiff"]}, ".avif": {"image": ["png", "jpg", "webp", "tiff"]}, ".gif": {"image": ["png", "webp"]}, ".ico": {"image": ["png"]}, ".icns": {"image": ["png", "ico"]}, ".psd": {"image": ["png", "jpg", "tiff"]}, ".xcf": {"image": ["png", "jpg", "tiff"]}, ".eps": {"image": ["png", "jpg"]}, ".ps": {"image": ["png", "jpg"]}, ".ppm": {"image": ["png", "jpg"]}, ".jfif": {"image": ["png", "jpg"]},
    ".docx": {"document": ["pdf", "odt", "txt"]}, ".doc": {"document": ["pdf", "odt", "txt"]},
    ".pdf": {"document": ["docx", "txt"]}, # MODIFIED LINE
    ".odt": {"document": ["pdf", "docx"]}, ".rtf": {"document": ["pdf", "docx"]}, ".txt": {"document": ["pdf", "docx"]}, ".pub": {"document": ["pdf", "docx"]}, ".xps": {"document": ["pdf", "docx"]},
    ".pptx": {"presentation": ["pdf", "odp"]}, ".ppt": {"presentation": ["pdf", "odp"]}, ".odp": {"presentation": ["pdf", "pptx"]},
    ".xlsx": {"spreadsheet": ["pdf", "ods", "csv", "xml", "fods"]}, ".xls": {"spreadsheet": ["pdf", "ods", "csv", "xml", "fods"]}, ".ods": {"spreadsheet": ["pdf", "xlsx", "csv", "xml", "fods"]},
}
for ext in RAW_EXTENSIONS: FLEXIBLE_CONVERSION_MAP[ext] = {"image": ["png", "jpg", "tiff"]}
def get_file_category(file_ext):
    if file_ext in FLEXIBLE_CONVERSION_MAP: return next(iter(FLEXIBLE_CONVERSION_MAP[file_ext]))
    return "unknown"

class FFmpegWorker(QObject):
    progress_updated=pyqtSignal(int,int); finished=pyqtSignal(int,str); error=pyqtSignal(int,str)
    def __init__(self,r,i,o,m,s,p=None): super().__init__(p); self.row,self.i,self.o,self.mode,self.settings,self.process=r,i,o,m,s,None
    def run(self):
        cmd=['ffmpeg','-i',self.i]; is_vid=get_file_category(os.path.splitext(self.i)[1].lower())=="video"
        if self.mode=="video_to_audio": cmd.extend(['-vn'])
        elif self.mode=="video_to_image": cmd.extend(['-ss','00:00:05','-vframes','1'])
        else: # Standard video/audio conversion, apply settings
            if self.settings:
                if (br:=self.settings.get('video_bitrate',"Default"))!="Default": cmd.extend(['-b:v',br])
                if (abr:=self.settings.get('audio_bitrate',"Default"))!="Default": cmd.extend(['-b:a',abr])
                if self.settings.get('remove_audio',False): cmd.extend(['-an'])
                if (rs:=self.settings.get('resize',"None"))!="None":
                    h={'1080p':1080,'720p':720,'480p':480}.get(rs.split()[0],None)
                    if h: cmd.extend(['-vf',f'scale=-2:{h}'])
        cmd.extend(['-y',self.o])
        try:
            self.process=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=='win32' else 0)
            dur=self.get_video_duration() if is_vid else 0
            for line in self.process.stdout:
                if is_vid and dur>0 and (m:=re.search(r"time=(\d{2}):(\d{2}):(\d{2})\.\d{2}",line)):
                    h,m,s=map(int,m.groups()); cur=h*3600+m*60+s; self.progress_updated.emit(self.row,min(100,int((cur/dur)*100)))
            self.process.wait()
            if self.process.returncode==0:self.progress_updated.emit(self.row,100);self.finished.emit(self.row,self.o)
            else:self.error.emit(self.row,f"FFmpeg error (code {self.process.returncode})")
        except Exception as e: self.error.emit(self.row,str(e))
    def get_video_duration(self):
        try:return float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',self.i],capture_output=True,text=True,check=True).stdout.strip())
        except: return None
    def stop(self):
        if self.process and self.process.poll()is None: self.process.terminate();self.process.wait()

class ImageWorker(QObject):
    finished=pyqtSignal(int,str); error=pyqtSignal(int,str)
    def __init__(self,r,i,o,s,p=None): super().__init__(p); self.row,self.i,self.o,self.settings=r,i,o,s
    def run(self):
        try:
            with Image.open(self.i) as img:
                if self.o.lower().endswith(('.jpg','.jpeg','.bmp')) and img.mode in ('RGBA','LA','P'): img=img.convert('RGB')
                if self.settings and (rs:=self.settings.get('resize',"None"))!="None":
                    w,h=img.size
                    if '%' in rs: s=int(rs.strip('%'))/100; nw,nh=int(w*s),int(h*s)
                    else: p=int(rs.split('px')[0]); nw,nh=(p,int(h*p/w)) if w>h else (int(w*p/h),p)
                    img=img.resize((nw,nh),Image.Resampling.LANCZOS)
                save_opts={'quality':self.settings.get('quality',95)} if self.settings else {}
                img.save(self.o,**save_opts)
            self.finished.emit(self.row,self.o)
        except Exception as e: self.error.emit(self.row,str(e))
    def stop(self): pass

class MergeWorker(QObject):
    progress_updated = pyqtSignal(int, int); finished = pyqtSignal(int, str); error = pyqtSignal(int, str)
    def __init__(self, row, inputs, output, cat, p=None):
        super().__init__(p); self.row, self.inputs, self.output, self.category, self.process = row, inputs, output, cat, None
    def run(self):
        try:
            if self.category == "document": # PDF
                merger = PdfWriter()
                for i, pdf_path in enumerate(self.inputs):
                    merger.append(pdf_path)
                    self.progress_updated.emit(self.row, int((i + 1) / len(self.inputs) * 100))
                merger.write(self.output); merger.close()
                self.finished.emit(self.row, self.output)
            elif self.category == "video":
                with tempfile.NamedTemporaryFile('w', delete=False, suffix='.txt', encoding='utf-8') as f:
                    for path in self.inputs: f.write(f"file '{os.path.normpath(path)}'\n")
                    list_file = f.name
                cmd = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', list_file, '-c', 'copy', '-y', self.output]
                self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
                self.process.wait()
                os.remove(list_file)
                if self.process.returncode == 0:
                    self.progress_updated.emit(self.row, 100); self.finished.emit(self.row, self.output)
                else:
                    self.error.emit(self.row, f"FFmpeg merge error (code {self.process.returncode})")
        except Exception as e: self.error.emit(self.row, f"Merge failed: {str(e)}")
    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate(); self.process.wait()
class PdfToDocxWorker(QObject):
    """A specialized worker to convert PDF to DOCX using the pdf2docx library."""
    finished = pyqtSignal(int, str)
    error = pyqtSignal(int, str)

    def __init__(self, row, input_path, output_path, parent=None):
        super().__init__(parent)
        self.row, self.input_path, self.output_path = row, input_path, output_path

    def run(self):
        try:
            cv = PdfConverter(self.input_path)
            cv.convert(self.output_path, start=0, end=None)
            cv.close()
            self.finished.emit(self.row, self.output_path)
        except Exception as e:
            self.error.emit(self.row, f"PDF to DOCX conversion failed: {str(e)}")

    def stop(self):
        pass

class PdfToTextWorker(QObject):
    """A specialized worker to extract text from a PDF using PyMuPDF."""
    finished = pyqtSignal(int, str)
    error = pyqtSignal(int, str)

    def __init__(self, row, input_path, output_path, parent=None):
        super().__init__(parent)
        self.row, self.input_path, self.output_path = row, input_path, output_path

    def run(self):
        try:
            full_text = ""
            with fitz.open(self.input_path) as doc:
                for page in doc:
                    full_text += page.get_text()
            
            with open(self.output_path, 'w', encoding='utf-8') as f:
                f.write(full_text)
                
            self.finished.emit(self.row, self.output_path)
        except Exception as e:
            self.error.emit(self.row, f"PDF to TXT conversion failed: {str(e)}")

    def stop(self):
        pass
# Other workers remain largely the same, but simplified for brevity
class RawImageWorker(QObject):
    finished=pyqtSignal(int,str);error=pyqtSignal(int,str)
    def __init__(self,r,i,o,s,p=None):super().__init__(p);self.row,self.i,self.o,self.s=r,i,o,s
    def run(self):
        try:
            with rawpy.imread(self.i) as raw:rgb=raw.postprocess()
            with Image.fromarray(rgb) as img:img.save(self.o)
            self.finished.emit(self.row,self.o)
        except Exception as e:self.error.emit(self.row,str(e))
    def stop(self):pass
# In main.py, replace the existing LibreOfficeWorker class with this one

# In main.py, replace the existing LibreOfficeWorker class with this one

class LibreOfficeWorker(QObject):
    finished=pyqtSignal(int,str)
    error=pyqtSignal(int,str)
    
    def __init__(self,r,i,o,o_dir,p=None):
        super().__init__(p)
        self.row, self.input_path, self.output_path, self.output_dir = r, i, o, o_dir

    def run(self):
        # The wrapper script solution with a crucial encoding fix.
        batch_file_path = os.path.join(tempfile.gettempdir(), 'run_soffice.bat')

        try:
            soffice_path = shutil.which('soffice')
            if not soffice_path:
                raise FileNotFoundError("soffice.exe not found in system PATH.")

            command_args = [
                f'"{soffice_path}"',
                '--headless',
                '--convert-to', os.path.splitext(self.output_path)[1][1:],
                '--outdir', f'"{self.output_dir}"',
                f'"{self.input_path}"'
            ]
            
            # --- THE FINAL FIX: Force UTF-8 in the Batch File ---
            # 'chcp 65001' sets the command prompt's active code page to UTF-8.
            # This ensures that filenames with special characters (like ş, ı, ö, etc.)
            # are read correctly by LibreOffice.
            with open(batch_file_path, 'w', encoding='utf-8') as f:
                f.write('@echo off\n')
                f.write('chcp 65001 > nul\n') # Set code page to UTF-8 and hide its output
                f.write(' '.join(command_args))

            # Execute the batch file, which now correctly handles special characters.
            proc = subprocess.run(
                [batch_file_path],
                capture_output=True,
                text=True,
                timeout=60,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )

            # Check the results
            if proc.returncode == 0 and any(f.lower() == os.path.basename(self.output_path).lower() for f in os.listdir(self.output_dir)):
                self.finished.emit(self.row, self.output_path)
            else:
                stderr_log = f"--- STDERR ---\n{proc.stderr}\n" if proc.stderr else "No error output."
                stdout_log = f"--- STDOUT ---\n{proc.stdout}\n" if proc.stdout else ""
                error_message = f"LibreOffice process failed via wrapper (Code: {proc.returncode}).\n{stderr_log}{stdout_log}"
                self.error.emit(self.row, error_message)

        except FileNotFoundError:
            self.error.emit(self.row, "LibreOffice (soffice.exe) not found. Please use Help > Dependency Checker to verify it is in the system's PATH.")
        except subprocess.TimeoutExpired:
            self.error.emit(self.row, "LibreOffice took too long to respond and was terminated.")
        except Exception as e:
            self.error.emit(self.row, f"An unexpected error occurred while running the wrapper script: {str(e)}")
        finally:
            if os.path.exists(batch_file_path):
                os.remove(batch_file_path)

    def stop(self):
        pass
class SevenZipWorker(QObject):
    finished=pyqtSignal(int,str);error=pyqtSignal(int,str)
    def __init__(self,r,i,o,p=None):super().__init__(p);self.row,self.i,self.o=r,i,o
    def run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                subprocess.run(['7z','x',self.i,f'-o{temp_dir}','-y'],capture_output=True,text=True,check=True,creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=='win32' else 0)
                proc=subprocess.run(['7z','a',self.o,os.path.join(temp_dir,'*'),'-y'],capture_output=True,text=True,check=True,creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=='win32' else 0)
                self.finished.emit(self.row,self.o)
            except Exception as e:self.error.emit(self.row,str(e))
    def stop(self):pass
class PlaceholderWorker(QObject):
    error=pyqtSignal(int,str)
    def __init__(self,r,c,p=None):super().__init__(p);self.row,self.category=r,c
    def run(self):self.error.emit(self.row,f"Conversion for '{self.category}' is not implemented.")
class FFmpegGifWorker(QObject):
    """A specialized worker for high-quality GIF conversion using a two-pass method."""
    progress_updated = pyqtSignal(int, int)
    finished = pyqtSignal(int, str)
    error = pyqtSignal(int, str)

    def __init__(self, row, input_path, output_path, settings, parent=None):
        super().__init__(parent)
        self.row, self.input_path, self.output_path, self.settings = row, input_path, output_path, settings
        self.process = None

    def run(self):
        # Sensible defaults for GIFs
        fps = 15
        scale_width = 480
        palette_path = os.path.join(tempfile.gettempdir(), f"palette_{os.path.basename(self.input_path)}.png")

        try:
            # --- PASS 1: Generate Palette ---
            self.progress_updated.emit(self.row, 5) # Small initial progress
            palette_cmd = [
                'ffmpeg', '-i', self.input_path,
                '-vf', f'fps={fps},scale={scale_width}:-1:flags=lanczos,palettegen',
                '-y', palette_path
            ]
            # Use subprocess.run for this short, blocking operation
            subprocess.run(palette_cmd, capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)

            # --- PASS 2: Create GIF using Palette ---
            self.progress_updated.emit(self.row, 50) # Halfway point
            gif_cmd = [
                'ffmpeg', '-i', self.input_path, '-i', palette_path,
                '-lavfi', f'fps={fps},scale={scale_width}:-1:flags=lanczos[x];[x][1:v]paletteuse',
                '-y', self.output_path
            ]
            
            self.process = subprocess.Popen(gif_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
            
            duration = self.get_video_duration()
            for line in self.process.stdout:
                if duration and (match := re.search(r"time=(\d{2}):(\d{2}):(\d{2})\.\d{2}", line)):
                    h, m, s = map(int, match.groups())
                    current_time = h * 3600 + m * 60 + s
                    # Scale progress from 50 to 100 for the second pass
                    percentage = 50 + int((current_time / duration) * 50)
                    self.progress_updated.emit(self.row, min(100, percentage))

            self.process.wait()
            if self.process.returncode == 0:
                self.progress_updated.emit(self.row, 100)
                self.finished.emit(self.row, self.output_path)
            else:
                self.error.emit(self.row, f"FFmpeg GIF creation error (code {self.process.returncode})")

        except Exception as e:
            self.error.emit(self.row, str(e))
        finally:
            if os.path.exists(palette_path):
                os.remove(palette_path)

    def get_video_duration(self):
        try:
            return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', self.input_path], capture_output=True, text=True, check=True).stdout.strip())
        except:
            return None

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait()
# =============================================================================
# MAIN APPLICATION WINDOW
# =============================================================================

class FileConverterApp(QMainWindow, Ui_MainWindow):
    def __init__(self, app_instance): # Modified to accept the app instance
        super().__init__()
        self.app = app_instance # Store the app instance
        self.setupUi(self)
        self.setup_table()
        
        self.running_threads = {}
        
        self.settings_file = 'settings.json'
        self.settings = {}
        self.presets = {}
        self.load_settings()
        self.output_directory = self.settings.get('default_output_dir', None)
        
        # Apply theme on startup
        self.apply_theme(self.settings.get('theme', 'System Default'))
        
        self.setup_settings_panels()
        self.connect_signals()
        self.setAcceptDrops(True)
        self.update_settings_panel()
        
        if self.settings.get('show_setup_guide_on_launch', True):
            self.show_setup_guide(is_launch=True)


    def show_setup_guide(self, is_launch=False):
        """Shows the setup guide dialog."""
        dialog = SetupGuideDialog(self)
        # Only show the checkbox if it's the automatic launch popup
        dialog.dontRemindCheckBox.setVisible(is_launch)
        
        dialog.exec()
        
        # If this was the automatic launch popup, check and save the user's preference
        if is_launch:
            if dialog.get_dont_remind_state():
                self.settings['show_setup_guide_on_launch'] = False
                self.save_settings()

    def setup_settings_panels(self):
        self.image_settings_panel = ImageSettingsPanel()
        self.video_settings_panel = VideoSettingsPanel()
        self.audio_settings_panel = AudioSettingsPanel()

        self.settings_panels = {
            "image": self.image_settings_panel,
            "video": self.video_settings_panel,
            "audio": self.audio_settings_panel
        }
        for panel in self.settings_panels.values():
            self.settingsStack.addWidget(panel)
            panel.settings_changed.connect(self.on_settings_changed)

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f: self.settings = json.load(f)
            else:
                self.settings = {
                    'default_output_dir': '', 
                    'clear_list_on_complete': False,
                    'show_setup_guide_on_launch': True,
                    'save_to_source_dir': False,
                    'theme': 'System Default' # New setting with default
                }
            
            self.presets = self.settings.get('presets', {})
            if 'image' not in self.presets: self.presets['image'] = {}
            if 'video' not in self.presets: self.presets['video'] = {}
            if 'audio' not in self.presets: self.presets['audio'] = {}

        except:
            self.settings = {'default_output_dir': '', 'clear_list_on_complete': False, 'show_setup_guide_on_launch': True, 'save_to_source_dir': False, 'theme': 'System Default'}
            self.presets = {'image': {}, 'video': {}, 'audio': {}}

    def save_settings(self):
        try:
            # New: Add the presets dictionary back to the main settings before saving
            self.settings['presets'] = self.presets
            with open(self.settings_file, 'w') as f: json.dump(self.settings, f, indent=4)
        except: QMessageBox.warning(self, "Error", "Could not save settings.")
    def open_preferences_dialog(self):
        old_theme = self.settings.get('theme', 'System Default')
        dialog = PreferencesDialog(self.settings, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_settings = dialog.get_settings()
            self.settings.update(new_settings)
            self.save_settings()
            self.output_directory = self.settings.get('default_output_dir', None)

            # Instantly apply theme if it changed
            new_theme = self.settings.get('theme')
            if new_theme != old_theme:
                self.apply_theme(new_theme)

    def apply_theme(self, theme_name):
        """Applies the selected UI theme."""
        if theme_name == "Dark":
            qt_material.apply_stylesheet(self.app, theme='dark_teal.xml')
        elif theme_name == "Light":
            qt_material.apply_stylesheet(self.app, theme='light_blue.xml')
        else: # "System Default"
            # To revert to the system default, we apply an empty stylesheet,
            # effectively removing the custom one.
            self.app.setStyleSheet("")


    def setup_table(self):
        header = self.fileListTableWidget.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.Stretch)
        for i,w in enumerate([150,100,120,100,100]): self.fileListTableWidget.setColumnWidth(i+1, w)
        
        # New lines for enabling row reordering
        self.fileListTableWidget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.fileListTableWidget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

# In main.py, inside the FileConverterApp class

    def connect_signals(self):
        self.actionAdd_Files.triggered.connect(self.add_files)
        self.actionRemove_Selected.triggered.connect(self.remove_selected_files)
        self.actionConvert_All.triggered.connect(self.convert_all_files)
        self.actionCancel_All.triggered.connect(self.cancel_all_files)
        self.actionMerge_Selected.triggered.connect(self.merge_selected_files)
        self.actionPreferences.triggered.connect(self.open_preferences_dialog)
        self.actionAbout.triggered.connect(lambda: QMessageBox.about(self, "About", "File Converter v1.5"))
        self.actionSetup_Guide.triggered.connect(self.show_setup_guide)
        self.actionDependency_Checker.triggered.connect(self.show_dependency_checker) # New connection
        self.actionExit.triggered.connect(self.close)
        self.fileListTableWidget.itemSelectionChanged.connect(self.update_settings_panel)
        
        self.savePresetButton.clicked.connect(self.save_current_preset)
        self.deletePresetButton.clicked.connect(self.delete_selected_preset)
        self.presetComboBox.activated.connect(self.apply_selected_preset)
        
    def update_settings_panel(self):
        selected_rows = self.get_selected_rows()
        
        # Block signals to prevent infinite loops while we update the UI
        self.presetComboBox.blockSignals(True)
        self.presetComboBox.clear()
        
        if not selected_rows:
            self.settingsStack.setCurrentWidget(self.placeholderSettingsPage)
            self.presetGroupBox.setEnabled(False)
            self.presetComboBox.blockSignals(False)
            return
        
        first_row = selected_rows[0]
        item = self.fileListTableWidget.item(first_row, 0)
        
        if not item or "MERGE JOB" in item.text():
            self.settingsStack.setCurrentWidget(self.placeholderSettingsPage)
            self.presetGroupBox.setEnabled(False)
            self.presetComboBox.blockSignals(False)
            return

        file_path = item.text()
        file_ext = os.path.splitext(file_path)[1].lower()
        category = get_file_category(file_ext)

        if category in self.settings_panels:
            panel = self.settings_panels[category]
            settings = item.data(Qt.ItemDataRole.UserRole) or {}
            panel.load_settings(settings)
            self.settingsStack.setCurrentWidget(panel)
            self.presetGroupBox.setEnabled(True) # Enable preset box for valid types
            
            # Populate combobox with presets for this category
            self.presetComboBox.addItem("Apply a Preset...")
            if category in self.presets:
                for preset_name in sorted(self.presets[category].keys()):
                    self.presetComboBox.addItem(preset_name)
        else:
            self.settingsStack.setCurrentWidget(self.placeholderSettingsPage)
            self.presetGroupBox.setEnabled(False) # Disable for unsupported types

        self.presetComboBox.blockSignals(False)
    def save_current_preset(self):
        selected_rows = self.get_selected_rows()
        if not selected_rows: return
        
        item = self.fileListTableWidget.item(selected_rows[0], 0)
        if not item: return

        category = get_file_category(os.path.splitext(item.text())[1].lower())
        if category not in self.settings_panels:
            QMessageBox.warning(self, "Cannot Save Preset", "Presets are not available for this file type.")
            return

        current_settings = self.settings_panels[category].get_settings()
        
        preset_name, ok = QInputDialog.getText(self, "Save Preset", "Enter a name for this preset:")
        
        if ok and preset_name:
            if category not in self.presets:
                self.presets[category] = {}
            self.presets[category][preset_name] = current_settings
            self.save_settings()
            self.update_settings_panel() # Refresh the UI to show the new preset
            QMessageBox.information(self, "Success", f"Preset '{preset_name}' saved.")
    def on_settings_changed(self, new_settings):
        selected_rows = self.get_selected_rows()
        for row in selected_rows:
            item = self.fileListTableWidget.item(row, 0)
            if item:
                settings = item.data(Qt.ItemDataRole.UserRole) or {}
                settings.update(new_settings)
                item.setData(Qt.ItemDataRole.UserRole, settings)
    def delete_selected_preset(self):
        current_preset = self.presetComboBox.currentText()
        if not current_preset or current_preset == "Apply a Preset...":
            return

        selected_rows = self.get_selected_rows()
        if not selected_rows: return
        category = get_file_category(os.path.splitext(self.fileListTableWidget.item(selected_rows[0], 0).text())[1].lower())

        reply = QMessageBox.question(self, "Delete Preset", f"Are you sure you want to delete the preset '{current_preset}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if category in self.presets and current_preset in self.presets[category]:
                del self.presets[category][current_preset]
                self.save_settings()
                self.update_settings_panel() # Refresh the UI

    def apply_selected_preset(self, index):
        preset_name = self.presetComboBox.itemText(index)
        if not preset_name or preset_name == "Apply a Preset...":
            return

        selected_rows = self.get_selected_rows()
        if not selected_rows: return
        
        category = get_file_category(os.path.splitext(self.fileListTableWidget.item(selected_rows[0], 0).text())[1].lower())
        
        if category in self.presets and preset_name in self.presets[category]:
            preset_settings = self.presets[category][preset_name]
            
            # Apply settings to all selected rows of the same category
            for row in selected_rows:
                item = self.fileListTableWidget.item(row, 0)
                if not item: continue
                item_category = get_file_category(os.path.splitext(item.text())[1].lower())
                
                if item_category == category:
                    item.setData(Qt.ItemDataRole.UserRole, preset_settings)
            
            # Refresh the settings panel to show the applied settings
            self.update_settings_panel()
            self.statusBar().showMessage(f"Preset '{preset_name}' applied to {len(selected_rows)} items.", 3000)

        # Reset combo box to placeholder
        self.presetComboBox.setCurrentIndex(0)
    def get_selected_rows(self):
        return sorted(list(set(index.row() for index in self.fileListTableWidget.selectedIndexes())))

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls(): e.acceptProposedAction()
        else: e.ignore()

    def dropEvent(self, e):
        if e.mimeData().hasUrls():
            self.add_files_from_paths([url.toLocalFile() for url in e.mimeData().urls()])
            e.acceptProposedAction()
        else: e.ignore()

    def add_files_from_paths(self, paths):
        for path in paths:
            if os.path.isdir(path):
                for root, _, files in os.walk(path): [self.add_file_to_table(os.path.join(root,f)) for f in files]
            elif os.path.isfile(path): self.add_file_to_table(path)
    
    def on_conversion_finished(self, row, output_path):
        self.update_status(row, "Completed", "green")
        if (btn := self.fileListTableWidget.cellWidget(row, 4)): btn.setEnabled(True)
        open_btn = QPushButton("Open Folder"); open_btn.clicked.connect(partial(self.open_file_location, output_path))
        self.fileListTableWidget.setCellWidget(row, 5, open_btn)

    def on_conversion_error(self, row, msg):
        self.update_status(row, "Failed", "red")
        if (btn := self.fileListTableWidget.cellWidget(row, 4)): btn.setEnabled(True)
        if row in self.running_threads: self.running_threads[row][0].quit()
        QMessageBox.critical(self, "Error", f"Row {row + 1}: {msg}")

    def remove_thread_reference(self, row):
        if row in self.running_threads: del self.running_threads[row]
        if not self.running_threads:
            self.statusBar().showMessage("All tasks completed.", 5000)
            self.actionConvert_All.setEnabled(True); self.actionAdd_Files.setEnabled(True)
            # Re-enable row reordering now that all jobs are done
            self.fileListTableWidget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
            
            if self.settings.get('clear_list_on_complete', False): self.fileListTableWidget.setRowCount(0)

    def open_file_location(self, path):
        try:
            if sys.platform=="win32": subprocess.run(['explorer','/select,',os.path.normpath(path)])
            elif sys.platform=="darwin": subprocess.run(['open','-R',path])
            else: subprocess.run(['xdg-open',os.path.dirname(path)])
        except: QMessageBox.warning(self,"Error",f"Could not open path:\n{path}")
    
    def update_status(self, row, text, color="black"):
        if (item := self.fileListTableWidget.item(row, 2)):
            item.setText(text); item.setForeground(getattr(Qt.GlobalColor,color,Qt.GlobalColor.black))
    
    def update_progress(self, row, val):
        if (pb := self.fileListTableWidget.cellWidget(row, 3)): pb.setValue(val)

    def closeEvent(self, e):
        if self.running_threads:
            reply = QMessageBox.question(self,'Exit',"Jobs are running. Exit anyway?",
                QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)
            if reply==QMessageBox.StandardButton.Yes:
                self.cancel_all_files()
                e.accept()
            else:
                e.ignore()
        else:
            e.accept()
        
    def add_files(self):
        files,_=QFileDialog.getOpenFileNames(self,"Select Files","",f"All Supported Files ({' '.join(f'*{e}' for e in FLEXIBLE_CONVERSION_MAP.keys())})")
        if files: self.add_files_from_paths(files)

    def add_file_to_table(self, file_path, is_merge_job=False, out_path=""):
        row = self.fileListTableWidget.rowCount(); self.fileListTableWidget.insertRow(row)
        source_text = "MERGE JOB" if is_merge_job else file_path
        path_item = QTableWidgetItem(source_text); path_item.setFlags(path_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        if not is_merge_job:
            settings={'quality':95,'resize':"None",'video_bitrate':"Default",'remove_audio':False,'audio_bitrate':"Default"}
            path_item.setData(Qt.ItemDataRole.UserRole, settings)
        self.fileListTableWidget.setItem(row, 0, path_item)
        
        combo = QComboBox()
        if is_merge_job:
            combo.addItem(os.path.basename(out_path)); combo.setEnabled(False)
        elif (file_ext := os.path.splitext(file_path)[1].lower()) in FLEXIBLE_CONVERSION_MAP:
            for cat, fmts in FLEXIBLE_CONVERSION_MAP[file_ext].items():
                for f in fmts: combo.addItem(f".{f} ({cat})", userData=(cat,f))
        else: combo.addItem("Unsupported"); combo.setEnabled(False)
        self.fileListTableWidget.setCellWidget(row, 1, combo)

        status_item = QTableWidgetItem("Pending"); status_item.setFlags(status_item.flags()&~Qt.ItemFlag.ItemIsEditable)
        self.fileListTableWidget.setItem(row, 2, status_item)
        
        pb=QProgressBar();pb.setValue(0);pb.setTextVisible(True);self.fileListTableWidget.setCellWidget(row,3,pb)
        
        btn = QPushButton("Convert" if not is_merge_job else "Start"); btn.setEnabled(combo.isEnabled())
        if not is_merge_job: btn.clicked.connect(partial(self.convert_single_file,row))
        self.fileListTableWidget.setCellWidget(row, 4, btn)
        self.fileListTableWidget.setCellWidget(row, 5, QWidget())
      
    def remove_selected_files(self):
        rows = self.get_selected_rows()
        if not rows: return
        for row in reversed(rows):
            if row in self.running_threads:
                thread, worker = self.running_threads[row]; worker.stop(); thread.quit(); thread.wait()
            self.fileListTableWidget.removeRow(row)
        if self.fileListTableWidget.rowCount() == 0: self.update_settings_panel()

    def convert_single_file(self, row):
        out_dir = self.get_output_directory_for_conversion()
        if out_dir: self.start_conversion_for_row(row, out_dir)

    def convert_all_files(self):
        """Starts conversion for all pending files, getting one output directory for the batch."""
        rows=[r for r in range(self.fileListTableWidget.rowCount()) if self.fileListTableWidget.item(r,2).text()=="Pending"]
        if not rows: return QMessageBox.information(self,"No Files","No pending files to convert.")
        
        # Only ask for a directory if "save to source" is disabled
        output_dir = None
        if not self.settings.get('save_to_source_dir', False):
            output_dir = self.get_output_directory_for_conversion()
            if not output_dir: return # User cancelled

        # Disable UI elements including reordering
        self.actionConvert_All.setEnabled(False); self.actionAdd_Files.setEnabled(False)
        self.fileListTableWidget.setDragDropMode(QAbstractItemView.DragDropMode.NoDragDrop)

        for row in rows:
            self.start_conversion_for_row(row, output_dir) # Pass the single directory (or None)
# In main.py, replace the existing start_conversion_for_row method

    def start_conversion_for_row(self, row, batch_output_dir):
        path_item = self.fileListTableWidget.item(row,0); i_path=path_item.text()

        if self.settings.get('save_to_source_dir', False):
            final_output_dir = os.path.dirname(i_path)
        else:
            final_output_dir = batch_output_dir

        combo = self.fileListTableWidget.cellWidget(row, 1); o_cat, t_fmt = combo.currentData()
        i_ext = os.path.splitext(i_path)[1].lower(); i_cat = get_file_category(i_ext)
        base = os.path.splitext(os.path.basename(i_path))[0]
        o_path = os.path.join(final_output_dir, f"{base}.{t_fmt}")
        settings = path_item.data(Qt.ItemDataRole.UserRole)
        
        thread = QThread(); worker = None

        # --- UPDATED WORKER SELECTION LOGIC ---
        if i_ext == ".pdf" and t_fmt == "docx":
            worker = PdfToDocxWorker(row, i_path, o_path)
        elif i_ext == ".pdf" and t_fmt == "txt":
            worker = PdfToTextWorker(row, i_path, o_path)
        elif i_cat == "video" and t_fmt == "gif":
            worker = FFmpegGifWorker(row, i_path, o_path, settings)
        elif i_cat=="video" and o_cat=="audio": 
            worker=FFmpegWorker(row,i_path,o_path,"video_to_audio",settings)
        elif i_cat=="video" and o_cat=="image": 
            worker=FFmpegWorker(row,i_path,o_path,"video_to_image",settings)
        elif i_cat==o_cat:
            if i_cat in ["video","audio"]: 
                worker=FFmpegWorker(row,i_path,o_path,"default",settings)
            elif i_cat=="image": 
                worker = RawImageWorker(row, i_path, o_path, settings) if i_ext in RAW_EXTENSIONS else ImageWorker(row, i_path, o_path, settings)
            elif i_cat in ["document","presentation","spreadsheet"]: 
                worker=LibreOfficeWorker(row,i_path,o_path,final_output_dir)
            elif i_cat=="archive": 
                worker=SevenZipWorker(row,i_path,o_path)
        else: 
            worker = PlaceholderWorker(row, f"{i_cat} to {o_cat}")
        # --- END UPDATED LOGIC ---
        
        if worker:
            self.fileListTableWidget.setDragDropMode(QAbstractItemView.DragDropMode.NoDragDrop)
            
            worker.moveToThread(thread)
            thread.started.connect(worker.run)
            if hasattr(worker, 'progress_updated'): worker.progress_updated.connect(self.update_progress)
            worker.finished.connect(self.on_conversion_finished); worker.error.connect(self.on_conversion_error)
            worker.finished.connect(thread.quit); worker.error.connect(thread.quit)
            thread.finished.connect(worker.deleteLater); thread.finished.connect(thread.deleteLater)
            thread.finished.connect(lambda r=row: self.remove_thread_reference(r))
            self.running_threads[row]=(thread,worker); thread.start()
            self.update_status(row, "In Progress", "blue")
            if (btn := self.fileListTableWidget.cellWidget(row, 4)): btn.setEnabled(False)
    def merge_selected_files(self):
        rows = self.get_selected_rows(); paths = [self.fileListTableWidget.item(r, 0).text() for r in rows]
        if len(rows) < 2: return QMessageBox.warning(self, "Selection Error", "Please select at least two files to merge.")
        
        exts = {os.path.splitext(p)[1].lower() for p in paths}; cats = {get_file_category(e) for e in exts}
        if len(cats) > 1: return QMessageBox.warning(self, "Type Error", "All selected files must be of the same category (e.g., all videos).")
        category = cats.pop()
        
        if category == "document" and any(e != ".pdf" for e in exts): return QMessageBox.warning(self, "Type Error", "PDF merging only supports .pdf files.")
        if category not in ["document", "video"]: return QMessageBox.warning(self, "Unsupported", f"Merging is not supported for '{category}' files.")

        filters = {"document": "PDF Files (*.pdf)", "video": f"Video Files (*{' *'.join(VIDEO_EXTENSIONS)})"}
        out_path, _ = QFileDialog.getSaveFileName(self, "Save Merged File As", "", filters.get(category))
        if not out_path: return

        job_row = self.fileListTableWidget.rowCount(); self.add_file_to_table(file_path="", is_merge_job=True, out_path=out_path)
        self.update_status(job_row, "Merging...", "blue")
        
        thread=QThread(); worker=MergeWorker(job_row, paths, out_path, category)
        worker.moveToThread(thread); thread.started.connect(worker.run)
        worker.progress_updated.connect(self.update_progress); worker.finished.connect(self.on_conversion_finished)
        worker.error.connect(self.on_conversion_error); worker.finished.connect(thread.quit)
        thread.finished.connect(worker.deleteLater); thread.finished.connect(thread.deleteLater)
        thread.finished.connect(lambda r=job_row: self.remove_thread_reference(r))
        self.running_threads[job_row] = (thread, worker); thread.start()
        
    def cancel_all_files(self):
        for row, (thread, worker) in list(self.running_threads.items()):
            worker.stop(); thread.quit(); thread.wait(); self.update_status(row, "Cancelled", "orange")
            if (btn := self.fileListTableWidget.cellWidget(row, 4)): btn.setEnabled(True)
        self.running_threads.clear(); self.remove_thread_reference(-1)

    def get_output_directory_for_conversion(self):
        if (d:=self.settings.get('default_output_dir')) and os.path.isdir(d): return d
        d = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if d: self.statusBar().showMessage(f"Output for this task set to: {d}", 3000)
        return d        
    def show_dependency_checker(self):
        """Creates and shows the dependency checker dialog."""
        dialog = DependencyCheckerDialog(self)
        dialog.exec()
# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================
def main():
    """Main function to initialize and run the application."""
    app = QApplication(sys.argv)
    window = FileConverterApp(app_instance=app) # Pass the app instance
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()