import os
import struct
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from tkinterdnd2 import TkinterDnD, DND_FILES
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import time

APP_NAME = "File Encryptor"
VERSION = "1.0"
MAGIC = b"FSY1"
ITERATIONS = 200_000
KEY_LEN = 32

def unique_path(path):
    base, ext = os.path.splitext(path)
    if not os.path.exists(path):
        return path
    i = 1
    while True:
        candidate = f"{base}{i}{ext}"
        if not os.path.exists(candidate):
            return candidate
        i += 1

def encrypt_file(file_path, password):
    salt = get_random_bytes(16)
    key = PBKDF2(password, salt, KEY_LEN, count=ITERATIONS)
    cipher = AES.new(key, AES.MODE_GCM)
    iv = cipher.nonce
    with open(file_path, "rb") as f:
        plaintext = f.read()
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    encrypted_path = file_path + ".sy"
    encrypted_path = unique_path(encrypted_path)
    with open(encrypted_path, "wb") as f:
        f.write(MAGIC)
        f.write(salt)
        f.write(iv)
        f.write(tag)
        f.write(struct.pack(">Q", len(ciphertext)))
        f.write(ciphertext)
    return encrypted_path

def decrypt_file(file_path, password):
    with open(file_path, "rb") as f:
        magic = f.read(4)
        if magic != MAGIC:
            raise ValueError("File format invalid or corrupted.")
        salt = f.read(16)
        iv = f.read(16)
        tag = f.read(16)
        length = struct.unpack(">Q", f.read(8))[0]
        ciphertext = f.read(length)
    key = PBKDF2(password, salt, KEY_LEN, count=ITERATIONS)
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    try:
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    except ValueError:
        raise ValueError("Wrong password or file integrity corrupted!")
    if file_path.lower().endswith(".sy"):
        original_path = file_path[:-3]
    else:
        original_path = file_path + ".dec"
    original_path = unique_path(original_path)
    with open(original_path, "wb") as f:
        f.write(plaintext)
    return original_path

class App:
    def __init__(self, root):
        self.root = root
        root.title(APP_NAME)
        root.geometry("750x640")
        root.configure(bg="black")
        try:
            root.iconbitmap("icon.ico")
        except Exception:
            pass
        self.page_state = "home"
        self.selected_file = None
        self.password = None
        self.title_font = ("Courier New", 16)
        self.button_font = ("Courier New", 14)
        self.log_path = os.path.join(os.getcwd(), "sy.log")
        if not os.path.exists(self.log_path):
            try:
                open(self.log_path, "a", encoding="utf-8").close()
            except Exception:
                pass
        self.log = None
        self.create_home_page()

    def write_log_to_file(self, text):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {text}\n"
        try:
            with open(self.log_path, "a", encoding="utf-8") as lf:
                lf.write(line)
        except Exception:
            pass

    def load_log_into_widget(self):
        try:
            with open(self.log_path, "r", encoding="utf-8") as lf:
                content = lf.read()
        except Exception:
            content = ""
        if not hasattr(self, "log") or self.log is None:
            try:
                self.log = ScrolledText(self.root, height=12, wrap=tk.WORD, bg="#111", fg="#ff2a2a", font=("Courier New", 12))
                self.log.pack(fill="both", expand=True, padx=20, pady=10)
            except Exception:
                self.log = None
        if self.log:
            try:
                self.log.delete("1.0", "end")
                if content:
                    self.log.insert("end", content)
                    self.log.see("end")
            except Exception:
                pass

    def show_notification(self, message, error=False, duration=3000):
        try:
            if error:
                messagebox.showerror("Error", message)
            else:
                messagebox.showinfo("Info", message)
        except Exception:
            pass
        try:
            n = tk.Toplevel(self.root)
            n.overrideredirect(True)
            n.attributes("-topmost", True)
            lbl = tk.Label(n, text=message, bg="#222", fg="#fff", font=("Courier New", 10), bd=2, relief="raised", padx=10, pady=6)
            lbl.pack()
            self.root.update_idletasks()
            rx = self.root.winfo_x()
            ry = self.root.winfo_y()
            rw = self.root.winfo_width()
            rh = self.root.winfo_height()
            nx = rx + max(10, rw - 260)
            ny = ry + max(10, rh - 100)
            try:
                n.geometry(f"+{nx}+{ny}")
            except Exception:
                pass
            n.after(duration, n.destroy)
        except Exception:
            pass

    def create_home_page(self):
        self.clear_screen()
        title = tk.Label(self.root, text="FILE ENCRYPTOR", fg="#ff2a2a", bg="black", font=("Courier New", 24, "bold"))
        title.pack(pady=12)
        self.drop_area = tk.Label(self.root, text="Drag & Drop File Here", bg="black", fg="#ff2a2a", font=self.title_font, relief="solid", width=45, height=5)
        self.drop_area.pack(pady=12)
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind('<<Drop>>', self.on_file_drop)
        select_button = tk.Button(self.root, text="Select File", command=self.select_file, font=self.button_font, bg="black", fg="red", width=20)
        select_button.pack(pady=6)
        if self.log:
            try:
                self.log.destroy()
            except Exception:
                pass
            self.log = None
        self.log = ScrolledText(self.root, height=12, wrap=tk.WORD, bg="#111", fg="#ff2a2a", font=("Courier New", 12))
        self.log.pack(fill="both", expand=True, padx=20, pady=10)
        self.load_log_into_widget()
        footer_frame = tk.Frame(self.root, bg="black")
        footer_frame.pack(fill="x", side="bottom", pady=6)
        ver_label = tk.Label(footer_frame, text=f"v{VERSION} by ", fg="#ff2a2a", bg="black", font=("Courier New", 10))
        ver_label.pack(side="left", padx=(20,0))
        link = tk.Label(footer_frame, text="SYRE", fg="#ff2a2a", bg="black", font=("Courier New", 10))
        link.pack(side="left")
        def open_link(event=None):
            try:
                webbrowser.open("https://github.com/realSina")
            except Exception:
                pass
        link.bind("<Button-1>", open_link)

    def create_encrypt_decrypt_page(self):
        self.clear_screen()
        title = tk.Label(self.root, text="Choose Action", fg="#ff2a2a", bg="black", font=("Courier New", 24, "bold"))
        title.pack(pady=12)
        file_display = os.path.basename(self.selected_file) if self.selected_file else "No file selected"
        file_label = tk.Label(self.root, text=f"Selected File: {file_display}", fg="#ff2a2a", bg="black", font=("Courier New", 12))
        file_label.pack(pady=6)
        encrypt_button = tk.Button(self.root, text="Encrypt File", command=self.prepare_encryption, font=self.button_font, bg="black", fg="red", width=20)
        encrypt_button.pack(pady=10)
        decrypt_button = tk.Button(self.root, text="Decrypt File", command=self.prepare_decryption, font=self.button_font, bg="black", fg="red", width=20)
        decrypt_button.pack(pady=10)
        back_button = tk.Button(self.root, text="Back to Home", command=self.back_to_home, font=self.button_font, bg="black", fg="red", width=20)
        back_button.pack(pady=10)

    def prepare_encryption(self):
        self.page_state = "encrypt"
        self.create_password_page("Encrypt File")

    def prepare_decryption(self):
        self.page_state = "decrypt"
        self.create_password_page("Decrypt File")

    def create_password_page(self, action):
        self.clear_screen()
        title = tk.Label(self.root, text=f"Enter Password to {action}", fg="#ff2a2a", bg="black", font=("Courier New", 24, "bold"))
        title.pack(pady=20)
        file_display = os.path.basename(self.selected_file) if self.selected_file else "No file selected"
        file_label = tk.Label(self.root, text=f"Selected File: {file_display}", fg="#ff2a2a", bg="black", font=("Courier New", 12))
        file_label.pack(pady=(0,10))
        pass_frame = tk.Frame(self.root, bg="black")
        pass_frame.pack(pady=10)
        self.password_entry = tk.Entry(pass_frame, show="*", width=30, bg="#111", fg="red", font=("Courier New", 14))
        self.password_entry.pack(side="left", padx=(0,8))
        self.show_var = tk.BooleanVar(value=False)
        def toggle_pwd():
            if self.show_var.get():
                self.password_entry.config(show="")
            else:
                self.password_entry.config(show="*")
        show_btn = tk.Checkbutton(pass_frame, text="Show", variable=self.show_var, command=toggle_pwd, fg="#ff2a2a", bg="black", selectcolor="#111", font=("Courier New", 10))
        show_btn.pack(side="left")
        submit_button = tk.Button(self.root, text="Submit", command=self.submit_password, font=self.button_font, bg="black", fg="red", width=20)
        submit_button.pack(pady=10)
        back_button = tk.Button(self.root, text="Back", command=self.back_to_previous, font=self.button_font, bg="black", fg="red", width=20)
        back_button.pack(pady=10)
        self.password_entry.bind("<Return>", self.submit_password)
        self.load_log_into_widget()

    def submit_password(self, event=None):
        password = self.password_entry.get()
        if not password:
            messagebox.showwarning("Warning", "Please enter a password.")
            return
        self.password = password
        if self.page_state == "encrypt":
            self.encrypt_action()
        elif self.page_state == "decrypt":
            self.decrypt_action()

    def encrypt_action(self):
        if not self.selected_file:
            messagebox.showwarning("Warning", "Please select a file first.")
            return
        info_text = f"[PROCESS] File '{self.selected_file}' is going to be encrypted with password '{self.password}'"
        self.write_log_to_file(info_text)
        self.load_log_into_widget()
        self.root.update()
        try:
            enc_file = encrypt_file(self.selected_file, self.password)
            success_text = f"[ENCRYPTION] File '{self.selected_file}' has been encrypted with password '{self.password}'. Saved to '{enc_file}'"
            self.write_log_to_file(success_text)
            self.load_log_into_widget()
            self.show_notification(f"Encrypted: {os.path.basename(enc_file)}", error=False)
            self.back_to_home()
        except Exception as e:
            err_text = f"[ENCRYPTION] File '{self.selected_file}' hasn't been encrypted with password '{self.password}'. Error: {e}"
            self.write_log_to_file(err_text)
            self.load_log_into_widget()
            self.show_notification(f"Encrypt error: {e}", error=True)

    def decrypt_action(self):
        if not self.selected_file:
            messagebox.showwarning("Warning", "Please select a file first.")
            return
        info_text = f"[PROCESS] File '{self.selected_file}' is going to be decrypted with password '{self.password}'"
        self.write_log_to_file(info_text)
        self.load_log_into_widget()
        self.root.update()
        try:
            dec_file = decrypt_file(self.selected_file, self.password)
            success_text = f"[DECRYPTION] File '{self.selected_file}' has been decrypted with password '{self.password}'. Saved to '{dec_file}'"
            self.write_log_to_file(success_text)
            self.load_log_into_widget()
            self.show_notification(f"Decrypted: {os.path.basename(dec_file)}", error=False)
            self.back_to_home()
        except Exception as e:
            err_text = f"[DECRYPTION] File '{self.selected_file}' hasn't been decrypted with password '{self.password}'. Error: {e}"
            self.write_log_to_file(err_text)
            self.load_log_into_widget()
            self.show_notification(f"Decrypt error: {e}", error=True)

    def on_file_drop(self, event):
        self.selected_file = event.data
        info_text = f"[DROPPED] {self.selected_file}"
        self.write_log_to_file(info_text)
        self.load_log_into_widget()
        self.create_encrypt_decrypt_page()

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.selected_file = file_path
            info_text = f"[SELECTED] {self.selected_file}"
            self.write_log_to_file(info_text)
            self.load_log_into_widget()
            self.create_encrypt_decrypt_page()

    def back_to_previous(self):
        if self.page_state == "encrypt" or self.page_state == "decrypt":
            self.create_encrypt_decrypt_page()

    def back_to_home(self):
        self.page_state = "home"
        self.create_home_page()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            try:
                widget.destroy()
            except Exception:
                pass

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = App(root)
    root.mainloop()
