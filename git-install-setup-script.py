import os
import platform
import subprocess
import sys
import shutil
import json
import urllib.request
import urllib.error
import ctypes

def run_command(cmd, check=True, shell=False, input=None):
    try:
        subprocess.run(cmd, shell=shell, check=check, input=input, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

def is_git_installed():
    return shutil.which("git") is not None

def install_git_linux():
    try:
        with open("/etc/os-release") as f:
            os_release = f.read()
    except FileNotFoundError:
        print("Cannot detect Linux distribution.")
        return False

    distro = ""
    for line in os_release.splitlines():
        if line.startswith("ID="):
            distro = line.split("=")[1].strip().strip('"')
            break

    print(f"Detected Linux distro: {distro}")

    if distro in ["ubuntu", "debian", "kali", "linuxmint", "pop", "elementary", "parrot"]:
        run_command(["sudo", "apt", "update"])
        return run_command(["sudo", "apt", "install", "-y", "git"])
    elif distro in ["arch", "manjaro"]:
        return run_command(["sudo", "pacman", "-Sy", "--noconfirm", "git"])
    elif distro == "fedora":
        return run_command(["sudo", "dnf", "install", "-y", "git"])
    elif distro in ["centos", "rhel"]:
        return run_command(["sudo", "yum", "install", "-y", "git"])
    elif distro in ["opensuse", "suse"]:
        return run_command(["sudo", "zypper", "install", "-y", "git"])
    elif distro == "alpine":
        return run_command(["sudo", "apk", "add", "git"])
    elif distro == "void":
        return run_command(["sudo", "xbps-install", "-Sy", "git"])
    elif distro == "gentoo":
        return run_command(["sudo", "emerge", "--ask", "dev-vcs/git"])
    else:
        print(f"Unsupported Linux distro: {distro}")
        return False

def install_git_macos():
    if shutil.which("brew") is None:
        print("Homebrew is not installed. Please install it from https://brew.sh/")
        return False
    return run_command(["brew", "install", "git"])

def install_git_windows():
    if shutil.which("choco"):
        return run_command(["choco", "install", "git", "-y"])
    elif shutil.which("winget"):
        return run_command(["winget", "install", "--id", "Git.Git", "-e", "--source", "winget"])
    else:
        print("Neither Chocolatey nor Winget is installed. Please install Git manually from https://git-scm.com/")
        return False

def install_git():
    if is_git_installed():
        print("✅ Git is already installed.")
        return True

    print("❌ Git is not installed. Installing now...")

    system = platform.system()
    if system == "Linux":
        success = install_git_linux()
    elif system == "Darwin":
        success = install_git_macos()
    elif system == "Windows":
        success = install_git_windows()
    else:
        print(f"Unsupported OS: {system}")
        success = False

    if success:
        print("✅ Git installed successfully.")
    else:
        print("❌ Failed to install Git.")
    return success

def configure_git():
    print("\n🔧 Git Setup")
    name = input("Enter your Git user name: ").strip()
    email = input("Enter your Git email address (check if it is set up as private [format: 12345678+USERNAME@users.noreply.github.com]): ").strip()

    if name and email:
        run_command(["git", "config", "--global", "user.name", name])
        run_command(["git", "config", "--global", "user.email", email])
        print(f"\n✅ Git configured with:\n  Name : {name}\n  Email: {email}")
    else:
        print("⚠️  Git configuration skipped (name or email empty).")
        return

    run_command(["git", "config", "--global", "init.defaultBranch", "main"])
    run_command(["git", "config", "--global", "pull.rebase", "false"])

    if platform.system() == "Darwin":
        gitignore_global = os.path.expanduser("~/.gitignore_global")
        try:
            with open(gitignore_global, "a+") as f:
                f.seek(0)
                lines = f.read().splitlines()
                if ".DS_Store" not in lines:
                    f.write(".DS_Store\n")
                    print("🧹 Added .DS_Store to ~/.gitignore_global")
        except Exception as e:
            print(f"Failed to update ~/.gitignore_global: {e}")

        run_command(["git", "config", "--global", "core.excludesfile", gitignore_global])

def check_or_create_ssh_key():
    ssh_pub = os.path.expanduser("~/.ssh/id_ed25519.pub")
    ssh_priv = os.path.expanduser("~/.ssh/id_ed25519")

    if os.path.exists(ssh_pub):
        print("🔑 SSH key already exists at ~/.ssh/id_ed25519.pub")
        return ssh_priv, ssh_pub
    else:
        print("🔐 No SSH key found. Generating a new Ed25519 SSH key...")
        os.makedirs(os.path.dirname(ssh_priv), exist_ok=True)
        try:
            subprocess.run([
                "ssh-keygen", "-t", "ed25519", "-C", "", "-f", ssh_priv, "-N", ""
            ], check=True)
            print("✅ SSH key generated at ~/.ssh/id_ed25519")
            return ssh_priv, ssh_pub
        except Exception as e:
            print(f"❌ Failed to generate SSH key: {e}")
            return None, None

def is_admin():
    """Return True if script is running with admin rights on Windows."""
    if platform.system() != "Windows":
        return False
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def start_ssh_agent_and_add_key(ssh_priv_path):
    ssh_auth_sock = os.environ.get("SSH_AUTH_SOCK")

    # Check for gpg-agent fallback on Linux/macOS
    if not ssh_auth_sock or not os.path.exists(ssh_auth_sock):
        if platform.system() == "Linux":
            gpg_sock_path = os.path.expanduser("~/.gnupg/S.gpg-agent.ssh")
            if os.path.exists(gpg_sock_path):
                os.environ["SSH_AUTH_SOCK"] = gpg_sock_path
                print("✅ Using gpg-agent as SSH agent.")
                ssh_auth_sock = gpg_sock_path

    if ssh_auth_sock and os.path.exists(ssh_auth_sock):
        print("🔑 ssh-agent or gpg-agent is already running.")
    else:
        system = platform.system()
        if system == "Windows":
            print("🔄 Checking ssh-agent service status on Windows...")

            # Check if ssh-agent service is running
            try:
                result = subprocess.run(
                    ["powershell", "-Command",
                     "Get-Service ssh-agent | Select-Object -ExpandProperty Status"],
                    capture_output=True, text=True, check=True
                )
                status = result.stdout.strip()
                if status == "Running":
                    print("✅ ssh-agent service is already running.")
                else:
                    if not is_admin():
                        print("⚠️ Cannot start ssh-agent service because the script is NOT running as Administrator.")
                        print("   Please run this script as Administrator or start the 'ssh-agent' service manually:")
                        print("   > Start-Service ssh-agent  (in an Admin PowerShell)")
                        print("Skipping ssh-agent startup.")
                        return
                    else:
                        print("🔄 Starting ssh-agent service...")
                        subprocess.run(["powershell", "-Command",
                                        "Set-Service -Name ssh-agent -StartupType Automatic"], check=True)
                        subprocess.run(["powershell", "-Command",
                                        "Start-Service ssh-agent"], check=True)
                        print("✅ ssh-agent service started.")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to query/start ssh-agent service: {e}")
                print("Skipping ssh-agent startup.")
                return

            # On Windows ssh-agent service is running, but no SSH_AUTH_SOCK env var is set
            # ssh-agent uses named pipe, so just try ssh-add and catch errors below
        else:
            print("🔄 Starting ssh-agent...")
            result = subprocess.run(["ssh-agent", "-s"], stdout=subprocess.PIPE, text=True)
            output = result.stdout
            for line in output.splitlines():
                if line.startswith("SSH_AUTH_SOCK"):
                    sock = line.split(";")[0].split("=")[1]
                    os.environ["SSH_AUTH_SOCK"] = sock
                elif line.startswith("SSH_AGENT_PID"):
                    pid = line.split(";")[0].split("=")[1]
                    os.environ["SSH_AGENT_PID"] = pid
            print("✅ ssh-agent started.")

    print(f"➕ Adding SSH key {ssh_priv_path} to ssh-agent...")
    try:
        subprocess.run(["ssh-add", ssh_priv_path], check=True)
        print("✅ SSH key added to ssh-agent.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to add SSH key to ssh-agent: {e}")
        if system == "Windows":
            print("⚠️ On Windows, please ensure ssh-agent service is running and you have permissions.")
            print("   You can start it manually in PowerShell as Administrator with:")
            print("   > Start-Service ssh-agent")
            print("   Then run ssh-add manually or restart this script as Administrator.")

def upload_ssh_key_to_github(ssh_pub_path):
    print("\n🌐 GitHub Authentication")
    token = input("Enter your GitHub personal access token (with 'admin:public_key' scope): ").strip()

    try:
        with open(ssh_pub_path, "r") as f:
            pub_key = f.read().strip()
    except Exception as e:
        print(f"❌ Failed to read SSH public key: {e}")
        return False

    key_title = f"Key added on {platform.node()}"

    data = {
        "title": key_title,
        "key": pub_key
    }

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }

    req = urllib.request.Request(
        "https://api.github.com/user/keys",
        data=json.dumps(data).encode(),
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status == 201:
                print("✅ SSH key uploaded to GitHub successfully.")
                return True
            else:
                print(f"❌ Failed to upload SSH key to GitHub. Status code: {resp.status}")
                return False
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP error while uploading SSH key: {e.read().decode()}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    if not install_git():
        print("Cannot proceed without Git installed. Exiting.")
        sys.exit(1)

    configure_git()

    ssh_priv, ssh_pub = check_or_create_ssh_key()
    if not ssh_priv or not ssh_pub:
        print("SSH key setup failed. Exiting.")
        sys.exit(1)

    start_ssh_agent_and_add_key(ssh_priv)

    upload_ssh_key_to_github(ssh_pub)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        while True:
            try:
                input("\nPress [Enter] to exit...")
                sys.exit(0)
            except KeyboardInterrupt:
                exit()