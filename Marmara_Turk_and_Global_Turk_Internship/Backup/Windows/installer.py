import os
import sys
import shutil
import ctypes
from win32com.client import Dispatch
import winreg
import subprocess
import json

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def create_shortcut(target_path, shortcut_path, working_dir):
    """Creates Windows shortcut"""
    try:
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target_path
        shortcut.WorkingDirectory = working_dir
        shortcut.save()
        return True
    except Exception as e:
        print(f"Shortcut creation error: {str(e)}")
        return False

def add_to_startup(exe_path):
    """Adds program to Windows startup"""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, 'BackupApp', 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Startup addition error: {str(e)}")
        return False

def create_key_file(key_content):
    """Creates .key file for USB drives"""
    try:
        downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        key_path = os.path.join(downloads_path, '.key')
        
        with open(key_path, 'w') as f:
            f.write(key_content)
        
        print(f"\n.key file created: {key_path}")
        print("You can backup by copying this file to your USB drive.")
        return True
    except Exception as e:
        print(f"Error creating .key file: {str(e)}")
        return False

def create_config(default_password):
    """Creates config file"""
    try:
        config = {
            "default_password": default_password
        }
        
        config_dir = os.path.join(os.getcwd(), 'config')
        os.makedirs(config_dir, exist_ok=True)
        
        config_path = os.path.join(config_dir, 'backup_config.json')
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        return True
    except Exception as e:
        print(f"Error creating config file: {str(e)}")
        return False

def compile_and_install():
    try:
        current_dir = os.getcwd()
        
        # Check required files
        if not os.path.exists('main.py'):
            print("Error: main.py file not found!")
            print("Please put installer.py in the same folder as main.py.")
            return False
        
        # Get required information from user
        print("\nEnter required information for installation:")
        print("-" * 40)
        
        # Default password
        default_password = input("Default backup password: ")
        if not default_password:
            print("Password cannot be empty!")
            return False
            
        # USB key password
        key_content = input("Key password for USB drives: ")
        if not key_content:
            print("Key password cannot be empty!")
            return False
        
        # Create config folder and config file
        print("\nCreating config file...")
        if not create_config(default_password):
            return False
            
        # Create .key file
        print("\nCreating key file...")
        if not create_key_file(key_content):
            return False
        
        # Create exe with PyInstaller
        print("\nCompiling program...")
        try:
            # Clean old build and dist folders
            for folder in ['build', 'dist']:
                if os.path.exists(folder):
                    shutil.rmtree(folder)
            
            # Get Python path
            python_exe = sys.executable
            
            # Icon check
            icon_path = os.path.join(current_dir, 'icon_backup.ico')
            if not os.path.exists(icon_path):
                print("Warning: icon_backup.ico not found. Using default icon.")
                command = f'"{python_exe}" -m PyInstaller --clean --noconfirm --onefile --windowed --add-data "config;config" main.py'
            else:
                command = f'"{python_exe}" -m PyInstaller --clean --noconfirm --onefile --windowed --icon="{icon_path}" --add-data "config;config" main.py'
            
            # Run PyInstaller
            print("Running compilation command...")
            print(f"Command: {command}")
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=current_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("PyInstaller hata detayları:")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                return False
                
            print("Program compiled successfully!")
            
        except Exception as e:
            print(f"Compilation error: {str(e)}")
            print("Error details:")
            import traceback
            traceback.print_exc()
            return False
            
        # Check if exe was created
        source_exe = os.path.join(current_dir, 'dist', 'main.exe')
        if not os.path.exists(source_exe):
            print(f"Error: Exe file could not be created: {source_exe}")
            print("PyInstaller output:")
            print(result.stdout)
            print("\nPyInstaller error output:")
            print(result.stderr)
            return False
        
        # Set installation directory
        install_dir = os.path.join(os.getenv('APPDATA'), 'BackupApp')
        
        # Clean old installation
        if os.path.exists(install_dir):
            try:
                shutil.rmtree(install_dir)
            except Exception as e:
                print(f"Could not remove old installation: {str(e)}")
                print("Please close the program and try again.")
                return False
        
        # Create installation directory
        os.makedirs(install_dir, exist_ok=True)
        
        # Copy exe file
        target_exe = os.path.join(install_dir, 'backup.exe')
        
        try:
            shutil.copy2(source_exe, target_exe)
            print("Program file copied")
        except Exception as e:
            print(f"Error copying exe: {str(e)}")
            return False
        
        # Copy config folder
        config_dir = os.path.join(current_dir, 'config')
        if os.path.exists(config_dir):
            try:
                if os.path.exists(os.path.join(install_dir, 'config')):
                    shutil.rmtree(os.path.join(install_dir, 'config'))
                shutil.copytree(config_dir, os.path.join(install_dir, 'config'))
                print("Config files copied")
            except Exception as e:
                print(f"Error copying config: {str(e)}")
                return False
        
        # Create shortcuts
        start_menu_dir = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs')
        shortcut_path = os.path.join(start_menu_dir, 'Backup App.lnk')
        
        if create_shortcut(target_exe, shortcut_path, install_dir):
            print("Start menu shortcut created")
        
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        desktop_shortcut = os.path.join(desktop_path, 'Backup App.lnk')
        
        if create_shortcut(target_exe, desktop_shortcut, install_dir):
            print("Desktop shortcut created")
        
        # Add to Windows startup option
        startup_choice = input("\nStart program with Windows? (Y/N): ")
        if startup_choice.lower() == 'y':
            if add_to_startup(target_exe):
                print("Program added to startup")
        
        print("\nInstallation completed successfully!")
        print(f"Program installed to: {install_dir}")
        
        # Option to start program
        run_now = input("\nRun program now? (Y/N): ")
        if run_now.lower() == 'y':
            os.startfile(target_exe)
        
        return True
        
    except Exception as e:
        print(f"\nError during installation: {str(e)}")
        return False

def main():
    print("Backup App Installation Wizard")
    print("-" * 30)
    
    # Admin rights check
    if not is_admin():
        print("Administrator rights required for installation...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        return
    
    # User confirmation
    print("\nThis program will:")
    print("1. Compile and create exe file")
    print("2. Install program to AppData folder")
    print("3. Add shortcuts to Start menu and desktop")
    print("4. Create .key file for USB drives")
    print("5. Optionally add to Windows startup")
    
    choice = input("\nDo you want to continue with installation? (Y/N): ")
    if choice.lower() != 'y':
        print("\nInstallation cancelled.")
        input("Press any key to exit...")
        return
    
    print("\nStarting installation...")
    if compile_and_install():
        print("\nInstallation completed!")
    else:
        print("\nInstallation failed!")
    
    input("\nPress any key to exit...")

if __name__ == "__main__":
    main() 