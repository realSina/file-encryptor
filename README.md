# File Encryptor

**File Encryptor** is a lightweight and secure file encryption and decryption tool built with Python and Tkinter. It uses AES-256 encryption, offers a user-friendly GUI, and ensures your files are safe without accidental overwrites.

---

## Features

* **AES-256 Encryption & Decryption** with secure PBKDF2 key derivation
* **Drag & Drop** or file selection
* **Automatic Logging** of all operations
* **Password Protection**
* **Overwrite Prevention**: Automatically appends numbers to avoid replacing existing files
* **Notifications** for success and errors
* **Cross-Platform GUI** using Tkinter

---

## Installation

### From Source

1. Clone the repository:

```bash
git clone https://github.com/realSina/file-encryptor.git
cd file-encryptor
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python main.py
```

### Pre-built Executable (Windows)

The Windows executable (`.exe`) can be found in the **Releases** section. Simply download, double-click, and start encrypting files. No Python installation required.

---

## Usage

1. Drag & drop a file into the main window or select a file manually.
2. Choose **Encrypt** or **Decrypt**.
3. Enter your password.
4. Success and error notifications will guide you.
5. The encrypted/decrypted file will be saved automatically, preventing overwrites.

---

## Logging

All operations are logged in `sy.log` in the application folder. Logs include:

* File name
* Operations performed
* Encryption/Decryption success or failure
* Timestamp and password info (masked for security if desired)

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

## License

[MIT License](LICENSE)
