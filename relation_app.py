import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

def parse_elements(elements_str):
    return sorted(set(e.strip() for e in elements_str.split(',') if e.strip()))

def parse_relation(relation_str, elements):
    relation = []
    for line in relation_str.strip().split('\n'):
        if not line.strip():
            continue
        if ',' not in line:
            st.warning(f"Invalid pair: {line}. Pairs must be comma-separated.")
            continue
        a, b = (x.strip() for x in line.split(',', 1))
        if a in elements and b in elements:
            relation.append((a, b))
        else:
            st.warning(f"Pair ({a},{b}) uses elements not in the set: {elements}")
    return relation

def is_reflexive(relation, elements):
    missing = [e for e in elements if (e, e) not in relation]
    if not missing:
        st.success("Relation is reflexive: All (a, a) pairs are present.")
        return True
    else:
        st.error(f"Relation is NOT reflexive. Missing: {missing}")
        return False

def is_symmetric(relation):
    missing = [(b, a) for (a, b) in relation if (b, a) not in relation]
    if not missing:
        st.success("Relation is symmetric: Each (a, b) has (b, a).")
        return True
    else:
        st.error(f"Relation is NOT symmetric. Missing reverse pairs: {missing}")
        return False

def is_transitive(relation):
    missing = []
    for (a, b) in relation:
        for (c, d) in relation:
            if b == c and (a, d) not in relation:
                missing.append((a, d))
    if not missing:
        st.success("Relation is transitive: For all (a, b) and (b, c), (a, c) is present.")
        return True
    else:
        st.error(f"Relation is NOT transitive. Missing (a, c) pairs: {set(missing)}")
        return False

def is_antisymmetric(relation):
    violating = [(a, b) for (a, b) in relation if (b, a) in relation and a != b]
    if not violating:
        st.success("Relation is antisymmetric: No (a, b) and (b, a) for a ≠ b.")
        return True
    else:
        st.error(f"Relation is NOT antisymmetric. Violating pairs: {violating}")
        return False

def is_partial_order(relation, elements):
    st.write("Checking if relation is a partial order...")
    r = is_reflexive(relation, elements)
    t = is_transitive(relation)
    a = is_antisymmetric(relation)
    if r and t and a:
        st.success("The relation is a partial order.")
        return True
    else:
        st.error("The relation is NOT a partial order.")
        return False

def is_linear_order(relation, elements):
    st.write("Checking if relation is a linear order...")
    if not is_partial_order(relation, elements):
        st.error("Not a linear order because the relation is not a partial order.")
        return False
    total = all((a, b) in relation or (b, a) in relation for a in elements for b in elements if a != b)
    if total:
        st.success("The relation is a linear order: every pair is comparable.")
        return True
    else:
        st.error("The relation is NOT a linear order: some pairs are not comparable.")
        return False

def find_max_min(relation, elements):
    st.write("Finding maximum and minimum elements...")
    greater_than = {x: set() for x in elements}
    for a, b in relation:
        if a != b:
            greater_than[a].add(b)
    minimal = [x for x in elements if all(x not in greater_than[y] for y in elements if y != x)]
    maximal = [x for x in elements if not greater_than[x]]
    st.info(f"Minimal elements: {minimal}")
    st.info(f"Maximal elements: {maximal}")
    return minimal, maximal

def draw_hasse(relation, elements):
    st.write("Drawing Hasse Diagram...")
    if not is_partial_order(relation, elements):
        st.error("Cannot draw Hasse Diagram: the relation is not a partial order.")
        return
    hasse_relation = [pair for pair in relation if pair[0] != pair[1]]
    transitive_closure = set((a, c) for (a, b) in hasse_relation for (x, c) in hasse_relation if x == b and a != c)
    hasse_relation = [edge for edge in hasse_relation if edge not in transitive_closure]
    G = nx.DiGraph()
    G.add_nodes_from(elements)
    G.add_edges_from(hasse_relation)
    greater_than = {x: set() for x in elements}
    for a, b in relation:
        if a != b:
            greater_than[a].add(b)
    minimal = [x for x in elements if all(x not in greater_than[y] for y in elements if y != x)]
    maximal = [x for x in elements if not greater_than[x]]
    color_map = []
    for node in G.nodes():
        if node in maximal:
            color_map.append('red')
        elif node in minimal:
            color_map.append('blue')
        else:
            color_map.append('green')
    pos = nx.spring_layout(G)
    fig, ax = plt.subplots()
    nx.draw(G, pos, with_labels=True, node_color=color_map, edge_color='black', arrows=True, ax=ax)
    for node in minimal:
        x, y = pos[node]
        ax.text(x, y + 0.08, 'MIN', fontsize=9, color='blue', ha='center', fontweight='bold')
    for node in maximal:
        x, y = pos[node]
        ax.text(x, y - 0.08, 'MAX', fontsize=9, color='red', ha='center', fontweight='bold')
    ax.set_title("Hasse Diagram (Red=Max, Blue=Min, Green=Other)")
    st.pyplot(fig)


st.title("Relations and Partial Orders Explorer")

st.sidebar.header("Input: Set and Relation")
elements_str = st.sidebar.text_input("Enter set elements (comma-separated)", "a,b,c")
relation_str = st.sidebar.text_area("Enter ordered pairs, one per line (e.g., a,b)", "a,a\na,b\nb,b\nb,c\nc,c")
elements = parse_elements(elements_str)
relation = parse_relation(relation_str, elements)

if not elements:
    st.warning("Please enter set elements to continue.")
elif not relation:
    st.warning("Please enter at least one ordered pair to continue.")
else:
    st.markdown(f"**Set:** {elements}")
    st.markdown(f"**Relation:** {relation}")

    if st.button("Check Reflexive"):
        is_reflexive(relation, elements)
    if st.button("Check Symmetric"):
        is_symmetric(relation)
    if st.button("Check Transitive"):
        is_transitive(relation)
    if st.button("Check Antisymmetric"):
        is_antisymmetric(relation)
    if st.button("Check Partial Order"):
        is_partial_order(relation, elements)
    if st.button("Check Linear Order"):
        is_linear_order(relation, elements)
    if st.button("Find Maximum and Minimum Elements"):
        find_max_min(relation, elements)
    if st.button("Draw Hasse Diagram"):
        draw_hasse(relation, elements)

