from abc import ABC, abstractmethod
import copy
import collections
import random
import queue


class Operator:
    def __init__(self, str_reps, f):
        self.str_reps = str_reps
        self.f = f

    def __str__(self):
        return self.str_reps[0]


T = Operator(["⊤", "T"], lambda: T)
F = Operator(["⊥", "F"], lambda: F)
vals = T, F

NOT = Operator(["¬", "~", "not", "!"], lambda x: T if x is F else F)
AND = Operator(["∧", "&", "and"], lambda args: T if all(a is T for a in args) else F)
OR = Operator(["∨", "|", "or"], lambda args: T if any(a is T for a in args) else F)
IMPL = Operator(["⇒", "->"], lambda x, y: T if x is F or y is T else F)
ops = NOT, AND, OR, IMPL


class Node(ABC):
    @abstractmethod
    def __eq__(self, other):
        pass

    def __ne__(self, other):
        return not self == other

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def bracket_if_necessary(self):
        pass

    @abstractmethod
    def evaluate(self, varvals):
        pass

    @abstractmethod
    def negate(self):
        pass


class Leaf(Node):
    def __init__(self, v):
        self.val = v

    def __eq__(self, other):
        if not isinstance(other, Leaf):
            return False
        return self.val == other.val

    def __str__(self):
        return str(self.val)

    def bracket_if_necessary(self):
        return str(self)

    def evaluate(self, varvals):
        return self.val if isinstance(self.val, Operator) else varvals[self.val]

    def negate(self):
        return UnaryNode(NOT, self)


class UnaryNode(Node):
    def __init__(self, op, child):
        self.op = op
        self.child = child

    def __eq__(self, other):
        if not isinstance(other, UnaryNode):
            return False
        return self.op is other.op and self.child == other.child

    def __str__(self):
        return str(self.op) + self.child.bracket_if_necessary()

    def bracket_if_necessary(self):
        return str(self)

    def evaluate(self, varvals):
        return self.op.f(self.child.evaluate(varvals))

    def negate(self):
        return self.child


class BinaryNode(Node):
    def __init__(self, op, lchild, rchild):
        self.op = op
        self.lchild = lchild
        self.rchild = rchild

    def __eq__(self, other):
        if not isinstance(other, BinaryNode):
            return False
        return self.op is other.op and self.lchild == other.lchild and self.rchild == other.rchild

    def __str__(self):
        return self.lchild.bracket_if_necessary() + " " + str(self.op) + " " + self.rchild.bracket_if_necessary()

    def bracket_if_necessary(self):
        return "(" + str(self) + ")"

    def evaluate(self, varvals):
        return self.op.f(self.lchild.evaluate(varvals), self.rchild.evaluate(varvals))

    def negate(self):
        if self.op is IMPL:
            return VariadicNode(AND, [self.lchild, self.rchild.negate()])
        return None


class VariadicNode(Node):
    def __init__(self, op, children):
        self.op = op
        self.children = children

    def __eq__(self, other):
        if not isinstance(other, VariadicNode):
            return False
        return (self.op is other.op and len(self.children) == len(other.children) and
                all(self.children.count(child) == other.children.count(child) for child in self))

    def __str__(self):
        return (" " + str(self.op) + " ").join(child.bracket_if_necessary() for child in self)

    def __iter__(self):
        return iter(self.children)

    def bracket_if_necessary(self):
        return "(" + str(self) + ")"

    def evaluate(self, varvals):
        return self.op.f(child.evaluate(varvals) for child in self)

    def negate(self):
        return VariadicNode(AND if self.op is OR else OR, [c.negate() for c in self])


#
# Functionality implementation
#


def main():
    print("Enter q to exit program.")
    while True:
        input_str = input("Input file name: ")
        if input_str.lower() in ('q', 'quit', 'exit'):
            break
        if "." not in input_str:
            input_str += ".txt"
        cnf = _read_cnf(input_str)
        val = sat(cnf)
        print(" ".join(_to_dimacs(x) for x in val) if val else "UNSATISFIABLE")


# Reads the input file in dimacs format and returns the expression tree of the formula in CNF
def _read_cnf(fname):
    children = []
    for line in open(fname, 'r'):
        if line[0] in ('c', 'p'):
            continue
        children.append(VariadicNode(OR, [_get_literal_node(l) for l in line.split() if int(l)]))
    return VariadicNode(AND, children)


# Returns the leaf xn for n in input, and not(xn) for -n in input
def _get_literal_node(l):
    i = int(l)
    return Leaf(l) if i > 0 else Leaf(str(-i)).negate()


# DPLL algorithm, as described in lectures
def sat(formula):
    states = [(formula, ())]
    while states:
        cnf, val = states.pop(_weighted_choice(states))
        while True:
            l = _find_unit_literal(cnf)
            if not l:
                break
            _simplify(cnf, l)
            val += l,
        if not cnf.children:
            return val
        if VariadicNode(OR, []) in cnf:
            return None

        p = _get_atom(cnf)
        cnf_copy = copy.deepcopy(cnf)

        cnf.children.append(VariadicNode(OR, [p]))
        cnf_copy.children.append(VariadicNode(OR, [p.negate()]))
        states.append((cnf, val))
        states.append((cnf_copy, val))


# Returns an index chosen randomly, weighted with the inverse of the number of clauses in formulas
def _weighted_choice(states):
    weights = [1.0 / len(formula.children) for formula, _ in states]
    rnd = random.uniform(0, sum(weights))
    for i in range(len(weights)):
        rnd -= weights[i]
        if rnd <= 0:
            return i


# Finds and returns a unit literal
def _find_unit_literal(cnf):
    for c in cnf:
        if len(c.children) == 1:
            return c.children[0]
    return None


# Simplify procedure as described in lectures
def _simplify(cnf, l):
    cnf.children = [_filter(c, l.negate()) for c in cnf if l not in c]


# Removes the chosen unit literal (negated above) from clause c
def _filter(c, l):
    return VariadicNode(c.op, [x for x in c if x != l])


# Returns the most common atom from the formula
def _get_atom(cnf):
    counter = collections.Counter(_get_var(l) for c in cnf for l in c)
    return Leaf(counter.most_common(1)[0])


def _get_var(node):
    return str(node.child) if isinstance(node, UnaryNode) else str(node)


def _to_dimacs(node):
    s = _get_var(node)
    return "-" + s if isinstance(node, UnaryNode) else s


if __name__ == '__main__':
    main()
