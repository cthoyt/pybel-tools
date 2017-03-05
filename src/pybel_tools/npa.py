"""

An implementation of the NPA algorithm inspired by Reagon Kharki's implementation

"""

from __future__ import print_function

from pybel.constants import RELATION, INCREASES, DIRECTLY_DECREASES, DIRECTLY_INCREASES, DECREASES

#: Signifies the initial gene expression/NPA score
WEIGHT = 'weight'

#: Signifies the NPA score in the node's data dictionary
SCORE = 'score'

#: The default score for NPA
DEFAULT_SCORE = 999.99

#: Signifies whether a node has predecessors in the node's data dictionary
HUB = 'hub'


def calculate_npa_score_iteration(graph, node):
    """

    Calculates the score of the given node

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :param node: A node in the BEL graph
    :type node: tuple
    :return:
    """

    weight = graph.node[node][WEIGHT]

    for predecessor in graph.predecessors_iter(node):
        if graph.edge[predecessor][node][RELATION] in {INCREASES, DIRECTLY_INCREASES}:
            weight += graph.node[predecessor][SCORE]
        elif graph.edge[predecessor][node][RELATION] in {DECREASES, DIRECTLY_DECREASES}:
            weight -= graph.node[predecessor][SCORE]

    return weight


def get_score_central_hub(graph, hub_dict, hub_list=None):
    """

    :param graph: A BEL graph
    :type graph: pybel.BELGraph
    :param hub_list:
    :param hub_dict:
    :return:
    """
    if not hub_list:
        return

    new_hub_list = []

    for hub in hub_list:
        flag = 0
        node = hub_dict[hub]

        for predecessor in graph.predecessors_iter(node):
            if graph.node[predecessor][SCORE] == DEFAULT_SCORE:
                flag = 1
                break

        if flag == 0:
            graph.node[node][SCORE] = calculate_npa_score_iteration(graph, node)
        else:
            new_hub_list.append(node)

    return get_score_central_hub(graph, hub_dict, new_hub_list)


def flag_hubs(graph):
    """

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    """
    for node in graph.nodes_iter():
        graph.node[node][HUB] = 0 < len(graph.predecessors(node))


def generate_hub_list(graph):
    """

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :return:
    """
    hub_dict = {i: node for i, node in enumerate(graph.nodes_iter()) if graph.node[node][HUB]}
    return hub_dict, list(hub_dict.values())


def do_work(graph, hub_dict, hub_list):
    """

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :param hub_dict:
    :type hub_dict: dict
    :param hub_list:
    :type hub_list: list

    :return:
    """
    c = 0
    while len(hub_list) > 0:
        toremove = []
        c += 1

        print("\n" + str(c), "hublist: ", hub_list)

        for h in hub_list:
            flag = 0
            node = hub_dict.get(h)
            for predecessor in graph.predecessors(node):
                if predecessor in hub_dict.values():
                    flag = 1
                    break
            if flag == 0:
                graph.node[node][SCORE] = calculate_npa_score_iteration(graph, node)
                toremove.append(h)

        hub_list = [x for x in hub_list if x not in toremove]
        print("removelist: ", toremove, 'hublist:', hub_list)

        if not toremove:
            hub_list = get_score_central_hub(graph, hub_dict, hub_list)

    print("\n############################\tfinal scores\t############################\n")
    for x in graph.nodes():
        print(x + "  =  " + str(graph.node[x]['score']))


def prep_scores(graph, heat_key=WEIGHT):
    """

    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :param heat_key:
    :type heat_key: str
    """
    for node in graph.nodes_iter():
        graph.node[node][SCORE] = DEFAULT_SCORE

        if not graph.predecessors(node):
            graph.node[node][SCORE] = graph.node[node][heat_key]


def npa(graph, heat_key=WEIGHT):
    """

    Limitations of this implenentation of the NPA algorithm:

    1. Collapse by central dogma down to genes
    2. need data already annotated on to your genes
    3. Networks can't contain:
        * yup


    :param graph: A BEL Graph
    :type graph: pybel.BELGraph
    :param heat_key:
    :type heat_key: str
    :return:
    """
    prep_scores(graph, heat_key=heat_key)
    flag_hubs(graph)
    hub_dict, hub_list = generate_hub_list(graph)
    do_work(graph, hub_dict, hub_list)
