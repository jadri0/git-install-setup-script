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
        print("No ha sido posible detectar la distribución de Linux.")
        return False

    distro = ""
    for line in os_release.splitlines():
        if line.startswith("ID="):
            distro = line.split("=")[1].strip().strip('"')
            break

    print(f"Distribución de Linux detectada: {distro}")

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
        print(f"Distribución de Linux no compatible: {distro}")
        return False

def install_git_macos():
    if shutil.which("brew") is None:
        print("Homebrew no ha sido detectado. Puedes descargarlo desde https://brew.sh/")
        return False
    return run_command(["brew", "install", "git"])

def install_git_windows():
    if shutil.which("choco"):
        return run_command(["choco", "install", "git", "-y"])
    elif shutil.which("winget"):
        return run_command(["winget", "install", "--id", "Git.Git", "-e", "--source", "winget"])
    else:
        print("Ni Chocolatey ni Winget han sido detectados. Puedes descargar Git manualmente desde https://git-scm.com/")
        return False

def install_git():
    if is_git_installed():
        print("✅ Git ya está instalado.")
        return True

    print("❌ Git no ha sido detectado. Instalando...")

    system = platform.system()
    if system == "Linux":
        success = install_git_linux()
    elif system == "Darwin":
        success = install_git_macos()
    elif system == "Windows":
        success = install_git_windows()
    else:
        print(f"Sistema Operativo no compatible: {system}")
        success = False

    if success:
        print("✅ Git ha sido instalado con éxito.")
    else:
        print("❌ No ha sido posible instalar Git.")
    return success

def configure_git():
    print("\n🔧 Configuración de Git")
    name = input("Nombre de usuario de Git: ").strip()
    email = input("Correo electrónico de Git (atención, puede que esté configurado como privado [Formato: 12345678+USUARIO@users.noreply.github.com]): ").strip()

    if name and email:
        run_command(["git", "config", "--global", "user.name", name])
        run_command(["git", "config", "--global", "user.email", email])
        print(f"\n✅ Git configurado con éxito:\n  Usuario : {name}\n  Correo electrónico: {email}")
    else:
        print("⚠️ Configuración de Git interrumpida: campo de nombre de usuario y/o de correo electrónico vacío.")
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
                    print("🧹 .DS_Store añadido a ~/.gitignore_global")
        except Exception as e:
            print(f"No ha sido posible actualizar ~/.gitignore_global: {e}")

        run_command(["git", "config", "--global", "core.excludesfile", gitignore_global])

def check_or_create_ssh_key():
    ssh_pub = os.path.expanduser("~/.ssh/id_ed25519.pub")
    ssh_priv = os.path.expanduser("~/.ssh/id_ed25519")

    if os.path.exists(ssh_pub):
        print("🔑 Clave SSH encontrada en ~/.ssh/id_ed25519.pub")
        return ssh_priv, ssh_pub
    else:
        print("🔐 No se ha encontrado clave SSH. Generando nueva clave SSH Ed25519...")
        os.makedirs(os.path.dirname(ssh_priv), exist_ok=True)
        try:
            subprocess.run([
                "ssh-keygen", "-t", "ed25519", "-C", "", "-f", ssh_priv, "-N", ""
            ], check=True)
            print("✅ Clave SSH generada con éxito en ~/.ssh/id_ed25519")
            return ssh_priv, ssh_pub
        except Exception as e:
            print(f"❌ No ha sido posible generar clave SSH: {e}")
            return None, None

def start_ssh_agent_and_add_key(ssh_priv_path):
    ssh_auth_sock = os.environ.get("SSH_AUTH_SOCK")
    if ssh_auth_sock and os.path.exists(ssh_auth_sock):
        print("🔑 ssh-agent ya está iniciado.")
    else:
        print("🔄 Iniciando ssh-agent...")
        result = subprocess.run(["ssh-agent", "-s"], stdout=subprocess.PIPE, text=True)
        output = result.stdout
        for line in output.splitlines():
            if line.startswith("SSH_AUTH_SOCK"):
                sock = line.split(";")[0].split("=")[1]
                os.environ["SSH_AUTH_SOCK"] = sock
            elif line.startswith("SSH_AGENT_PID"):
                pid = line.split(";")[0].split("=")[1]
                os.environ["SSH_AGENT_PID"] = pid
        print("✅ ssh-agent iniciado con éxito.")

    print(f"➕ Añadiendo la clave SSH {ssh_priv_path} a ssh-agent...")
    try:
        subprocess.run(["ssh-add", ssh_priv_path], check=True)
        print("✅ Clave SSH añadida con éxito a ssh-agent.")
    except subprocess.CalledProcessError as e:
        print(f"❌ No ha sido posible añadir la clave SSH a ssh-agent: {e}")

def upload_ssh_key_to_github(ssh_pub_path):
    print("\n🌐 Añadir la clave SSH a GitHub")
    token = input("Introduce tu Personal Access Token de Github (scope/permisos: `admin:public_key`). Si no tienes uno, puedes crearlo en https://github.com/settings/tokens: ").strip()
    if not token:
        print("⚠️ No se ha introducido un token válido. Subida interrumpida.")
        return

    title = input("Intruduce un nombre para esta clave SSH (por ejemplo, 'mi ordenador'): ").strip()
    if not os.path.exists(ssh_pub_path):
        print(f"❌ No se ha encontrado clave SSH: {ssh_pub_path}")
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
                print("✅ Clave SSH subida con éxito a GitHub.")
            else:
                print(f"Código de respuesta inesperado: {response.status}")
    except urllib.error.HTTPError as e:
        error_content = e.read().decode()
        if e.code == 422 and '"key is already in use"' in error_content:
            print("⚠️ Esta clave SSH ya ha sido subida a GitHub. No hace falta hacer nada más.")
        else:
            print(f"❌ No ha sido posible subir la clave SSH: {e.code} - {error_content}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def print_ssh_public_key(ssh_pub_path):
    if os.path.exists(ssh_pub_path):
        print("\n📋 Tu clave SSH pública es:\n")
        with open(ssh_pub_path, "r") as f:
            print(f.read())
    else:
        print(f"❌ No se ha encontrado clave SSH pública en {ssh_pub_path}")

def test_ssh_connection():
    print("\n🔑 Comprobando conexión SSH a GitHub...")
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
            print("\n✅ Conexión SSH a GitHub exitosa.")
            return True
        else:
            print("\n❌ Conexión SSH a GitHub fallida.")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Se ha agotado el tiempo de espera. Comprueba tu red y tu instalación SSH.")
        return False
    except Exception as e:
        print(f"❌ Test SSH fallido: {e}")
        return False

def main():
    if not install_git():
        print("Fallo en la instalación de Git. Abortando...")
        sys.exit(1)

    configure_git()

    ssh_priv, ssh_pub = check_or_create_ssh_key()
    if not ssh_priv or not ssh_pub:
        print("Problemas con la clave SSH. Abortando...")
        sys.exit(1)

    start_ssh_agent_and_add_key(ssh_priv)

    upload_ssh_key_to_github(ssh_pub)

    print_ssh_public_key(ssh_pub)

    if test_ssh_connection():
        print("\n🎉 ¡Todo listo! Tu Git y SSH han sido configurados con éxito.")
    else:
        print("\n⚠️  Test de conexión SSH fallido. Comprueba tu clave SSH en GitHub.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        while True:
            try:
                input("\nPresiona [Intro] para salir...")
                sys.exit(0)
            except KeyboardInterrupt:
                exit()