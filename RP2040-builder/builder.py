import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog

import customtkinter as ctk

# Function to convert a Windows path (e.g., "G:\path\to\file") to its WSL equivalent ("/mnt/g/path/to/file")
def windows_to_wsl_path(win_path):
    drive, path = os.path.splitdrive(win_path)
    if drive:
        drive_letter = drive[0].lower()
        return f"/mnt/{drive_letter}" + path.replace("\\", "/")
    return win_path.replace("\\", "/")

class CompilerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MicroPython Firmware Compiler")
        self.geometry("700x500")
        ctk.set_appearance_mode("dark")

        # Variables to store selected project files and output folder.
        self.project_files = []  # List of Windows file paths.
        self.output_path = ""

        # --- Project Files Selection ---
        self.project_frame = ctk.CTkFrame(self)
        self.project_frame.pack(pady=10, fill="x", padx=20)
        self.project_button = ctk.CTkButton(self.project_frame, text="Select Project Files", command=self.select_project_files)
        self.project_button.pack(side="left", padx=5)
        self.project_label = ctk.CTkLabel(self.project_frame, text="No project files selected")
        self.project_label.pack(side="left", padx=5)

        # --- Output Folder Selection ---
        self.output_frame = ctk.CTkFrame(self)
        self.output_frame.pack(pady=10, fill="x", padx=20)
        self.out_button = ctk.CTkButton(self.output_frame, text="Select Output Folder", command=self.select_output)
        self.out_button.pack(side="left", padx=5)
        self.out_label = ctk.CTkLabel(self.output_frame, text="No output folder selected")
        self.out_label.pack(side="left", padx=5)

        # --- Build Firmware Button ---
        self.build_button = ctk.CTkButton(
            self,
            text="Build Firmware",
            command=self.start_build,
            fg_color="#006400",    # Dark green.
            hover_color="#004d00"   # Darker green on hover.
        )
        self.build_button.pack(pady=20)

        # --- Terminal / Log Output ---
        self.log_text = ctk.CTkTextbox(self, width=650, height=250)
        self.log_text.pack(pady=10)


        # --- Progress Bar (at the bottom) ---
        self.progress_bar = ctk.CTkProgressBar(self, width=600)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10, side="bottom", fill="x")

    def log(self, message):
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.update_idletasks()

    def select_project_files(self):
        files = filedialog.askopenfilenames(title="Select Project Files")
        if files:
            self.project_files = list(files)
            self.project_label.configure(text=f"{len(self.project_files)} file(s) selected")

    def select_output(self):
        folder = filedialog.askdirectory(title="Select Output Folder for Firmware")
        if folder:
            self.output_path = folder
            self.out_label.configure(text=self.output_path)

    def start_build(self):
        if not self.project_files or not self.output_path:
            self.log("Error: Please select project files and an output folder.")
            return
        self.build_button.configure(state="disabled")
        threading.Thread(target=self.build_firmware, daemon=True).start()

    def build_firmware(self):
        try:
            self.log("Starting build process...")
            self.progress_bar.set(0)

            # Convert selected file paths to WSL paths.
            wsl_files = [windows_to_wsl_path(f) for f in self.project_files]
            files_str = " ".join(f'"{f}"' for f in wsl_files)
            self.log("Project files (WSL): " + files_str)

            # Convert output folder to WSL path.
            output_wsl = windows_to_wsl_path(self.output_path)
            self.log(f"Output folder (WSL): {output_wsl}")

            # === STEP 1: Copy project files into the frozen folder ===
            self.log("Copying project files into frozen folder...")
            copy_files_cmd = (
                "rm -rf ~/micropython/ports/rp2/frozen/* && "
                f"cp {files_str} ~/micropython/ports/rp2/frozen/"
            )
            result = subprocess.run(["wsl", "bash", "-c", copy_files_cmd],
                                    capture_output=True, text=True)
            if result.returncode != 0:
                self.log("Error copying project files:")
                self.log(result.stderr)
                self.build_button.configure(state="normal")
                return
            self.progress_bar.set(0.3)

            # === STEP 2: Build the firmware ===
            self.log("Starting firmware build...")
            build_cmd = "cd ~/micropython/ports/rp2 && make clean && make V=1"
            proc = subprocess.Popen(["wsl", "bash", "-c", build_cmd],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    text=True)
            for line in proc.stdout:
                self.log(line.strip())
            proc.wait()
            if proc.returncode != 0:
                self.log("Build failed!")
                self.build_button.configure(state="normal")
                return
            self.progress_bar.set(0.8)

            # === STEP 3: Copy the compiled firmware to the output folder ===
            self.log("Copying firmware to output folder...")
            firmware_path = "~/micropython/ports/rp2/build-RPI_PICO/firmware.uf2"
            copy_firmware_cmd = f"cp {firmware_path} {output_wsl}/"
            result = subprocess.run(["wsl", "bash", "-c", copy_firmware_cmd],
                                    capture_output=True, text=True)
            if result.returncode != 0:
                self.log("Error copying firmware:")
                self.log(result.stderr)
                self.build_button.configure(state="normal")
                return

            self.progress_bar.set(1.0)
            self.log("Firmware built and copied successfully!")
        except Exception as e:
            self.log("Exception occurred: " + str(e))
        finally:
            self.build_button.configure(state="normal")

if __name__ == "__main__":
    app = CompilerApp()
    app.mainloop()
