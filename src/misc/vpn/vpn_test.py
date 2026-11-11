
import subprocess
import ctypes
import sys

CLI = r"C:\Program Files (x86)\ExpressVPN\services\ExpressVPN.CLI.exe"

def is_admin():
    return ctypes.windll.shell32.IsUserAnAdmin() != 0

def vpn(*args):
    command = subprocess.list2cmdline([CLI, *args])

    if is_admin():
        result = subprocess.run(
            [CLI, *args],
            capture_output=True,
            text=True
        )
        print(result.stdout or result.stderr)
        return result.returncode

    # Relaunch this command with administrator privileges
    print("Requesting administrator permission...")

    result = ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        CLI,
        subprocess.list2cmdline(args),
        None,
        1
    )

    if result <= 32:
        print("Could not launch CLI. Error:", result)
        return result

    return 0

if __name__ == "__main__":
    vpn("activation_status")
    vpn("status")
