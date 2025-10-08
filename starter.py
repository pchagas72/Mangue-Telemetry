import tkinter as tk
from tkinter import scrolledtext, messagebox, Toplevel, StringVar, OptionMenu, Entry, Frame, Label
import subprocess
import threading
import os
import sys
import webbrowser
import queue
import re

# This new import is for detecting serial ports
try:
    import serial.tools.list_ports
except ImportError:
    messagebox.showerror(
        "Dependency Missing",
        "The 'pyserial' library is not installed for the starter script.\n"
        "Please close this window and run:\n\n"
        "pip install pyserial"
    )
    sys.exit(1)


# --- Configuration Constants ---
# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

# --- Project Structure Paths ---
INTERFACE_DIR = os.path.join(SCRIPT_DIR, 'interface')
INTERFACE_DIST_DIR = os.path.join(INTERFACE_DIR, 'dist')
SERVER_DIR = os.path.join(SCRIPT_DIR, 'server')
SERVER_RUN_FILE = os.path.join(SERVER_DIR, 'run.py')
REQUIREMENTS_FILE = os.path.join(SERVER_DIR, 'requirements.txt')
SETTINGS_FILE = os.path.join(SERVER_DIR, 'settings.py')
VENV_PATH = os.path.join(SERVER_DIR, 'venv')

# --- Webserver Configuration ---
FRONTEND_PORT = 3000
WEBSERVER_URL = f"http://localhost:{FRONTEND_PORT}"

# --- Platform-Specific Executable Names ---
IS_WINDOWS = sys.platform == 'win32'
PYTHON_EXEC_NAME = 'python.exe' if IS_WINDOWS else 'python'
PIP_EXEC_NAME = 'pip.exe' if IS_WINDOWS else 'pip'
VENV_BIN_DIR = 'Scripts' if IS_WINDOWS else 'bin'
VENV_PYTHON_EXECUTABLE = os.path.join(VENV_PATH, VENV_BIN_DIR, PYTHON_EXEC_NAME)
VENV_PIP_EXECUTABLE = os.path.join(VENV_PATH, VENV_BIN_DIR, PIP_EXEC_NAME)
NPX_EXEC_NAME = 'npx.cmd' if IS_WINDOWS else 'npx'


class ServerManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Servidores - Mangue Telemetry")
        self.root.geometry("850x650")

        self.processes = {}
        self.log_queue = queue.Queue()

        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.log("Bem-vindo ao Gerenciador de Servidores da Mangue Telemetry!")
        self.log("Use 'Editar Settings' para configurar a fonte de dados e a porta serial.")
        self.check_log_queue()

    def create_widgets(self):
        main_frame = tk.Frame(self.root, padx=15, pady=15, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True)

        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(pady=10, fill=tk.X)

        self.start_button = self._create_button(button_frame, "Iniciar Servidores", self.start_servers, "#4CAF50")
        self.stop_button = self._create_button(button_frame, "Parar Servidores", self.stop_servers, "#F44336", state=tk.DISABLED)
        self.config_button = self._create_button(button_frame, "Configurar Ambiente", self.configure_venv, "#2196F3")
        self.build_button = self._create_button(button_frame, "Build Frontend", self.build_frontend, "#FF9800")
        self.settings_button = self._create_button(button_frame, "Editar Settings", self.open_settings_window, "#673AB7")
        self.browser_button = self._create_button(button_frame, "Abrir Navegador", self.open_in_browser, "#FFC107", state=tk.DISABLED)


        for button in button_frame.winfo_children():
            button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        debug_label = tk.Label(main_frame, text="Terminal de Depuração:", font=("Helvetica", 12, "bold"), bg="#f0f0f0", anchor="w")
        debug_label.pack(fill=tk.X, pady=(10, 5))

        self.debug_text = scrolledtext.ScrolledText(
            main_frame, wrap=tk.WORD, state=tk.DISABLED,
            font=("Courier New", 10), bg="#2c3e50", fg="#ecf0f1",
            insertbackground="#ecf0f1", relief=tk.FLAT
        )
        self.debug_text.pack(fill=tk.BOTH, expand=True)

    def _create_button(self, parent, text, command, bg_color, state=tk.NORMAL):
        return tk.Button(
            parent, text=text, command=command, font=("Helvetica", 12, "bold"),
            bg=bg_color, fg="white", activebackground=bg_color,
            bd=0, relief=tk.FLAT, padx=15, pady=8, cursor="hand2", state=state
        )

    def start_servers(self):
        if self.processes:
            self.log("ERRO: Servidores já estão rodando.")
            return

        if not os.path.exists(INTERFACE_DIST_DIR):
             self.log("ERRO: O diretório 'interface/dist' não foi encontrado. Execute o 'Build Frontend' primeiro.")
             messagebox.showerror("Build Necessário", "O diretório 'interface/dist' não foi encontrado. Por favor, clique em 'Build Frontend' para compilar a interface antes de iniciar os servidores.")
             return

        self.log("Iniciando servidores...")
        self.update_button_states(is_running=True)

        backend_command = [
            VENV_PYTHON_EXECUTABLE,
            "-m", "uvicorn",
            "main:app",
            "--host", "0.0.0.0",
            "--port", "8000"
        ]
        self._start_process("backend", backend_command, cwd=SERVER_DIR)
        
        frontend_command = [NPX_EXEC_NAME, "serve", "-s", ".", "-l", str(FRONTEND_PORT)]
        self._start_process("frontend", frontend_command, cwd=INTERFACE_DIST_DIR)


    def stop_servers(self):
        self.log("Parando servidores...")
        for name in list(self.processes.keys()):
            self._stop_process(name)
        self.update_button_states(is_running=False)

    def _start_process(self, name, command, cwd):
        if not os.path.exists(cwd):
            self.log(f"ERRO: Diretório de trabalho não encontrado para '{name}': {cwd}")
            self.stop_servers()
            return
        try:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0,
                shell=IS_WINDOWS
            )
            self.processes[name] = {"process": process, "thread": None}

            thread = threading.Thread(target=self._enqueue_output, args=(process, name), daemon=True)
            thread.start()
            self.processes[name]["thread"] = thread
            self.log(f"Processo '{name}' iniciado com PID: {process.pid}")

        except FileNotFoundError:
            self.log(f"ERRO: Comando '{command[0]}' não encontrado. Verifique se está instalado e no PATH do sistema.")
            self.stop_servers()
        except Exception as e:
            self.log(f"ERRO ao iniciar o processo '{name}': {e}")
            self.stop_servers()

    def _stop_process(self, name):
        if name in self.processes:
            proc_info = self.processes.pop(name)
            process = proc_info["process"]
            if process.poll() is None:
                try:
                    self.log(f"Parando processo '{name}' (PID: {process.pid})...")
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.log(f"Processo '{name}' não terminou, forçando o encerramento.")
                    process.kill()
                except Exception as e:
                    self.log(f"Erro ao parar o processo '{name}': {e}")
            self.log(f"Processo '{name}' parado.")

    def _enqueue_output(self, process, name):
        try:
            for line in iter(process.stdout.readline, ''):
                self.log_queue.put(f"[{name.upper()}]: {line.strip()}")
            for line in iter(process.stderr.readline, ''):
                self.log_queue.put(f"[{name.upper()} ERROR]: {line.strip()}")
        except Exception as e:
            self.log_queue.put(f"[ERROR ENQUEUE {name.upper()}]: {e}")
        finally:
             self.log_queue.put(f"[{name.upper()}]: Processo finalizado.")

    def check_log_queue(self):
        while not self.log_queue.empty():
            try:
                message = self.log_queue.get_nowait()
                self.log(message)
            except queue.Empty:
                pass
        self.root.after(100, self.check_log_queue)

    def log(self, message):
        if self.debug_text.winfo_exists():
            self.debug_text.config(state=tk.NORMAL)
            self.debug_text.insert(tk.END, f"{message}\n")
            self.debug_text.see(tk.END)
            self.debug_text.config(state=tk.DISABLED)

    def configure_venv(self):
        self.log("Iniciando configuração do ambiente virtual...")
        self.update_button_states(is_running=True) # Temporarily disable buttons
        thread = threading.Thread(target=self._run_venv_setup, daemon=True)
        thread.start()

    def _run_venv_setup(self):
        try:
            if not os.path.exists(REQUIREMENTS_FILE):
                self.log_queue.put(f"ERRO: 'requirements.txt' não encontrado em: {REQUIREMENTS_FILE}")
                return
            if not os.path.exists(VENV_PATH):
                self.log_queue.put("Ambiente virtual não encontrado. Criando...")
                subprocess.run([sys.executable, "-m", "venv", "venv"], cwd=SERVER_DIR, check=True, capture_output=True, text=True)
                self.log_queue.put("Ambiente virtual criado com sucesso.")
            else:
                self.log_queue.put("Ambiente virtual já existe.")

            self.log_queue.put("Instalando dependências de 'requirements.txt'...")
            install_process = subprocess.Popen([VENV_PIP_EXECUTABLE, "install", "-r", REQUIREMENTS_FILE], cwd=SERVER_DIR,
                                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
                                               creationflags=subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0)
            self._enqueue_output(install_process, "pip-install")
        except Exception as e:
            self.log_queue.put(f"Ocorreu um erro inesperado durante a configuração: {e}")
        finally:
            self.root.after(0, lambda: self.update_button_states(is_running=False))
            self.log_queue.put("Configuração do ambiente finalizada.")

    def build_frontend(self):
        self.log("Iniciando o build do frontend... Isso pode levar alguns minutos.")
        self.update_button_states(is_running=True)
        thread = threading.Thread(target=self._run_frontend_build, daemon=True)
        thread.start()

    def _run_frontend_build(self):
        try:
            install_process = subprocess.Popen(["npm", "install"], cwd=INTERFACE_DIR,
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
                                             shell=IS_WINDOWS,
                                             creationflags=subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0)
            self._enqueue_output(install_process, "npm-install")
            install_process.wait()
            self.log_queue.put("Instalação das dependências do frontend finalizada.")
            self.log_queue.put("Iniciando o build...")
            build_process = subprocess.Popen(["npm", "run", "build"], cwd=INTERFACE_DIR,
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
                                             shell=IS_WINDOWS,
                                             creationflags=subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0)
            self._enqueue_output(build_process, "npm-build")
            build_process.wait()
        except Exception as e:
            self.log_queue.put(f"Ocorreu um erro inesperado durante o build: {e}")
        finally:
            self.root.after(0, lambda: self.update_button_states(is_running=False))
            self.log_queue.put("Build do frontend finalizado.")

    def open_in_browser(self):
        if "frontend" in self.processes:
            self.log(f"Abrindo {WEBSERVER_URL} no navegador...")
            webbrowser.open_new_tab(WEBSERVER_URL)
        else:
            self.log("ERRO: O servidor web não está rodando.")

    def update_button_states(self, is_running):
        state = tk.DISABLED if is_running else tk.NORMAL
        self.start_button.config(state=tk.DISABLED if is_running else tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL if is_running else tk.DISABLED)
        self.browser_button.config(state=tk.NORMAL if is_running else tk.DISABLED)
        self.config_button.config(state=state)
        self.build_button.config(state=state)
        self.settings_button.config(state=state)

    def on_close(self):
        if self.processes:
            if messagebox.askyesno("Confirmar Saída", "Os servidores ainda estão rodando. Deseja pará-los e sair?"):
                self.stop_servers()
                self.root.destroy()
        else:
            self.root.destroy()
            
    def open_settings_window(self):
        SettingsWindow(self.root, self)

class SettingsWindow(Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.title("Edit Settings")
        self.geometry("450x200")
        self.app = app
        self.resizable(False, False)

        self.data_source_var = StringVar()
        self.serial_port_var = StringVar()

        self.load_current_settings()
        self.create_widgets()

    def create_widgets(self):
        main_frame = Frame(self, padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)

        Label(main_frame, text="Data Source:", font=("Helvetica", 10)).grid(row=0, column=0, sticky="w", pady=10, padx=5)
        data_source_options = ["serial", "mqtt", "simulator"]
        ds_menu = OptionMenu(main_frame, self.data_source_var, *data_source_options)
        ds_menu.grid(row=0, column=1, sticky="ew")

        Label(main_frame, text="Serial Port:", font=("Helvetica", 10)).grid(row=1, column=0, sticky="w", pady=10, padx=5)
        
        # --- NEW: Auto-detect serial ports ---
        ports = serial.tools.list_ports.comports()
        port_names = [port.device for port in ports]
        if not port_names:
            port_names.append("No ports found")
            if not self.serial_port_var.get():
                 self.serial_port_var.set(port_names[0])
        elif self.serial_port_var.get() not in port_names:
            self.serial_port_var.set(port_names[0]) # Default to the first available port

        port_menu = OptionMenu(main_frame, self.serial_port_var, *port_names)
        port_menu.grid(row=1, column=1, sticky="ew")

        save_button = tk.Button(main_frame, text="Save Settings", command=self.save_settings, bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold"))
        save_button.grid(row=2, column=0, columnspan=2, pady=20, sticky="ew")


    def load_current_settings(self):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                content = f.read()
            
            ds_match = re.search(r"data_source:\s*Literal\[.*]\s*=\s*\"(.*?)\"", content)
            if ds_match: self.data_source_var.set(ds_match.group(1))

            sp_match = re.search(r"serial_port:\s*str\s*=\s*\"(.*?)\"", content)
            if sp_match: self.serial_port_var.set(sp_match.group(1))

        except Exception as e:
            self.app.log(f"Error loading settings: {e}")
            messagebox.showerror("Error", f"Could not load settings from {SETTINGS_FILE}")

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                content = f.read()

            new_data_source = self.data_source_var.get()
            new_serial_port = self.serial_port_var.get()

            if new_serial_port == "No ports found":
                messagebox.showwarning("Warning", "No serial port selected. Please connect a device.")
                return

            content = re.sub(r"(data_source:\s*Literal\[.*]\s*=\s*\").*?(\")", f"\\1{new_data_source}\\2", content)
            content = re.sub(r"(serial_port:\s*str\s*=\s*\").*?(\")", f"\\1{new_serial_port}\\2", content)

            with open(SETTINGS_FILE, 'w') as f:
                f.write(content)

            self.app.log(f"Settings saved: Source='{new_data_source}', Port='{new_serial_port}'")
            self.destroy()

        except Exception as e:
            self.app.log(f"Error saving settings: {e}")
            messagebox.showerror("Error", f"Could not save settings to {SETTINGS_FILE}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ServerManagerApp(root)
    root.mainloop()
