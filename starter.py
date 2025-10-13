import tkinter as tk
from tkinter import scrolledtext, messagebox, Toplevel, StringVar, OptionMenu, Frame, Label
import subprocess
import threading
import os
import sys
import webbrowser
import queue
import re

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

# --- NEW: Configuration/Styling Constants for a "Cool" Look ---
DARK_BG = "#1e1e1e"
PANEL_BG = "#2c2c2c"
TEXT_COLOR = "#f0f0f0"
PRIMARY_COLOR = "#4a90e2"  # Blue for open dashboard
SUCCESS_COLOR = "#4CAF50"  # Green for Start
DANGER_COLOR = "#e53935"   # Red for Stop
ACTION_COLOR = "#FF9800"   # Orange/Amber for System Log Title

class ServerManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mangue Telemetry: Control Hub")
        self.root.geometry("850x650")
        self.root.configure(bg=DARK_BG)

        self.processes = {}
        self.log_queue = queue.Queue()

        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.log("Bem-vindo ao Gerenciador de Servidores da Mangue Telemetry!")
        self.log("Use 'Editar Settings' para configurar a fonte de dados e a porta serial.")
        self.check_log_queue()

    def create_widgets(self):
        # --- Main Frame ---
        main_frame = tk.Frame(self.root, padx=20, pady=20, bg=DARK_BG)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Title ---
        title_label = tk.Label(main_frame, text="MANGUE TELEMETRY CONTROL HUB", 
                                font=("Helvetica", 18, "bold"), 
                                fg=SUCCESS_COLOR, bg=DARK_BG, pady=10)
        title_label.pack(fill=tk.X)

        # --- Action Buttons Frame (Start/Stop/Browser) ---
        action_frame = tk.Frame(main_frame, bg=PANEL_BG, padx=15, pady=15, bd=0, relief=tk.FLAT)
        action_frame.pack(pady=15, fill=tk.X)
        
        self.start_button = self._create_button(action_frame, "▶ START SERVERS", self.start_servers, SUCCESS_COLOR)
        self.stop_button = self._create_button(action_frame, "■ STOP SERVERS", self.stop_servers, DANGER_COLOR, state=tk.DISABLED)
        self.browser_button = self._create_button(action_frame, "🌐 OPEN DASHBOARD", self.open_in_browser, PRIMARY_COLOR, state=tk.DISABLED)

        self.start_button.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        self.stop_button.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        self.browser_button.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

        # --- Utility Buttons Frame (Config/Build/Settings) ---
        utility_frame = tk.Frame(main_frame, bg=DARK_BG)
        utility_frame.pack(pady=(5, 20), fill=tk.X)

        self.config_button = self._create_button(utility_frame, "   CONFIGURE VENV", self.configure_venv, PANEL_BG, fg=TEXT_COLOR, active_bg=PRIMARY_COLOR)
        self.build_button = self._create_button(utility_frame, "📦 BUILD FRONTEND", self.build_frontend, PANEL_BG, fg=TEXT_COLOR, active_bg=PRIMARY_COLOR)
        self.settings_button = self._create_button(utility_frame, "🔧 EDIT SETTINGS", self.open_settings_window, PANEL_BG, fg=TEXT_COLOR, active_bg=PRIMARY_COLOR)
        
        for button in utility_frame.winfo_children():
            button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        # --- Debug/Log Section ---
        debug_label = tk.Label(main_frame, text="[ SYSTEM LOG / DEBUG TERMINAL ]", 
                                font=("Courier", 12, "bold"), 
                                fg=ACTION_COLOR, bg=DARK_BG, anchor="w", pady=5)
        debug_label.pack(fill=tk.X, pady=(10, 5))

        self.debug_text = scrolledtext.ScrolledText(
            main_frame, wrap=tk.WORD, state=tk.DISABLED,
            font=("Courier New", 10), bg="#111111", fg="#00FF00", # Classic hacker terminal look
            insertbackground="#00FF00", relief=tk.FLAT, bd=0
        )
        self.debug_text.pack(fill=tk.BOTH, expand=True)

    def _create_button(self, parent, text, command, bg_color, state=tk.NORMAL, fg="white", active_bg=None):
        return tk.Button(
            parent, text=text, command=command, font=("Helvetica", 11, "bold"),
            bg=bg_color, fg=fg, activebackground=active_bg or bg_color,
            bd=0, relief=tk.FLAT, padx=15, pady=10, cursor="hand2", state=state
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
                shell=IS_WINDOWS # Use shell=True on Windows for npx/npm to be found reliably
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
            
            # Simple color coding for better readability in the log
            if "ERRO:" in message or "ERROR" in message or "Fail" in message:
                self.debug_text.insert(tk.END, f"{message}\n", 'error')
                self.debug_text.tag_config('error', foreground=DANGER_COLOR)
            elif "SUCCESS" in message or "iniciado com PID" in message or "finalizada" in message or "conectado" in message:
                self.debug_text.insert(tk.END, f"{message}\n", 'success')
                self.debug_text.tag_config('success', foreground=SUCCESS_COLOR)
            elif "[SYSTEM LOG" in message:
                 self.debug_text.insert(tk.END, f"{message}\n", 'title')
                 self.debug_text.tag_config('title', foreground=ACTION_COLOR)
            else:
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
            install_process.wait()
            if install_process.returncode == 0:
                 self.log_queue.put("SUCCESS: Instalação de dependências do backend finalizada com sucesso.")
            else:
                 self.log_queue.put("ERROR: Instalação de dependências do backend falhou.")

        except Exception as e:
            self.log_queue.put(f"Ocorreu um erro inesperado durante a configuração: {e}")
        finally:
            self.root.after(0, lambda: self.update_button_states(is_running=False))
            self.log_queue.put("[SYSTEM LOG / DEBUG TERMINAL]")

    def build_frontend(self):
        self.log("Iniciando o build do frontend... Isso pode levar alguns minutos.")
        self.update_button_states(is_running=True)
        thread = threading.Thread(target=self._run_frontend_build, daemon=True)
        thread.start()

    def _run_frontend_build(self):
        try:
            self.log_queue.put("[NPM] Instalando dependências do frontend...")
            install_process = subprocess.Popen(["npm", "install"], cwd=INTERFACE_DIR,
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
                                             shell=IS_WINDOWS,
                                             creationflags=subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0)
            self._enqueue_output(install_process, "npm-install")
            install_process.wait()
            
            if install_process.returncode != 0:
                 self.log_queue.put("ERROR: Instalação das dependências do frontend falhou.")
                 return

            self.log_queue.put("Instalação das dependências do frontend concluída. Iniciando o build...")
            
            build_process = subprocess.Popen(["npm", "run", "build"], cwd=INTERFACE_DIR,
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
                                             shell=IS_WINDOWS,
                                             creationflags=subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0)
            self._enqueue_output(build_process, "npm-build")
            build_process.wait()

            if build_process.returncode == 0:
                 self.log_queue.put("SUCCESS: Build do frontend finalizado com sucesso. Pronto para iniciar!")
            else:
                 self.log_queue.put("ERROR: Build do frontend falhou.")

        except Exception as e:
            self.log_queue.put(f"Ocorreu um erro inesperado durante o build: {e}")
        finally:
            self.root.after(0, lambda: self.update_button_states(is_running=False))
            self.log_queue.put("[SYSTEM LOG / DEBUG TERMINAL]")

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
        SettingsWindow(self.root, self, DARK_BG, PANEL_BG, TEXT_COLOR, SUCCESS_COLOR)

class SettingsWindow(Toplevel):
    def __init__(self, parent, app, bg_color, panel_bg, text_color, button_color):
        super().__init__(parent)
        self.title("Configuration Settings")
        self.geometry("450x250") 
        self.app = app
        self.resizable(False, False)
        self.configure(bg=bg_color)

        self.data_source_var = StringVar()
        self.serial_port_var = StringVar()
        self.text_color = text_color
        self.panel_bg = panel_bg
        self.button_color = button_color

        self.load_current_settings()
        self.create_widgets()

    def create_widgets(self):
        main_frame = Frame(self, padx=20, pady=20, bg=self.panel_bg)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        main_frame.columnconfigure(1, weight=1)

        Label(main_frame, text="DATA SOURCE:", font=("Helvetica", 10, "bold"), 
              bg=self.panel_bg, fg=self.text_color).grid(row=0, column=0, sticky="w", pady=10, padx=5)
        
        data_source_options = ["serial", "mqtt", "simulator"]
        ds_menu = OptionMenu(main_frame, self.data_source_var, *data_source_options)
        ds_menu.config(bg=self.button_color, fg="white", activebackground=self.button_color, relief=tk.FLAT)
        ds_menu["menu"].config(bg=self.panel_bg, fg=self.text_color)
        ds_menu.grid(row=0, column=1, sticky="ew")

        Label(main_frame, text="SERIAL PORT:", font=("Helvetica", 10, "bold"), 
              bg=self.panel_bg, fg=self.text_color).grid(row=1, column=0, sticky="w", pady=10, padx=5)
        
        # --- NEW: Auto-detect serial ports ---
        ports = serial.tools.list_ports.comports()
        port_names = [port.device for port in ports]
        if not port_names:
            port_names.append("No ports found")
            if not self.serial_port_var.get() or self.serial_port_var.get() == "":
                 self.serial_port_var.set("No ports found")
        elif self.serial_port_var.get() not in port_names:
            self.serial_port_var.set(port_names[0]) # Default to the first available port

        port_menu = OptionMenu(main_frame, self.serial_port_var, *port_names)
        port_menu.config(bg=self.button_color, fg="white", activebackground=self.button_color, relief=tk.FLAT)
        port_menu["menu"].config(bg=self.panel_bg, fg=self.text_color)
        port_menu.grid(row=1, column=1, sticky="ew")

        save_button = tk.Button(main_frame, text="✅ SAVE & APPLY", command=self.save_settings, 
                                bg=self.button_color, fg="white", 
                                font=("Helvetica", 11, "bold"), bd=0, relief=tk.FLAT, pady=10)
        save_button.grid(row=2, column=0, columnspan=2, pady=30, sticky="ew")


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
                messagebox.showwarning("Warning", "No serial port selected. Please connect a device or select 'simulator'.")
                return

            content = re.sub(r"(data_source:\s*Literal\[.*]\s*=\s*\").*?(\")", f"\\1{new_data_source}\\2", content)
            content = re.sub(r"(serial_port:\s*str\s*=\s*\").*?(\")", f"\\1{new_serial_port}\\2", content)

            with open(SETTINGS_FILE, 'w') as f:
                f.write(content)

            self.app.log(f"SUCCESS: Settings saved: Source='{new_data_source}', Port='{new_serial_port}'")
            self.destroy()

        except Exception as e:
            self.app.log(f"Error saving settings: {e}")
            messagebox.showerror("Error", f"Could not save settings to {SETTINGS_FILE}")

if __name__ == "__main__":
    # --- ADD THIS SECTION ---
    # This environment variable forces Tcl/Tk to use the native Wayland
    # backend via D-Bus instead of XWayland, which often fixes freezes.
    if os.environ.get('WAYLAND_DISPLAY'):
        os.environ['TK_XIM_CLIENT'] = '1'
        os.environ['TK_XIM_SERVER'] = '1'
        # On some systems, setting the WM to D-Bus/Wayland is sufficient
        # On others, these two are necessary for stability
    # ------------------------
    
    root = tk.Tk()
    app = ServerManagerApp(root)
    root.mainloop()
