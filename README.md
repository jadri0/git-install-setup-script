# 🇬🇧🇺🇸 ENGLISH


# 🔧 Automatic Git + SSH Setup and Installation Script for GitHub

This Python script installs Git (if it's not already installed), configures your name and email, generates an SSH key (if one doesn't exist), adds it to the `ssh-agent`, uploads it to GitHub via the API using your personal token, and tests the SSH connection.

## 🚀 Features

- ✅ Git installation support for Linux, macOS, and Windows.  
- 🛠️ Global Git configuration (user name, email, automatically sets the main branch to 'main', etc.).  
- 🔐 Automatic generation of an Ed25519 SSH key.  
- 🧠 Starts and configures the `ssh-agent`.  
- ☁️ Automatically uploads your public SSH key to GitHub.  
- 🔎 Tests your SSH connection to GitHub.  

## 🧰 Requirements

- Python 3.x  
- Internet access  
- On Linux/macOS: `ssh`, `ssh-keygen`, and `git` available or installable with `sudo`  
- On Windows: Chocolatey or Winget  

## 📝 Usage

1. Clone this repository or download one of the `.py` files. There are two `.py` files: `git-install-setup-script-en.py`, for English speakers, and `git-install-setup-script-es.py`, for Spanish speakers.

2. Run the script:  
   
   ```bash
   python3 git-install-setup-script-en.py

3. The script will ask you for:  
   - Your name and email for Git. Before entering it, check if your GitHub email is private. A private email looks like this: `12345678+USERNAME@users.noreply.github.com`.  
   - A GitHub personal access token with `admin:public_key` permissions.  

     You can generate it here: https://github.com/settings/tokens

4. If everything works correctly, you’ll see a message confirming successful authentication with GitHub.  

## 💡 Notes

- If you already have an SSH key (`~/.ssh/id_ed25519.pub`), it will be reused.  
- If your key is already added to GitHub, the script will detect that and skip the upload.  
- On macOS, `.DS_Store` is automatically added to your global `.gitignore`.

<br>
<br>
<br>
<br>
<br>

# 🇪🇸🇲🇽 ESPAÑOL


# 🔧 Script de Instalación y Configuración Automática de Git + SSH para GitHub

Este script en Python instala Git (si no está instalado), configura tu nombre y correo electrónico, genera claves SSH (si no existen), las añade al `ssh-agent`, las sube a GitHub mediante la API usando tu token personal, y comprueba la conexión SSH.

## 🚀 Características

- ✅ Instalación de Git en Linux, macOS y Windows.
- 🛠️ Configuración global de Git (nombre de usuario, correo electrónico, cambio automático de nombre de la rama principal a 'main', etc.).
- 🔐 Generación automática de clave SSH (Ed25519).
- 🧠 Arranque y configuración del `ssh-agent`.
- ☁️ Subida automática de la clave pública SSH a GitHub.
- 🔎 Prueba de conexión SSH a GitHub.

## 🧰 Requisitos

- Python 3.x
- Acceso a Internet
- En sistemas Linux/macOS: tener `ssh`, `ssh-keygen`, `git` disponibles o instalables con `sudo`
- En Windows: Chocolatey o Winget

## 📝 Uso

1. Clona este repositorio o descarga uno de los archivos `.py`. Hay dos archivos `.py`: `git-install-setup-script-en.py`, en inglés, y `git-install-setup-script-es.py`, en español.

2. Ejecuta el script:

   ```bash
   python3 git-install-setup-script-es.py

3. El script te pedirá:
   - Tu nombre y correo para Git. Antes de introducirlo, comprueba si tu correo electrónico es privado. Un correo privado tiene un formato del tipo: 12345678+USUARIO@users.noreply.github.com.
   - Un token de acceso personal de GitHub con permisos `admin:public_key`.

     Puedes generarlo aquí: https://github.com/settings/tokens

4. Si todo va bien, verás un mensaje de autenticación exitosa con GitHub.

## 💡 Notas

- Si ya tienes una clave SSH existente (`~/.ssh/id_ed25519.pub`), se reutilizará.
- Si tu clave ya está en GitHub, el script lo detectará y no la subirá otra vez.
- En macOS, se añade automáticamente `.DS_Store` al `.gitignore_global`.