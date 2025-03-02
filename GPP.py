# -*- coding: utf-8 -*-
"""CMP3005project

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1KISr79fuRVCSAa24y5ymRSEoBlyRXrui
"""

import networkx as nx
import random
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
import numpy as np
from scipy.optimize import linprog
import time

def kernighan_lin_algorithm(G, k):
    """
    Kernighan-Lin algorithm for graph partitioning.

    :param G: A NetworkX graph.
    :param k: Number of partitions to create.
    :return: List of 'k' partitions of the graph with minimized edge cuts.

    """
    # Initial Partitioning
    nodes = list(G.nodes())
    partitions = [set(nodes[i::k]) for i in range(k)]

    def compute_cost():
        cost = 0
        for edge in G.edges():
            for i in range(k):
                for j in range(i + 1, k):
                    if (edge[0] in partitions[i] and edge[1] in partitions[j]) or (edge[1] in partitions[i] and edge[0] in partitions[j]):
                        cost += 1
        return cost

    def swap_cost(node_i, node_j, partition_i, partition_j):
        cost = 0
        for neighbor in G[node_i]:
            if neighbor in partitions[partition_j]:
                cost -= 1
            elif neighbor in partitions[partition_i]:
                cost += 1
        for neighbor in G[node_j]:
            if neighbor in partitions[partition_i]:
                cost -= 1
            elif neighbor in partitions[partition_j]:
                cost += 1
        return cost

    initial_cost = compute_cost()
    improved = True

    while improved:
        improved = False
        best_cost_decrease = 0
        best_pair = (None, None, None, None)

        for i in range(k):
            for j in range(i + 1, k):
                for node_i in partitions[i]:
                    for node_j in partitions[j]:
                        cost_decrease = swap_cost(node_i, node_j, i, j)
                        if cost_decrease > best_cost_decrease:
                            best_cost_decrease = cost_decrease
                            best_pair = (node_i, node_j, i, j)

        if best_pair[0] is not None and best_pair[1] is not None:
            # Swap the nodes
            node_i, node_j, partition_i, partition_j = best_pair
            partitions[partition_i].remove(node_i)
            partitions[partition_j].remove(node_j)
            partitions[partition_i].add(node_j)
            partitions[partition_j].add(node_i)

            # Recompute the cost
            new_cost = compute_cost()
            if new_cost < initial_cost:
                improved = True
                initial_cost = new_cost
            else:
                # Swap back if no improvement
                partitions[partition_i].remove(node_j)
                partitions[partition_j].remove(node_i)
                partitions[partition_i].add(node_i)
                partitions[partition_j].add(node_j)


    return partitions

import random

def monte_carlo_gpp(G, k, iterations=1000):
    # G is the graph represented as an adjacency list or matrix
    # k is the number of partitions
    # iterations is the number of Monte Carlo trials

    best_partition = None
    min_edge_cut = float('inf')

    for _ in range(iterations):
        # Generate a random partition of the nodes
        partition = [random.randint(0, k-1) for _ in G.nodes()]

        # Calculate the edge cut of this partition
        edge_cut = calculate_edge_cut(G, partition)

        # Update the best partition if a lower edge cut is found
        if edge_cut < min_edge_cut:
            min_edge_cut = edge_cut
            best_partition = partition

    return best_partition, min_edge_cut

def calculate_edge_cut(G, partition):
    edge_cut = 0
    for edge in G.edges():
        if partition[edge[0]] != partition[edge[1]]:
            edge_cut += 1
    return edge_cut

# Example usage
# G = {your_graph_structure}
# k = {number_of_partitions}
# best_partition, min_edge_cut = monte_carlo_gpp(G, k)

import numpy as np
import networkx as nx

def calculate_edge_cuts(G, partitions):
    """Calculates the number of edge cuts in a graph partitioning.

    Args:
      G: A networkx graph.
      partitions: A dictionary mapping nodes to partitions.

    Returns:
      The number of edge cuts.
    """
    edge_cuts = 0
    for u, v in G.edges():
        if partitions[u] != partitions[v]:
            edge_cuts += 1
    return edge_cuts

def adaptive_method(G, k, max_iter=1000):
    """Performs an adaptive method for graph partitioning.

    Args:
      G: A networkx graph.
      k: Number of partitions.
      max_iter: Maximum number of iterations.

    Returns:
      A dictionary representing the partitioning of the nodes.
    """
    V = list(G.nodes())
    partitions = {node: np.random.choice(k) for node in V}
    iter = 0

    while iter < max_iter:
        improved = False
        iter += 1
        current_edge_cuts = calculate_edge_cuts(G, partitions)

        for u in V:
            original_partition = partitions[u]
            best_partition = original_partition
            min_edge_cuts = current_edge_cuts

            for partition in range(k):
                if partition != original_partition:
                    partitions[u] = partition
                    edge_cuts = calculate_edge_cuts(G, partitions)
                    if edge_cuts < min_edge_cuts:
                        min_edge_cuts = edge_cuts
                        best_partition = partition
                        improved = True

            partitions[u] = best_partition

        if not improved:
            break

    return partitions

import networkx as nx
import time
import matplotlib.pyplot as plt


def create_graph(size):
    return nx.gnp_random_graph(size, 0.5)

# Sizes for testing (from 100 to 500, incrementing by 100)
graph_sizes = list(range(100, 1001, 100))

# Lists to store times
kl_times = []
mc_times = []
k_way_times = []

# Number of partitions (k)
k = 4

# Testing each size
for size in graph_sizes:
    G = create_graph(size)



    # Test Kernighan-Lin algorithm
    start_time = time.time()
    kernighan_lin_algorithm(G, k)
    kl_times.append(time.time() - start_time)

    # Test Monte Carlo algorithm
    start_time = time.time()
    monte_carlo_gpp(G, k)
    mc_times.append(time.time() - start_time)

    # Test adaptive_method algorithm
    start_time = time.time()
    adaptive_method(G, k)
    k_way_times.append(time.time() - start_time)


    # Optional: Print progress
    print(f"Completed size: {size}")

# Plotting the results
plt.figure(figsize=(10, 6))

# Apply different colors, dashed lines
plt.plot(graph_sizes, kl_times, label='Kernighan-Lin', color='crimson', linestyle='--', marker='s')
plt.plot(graph_sizes, mc_times, label='Monte Carlo', color='forestgreen', linestyle='--', marker='^')
plt.plot(graph_sizes, k_way_times, label='adaptive_method', color='royalblue', linestyle='--', marker='d')


# Customizing the grid and background
plt.grid(True, linestyle='--', alpha=0.7) # Dashed grid lines
plt.gca().set_facecolor('whitesmoke') # Light grey background

plt.xlabel('Graph Size (Number of Nodes)')
plt.ylabel('Time Taken (seconds)')
plt.title('Graph Partitioning Algorithms Performance Comparison')
plt.legend()
plt.show()