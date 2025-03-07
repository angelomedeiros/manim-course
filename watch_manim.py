import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import os
import sys
import signal
import psutil

WATCH_DIR = "."  # Diretório atual
# Use environment variables to set the Python path
COMMAND_TEMPLATE = "PYTHONPATH={project_root}:{project_root}/src manim --renderer=cairo -pqp {file} {scene}"

# Variável global para controle de processos ativos
current_process = None
lock = threading.Lock()
last_file = None
last_scene = None

def get_manim_class(file):
    """ Obtém a primeira classe do Manim no arquivo. """
    try:
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("class ") and "(Scene)" in line:
                    return line.split("class ")[1].split("(")[0].strip()
    except Exception as e:
        print(f"⚠️ Erro ao ler arquivo: {e}")
    return None

def kill_opengl_processes():
    """Mata todos os processos OpenGL relacionados ao Manim exceto o atual"""
    if current_process is None:
        return
        
    current_pid = current_process.pid
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Verifica se é um processo OpenGL do Manim, mas não o processo principal
            if proc.pid != current_pid and proc.info['name'] == 'python':
                cmdline = ' '.join(proc.info['cmdline'] if proc.info['cmdline'] else [])
                if 'manim' in cmdline and '--renderer=opengl' in cmdline:
                    print(f"🗑️ Removendo processo OpenGL extra (PID: {proc.pid})")
                    proc.terminate()
                    try:
                        proc.wait(timeout=2)
                    except:
                        proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def run_manim(file):
    """ Executa o Manim, recriando a instância quando o arquivo é alterado. """
    global current_process, last_file, last_scene

    # Ignora o próprio script
    if os.path.basename(file) == "watch_manim.py":
        return

    scene_name = get_manim_class(file)
    if not scene_name:
        print(f"⚠️ Nenhuma classe Manim encontrada em {file}.")
        return

    # Get the absolute path to the project root directory
    project_root = os.path.abspath(".")
    
    # Format the command with the project root and file path
    command = COMMAND_TEMPLATE.format(
        project_root=project_root,
        file=file,
        scene=scene_name
    )
    
    with lock:  # Evita execução concorrente
        # Sempre encerra o processo atual se for o mesmo arquivo
        if current_process and current_process.poll() is None:
            if file == last_file and scene_name == last_scene:
                print(f"🔄 Recriando instância para: {file} {scene_name}")
                current_process.terminate()
                try:
                    current_process.wait(timeout=2)
                except:
                    current_process.kill()
            else:
                # Se mudou o arquivo ou a cena, encerra o processo atual
                print(f"🔄 Mudando para: {file} {scene_name}")
                current_process.terminate()
                try:
                    current_process.wait(timeout=2)
                except:
                    current_process.kill()
        
        # Mata qualquer processo OpenGL extra que possa estar rodando
        kill_opengl_processes()
        
        print(f"🚀 Rodando: {file} {scene_name}")
        # Use shell=True to properly handle environment variables
        current_process = subprocess.Popen(command, shell=True)
        last_file = file
        last_scene = scene_name

class ManimHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified_time = {}
        self.debounce_time = 0.5  # Tempo mínimo entre execuções para o mesmo arquivo

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith(".py"):
            return

        current_time = time.time()
        last_time = self.last_modified_time.get(event.src_path, 0)
        
        # Verifica se o arquivo foi modificado recentemente para evitar múltiplas execuções
        if current_time - last_time < self.debounce_time:
            return
            
        self.last_modified_time[event.src_path] = current_time
        print(f"🔄 Arquivo modificado: {event.src_path}")
        time.sleep(0.2)  # Pequena pausa para garantir que o arquivo foi salvo completamente
        run_manim(event.src_path)

if __name__ == "__main__":
    # Mata qualquer processo OpenGL que possa estar rodando
    kill_opengl_processes()
    
    event_handler = ManimHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=True)  # Alterado para True para monitorar subdiretórios

    print("🔄 Monitorando mudanças em todos os subdiretórios... Pressione Ctrl+C para parar.")
    observer.start()

    try:
        while True:
            time.sleep(0.5)  # Loop principal mais responsivo
    except KeyboardInterrupt:
        if current_process:
            current_process.terminate()
        observer.stop()
        print("\n🛑 Monitoramento encerrado.")

    observer.join()
