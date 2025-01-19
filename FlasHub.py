#!/usr/bin/env python3
import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class FastbootFlashTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Fastboot Flash Tool")
        self.root.geometry("800x600")

        # Variables pour le thème et la langue
        self.theme = tk.StringVar(value="clair")
        self.lang = tk.StringVar(value="fr")

        # Liste des partitions disponibles
        self.partitions = [
            "boot", "recovery", "bootloader", "vbmeta", "vendor",
            "boot_a", "recovery_a", "bootloader_a", "vbmeta_a", "vendor_a",
            "boot_b", "recovery_b", "bootloader_b", "vbmeta_b", "vendor_b",
           "system", "system_a", "system_b",
            "dtbo", "dtbo_a", "dtbo_b",
            "radio", "radio_a", "radio_b",
            "modem", "modem_a", "modem_b",
            "cache", "userdata", "metadata",
            "persist", "misc", "splash"
        ]

        # État de connexion
        self.device_status = tk.StringVar(value="Inactif")

        # Création des onglets
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.main_frame = ttk.Frame(self.notebook)
        self.terminal_frame = ttk.Frame(self.notebook)
        self.settings_frame = ttk.Frame(self.notebook)
        self.readme_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.main_frame, text="Flash")
        self.notebook.add(self.terminal_frame, text="Terminal")
        self.notebook.add(self.settings_frame, text="Paramètres")
        self.notebook.add(self.readme_frame, text="README")

        self.create_main_frame()
        self.create_terminal_frame()
        self.create_settings_frame()
        self.create_readme_frame()

    def create_main_frame(self):
        # Frame pour l'état de l'appareil
        status_frame = ttk.LabelFrame(self.main_frame, text="État de l'appareil", padding=(10, 10))
        status_frame.pack(fill="x", padx=10, pady=5)

        self.status_label = tk.Label(status_frame, textvariable=self.device_status, bg="red", fg="white", width=10, anchor="center")
        self.status_label.pack(side="left", padx=5, pady=5)

        check_status_button = ttk.Button(status_frame, text="Vérifier l'état", command=self.check_device_status)
        check_status_button.pack(side="left", padx=5, pady=5)

        # Frame pour les fichiers
        file_frame = ttk.LabelFrame(self.main_frame, text="Fichier à flasher", padding=(10, 10))
        file_frame.pack(fill="x", padx=10, pady=5)

        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=80)
        self.file_entry.pack(side="left", padx=5, pady=5)

        browse_button = ttk.Button(file_frame, text="Parcourir", command=self.browse_file)
        browse_button.pack(side="left", padx=5, pady=5)

        # Frame pour choisir la partition
        partition_frame = ttk.LabelFrame(self.main_frame, text="Choisir une partition", padding=(10, 10))
        partition_frame.pack(fill="x", padx=10, pady=5)

        self.partition_var = tk.StringVar(value=self.partitions[0])
        self.partition_menu = ttk.Combobox(partition_frame, textvariable=self.partition_var, values=self.partitions, state="readonly")
        self.partition_menu.pack(fill="x", padx=5, pady=5)

        # Frame pour les actions et logs
        action_frame = ttk.LabelFrame(self.main_frame, text="Actions", padding=(10, 10))
        action_frame.pack(fill="x", padx=10, pady=5)

        self.slot_var = tk.StringVar(value="")
        slot_frame = ttk.Frame(action_frame)
        slot_frame.pack(side="left", padx=5, pady=5)

        ttk.Label(slot_frame, text="Slot (optionnel) :").pack(side="left", padx=5)
        self.slot_menu = ttk.Combobox(slot_frame, textvariable=self.slot_var, values=["", "a", "b"], state="readonly", width=5)
        self.slot_menu.pack(side="left", padx=5)

        execute_button = ttk.Button(action_frame, text="Flasher", command=self.start_flash_thread)
        execute_button.pack(side="left", padx=5, pady=5)

        reboot_button = ttk.Button(action_frame, text="Reboot", command=self.reboot_device)
        reboot_button.pack(side="left", padx=5, pady=5)

        wipe_button = ttk.Button(action_frame, text="Wipe Partition", command=self.confirm_wipe_partition)
        wipe_button.pack(side="left", padx=5, pady=5)

        boot_temp_button = ttk.Button(action_frame, text="Boot Temporaire", command=self.boot_temp_image)
        boot_temp_button.pack(side="left", padx=5, pady=5)

        # Frame des logs
        log_frame = ttk.LabelFrame(self.main_frame, text="Logs", padding=(10, 10))
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log_text = tk.Text(log_frame, wrap="word", state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

    def create_terminal_frame(self):
        terminal_label = ttk.Label(self.terminal_frame, text="Terminal Emulator")
        terminal_label.pack(pady=10)

        self.terminal_input = tk.Text(self.terminal_frame, height=15, bg="black", fg="white", insertbackground="white")
        self.terminal_input.pack(fill="both", expand=True, padx=10, pady=10)

        execute_terminal_button = ttk.Button(self.terminal_frame, text="Exécuter", command=self.execute_terminal_command)
        execute_terminal_button.pack(pady=5)

    def execute_terminal_command(self):
        command = self.terminal_input.get("1.0", "end").strip()
        if not command:
            self.log("Erreur : Aucune commande spécifiée.")
            return

        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            self.log(result.stdout)
            if result.stderr:
                self.log(result.stderr)
        except Exception as e:
            self.log(f"Erreur lors de l'exécution : {str(e)}")

    def create_settings_frame(self):
        settings_label = ttk.Label(self.settings_frame, text="Paramètres")
        settings_label.pack(pady=10)

        theme_frame = ttk.LabelFrame(self.settings_frame, text="Thème", padding=(10, 10))
        theme_frame.pack(fill="x", padx=10, pady=5)

        ttk.Radiobutton(theme_frame, text="Clair", variable=self.theme, value="clair", command=self.apply_theme).pack(anchor="w", padx=5, pady=5)
        ttk.Radiobutton(theme_frame, text="Sombre", variable=self.theme, value="sombre", command=self.apply_theme).pack(anchor="w", padx=5, pady=5)

        lang_frame = ttk.LabelFrame(self.settings_frame, text="Langue", padding=(10, 10))
        lang_frame.pack(fill="x", padx=10, pady=5)

        ttk.Radiobutton(lang_frame, text="Français", variable=self.lang, value="fr", command=self.apply_language).pack(anchor="w", padx=5, pady=5)
        ttk.Radiobutton(lang_frame, text="Anglais", variable=self.lang, value="en", command=self.apply_language).pack(anchor="w", padx=5, pady=5)

    def apply_theme(self):
        theme = self.theme.get()
        if theme == "clair":
            self.root.config(bg="white")
            self.log_text.config(bg="white", fg="black")
        elif theme == "sombre":
            self.root.config(bg="black")
            self.log_text.config(bg="black", fg="white")

    def apply_language(self):
        lang = self.lang.get()
        # Placeholder pour les ajustements de langue (traductions si nécessaires)
        if lang == "fr":
            self.log("Langue définie sur Français.")
        elif lang == "en":
            self.log("Language set to English.")

    def create_readme_frame(self):
        readme_label = ttk.Label(self.readme_frame, text="Info")
        readme_label.pack(pady=10)

        self.readme_text = tk.Text(self.readme_frame, wrap="word")
        self.readme_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.readme_text.insert("1.0", "Bienvenue dans Fastboot Flash Tool !\n\n- Utilisez l'onglet Flash pour sélectionner et flasher des partitions.\n- L'onglet Terminal permet d'exécuter des commandes Fastboot/ADB ou autres.\n- Les Paramètres Languages Ne Sont Pas Configurés.\n-Pour Des Questions Ou Autres Contacter-Moi : tomroger8012@gmail.com")
        self.readme_text.config(state="disabled")

    def browse_file(self):
        file_path = filedialog.askopenfilename(title="Choisir un fichier .img", filetypes=[("Images Fastboot", "*.img")])
        if file_path:
            self.file_path_var.set(file_path)

    def check_device_status(self):
        try:
            result = subprocess.run(["fastboot", "devices"], capture_output=True, text=True)
            if result.stdout.strip():
                self.device_status.set("Actif")
                self.status_label.config(bg="green")
                self.log("Appareil détecté :\n" + result.stdout.strip())
            else:
                self.device_status.set("Inactif")
                self.status_label.config(bg="red")
                self.log("Aucun appareil détecté.")
        except FileNotFoundError:
            self.device_status.set("Inactif")
            self.status_label.config(bg="red")
            self.log("Erreur : Fastboot n'est pas installé ou introuvable dans le PATH.")

    def start_flash_thread(self):
        self.check_device_status()
        if self.device_status.get() != "Actif":
            messagebox.showerror("Erreur", "Aucun appareil actif détecté.")
            return
        threading.Thread(target=self.flash_partition, daemon=True).start()

    def flash_partition(self):
        partition = self.partition_var.get()
        file_path = self.file_path_var.get()
        slot = self.slot_var.get()

        if not os.path.exists(file_path):
            self.log("Erreur : Fichier introuvable.")
            return

        cmd = ["fastboot", "flash", partition]
        if slot:
            cmd.extend(["--slot", slot])
        cmd.append(file_path)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.log(result.stdout)
            if result.stderr:
                self.log(result.stderr)
        except Exception as e:
            self.log(f"Erreur lors du flash : {str(e)}")

    def confirm_wipe_partition(self):
        response = messagebox.askyesno("Attention", "Êtes-vous sûr de vouloir effacer la partition ? Cette action est irréversible.")
        if response:
            self.wipe_partition()

    def wipe_partition(self):
        self.check_device_status()
        if self.device_status.get() != "Actif":
            messagebox.showerror("Erreur", "Aucun appareil actif détecté.")
            return

        partition = self.partition_var.get()

        try:
            result = subprocess.run(["fastboot", "erase", partition], capture_output=True, text=True)
            self.log(result.stdout)
            if result.stderr:
                self.log(result.stderr)
        except Exception as e:
            self.log(f"Erreur lors de l'effacement : {str(e)}")

    def reboot_device(self):
        self.check_device_status()
        if self.device_status.get() != "Actif":
            messagebox.showerror("Erreur", "Aucun appareil actif détecté.")
            return

        try:
            result = subprocess.run(["fastboot", "reboot"], capture_output=True, text=True)
            self.log(result.stdout)
            if result.stderr:
                self.log(result.stderr)
        except Exception as e:
            self.log(f"Erreur lors du redémarrage : {str(e)}")

    def boot_temp_image(self):
        file_path = self.file_path_var.get()

        if not os.path.exists(file_path):
            self.log("Erreur : Fichier introuvable.")
            return

        self.check_device_status()
        if self.device_status.get() != "Actif":
            messagebox.showerror("Erreur", "Aucun appareil actif détecté.")
            return

        try:
            result = subprocess.run(["fastboot", "boot", file_path], capture_output=True, text=True)
            self.log(result.stdout)
            if result.stderr:
                self.log(result.stderr)
        except Exception as e:
            self.log(f"Erreur lors du démarrage temporaire : {str(e)}")

    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.config(state="disabled")
        self.log_text.see("end")

if __name__ == "__main__":
    root = tk.Tk()
    app = FastbootFlashTool(root)
    root.mainloop()
