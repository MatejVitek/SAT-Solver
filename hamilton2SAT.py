import math

from operators import *


# Reduces the Hamiltonian cycle problem on given graph to a SAT formula in CNF
# If fname is given, additionally writes the result in Dimacs form into new file with name fname.
def ham2sat(graph, fname=None):
    n = len(graph.nodes())

    # Returns a literal node with the appropriate atom representation for x_iv (i * n + v)
    # If parameter t is False, it returns the negated atom.
    def x(i, v, t=True):
        l = Leaf(str(i * n + v + 1))
        return l if t else ~l

    # for each v: v appears in cycle: clause = (x_0v | ... | x_nv)
    clauses = [
        VariadicNode(OR, tuple(x(i, v) for i in range(n + 1)))
        for v in range(n)
    ]

    # for each v: v in position 0 <-> v in position n: clauses = (x_0v | ~x_nv) and (~x_0v | x_nv)
    clauses.extend(
        VariadicNode(OR, (x(0, v), x(n, v, False)))
        for v in range(n)
    )
    clauses.extend(
        VariadicNode(OR, (x(0, v, False), x(n, v)))
        for v in range(n)
    )

    # for each v: v does not repeat on cycle (except in the above case):
    # clause = (~x_iv | ~x_jv) for 0 <= i < j <= n, except for i = 0, j = n
    clauses.extend(
        VariadicNode(OR, (x(i, v, False), x(j, v, False)))
        for v in range(n) for i in range(n) for j in range(i+1, n+1)
        if not (i == 0 and j == n)
    )

    # for each i: position must be filled: clause = (x_i1 | ... | x_in)
    clauses.extend(
        VariadicNode(OR, tuple(x(i, v) for v in range(n)))
        for i in range(n+1)
    )

    # for each i: position cannot have more than one vertex: clause = (~x_iv | ~x_iu) for 1 <= v < u <= n
    clauses.extend(
        VariadicNode(OR, (x(i, v, False), x(i, u, False)))
        for i in range(n+1) for v in range(n-1) for u in range(v+1, n)
    )

    # for each i (except i = n): only neighbours (in graph G) of vertex at i can follow it in the cycle
    # clause = (~x_iv | ~x_i+1u) for 1 <= v < u <= n, where v and u are not connected in G
    clauses.extend(
        VariadicNode(OR, (x(i, v, False), x(i + 1, u, False)))
        for i in range(n) for v in range(n-1) for u in range(v+1, n)
        if u not in graph[v]
    )

    if fname:
        with open(fname, 'w') as f:
            print("c Reduction of Hamiltonian cycle problem on " + str(graph) + " to SAT in CNF form.", file=f)
            print("c The vertices are denoted as numbers v (1 <= v <= " + str(n) + ").", file=f)
            print("c Atom x_iv (0 <= i <= " + str(n) + ") implies vertex v is in i-th position on the cycle.", file=f)
            print("c Atom x_iv is represented as " + str(n) + " * i + v.", file=f)
            print("p cnf " + str(n * (n + 1)) + " " + str(len(clauses)), file=f)
            for c in clauses:
                print(" ".join(_to_dimacs(l) for l in c) + " 0", file=f)

    return VariadicNode(AND, tuple(clauses))


def _to_dimacs(node):
    return "-" + str(node.child) if isinstance(node, UnaryNode) else str(node)


def interpret_solution(fname):
    with open(fname, 'r') as f:
        solution = f.readline().split()

    if solution[0] == "UNSATISFIABLE":
        print(solution[0])
        return

    # to get n from the file, note that max variable = n * (n + 1) -> use quadratic formula to get n
    max_var = max(abs(int(x)) for x in solution)
    n = int(-1 + math.sqrt(1 + 4 * max_var)) // 2

    solution = [int(x) for x in solution if int(x) > 0]
    solution.sort()
    print(" - ".join(str(x % n) for x in solution))