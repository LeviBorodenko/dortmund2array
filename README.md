## dortmund2array

Tool to convert datasets from [_Benchmark Data Sets for Graph Kernels (K. Kersting et al., 2016)_](http://graphkernels.cs.tu-dortmund.de) into a format suitable for deep learning research in graph classification.

<hr>

#### Installation

Simply run `pip install dortmund2array` to install the command-line interface. The only dependencies are `numpy networkx pandas`.

#### Output

Given any benchmark dataset, this tool will create a file `DATASET.pickle` that contains a pickled list. At index `i` the list has a dictionary with the adjacency matrix, the graph signal (also known as graph feature matrix) and the corresponding label for the `i`th graph.

```python
{
    "adjacency":    ...  # as numpy array. Shape: (nodes, nodes)
    "graph_signal": ...  # as numpy array. Shape: (nodes, features)
    "label":        ...  # usually a scalar.
}
```

The graph signal is an array of shape `(nodes, features)` where the features are either attributes given by the dataset or if no attributes are available, we simply take the node labels as attributes.

#### How to use

Simply get the `dortmund2array` command line tool via `pip install dortmund2array`.

```
usage: dortmund2array [-h] [--version] [--output OUTPUT_FOLDER]
                      [--input INPUT_FOLDER]

Tool to convert datasets from 'Benchmark Data Sets for Graph Kernels' (K.
Kersting et al., 2016)

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --output OUTPUT_FOLDER, -o OUTPUT_FOLDER
                        Output folder.
  --input INPUT_FOLDER, -i INPUT_FOLDER
                        Input folder containing the dataset of the same name.
  -e                    Output edge list instead of adjacency for each
                        graph.
```

Thus, download and unzip a dataset. Make sure the folder-name agrees with the dataset-name on the files inside of it. If you for instance download `MUTAG` and the corresponding folder is `.\MUTAG\` and you want the array data saved in `.\MUTAG_array\` then you need to simply run:

```
dortmund2array -i ./MUTAG/ -o ./MUTAG_array/
```

#### Requirements
Make sure you meet all the dependencies inside the `requirements.txt`.
