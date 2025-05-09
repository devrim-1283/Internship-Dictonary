#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

def install():
    try:
        # Get user's home directory
        home = Path.home()
        
        # Create application directory
        app_dir = home / '.local/share/backup-app'
        app_dir.mkdir(parents=True, exist_ok=True)
        
        # Create bin directory if not exists
        bin_dir = home / '.local/bin'
        bin_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy program files
        current_dir = Path(__file__).parent
        required_files = ['main.py', 'backup_ui.py']
        optional_files = ['icon_backup.png']
        
        # Copy required files
        for file in required_files:
            if not (current_dir / file).exists():
                print(f"Error: Required file {file} not found!")
                return
            shutil.copy2(current_dir / file, app_dir / file)
        
        # Copy optional files if they exist
        for file in optional_files:
            if (current_dir / file).exists():
                shutil.copy2(current_dir / file, app_dir / file)
        
        # Create config and log directories
        config_dir = app_dir / 'config'
        config_dir.mkdir(exist_ok=True)
        
        # Create executable script in bin
        bin_file = bin_dir / 'backup'
        with open(bin_file, 'w') as f:
            f.write(f"""#!/usr/bin/env python3
import sys
import os
sys.path.append('{app_dir}')
os.chdir('{app_dir}')
from main import main
if __name__ == '__main__':
    main()
""")
        
        # Make bin file executable
        bin_file.chmod(0o755)
        
        # Create .desktop file
        icon_path = app_dir / 'icon_backup.jpg'
        if not icon_path.exists():
            icon_path = 'system-backup'  # Use system backup icon if custom icon not found
            
        desktop_entry = f"""[Desktop Entry]
Name=Backup
Comment=Backup your files
Exec={bin_file}
Icon={icon_path}
Terminal=false
Type=Application
Categories=Utility;
"""
        
        # Save .desktop file
        desktop_file = home / '.local/share/applications/backup.desktop'
        with open(desktop_file, 'w') as f:
            f.write(desktop_entry)
        
        # Make .desktop file executable
        desktop_file.chmod(0o755)
        
        print("Installation completed successfully!")
        print(f"Application installed to: {app_dir}")
        print(f"Executable created at: {bin_file}")
        print(f"Desktop entry created at: {desktop_file}")
        print("\nYou may need to log out and log back in for the changes to take effect.")
        print("You can run the program by typing 'backup' in terminal or from the application menu.")

    except Exception as e:
        print(f"Installation failed: {str(e)}")

if __name__ == "__main__":
    install() 