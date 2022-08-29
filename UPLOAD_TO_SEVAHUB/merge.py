import os
from rdflib import Graph
def merge():
    g = Graph()
    g.load("Canonical_collection.xml")
    s_dir = "sbol"
    for fn in os.listdir(s_dir):
        g.load(os.path.join(s_dir,fn))

    g.serialize("out.xml","xml")

if __name__ == "__main__":
    merge()