# Differential Pair Length Checker

Differential Pair Length Checker is a GUI application built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) that analyzes a text file (for example, an Eagle design signal report) containing a list of signals and their lengths (in mm). It filters signals ending with `_N` or `_P`, groups them into differential pairs based on their common base name, and checks each pair’s length matching against interface-specific tolerances.

For grouping, the “base name” is extracted by taking the token immediately before the trailing channel indicator. However, if the signal name contains an expansion (i.e. more than two tokens), the grouping key is built from the first token (the expansion) and the token immediately before the trailing channel indicator. This allows signals like `HDMI0_TDMS0_N` and `HDMI1_TDMS0_N` to be grouped separately while still allowing for proper interface recommendation.

When you click **Run Check**, the application verifies:
- That each differential pair’s two channels match within the assigned interface’s pair tolerance.
- If more than one pair is assigned to an interface (and if an inter‑pair tolerance is defined), that the average lengths of the pairs are sufficiently matched.
- Additionally, for HDMI 1.4 the TMDSCK (clock) pair is checked to ensure it is shorter than the data lane pairs.

Tolerances (converted from mils to mm; 1 mil = 0.0254 mm) are defined in the `INTERFACE_TOLERANCES` dictionary.

## Features

- **Signal Grouping:**  
    - Groups signals based on the token immediately before the trailing channel indicator.
    - Supports grouping with an expansion prefix (e.g. `HDMI0_TDMS0_N` and `HDMI1_TDMS0_N` are grouped separately).

- **Interface Assignment:**  
    - Each differential pair can be assigned an interface (e.g. USB 3.0, PCIe Gen4, etc.) via a dropdown.
    - Automatic interface recommendations are provided based on the signal name grouping.

- **Length Checking:**  
    - Checks that each pair’s two channels match within the assigned interface’s pair tolerance.
    - For interfaces with multiple pairs (and a defined inter‑pair tolerance), it verifies that the average lengths are sufficiently matched.
    - For HDMI 1.4, the TMDSCK (clock) pair is validated to be shorter than the data lane pairs.

- **Markdown Report Generation:**  
    - Generates a detailed Markdown report including input file details, date/time, overall status, and a formatted table of results with colored PASS/FAIL statuses.

## Supported Interfaces and Tolerances

- **USB 2.0:** Pair tolerance ±150 mil (≈3.81 mm)
- **USB 3.0:** Pair tolerance ±2 mil (≈0.051 mm), Inter‑pair tolerance ±5 mil (≈0.127 mm)
- **USB 3.1/3.2:** Pair tolerance ±2 mil, Inter‑pair tolerance ±5 mil
- **USB4 / Thunderbolt 3:** Pair tolerance ±1 mil (≈0.0254 mm), Inter‑pair tolerance ±3 mil (≈0.0762 mm)
- **Ethernet 100BASE-TX:** Pair tolerance ±50 mil, Inter‑pair tolerance ±100 mil
- **Ethernet 1000BASE-T:** Pair tolerance ±5 mil, Inter‑pair tolerance ±10 mil
- **Ethernet 10GBASE-T:** Pair tolerance ±2 mil, Inter‑pair tolerance ±5 mil
- **HDMI 1.4:** Pair tolerance ±5 mil, Inter‑pair tolerance ±20 mil  
    *Note: For HDMI 1.4, the TMDSCK (clock) pair must be shorter than the data lanes.*
- **HDMI 2.0:** Pair tolerance ±2 mil, Inter‑pair tolerance ±10 mil
- **DisplayPort 1.2:** Pair tolerance ±3 mil, Inter‑pair tolerance ±10 mil
- **DisplayPort 2.0:** Pair tolerance ±2 mil, Inter‑pair tolerance ±5 mil
- **PCIe Gen1/2:** Pair tolerance ±5 mil, Inter‑pair tolerance ±20 mil
- **PCIe Gen3:** Pair tolerance ±2 mil, Inter‑pair tolerance ±10 mil
- **PCIe Gen4:** Pair tolerance ±1 mil, Inter‑pair tolerance ±5 mil
- **PCIe Gen5:** Pair tolerance ±0.5 mil, Inter‑pair tolerance ±2 mil
- **SATA 3.0:** Pair tolerance ±5 mil, Inter‑pair tolerance ±20 mil
- **SAS 12G:** Pair tolerance ±2 mil, Inter‑pair tolerance ±5 mil
- **MIPI DSI/CSI:** Pair tolerance ±2 mil, Inter‑pair tolerance ±10 mil
- **LVDS:** Pair tolerance ±5 mil, Inter‑pair tolerance ±20 mil

## Directory Structure

```
diffpaircheck/
├── __init__.py
├── config.py
├── utils.py
├── parser.py
├── markdown_exporter.py
├── app.py
└── main.py
```

- **config.py:** Contains configuration settings and constants.
- **utils.py:** Utility functions used throughout the project.
- **parser.py:** Implements file parsing logic to read the signal report and group differential pairs.
- **markdown_exporter.py:** Implements the Markdown report generation functionality.
- **app.py:** Contains the main GUI application class built with CustomTkinter.
- **main.py:** The entry point to run the application.

## Installation

     Make sure you have Python 3.6+ installed. Then install the required package:

     ```bash
     pip install customtkinter
     ```

     > **Note:** CustomTkinter supports dark mode and is required for this application.

## Usage

Run the application by executing the following command from the repository's root directory:

```bash
python -m diffpaircheck.main
```

Alternatively, adjust your `PYTHONPATH` to include the parent directory of `diffpaircheck` and run:

```bash
python diffpaircheck/main.py
```

## Application Workflow

1. **Load Signal File:**  
     Click the **Load Signal File** button to browse and select a text file containing signal data.

2. **Assign Interfaces:**  
     Once the file is loaded, the left panel displays the signal pairs. Use the dropdown menus to assign an interface to each pair.

3. **Run Check:**  
     Click the **Run Check** button (displayed in dark green, with a darker green hover effect) to perform the length matching checks. The results are displayed in a formatted, scrollable table in the right panel.

4. **Save Report:**  
     Click the **Save Report** button to save the generated Markdown report. The report includes:
     - Input file name
     - Date/Time of the check
     - Overall PASS/FAIL status (displayed in large, colored text)
     - A detailed table with columns for Group, Pair, Diff (mm), Tolerance (mm), and Status (colored green for PASS and red for FAIL)

## Example Markdown Report

Below is an example of a generated Markdown report:

| **Group** | **Pair** | **Diff (mm)** | **Tolerance (mm)** | **Status** |
| --- | --- | --- | --- | --- |
| **Ethernet 1000BASE-T (ETH)** | ----- |  |  |  |
|  | ETH_TX4_N / ETH_TX4_P | 0.471 | ±0.127 | <span style="color:red">FAIL</span> |
|  | ETH_TX3_N / ETH_TX3_P | 0.528 | ±0.127 | <span style="color:red">FAIL</span> |
|  | ETH_TX2_N / ETH_TX2_P | 0.581 | ±0.127 | <span style="color:red">FAIL</span> |
|  | ETH_TX1_N / ETH_TX1_P | 0.607 | ±0.127 | <span style="color:red">FAIL</span> |
|  | **Inter‑Pair** | 12.271 | ±0.254 | <span style="color:red">FAIL</span> |
| **HDMI 1.4 (HDMI0)** | ----- |  |  |  |
|  | HDMI0_TDMSCK_N / HDMI0_TDMSCK_P | 0.562 | ±0.127 | <span style="color:red">FAIL</span> |
|  | HDMI0_TDMS0_N / HDMI0_TDMS0_P | 0.485 | ±0.127 | <span style="color:red">FAIL</span> |
|  | HDMI0_TDMS1_N / HDMI0_TDMS1_P | 0.408 | ±0.127 | <span style="color:red">FAIL</span> |
|  | HDMI0_TDMS2_N / HDMI0_TDMS2_P | 0.508 | ±0.127 | <span style="color:red">FAIL</span> |
|  | **Inter‑Pair** | 9.342 | ±0.508 | <span style="color:red">FAIL</span> |
|  | HDMI0_TDMSCK_N / HDMI0_TDMSCK_P (TMDSCK) | 43.453 |  | <span style="color:green">PASS</span> |

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the GPL3 License. See the LICENSE file for details.

## Contact

For questions or feedback, email s.dvid@hotmail.com or visit [GitHub](https://github.com/DvidMakesThings).