# diffpaircheck/app.py

import os
import tkinter as tk
from tkinter import filedialog, messagebox
import datetime
import customtkinter as ctk

from diffpaircheck import config, utils, parser, markdown_exporter

class DiffPairApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Differential Pair Length Checker")
        self.geometry("1500x700")
        self.resizable(False, False)
        self.last_report = None  # Store generated Markdown report text
        self.input_filename = "N/A"
        
        # Data containers.
        self.pairs = []      # List of dicts (each with keys "key", "N", "P")
        self.pair_vars = []  # List of tk.StringVar for interface assignment

        # Left frame: fixed width 700 px.
        self.left_frame = ctk.CTkFrame(self, width=700)
        self.left_frame.pack(side="left", fill="both", expand=False, padx=10, pady=5)
        self.left_frame.pack_propagate(False)

        # Right frame: fixed width 800 px.
        self.right_frame = ctk.CTkFrame(self, width=800)
        self.right_frame.pack(side="right", fill="both", expand=False, padx=10, pady=5)
        self.right_frame.pack_propagate(False)

        # --- Left Frame: File load controls and Signal Pair Selector ---
        self.top_frame = ctk.CTkFrame(self.left_frame, height=50)
        self.top_frame.pack(fill="x", padx=5, pady=5)
        self.load_button = ctk.CTkButton(self.top_frame, text="Load Signal File", command=self.load_file)
        self.load_button.pack(side="left", padx=5, pady=5)
        self.file_label = ctk.CTkLabel(self.top_frame, text="No file loaded", anchor="w")
        self.file_label.pack(side="left", padx=5, pady=5)

        self.scrollable_frame = ctk.CTkScrollableFrame(self.left_frame)
        self.scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Button Frame: 4-column layout (empty, Run Check, Save Report, empty) ---
        self.button_frame = ctk.CTkFrame(self.left_frame, height=50)
        self.button_frame.pack(fill="x", padx=5, pady=5)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=0)
        self.button_frame.columnconfigure(2, weight=0)
        self.button_frame.columnconfigure(3, weight=1)
        self.run_button = ctk.CTkButton(
            self.button_frame,
            text="Run Check",
            command=self.run_check,
            fg_color="#006400",      # Dark green
            hover_color="#004d00"      # Even darker green on hover
        )
        self.run_button.grid(row=0, column=1, padx=5, pady=5)
        self.save_button = ctk.CTkButton(
            self.button_frame,
            text="Save Report",
            command=self.save_report
        )
        self.save_button.grid(row=0, column=2, padx=5, pady=5, sticky="e")

        # --- Right Frame: Results Table (in a scrollable frame) ---
        self.result_frame = ctk.CTkScrollableFrame(self.right_frame)
        self.result_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Signal File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not file_path:
            return
        self.input_filename = os.path.basename(file_path)
        self.file_label.configure(text=self.input_filename)
        try:
            self.pairs = parser.parse_file(file_path)
            self.populate_pairs()
        except Exception as e:
            messagebox.showerror("File Load Error", f"Error loading file: {e}")

    def populate_pairs(self):
        # Clear the left scrollable frame.
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.pair_vars = []
        row = 0
        header_n = ctk.CTkLabel(self.scrollable_frame, text="Channel _N", width=200, anchor="w")
        header_n.grid(row=row, column=0, padx=5, pady=5)
        header_p = ctk.CTkLabel(self.scrollable_frame, text="Channel _P", width=200, anchor="w")
        header_p.grid(row=row, column=1, padx=5, pady=5)
        header_iface = ctk.CTkLabel(self.scrollable_frame, text="Interface", width=200, anchor="w")
        header_iface.grid(row=row, column=2, padx=5, pady=5)
        row += 1
        for pair in self.pairs:
            if pair.get("N"):
                full_name_n, _ = pair["N"]
                text_n = full_name_n
            else:
                text_n = "Missing"
            label_n = ctk.CTkLabel(self.scrollable_frame, text=text_n, anchor="w", width=200)
            label_n.grid(row=row, column=0, padx=5, pady=2, sticky="w")
            if pair.get("P"):
                full_name_p, _ = pair["P"]
                text_p = full_name_p
            else:
                text_p = "Missing"
            label_p = ctk.CTkLabel(self.scrollable_frame, text=text_p, anchor="w", width=200)
            label_p.grid(row=row, column=1, padx=5, pady=2, sticky="w")
            rec = utils.recommend_interface_for_pair(pair)
            var = tk.StringVar(value=rec)
            dropdown = ctk.CTkOptionMenu(self.scrollable_frame, variable=var, values=config.INTERFACE_OPTIONS, width=200)
            dropdown.grid(row=row, column=2, padx=5, pady=2, sticky="w")
            self.pair_vars.append(var)
            row += 1

    def run_check(self):
        result_rows = []
        assignments = {}  # key: (assigned_iface, expansion); value: list of complete pairs
        incomplete_rows = []  # for pairs missing one channel
        for idx, pair in enumerate(self.pairs):
            assigned_iface = self.pair_vars[idx].get()
            if assigned_iface == "Unassigned":
                continue
            key = pair["key"]
            expansion = key.split("_")[0] if "_" in key else None
            group_key = (assigned_iface, expansion)
            if pair.get("N") and pair.get("P"):
                if group_key not in assignments:
                    assignments[group_key] = []
                assignments[group_key].append(pair)
            else:
                grp = f"{assigned_iface}" if not expansion else f"{assigned_iface} ({expansion})"
                incomplete_rows.append((grp, f"Incomplete pair in {pair['key']}", "", "", "FAIL"))
        
        # Process each group (sorted by interface and expansion)
        for group_key in sorted(assignments.keys(), key=lambda x: (x[0], x[1] or "")):
            assigned_iface, expansion = group_key
            grp = f"{assigned_iface}" if not expansion else f"{assigned_iface} ({expansion})"
            result_rows.append((grp, "-----", "", "", ""))
            pair_tol = config.INTERFACE_TOLERANCES[assigned_iface]["pair_tol"]
            inter_pair_tol = config.INTERFACE_TOLERANCES[assigned_iface]["inter_pair_tol"]
            pair_avgs = []
            for pair in assignments[group_key]:
                n_full, n_length = pair["N"]
                p_full, p_length = pair["P"]
                diff = abs(n_length - p_length)
                avg = (n_length + p_length) / 2.0
                pair_avgs.append(avg)
                status = "PASS" if diff <= pair_tol else "FAIL"
                pair_label = f"{n_full} / {p_full}"
                result_rows.append(("", pair_label, f"{diff:.3f}", f"±{pair_tol:.3f}", status))
            if inter_pair_tol is not None and len(pair_avgs) > 1:
                min_avg = min(pair_avgs)
                max_avg = max(pair_avgs)
                inter_diff = max_avg - min_avg
                inter_status = "PASS" if inter_diff <= inter_pair_tol else "FAIL"
                result_rows.append(("", "Inter‑Pair", f"{inter_diff:.3f}", f"±{inter_pair_tol:.3f}", inter_status))
            if assigned_iface == "HDMI 1.4":
                clock_pairs = []
                data_avgs = []
                for pair in assignments[group_key]:
                    pk = pair["key"].upper()
                    n_full, n_length = pair["N"]
                    p_full, p_length = pair["P"]
                    avg = (n_length + p_length) / 2.0
                    if "TMDSCK" in pk or "TDMSCK" in pk:
                        clock_pairs.append((pair, avg))
                    elif "TMDS" in pk or "TDMS" in pk:
                        data_avgs.append(avg)
                if clock_pairs and data_avgs:
                    min_data_avg = min(data_avgs)
                    for pair, clock_avg in clock_pairs:
                        status = "PASS" if clock_avg < min_data_avg else "FAIL"
                        pair_label = f"{pair['N'][0]} / {pair['P'][0]} (TMDSCK)"
                        result_rows.append(("", pair_label, f"{clock_avg:.3f}", "", status))
        result_rows.extend(incomplete_rows)
        if not result_rows:
            result_rows.append(("", "No pairs assigned to any interface.", "", "", ""))
        
        # Clear previous results.
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        headers = ["Group", "Pair", "Diff (mm)", "Tolerance (mm)", "Status"]
        col_widths = [150, 250, 60, 60, 60]
        header_font = ("TkDefaultFont", 12, "bold")
        cell_font = ("TkDefaultFont", 10)
        for col, (htext, width) in enumerate(zip(headers, col_widths)):
            label = ctk.CTkLabel(self.result_frame, text=htext, width=width, anchor="w", font=header_font)
            label.grid(row=0, column=col, padx=2, pady=2)
        for row_idx, row_values in enumerate(result_rows, start=1):
            for col_idx, value in enumerate(row_values):
                if col_idx == len(row_values) - 1 and str(value).upper() in ["PASS", "FAIL"]:
                    txt_color = "green" if str(value).upper() == "PASS" else "red"
                    label = ctk.CTkLabel(self.result_frame, text=value, width=col_widths[col_idx],
                                          anchor="center", text_color=txt_color, font=cell_font)
                else:
                    label = ctk.CTkLabel(self.result_frame, text=value, width=col_widths[col_idx],
                                          anchor="w", font=cell_font)
                label.grid(row=row_idx, column=col_idx, padx=2, pady=2)
        
        overall_status = "PASS"
        for row in result_rows:
            if str(row[-1]).strip().upper() == "FAIL":
                overall_status = "FAIL"
                break
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_report = markdown_exporter.generate_markdown_report(result_rows, self.input_filename, overall_status, timestamp)

    def save_report(self):
        if not self.last_report:
            messagebox.showwarning("No Report", "There is no report to save. Please run the check first.")
            return
        save_path = filedialog.asksaveasfilename(
            title="Save Report",
            defaultextension=".md",
            filetypes=[("Markdown Files", "*.md"), ("All Files", "*.*")]
        )
        if not save_path:
            return
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(self.last_report)
            messagebox.showinfo("Report Saved", f"Report saved successfully to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving report: {e}")

if __name__ == "__main__":
    app = DiffPairApp()
    app.mainloop()
