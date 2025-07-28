import tkinter as tk

class EditableLabel(tk.Label):
    def __init__(self, parent, text="", font=None, **kwargs):
        super().__init__(parent, text=text, font=font, **kwargs)
        self._parent = parent
        self._text = text
        self._font = font
        self.bind("<Double-1>", self._on_double_click)

    def Get(self):
        return self.cget("text")
    
    def _on_double_click(self, event):
        self._entry = tk.Entry(self._parent, font=self._font, width=0)
        self._entry.insert(0, self.cget("text"))
        self._entry.select_range(0, tk.END)
        self._entry.focus()
        self._entry.grid(row=self.grid_info()["row"], column=self.grid_info()["column"], sticky="nsew")

        self._entry.bind("<Return>", self._save)
        self._entry.bind("<FocusOut>", self._save)
        self._entry.bind("<Escape>", self._cancel)

        self.grid_remove()

    def _save(self, event=None):
        new_text = self._entry.get()
        self._text = new_text
        self.configure(text=new_text)
        self._entry.destroy()
        self.grid()

    def _cancel(self, event=None):
        self._entry.destroy()
        self.grid()