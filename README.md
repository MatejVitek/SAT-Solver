## Description

The SAT solver reads a dimacs file and outputs the solution (in pseudo-dimacs form) to the CNF-SAT formula the file defines.

## Files

The SAT Solver is implemented in Python in the file SAT_solver.py. Included alongside it are the sudoku test files from the lectures and 4 translations of the Hamiltonian cycle problem (in undirected graphs) to SAT in dimacs form, as well as their respective solutions.

All the problems were successfully solved by this SAT solver in under a minute (though the more difficult ones came close). Note however, that since there can be more than one Hamiltonian cycle in a graph, the solution may differ from those found by other implementations. Indeed, as this particular SAT solver is randomized, the solutions may even differ between consecutive runs of this program.

The sudokus have unique solutions, so the solution found by this SAT solver should be equivalent to that found by any other (up to the permutation of variables in the valuation).

## Execution

To run the SAT solver, simply download all files to one folder and run python SAT_solver.py from the command line. Then, when prompted, input the name of the problem dimacs file and press Enter. When prompted for a solution file name, input a name if desired, or leave empty to not write a solution file.

To terminate the program, simply leave the input file name empty and press Enter.
