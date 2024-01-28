# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : generate_graph.py
# Description：make dot and pdf file for all generated IAG
"""
import argparse
import re
import os
import shutil
from graphviz import Digraph

def graph_txt_construct(fname):
    file_path = r".\exp_ASG_CTI_epoch3_1gpu\multirow_asg"+"\\"+fname
    f = open(file_path, "r")
    graph_lines = f.readlines()
    f.close()
    i = 1
    desktop_path = r".\exp_ASG_CTI_epoch3_1gpu\generated-graph-txt2"+"\\"  # new txt file
    if not os.path.exists(desktop_path):
        os.makedirs(desktop_path)
    else:
        shutil.rmtree(desktop_path)
        os.makedirs(desktop_path)

    for line in graph_lines:
        line = line.strip()
        if re.match("#[0-9]+", line):
            filename = desktop_path+str(i)+".txt"
            i += 1
            f = open(filename, "a+")
        elif line != "\n":
            f.write(line+"\n")
        else:
            continue

def graph_construct(fname,reslut_dir):
    desktop_path = reslut_dir
    if not os.path.exists(desktop_path):
        os.makedirs(desktop_path)
    else:
        shutil.rmtree(desktop_path)
        os.makedirs(desktop_path)

    for path in os.listdir(fname):
        graph_txt = fname + "\\"+ path
        f = open(graph_txt,"r",encoding="utf-8")
        graph_name_dot = path[:-4] + ".dot"
        graph_name_dot_path = desktop_path+graph_name_dot
        g = Digraph(graph_name_dot_path, filename=graph_name_dot)
        g.body.extend(
            ['rankdir="LR"', 'size="9"', 'fixedsize="false"', 'splines="true"', 'nodesep=0.3', 'ranksep=0',
             'fontsize=10',
             'overlap="scalexy"',
             'engine= "neato"'])
        graph_lines = f.readlines()
        entity_list = []
        #entity list
        entity_count = 0
        for line in graph_lines:
            if re.match("[A-Z]|[A-Z]/d",line):
                line = line.replace("\\", "\\\\\\\\")
                line = line.replace(":", "\\")
                line = line.replace("/", "\\\\")
                entity_list.append(str(entity_count)+"_"+line.strip())
                entity_count += 1
        print(entity_list)

        #relation list
        relation_list = []
        for line in graph_lines:
            if re.match("\d+\s\d+\s[A-Z]+",line):
                relation_list.append(line)
        print(relation_list)
        #draw entity
        for entity in entity_list:

            if entity.split("_")[1] in ["MP*","TP*"]:
                g.node(entity, shape='rectangle', node_type="Process",style='filled',fillcolor="lightblue:red")
            elif entity.split("_")[1] in ["MP","TP"]:
                g.node(entity, shape='rectangle', node_type="Process")
            elif entity.split("_")[1] == "SO":
                g.node(entity, shape='diamond', node_type="Socket")
            elif entity.split("_")[1] in ["MF","SF","TF"]:
                g.node(entity, shape='ellipse', node_type="File")
            elif entity.split("_")[1] == "R":
                g.node(entity, shape='house', node_type="registry")
        #draw edge
        edge_count = 1
        for relation in relation_list:
            sub = relation.split(" ",1)[0]
            obj = relation.split(" ",2)[1]
            verb_stage = relation.split(" ",2)[2].strip()
            parts = verb_stage.split("-")
            verb = parts[0]
            stage = parts[1:]
            sub = int(sub)
            obj = int(obj)
            print(sub,obj,verb)
            if verb == "RD":
                g.edge(entity_list[sub], entity_list[obj], label=str(edge_count) + ': ' + "RD")
                edge_count += 1
            elif verb == 'WR':
                g.edge(entity_list[sub], entity_list[obj], label=str(edge_count) + ': ' + "WR")
                edge_count += 1
            elif verb == 'EX':
                g.edge(entity_list[sub], entity_list[obj], label=str(edge_count) + ': ' + "EX")
                edge_count += 1
            elif verb == 'UK':
                g.edge(entity_list[sub], entity_list[obj], label=str(edge_count) + ': ' + "UK")
                edge_count += 1
            elif verb == 'CD':
                g.edge(entity_list[sub], entity_list[obj], label=str(edge_count) + ': ' + "CD")
                edge_count += 1
            elif verb == 'FR':
                g.edge(entity_list[sub], entity_list[obj], label=str(edge_count) + ': ' + "FR")
                edge_count += 1
            elif verb == 'IJ':
                g.edge(entity_list[sub], entity_list[obj], label=str(edge_count) + ': ' + "IJ")
                edge_count += 1
            elif verb == 'ST':
                g.edge(entity_list[sub], entity_list[obj], label=str(edge_count) + ': ' + "ST")
                edge_count += 1
            elif verb == 'RF':
                g.edge(entity_list[sub], entity_list[obj], label=str(edge_count) + ': ' + "RF")
                edge_count += 1
            if "1" in stage:
                g.edge(entity_list[sub], entity_list[obj], label=str(1), color="red")
            if "2" in stage:
                g.edge(entity_list[sub], entity_list[obj], label=str(2), color="blue")
            if "3" in stage:
                g.edge(entity_list[sub], entity_list[obj], label=str(3), color="yellow")
            if "4" in stage:
                g.edge(entity_list[sub], entity_list[obj], label=str(4), color="green")
            if "5" in stage:
                g.edge(entity_list[sub], entity_list[obj], label=str(5), color="pink")
        g.render(graph_name_dot_path, view=True)
        g.save(graph_name_dot_path)
def make_directory(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"'{directory_path}'creat")
    else:
        print(f"'{directory_path}'exist")
    return 1
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='visualize instantiation graph')
    # ******data args******
    parser.add_argument('--graph_path_txt', type=str, default='./generated_100_Asg/generated-graph-instance-result',
                        help='the instantiation graph', required=True)  # input generated data
    parser.add_argument('--graph_txt_path_2', type=str, default='./generated_100_Asg/generated-graph-instance-result-visualization',
                        help='the visualization result', required=True)  # output
    args = parser.parse_args()
    make_directory(args.graph_txt_path_2)
    graph_path_txt = args.graph_path_txt+"\\"
    graph_result = args.graph_txt_path_2+"\\"
    graph_construct(graph_path_txt,graph_result)