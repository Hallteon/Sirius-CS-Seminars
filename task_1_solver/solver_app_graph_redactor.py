import sys
import json
import networkx as nx

from typing import Optional, List, Dict
from PySide6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene,
                               QGraphicsItem, QGraphicsEllipseItem,
                               QGraphicsLineItem, QGraphicsTextItem,
                               QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QPushButton, QFileDialog, QMessageBox, QLabel,
                               QTextEdit, QComboBox, QGroupBox, QSplitter)
from PySide6.QtCore import Qt, QRectF, QLineF, QPointF, Signal, QObject
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QPainterPathStroker, QAction


class GraphConfig:
    NODE_DIAMETER = 20
    NODE_RADIUS = NODE_DIAMETER / 2
    EDGE_WIDTH = 2
    MIN_DISTANCE = 40

    COLOR_BG = QColor(40, 40, 40)
    COLOR_NODE = QColor(0, 255, 255)
    COLOR_NODE_ACTIVE = QColor(255, 0, 255)
    COLOR_EDGE = QColor(255, 255, 255)
    COLOR_TEXT = QColor(255, 255, 255)
    COLOR_NODE_ISOMORPH = QColor(255, 200, 0)

    TABLE_BG = QColor(50, 50, 50)
    TABLE_TEXT = QColor(255, 255, 255)
    TABLE_DIAGONAL = QColor(80, 80, 80)


class EdgeItem(QGraphicsLineItem):
    def __init__(self, source_item, dest_item):
        super().__init__()
        self.source = source_item
        self.dest = dest_item
        self.setPen(QPen(GraphConfig.COLOR_EDGE, GraphConfig.EDGE_WIDTH))
        self.setZValue(0)
        self.update_geometry()

    def update_geometry(self):
        line = QLineF(self.source.scenePos(), self.dest.scenePos())
        self.setLine(line)

    def shape(self):
        path = super().shape()
        stroker = QPainterPathStroker()
        stroker.setWidth(10)
        return stroker.createStroke(path)


class NodeItem(QGraphicsEllipseItem):
    def __init__(self, name: str, x: float, y: float):
        rect = QRectF(-GraphConfig.NODE_RADIUS, -GraphConfig.NODE_RADIUS,
                      GraphConfig.NODE_DIAMETER, GraphConfig.NODE_DIAMETER)
        super().__init__(rect)
        self.name = name
        self.edges: List[EdgeItem] = []
        self.setBrush(QBrush(GraphConfig.COLOR_NODE))
        self.setPen(QPen(Qt.NoPen))
        self.setPos(x, y)
        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self._create_label(name)

    def _create_label(self, text: str):
        self.label = QGraphicsTextItem(text, self)
        self.label.setDefaultTextColor(GraphConfig.COLOR_TEXT)
        dx = -10 if len(text) == 1 else -15
        self.label.setPos(dx, -30)
        self.label.setFlag(QGraphicsItem.ItemIsMovable)
        self.label.setFlag(QGraphicsItem.ItemIgnoresTransformations)

    def set_highlighted(self, is_active: bool):
        color = GraphConfig.COLOR_NODE_ACTIVE if is_active else GraphConfig.COLOR_NODE
        self.setBrush(QBrush(color))

    def set_isomorphism_color(self, is_isomorphic: bool):
        if is_isomorphic:
            self.setBrush(QBrush(GraphConfig.COLOR_NODE_ISOMORPH))
        else:
            self.setBrush(QBrush(GraphConfig.COLOR_NODE))

    def add_connection(self, edge: EdgeItem):
        self.edges.append(edge)

    def remove_connection(self, edge: EdgeItem):
        if edge in self.edges:
            self.edges.remove(edge)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged and self.scene():
            for edge in self.edges:
                edge.update_geometry()
        return super().itemChange(change, value)


class GraphManager(QObject):
    node_count_changed = Signal(int)
    graph_changed = Signal()

    def __init__(self, scene: QGraphicsScene):
        super().__init__()
        self.scene = scene
        self.node_counter = 0

    def reset(self):
        self.node_counter = 0
        self.scene.clear()
        self.node_count_changed.emit(0)
        self.graph_changed.emit()

    def generate_name(self) -> str:
        n = self.node_counter
        name = ""
        while n >= 0:
            name = chr(ord('A') + (n % 26)) + name
            n = n // 26 - 1
        self.node_counter += 1
        return name

    def create_node(self, pos: QPointF, name: str = None) -> NodeItem:
        if name is None:
            name = self.generate_name()
        else:
            self.node_counter += 1

        node = NodeItem(name, pos.x(), pos.y())
        self.scene.addItem(node)
        self.node_count_changed.emit(self.get_node_count())
        self.graph_changed.emit()
        return node

    def create_edge(self, u: NodeItem, v: NodeItem):
        if u == v:
            return
        for edge in u.edges:
            if (edge.source == u and edge.dest == v) or (edge.source == v and edge.dest == u):
                return
        edge = EdgeItem(u, v)
        self.scene.addItem(edge)
        u.add_connection(edge)
        v.add_connection(edge)
        self.graph_changed.emit()

    def delete_item(self, item: QGraphicsItem):
        if isinstance(item, NodeItem):
            for edge in list(item.edges):
                self.delete_item(edge)
            self.scene.removeItem(item)
            self.node_count_changed.emit(self.get_node_count())
            self.graph_changed.emit()
        elif isinstance(item, EdgeItem):
            item.source.remove_connection(item)
            item.dest.remove_connection(item)
            self.scene.removeItem(item)
            self.graph_changed.emit()
        elif isinstance(item, QGraphicsTextItem):
            parent = item.parentItem()
            if isinstance(parent, NodeItem):
                self.delete_item(parent)

    def get_node_count(self) -> int:
        return sum(1 for item in self.scene.items() if isinstance(item, NodeItem))

    def is_position_valid(self, pos: QPointF) -> bool:
        for item in self.scene.items():
            if isinstance(item, NodeItem):
                distance = QLineF(pos, item.scenePos()).length()
                if distance < GraphConfig.MIN_DISTANCE:
                    return False
        return True

    def get_nodes(self) -> List[NodeItem]:
        return [item for item in self.scene.items() if isinstance(item, NodeItem)]

    def get_edges(self) -> List[EdgeItem]:
        edges = []
        for node in self.get_nodes():
            for edge in node.edges:
                if edge not in edges:
                    edges.append(edge)
        return edges

    def get_adjacency_dict(self) -> Dict[str, set]:
        adj_dict = {}
        nodes = self.get_nodes()

        for node in nodes:
            adj_dict[node.name] = set()

        for edge in self.get_edges():
            source_name = edge.source.name
            dest_name = edge.dest.name
            adj_dict[source_name].add(dest_name)
            adj_dict[dest_name].add(source_name)

        return adj_dict

    def get_node_names(self) -> List[str]:
        return [node.name for node in self.get_nodes()]

    def highlight_isomorphism(self, mapping):
        nodes = self.get_nodes()

        for node in nodes:
            node.set_isomorphism_color(False)

        if mapping and isinstance(mapping, dict):
            for matrix_node, graph_node in mapping.items():
                for node in nodes:
                    if node.name == graph_node:
                        node.set_isomorphism_color(True)
                        break


class AdjacencyMatrixWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(0)
        self.setRowCount(0)

        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {GraphConfig.TABLE_BG.name()};
                color: {GraphConfig.TABLE_TEXT.name()};
                gridline-color: #666;
            }}
            QHeaderView::section {{
                background-color: #333;
                color: white;
                padding: 4px;
                border: 1px solid #666;
            }}
        """)

        self.itemChanged.connect(self.on_item_changed)
        self.horizontalHeader().setDefaultSectionSize(50)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

    def update_size(self, node_count: int):
        self.setRowCount(node_count)
        self.setColumnCount(node_count)

        headers = [str(i + 1) for i in range(node_count)]
        self.setHorizontalHeaderLabels(headers)
        self.setVerticalHeaderLabels(headers)

        self.blockSignals(True)
        for r in range(node_count):
            for c in range(node_count):
                item = self.item(r, c)
                if not item:
                    item = QTableWidgetItem("")
                    item.setTextAlignment(Qt.AlignCenter)
                    self.setItem(r, c, item)

                if r == c:
                    item.setFlags(Qt.ItemIsEnabled)
                    item.setBackground(QBrush(GraphConfig.TABLE_DIAGONAL))
                    item.setText("0")
                else:
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable)
                    item.setBackground(QBrush(GraphConfig.TABLE_BG))
                    if item.text() == "":
                        item.setText("0")

        self.blockSignals(False)

    def on_item_changed(self, item):
        row = item.row()
        col = item.column()
        if row == col:
            return

        text = item.text()
        self.blockSignals(True)
        symmetric_item = self.item(col, row)
        if symmetric_item:
            symmetric_item.setText(text)
        self.blockSignals(False)

    def get_data(self) -> List[List[str]]:
        rows = self.rowCount()
        data = []
        for r in range(rows):
            row_data = []
            for c in range(rows):
                item = self.item(r, c)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data

    def set_data(self, data: List[List[str]]):
        size = len(data)
        self.update_size(size)
        self.blockSignals(True)
        for r in range(size):
            for c in range(size):
                if r < len(data) and c < len(data[r]):
                    val = data[r][c]
                    item = self.item(r, c)
                    if item:
                        item.setText(val)
        self.blockSignals(False)

    def get_adjacency_matrix(self) -> List[List[int]]:
        data = self.get_data()
        n = len(data)
        matrix = []
        for i in range(n):
            row = []
            for j in range(n):
                if i == j:
                    row.append(0)
                else:
                    val_str = data[i][j].strip()
                    if val_str == "*":
                        row.append(1)
                    elif val_str == "":
                        row.append(0)
                    else:
                        try:
                            val = int(val_str)
                            row.append(1 if val != 0 else 0)
                        except ValueError:
                            row.append(0)
            matrix.append(row)
        return matrix


class GraphScene(QGraphicsScene):
    def __init__(self, manager: GraphManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.active_node: Optional[NodeItem] = None
        self.setBackgroundBrush(QBrush(GraphConfig.COLOR_BG))
        self.setSceneRect(0, 0, 800, 600)

    def mousePressEvent(self, event):
        pos = event.scenePos()
        view = self.views()[0] if self.views() else None
        if not view:
            super().mousePressEvent(event)
            return

        item = self.itemAt(pos, view.transform())

        if event.button() == Qt.LeftButton:
            if event.modifiers() & Qt.ShiftModifier:
                if isinstance(item, NodeItem):
                    if self.active_node:
                        self.active_node.set_highlighted(False)
                        if self.active_node != item:
                            self.manager.create_edge(self.active_node, item)
                    self.active_node = item
                    self.active_node.set_highlighted(True)
                    event.accept()
                    return
                else:
                    if self.active_node:
                        self.active_node.set_highlighted(False)
                        self.active_node = None
            else:
                if self.active_node:
                    self.active_node.set_highlighted(False)
                    self.active_node = None

            if item is None:
                if self.manager.is_position_valid(pos):
                    self.manager.create_node(pos)
                event.accept()
                return

            super().mousePressEvent(event)

        elif event.button() == Qt.RightButton:
            if self.active_node:
                self.active_node.set_highlighted(False)
                self.active_node = None
            if item:
                self.manager.delete_item(item)
                event.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Поиск изоморфизмов графов")
        self.resize(1200, 700)

        self.current_isomorphism: Dict[str, str] = {}

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        matrix_buttons_layout = QHBoxLayout()

        self.insert_star_btn = QPushButton("Вставить *")
        self.insert_star_btn.clicked.connect(self.insert_star_to_selected)
        matrix_buttons_layout.addWidget(self.insert_star_btn)

        self.insert_zero_btn = QPushButton("Вставить 0")
        self.insert_zero_btn.clicked.connect(self.insert_zero_to_selected)
        matrix_buttons_layout.addWidget(self.insert_zero_btn)

        matrix_buttons_layout.addStretch()
        left_layout.addLayout(matrix_buttons_layout)

        self.matrix_widget = AdjacencyMatrixWidget()
        left_layout.addWidget(QLabel("Матрица смежности (* - ребро, число - вес):"))
        left_layout.addWidget(self.matrix_widget)

        isomorphism_panel = QGroupBox("Поиск изоморфизма")
        isomorphism_layout = QVBoxLayout()

        self.find_isomorphism_btn = QPushButton("Найти изоморфизм")
        self.find_isomorphism_btn.clicked.connect(self.find_isomorphism)
        isomorphism_layout.addWidget(self.find_isomorphism_btn)

        self.isomorphism_result = QTextEdit()
        self.isomorphism_result.setReadOnly(True)
        self.isomorphism_result.setMaximumHeight(100)
        isomorphism_layout.addWidget(self.isomorphism_result)

        isomorphism_panel.setLayout(isomorphism_layout)
        left_layout.addWidget(isomorphism_panel)

        path_panel = QGroupBox("Поиск пути")
        path_layout = QVBoxLayout()

        path_controls = QWidget()
        path_controls_layout = QHBoxLayout(path_controls)

        path_controls_layout.addWidget(QLabel("От:"))
        self.path_from_cb = QComboBox()
        self.path_from_cb.setEditable(False)
        path_controls_layout.addWidget(self.path_from_cb)

        path_controls_layout.addWidget(QLabel("До:"))
        self.path_to_cb = QComboBox()
        self.path_to_cb.setEditable(False)
        path_controls_layout.addWidget(self.path_to_cb)

        path_layout.addWidget(path_controls)

        self.find_path_btn = QPushButton("Найти кратчайший путь")
        self.find_path_btn.clicked.connect(self.find_shortest_path)
        path_layout.addWidget(self.find_path_btn)

        self.path_result = QTextEdit()
        self.path_result.setReadOnly(True)
        self.path_result.setMaximumHeight(100)
        path_layout.addWidget(self.path_result)

        path_panel.setLayout(path_layout)
        left_layout.addWidget(path_panel)

        left_layout.addStretch()

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.scene = QGraphicsScene()
        self.graph_manager = GraphManager(self.scene)
        self.scene = GraphScene(self.graph_manager, self)
        self.graph_manager.scene = self.scene

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)

        right_layout.addWidget(QLabel("Редактор графа (ЛКМ - узел, Shift+ЛКМ - ребро, ПКМ - удалить):"))
        right_layout.addWidget(self.view)

        graph_buttons_layout = QHBoxLayout()

        self.clear_graph_btn = QPushButton("Очистить граф")
        self.clear_graph_btn.clicked.connect(self.clear_graph)
        graph_buttons_layout.addWidget(self.clear_graph_btn)

        graph_buttons_layout.addStretch()
        right_layout.addLayout(graph_buttons_layout)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])

        main_layout.addWidget(splitter)

        self.graph_manager.node_count_changed.connect(self.matrix_widget.update_size)
        self.graph_manager.graph_changed.connect(self.update_graph_info)

        self.create_menu()

        self.update_graph_info()

    def create_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("Файл")

        save_action = QAction("Сохранить...", self)
        save_action.triggered.connect(self.save_graph)
        file_menu.addAction(save_action)

        load_action = QAction("Загрузить...", self)
        load_action.triggered.connect(self.load_graph)
        file_menu.addAction(load_action)

        clear_action = QAction("Очистить всё", self)
        clear_action.triggered.connect(self.clear_all)
        file_menu.addAction(clear_action)

    def insert_star_to_selected(self):
        selected = self.matrix_widget.selectedRanges()
        if not selected:
            QMessageBox.information(self, "Информация", "Выделите ячейки в матрице")
            return

        self.matrix_widget.blockSignals(True)
        for range_ in selected:
            for row in range(range_.topRow(), range_.bottomRow() + 1):
                for col in range(range_.leftColumn(), range_.rightColumn() + 1):
                    if row != col:
                        item = self.matrix_widget.item(row, col)
                        if item:
                            item.setText("*")
        self.matrix_widget.blockSignals(False)

    def insert_zero_to_selected(self):
        selected = self.matrix_widget.selectedRanges()
        if not selected:
            QMessageBox.information(self, "Информация", "Выделите ячейки в матрице")
            return

        self.matrix_widget.blockSignals(True)
        for range_ in selected:
            for row in range(range_.topRow(), range_.bottomRow() + 1):
                for col in range(range_.leftColumn(), range_.rightColumn() + 1):
                    if row != col:
                        item = self.matrix_widget.item(row, col)
                        if item:
                            item.setText("0")
        self.matrix_widget.blockSignals(False)

    def update_graph_info(self):
        nodes = self.graph_manager.get_node_names()

        self.path_from_cb.clear()
        self.path_to_cb.clear()
        self.path_from_cb.addItems(sorted(nodes))
        self.path_to_cb.addItems(sorted(nodes))

    def find_isomorphism(self):
        try:
            matrix = self.matrix_widget.get_adjacency_matrix()
            matrix_nodes = [f"П{i + 1}" for i in range(len(matrix))]

            graph_adj = self.graph_manager.get_adjacency_dict()

            if len(matrix_nodes) != len(graph_adj):
                self.isomorphism_result.setText(
                    f"Количество вершин не совпадает!\n"
                    f"В матрице: {len(matrix_nodes)} вершин\n"
                    f"В графе: {len(graph_adj)} вершин"
                )
                for node in self.graph_manager.get_nodes():
                    node.set_isomorphism_color(False)
                self.current_isomorphism = {}
                return

            G1 = nx.Graph()
            G2 = nx.Graph()

            for node in matrix_nodes:
                G1.add_node(node)

            for node_name in graph_adj.keys():
                G2.add_node(node_name)

            n = len(matrix)
            for i in range(n):
                for j in range(i + 1, n):
                    if matrix[i][j] != 0:
                        G1.add_edge(matrix_nodes[i], matrix_nodes[j])

            for node, neighbors in graph_adj.items():
                for neighbor in neighbors:
                    if node < neighbor:
                        G2.add_edge(node, neighbor)

            debug_info = (
                f"G1: {len(G1.nodes())} вершин, {len(G1.edges())} рёбер\n"
                f"G2: {len(G2.nodes())} вершин, {len(G2.edges())} рёбер\n"
                f"Рёбра G1: {list(G1.edges())}\n"
                f"Рёбра G2: {list(G2.edges())}\n"
            )

            if len(G1.edges()) != len(G2.edges()):
                self.isomorphism_result.setText(
                    f"Количество рёбер не совпадает!\n"
                    f"В матрице: {len(G1.edges())} рёбер\n"
                    f"В графе: {len(G2.edges())} рёбер\n\n"
                    f"{debug_info}"
                )
                for node in self.graph_manager.get_nodes():
                    node.set_isomorphism_color(False)
                self.current_isomorphism = {}
                return

            try:
                isomorphism_mapping = nx.vf2pp_isomorphism(G1, G2)
            except AttributeError:
                from networkx.algorithms import isomorphism
                GM = isomorphism.GraphMatcher(G1, G2)
                if GM.is_isomorphic():
                    isomorphism_mapping = GM.mapping
                else:
                    isomorphism_mapping = None

            if isomorphism_mapping is None:
                self.current_isomorphism = {}
                self.isomorphism_result.setText(
                    f"Изоморфизм не найден\n\n{debug_info}"
                )
                for node in self.graph_manager.get_nodes():
                    node.set_isomorphism_color(False)
            else:
                self.current_isomorphism = isomorphism_mapping

                result_text = "Изоморфизм найден:\n"
                for matrix_node, graph_node in sorted(self.current_isomorphism.items()):
                    result_text += f"{matrix_node} → {graph_node}\n"

                self.graph_manager.highlight_isomorphism(self.current_isomorphism)

                self.isomorphism_result.setText(result_text)

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.current_isomorphism = {}
            self.isomorphism_result.setText(f"Ошибка: {str(e)}\n\nДетали:\n{error_details}")
            for node in self.graph_manager.get_nodes():
                node.set_isomorphism_color(False)

    def find_shortest_path(self):
        if not self.current_isomorphism or not isinstance(self.current_isomorphism, dict):
            QMessageBox.warning(self, "Ошибка", "Сначала найдите изоморфизм")
            return

        from_node = self.path_from_cb.currentText()
        to_node = self.path_to_cb.currentText()

        if not from_node or not to_node:
            QMessageBox.warning(self, "Ошибка", "Выберите вершины")
            return

        if from_node == to_node:
            QMessageBox.warning(self, "Ошибка", "Выберите разные вершины")
            return

        try:
            matrix_data = self.matrix_widget.get_data()
            n = len(matrix_data)
            weight_matrix = []

            for i in range(n):
                row = []
                for j in range(n):
                    if i == j:
                        row.append(0.0)
                    else:
                        val_str = matrix_data[i][j].strip()
                        if val_str == "*":
                            row.append(1.0)
                        elif val_str == "":
                            row.append(float('inf'))
                        else:
                            try:
                                val = float(val_str)
                                row.append(val if val != 0 else float('inf'))
                            except ValueError:
                                row.append(float('inf'))
                weight_matrix.append(row)

            reverse_map = {v: k for k, v in self.current_isomorphism.items()}

            weighted_graph = nx.Graph()

            for node in self.graph_manager.get_node_names():
                weighted_graph.add_node(node)

            nodes = self.graph_manager.get_node_names()
            for i, node_i in enumerate(nodes):
                matrix_node_i = reverse_map.get(node_i)
                if not matrix_node_i:
                    continue

                idx_i = int(matrix_node_i[1:]) - 1

                for j, node_j in enumerate(nodes):
                    if i >= j:
                        continue

                    matrix_node_j = reverse_map.get(node_j)
                    if not matrix_node_j:
                        continue

                    idx_j = int(matrix_node_j[1:]) - 1
                    weight = weight_matrix[idx_i][idx_j]

                    if weight != float('inf'):
                        weighted_graph.add_edge(node_i, node_j, weight=weight)

            if nx.has_path(weighted_graph, from_node, to_node):
                path = nx.shortest_path(weighted_graph, from_node, to_node, weight='weight')
                length = nx.shortest_path_length(weighted_graph, from_node, to_node, weight='weight')

                path_str = " → ".join(path)
                result = f"Путь: {path_str}\nДлина: {length}"
                self.path_result.setText(result)
            else:
                self.path_result.setText("Путь не существует")

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.path_result.setText(f"Ошибка: {str(e)}\n\nДетали:\n{error_details}")

    def clear_graph(self):
        self.graph_manager.reset()
        self.current_isomorphism = {}
        self.isomorphism_result.clear()
        self.path_result.clear()

    def clear_all(self):
        self.clear_graph()
        self.matrix_widget.setRowCount(0)
        self.matrix_widget.setColumnCount(0)

    def save_graph(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить граф", "", "JSON Files (*.json)")
        if not file_path:
            return

        nodes_data = []
        node_id_map = {}

        nodes = self.graph_manager.get_nodes()
        for idx, node in enumerate(nodes):
            node_id_map[node] = idx
            nodes_data.append({
                "name": node.name,
                "x": node.pos().x(),
                "y": node.pos().y()
            })

        edges_data = []
        visited = set()
        for node in nodes:
            for edge in node.edges:
                if edge not in visited:
                    visited.add(edge)
                    u_id = node_id_map.get(edge.source)
                    v_id = node_id_map.get(edge.dest)
                    if u_id is not None and v_id is not None:
                        edges_data.append({"u": u_id, "v": v_id})

        matrix_data = self.matrix_widget.get_data()

        data = {
            "nodes": nodes_data,
            "edges": edges_data,
            "matrix": matrix_data
        }

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "Успех", "Граф сохранен")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {e}")

    def load_graph(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Загрузить граф", "", "JSON Files (*.json)")
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.clear_all()

            nodes_list = data.get("nodes", [])
            edges_list = data.get("edges", [])
            matrix_data = data.get("matrix", [])

            id_to_node = {}
            for n_data in nodes_list:
                pos = QPointF(n_data["x"], n_data["y"])
                name = n_data["name"]
                node = self.graph_manager.create_node(pos, name)
                id_to_node[n_data.get("id", len(id_to_node))] = node

            for e_data in edges_list:
                u = id_to_node.get(e_data["u"])
                v = id_to_node.get(e_data["v"])
                if u and v:
                    self.graph_manager.create_edge(u, v)

            self.matrix_widget.set_data(matrix_data)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyle("Fusion")
    dark_palette = app.palette()
    dark_palette.setColor(dark_palette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette.setColor(dark_palette.ColorRole.WindowText, Qt.white)
    dark_palette.setColor(dark_palette.ColorRole.Base, QColor(25, 25, 25))
    dark_palette.setColor(dark_palette.ColorRole.Text, Qt.white)
    dark_palette.setColor(dark_palette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(dark_palette.ColorRole.ButtonText, Qt.white)
    app.setPalette(dark_palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())