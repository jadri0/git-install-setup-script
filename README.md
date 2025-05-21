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

1. Clona este repositorio o descarga el archivo `.py`.

2. Ejecuta el script:

   ```bash
   python3 setup_git_ssh.py

3. El script te pedirá:
   - Tu nombre y correo para Git. Antes de introducirlo, comprueba si tu correo electrónico es privado. Un correo privado tiene un formato del tipo: 12345678+USUARIO@users.noreply.github.com.
   - Un token de acceso personal de GitHub con permisos `admin:public_key`.

     Puedes generarlo aquí: https://github.com/settings/tokens

4. Si todo va bien, verás un mensaje de autenticación exitosa con GitHub.

## 💡 Notas

- Si ya tienes una clave SSH existente (`~/.ssh/id_ed25519.pub`), se reutilizará.
- Si tu clave ya está en GitHub, el script lo detectará y no la subirá otra vez.
- En macOS, se añade automáticamente `.DS_Store` al `.gitignore_global`.