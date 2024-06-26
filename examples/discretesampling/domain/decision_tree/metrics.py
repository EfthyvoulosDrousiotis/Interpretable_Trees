import math
import numpy as np
import collections
import pandas as pd


class stats():
    def __init__(self, trees, X_test):
        self.trees = trees

    def getLeafPossibilities(self, x):
        target1, leafs_possibilities_for_prediction = calculate_leaf_occurences(x)
        return leafs_possibilities_for_prediction
    
    def print_top_k_performing_trees(smcAccuracy_diagnostics, treeSMCSamples, k, weights, leaf_possibilities):
        top_k_performing_trees = []
        enumerated_list = list(enumerate(weights))
        # Sort the enumerated list based on the values (the second element in each pair)
        sorted_list = sorted(enumerated_list, key=lambda x: x[1], reverse = True)
        # Extract the sorted values and indices
        sorted_values = [x[1] for x in sorted_list]
        sorted_indices = [x[0] for x in sorted_list]
        av_acc= []
        leaf_poss= []
        for i in range(k):
            #print("Accuracy of the tree:", smcAccuracy_diagnostics[sorted_indices[i]])
            #print(treeSMCSamples[sorted_indices[i]].tree)
            top_k_performing_trees.append(treeSMCSamples[sorted_indices[i]])
            av_acc.append(smcAccuracy_diagnostics[sorted_indices[i]])
            leaf_poss.append(leaf_possibilities[sorted_indices[i]])
        return top_k_performing_trees, av_acc, leaf_poss
    
    

    def majority_voting_predict(self, smcLabels):  # this function should be moved to a more appropriate place
        labels = []
        predictions = pd.DataFrame(smcLabels)
        for column in predictions:
            labels.append(predictions[column].mode())
        labels = pd.DataFrame(labels)
        labels = labels.values.tolist()
        labels1 = []
        
        if len(labels[0]) > 1:
            for label in labels:
                labels1.append(label[0])
            # acc = dt.accuracy(y_test, labels1)
            labels = labels1
        # else:
            # acc = dt.accuracy(y_test, labels)
        labels = list(np.array(labels).flatten())
        return labels

    def predict(self, X_test, use_majority=True):
        all_labels_from_all_trees = []
        for tree in self.trees:
            all_labels_from_this_trees = self.predict_for_one_tree(tree, X_test)
            all_labels_from_all_trees.append(all_labels_from_this_trees)

        if use_majority:
            return self.majority_voting_predict(all_labels_from_all_trees)
        else:
            return all_labels_from_all_trees

    def predict_for_one_tree(self, tree, X_test):
        all_labels_for_this_tree = []
        leaf_possibilities = self.getLeafPossibilities(tree)
        leafs = sorted(tree.leafs)
        for datum in X_test:
            label_for_this_datum = self.predict_for_one_datum(tree, leafs, leaf_possibilities, datum)
            all_labels_for_this_tree.append(label_for_this_datum)
        return all_labels_for_this_tree

    def predict_for_one_datum(self, tree, leafs, leaf_possibilities, datum):

        label = None
        flag = "false"
        current_node = tree.tree[0]
        label_max = -1
        # make sure that we are not in leafs. current_node[0] is the node
        while current_node[0] not in leafs and flag == "false":
            if datum[current_node[3]] > current_node[4]:
                for node in tree.tree:
                    if node[0] == current_node[2]:
                        current_node = node
                        break
                    if current_node[2] in leafs:
                        leaf = current_node[2]
                        flag = "true"
                        indice = leafs.index(leaf)
                        for x, y in leaf_possibilities[indice].items():
                            if y == label_max:
                                actual_label = 1

                            if y > label_max:
                                label_max = y
                                actual_label = x

                        label = actual_label
                        break

            else:
                for node in tree.tree:
                    if node[0] == current_node[1]:
                        current_node = node
                        break
                    if current_node[1] in leafs:
                        leaf = current_node[1]
                        flag = "true"
                        indice = leafs.index(leaf)
                        for x, y in leaf_possibilities[indice].items():
                            if y == label_max:
                                actual_label = 1

                            if y > label_max:
                                label_max = y
                                actual_label = x

                        label = actual_label
                        break

        return label


def accuracy(y_test, labels):
    correct_classification = 0
    for i in range(len(y_test)):
        if labels[i] == y_test[i]:
            correct_classification += 1

    acc = correct_classification*100/len(y_test)
    return acc


# Π(Y_i|T,theta,x_i)
def calculate_leaf_occurences(x):
    '''
    we calculate how many labelled as 0 each leaf has, how many labelled as 1
    each leaf has and so on
    '''
    leaf_occurences = []
    k = 0
    for leaf in x.leafs:
        leaf_occurences.append([leaf])

    for datum in x.X_train:
        flag = "false"
        current_node = x.tree[0]

        # make sure that we are not in leafs. current_node[0] is the node
        while current_node[0] not in x.leafs and flag == "false":
            if datum[current_node[3]] > current_node[4]:
                for node in x.tree:
                    if node[0] == current_node[2]:
                        current_node = node
                        break
                    if current_node[2] in x.leafs:
                        leaf = current_node[2]
                        flag = "true"
                        break

            else:
                for node in x.tree:
                    if node[0] == current_node[1]:
                        current_node = node
                        break
                    if current_node[1] in x.leafs:
                        leaf = current_node[1]
                        flag = "true"
                        break

        '''
        create a list of lists that holds the leafs and the number of
        occurences for example [[4, 1, 1, 2, 2, 2], [5, 1, 1, 2, 2, 1],
        [6, 1, 2, 2, 1, 2], [7, 2, 2, 2, 1, 2, 1, 2]]
        The first number represents the leaf id number
        '''

        for item in leaf_occurences:

            if item[0] == leaf:
                item.append(x.y_train[k])
        k += 1

    '''
    we have some cases where some leaf nodes may do not have any probabilities
    because no data point ended up in the particular leaf
    We add equal probabilities for each label to the particular leaf.
    For example if we have 4 labels, we add 0:0.25, 1:0.25, 2:0.25, 3:0.25
    '''

    for item in leaf_occurences:
        if len(item) == 1:
            unique = set(x.y_train)
            unique = list(unique)
            for i in range(len(unique)):
                item.append(i)

    leaf_occurences = sorted(leaf_occurences)
    leafs = sorted(x.leafs)

    '''
    we then delete the first number of the list which represents the leaf node
    id.
    '''
    for i in range(len(leaf_occurences)):
        new_list = True
        for p in range(len(leaf_occurences[i])):
            if new_list:
                new_list = False
                del leaf_occurences[i][p]

    '''
    first count the number of labels in each leaf.
    Then create probabilities by normalising those values[0,1]
    '''
    leafs_possibilities = []
    for number_of_leafs in range(len(leaf_occurences)):
        occurrences = collections.Counter(leaf_occurences[number_of_leafs][:])
        leafs_possibilities.append(occurrences)

    # create leafs possibilities
    for item in leafs_possibilities:
        factor = 1.0/sum(item.values())
        for k in item:
            item[k] = item[k]*factor

    product_of_leafs_probabilities = []
    k = 0
    for datum in x.X_train:
        # print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        flag = "false"
        current_node = x.tree[0]
        # make sure that we are not in leafs. current_node[0] is the node
        while current_node[0] not in leafs and flag == "false":
            if datum[current_node[3]] > current_node[4]:
                for node in x.tree:
                    if node[0] == current_node[2]:
                        current_node = node
                        break
                    if current_node[2] in leafs:
                        leaf = current_node[2]
                        # print(leaf)
                        flag = "true"
                        break

            else:
                for node in x.tree:
                    if node[0] == current_node[1]:
                        current_node = node
                        break
                    if current_node[1] in leafs:
                        leaf = current_node[1]
                        # print(leaf)
                        flag = "true"
                        break

        if leaf in leafs:
            # find the position of the dictionary probabilities given the leaf
            # number
            indice = leafs.index(leaf)
            probs = leafs_possibilities[indice]
            for prob in probs:
                target_probability = probs[x.y_train[k]]

                '''
                we make sure that in the case we are on a homogeneous leaf,
                we dont get a 0 probability but a very low one
                '''

                if target_probability == 0:
                    target_probability = 0.02
                if target_probability == 1:
                    target_probability = 0.98

            product_of_leafs_probabilities.append(math.log(target_probability))

        k += 1
    product_of_target_feature = np.sum(product_of_leafs_probabilities)
    return product_of_target_feature, leafs_possibilities

def max_depth(tree):
    max_depth_tree=0
    for node in tree:#calculate the depth of tree (node[5] is the depth of each node)
        if node[5] > max_depth_tree:
            max_depth_tree = node[5]
    return max_depth_tree

def trees_similarity(tree1, tree2):
    tree1_depth = max_depth(tree1)
    tree2_depth = max_depth(tree2)
    
    points_list1 = [0.5]
    points_list2 = [0.5]
    
    '''
    calculate the points for every tree
    '''
    for i in (n+1 for n in range(len(tree1))):
        points_list1.append(points_list1[i-1]/2)
    for i in (n+1 for n in range(len(tree2))):
        points_list2.append(points_list2[i-1]/2)
    
    
    
    if sum(points_list1) >= sum(points_list2):#create the points list based on the biggest tree
        big_tree = tree1
        small_tree = tree2
        points_list = points_list1
    else:
        big_tree = tree2
        small_tree = tree1
        points_list = points_list2       
    
    # print("tree1 points ", points_list1)
    # print("tree2 points ", points_list2)
    
    points = []
    total_avail_points = []
    for big_node in big_tree: #allocate the points for same node in depth i
        current_depth = big_node[5]
        total_avail_points.append(points_list[current_depth])
        for small_node in small_tree :
            # if big_node == small_node and small_node[5]==current_depth:
            #     points += points_list[current_depth]
            if big_node[3] == small_node[3] and small_node[5]==current_depth:
                points.append(points_list[current_depth])
                break      
    return np.sum(points)*100/(np.sum(total_avail_points))




