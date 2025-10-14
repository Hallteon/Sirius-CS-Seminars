import networkx as nx


def find_isomorphisms_networkx(matrix, num_nodes, letter_adj_dict, pins=None):
    """
    Сверхкомпактная версия с использованием NetworkX
    """
    G1 = nx.Graph()
    G2 = nx.Graph()

    for i, node1 in enumerate(num_nodes):
        for j, node2 in enumerate(num_nodes):
            if i < j and matrix[i][j] not in (0, None):
                G1.add_edge(node1, node2)

    for node, neighbors in letter_adj_dict.items():
        for neighbor in neighbors:
            G2.add_edge(node, neighbor)

    if pins:
        all_mappings = list(nx.vf2pp_isomorphism(G1, G2))
        valid_mappings = []

        for mapping in all_mappings:
            if all(mapping.get(k) == v for k, v in pins.items()):
                valid_mappings.append(mapping)

        return valid_mappings

    return nx.vf2pp_isomorphism(G1, G2)


# # Пример использованияlist(
# P = ['П1', 'П2', 'П3', 'П4', 'П5', 'П6', 'П7']
# M = [
#     [0, 0, 10, 0, 0, 0, 0],
#     [0, 0, 20, 0, 0, 0, 0],
#     [10, 20, 0, 8, 0, 0, 0],
#     [0, 0, 8, 0, 15, 12, 0],
#     [0, 0, 0, 15, 0, 0, 0],
#     [0, 0, 0, 12, 0, 0, 18],
#     [0, 0, 0, 0, 0, 18, 0],
# ]
#
# letters = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'К']
# letter_adj = {
#     'А': {'В'}, 'Б': {'Г'}, 'В': {'А', 'Д', 'Г'},
#     'Г': {'В', 'Б', 'Е'}, 'Д': {'В'}, 'Е': {'Г', 'К'}, 'К': {'Е'},
# }
#
# isomorphisms = find_isomorphisms_networkx(M, P, letter_adj)
#
# print(isomorphisms)
