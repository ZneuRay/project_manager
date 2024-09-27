import os
import subprocess
import threading
import queue
import tkinter as tk
from tkinter import scrolledtext

class Process:
  def __init__(self, project, btn_run_stop, status_indicator):
    self.project = project
    self.core = None
    self.stdout_thread = None
    self.stderr_thread = None
    self.queue = queue.Queue()
    self.btn_run_stop = btn_run_stop
    self.status_indicator = status_indicator

class ProjectManager:
  def __init__(self):
    try:
      from config import root_dir
      self.root_dir = root_dir
    except ImportError:
      print('Failed to import root_dir from config.py')
      exit(1)
    except AttributeError:
      print('root_dir not found in config.py')
      exit(1)
      
    if not self.root_dir:
      print('root_dir is empty, Please set root_dir in config.py')
      exit(1)
    
    try:
      from config import project_list
      self.project_list = project_list
    except ImportError:
      print('Failed to import project_list from config.py')
      exit(1)
    except AttributeError:
      print('project_list not found in config.py')
      exit(1)
      
    if not self.project_list:
      print('project_list is empty, Please add projects to config.py')
      exit(1)
    
    self.processes = {}
    self.npm_processes = {}
    
    self.root = tk.Tk()
    self.root.title('Node Project Manager')
    self.create_ui()
    
  def create_ui(self):
    
    project_frame = tk.Frame(self.root)
    project_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    for idx, project in enumerate(self.project_list):
      frame = tk.Frame(project_frame)
      frame.pack(fill=tk.X, padx=5, pady=5)
      
      status_indicator = tk.Label(frame, text='●', fg='red', width=2)
      status_indicator.pack(side=tk.LEFT, padx=5)
      
      label = tk.Label(frame, text=project, width=20)
      label.pack(side=tk.LEFT)
      
      btn_npm_install = tk.Button(frame, text='npm install', command=lambda p=project: self.npm_install(p))
      btn_npm_install.pack(side=tk.LEFT, padx=5)
      
      btn_run_stop = tk.Button(frame, text='Start', command=lambda p=project: self.toggle_project(p))
      btn_run_stop.pack(side=tk.LEFT, padx=5)
      
      btn_restart = tk.Button(frame, text='Restart', command=lambda p=project: self.restart_project(p))
      btn_restart.pack(side=tk.LEFT, padx=5)
      
      self.processes[project] = Process(project, btn_run_stop, status_indicator)
      self.npm_processes[project] = Process(project, None, None)
      
    control_frame = tk.Frame(project_frame)
    control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
    
    btn_run_all = tk.Button(control_frame, text='Start All', command=self.run_all)
    btn_run_all.pack(side=tk.LEFT, padx=5)
    
    btn_stop_all = tk.Button(control_frame, text='Stop All', command=self.stop_all)
    btn_stop_all.pack(side=tk.LEFT, padx=5)
    
    self.log_text = scrolledtext.ScrolledText(self.root, height=20)
    self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    self.log_text.tag_config('info', foreground='gray')
    self.log_text.tag_config('error', foreground='red')
    
  def log(self, title, message, log_type=None):
    self.log_text.insert(tk.END, f'[{title}]: {message}\n', log_type)
    self.log_text.see(tk.END)
    
  def log_error(self, message):
    self.log('Error', message, 'error')
    
  def log_info(self, message):
    self.log('Info', message, 'info')
      
  def toggle_project(self, project):
    process = self.processes[project]
    if process.core and process.core.poll() is None:
      self.stop_project(project)
    else:
      self.run_project(project)
      
  def npm_install(self, project):
    process = self.npm_processes[project]
    project_path = os.path.join(self.root_dir, project)
    if os.path.exists(os.path.join(project_path, 'package.json')):
      process.core = subprocess.Popen(
        ['npm', 'install'],
        cwd=project_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
      )

      q = process.queue

      stdout_thread = threading.Thread(
        target=self.read_output,
        args=(process.core.stdout, q, ''),
        daemon=True
      )

      stderr_thread = threading.Thread(
        target=self.read_output,
        args=(process.core.stderr, q, ''),
        daemon=True
      )

      stdout_thread.start()
      stderr_thread.start()

      process.stdout_thread = stdout_thread
      process.stderr_thread = stderr_thread
      
      def wait_for_npm_install():
        process.core.wait()
        process.core = None
        self.log_info(f'{project} npm install finished')
      
      threading.Thread(target=wait_for_npm_install, daemon=True).start()
    else:
      self.log_error(f'{project} package.json not found')
      
  def run_project(self, project):
    process = self.processes[project]
    if process.core and process.core.poll() is None:
      self.log_error(f'{project} already running')
      return
    
    project_path = os.path.join(self.root_dir, project)
    if os.path.exists(os.path.join(project_path, 'index.js')):
      self.log_info(f'{project} starting...')
      process.core = subprocess.Popen(
        ['node', 'index.js'],
        cwd=project_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
      )
      
      q = process.queue
      
      stdout_thread = threading.Thread(
        target=self.read_output,
        args=(process.core.stdout, q, f'{project} STDOUT:'),
        daemon=True
      )
      
      stderr_thread = threading.Thread(
        target=self.read_output,
        args=(process.core.stderr, q, f'{project} STDERR:'),
        daemon=True
      )
      
      stdout_thread.start()
      stderr_thread.start()
      
      process.stdout_thread = stdout_thread
      process.stderr_thread = stderr_thread
      
      process.btn_run_stop.config(text='Stop')
      process.status_indicator.config(fg='green')
    else:
      self.log_error(f'{project} index.js not found')
    
  def read_output(self, pipe, q, title):
    for line in iter(pipe.readline, ''):
      q.put(f'{title} {line.strip()}')
    pipe.close()
    
  def stop_project(self, project):
    process = self.processes[project]
    if process.core and process.core.poll() is None:
      process.core.terminate()
      process.core.wait()
      process.core = None
      process.btn_run_stop.config(text='Start')
      process.status_indicator.config(fg='red')
      self.log_info(f'{project} already stopped')
    else:
      self.log_error(f'{project} is not running')
    
  def restart_project(self, project):
    self.stop_project(project)
    self.run_project(project)
    
  def run_all(self):
    self.log_info('Starting all projects...')
    for project in self.project_list:
      self.run_project(project)
    self.log_info('All projects started')
      
  def stop_all(self):
    self.log_info('Stopping all projects...')
    for project in self.project_list:
      self.stop_project(project)
    self.log_info('All projects stopped')
    
  def run(self):
    self.root.protocol('WM_DELETE_WINDOW', self.on_close)
    self.check_queues()
    self.root.mainloop()
    
  def check_queues(self):
    for project in self.project_list:
      q = self.processes[project].queue
      while not q.empty():
        self.log(project, q.get())
        
      npm_q = self.npm_processes[project].queue
      while not npm_q.empty():
        self.log(project, npm_q.get())
        
    self.root.after(100, self.check_queues)
    
  def on_close(self):
    for project in self.project_list:
      core = self.processes[project].core
      if core and core.poll() is None:
        core.terminate()
        core.wait()
        
      npm_core = self.npm_processes[project].core
      if npm_core and npm_core.poll() is None:
        npm_core.terminate()
        npm_core.wait()
    
    self.root.destroy()
    
if __name__ == '__main__':
  app = ProjectManager()
  app.run()
  