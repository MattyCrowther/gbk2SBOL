import os
from Bio import SeqIO
from rdflib import Graph, DCTERMS, Literal, URIRef
from sbol_generator import SBOLGenerator
from pysbolgraph.SBOL2Serialize import serialize_sboll2
from pysbolgraph.SBOL2Graph import SBOL2Graph

from identifiers import identifiers
from validate_sbol import validate_sbol
blacklist_features = ["source", "exon"]

dna_o = identifiers.roles.DNA
generator = SBOLGenerator()
gbk_map = {
    "DNA": identifiers.roles.DNA,
    "PROMOTER": identifiers.roles.promoter,
    "RBS": identifiers.roles.rbs,
    "CDS": identifiers.roles.cds,
    "TERMINATOR": identifiers.roles.terminator,
    "GENE": identifiers.roles.gene
}
existing_entities = []

def convert(gbk, prefix, out):
    graph = Graph()
    for record in SeqIO.parse(gbk, "genbank"):
        name = record.name
        seq = record.seq
        if record.name is None and record.name == "":
            name = record.id
        subject = _build_uri(prefix,name)
        sources = [f for f in record.features if f.type == "source"]
        props = ""
        components = []
        sas = []

        for source in sources:
            for k, v in source.qualifiers.items():
                if isinstance(v, list):
                    props += " - " .join(v)
                else:
                    props += f' - {v}'
        if len(props) > 0:
            props = {DCTERMS.description: Literal(props)}
        else:
            props = {}

        for f in record.features:
            if f.type in blacklist_features:
                continue
            location = f.location
            complement = identifiers.roles.inline if location.strand == 1 else identifiers.roles.reverse
            quals = f.qualifiers
            if "label" in quals:
                cd_subject = _build_uri(prefix,quals["label"][0],default=f.type)
                c_subject = _build_uri(prefix,quals["label"][0],suffix="_c",default=f.type)
                s_subject = _build_uri(prefix,quals["label"][0],suffix="_annotation",default=f.type)
            elif "note" in quals:
                cd_subject = _build_uri(prefix,quals["note"][0],default=f.type)
                c_subject = _build_uri(prefix,quals["note"][0],suffix="_c",default=f.type)
                s_subject = _build_uri(prefix,quals["note"][0],suffix="_annotation",default=f.type)
            elif "gene" in quals:
                cd_subject = _build_uri(prefix,quals["gene"][0],default=f.type)
                c_subject = _build_uri(prefix,quals["gene"][0],suffix="_c",default=f.type)
                s_subject = _build_uri(prefix,quals["gene"][0],suffix="_annotation",default=f.type)
            elif "primer" in quals:
                primer = quals["primer"][0].split()[0]
                cd_subject = _build_uri(prefix,primer,default=f.type)
                c_subject = _build_uri(prefix,primer,suffix="_c",default=f.type)
                s_subject = _build_uri(prefix,primer,suffix="_annotation",default=f.type)
            else:
                raise ValueError("Cant find")

            c_subject = generator.build_children_uri(subject, c_subject)
            s_subject = generator.build_children_uri(subject, s_subject)
            role = _get_role(f)
            start = Literal(location.start)
            end = Literal(location.end)

            _add_cd(graph, cd_subject, dna_o, role)
            _add_component(graph, c_subject, cd_subject)
            _add_sa(graph, s_subject, start, end, complement, c_subject)

            components.append(c_subject)
            sas.append(s_subject)

        _add_sequence(graph, subject, seq)
        _add_cd(graph, subject, dna_o,
                components=components, sas=sas, props=props)

    sbol = _serialise(graph)
    out_fn = os.path.join(out, gbk.split(os.path.sep)[-1].split(".")[0]+".xml")
    with open(out_fn, 'w') as o:
        o.write(sbol)
    existing_entities.clear()
    return out_fn


def _get_role(feature):
    descs = [feature.type]
    for q in feature.qualifiers.values():
        if isinstance(q, list):
            for e in q:
                descs += e.split()
        else:
            descs += q.split()
    for d in descs:
        d = d.upper()
        if d in gbk_map:
            return gbk_map[d]


def _build_uri(prefix,name,suffix=None,default=None):
    name = _get_name(name)
    if name.isdigit() and default is not None:
        name = default
    uri = f'{prefix}{name}{suffix if suffix is not None else ""}/1'
    if uri not in existing_entities:
        return URIRef(uri)
    orig_uri = uri
    count = 0
    while uri not in existing_entities:
        uri = f'{orig_uri[0:-2]}{str(count)}/1'
        count +=1
    return URIRef(uri) 

def _add_sequence(graph, cd, elements):
    subject = URIRef(cd[0:-2] + "_sequence/1")
    elements = Literal(elements)
    for triple in generator.sequence(subject, elements, identifiers.objects.naseq):
        graph.add(triple)
    graph.add((cd, identifiers.predicates.sequence, subject))
    return graph


def _add_cd(graph, subject, c_type, c_role=None, components=[], sas=[], props={}):
    subject = URIRef(subject)
    for triple in generator.component_definition(subject, c_type, c_role, components, sas, props):
        graph.add(triple)
    return graph


def _add_component(graph, subject, definition):
    subject = URIRef(subject)
    definition = URIRef(definition)
    for triple in generator.component(subject, definition):
        graph.add(triple)
    return graph


def _add_sa(graph, subject, start, end, strand, c_subject):
    subject = URIRef(subject)
    c_subject = URIRef(c_subject)
    for triple in generator.sequence_annotation(subject, start, end, strand, c_subject):
        graph.add(triple)
    return graph


def _get_name(name):
    blacklist_chars = ["(",")",".","+"]
    for c in blacklist_chars:
        name = name.replace(c,"")
    return name.replace(" ", "_").replace("-", "_")


def _serialise(graph):
    pysbolG = SBOL2Graph()
    pysbolG += graph
    return serialize_sboll2(pysbolG).decode("utf-8")


if __name__ == "__main__":
    prefix = "http://sevahub.es/public/Canonical/"
    results = {}
    try:
        os.mkdir("sbol")
    except FileExistsError:
        pass
    for file in os.listdir("gbk"):
        i = os.path.join("gbk", file)
        rv = convert(i, prefix, "sbol")
        res = validate_sbol(rv)
        if res["valid"] == False:
            results[file] = res["errors"]

    print("Invalid Designs:")
    for k, v in results.items():
        print(k,v)
        print("\n")
