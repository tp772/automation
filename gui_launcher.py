"""
Simple Tkinter GUI launcher for the Job Automation tool.
Provides buttons to run `main.py` with common flags and shows basic output.
"""
import subprocess
import threading
import os
import sys
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
from html.parser import HTMLParser
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable or 'python'


class BookmarkParser(HTMLParser):
    """Parse bookmarks from HTML export files"""
    def __init__(self):
        super().__init__()
        self.bookmarks = []
        self.current_link = None
        self.current_title = None
        self.in_h3 = False
        
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            attrs_dict = dict(attrs)
            self.current_link = attrs_dict.get('href', '')
        elif tag == 'h3':
            self.in_h3 = True
            
    def handle_endtag(self, tag):
        if tag == 'h3':
            self.in_h3 = False
            
    def handle_data(self, data):
        if self.current_link:
            title = data.strip()
            if title and title not in ['Bookmarks bar', 'Bookmarks']:
                self.bookmarks.append({'title': title, 'url': self.current_link})
            self.current_link = None


def parse_bookmarks(filepath: str):
    """Parse bookmarks from HTML file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            parser = BookmarkParser()
            parser.feed(f.read())
        return parser.bookmarks
    except Exception as e:
        print(f"Error parsing bookmarks: {e}")
        return []

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Job Automation Launcher')
        self.geometry('800x650')
        self.bookmarks = []
        
        self._build_ui()
        self._load_bookmarks()

    def _build_ui(self):
        # --- Config Frame ---
        frame = tk.Frame(self)
        frame.pack(fill=tk.X, padx=10, pady=8)

        tk.Label(frame, text='Config file:').grid(row=0, column=0, sticky='w')
        self.config_var = tk.StringVar(value=os.path.join(ROOT, 'config', 'config.json'))
        tk.Entry(frame, textvariable=self.config_var, width=60).grid(row=0, column=1, padx=6)
        tk.Button(frame, text='Browse', command=self.browse_config).grid(row=0, column=2)

        # --- Action Buttons ---
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10)

        tk.Button(btn_frame, text='Scrape (no apply)', width=18, command=self._run_scrape).pack(side=tk.LEFT, padx=6, pady=6)
        tk.Button(btn_frame, text='Test Mode (dry run)', width=18, command=self._run_test).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_frame, text='Run Full', width=18, command=self._run_full).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_frame, text='Open Logs', width=12, command=self.open_logs).pack(side=tk.RIGHT, padx=6)

        # --- Bookmarks Tab ---
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Output tab
        output_frame = tk.Frame(notebook)
        notebook.add(output_frame, text='Output')
        
        self.output = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=20)
        self.output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.output.configure(state='disabled')

        # Bookmarks tab
        bookmarks_frame = tk.Frame(notebook)
        notebook.add(bookmarks_frame, text='Job Board Bookmarks')
        
        btn_reload = tk.Button(bookmarks_frame, text='Reload Bookmarks', command=self._load_bookmarks)
        btn_reload.pack(fill=tk.X, padx=5, pady=5)
        
        self.bookmarks_list = tk.Listbox(bookmarks_frame, height=20)
        self.bookmarks_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.bookmarks_list.bind('<Double-Button-1>', self._open_selected_bookmark)
        
        tk.Button(bookmarks_frame, text='Open Selected', command=self._open_selected_bookmark).pack(fill=tk.X, padx=5, pady=5)

    def _load_bookmarks(self):
        """Load and display bookmarks from bookmarks.html"""
        bookmarks_file = os.path.join(ROOT, 'bookmarks.html')
        if os.path.exists(bookmarks_file):
            self.bookmarks = parse_bookmarks(bookmarks_file)
            self.bookmarks_list.delete(0, tk.END)
            for bm in self.bookmarks:
                self.bookmarks_list.insert(tk.END, f"{bm['title']}")
            self.append_output(f"Loaded {len(self.bookmarks)} bookmarks from bookmarks.html")
        else:
            self.append_output("bookmarks.html not found")

    def _open_selected_bookmark(self, event=None):
        """Open selected bookmark in browser"""
        selection = self.bookmarks_list.curselection()
        if selection:
            bm = self.bookmarks[selection[0]]
            try:
                webbrowser.open(bm['url'])
                self.append_output(f"Opened: {bm['title']}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open bookmark: {e}")

    def browse_config(self):
        path = filedialog.askopenfilename(initialdir=os.path.join(ROOT, 'config'), filetypes=[('JSON','*.json')])
        if path:
            self.config_var.set(path)

    def append_output(self, text: str):
        self.output.configure(state='normal')
        self.output.insert(tk.END, text + '\n')
        self.output.see(tk.END)
        self.output.configure(state='disabled')

    def _run_command(self, args: list):
        def target():
            try:
                cmd = [PYTHON, os.path.join(ROOT, 'main.py')] + args + ['--config', self.config_var.get()]
                self.append_output('Running: ' + ' '.join(cmd))
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=ROOT)
                for line in proc.stdout:
                    self.append_output(line.rstrip())
                proc.wait()
                self.append_output(f'Process exited with code {proc.returncode}')
                if proc.returncode != 0:
                    messagebox.showwarning('Finished', f'Process exited with code {proc.returncode}')
                else:
                    messagebox.showinfo('Finished', 'Process completed successfully')
            except Exception as e:
                self.append_output(f'Error running process: {e}')
                messagebox.showerror('Error', str(e))

        thread = threading.Thread(target=target, daemon=True)
        thread.start()

    def _run_scrape(self):
        self._run_command(['--no-apply'])

    def _run_test(self):
        self._run_command(['--test'])

    def _run_full(self):
        self._run_command([])

    def open_logs(self):
        log_path = os.path.join(ROOT, 'logs', 'automation.log')
        if os.path.exists(log_path):
            if sys.platform.startswith('win'):
                os.startfile(log_path)
            else:
                subprocess.Popen(['xdg-open', log_path])
        else:
            messagebox.showinfo('No Logs', 'Log file not found: ' + log_path)

if __name__ == '__main__':
    app = App()
    app.mainloop()
