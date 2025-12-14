import math


class Shape:
    def __init__(self):
        pass

    def get_area(self):
        raise NotImplementedError

    def get_perimeter(self):
        raise NotImplemented

    def get_diameter(self):
        raise NotImplemented

    @property
    def area(self) -> float:
        return self.get_area()

    @property
    def perimeter(self) -> float:
        return self.get_perimeter()

    @property
    def diameter(self) -> float:
        return self.get_diameter()

    def __str__(self):
        return 'Базовый шаблон фигуры'


class Circle(Shape):
    def __init__(self, radius: float):
        super().__init__()

        self.radius = radius

    def get_area(self) -> float:
        return math.pi * (self.radius ** 2)

    def get_perimeter(self) -> float:
        return 2 * math.pi * self.radius

    def get_diameter(self) -> float:
        return self.radius * 2

    def __str__(self):
        return f'Круг с радиусом {self.radius}'


class Triangle(Shape):
    def __init__(self, a: float, b: float, c: float):
        super().__init__()

        self.a = a
        self.b = b
        self.c = c

    def get_area(self) -> float:
        half_per = self.get_perimeter() / 2

        return math.sqrt(half_per * (half_per - self.a) * (half_per - self.b) * (half_per - self.c))

    def get_perimeter(self) -> float:
        return sum([self.a, self.b, self.c])

    def get_diameter(self) -> float:
        return max([self.a, self.b, self.c])

    def __str__(self):
        return f'Треугольник со сторонами: {str([self.a, self.b, self.c])}'


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        super().__init__()

        self.width = width
        self.height = height

    def get_area(self):
        return self.width * self.height

    def get_perimeter(self):
        return (self.width + self.height) * 2

    def get_diameter(self):
        return math.sqrt((self.height ** 2) + (self.width ** 2))

    def __str__(self):
        return f'Прямоугольник с шириной {self.width} и с высотой {self.height}'


class Square(Rectangle):
    def __init__(self, width: float, height: float):
        super().__init__(width=width, height=height)

    def __str__(self):
        return f'Квадрат с шириной {self.width} и высотой {self.height}'


if __name__ == '__main__':
    square = Square(width=200, height=100)

    print(square.area)