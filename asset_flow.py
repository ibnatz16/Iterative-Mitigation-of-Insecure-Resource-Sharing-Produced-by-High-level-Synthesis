import os
import argparse
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout

"""
Below are the variable names to change based on example.
Change the DOT file names to those of which you are working on.
Variable "l" should be changed to the top level function name
Insecure and secure assets should be changed based on example.
"""

if __name__ == "__main__":
    argparser = argparse.ArgumentParser('Asset Flow')
    argparser.add_argument('datapath', default='HLS_Datapath.dot', nargs='?', help='name of HLS Datapath DOT file')
    argparser.add_argument('vars', default='OP_variables.dot', nargs='?', help='name of OP Variables DOT file')
    argparser.add_argument('label', default='top', help='name of top level function')
    argparser.add_argument('secure', default='input', help="secure asset name")
    argparser.add_argument('insecure', default='input', help="insecure asset name")
    args = argparser.parse_args()

    # Filename = HLS Datapath DOT file
    filename = args.datapath
    filepath = os.path.join("../dot_files",filename)

    # Filename = OP variable DOT file
    filename = args.vars
    filep = os.path.join("../dot_files",filename)

    l = args.label # Label based on top level
    # Read in dot file as text file
    with open(filep) as f:
        contents_OP = f.readlines()

    insecure_ast = "in_port_%s" % str(args.insecure) #From the top level inputs
    secure_ast = "in_port_%s" % str(args.secure) # From the top level inputs

    G = nx.DiGraph(nx.drawing.nx_pydot.read_dot(filepath))
    G.remove_node("\\n")
    """
    Get the name of nodes where insecure and secure go from the root.
    Input ports are not as nodes but as edges. So, get the nodes where they go and then traverse
    through them.
    """

    root = '0'
    insec_nodes = []
    sec_nodes = []
    clk_nodes = []

    # For coloring the nodes
    color_map_full = []

    # For labeling the graphs
    labelDict = {}

    succ = G._succ[root]
    for node in succ:
        if succ[node]['label'].find(insecure_ast) != -1:
            insec_nodes.append(node)
        if succ[node]['label'].find(secure_ast) != -1:
            sec_nodes.append(node)

    for node in insec_nodes: 
        # edges = list(nx.bfs_edges(G,node))
        successors = list(nx.bfs_successors(G,node))
        for i in successors:
            nodes = i[1]
            insec_nodes.extend(nodes)
        insec_nodes = list(set(insec_nodes))
    # nodes = [node] + [v for u, v in edges]
    # insec_nodes.extend(nodes)
    # insec_nodes = list(set(insec_nodes))

    for node in sec_nodes:
        successors = list(nx.bfs_successors(G,node))
        for i in successors:
            nodes = i[1]
            sec_nodes.extend(nodes)
        sec_nodes = list(set(sec_nodes))
    # edges = list(nx.bfs_edges(G,node))
    # nodes = [node] + [v for u, v in edges]
    # sec_nodes.extend(nodes)
    # sec_nodes = list(set(sec_nodes))
    color_dict = dict()
    nodes = G._node 
    for key in nodes:
        if key.isnumeric():
            labelDict[key] = nodes[key]['label']
        # if key in insec_nodes and key in sec_nodes:
        #     print(key)
        if key in insec_nodes:
            # if key in sec_nodes:
            #     color_map_full.append('purple')
            # else:
            color_dict[key] = "red"
            color_map_full.append('red')
        elif key in sec_nodes:
            color_dict[key] = "blue"
            color_map_full.append('blue')
        else:
            color_dict[key] = "black"
            color_map_full.append('black')

    operations = []
    for i in contents_OP:
        node_index = i.find(l)
        if node_index != -1:
            end_index = i.find("source")
            if end_index != -1:
                operations.append(i[node_index:end_index])

    for i in labelDict:
        f_unit = labelDict[i]
        if f_unit.find(l) != -1:
            space_index = f_unit.find(" ")
            f_unit = f_unit[4:space_index]
            for j in operations:
                if f_unit in j:
                    eq_index = j.find("=")
                    semicolon = j.find(";")
                    if eq_index != -1 and semicolon != -1:
                        labelDict[i] = j[eq_index+1:semicolon]

    #Get the subgraph for all the nodes of secure and insecure
    pos = graphviz_layout(G, prog='dot') #This do not work on ECE server as graphviz is not installed
    sub1 = G.subgraph(insec_nodes)
    sub2 = G.subgraph(sec_nodes)

    # Color the edges
    e_colors = nx.get_edge_attributes(G, 'color')
    insec_edges = sub1.edges()
    sec_edges = sub2.edges()
    plt.figure("Full Network")
    for edge in e_colors:
        if edge in insec_edges:
            e_colors[edge] = 'red'
        elif edge in sec_edges:
            e_colors[edge] = 'blue'
        else:
            e_colors[edge] = 'black'
    e_colors_values = e_colors.values()

    # Find the resource sharing problem
    secure_problem = []
    insec_areas = dict()
    prev_sec = []
    count = 0
    operations = ["plus", "mult"]
    prev_value = []
    prev_node = 0
    final_insec = {}
    for m,n in e_colors:
        if m in sec_nodes and n in insec_nodes:
            if color_dict[m] == "blue":
                secure_problem.append(m)
                insec = []
                insec.append(n)
                successors = list(nx.bfs_successors(G,n))
                for i in successors:
                    nodes = i[1]
                    insec.extend(nodes)
                if count == 0:
                    insec_areas[n] = insec
                    prev_sec = insec
                    count += 1
                elif (count != 0):
                    if n not in prev_sec:
                        insec_areas[n] = insec
                        prev_sec = insec
                        count += 1

    for m,n in insec_areas.items():
        for values in n:
            if labelDict[values].find("MUX") == -1:
                res = [op for op in operations if op in labelDict[values]]
                if res:
                    if prev_value:
                        if labelDict[values].find("reg"):
                            final_insec[prev_node] = prev_value
                    prev_value = res[0]
                    prev_node = values
    print("Resources Shared: ",final_insec)
    f = open("resource_sharing.txt", "w")
    f.write("Filename: top.c\nResources Shared: %s\n" % final_insec)
    f.close()

    # Draw the graph
    label_options = {"ec": "k", "fc": "white", "alpha": 0.7}
    nx.draw_networkx(G,pos,node_size=200,arrowsize=5, edge_color = e_colors_values, width = 0.5, node_color=color_map_full, bbox=label_options, node_shape='s', labels=labelDict,with_labels=True,arrows=True,font_size = 5)
    plt.show()
    nx.draw_networkx(G,pos,node_size=200,arrowsize=5, edge_color = e_colors_values, node_color=color_map_full, bbox=label_options, node_shape='s', arrows=True,font_size = 7)
    plt.show()
    print("Graphs are printed.")
