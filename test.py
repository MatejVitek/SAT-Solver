import networkx as nx

import SAT_solver
import hamilton2SAT


# G = nx.petersen_graph()
# G = nx.complete_graph(15)
G = nx.caveman_graph(2, 3)

# ham2sat writes a Dimacs file with the name given as the (optional) second argument.
# It also returns the formula already in the appropriate CNF for the SAT Solver.
print("Writing Dimacs file for " + str(G) + "...")
cnf = hamilton2SAT.ham2sat(G, "hamilton.txt")

# The SAT Solver accepts the formula given in appropriate CNF (such as the one returned above).
# It can also read it from a file in Dimacs format, the name of which is to be given as the first argument.
# The second argument is the (optional) name of the output (solution) file.
print("Finding a satisfying valuation...")
SAT_solver.sat(cnf, "hamilton_solution.txt")
# SAT_solver.sat("hamilton.txt", "hamilton_solution.txt")

# interpret_solution reads the solution of the SAT problem and deciphers the Hamiltonian cycle from it.
print("Interpreting solution...")
hamilton2SAT.interpret_solution("hamilton_solution.txt")