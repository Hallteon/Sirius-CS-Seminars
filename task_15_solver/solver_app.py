import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QTextEdit, QSpinBox, QComboBox, QTableWidget,
                               QTableWidgetItem, QDoubleSpinBox, QMessageBox)


class SegmentSolver(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Задача 15 ЕГЭ - Отрезки")
        self.resize(700, 600)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        layout.addWidget(QLabel("Отрезки (имя, начало, конец):"))
        self.table = QTableWidget(5, 3)
        self.table.setHorizontalHeaderLabels(["Имя", "Начало", "Конец"])
        self.table.setMaximumHeight(150)
        self.table.setItem(0, 0, QTableWidgetItem("B"))
        self.table.setItem(0, 1, QTableWidgetItem("10"))
        self.table.setItem(0, 2, QTableWidgetItem("15"))
        self.table.setItem(1, 0, QTableWidgetItem("C"))
        self.table.setItem(1, 1, QTableWidgetItem("20"))
        self.table.setItem(1, 2, QTableWidgetItem("27"))
        layout.addWidget(self.table)

        layout.addWidget(QLabel("Выражение (B(x), C(x), A(x), impl(A,B), and, or, not):"))
        self.expr = QLineEdit("not(impl(B(x) or C(x), A(x)))")
        layout.addWidget(self.expr)

        params = QHBoxLayout()

        params.addWidget(QLabel("A от:"))
        self.a_min = QSpinBox()
        self.a_min.setRange(-1000, 1000)
        self.a_min.setValue(0)
        params.addWidget(self.a_min)

        params.addWidget(QLabel("до:"))
        self.a_max = QSpinBox()
        self.a_max.setRange(-1000, 1000)
        self.a_max.setValue(100)
        params.addWidget(self.a_max)

        params.addWidget(QLabel("x от:"))
        self.x_min = QSpinBox()
        self.x_min.setRange(-1000, 1000)
        self.x_min.setValue(0)
        params.addWidget(self.x_min)

        params.addWidget(QLabel("до:"))
        self.x_max = QSpinBox()
        self.x_max.setRange(-1000, 1000)
        self.x_max.setValue(100)
        params.addWidget(self.x_max)

        params.addWidget(QLabel("шаг:"))
        self.step = QDoubleSpinBox()
        self.step.setRange(0.1, 10)
        self.step.setValue(0.5)
        params.addWidget(self.step)

        layout.addLayout(params)

        params2 = QHBoxLayout()

        params2.addWidget(QLabel("Искать:"))
        self.search_type = QComboBox()
        self.search_type.addItems(["мин. длину", "макс. длину", "все"])
        params2.addWidget(self.search_type)

        params2.addWidget(QLabel("Выражение:"))
        self.condition = QComboBox()
        self.condition.addItems(["истинно при всех x", "ложно при всех x"])
        params2.addWidget(self.condition)

        params2.addStretch()
        layout.addLayout(params2)

        self.btn = QPushButton("РЕШИТЬ")
        self.btn.clicked.connect(self.solve)
        layout.addWidget(self.btn)

        self.result = QTextEdit()
        self.result.setReadOnly(True)
        layout.addWidget(self.result)

    def solve(self):
        try:
            segments = {}
            for row in range(self.table.rowCount()):
                name = self.table.item(row, 0)
                start = self.table.item(row, 1)
                end = self.table.item(row, 2)
                if name and start and end:
                    n, s, e = name.text().strip(), start.text().strip(), end.text().strip()
                    if n and s and e:
                        segments[n] = (float(s), float(e))

            if not segments:
                QMessageBox.warning(self, "Ошибка", "Добавьте отрезки")
                return

            expression = self.expr.text().strip()
            if not expression:
                QMessageBox.warning(self, "Ошибка", "Введите выражение")
                return

            a_min, a_max = self.a_min.value(), self.a_max.value()
            x_min, x_max = self.x_min.value(), self.x_max.value()
            step = self.step.value()
            search_type = self.search_type.currentIndex()
            must_be_true = self.condition.currentIndex() == 0

            def in_seg(a, b, x):
                return a <= x <= b

            def impl(a, b):
                return (not a) or b

            seg_funcs = {}
            for name, (s, e) in segments.items():
                seg_funcs[name] = lambda x, s=s, e=e: in_seg(s, e, x)
                seg_funcs[f"in{name}"] = seg_funcs[name]

            x_vals = []
            x = x_min
            while x <= x_max:
                x_vals.append(x)
                x += step
            total = len(x_vals)

            valid = []
            best_len = float('inf') if search_type == 0 else float('-inf')
            best = None

            ctx = {'impl': impl, '__builtins__': {}}
            ctx.update(seg_funcs)

            for a in range(a_min, a_max + 1):
                for b in range(a, a_max + 1):
                    ctx['A'] = lambda x, a=a, b=b: in_seg(a, b, x)
                    ctx['inA'] = ctx['A']

                    ok = 0
                    for xv in x_vals:
                        ctx['x'] = xv
                        try:
                            r = eval(expression, ctx)
                            if (must_be_true and r) or (not must_be_true and not r):
                                ok += 1
                        except:
                            pass

                    if ok == total:
                        length = b - a
                        valid.append((a, b, length))
                        if search_type == 0 and length < best_len:
                            best_len, best = length, (a, b)
                        elif search_type == 1 and length > best_len:
                            best_len, best = length, (a, b)

            out = []
            out.append(f"Отрезки: {segments}")
            out.append(f"Выражение: {expression}")
            out.append(f"Проверено {total} значений x\n")

            if valid:
                if search_type == 2:
                    out.append(f"Найдено {len(valid)} отрезков:")
                    for a, b, l in sorted(valid)[:15]:
                        out.append(f"  [{a}; {b}], длина {l}")
                else:
                    out.append(f"A = [{best[0]}; {best[1]}]")
                    out.append(f"ОТВЕТ: {best_len}")
            else:
                out.append("Отрезков не найдено")

            self.result.setText("\n".join(out))

        except Exception as e:
            self.result.setText(f"Ошибка: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = SegmentSolver()
    w.show()
    sys.exit(app.exec())