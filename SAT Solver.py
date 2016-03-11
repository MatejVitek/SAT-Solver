from abc import ABC, abstractmethod


class Operator:
    def __init__(self, str_reps, f):
        self.str_reps = str_reps
        self.f = f

    def __str__(self):
        return self.str_reps[0]


T = Operator(["⊤", "T"], lambda: T)
F = Operator(["⊥", "F"], lambda: F)
vals = (T, F)

NOT = Operator(["¬", "~", "not", "!"], lambda x: T if x is F else F)
AND = Operator(["∧", "&", "and"], lambda args: T if all(a is T for a in args) else F)
OR = Operator(["∨", "|", "or"], lambda args: T if any(a is T for a in args) else F)
IMPL = Operator(["⇒", "->"], lambda x, y: T if x is F or y is T else F)
ops = (NOT, AND, OR, IMPL)


class Node(ABC):
    @abstractmethod
    def __eq__(self, other):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def bracket_if_necessary(self):
        pass

    @abstractmethod
    def evaluate(self, varvals):
        pass

class Leaf(Node):
    def __init__(self, v):
        self.var = v

    def __eq__(self, other):
        if not isinstance(other, Leaf):
            return False
        return self.var == other.var

    def __str__(self):
        return self.var

    def bracket_if_necessary(self):
        return str(self)

    def evaluate(self, varvals):
        return varvals[self.var]


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


class VariadicNode(Node):
    def __init__(self, op, children):
        self.op = op
        self.children = children

    def __eq__(self, other):
        if not isinstance(other, VariadicNode):
            return False
        return (self.op is other.op and
                all(child in other.children for child in self.children) and
                all(child in self.children for child in other.children))

    def __str__(self):
        return (" " + str(self.op) + " ").join(child.bracket_if_necessary() for child in self.children)

    def bracket_if_necessary(self):
        return "(" + str(self) + ")"

    def evaluate(self, varvals):
        return self.op.f(child.evaluate(varvals) for child in self.children)


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
        cnf = read_cnf(input_str)
        print(cnf)
        print("SATISFIABLE" if sat(cnf) else "UNSATISFIABLE")


# Reads the input file in dimacs form and returns the expression tree of the formula in CNF
def read_cnf(fname):
    children = []
    for line in open(fname, 'r'):
        if line[0] in ("c", "p"):
            continue
        children.append(VariadicNode(OR, [get_literal_node(l) for l in line.split() if int(l)]))
    return VariadicNode(AND, children)


# Returns the leaf xn for n in input, and not(xn) for -n in input
def get_literal_node(l):
    i = int(l)
    return Leaf("x" + l) if i > 0 else UnaryNode(NOT, Leaf("x" + str(-i)))


def sat(cnf):
    return False


if __name__ == '__main__':
    main()
