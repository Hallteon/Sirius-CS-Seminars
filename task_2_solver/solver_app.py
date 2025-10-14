import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from custom_ttk import ColoredCombobox
from auto_solver import AutoSolver


class VirtualKeyboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Виртуальная клавиатура")

        self.keyboard_layout = [['→', '¬', '(', ')'],
                                ['∧', '∨', '≡']]

        self.bool_combobox_values = ['True', 'False']
        self.default_combox_value = 'None'

        self.additional_keys = []

        self.matrix_widgets = {}
        self.result_widgets = {}

        self.matrix_table = None
        self.result_table = None

        self.answer_widget = None
        self.table_matrix_frame = None

        self.create_input_field()
        self.create_keyboard()
        self.create_input_matrix()

    def create_input_field(self):
        """Создает поле для ввода текста"""
        input_frame = ttk.Frame(self.root, padding="10")
        input_frame.pack(fill=tk.X)

        ttk.Label(input_frame, text="Ввод:").pack(side=tk.LEFT)

        self.table_expression = tk.Entry(input_frame, width=50, font=("Arial", 12))
        self.table_expression.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        ttk.Button(input_frame, text="Очистить", command=self.clear_table_expression).pack(side=tk.LEFT, padx=(10, 0))

        add_frame = ttk.Frame(self.root, padding="5")
        add_frame.pack(fill=tk.X)

        ttk.Label(add_frame, text="Добавить символы:").pack(side=tk.LEFT)

        self.add_table_expression = tk.Entry(add_frame, width=30, font=("Arial", 10))
        self.add_table_expression.pack(side=tk.LEFT, padx=(10, 0))

        ttk.Button(add_frame, text="Добавить", command=self.add_keys_from_string).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(add_frame, text="Сбросить", command=self.reset_keyboard).pack(side=tk.LEFT, padx=(5, 0))

    def create_input_matrix(self):
        self.input_table_frame = ttk.Frame(self.root, padding='10')
        self.input_table_frame.pack(fill=tk.X)

        self.table_rows_count = tk.Entry(self.input_table_frame, width=10, font=('Arial', 12))
        self.table_rows_count.pack(side=tk.LEFT)

        ttk.Label(self.input_table_frame, text='x').pack(side=tk.LEFT, padx=10)

        self.table_columns_count = tk.Entry(self.input_table_frame, width=10, font=('Arial', 12))
        self.table_columns_count.pack(side=tk.LEFT)

        ttk.Button(self.input_table_frame, text='Добавить матрицу', command=self.add_matrix).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(self.input_table_frame, text='Удалить матрицу', command=self.delete_matrix).pack(side=tk.LEFT, padx=(10, 0))

        self.answer_button = None

        self.answer_frame = ttk.Frame(self.root, padding='10')
        self.answer_frame.pack(side='top')

    def add_matrix(self):
        """Метод для создания таблицы булевых значений"""

        if '' not in [self.table_columns_count.get(), self.table_rows_count.get()]:
            self.table_matrix_frame = ttk.Frame(self.root, padding='10')
            self.table_matrix_frame.pack(fill=tk.BOTH, side='top', expand=True)

            self.matrix_table = [[None for j in range(int(self.table_columns_count.get()))] for i in
                                 range(int(self.table_rows_count.get()))]

            for i in range(int(self.table_rows_count.get())):
                for j in range(int(self.table_columns_count.get()) + 1):
                    if j != int(self.table_columns_count.get()):
                        table_bool = ttk.Combobox(self.table_matrix_frame,
                                                  values=self.bool_combobox_values + [self.default_combox_value],
                                                  state="readonly", width=15)
                        table_bool.set(self.default_combox_value)
                        table_bool.grid(row=i, column=j, padx=10, pady=10)

                        self.matrix_widgets[table_bool] = (i, j)

                    else:
                        result_bool = ColoredCombobox(self.table_matrix_frame,
                                                      values=self.bool_combobox_values, width=10,
                                                      colors=['green', 'red'])
                        result_bool.set('True')

                        result_bool.grid(row=i, column=j, padx=10, pady=10)

                        self.result_widgets[result_bool] = (i, j)

            if not self.answer_button:
                self.answer_button = ttk.Button(self.input_table_frame, text='Решить', command=self.add_answer)
                self.answer_button.pack(side=tk.RIGHT, padx=10)

        else:
            messagebox.showwarning('Предупреждение', 'Задайте размеры матрицы')

    def get_table_answer(self):
        for widget in self.matrix_widgets.items():
            self.matrix_table[widget[1][0]][widget[1][1]] = self.get_bool_value(widget[0].get())

        self.result_table = []

        for widget in self.result_widgets.items():
            self.result_table.append(self.get_bool_value(widget[0].get()))

        # print(self.process_expression(expression=self.table_expression.get()))
        # print(self.matrix_table)
        # print(self.result_table)
        # print(list(self.add_table_expression.get()))

        table_answer = AutoSolver(expression=self.process_expression(expression=self.table_expression.get()),
                            bool_table=self.matrix_table,
                            answer_column=self.result_table,
                            variables=list(self.add_table_expression.get())).get_answer()

        return table_answer

    def add_answer(self):
        if not self.answer_widget and '' not in [self.table_expression.get(), self.add_table_expression.get()]:
            answer = self.get_table_answer()
            # print(answer)

            self.answer_widget = ttk.Label(text=answer, foreground='green')
            self.answer_widget.pack(side=tk.LEFT, padx=10)

        else:
            messagebox.showwarning('Предупреждение', 'Задайте выражение и/или переменные')

    def process_expression(self, expression: str) -> str:
        for i, var in enumerate(self.add_table_expression.get()):
            expression = expression.replace(var, f'{{{i}}}')

        expression = expression.replace('→', '<=')
        expression = expression.replace('∧', 'and')
        expression = expression.replace('∨', 'or')
        expression = expression.replace('¬', 'not ')
        expression = expression.replace('≡', '==')

        print(expression)

        return expression

    def delete_matrix(self):
        if self.table_matrix_frame:
            for widgets_set in [self.matrix_widgets.keys(), self.result_widgets.keys()]:
                for btn in widgets_set:
                    btn.destroy()

            self.table_matrix_frame.destroy()

            self.matrix_widgets = {}
            self.result_widgets = {}

            self.table_matrix_frame = None

            self.answer_button.destroy()
            self.answer_button = None

            if self.answer_widget:
                self.answer_widget.destroy()
                self.answer_widget = None

        else:
            messagebox.showwarning('Предупреждение', 'Матрица ещё не создана')

    def create_keyboard(self):
        """Создает виртуальную клавиатуру"""
        self.keyboard_frame = ttk.Frame(self.root, padding="10")
        self.keyboard_frame.pack(fill=tk.BOTH, expand=True)

        self.update_keyboard_display()

    def update_keyboard_display(self):
        """Обновляет отображение клавиатуры"""
        for widget in self.keyboard_frame.winfo_children():
            widget.destroy()

        full_layout = self.keyboard_layout.copy()

        if self.additional_keys:
            chunk_size = 10
            additional_rows = [self.additional_keys[i:i + chunk_size]
                               for i in range(0, len(self.additional_keys), chunk_size)]

            for row in additional_rows:
                full_layout.append(row)

        for row in full_layout:
            row_frame = ttk.Frame(self.keyboard_frame)
            row_frame.pack(fill=tk.X, pady=2)

            for key in row:
                button = ttk.Button(
                    row_frame,
                    text=key,
                    width=3,
                    command=lambda k=key: self.add_character(k)
                )
                button.pack(side=tk.LEFT, padx=1)

    def add_keys_from_string(self, input_string=None):
        """Добавляет уникальные символы из строки в клавиатуру"""
        if input_string is None:
            input_string = self.add_table_expression.get().strip()

        if not input_string:
            return

        input_string = ''.join(set(input_string))

        new_chars = []
        for char in input_string:
            if char != ' ' and char not in self.additional_keys and not self.char_in_main_layout(char):
                new_chars.append(char)

        self.additional_keys.extend(new_chars)
        self.update_keyboard_display()

        if input_string == self.add_table_expression.get():
            self.add_table_expression.delete(0, tk.END)

    def add_keys_from_string_simple(self, input_string):
        """Упрощенный метод для добавления символов из строки"""

        unique_chars = []
        for char in input_string:
            if char != ' ' and char not in unique_chars:
                unique_chars.append(char)

        for char in unique_chars:
            if char not in self.additional_keys:
                self.additional_keys.append(char)

        self.update_keyboard_display()

    def char_in_main_layout(self, char):
        """Проверяет, есть ли символ в основной раскладке"""
        for row in self.keyboard_layout:
            if char in row:
                return True
        return False

    def get_bool_value(self, value: str):
        if value == 'True':
            return True

        elif value == 'False':
            return False

        else:
            return None

    def reset_keyboard(self):
        """Сбрасывает клавиатуру к исходному состоянию"""
        self.additional_keys = []
        self.update_keyboard_display()
        self.add_table_expression.delete(0, tk.END)

    def add_character(self, character):
        """Добавляет символ в поле ввода"""
        current_text = self.table_expression.get()
        cursor_position = self.table_expression.index(tk.INSERT)

        new_text = current_text[:cursor_position] + character + current_text[cursor_position:]
        self.table_expression.delete(0, tk.END)
        self.table_expression.insert(0, new_text)

        self.table_expression.icursor(cursor_position + 1)

    def backspace(self):
        """Удаляет символ перед курсором"""
        current_text = self.table_expression.get()
        cursor_position = self.table_expression.index(tk.INSERT)

        if cursor_position > 0:
            new_text = current_text[:cursor_position - 1] + current_text[cursor_position:]
            self.table_expression.delete(0, tk.END)
            self.table_expression.insert(0, new_text)

            self.table_expression.icursor(cursor_position - 1)

    def clear_table_expression(self):
        """Очищает поле ввода"""
        self.table_expression.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualKeyboard(root)

    root.mainloop()