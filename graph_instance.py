# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : graph_instance.py
# Description：
"""
import os
import random
import re
from operator import itemgetter
import json

class Dataloader:
    def __init__(self):
        self.regu_path = r".\regulation_dic"
        self.tech_path = r".\tech_dic"
        self.sub_graph_path = r".\4000_3_generated_data_new2_sub"

    def get_relation_list(self,data):
        relation_list = [[],[],[],[]]
        i1 = 0
        for line in data:
            relation = []
            pattern = r'(\d+)\s+(\d+)\s+([A-Z]+)+(-\d+)'
            matches = re.findall(pattern, line)
            for match in matches:
                num1, num2, text, stage = match
                stage_true = int(stage[-1])-1
                relation.append(num1)
                relation.append(num2)
                relation.append(text)
                relation.append(i1)
                i1+=1
                relation_list[stage_true].append(relation)
        return relation_list

    def get_entity_list(self,data):
        entity_list = []
        for line in data:
            pattern = r"^([A-Z]{2})\*?"
            matches = re.findall(pattern, line)
            for match in matches:
                text = match
                entity_list.append(text)
        return entity_list

    def get_graph_info(self,whole_file_path):
        with open(whole_file_path,"r") as file:
            data = file.readlines()
            entity_list = self.get_entity_list(data)
            relation_list = self.get_relation_list(data)
        return data,entity_list,relation_list

    def read_json(self,file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data

    def load_regulation(self):
        for regulation in os.listdir(self.regu_path):
            if regulation.find("stage1")!=-1:
                whole_path = self.regu_path + "\\" + regulation
                stage1_index_regu_dic = self.read_json(whole_path)
            elif regulation.find("stage2")!=-1:
                whole_path = self.regu_path + "\\" + regulation
                stage2_index_regu_dic = self.read_json(whole_path)
            elif regulation.find("stage3")!=-1:
                whole_path = self.regu_path + "\\" + regulation
                stage3_index_regu_dic = self.read_json(whole_path)
            elif regulation.find("stage4")!=-1:
                whole_path = self.regu_path + "\\" + regulation
                stage4_index_regu_dic = self.read_json(whole_path)
        return stage1_index_regu_dic,stage2_index_regu_dic,stage3_index_regu_dic,stage4_index_regu_dic

    def load_tech(self):
        for tech in os.listdir(self.tech_path):
            whole_path = self.tech_path + "\\" + tech
            if tech.find("stage1") !=-1:
                stage1_index_tech_dic = self.read_json(whole_path)
            elif tech.find("stage2")!=-1:
                stage2_index_tech_dic = self.read_json(whole_path)
            elif tech.find("stage3")!=-1:
                stage3_index_tech_dic = self.read_json(whole_path)
            elif tech.find("stage4")!=-1:
                stage4_index_tech_dic = self.read_json(whole_path)
        return stage1_index_tech_dic,stage2_index_tech_dic,stage3_index_tech_dic,stage4_index_tech_dic

class Gene:
    """
    This is a class to represent individual(Gene) in GA algorithom
    each object of this class have two attribute: data, size
    """
    def __init__(self, **data):
        self.__dict__.update(data)
        self.size = len(data['data'])  # length of gene

class GA:
    """
    This is a class of GA algorithm.
    """
    def __init__(self, parameter):
        """
        Initialize the pop of GA algorithom and evaluate the pop by computing its' fitness value.
        The data structure of pop is composed of several individuals which has the form like that:
        {'Gene':a object of class Gene, 'fitness': 1.02(for example)}
        Representation of Gene is a list: [b s0 u0 sita0 s1 u1 sita1 s2 u2 sita2]
        """
        self.parameter = parameter
        stage_len_1 = self.parameter[4]
        stage_index_regu_dic = self.parameter[5]
        stage_index_tech_dic = self.parameter[6]
        entity_list = self.parameter[7]
        relation_list = self.parameter[8]
        stage = self.parameter[9]
        self.bound = []
        pop = []

        for i in range(self.parameter[3]):
            geneinfo = []
            for pos in range(stage_len_1):
                geneinfo.append(random.randint(0, 1))

            fitness,geneinfo,entity_regu_dic,relation_regu_dic = self.evaluate(geneinfo,relation_list,entity_list,stage,stage_len_1)  # evaluate each chromosome
            pop.append({'Gene': Gene(data=geneinfo), 'fitness': fitness,'entity_regu_dic':entity_regu_dic,'relation_regu_dic':relation_regu_dic})  # store the chromosome and its fitness

        self.pop = pop
        self.bestindividual = self.selectBest(self.pop)

    def match_rule(self,relation_info,entity_info,stage,stage_len_1):
        stage_index_regu_dic = self.parameter[5]
        stage_entity_list = []
        relation = relation_info[stage - 1]
        relation_list_specific = []
        relation_index_dic = {}
        index_small = 0
        rule_tatic_dic = {}
        for relation_small in relation:
            if relation_small[0] not in stage_entity_list:
                stage_entity_list.append(relation_small[0])
            if relation_small[1] not in stage_entity_list:
                stage_entity_list.append(relation_small[1])
            relation_specific = []
            relation_specific.append(entity_info[int(relation_small[0])])
            relation_specific.append(relation_small[2])
            relation_specific.append(entity_info[int(relation_small[1])])
            relation_index_dic[index_small] = relation_small[3]
            index_small += 1
            relation_list_specific.append(relation_specific)
        rule_match_edge_dic = {}
        for i in range(stage_len_1):
            rule_match_edge_dic[i] = []
            rule_name = list(stage_index_regu_dic.keys())[i]
            regu = stage_index_regu_dic[rule_name]
            j = 0
            flag = 0
            result = []
            temp = []
            while (j < len(relation_list_specific)):
                target_sub_index = flag % len(regu)
                sub = regu[target_sub_index]
                if relation_list_specific[j] == sub:
                    real_index = relation_index_dic[j]
                    temp.append(real_index)
                    flag += 1
                    if flag % len(regu) == 0 and flag != 0:
                        rule_match_edge_dic[i].append(temp)
                        temp = []
                j += 1

        for j in range(len(list(stage_index_regu_dic.keys()))):
            tactic = (list(stage_index_regu_dic.keys())[j].split(".")[1]).split("-")[0]
            rule_tatic_dic[j] = tactic
        return rule_match_edge_dic,rule_tatic_dic

    def find_target_rule(self,last_rule,match_rule):
        greater_numbers = [num for num in match_rule if num >= last_rule]
        smaller_numbers = [num for num in match_rule if num <= last_rule]

        if greater_numbers:
            nearest_greater = min(greater_numbers)
            return nearest_greater
        elif smaller_numbers:
            nearest_smaller = max(smaller_numbers)
            return nearest_smaller
        else:
            return None

    def check_order_of_values(self,my_dict, value1, value2):
        i1 = -1
        i2 = -1
        for value in my_dict.values():
            i1 += 1
            if value == value1:
                break
        for value in my_dict.values():
            i2 += 1
            if value == value2:
                break
        if i1 == -1 or i2 == -1:
            return True
        elif (i1 != -1 and i2 != -1) and (i1>i2):
            return False
        else:
            return True

    def evaluate(self, geneinfo,relation_info,entity_info,stage,stage_len_1):
        rule_match_edge_dic,rule_tatic_dic = self.match_rule(relation_info,entity_info,stage,stage_len_1)
        stage_entity_list = []
        relation = relation_info[stage-1]
        relation_list_specific = []
        relation_index_dic = {}
        index_small = 0
        for relation_small in relation:
            if relation_small[0] not in stage_entity_list:
                stage_entity_list.append(relation_small[0])
            if relation_small[1] not in stage_entity_list:
                stage_entity_list.append(relation_small[1])
            relation_specific = []
            relation_specific.append(entity_info[int(relation_small[0])])
            relation_specific.append(relation_small[2])
            relation_specific.append(entity_info[int(relation_small[1])])
            relation_index_dic[index_small] = relation_small[3]
            index_small += 1
            relation_list_specific.append(relation_specific)
        relation_arrange_dic = {}
        relation_regu_dic = {}
        relation_tactic_dic = {}
        entity_arrange_dic = {}
        entity_regu_dic = {}

        for i in range(len(relation)):
            index = relation_index_dic[i]
            relation_arrange_dic[index] = 0
            relation_regu_dic[index] = []

        for entity_small in stage_entity_list:
            entity_arrange_dic[entity_small] = 0
            entity_regu_dic[int(entity_small)] = []

        match_rule_whole = []
        match_edge_whole = []
        for i in range(len(relation)):
            real_index = relation_index_dic[i]
            if real_index not in match_edge_whole:
                match_rule = []
                for j in range(len(rule_match_edge_dic.items())):
                    key,value = list(rule_match_edge_dic.items())[j]
                    for small_match in value:
                        if real_index in small_match:
                            match_rule.append(key)
                if len(match_rule) == 0:
                    continue
                else:
                    if len(match_rule_whole) == 0:
                        last_rule = 0
                    else:
                        last_rule = match_rule_whole[-1]
                    target_rule = self.find_target_rule(last_rule,match_rule)
                    while(geneinfo[target_rule] != 1):
                        match_rule.remove(target_rule)
                        target_rule = self.find_target_rule(last_rule, match_rule)
                        if target_rule == None:
                            break
                    if target_rule != None:
                        match_rule_whole.append(target_rule)
                        for match_cluster in rule_match_edge_dic[target_rule]:
                            if real_index in match_cluster:
                                target_cluster = match_cluster
                        for edge in target_cluster:
                            relation_arrange_dic[edge] = 1
                            if edge not in match_edge_whole:
                                relation_regu_dic[edge].append(target_rule)
                                relation_tactic_dic[edge] = rule_tatic_dic[target_rule]
                            match_edge_whole.append(edge)
                            edge_info = relation[i]
                            entity_1 = int(edge_info[0])
                            entity_2 = int(edge_info[1])
                            entity_arrange_dic[int(entity_1)] = 1
                            entity_arrange_dic[int(entity_2)] = 1
                            if target_rule not in entity_regu_dic[int(entity_1)]:
                                entity_regu_dic[int(entity_1)].append(target_rule)
                            if target_rule not in entity_regu_dic[int(entity_2)]:
                                entity_regu_dic[int(entity_2)].append(target_rule)

        for x in range(len(geneinfo)):
            if geneinfo[x] ==1 and x not in match_rule_whole:
                geneinfo[x] = 0
        count = sum(1 for value in entity_arrange_dic.values() if value != 0)
        fitness = count / len(list(entity_arrange_dic.keys()))
        Flag1 = self.check_order_of_values(relation_tactic_dic,"Initial Access","Execution")
        Flag2 = self.check_order_of_values(relation_tactic_dic,"Privilege Escalation","Discovery")
        if (Flag1 == False) or (Flag2 == False):
            fitness = 0

        return fitness,geneinfo,entity_regu_dic,relation_regu_dic

    def selectBest(self, pop):
        """
        select the best individual from pop
        """
        s_inds = sorted(pop, key=itemgetter("fitness"), reverse=True)          # from large to small, return a pop
        return s_inds[0]

    def selection(self, individuals, k):
        """
        select some good individuals from pop, note that good individuals have greater probability to be choosen
        for example: a fitness list like that:[5, 4, 3, 2, 1], sum is 15,
        [-----|----|---|--|-]
        012345|6789|101112|1314|15
        we randomly choose a value in [0, 15],
        it belongs to first scale with greatest probability
        """
        s_inds = sorted(individuals, key=itemgetter("fitness"), reverse=True)  # sort the pop by the reference of fitness
        sum_fits = sum(ind['fitness'] for ind in individuals)  # sum up the fitness of the whole pop
        chosen = []
        for i in range(k):
            u = random.random() * sum_fits
            sum_ = 0
            for ind in s_inds:
                sum_ += ind['fitness']
                if sum_ >= u:
                    chosen.append(ind)
                    break
        chosen = sorted(chosen, key=itemgetter("fitness"), reverse=False)
        return chosen

    def crossoperate(self, offspring):
        """
        cross operation
        here we use two points crossoperate
        for example: gene1: [5, 2, 4, 7], gene2: [3, 6, 9, 2], if pos1=1, pos2=2
        5 | 2 | 4  7
        3 | 6 | 9  2
        =
        3 | 2 | 9  2
        5 | 6 | 4  7
        """
        dim = len(offspring[0]['Gene'].data)
        geninfo1 = offspring[0]['Gene'].data  # Gene's data of first offspring chosen from the selected pop
        geninfo2 = offspring[1]['Gene'].data  # Gene's data of second offspring chosen from the selected pop

        if dim == 1:
            pos1 = 1
            pos2 = 1
        else:
            pos1 = random.randrange(1, dim)  # select a position in the range from 0 to dim-1,
            pos2 = random.randrange(1, dim)

        newoff1 = Gene(data=[])  # offspring1 produced by cross operation
        newoff2 = Gene(data=[])  # offspring2 produced by cross operation
        temp1 = []
        temp2 = []
        for i in range(dim):
            if min(pos1, pos2) <= i < max(pos1, pos2):
                temp2.append(geninfo2[i])
                temp1.append(geninfo1[i])
            else:
                temp2.append(geninfo1[i])
                temp1.append(geninfo2[i])
        newoff1.data = temp1
        newoff2.data = temp2

        return newoff1, newoff2

    def mutation(self, crossoff, bound):
        """
        mutation operation
        """
        dim = len(crossoff.data)

        if dim == 1:
            pos = 0
        else:
            pos = random.randrange(0, dim)  # chose a position in crossoff to perform mutation.

        crossoff.data[pos] = random.randint(0, 1)
        return crossoff

    def GA_main(self):
        """
        main frame work of GA
        """
        popsize = self.parameter[3]
        stage_len_1 = self.parameter[4]
        # print("Start of evolution")
        stage_index_regu_dic = self.parameter[5]
        stage_index_tech_dic = self.parameter[6]
        entity_list = self.parameter[7]
        relation_list = self.parameter[8]
        stage = self.parameter[9]
        # Begin the evolution
        for g in range(NGEN):

            # Apply selection based on their converted fitness
            selectpop = self.selection(self.pop, popsize)

            nextoff = []
            while len(nextoff) != popsize:
                # Apply crossover and mutation on the offspring

                # Select two individuals
                offspring = [selectpop.pop() for _ in range(2)]
                if random.random() < CXPB:
                    crossoff1, crossoff2 = self.crossoperate(offspring)
                    if random.random() < MUTPB:
                        muteoff1 = self.mutation(crossoff1, self.bound)
                        muteoff2 = self.mutation(crossoff2, self.bound)
                        fit_muteoff1,muteoff1,entity_regu_dic1,relation_regu_dic1 = self.evaluate(muteoff1.data,relation_list,entity_list,stage,stage_len_1)  # Evaluate the individuals
                        fit_muteoff2,muteoff2,entity_regu_dic2,relation_regu_dic2 = self.evaluate(muteoff2.data,relation_list,entity_list,stage,stage_len_1)  # Evaluate the individuals
                        nextoff.append({'Gene': Gene(data=muteoff1), 'fitness': fit_muteoff1,'entity_regu_dic':entity_regu_dic1,'relation_regu_dic':relation_regu_dic1})
                        nextoff.append({'Gene': Gene(data=muteoff2), 'fitness': fit_muteoff2,'entity_regu_dic':entity_regu_dic2,'relation_regu_dic':relation_regu_dic2})
                    else:
                        fit_crossoff1,crossoff1,entity_regu_dic3,relation_regu_dic3 = self.evaluate(crossoff1.data,relation_list,entity_list,stage,stage_len_1)  # Evaluate the individuals
                        fit_crossoff2,crossoff2,entity_regu_dic4,relation_regu_dic4 = self.evaluate(crossoff2.data,relation_list,entity_list,stage,stage_len_1)
                        nextoff.append({'Gene': Gene(data=crossoff1), 'fitness': fit_crossoff1,'entity_regu_dic':entity_regu_dic3,'relation_regu_dic':relation_regu_dic3})
                        nextoff.append({'Gene': Gene(data=crossoff2), 'fitness': fit_crossoff2,'entity_regu_dic':entity_regu_dic4,'relation_regu_dic':relation_regu_dic4})
                else:
                    nextoff.extend(offspring)

                    # The population is entirely replaced by the offspring
                self.pop = nextoff

                # Gather all the fitnesses in one list and print the stats
                fits = [ind['fitness'] for ind in self.pop]

                best_ind = self.selectBest(self.pop)

                if best_ind['fitness'] > self.bestindividual['fitness']:
                    self.bestindividual = best_ind

        return self.bestindividual['Gene'].data,self.bestindividual['entity_regu_dic'],self.bestindividual['relation_regu_dic']

def read_new(json_file):
    file = open(json_file, 'r', encoding='utf-8')
    papers = []
    for line in file.readlines():
        dic = json.loads(line,strict=False)
        papers.append(dic)
    file.close()
    return papers

def make_directory(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    return 1


def find_target_relation(relation_list, key):
    for rela in relation_list:
        if rela[3] == key:
            return rela


if __name__ == "__main__":
    CXPB, MUTPB, NGEN, popsize = 0.8, 0.4, 5, 20  # popsize must be even number
    stage_len = [58,119,94,101]
    DL = Dataloader()
    stage1_index_regu_dic, stage2_index_regu_dic, stage3_index_regu_dic, stage4_index_regu_dic = DL.load_regulation()
    stage1_index_tech_dic, stage2_index_tech_dic, stage3_index_tech_dic, stage4_index_tech_dic = DL.load_tech()
    instance_lib = read_new(r".\instance_lib\technique-instance-lib-os-filter-add.json") #dir for instantiation lib
    new_instance_path = r".\4000_3_generated_data_new2_sub_instance_windows" #dir for IAG
    make_directory(new_instance_path)
    os_type = "linux"
    for txt in os.listdir(DL.sub_graph_path):
        whole_file_path = DL.sub_graph_path + "\\" + txt
        new_file_path = new_instance_path+"\\"+txt
        graph_data,entity_list,relation_list1 = DL.get_graph_info(whole_file_path)
        print(whole_file_path)
        entity_instance_dic = {}
        relation_instance_dic = {}
        for i in range(len(entity_list)):
            entity_instance_dic[i] = []
        sum_relation = 0
        for sublist in relation_list1:
            sum_relation += len(sublist)
        for i in range(sum_relation):
            relation_instance_dic[i] = []
        for stage in range(1,5):
            stage_index_regu_dic = DL.load_regulation()[stage-1]
            stage_index_tech_dic = DL.load_tech()[stage-1]
            stage_regu_len = stage_len[stage-1]
            print("entity_list"+str(entity_list))
            print("relation_list" + str(relation_list1))
            parameter = [CXPB, MUTPB, NGEN, popsize, stage_regu_len,stage_index_regu_dic, stage_index_tech_dic,entity_list,relation_list1,stage]
            run = GA(parameter)
            bestindividual_gene,bestindividual_entity_regu_dic,bestindividual_relation_regu_dic = run.GA_main()
            print("bestindividual_entity_regu_dic" + str(bestindividual_entity_regu_dic))
            print("bestindividual_relation_regu_dic"+str(bestindividual_relation_regu_dic))
            unsuccess_edge = [[]]
            for key in bestindividual_relation_regu_dic.keys():
                if len(bestindividual_relation_regu_dic[key]) == 0:
                    target_relation = find_target_relation(relation_list1[stage-1],key)
                    unsuccess_edge[0].append(target_relation)
            print("unsuccess_edge"+str(unsuccess_edge))
            if len(unsuccess_edge[0]) != 0:
                if stage == 1:
                    new_target_stage = 2
                else:
                    new_target_stage = stage-1
                stage_index_regu_dic2 = DL.load_regulation()[new_target_stage - 1]
                stage_index_tech_dic2 = DL.load_tech()[new_target_stage - 1]
                stage_regu_len2 = stage_len[new_target_stage - 1]
                parameter2 = [CXPB, MUTPB, NGEN, popsize, stage_regu_len2, stage_index_regu_dic2, stage_index_tech_dic2,entity_list, unsuccess_edge, 1]
                run2 = GA(parameter2)
                bestindividual_gene2, bestindividual_entity_regu_dic2, bestindividual_relation_regu_dic2 = run2.GA_main()
                print("bestindividual_entity_regu_dic2" + str(bestindividual_entity_regu_dic2))
                print("bestindividual_relation_regu_dic2 " + str(stage)+str(bestindividual_relation_regu_dic2))
                for key1 in bestindividual_relation_regu_dic2.keys():
                    if len(bestindividual_relation_regu_dic2[key1]) != 0:
                        info = str(new_target_stage) + "-" + str(bestindividual_relation_regu_dic2[key1][0])
                        bestindividual_relation_regu_dic[key1].append(info)
                        target_relation = find_target_relation(relation_list1[stage - 1], key1)
                        entity1 = int(target_relation[0])
                        entity2 = int(target_relation[1])
                        bestindividual_entity_regu_dic[entity1].append(info)
                        bestindividual_entity_regu_dic[entity2].append(info)
                print("bestindividual_relation_regu_dic"+str(bestindividual_relation_regu_dic))

            for key in list(bestindividual_entity_regu_dic.keys()):
                for l in range(len(bestindividual_entity_regu_dic[key])):
                    if str(bestindividual_entity_regu_dic[key][l]).find("-") != -1:
                        info = bestindividual_entity_regu_dic[key][l]
                    else:
                        info = str(stage)+"-"+str(bestindividual_entity_regu_dic[key][l])
                    if info not in entity_instance_dic[key]:
                        entity_instance_dic[key].append(info)

            for key in list(bestindividual_relation_regu_dic.keys()):
                for l in range(len(bestindividual_relation_regu_dic[key])):
                    if str(bestindividual_relation_regu_dic[key][l]).find("-") != -1:
                        info = bestindividual_relation_regu_dic[key][l]
                    else:
                        info = str(stage)+"-"+str(bestindividual_relation_regu_dic[key][l])
                    if info not in relation_instance_dic[key]:
                        relation_instance_dic[key].append(info)
        print("entity_instance_dic"+str(entity_instance_dic))
        print("relation_instance_dic"+str(relation_instance_dic))
        entity_one_instance_dic = {}

        for key in entity_instance_dic.keys():
            entity_one_instance_dic[key] = 0
            if len(entity_instance_dic[key]) != 0:
                target_rule = entity_instance_dic[key][random.randint(0, len(entity_instance_dic[key])-1)]
                target_type = entity_list[int(key)]
                target_stage = int(target_rule[0])
                target_rule_index = int(target_rule.split("-")[1])-1
                target_tech_dic = DL.load_tech()[target_stage-1]
                target_tech = target_tech_dic[list(target_tech_dic.keys())[target_rule_index]]
                target_instance_list = []
                for tech in target_tech:
                    for data in instance_lib:
                        if data["stage-key"] == tech+"-"+os_type:
                            for instance in data[target_type]:
                                target_instance_list.append(instance)
                if len(target_instance_list) != 0:
                    entity_one_instance_dic[key] = random.choice(target_instance_list)
                else:
                    entity_one_instance_dic[key] = "#######"
        print(entity_one_instance_dic)

        not_satisfied_entity = []
        for i in range(len(entity_one_instance_dic.keys())):
            if entity_one_instance_dic[list(entity_one_instance_dic.keys())[i]] != 0:
                graph_data[i+1] = graph_data[i+1].strip()+"-"+entity_one_instance_dic[list(entity_one_instance_dic.keys())[i]]+"\n"
            else:
                not_satisfied_entity.append(i+1)
        temp_graph_data = []
        for j in range(len(graph_data)):
            if j not in not_satisfied_entity:
                temp_graph_data.append(graph_data[j])
        delete_edge_list = []

        new_entity_match_dic = {}
        for e in range(int(temp_graph_data[0])):
            if e+1 not in not_satisfied_entity:
                i1 = 0
                for t in not_satisfied_entity:
                    if e+1 > t:
                        i1 += 1
                new_entity_match_dic[e] = e-i1
        print(new_entity_match_dic)
        for x in range(len(temp_graph_data)):
            if re.match("\d+\s\d+\s[A-Z]+", temp_graph_data[x]):
                sub = temp_graph_data[x].split(" ", 1)[0]
                obj = temp_graph_data[x].split(" ", 2)[1]
                verb = temp_graph_data[x].split(" ", 2)[2].strip()
                sub = int(sub)
                obj = int(obj)

                if (sub+1 in not_satisfied_entity ) or (obj+1 in not_satisfied_entity) :
                    if x not in delete_edge_list:
                        delete_edge_list.append(x)
                else:
                    temp_graph_data[x] = str(new_entity_match_dic[sub]) + " " +str(new_entity_match_dic[obj]) + " " + temp_graph_data[x][-5:]
        final_graph_data = []

        for v in range(len(temp_graph_data)):
            if v == 0:
                final_graph_data.append(str(len(new_entity_match_dic.keys()))+"\n")
            elif v not in delete_edge_list:
                final_graph_data.append(temp_graph_data[v])
        final_graph_data[len(new_entity_match_dic.keys())+1] = str(int(final_graph_data[len(new_entity_match_dic.keys())+1])-len(delete_edge_list))+"\n"

        with open(new_file_path, 'w', encoding='utf-8') as file:
            file.writelines(final_graph_data)
            file.close()

        count = sum(1 for value in entity_instance_dic.values() if len(value) != 0)
        coverage = count / len(list(entity_instance_dic.keys()))
        print(coverage)
        print(entity_instance_dic)