# USB Storage Tester v2.0

A comprehensive USB storage device testing tool for drive analysis, speed testing, data integrity verification, and detailed reporting.

## Features

### 🔍 **Drive Detection**
- Automatic USB drive scanning and detection
- Hardware metadata extraction (model, serial, size)
- Cross-platform compatibility (Windows, Linux, macOS)
- Real-time drive information display

### ⚡ **Speed Testing**
- Sequential read/write performance measurement
- Random access speed testing
- Access time measurement
- Multiple test iterations for accuracy
- Real-time progress monitoring with ETA

### 🛡️ **Data Integrity Verification**
- Multiple test patterns (zeros, ones, alternating, random, incremental)
- SHA-256 hash verification for data accuracy
- Comprehensive error detection and reporting
- Pattern-based failure analysis

### 📊 **Capacity Testing**
- **Fast Capacity Verify**: Quick capacity validation (10% of free space)
- **Full Capacity Test**: Complete drive capacity utilization
- Real-time write and verify operations
- Performance metrics during capacity tests

### 🔍 **Comprehensive Testing**
- **Fast Mode**: Speed + Integrity + Fast Capacity (recommended)
- **Detailed Mode**: Speed + Integrity + Full Capacity (thorough)
- Complete drive analysis in single operation
- Automatic drive restoration after testing

### 📋 **Multi-Format Reporting**
- **JSON**: Machine-readable structured data
- **Text**: Human-readable comprehensive reports
- **CSV**: Spreadsheet-compatible summaries
- Detailed test logs with timestamps
- Executive summary with pass/fail status

### 🎨 **Enhanced User Interface**
- Colorized console output with status indicators
- Real-time progress bars with speed and ETA
- Interactive menu system
- Detailed drive selection interface
- Safety confirmations for destructive tests

## Installation

### Prerequisites
- Python 3.7 or higher
- Windows (recommended for full functionality)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Windows Dependencies
```bash
pip install pywin32 wmi colorama psutil
```

## Usage

### Start the Application
```bash
python usb_storage_tester.py
```

### Menu Options
1. **📊 Scan for USB drives** - Detect and display connected USB devices
2. **⚡ Run speed test only** - Measure read/write performance
3. **🛡️ Run data integrity test only** - Verify data accuracy with multiple patterns
4. **🚀 Run fast capacity verify only** - Quick capacity validation
5. **💾 Run full capacity test only** - Complete capacity utilization test
6. **🔍 Run comprehensive test fast** - All tests with fast capacity verify
7. **🔍 Run comprehensive test detailed** - All tests with full capacity test
8. **📋 View test logs** - Browse detailed execution logs
9. **📄 View test reports** - Access generated test reports
10. **🚪 Exit** - Close application

### Test Types Explained

#### Speed Test Only
- Sequential write/read performance
- Random access testing
- Access time measurement
- Non-destructive (safe for data)

#### Data Integrity Test Only
- Creates test files with different patterns
- Verifies data accuracy using SHA-256 hashing
- **⚠️ DESTRUCTIVE** - overwrites data on drive
- Automatic drive formatting after test

#### Fast Capacity Verify Only
- Tests 10% of available drive space
- Quick validation of drive capacity
- **⚠️ DESTRUCTIVE** - overwrites data on drive
- Automatic drive formatting after test

#### Full Capacity Test Only
- Tests 90% of available drive space
- Complete capacity validation
- **⚠️ DESTRUCTIVE** - overwrites data on drive
- Automatic drive formatting after test

#### Comprehensive Tests
- **Fast**: Speed + Integrity + Fast Capacity (recommended)
- **Detailed**: Speed + Integrity + Full Capacity (thorough)
- **⚠️ DESTRUCTIVE** - completely overwrites drive
- Automatic drive formatting after test

## Output Files

### Directory Structure
```
usb_storage_tester.py
├── usb_test_logs/          # Detailed execution logs
├── test_reports/           # Generated test reports
│   ├── *.json             # Machine-readable reports
│   ├── *.txt              # Human-readable reports
│   └── *.csv              # Spreadsheet summaries
└── temp_test_files/        # Temporary test files (preserved)
```

### Report Contents

#### JSON Report
- Complete test metadata and results
- Drive information and specifications
- Detailed performance metrics
- Error logs and timestamps

#### Text Report
- Executive summary with pass/fail status
- Detailed test results by category
- Performance metrics and analysis
- Error documentation

#### CSV Summary
- Key metrics in spreadsheet format
- Performance data for analysis
- Pass/fail status indicators

## Configuration

### Test Parameters
Edit `src/config.py` to customize:

```python
DEFAULT_BLOCK_SIZE_MB = 100        # Block size for capacity tests
SPEED_TEST_BLOCK_SIZE_MB = 10      # Block size for speed tests
SPEED_TEST_ITERATIONS = 5          # Number of speed test runs
DELETE_TEMP_FILES = False          # Keep test files for analysis
```

### File Management
- **DELETE_TEMP_FILES = False**: Preserves test files on USB drive
- **DELETE_TEMP_FILES = True**: Automatically removes test files

## Safety Features

### Destructive Test Protection
- Clear warnings for data-destroying tests
- Confirmation prompts requiring "YES" (case-sensitive)
- Drive information display before testing
- Automatic drive formatting after destructive tests

### Drive Restoration
- Automatic filesystem detection
- PowerShell-based drive formatting
- Restoration to original filesystem and label
- Clean drive state after testing

### Error Handling
- Graceful handling of USB disconnect/reconnect
- Comprehensive exception handling
- Detailed error logging
- Safe test interruption (Ctrl+C)

## Technical Details

### Drive Detection
- Windows: WMI (Windows Management Instrumentation)
- Cross-platform: psutil fallback
- Real-time USB device enumeration
- Hardware metadata extraction

### Performance Testing
- Direct USB drive I/O operations
- Multiple test iterations for accuracy
- Cache-bypassing techniques
- Statistical analysis of results

### Data Integrity
- Multiple test patterns for comprehensive validation
- Cryptographic hash verification (SHA-256)
- Immediate write-read verification
- Pattern-specific failure analysis

### Multi-Threading
- Configurable thread pool size
- Concurrent operations for efficiency
- Real-time progress monitoring
- Thread-safe error handling

## Troubleshooting

### Common Issues

#### "No USB drives detected"
- Ensure USB drives are properly connected
- Check drive letter assignment in Windows
- Try rescanning drives (option 1)

#### "Format operation failed"
- Run application as Administrator
- Manually format drive if needed
- Check drive write protection

#### High Speed Results
- Ensure tests write to USB drive (not temp directory)
- Check USB port type (2.0 vs 3.0+)
- Verify drive specifications

### Performance Tips
- Use USB 3.0+ ports for best performance
- Close other applications during testing
- Ensure adequate free space
- Test drives in good health condition

## System Requirements

### Minimum Requirements
- Python 3.7+
- 4GB RAM
- Windows 10+ (recommended)

### Recommended Setup
- Python 3.9+
- 8GB RAM
- Administrator privileges
- USB 3.0+ ports

## Contributing

Contributions welcome! Please submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under the **GPL-3.0 License**. See the [LICENSE](LICENSE)
file for details.

## Contact

For questions or feedback:
- **Email:** [dvidmakesthings@gmail.com](mailto:dvidmakesthings@gmail.com)
- **GitHub:** [DvidMakesThings](https://github.com/DvidMakesThings)

