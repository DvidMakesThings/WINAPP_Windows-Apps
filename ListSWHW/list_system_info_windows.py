import winreg
import subprocess
import csv
import io
import sys
import platform

def get_installed_software():
   """
   Reads several registry keys to enumerate installed software.
   Returns a list of tuples: (Software Name, Version)
   """
   software_list = []
   # List of (Registry Hive, Subkey Path) to check.
   registry_paths = [
       (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
       (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
       (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
   ]
   for hive, path in registry_paths:
       try:
           key = winreg.OpenKey(hive, path)
       except FileNotFoundError:
           continue  # This registry path might not exist on every system.
       num_subkeys = winreg.QueryInfoKey(key)[0]
       for i in range(num_subkeys):
           try:
               subkey_name = winreg.EnumKey(key, i)
               subkey = winreg.OpenKey(key, subkey_name)
               try:
                   name, _ = winreg.QueryValueEx(subkey, "DisplayName")
               except FileNotFoundError:
                   continue  # Skip entries with no DisplayName.
               try:
                   version, _ = winreg.QueryValueEx(subkey, "DisplayVersion")
               except FileNotFoundError:
                   version = "Unknown"
               software_list.append((name, version))
           except Exception:
               continue
   return software_list

def get_hardware_drivers():
   """
   Uses WMIC to query Win32_PnPSignedDriver for device driver information.
   Returns a list of tuples: (Device Name, Driver Version)
   """
   drivers = []
   try:
       # The /format:csv option outputs CSV data that we can easily parse.
       result = subprocess.run(
           ["wmic", "path", "Win32_PnPSignedDriver", "get", "DeviceName,DriverVersion", "/format:csv"],
           capture_output=True, text=True, shell=False
       )
       output = result.stdout.strip()
       if output:
           # Parse the CSV output.
           f = io.StringIO(output)
           reader = csv.DictReader(f)
           for row in reader:
               device = row.get("DeviceName", "").strip()
               version = row.get("DriverVersion", "").strip()
               if device:
                   drivers.append((device, version))
   except Exception:
       pass
   return drivers

def main():
   if platform.system() != "Windows":
       print("This script currently only supports Windows systems.")
       sys.exit(1)
   # Retrieve lists of installed software and hardware drivers.
   software = get_installed_software()
   drivers = get_hardware_drivers()
   # Write the output to a text file.
   try:
       with open("system_info.txt", "w", encoding="utf-8") as f:
           f.write("Installed Software:\n")
           f.write("{:<60} {}\n".format("Name", "Version"))
           f.write("-" * 80 + "\n")
           # Use a set to remove duplicates and sort by name.
           for name, version in sorted(set(software)):
               f.write("{:<60} {}\n".format(name, version))
           f.write("\nInstalled Hardware Drivers:\n")
           f.write("{:<60} {}\n".format("Device Name", "Driver Version"))
           f.write("-" * 80 + "\n")
           for device, version in sorted(set(drivers)):
               f.write("{:<60} {}\n".format(device, version))
       print("System information has been written to 'system_info.txt'.")
   except Exception as e:
       print(f"An error occurred while writing the file: {e}")

if __name__ == "__main__":
   main()