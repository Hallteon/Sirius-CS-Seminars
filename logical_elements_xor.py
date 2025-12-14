from typing import Optional


class LogicalElement:
    """Базовый класс для логических элементов"""

    def __init__(self):
        self._inputs = [False, False]
        self._result = False
        self._next_element: Optional['LogicalElement'] = None
        self._next_input_index: int = 0

    def connect(self, next_element: 'LogicalElement', input_index: int) -> None:
        """Подключает следующий элемент к указанному входу"""
        if input_index not in (1, 2):
            raise ValueError("Input index must be 1 or 2")
        self._next_element = next_element
        self._next_input_index = input_index

    @property
    def result(self) -> bool:
        """Возвращает текущий результат вычисления"""
        return self._result

    def _propagate_result(self) -> None:
        """Передает результат следующему элементу в цепи"""
        if self._next_element is not None:
            if self._next_input_index == 1:
                self._next_element.input1 = self.result
            else:
                self._next_element.input2 = self.result

    def _update_and_propagate(self) -> None:
        """Обновляет результат и передает его дальше по цепи"""
        self.calculate()
        self._propagate_result()

    @property
    def input1(self) -> bool:
        return self._inputs[0]

    @input1.setter
    def input1(self, value: bool) -> None:
        self._inputs[0] = value
        self._update_and_propagate()

    @property
    def input2(self) -> bool:
        return self._inputs[1]

    @input2.setter
    def input2(self, value: bool) -> None:
        self._inputs[1] = value
        self._update_and_propagate()

    def calculate(self) -> None:
        """Вычисляет логическую операцию - должен быть переопределен в потомках"""
        raise NotImplementedError("Use child classes for logical elements")


class NotGate(LogicalElement):
    """Логический элемент НЕ"""

    def calculate(self) -> None:
        self._result = not self.input1


class AndGate(LogicalElement):
    """Логический элемент И"""

    def calculate(self) -> None:
        self._result = self.input1 and self.input2


class OrGate(LogicalElement):
    """Логический элемент ИЛИ"""

    def calculate(self) -> None:
        self._result = self.input1 or self.input2


def demonstrate_nand_gate():
    print('NAND вентль:')
    not_gate = NotGate()
    and_gate = AndGate()

    print('A | B | not (A and B)')
    print('--+---+--------------')

    for a in (False, True):
        for b in (False, True):
            and_gate.input1 = a
            and_gate.input2 = b
            not_gate.input1 = and_gate.result
            print(f'{int(a)} | {int(b)} | {int(not_gate.result)}')
    print()


def demonstrate_xor_gate():
    print('XOR вентиль:')

    and_gate1 = AndGate()
    and_gate2 = AndGate()
    or_gate = OrGate()
    not_gate1 = NotGate()
    not_gate2 = NotGate()

    not_gate1.connect(and_gate2, 1)
    not_gate2.connect(and_gate1, 2)

    and_gate1.connect(or_gate, 1)
    and_gate2.connect(or_gate, 2)

    print('A | B | A XOR B')
    print('--+---+---------')

    for a in (False, True):
        for b in (False, True):
            and_gate1.input1 = a
            and_gate2.input2 = b
            not_gate1.input1 = a
            not_gate2.input1 = b

            print(f'{int(a)} | {int(b)} | {int(or_gate.result)}')
    print()


if __name__ == "__main__":
    demonstrate_nand_gate()
    demonstrate_xor_gate()