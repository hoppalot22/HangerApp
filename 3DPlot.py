import tkinter as tk
from tkinter import filedialog
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
import traceback

class Node3DPlotter(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.figure = Figure(figsize=(5, 5))
        self.ax = self.figure.add_subplot(111, projection='3d')

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

        # Load Button
        self.load_button = tk.Button(self, text="Load XYZ File", command=self.load_data)
        self.load_button.pack()

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if not file_path:
            return

        try:
            header = 2
            data_start = 0
            df = pd.read_excel(file_path, sheet_name= "Piping Lengths", header=header)
            df = df.infer_objects()
            df = df.drop(data_start)
            df = df.fillna(0)

            print(df[["DX", "DY", "DZ"]])
            if not all(col in df.columns for col in ["DX", "DY", "DZ"]):
                tk.messagebox.showerror("Invalid Data", "File must contain X, Y, Z columns.")
                return

            self.plot_data(df)
        except Exception as e:
            print(e)
            traceback.print_exc()
            tk.messagebox.showerror("Error", message = str(e))

    def plot_data(self, df : pd.DataFrame):
        self.ax.clear()

        
        # Extract displacements
        dx = df["DX"]
        dy = df["DY"]
        dz = df["DZ"]

        # Cumulative sum to get absolute positions
        x = [0]
        y = [0]
        z = [0]

        for i in range(len(dx)):
            x.append(x[-1] + dx.iloc[i])
            y.append(y[-1] + dy.iloc[i])
            z.append(z[-1] + dz.iloc[i])
        self.ax.scatter(x, y, z, c='blue', marker='o')

        # Draw lines between consecutive nodes (can be changed)
        for i in range(len(df) - 1):
            self.ax.plot([x[i], x[i+1]], [y[i], y[i+1]], [z[i], z[i+1]], c='gray')

        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')

        self.figure.tight_layout()
        self.canvas.draw()

# Sample usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("3D Node Visualizer")
    plotter = Node3DPlotter(root)
    plotter.pack(fill="both", expand=True)
    root.mainloop()