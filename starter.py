import tkinter as tk
from tkinter import scrolledtext, messagebox, Toplevel, StringVar, OptionMenu, Entry, Frame, Label
import subprocess
import threading
import os
import sys
import webbrowser
import queue
import re

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
# The port can be found in `package.json` or `vite.config.ts`. Default for `serve` is 3000.
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
    """
    A robust Tkinter application to manage the Mangue Telemetry servers.
    Features non-blocking process handling to prevent UI freezing.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Servidores - Mangue Telemetry")
        self.root.geometry("850x650")

        self.processes = {}
        self.log_queue = queue.Queue()

        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.log("Bem-vindo ao Gerenciador de Servidores da Mangue Telemetry!")
        self.log("Verifique se o ambiente virtual e as dependências estão configurados.")
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


        # Pack buttons with expansion
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

        # --- KEY CHANGE HERE ---
        # Launch uvicorn directly to avoid the reloader subprocess issues on Windows
        backend_command = [
            VENV_PYTHON_EXECUTABLE,
            "-m", "uvicorn",
            "main:app",
            "--host", "0.0.0.0",
            "--port", "8000"
        ]
        self._start_process("backend", backend_command, cwd=SERVER_DIR)
        
        # Start frontend server
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
                shell=IS_WINDOWS # Use shell=True on Windows for .cmd files
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
        self.config_button.config(state=tk.DISABLED)
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
            self.root.after(0, lambda: self.config_button.config(state=tk.NORMAL))
            self.log_queue.put("Configuração do ambiente finalizada.")


    def build_frontend(self):
        self.log("Iniciando o build do frontend... Isso pode levar alguns minutos.")
        self.build_button.config(state=tk.DISABLED)
        thread = threading.Thread(target=self._run_frontend_build, daemon=True)
        thread.start()

    def _run_frontend_build(self):
        try:
            # Use shell=True for Windows to correctly resolve npm.cmd and npx.cmd
            install_process = subprocess.Popen(["npm", "install"], cwd=INTERFACE_DIR,
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
                                             shell=IS_WINDOWS,
                                             creationflags=subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0)
            self._enqueue_output(install_process, "npm-install")
            install_process.wait()

            build_process = subprocess.Popen(["npm", "run", "build"], cwd=INTERFACE_DIR,
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
                                             shell=IS_WINDOWS,
                                             creationflags=subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0)
            self._enqueue_output(build_process, "npm-build")
            build_process.wait()
        except Exception as e:
            self.log_queue.put(f"Ocorreu um erro inesperado durante o build: {e}")
        finally:
            self.root.after(0, lambda: self.build_button.config(state=tk.NORMAL))
            self.log_queue.put("Build do frontend finalizado.")

    def open_in_browser(self):
        if "frontend" in self.processes:
            self.log(f"Abrindo {WEBSERVER_URL} no navegador...")
            webbrowser.open_new_tab(WEBSERVER_URL)
        else:
            self.log("ERRO: O servidor web não está rodando.")

    def update_button_states(self, is_running):
        self.start_button.config(state=tk.DISABLED if is_running else tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL if is_running else tk.DISABLED)
        self.browser_button.config(state=tk.NORMAL if is_running else tk.DISABLED)
        self.config_button.config(state=tk.DISABLED if is_running else tk.NORMAL)
        self.build_button.config(state=tk.DISABLED if is_running else tk.NORMAL)
        self.settings_button.config(state=tk.DISABLED if is_running else tk.NORMAL)


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
        self.geometry("400x200")
        self.app = app

        self.data_source_var = StringVar()
        self.serial_port_var = StringVar()

        self.load_current_settings()
        self.create_widgets()

    def create_widgets(self):
        main_frame = Frame(self, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        Label(main_frame, text="Data Source:").grid(row=0, column=0, sticky="w", pady=5)
        data_source_options = ["serial", "mqtt", "simulator"]
        OptionMenu(main_frame, self.data_source_var, *data_source_options).grid(row=0, column=1, sticky="ew")

        Label(main_frame, text="Serial Port:").grid(row=1, column=0, sticky="w", pady=5)
        Entry(main_frame, textvariable=self.serial_port_var).grid(row=1, column=1, sticky="ew")

        save_button = tk.Button(main_frame, text="Save", command=self.save_settings)
        save_button.grid(row=2, column=0, columnspan=2, pady=10)

    def load_current_settings(self):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                content = f.read()
                data_source_match = re.search(r"data_source:\s*Literal\[.*]\s*=\s*\"(.*?)\"", content)
                if data_source_match:
                    self.data_source_var.set(data_source_match.group(1))

                serial_port_match = re.search(r"serial_port:\s*str\s*=\s*\"(.*?)\"", content)
                if serial_port_match:
                    self.serial_port_var.set(serial_port_match.group(1))
        except Exception as e:
            self.app.log(f"Error loading settings: {e}")
            messagebox.showerror("Error", f"Could not load settings from {SETTINGS_FILE}")

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                content = f.read()

            new_data_source = self.data_source_var.get()
            new_serial_port = self.serial_port_var.get()

            content = re.sub(r"(data_source:\s*Literal\[.*]\s*=\s*\").*?(\")", f"\\1{new_data_source}\\2", content)
            content = re.sub(r"(serial_port:\s*str\s*=\s*\").*?(\")", f"\\1{new_serial_port}\\2", content)

            with open(SETTINGS_FILE, 'w') as f:
                f.write(content)

            self.app.log("Settings saved successfully.")
            self.destroy()

        except Exception as e:
            self.app.log(f"Error saving settings: {e}")
            messagebox.showerror("Error", f"Could not save settings to {SETTINGS_FILE}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ServerManagerApp(root)
    root.mainloop()
