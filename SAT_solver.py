import copy
import collections
import random

from operators import *


#
# Functionality implementation
#


def main():
    while True:
        in_name = input("Input Dimacs problem file name (leave empty to exit program): ")
        if not in_name:
            break
        if '.' not in in_name:
            in_name += '.txt'
        out_name = input("Input file name for solution file (if left empty, will not write one): ")
        if out_name and '.' not in out_name:
            out_name += '.txt'
        val = sat(in_name, out_name)
        print(", ".join(str(x) for x in val) if val else "UNSATISFIABLE")


# DPLL algorithm, as described in lectures
# Implemented iteratively for easier non-chronological backtracking
# Assumes formula is either already the CNF form or is the name of the file containing the Dimacs representation of it
def sat(formula, solution_fname=None):
    if isinstance(formula, str):
        formula = _read_cnf(formula)
    openset = [(formula, ())]
    closedset = set([None])
    while openset:
        cnf = None
        while openset and cnf in closedset:
            cnf, val = openset.pop(_weighted_choice(openset))
        closedset.add(cnf)
        while cnf and all(c for c in cnf):
            l = _find_unit_literal(cnf)
            if not l:
                break
            cnf = _simplify(cnf, l)
            val += l,

        if not cnf:
            if solution_fname:
                with open(solution_fname, 'w') as f:
                    print(" ".join(_to_dimacs(x) for x in val), file=f)
            return val

        if all(c for c in cnf):
            p = _get_atom(cnf)
            cnf_copy = copy.deepcopy(cnf)

            cnf += VariadicNode(OR, [p])
            cnf_copy += VariadicNode(OR, [~p])

            openset.append((cnf, val))
            openset.append((cnf_copy, val))

    if solution_fname:
        with open(solution_fname, 'w') as f:
            print("UNSATISFIABLE", file=f)


# Reads the input file in dimacs format and returns the expression tree of the formula in CNF
def _read_cnf(fname):
    clauses = []
    with open(fname, 'r') as f:
        for line in f:
            if line[0] not in ('c', 'p'):
                clauses.append(VariadicNode(OR, tuple(_get_literal_node(l) for l in line.split() if int(l))))
    return VariadicNode(AND, tuple(clauses))


# Returns the leaf xn for n in input, and not(xn) for -n in input
def _get_literal_node(l):
    i = int(l)
    return Leaf(l) if i > 0 else ~Leaf(str(-i))


# Returns an index chosen randomly, weighted with the inverse of the squared number of clauses in formulas
# This way formulas with fewer clauses are more likely to be chosen (as they are more promising)
# Occasionally however, other branches will still be explored (exploration/exploitation trade-off)
def _weighted_choice(l):
    weights = [1.0 / len(formula) ** 2 for formula, _ in l]
    rnd = random.uniform(0, sum(weights))
    for i in range(len(weights)):
        rnd -= weights[i]
        if rnd <= 0:
            return i


# Finds and returns a unit literal
def _find_unit_literal(cnf):
    for c in cnf:
        if len(c) == 1:
            return c[0]
    return None


# Simplify procedure as described in lectures
def _simplify(cnf, l):
    for c in cnf:
        print("b", l, ~l, type(l), "B", c, type(c), l in c)
    return VariadicNode(AND, tuple(_filter(c, ~l) for c in cnf if l not in c))


# Removes the chosen unit literal (negated above) from clause c
def _filter(c, l):
    for x in c:
        print("a", l, type(l), "A", x, type(x), x==l)
    return VariadicNode(c.op, tuple(x for x in c if x != l))


# Returns the best atom from the formula by below heuristic
# h(a) = sum(1/clause_length) over all clauses a appears in
# Atoms that appear in many clauses will be rated highly
# Atoms that appear in short clauses will be rated highly
def _get_atom(cnf):
    h = collections.defaultdict(float)
    for c in cnf:
        for l in c:
            h[_get_var(l)] += 1.0 / len(c)
    return Leaf(sorted(h.items(), key=lambda x: x[1], reverse=True)[0][0])


def _get_var(node):
    return str(node.child) if isinstance(node, UnaryNode) else str(node)


def _to_dimacs(node):
    return "-" + str(node.child) if isinstance(node, UnaryNode) else str(node)


if __name__ == '__main__':
    main()
