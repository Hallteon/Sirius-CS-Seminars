import tkinter as tk
from tkinter import messagebox


class Shape:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, canvas):
        raise NotImplementedError("Метод draw должен быть переопределен в подклассе")


class Circle(Shape):
    def __init__(self, x, y, radius=30):
        super().__init__(x, y)
        self.radius = radius

    def draw(self, canvas):
        return canvas.create_oval(
            self.x - self.radius,
            self.y - self.radius,
            self.x + self.radius,
            self.y + self.radius,
            fill="lightblue",
            outline="black"
        )


class Square(Shape):
    def __init__(self, x, y, side=60):
        super().__init__(x, y)
        self.side = side

    def draw(self, canvas):
        return canvas.create_rectangle(
            self.x - self.side // 2,
            self.y - self.side // 2,
            self.x + self.side // 2,
            self.y + self.side // 2,
            fill="lightgreen",
            outline="black"
        )


class Line(Shape):
    def __init__(self, x, y, length=80):
        super().__init__(x, y)
        self.length = length

    def draw(self, canvas):
        return canvas.create_line(
            self.x - self.length // 2,
            self.y,
            self.x + self.length // 2,
            self.y,
            fill="red",
            width=3
        )


class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Рисовалка фигур")
        self.current_shape_class = None
        self.shapes = []

        self.canvas = tk.Canvas(root, width=600, height=400, bg='white')
        self.canvas.pack(pady=10)

        self.canvas.bind("<Button-1>", self.canvas_click)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)

        shapes = [
            ("Круг", Circle),
            ("Квадрат", Square),
            ("Линия", Line)
        ]

        for text, shape_class in shapes:
            btn = tk.Button(
                button_frame,
                text=text,
                command=lambda sc=shape_class: self.set_shape(sc)
            )
            btn.pack(side=tk.LEFT, padx=5)

        clear_btn = tk.Button(
            button_frame,
            text="Очистить",
            command=self.clear_canvas
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        self.info_label = tk.Label(root, text="Выберите фигуру и кликните на холст", fg="blue")
        self.info_label.pack(pady=5)

    def set_shape(self, shape_class):
        self.current_shape_class = shape_class
        shape_name = ""
        if shape_class == Circle:
            shape_name = "Круг"
        elif shape_class == Square:
            shape_name = "Квадрат"
        elif shape_class == Line:
            shape_name = "Линия"

        self.info_label.config(text=f"Выбрано: {shape_name}. Кликните на холст")

    def canvas_click(self, event):
        if self.current_shape_class:
            shape = self.current_shape_class(event.x, event.y)
            shape.draw(self.canvas)
            self.shapes.append(shape)

        else:
            messagebox.showwarning("Предупреждение", "Сначала выберите фигуру!")

    def clear_canvas(self):
        self.canvas.delete("all")
        self.shapes = []


if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()