import os
import platform
import subprocess
import sys
import shutil
import json
import urllib.request
import urllib.error

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
    email = input("Enter your Git email address: ").strip()

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

def start_ssh_agent_and_add_key(ssh_priv_path):
    ssh_auth_sock = os.environ.get("SSH_AUTH_SOCK")
    if ssh_auth_sock and os.path.exists(ssh_auth_sock):
        print("🔑 ssh-agent is already running.")
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

def upload_ssh_key_to_github(ssh_pub_path):
    print("\n🌐 Upload SSH key to GitHub")
    token = input("Enter your GitHub Personal Access Token (with `admin:public_key` scope): ").strip()
    if not token:
        print("⚠️  Token not provided. Skipping GitHub upload.")
        return

    title = input("Enter a title for this SSH key (e.g. 'My Laptop'): ").strip()
    if not os.path.exists(ssh_pub_path):
        print(f"❌ SSH key file not found: {ssh_pub_path}")
        return

    with open(ssh_pub_path, "r") as f:
        key_content = f.read().strip()

    data = json.dumps({
        "title": title,
        "key": key_content
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.github.com/user/keys",
        data=data,
        method="POST",
        headers={
            "Authorization": f"token {token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json"
        }
    )

    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 201:
                print("✅ SSH key successfully uploaded to GitHub.")
            else:
                print(f"Unexpected response code: {response.status}")
    except urllib.error.HTTPError as e:
        error_content = e.read().decode()
        if e.code == 422 and '"key is already in use"' in error_content:
            print("⚠️ SSH key is already uploaded to GitHub. No action needed.")
        else:
            print(f"❌ Failed to upload SSH key: {e.code} - {error_content}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def print_ssh_public_key(ssh_pub_path):
    if os.path.exists(ssh_pub_path):
        print("\n📋 Your SSH public key (copy this to GitHub if needed):\n")
        with open(ssh_pub_path, "r") as f:
            print(f.read())
    else:
        print(f"❌ SSH public key not found at {ssh_pub_path}")

def test_ssh_connection():
    print("\n🔑 Testing SSH connection to GitHub...")
    try:
        result = subprocess.run(
            ["ssh", "-T", "-o", "StrictHostKeyChecking=accept-new", "git@github.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=15
        )
        output = result.stdout.strip()
        print("=== SSH Test Output ===")
        print(output)

        if "Hi " in output and "You've successfully authenticated" in output:
            print("\n✅ SSH connection to GitHub successful!")
            return True
        else:
            print("\n❌ SSH connection to GitHub failed or was not fully successful.")
            return False
    except subprocess.TimeoutExpired:
        print("❌ SSH test timed out. Check your network and SSH installation.")
        return False
    except Exception as e:
        print(f"❌ SSH test failed: {e}")
        return False

def main():
    if not install_git():
        print("Aborting due to Git installation failure.")
        sys.exit(1)

    configure_git()

    ssh_priv, ssh_pub = check_or_create_ssh_key()
    if not ssh_priv or not ssh_pub:
        print("Aborting due to SSH key issues.")
        sys.exit(1)

    start_ssh_agent_and_add_key(ssh_priv)

    upload_ssh_key_to_github(ssh_pub)

    print_ssh_public_key(ssh_pub)

    if test_ssh_connection():
        print("\n🎉 All done! Your Git and SSH are set up for GitHub.")
    else:
        print("\n⚠️  SSH connection test failed. Double-check your SSH key on GitHub.")

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