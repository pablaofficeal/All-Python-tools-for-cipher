import os
import tkinter as tk
from tkinter import filedialog, scrolledtext
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.styles import get_style_by_name
from pygments.token import Token
from pygments.util import ClassNotFound

class SimpleIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Python IDE")
        self.root.geometry("800x600")

        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=80, height=20)
        self.text_area.pack(expand=True, fill='both')

        self.menu_bar = tk.Menu(self.root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_command(label="Save As", command=self.save_file_as)
        self.file_menu.add_command(label="Delete", command=self.delete_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.root.config(menu=self.menu_bar)

        self.current_file = None

        # Подсветка синтаксиса
        self.text_area.bind('<KeyRelease>', self.highlight_syntax)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, 'r') as file:
                content = file.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, content)
            self.current_file = file_path

    def save_file(self):
        if self.current_file:
            with open(self.current_file, 'w') as file:
                file.write(self.text_area.get(1.0, tk.END))
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.text_area.get(1.0, tk.END))
            self.current_file = file_path

    def delete_file(self):
        if self.current_file:
            os.remove(self.current_file)
            self.text_area.delete(1.0, tk.END)
            self.current_file = None

    def highlight_syntax(self, event=None):
        code = self.text_area.get(1.0, tk.END)
        self.text_area.mark_set(tk.INSERT, 1.0)
        self.text_area.mark_set(tk.END, tk.END)
        self.text_area.tag_remove("Token", 1.0, tk.END)

        lexer = PythonLexer()
        tokens = lex(code, lexer)

        for token_type, value in tokens:
            start_index = self.text_area.index(tk.INSERT)
            self.text_area.insert(tk.END, value)
            end_index = self.text_area.index(tk.INSERT)
            self.text_area.tag_add(str(token_type), start_index, end_index)
            self.text_area.tag_config(str(token_type), foreground=self.get_color(token_type))

    def get_color(self, token_type):
        style = get_style_by_name('monokai')
        return style.style_for_token(token_type)['color']

if __name__ == "__main__":
    root = tk.Tk()
    ide = SimpleIDE(root)
    root.mainloop()