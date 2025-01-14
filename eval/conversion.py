import networkx as nx
import sys
import random
import io
import copy
import numpy as np
import time
import pickle
import argparse
import os

def main():
    args = make_arguments().parse_args()
    source_path = args.src
    store_dir = args.store_dir
    action = args.action

    try:
        os.mkdir(store_dir)
    except:
        pass

    if action == "sat2lcg":  # default TODO
        for filename in os.listdir(source_path):  # G2SAT/dataset/test_formulas/
            assert(filename[-4:] == ".cnf")
            lcg_filename = filename.split(".")[0] + "_lcg_edge_list"
            LCG = sat_to_LCG(source_path + "/" + filename)
            save_graph_list(LCG, "{}/{}".format(store_dir, lcg_filename))
    elif action == "lcg2sat":  # used for generation
        graphs = load_graphs(source_path)
        benchmark_name = os.path.basename(source_path).split('.')[0]
        for i, graph in enumerate(graphs):
            LCG_to_sat(graph, "{}/{}_{}.cnf".format(store_dir, benchmark_name, i))
    else:
        print("Invalid action!")
    return

def make_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", type=str, help="path to source objects")
    parser.add_argument("--store-dir", "-s", type=str, help="Directory to store the converted objects")
    parser.add_argument("--action", "-a", type=str, default="sat2lcg", help="sat2lcg/lcg2sat")
    return parser

def save_graph_list(G, fname):
    with open(fname, "wb") as f:
        nx.write_edgelist(G, f)

def load_graphs(filename):
    graphs = []
    Gs = nx.read_gpickle(filename)
    for G in Gs:
        graph = nx.Graph()
        graph.add_nodes_from(G[0])
        graph.add_edges_from(G[1])
        graphs.append(graph)
    return graphs     

def cut_inner_edge(mat, partite):
    for i in range(partite):
        for j in range (partite):
            mat[i][j] = 0
    for i in range(len(mat) - partite):
        for j in range(len(mat) - partite):
            mat[i + partite][j + partite] = 0
    return mat

# convert a file of adjacency matrix to a matrix
def file_to_mat(filename):
    print ("reading file...")
    lst = []
    with open(filename, 'r') as file:
        for line in file.readlines():
            if ',' in line:
                l = line.split(", ")
                while "\n" in l:
                    l.remove("\n")
            else:
                l = line.split()
            for i in range(len(l)):
                l[i] = int(float(l[i]))
            lst.append(l)
    print ("Successful!")
    return lst

# Takes in an adjacency matrix of a VCG, convert it to a dimacs file
def LCG_to_sat(graph, save_name):
    nodes = list(graph.nodes())
    assert(0 in nodes)
    num_var = min(list(graph.neighbors(0)))  #TODO ??????? min???
    clauses = []
    for node in nodes:
        if (node >= num_var * 2):
            neighbors = list(graph.neighbors(node))
            clause = ""
            assert(len(neighbors) > 0)
            for lit in neighbors:
                if lit < num_var:
                    clause += "{} ".format(lit + 1)
                else:
                    assert(lit < 2 * num_var)
                    clause += "{} ".format(-(lit - num_var + 1))
            clause += "0\n"
            clauses.append(clause)
    with open(save_name, 'w') as out_file:
        out_file.write("c generated by G2SAT lcg\n")
        out_file.write("p cnf {} {}\n".format(num_var, len(clauses)))
        for clause in clauses:
            out_file.write(clause)
    return

# Takes in an dimacs file, convert it to a networkx graph representation of the variable-clause graph
def sat_to_VCG(source):
    cnf = open(source)
    content = cnf.readlines()
    while content[0].split()[0] == 'c':
        content = content[1:]
    while len(content[-1].split()) <= 1:
        content = content[:-1]

    # Paramters
    parameters = content[0].split()
    formula = content[1:] # The clause part of the dimacs file
    formula = to_int_matrix(formula)
    num_vars = int(parameters[2])
    num_clause = int(parameters[3])

    VCG = nx.Graph()
    VCG.add_nodes_from(range(num_vars + num_clause + 1)[1:])
    preprocess_VCG(formula, VCG, num_vars) # Build a VCG
    return VCG

# Takes in an dimacs file, convert it to a nx graph representation of the literal-clause graph
def sat_to_LCG(source):
    cnf = open(source)
    content = cnf.readlines()
    while content[0].split()[0] == 'c':
        content = content[1:]
    while len(content[-1].split()) <= 1:
        content = content[:-1]

    # Paramters
    parameters = content[0].split()
    formula = content[1:] # The clause part of the dimacs file
    formula = to_int_matrix(formula)
    num_vars = int(parameters[2])
    num_clause = int(parameters[3])

    VCG = nx.Graph()
    VCG.add_nodes_from(range(num_vars * 2 + num_clause + 1)[1:])
    preprocess_LCG(formula, VCG, num_vars) # Build a VCG
    #    mat = nx.adjacency_matrix(VCG)
    return VCG

# Takes in an dimacs file, convert it to a nx graph representation of the literal incidence graph
def sat_to_LIG(source):
    cnf = open(source)
    content = cnf.readlines()
    while content[0].split()[0] == 'c':
        content = content[1:]
    while len(content[-1].split()) <= 1:
        content = content[:-1]

    # Paramters
    parameters = content[0].split()
    formula = content[1:]
    formula = to_int_matrix(formula)
    num_vars = int(parameters[2])
    num_clause = int(parameters[3])
    #print (num_vars)

    LIG = nx.Graph()
    LIG.add_nodes_from(range(num_vars * 2 + 1)[1:])
    preprocess_LIG(formula, LIG, num_vars) # Build a LIG
    return LIG

# Takes in an dimacs file, convert it to a nx graph representation of the variable incidence graph
def sat_to_VIG(source):
    cnf = open(source)
    content = cnf.readlines()
    while content[0].split()[0] == 'c':
        content = content[1:]
    while len(content[-1].split()) <= 1:
        content = content[:-1]

    # Paramters
    parameters = content[0].split()
    formula = content[1:]
    formula = to_int_matrix(formula)
    num_vars = int(parameters[2])
    num_clause = int(parameters[3])
    #print (num_vars)

    VIG = nx.Graph()
    VIG.add_nodes_from(range(num_vars + 1)[1:])
    preprocess_VIG(formula, VIG, num_vars) # Build a LIG
    return VIG

def get_cl_string(clause):
    s = ""
    clause = sorted(clause)
    for ele in clause:
        s += str(ele) + "-"
    return s[:-1]

def remove_duplicate(content):
    new_content = [content[0].split()]
    cs = set()
    num_clause = 0
    for line in content[1:]:
        line = map(int, line.split()[:-1])
        c = get_cl_string(line)
        if c not in cs:
            num_clause += 1
            new_content.append(line)
            cs.add(c)
    new_content[0][3] = num_clause
    return new_content

def preprocess_VCG(formula, VCG, num_vars):
    """
    Builds VCG
    """
    for cn in range(len(formula)):
        for var in formula[cn]:
            if var > 0:
                VCG.add_edge(var, cn +  num_vars + 1)
            elif var < 0:
                VCG.add_edge(abs(var), cn + num_vars + 1)

def preprocess_LCG(formula, LCG, num_vars):
    """
    Builds LCG
    """
    for cn in range(len(formula)):
        for var in formula[cn]:
            if var > 0:
                LCG.add_edge(var, cn + 2 * num_vars + 1)
            elif var < 0:
                LCG.add_edge(abs(var) + num_vars, cn + 2 * num_vars + 1)

def preprocess_LIG(formula, LIG, num_vars):
    """
    Builds LIG.
    """
    for cn in range(len(formula)):
        for i in range(len(formula[cn])-1):
            for j in range(len(formula[cn]))[i+1:]:
                lit1 = formula[cn][i]
                lit2 = formula[cn][j]
                if lit1 > 0:
                    node1 = lit1
                elif lit1 < 0:
                    node1 = abs(lit1) + num_vars
                if lit2 > 0:
                    node2 = lit2
                elif lit2 < 0:
                    node2 = abs(lit2) + num_vars
                LIG.add_edge(node1, node2)

def preprocess_VIG(formula, VIG, num_vars):
    """
    Builds VIG.
    """
    for cn in range(len(formula)):
        for i in range(len(formula[cn])-1):
            for j in range(len(formula[cn]))[i+1:]:
                lit1 = formula[cn][i]
                lit2 = formula[cn][j]
                if lit1 > 0:
                    node1 = lit1
                elif lit1 < 0:
                    node1 = abs(lit1)
                if lit2 > 0:
                    node2 = lit2
                elif lit2 < 0:
                    node2 = abs(lit2)
                VIG.add_edge(node1, node2)

def to_int_matrix(formula):
    new_formula = []
    for i in range(len(formula)):
        line = []
        for ele in formula[i].split()[: -1]:
            line.append(int(ele))
        new_formula.append(line)
    return new_formula

if __name__ == "__main__":
    main()
