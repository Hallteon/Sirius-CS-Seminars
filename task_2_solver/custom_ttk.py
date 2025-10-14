import tkinter as tk
from tkinter import ttk


class ColoredCombobox:
    def __init__(self, parent, values, colors, width=15, height=5):
        self.parent = parent
        self.values = values
        self.colors = colors
        self.width = width
        self.height = min(height, len(values))

        self.selected_value = tk.StringVar()
        self.frame = ttk.Frame(parent)

        self.entry = ttk.Entry(self.frame, textvariable=self.selected_value,
                               width=width, state='readonly')
        self.entry.grid(row=0, column=0, sticky='ew')

        self.button = ttk.Button(self.frame, text='▼', width=3,
                                 command=self.toggle_listbox)
        self.button.grid(row=0, column=1, padx=(2, 0))

        self.listbox_frame = ttk.Frame(parent, relief='solid', borderwidth=1)
        self.listbox = tk.Listbox(self.listbox_frame, width=width,
                                  height=self.height, exportselection=False)

        # Полоса прокрутки
        self.scrollbar = ttk.Scrollbar(self.listbox_frame, orient='vertical',
                                       command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=self.scrollbar.set)

        self.listbox.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')

        # Заполняем список с цветами
        for i, (value, color) in enumerate(zip(values, colors)):
            self.listbox.insert(i, value)
            self.listbox.itemconfig(i, {'fg': color, 'bg': 'white'})

        # Привязываем события
        self.entry.bind('<Button-1>', self.toggle_listbox)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        self.listbox.bind('<FocusOut>', self.on_focus_out)
        self.listbox.bind('<Escape>', self.hide_listbox)
        self.listbox.bind('<Return>', self.on_select)

        self.is_listbox_visible = False
        self.frame.columnconfigure(0, weight=1)

    def toggle_listbox(self, event=None):
        if not self.is_listbox_visible:
            self.show_listbox()
        else:
            self.hide_listbox()

    def show_listbox(self):
        x = self.frame.winfo_x()
        y_bottom = self.frame.winfo_y() + self.frame.winfo_height()
        frame_width = self.frame.winfo_width()

        parent_height = self.parent.winfo_height()
        available_space_bottom = parent_height - y_bottom

        item_height = 20
        desired_height = min(self.height * item_height, 200)

        if available_space_bottom >= desired_height:
            y = y_bottom
            listbox_height = min(desired_height, available_space_bottom)
        else:
            y_top = self.frame.winfo_y() - desired_height
            y = max(0, y_top)
            listbox_height = desired_height

        # Позиционируем список
        self.listbox_frame.place(
            x=x,
            y=y,
            width=frame_width,
            height=listbox_height
        )
        self.listbox_frame.lift()

        visible_items = min(self.height, listbox_height // item_height)
        self.listbox.configure(height=visible_items)

        current_value = self.selected_value.get()
        if current_value in self.values:
            index = self.values.index(current_value)
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(index)
            self.listbox.see(index)

        self.listbox.focus_set()
        self.is_listbox_visible = True

    def hide_listbox(self, event=None):
        self.listbox_frame.place_forget()
        self.is_listbox_visible = False

    def on_focus_out(self, event):
        current_focus = self.parent.focus_get()
        our_widgets = [self.entry, self.button, self.listbox, self.listbox_frame]

        if current_focus not in our_widgets:
            self.hide_listbox()

    def on_select(self, event=None):
        if self.listbox.curselection():
            index = self.listbox.curselection()[0]
            selected_value = self.values[index]
            selected_color = self.colors[index]

            self.selected_value.set(selected_value)
            self.entry.configure(foreground=selected_color)
            self.hide_listbox()

    # Методы для размещения в grid
    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def grid_remove(self):
        self.hide_listbox()
        self.frame.grid_remove()

    def grid_forget(self):
        self.hide_listbox()
        self.frame.grid_forget()

    def grid_info(self):
        return self.frame.grid_info()

    # Методы для pack (если понадобятся)
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def pack_forget(self):
        self.hide_listbox()
        self.frame.pack_forget()

    def pack_info(self):
        return self.frame.pack_info()

    # Методы для place (если понадобятся)
    def place(self, **kwargs):
        self.frame.place(**kwargs)

    def place_forget(self):
        self.hide_listbox()
        self.frame.place_forget()

    def place_info(self):
        return self.frame.place_info()

    def get(self):
        return self.selected_value.get()

    def set(self, value):
        if value in self.values:
            self.selected_value.set(value)
            index = self.values.index(value)
            self.entry.configure(foreground=self.colors[index])

    def bind(self, sequence, func):
        self.entry.bind(sequence, func)

    def destroy(self):
        try:
            self.hide_listbox()
            self.listbox.destroy()
            self.scrollbar.destroy()
            self.listbox_frame.destroy()
            self.entry.destroy()
            self.button.destroy()
            self.frame.destroy()
        except tk.TclError:
            pass