# import networkx as nx
import pickle
from collections import Counter
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

__author__ = "Levi Borodenko"
__copyright__ = "Levi Borodenko"
__license__ = "mit"


class BenchmarkData(object):
    """docstring for BenchmarkData

    Arguments:
        raw_path (Path): Path to dataset
        clean_path (Path): Path where to store the transformed data.

    """

    def __init__(self, raw_path: Path, clean_path: Path):
        super(BenchmarkData, self).__init__()

        # save paths
        self.raw_path = Path(raw_path)
        self.clean_path = Path(clean_path)

        # Name of Folder that contains the data.
        # This is also the name of the dataset.
        name = self.raw_path.name
        self.name = name

        # make sure raw_path exists
        assert self.raw_path.exists()

        # if clean_path does not exists, create it
        if not self.clean_path.exists():
            self.clean_path.mkdir(parents=True)

        # creating all paths needed to work with the data
        self.edge_list_file = self.raw_path / (name + "_A.txt")
        self.graph_labels_file = self.raw_path / (name + "_graph_labels.txt")
        self.graph_indicator_file = self.raw_path / (name + "_graph_indicator.txt")

        # node labels are always present but node attributes
        # are not. We follow the convention that if no attributes
        # are given, then we use node labels as the node features.
        self.node_labels_file = self.raw_path / (name + "_node_labels.txt")
        self.node_attributes_file = self.raw_path / (name + "_node_attributes.txt")

        if self.node_attributes_file.exists():
            self.node_features_file = self.node_attributes_file
        else:
            self.node_features_file = self.node_labels_file

        # These two attributes are for bookkeeping.
        # We construct the graphs by going through
        # the nodes in increasing order
        # smallest_node is the smallest node of the
        # graph that we are currently constructing.

        # graph_id is the id of the graph that we are
        # currently constructing.
        self.smallest_node = 0
        self.graph_id = 1

    def _parse_indicators(self):
        """Parses the graph indicator file.

        It we calculate the number of graphs
        and create a collections.Counter instance
        that counts the number of nodes in a graph
        with given id.

        """

        indicators = pd.read_csv(self.graph_indicator_file, header=None)

        # saving first (and only) column.
        # This contains all the indicators.
        indicators = indicators[0]

        self.number_of_graphs = max(indicators)

        # relevant counter instance.
        self.node_counter = Counter(indicators)

    def _parse_labels(self):
        """Parses the labels from the graph label file
        into an array of labels.
        """

        # loading labels from file
        labels = pd.read_csv(self.graph_labels_file, header=None)

        # saving first and only column as array
        self.labels = np.asarray(labels[0])

    def edge_yielder(self) -> iter:
        """Generator that yields edges from
        the edge file
        """
        with open(self.edge_list_file, "r") as f:
            for line in f:

                # line looks like:
                # "1, 3 \n"
                # so we strip all white spaces
                line = line.strip()

                # and split at the ","
                line = line.split(",")

                # convert to int
                u, v = [int(i) for i in line]

                yield (u, v)

    def _parse_features(self):
        """parses the node attributes / labels and saves them at
        self.features
        """

        # read from file
        features = pd.read_csv(self.node_features_file, header=None)

        # save as numpy array of shape (#nodes, #features)
        self.features = np.asarray(features)

    def preporcess(self):
        """Creates all necessary data to construct the tensors
        """
        self._parse_indicators()

        self._parse_labels()

        self._parse_features()

    def get_next_graph(self) -> dict:
        """Constructs the adjacency matrix, a graph signal
        and the label for one graph. Retuns them as a dict.

        When run again, it will return the same information for
        a different graph.

        Raises:
            - "IndexError" if no more graphs left.

        Returns:
            - Dict of the form:
                - {"adjacency": adjacency_matrix,
                        "graph_signal": graph_features,
                        "label": graph_label}

        """

        # getting the label correspond to the considered graph_id
        graph_label = self.labels[self.graph_id - 1]

        # get number of nodes in this graph
        nodes_in_graph = self.node_counter[self.graph_id]

        # largest node inside the present graph
        largest_node = self.smallest_node + nodes_in_graph

        # get all features for nodes in this graph
        graph_features = self.features[self.smallest_node : largest_node, :]

        # initiate directional graph
        G = nx.DiGraph()

        # iterate over ALL edge (bad idea actually, but oh well)
        for edge in self.edge_yielder():
            u, v = edge

            # if edge is contained in this graph
            if self.smallest_node <= u <= largest_node:
                if self.smallest_node <= v <= largest_node:

                    # add edge to graph
                    G.add_edge(u, v)

            # If it isn't, then it means we reached the end of this
            # graph's edges.
            if u > largest_node or v > largest_node:

                # go to next graph
                self.graph_id += 1
                self.smallest_node = largest_node

                # get adjacency
                adjacency_matrix = nx.to_numpy_matrix(G)

                if adjacency_matrix.shape[-1] != graph_features.shape[-2]:

                    raise ValueError(f"Graph {self.graph_id - 1} is corrupted.")

                return {
                    "adjacency": adjacency_matrix,
                    "graph_signal": graph_features,
                    "label": graph_label,
                }
        else:

            # We reached end without breaking
            # thus we have considered every single edge and
            # found all graphs
            raise IndexError

    def get_data(self):
        """Creates the list of dicts each
        corresponding to a graph and returns it.

        Returns:
            List: list of outputs from self.get_next_graph
        """

        # will be populated with returns of self.get_next_graph()
        data = []

        for _ in range(self.number_of_graphs):
            try:
                data.append(self.get_next_graph())

            # graph for some reason corrupted.
            # Most-likely due to having isolated nodes.
            except ValueError:
                pass

            # Once we run out of data.
            except IndexError:
                return data

    def save_data(self):
        """Saves the output of self.get_data
        to a pickle as clean_path / NAME.pickle
        """

        data = self.get_data()

        with open(self.clean_path / (self.name + ".pickle"), "wb") as f:
            pickle.dump(data, f, -1)

    def run(self):
        """Creates a pickle with the transformed data
        """

        self.preporcess()

        self.save_data()


if __name__ == "__main__":
    data = BenchmarkData("./NCI1/", "./clean/")
    data.run()

    with open("./clean/NCI1.pickle", "rb") as f:
        data = pickle.load(f)

        for i in data:
            print(i)
            break
