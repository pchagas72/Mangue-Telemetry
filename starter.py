import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading
import os
import signal
import sys
import webbrowser

# Constants for file paths based on the project structure
INTERFACE_DIST_DIR = os.path.join(os.path.dirname(__file__), 'interface', 'dist')
SERVER_DIR = os.path.join(os.path.dirname(__file__), 'server')
SERVER_RUN_FILE = os.path.join(SERVER_DIR, 'run.py')
REQUIREMENTS_FILE = os.path.join(SERVER_DIR, 'requirements.txt')
VENV_PATH = os.path.join(SERVER_DIR, 'venv')
WEBSERVER_URL = "http://localhost:3000"

# --- Novo: Determinar o caminho do executável Python e pip dentro do venv ---
# Define o nome do executável com base no sistema operacional
PYTHON_EXECUTABLE_NAME = 'python.exe' if sys.platform == 'win32' else 'python'
PIP_EXECUTABLE_NAME = 'pip.exe' if sys.platform == 'win32' else 'pip'
# Constrói o caminho completo para os executáveis
VENV_PYTHON_EXECUTABLE = os.path.join(VENV_PATH, 'Scripts' if sys.platform == 'win32' else 'bin', PYTHON_EXECUTABLE_NAME)
VENV_PIP_EXECUTABLE = os.path.join(VENV_PATH, 'Scripts' if sys.platform == 'win32' else 'bin', PIP_EXECUTABLE_NAME)
# ----------------------------------------------------------------------------


class ServerManagerApp:
    """
    A simple Tkinter application to manage two server processes.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Servidores")
        self.root.geometry("800x600")
        
        # Keep track of the running processes
        self.serve_process = None
        self.run_py_process = None

        # Create and pack UI elements
        self.create_widgets()
        
        # Bind the window closing event to a handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        """
        Sets up the main GUI layout with buttons and a debug terminal.
        """
        # Main frame for buttons and terminal
        main_frame = tk.Frame(self.root, padx=20, pady=20, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Button frame at the top
        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(pady=10)

        # Start Servers Button
        self.start_button = tk.Button(
            button_frame, 
            text="Iniciar Servidores", 
            command=self.start_servers,
            font=("Helvetica", 16, "bold"),
            bg="#4CAF50", fg="white",
            activebackground="#45a049",
            bd=0, relief=tk.FLAT,
            padx=20, pady=10,
            cursor="hand2"
        )
        self.start_button.pack(side=tk.LEFT, padx=10)

        # Stop Servers Button
        self.stop_button = tk.Button(
            button_frame, 
            text="Parar Servidores", 
            command=self.stop_servers,
            font=("Helvetica", 16, "bold"),
            bg="#F44336", fg="white",
            activebackground="#da190b",
            bd=0, relief=tk.FLAT,
            padx=20, pady=10,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=10)

        # Configure Venv Button
        self.config_button = tk.Button(
            button_frame,
            text="Configurar Ambiente",
            command=self.configure_venv,
            font=("Helvetica", 16, "bold"),
            bg="#2196F3", fg="white",
            activebackground="#1e88e5",
            bd=0, relief=tk.FLAT,
            padx=20, pady=10,
            cursor="hand2"
        )
        self.config_button.pack(side=tk.LEFT, padx=10)

        # New: Open Browser Button
        self.browser_button = tk.Button(
            button_frame,
            text="Abrir no Navegador",
            command=self.open_in_browser,
            font=("Helvetica", 16, "bold"),
            bg="#FFC107", fg="black",
            activebackground="#ffb300",
            bd=0, relief=tk.FLAT,
            padx=20, pady=10,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.browser_button.pack(side=tk.LEFT, padx=10)

        # Debug Terminal Label
        debug_label = tk.Label(
            main_frame, 
            text="Terminal de Depuração:", 
            font=("Helvetica", 12, "bold"),
            bg="#f0f0f0",
            anchor="w"
        )
        debug_label.pack(fill=tk.X, pady=(10, 5))

        # Debug Terminal (ScrolledText)
        self.debug_text = scrolledtext.ScrolledText(
            main_frame, 
            wrap=tk.WORD, 
            state=tk.DISABLED,
            font=("Courier New", 10),
            bg="#2c3e50", fg="#ecf0f1",
            insertbackground="#ecf0f1",
            relief=tk.FLAT
        )
        self.debug_text.pack(fill=tk.BOTH, expand=True)

    def start_servers(self):
        """
        Starts the `npx serve` and `run.py` processes in separate threads.
        """
        if self.serve_process or self.run_py_process:
            self.log("Servidores já estão rodando.")
            return

        self.log("Iniciando servidores...")
        
        # Enable the stop button and disable the start button
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.browser_button.config(state=tk.NORMAL)

        # Start the first server (npx serve)
        self.serve_thread = threading.Thread(target=self._start_serve_process, daemon=True)
        self.serve_thread.start()

        # Start the second server (run.py)
        self.run_py_thread = threading.Thread(target=self._start_run_py_process, daemon=True)
        self.run_py_thread.start()

    def _start_serve_process(self):
        """
        Helper method to run the npx serve command.
        """
        try:
            # Change directory to the interface/dist folder
            original_dir = os.getcwd()
            os.chdir(INTERFACE_DIST_DIR)
            self.log(f"Executando 'npx serve -s .' no diretório: {os.getcwd()}")
            
            self.serve_process = subprocess.Popen(
                ["npx", "serve", "-s", "."],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Change back to the original directory
            os.chdir(original_dir)
            
            # Read and log the output in a separate thread to prevent blocking
            self._log_process_output(self.serve_process, "NPM Serve")
        except FileNotFoundError:
            self.log("ERRO: 'npx' não foi encontrado. Certifique-se de que o Node.js e o npm estão instalados e no PATH.")
            self.stop_servers()
        except Exception as e:
            self.log(f"ERRO ao iniciar o servidor NPM: {e}")
            self.stop_servers()

    def _start_run_py_process(self):
        """
        Helper method to run the run.py file using the venv's Python interpreter.
        """
        try:
            # --- Modificado para usar o executável do venv ---
            self.log(f"Executando '{VENV_PYTHON_EXECUTABLE} {SERVER_RUN_FILE}' a partir do diretório: {SERVER_DIR}")
            self.run_py_process = subprocess.Popen(
                [VENV_PYTHON_EXECUTABLE, SERVER_RUN_FILE],
                cwd=SERVER_DIR,  # This ensures the process starts in the correct directory
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            # ---------------------------------------------------
            
            # Read and log the output in a separate thread
            self._log_process_output(self.run_py_process, "run.py")
        except FileNotFoundError:
            self.log("ERRO: O arquivo 'run.py' ou o executável do venv não foi encontrado.")
            self.stop_servers()
        except Exception as e:
            self.log(f"ERRO ao iniciar o servidor Python: {e}")
            self.stop_servers()

    def _log_process_output(self, process, process_name):
        """
        Reads output from a subprocess and logs it to the text widget.
        This runs in a separate thread.
        """
        try:
            for line in iter(process.stdout.readline, ''):
                self.log(f"[{process_name}]: {line.strip()}")
            for line in iter(process.stderr.readline, ''):
                self.log(f"[{process_name} ERROR]: {line.strip()}")
            
            process.stdout.close()
            process.stderr.close()
            process.wait()
            self.log(f"[{process_name}]: Processo finalizado.")
        except Exception as e:
            self.log(f"ERRO ao ler a saída do processo {process_name}: {e}")

    def stop_servers(self):
        """
        Stops all running server processes and cleans up.
        """
        self.log("Parando servidores...")
        
        # Stop npx serve process
        if self.serve_process and self.serve_process.poll() is None:
            self.log("Parando processo 'npx serve'...")
            self.serve_process.terminate()
            # Wait for the process to exit
            self.serve_process.wait()
            self.log("'npx serve' parado.")
        self.serve_process = None

        # Stop run.py process
        if self.run_py_process and self.run_py_process.poll() is None:
            self.log("Parando processo 'run.py'...")
            self.run_py_process.terminate()
            # Wait for the process to exit
            self.run_py_process.wait()
            self.log("'run.py' parado.")
        self.run_py_process = None

        self.log("Servidores parados.")
        
        # Enable the start button and disable the stop button
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.browser_button.config(state=tk.DISABLED)
        
    def log(self, message):
        """
        Thread-safe method to update the debug terminal.
        """
        # Schedule the update on the main thread using root.after
        self.root.after(0, self._append_to_debug_text, message)

    def _append_to_debug_text(self, message):
        """
        Appends a message to the debug terminal widget.
        """
        self.debug_text.config(state=tk.NORMAL)
        self.debug_text.insert(tk.END, message + "\n")
        self.debug_text.see(tk.END) # Auto-scroll to the end
        self.debug_text.config(state=tk.DISABLED)

    def configure_venv(self):
        """
        Creates a virtual environment and installs dependencies from requirements.txt.
        This is run in a separate thread to prevent the UI from freezing.
        """
        self.log("Iniciando a configuração do ambiente virtual...")
        self.config_button.config(state=tk.DISABLED)
        
        config_thread = threading.Thread(target=self._run_venv_setup, daemon=True)
        config_thread.start()

    def _run_venv_setup(self):
        """
        Helper method to execute the venv and pip commands.
        """
        try:
            # Check if requirements.txt exists
            if not os.path.exists(REQUIREMENTS_FILE):
                self.log(f"ERRO: Arquivo 'requirements.txt' não encontrado em: {REQUIREMENTS_FILE}")
                return
            
            self.log("Verificando se o ambiente virtual já existe...")
            if not os.path.exists(VENV_PATH):
                self.log("Ambiente virtual não encontrado. Criando...")
                subprocess.run(
                    [sys.executable, "-m", "venv", "venv"],
                    cwd=SERVER_DIR,
                    check=True,
                    capture_output=True,
                    text=True
                )
                self.log("Ambiente virtual criado com sucesso.")
            else:
                self.log("Ambiente virtual já existe.")
                
            self.log("Instalando dependências de 'requirements.txt'...")
            
            # --- Modificado para usar o executável do pip do venv ---
            install_process = subprocess.Popen(
                [VENV_PIP_EXECUTABLE, "install", "-r", REQUIREMENTS_FILE],
                cwd=SERVER_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            # -------------------------------------------------------
            
            self._log_process_output(install_process, "Instalação")

        except FileNotFoundError as e:
            self.log(f"ERRO: Comando não encontrado durante a configuração: {e}")
        except subprocess.CalledProcessError as e:
            self.log(f"ERRO durante a criação do venv: {e.stderr}")
        except Exception as e:
            self.log(f"Ocorreu um erro inesperado: {e}")
        finally:
            self.log("Configuração do ambiente virtual finalizada.")
            self.root.after(0, self.config_button.config, {'state': tk.NORMAL})
            
    def open_in_browser(self):
        """
        Opens the web interface URL in the default browser.
        """
        if self.serve_process and self.serve_process.poll() is None:
            self.log(f"Abrindo {WEBSERVER_URL} no navegador...")
            try:
                webbrowser.open_new_tab(WEBSERVER_URL)
            except webbrowser.Error:
                self.log("ERRO: Não foi possível abrir o navegador. Por favor, abra o URL manualmente.")
        else:
            self.log("ERRO: O servidor web não está rodando. Por favor, inicie os servidores primeiro.")
            
    def on_close(self):
        """
        Handler for the window close event to ensure processes are terminated.
        """
        self.stop_servers()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerManagerApp(root)
    root.mainloop()
