# 🔧 Automatic Git + SSH Setup and Installation Script for GitHub

This Python script installs Git (if it's not already installed), configures your name and email, generates an SSH key (if one doesn't exist), adds it to the `ssh-agent`, uploads it to GitHub via the API using your personal token, and tests the SSH connection. Simplifies an annoying process that distro hoppers and dual boot enjoyers know too well.

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

1. Clone this repository or download the `.py` file

2. Run the script:  
   
   ```bash
   python3 git-install-setup-script.py

3. The script will ask you for:  
   - Your name and email for Git. Before entering it, check if your GitHub email is private. A private email looks like this: `12345678+USERNAME@users.noreply.github.com`.  
   - A GitHub personal access token with `admin:public_key` permissions.  

     You can generate it here: https://github.com/settings/tokens

4. If everything works correctly, you’ll see a message confirming successful authentication with GitHub.  

## 💡 Notes

- If you already have an SSH key (`~/.ssh/id_ed25519.pub`), it will be reused.  
- If your key is already added to GitHub, the script will detect that and skip the upload.  
- On macOS, `.DS_Store` is automatically added to your global `.gitignore`.