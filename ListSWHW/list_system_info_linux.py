#!/usr/bin/env python3

import subprocess
import sys
import os
from shutil import which

def get_installed_software():
   """
   Retrieves a list of installed packages along with their version.
   It first checks for dpkg (Debian-based) and then rpm (RPM-based).
   Returns a list of tuples: (Package Name, Version)
   """
   software_list = []
   # Check if dpkg-query is available (Debian/Ubuntu)
   if which("dpkg-query") is not None:
       try:
           output = subprocess.check_output(
               ["dpkg-query", "-W", "-f=${Package}\t${Version}\n"],
               text=True
           )
           for line in output.splitlines():
               if line.strip():
                   parts = line.split("\t")
                   if len(parts) >= 2:
                       name, version = parts[0], parts[1]
                       software_list.append((name, version))
       except Exception as e:
           print(f"Error getting installed software via dpkg-query: {e}", file=sys.stderr)
   # Check if rpm is available (Fedora, RHEL, CentOS, etc.)
   elif which("rpm") is not None:
       try:
           output = subprocess.check_output(
               ["rpm", "-qa", "--queryformat", r'%{NAME}\t%{VERSION}-%{RELEASE}\n'],
               text=True
           )
           for line in output.splitlines():
               if line.strip():
                   parts = line.split("\t")
                   if len(parts) >= 2:
                       name, version = parts[0], parts[1]
                       software_list.append((name, version))
       except Exception as e:
           print(f"Error getting installed software via rpm: {e}", file=sys.stderr)
   else:
       print("Neither dpkg-query nor rpm is available to list installed software.", file=sys.stderr)
   return software_list

def get_hardware_drivers():
   """
   Retrieves a list of loaded kernel modules (hardware drivers) along with a version,
   if available. For each module from lsmod, modinfo is called to try to get the version.
   Returns a list of tuples: (Module Name, Version)
   """
   drivers = []
   try:
       lsmod_output = subprocess.check_output(["lsmod"], text=True)
       lines = lsmod_output.splitlines()
       # Skip the header line
       for line in lines[1:]:
           parts = line.split()
           if parts:
               module = parts[0]
               version = "Unknown"
               try:
                   modinfo_output = subprocess.check_output(
                       ["modinfo", module],
                       text=True,
                       stderr=subprocess.DEVNULL
                   )
                   for info_line in modinfo_output.splitlines():
                       if info_line.startswith("version:"):
                           version = info_line.split(":", 1)[1].strip()
                           break
               except Exception:
                   version = "Unknown"
               drivers.append((module, version))
   except Exception as e:
       print(f"Error listing hardware drivers using lsmod: {e}", file=sys.stderr)
   return drivers

def main():
   if os.name != 'posix':
       print("This script is intended for Linux (POSIX systems).", file=sys.stderr)
       sys.exit(1)
   software = get_installed_software()
   drivers = get_hardware_drivers()
   try:
       with open("system_info.txt", "w", encoding="utf-8") as f:
           f.write("Installed Software:\n")
           f.write("{:<40} {}\n".format("Name", "Version"))
           f.write("-" * 80 + "\n")
           for name, version in sorted(software, key=lambda x: x[0].lower()):
               f.write("{:<40} {}\n".format(name, version))
           f.write("\nInstalled Hardware Drivers (Loaded Kernel Modules):\n")
           f.write("{:<30} {}\n".format("Module Name", "Version"))
           f.write("-" * 80 + "\n")
           for module, version in sorted(drivers, key=lambda x: x[0].lower()):
               f.write("{:<30} {}\n".format(module, version))
       print("System information has been written to 'system_info.txt'.")
   except Exception as e:
       print(f"Error writing to file: {e}", file=sys.stderr)

if __name__ == "__main__":
   main()