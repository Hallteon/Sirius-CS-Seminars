import tkinter as tk
import networkx as nx

from tkinter import ttk, messagebox
from typing import List, Dict, Tuple

from auto_solver import find_isomorphisms_networkx


class GraphIsomorphismApp:
    """Главное окно приложения для поиска изоморфизмов графов"""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Поиск изоморфизмов графов")
        self.root.geometry("800x600")

        self.matrix_entries: List[List[tk.Entry]] = []
        self.graph_nodes: List[str] = []
        self.graph_edges: List[Tuple[str, str]] = []
        self.graph_nx = nx.Graph()
        self.current_isomorphism: Dict[str, str] = {}

        self.setup_ui()

    def setup_ui(self) -> None:
        """Создает и размещает все элементы интерфейса"""

        matrix_frame = ttk.LabelFrame(self.root, text="Матрица смежности", padding=10)
        matrix_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(matrix_frame, text="Размер матрицы (n x n):").grid(row=0, column=0, padx=5)
        self.matrix_size = tk.StringVar(value="5")
        size_entry = ttk.Entry(matrix_frame, textvariable=self.matrix_size, width=10)
        size_entry.grid(row=0, column=1, padx=5)

        ttk.Button(matrix_frame, text="Создать матрицу",
                   command=self.create_matrix_table).grid(row=0, column=2, padx=5)

        self.matrix_container = ttk.Frame(self.root)
        self.matrix_container.pack(fill="both", expand=True, padx=10, pady=5)

        graph_frame = ttk.LabelFrame(self.root, text="Граф", padding=10)
        graph_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(graph_frame, text="Вершина:").grid(row=0, column=0, padx=5)
        self.node_entry = ttk.Entry(graph_frame, width=10)
        self.node_entry.grid(row=0, column=1, padx=5)
        ttk.Button(graph_frame, text="Добавить вершину",
                   command=self.add_node).grid(row=0, column=2, padx=5)

        # Добавление рёбер
        ttk.Label(graph_frame, text="Ребро от:").grid(row=1, column=0, padx=5)
        self.edge_from = ttk.Combobox(graph_frame, width=8, state="readonly")
        self.edge_from.grid(row=1, column=1, padx=5)

        ttk.Label(graph_frame, text="до:").grid(row=1, column=2, padx=5)
        self.edge_to = ttk.Combobox(graph_frame, width=8, state="readonly")
        self.edge_to.grid(row=1, column=3, padx=5)

        ttk.Button(graph_frame, text="Добавить ребро",
                   command=self.add_edge).grid(row=1, column=4, padx=5)

        self.graph_text = tk.Text(graph_frame, height=4, width=50)
        self.graph_text.grid(row=2, column=0, columnspan=5, pady=5, sticky="we")

        calc_frame = ttk.LabelFrame(self.root, text="Вычисления", padding=10)
        calc_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(calc_frame, text="Найти изоморфизм",
                   command=self.find_isomorphism).pack(side="left", padx=5)
        ttk.Button(calc_frame, text="Очистить всё",
                   command=self.clear_all).pack(side="left", padx=5)

        self.result_text = tk.Text(calc_frame, height=6, width=50)
        self.result_text.pack(fill="both", expand=True, pady=5)

        path_frame = ttk.Frame(calc_frame)
        path_frame.pack(fill="x", pady=5)

        ttk.Label(path_frame, text="Путь от:").pack(side="left", padx=5)
        self.path_from = ttk.Combobox(path_frame, width=8, state="readonly")
        self.path_from.pack(side="left", padx=5)

        ttk.Label(path_frame, text="до:").pack(side="left", padx=5)
        self.path_to = ttk.Combobox(path_frame, width=8, state="readonly")
        self.path_to.pack(side="left", padx=5)

        ttk.Button(path_frame, text="Найти сумму весов",
                   command=self.find_weight_sum).pack(side="left", padx=5)

    def create_matrix_table(self) -> None:
        """Создает таблицу для ввода матрицы смежности заданного размера"""
        try:
            n = int(self.matrix_size.get())
            if n < 2 or n > 10:
                messagebox.showerror("Ошибка", "Размер матрицы должен быть от 2 до 10")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Введите целое число")
            return

        for widget in self.matrix_container.winfo_children():
            widget.destroy()

        self.matrix_entries = []
        for i in range(n):
            row_entries = []
            for j in range(n):
                entry = tk.Entry(self.matrix_container, width=5, justify='center')
                entry.grid(row=i, column=j, padx=1, pady=1)

                if i == j:
                    entry.insert(0, "0")
                    entry.config(state='disabled')
                else:
                    entry.insert(0, "0")
                    if i < j:
                        entry.bind('<KeyRelease>', lambda e, row=i, col=j: self.on_upper_triangle_change(row, col))

                row_entries.append(entry)
            self.matrix_entries.append(row_entries)

    def on_upper_triangle_change(self, row: int, col: int) -> None:
        """Обрабатывает изменение значения в верхнем треугольнике матрицы"""
        try:
            value = self.matrix_entries[row][col].get()

            if row != col:  # Не главная диагональ
                self.matrix_entries[col][row].delete(0, tk.END)
                self.matrix_entries[col][row].insert(0, value)
        except (ValueError, IndexError):
            pass

    def add_node(self) -> None:
        """Добавляет вершину в граф"""
        node = self.node_entry.get().strip().upper()
        if not node:
            messagebox.showerror("Ошибка", "Введите название вершины")
            return

        if node in self.graph_nodes:
            messagebox.showerror("Ошибка", "Вершина уже существует")
            return

        self.graph_nodes.append(node)
        self.graph_nx.add_node(node)
        self.update_graph_display()
        self.update_comboboxes()
        self.node_entry.delete(0, tk.END)

    def add_edge(self) -> None:
        """Добавляет ребро между двумя вершинами"""
        from_node = self.edge_from.get()
        to_node = self.edge_to.get()

        if not from_node or not to_node:
            messagebox.showerror("Ошибка", "Выберите обе вершины")
            return

        if from_node == to_node:
            messagebox.showerror("Ошибка", "Нельзя добавить петлю")
            return

        edge = (from_node, to_node)

        if (from_node, to_node) in self.graph_edges or (to_node, from_node) in self.graph_edges:
            messagebox.showerror("Ошибка", "Ребро уже существует")
            return

        self.graph_edges.append(edge)
        self.graph_nx.add_edge(from_node, to_node)
        self.update_graph_display()

    def update_graph_display(self) -> None:
        """Обновляет текстовое представление графа"""
        self.graph_text.delete(1.0, tk.END)
        self.graph_text.insert(1.0, f"Вершины: {', '.join(sorted(self.graph_nodes))}\n")
        edges_str = ', '.join([f'{a}-{b}' for a, b in self.graph_edges])
        self.graph_text.insert(tk.END, f"Рёбра: {edges_str}")

    def update_comboboxes(self) -> None:
        """Обновляет выпадающие списки вершин"""
        nodes = sorted(self.graph_nodes)
        self.edge_from['values'] = nodes
        self.edge_to['values'] = nodes
        self.path_from['values'] = nodes
        self.path_to['values'] = nodes

    def find_isomorphism(self) -> None:
        """Находит изоморфизм между матрицей и графом с использованием импортированного солвера"""
        if not self.matrix_entries:
            messagebox.showerror("Ошибка", "Сначала создайте матрицу")
            return

        if len(self.graph_nodes) < 2:
            messagebox.showerror("Ошибка", "Добавьте хотя бы 2 вершины в граф")
            return

        n = len(self.matrix_entries)
        matrix = []
        node_names = [f"П{i + 1}" for i in range(n)]

        for i in range(n):
            row = []
            for j in range(n):
                try:
                    value = int(self.matrix_entries[i][j].get())
                    row.append(value)
                except ValueError:
                    row.append(0)
            matrix.append(row)

        letter_adj_dict = self.create_letter_adj_dict()

        try:
            isomorphisms_generator = find_isomorphisms_networkx(matrix, node_names, letter_adj_dict)
            isomorphism = isomorphisms_generator

            if isomorphism:
                self.current_isomorphism = isomorphism
                self.display_result(isomorphism)
            else:
                self.current_isomorphism = {}
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(1.0, "Изоморфизм не найден")
        except Exception as e:
            self.current_isomorphism = {}
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, f"Ошибка при поиске изоморфизма: {str(e)}")

    def create_letter_adj_dict(self) -> Dict[str, set]:
        """Создает словарь смежности для графа из интерфейса"""
        adj_dict = {}
        for node in self.graph_nodes:
            adj_dict[node] = set()

        for edge in self.graph_edges:
            from_node, to_node = edge
            adj_dict[from_node].add(to_node)
            adj_dict[to_node].add(from_node)

        return adj_dict

    def find_weight_sum(self) -> None:
        """Находит сумму весов ребер между двумя вершинами (кратчайшего пути если не смежные)"""
        if not self.current_isomorphism:
            messagebox.showerror("Ошибка", "Сначала найдите изоморфизм")
            return

        from_node = self.path_from.get()
        to_node = self.path_to.get()

        if not from_node or not to_node:
            messagebox.showerror("Ошибка", "Выберите обе вершины")
            return

        if from_node == to_node:
            messagebox.showerror("Ошибка", "Выберите разные вершины")
            return

        if from_node not in self.graph_nx or to_node not in self.graph_nx:
            messagebox.showerror("Ошибка", "Обе вершины должны быть в графе")
            return

        try:
            weighted_graph = self.create_weighted_graph_from_matrix()

            path = nx.shortest_path(weighted_graph, from_node, to_node, weight='weight')
            path_length = nx.shortest_path_length(weighted_graph, from_node, to_node, weight='weight')

            path_str = " → ".join(path)

            current_text = self.result_text.get(1.0, tk.END).strip()
            if current_text:
                new_text = f"{current_text}\n\nПуть от {from_node} до {to_node}: {path_str}\nСумма весов: {path_length}"
            else:
                new_text = f"Путь от {from_node} до {to_node}: {path_str}\nСумма весов: {path_length}"

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, new_text)

        except nx.NetworkXNoPath:
            current_text = self.result_text.get(1.0, tk.END).strip()
            if current_text:
                new_text = f"{current_text}\n\nПути от {from_node} до {to_node} не существует"
            else:
                new_text = f"Пути от {from_node} до {to_node} не существует"

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, new_text)

    def create_weighted_graph_from_matrix(self) -> nx.Graph:
        """Создает взвешенный граф на основе матрицы смежности после изоморфизма"""
        weighted_graph = nx.Graph()

        for node in self.graph_nodes:
            weighted_graph.add_node(node)

        reverse_isomorphism = {v: k for k, v in self.current_isomorphism.items()}

        n = len(self.matrix_entries)
        matrix = []
        for i in range(n):
            row = []
            for j in range(n):
                try:
                    value = int(self.matrix_entries[i][j].get())
                    row.append(value)
                except ValueError:
                    row.append(0)
            matrix.append(row)

        for i, graph_node_i in enumerate(self.graph_nodes):
            matrix_node_i = reverse_isomorphism[graph_node_i]
            matrix_index_i = int(matrix_node_i[1:]) - 1

            for j, graph_node_j in enumerate(self.graph_nodes):
                if i >= j:
                    continue

                matrix_node_j = reverse_isomorphism[graph_node_j]
                matrix_index_j = int(matrix_node_j[1:]) - 1

                weight = matrix[matrix_index_i][matrix_index_j]

                if weight > 0:
                    weighted_graph.add_edge(graph_node_i, graph_node_j, weight=weight)

        return weighted_graph

    def display_result(self, isomorphism: Dict[str, str]) -> None:
        """Отображает результат поиска изоморфизма"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, "Найден изоморфизм:\n")
        for matrix_node, graph_node in sorted(isomorphism.items()):
            self.result_text.insert(tk.END, f"{matrix_node} → {graph_node}\n")

    def clear_all(self) -> None:
        """Очищает все поля и данные"""
        for widget in self.matrix_container.winfo_children():
            widget.destroy()
        self.matrix_entries = []

        self.graph_nodes = []
        self.graph_edges = []
        self.graph_nx = nx.Graph()
        self.current_isomorphism = {}
        self.graph_text.delete(1.0, tk.END)

        self.edge_from.set('')
        self.edge_to.set('')
        self.path_from.set('')
        self.path_to.set('')
        self.update_comboboxes()

        self.result_text.delete(1.0, tk.END)


def main() -> None:
    """Запускает главное окно приложения"""
    root = tk.Tk()
    app = GraphIsomorphismApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()