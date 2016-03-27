from abc import ABC, abstractmethod
import copy


class Operator:
    def __init__(self, str_reps, f):
        self.str_reps = str_reps
        self.f = f

    def __str__(self):
        return self.str_reps[0]

    def __eq__(self, other):
        if not isinstance(other, Operator):
            return NotImplemented
        return str(self) == str(other)

    def __ne__(self, other):
        if not isinstance(other, Operator):
            return NotImplemented
        return str(self) != str(other)

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self


T = Operator(["⊤", "T"], lambda: T)
F = Operator(["⊥", "F"], lambda: F)
vals = T, F

NOT = Operator(["¬", "~", "not", "!"], lambda x: T if x == F else F)
AND = Operator(["∧", "&", "and"], lambda args: T if all(a == T for a in args) else F)
OR = Operator(["∨", "|", "or"], lambda args: T if any(a == T for a in args) else F)
IMPL = Operator(["⇒", "->"], lambda x, y: T if x == F or y == T else F)
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
    def __invert__(self):
        pass

    def bracket_if_necessary(self):
        return str(self)

    @abstractmethod
    def evaluate(self, varvals):
        pass

    #
    # Special methods
    #

    def __and__(self, other):
        if not isinstance(other, Node):
            return NotImplemented
        if isinstance(other, VariadicNode) and other.op == AND:
            return self + other
        return VariadicNode(AND, [self, other])

    def __or__(self, other):
        if not isinstance(other, Node):
            return NotImplemented
        if isinstance(other, VariadicNode) and other.op == OR:
            return self + other
        return VariadicNode(OR, [self, other])

    def __neg__(self):
        return ~self


class Leaf(Node):
    def __init__(self, v):
        self.val = v

    def __eq__(self, other):
        if not isinstance(other, Leaf):
            return False
        return self.val == other.val

    def __str__(self):
        return str(self.val)

    def __invert__(self):
        return UnaryNode(NOT, self)

    def evaluate(self, varvals):
        return self.val if isinstance(self.val, Operator) else varvals[self.val]

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self


class UnaryNode(Node):
    def __init__(self, op, child):
        self.op = op
        self.child = child

    def __eq__(self, other):
        if not isinstance(other, UnaryNode):
            return False
        return self.op == other.op and self.child == other.child

    def __str__(self):
        return str(self.op) + self.child.bracket_if_necessary()

    def __invert__(self):
        return self.child if self.op == NOT else UnaryNode(NOT, self)

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
        return self.op == other.op and self.lchild == other.lchild and self.rchild == other.rchild

    def __str__(self):
        return self.lchild.bracket_if_necessary() + " " + str(self.op) + " " + self.rchild.bracket_if_necessary()

    def __invert__(self):
        if self.op == IMPL:
            return VariadicNode(AND, [self.lchild, ~self.rchild])
        return None

    def bracket_if_necessary(self):
        return "(" + str(self) + ")"

    def evaluate(self, varvals):
        return self.op.f(self.lchild.evaluate(varvals), self.rchild.evaluate(varvals))


class VariadicNode(Node):
    def __init__(self, op, children=[]):
        self.op = op
        self.children = children

    def __eq__(self, other):
        if not isinstance(other, VariadicNode):
            return False
        return (self.op == other.op and len(self) == len(other) and
                all(self.children.count(child) == other.children.count(child) for child in self))

    def __str__(self):
        return (" " + str(self.op) + " ").join(child.bracket_if_necessary() for child in self)

    def __invert__(self):
        return VariadicNode(AND if self.op == OR else OR, [~c for c in self])

    def bracket_if_necessary(self):
        return "(" + str(self) + ")"

    def evaluate(self, varvals):
        return self.op.f(child.evaluate(varvals) for child in self)

    #
    #  Special methods
    #

    def __bool__(self):
        return self is not None and bool(self.children)

    def __iter__(self):
        return iter(self.children)

    def __len__(self):
        return len(self.children)

    def __contains__(self, item):
        return item in self.children

    def __getitem__(self, i):
        return self.children[i]

    def __add__(self, other):
        if not isinstance(other, Node):
            return NotImplemented
        if isinstance(other, VariadicNode) and self.op == other.op:
            return VariadicNode(self.op, copy.copy(self.children) + copy.copy(other.children))
        return VariadicNode(self.op, self.children + [other])

    def __radd__(self, other):
        if not isinstance(other, Node):
            return NotImplemented
        if isinstance(other, VariadicNode) and self.op == other.op:
            return VariadicNode(self.op, other.children + self.children)
        return VariadicNode(self.op, [other] + self.children)

    def __iadd__(self, other):
        if not isinstance(other, Node):
            return NotImplemented
        if isinstance(other, VariadicNode) and self.op == other.op:
            self.children.extend(other.children)
            return self
        return self + other

    def __or__(self, other):
        if self.op == OR:
            return self.__add__(other)
        return super().__or__(other)

    def __ior__(self, other):
        if self.op == OR:
            return self.__iadd__(other)
        return super().__or__(other)

    def __and__(self, other):
        if self.op == AND:
            return self.__add__(other)
        return super().__and__(other)

    def __iand__(self, other):
        if self.op == AND:
            return self.__iadd__(other)
        return super().__and__(other)
