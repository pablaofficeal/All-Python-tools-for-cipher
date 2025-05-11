import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from PIL import Image, ImageTk

class DiagramApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Diagram Builder")
        
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        self.toolbar = tk.Frame(self.root)
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.create_buttons()
        self.custom_shapes = []
        
    def create_buttons(self):
        btn_create = tk.Button(self.toolbar, text="Create Diagram", command=self.create_diagram)
        btn_create.pack(side=tk.LEFT, padx=2, pady=2)
        
        btn_export = tk.Button(self.toolbar, text="Export Diagram", command=self.export_diagram)
        btn_export.pack(side=tk.LEFT, padx=2, pady=2)
        
        btn_save = tk.Button(self.toolbar, text="Save Diagram", command=self.save_diagram)
        btn_save.pack(side=tk.LEFT, padx=2, pady=2)
        
        btn_add_shape = tk.Button(self.toolbar, text="Add Custom Shape", command=self.add_custom_shape)
        btn_add_shape.pack(side=tk.LEFT, padx=2, pady=2)
        
    def create_diagram(self):
        self.ax.clear()
        self.ax.plot([0, 1, 2, 3], [0, 1, 4, 9])
        self.canvas.draw()
        
    def export_diagram(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            self.fig.savefig(file_path)
            messagebox.showinfo("Export", "Diagram exported successfully!")
        
    def save_diagram(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            self.fig.savefig(file_path)
            messagebox.showinfo("Save", "Diagram saved successfully!")
        
    def add_custom_shape(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            img = Image.open(file_path)
            img = img.resize((50, 50), Image.ANTIALIAS)
            img_tk = ImageTk.PhotoImage(img)
            self.custom_shapes.append(img_tk)
            
            label = tk.Label(self.root, image=img_tk)
            label.image = img_tk
            label.pack(side=tk.LEFT, padx=2, pady=2)
            
            label.bind("<Button-1>", self.on_shape_click)
            
    def on_shape_click(self, event):
        shape = event.widget
        shape.place(x=event.x_root - self.root.winfo_rootx(), y=event.y_root - self.root.winfo_rooty())

if __name__ == "__main__":
    root = tk.Tk()
    app = DiagramApp(root)
    root.mainloop()