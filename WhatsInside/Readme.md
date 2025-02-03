# WhatIsInside

`WhatIsInside` is a Python script that lists all subfolders and files inside a specified parent folder. The output can be printed to the terminal or saved to a file.

## Usage

```sh
python whatisinside.py <parent_folder> [--file <filename>] [--save <save_location>]
```

### Arguments

- `<parent_folder>`: The parent folder to list contents of.
- `--file <filename>`: The filename to save the output to. If not specified, the output is only printed to the terminal.
- `--save <save_location>`: The location to save the output file. If not specified, the file is saved to the folder the script is running from.

### Examples

- Print to terminal only:
    ```sh
    python whatisinside.py C:\_GitHub
    ```
- Print to terminal and save to a file in the current directory:
    ```sh
    python whatisinside.py C:\_GitHub --file github.txt
    ```
- Print to terminal and save to a file in a specified directory:
    ```sh
    python whatisinside.py C:\_GitHub --file github.txt --save C:\temp
    ```
- Print help message:
    ```sh
    python whatisinside.py --help
    ```

## Requirements

- Python 3.x

## Installation

1. Clone the repository or download the script.
2. Ensure you have Python 3.x installed on your system.

## License

This project is licensed under the **GPL-3.0 License**. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback:
- **Email:** [s.dvid@hotmail.com](mailto:s.dvid@hotmail.com)
- **GitHub:** [DvidMakesThings](https://github.com/DvidMakesThings)