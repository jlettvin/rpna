#!/usr/bin/env python

"""
rpn.py Copyright(c) 2011 Jonathan D. Lettvin, All Rights Reserved.
This script is licensed under Creative Commons Attribution 3.0.
http://creativecommons.org/licenses/by/3.0/
The author requests attribution of authorship under this license.
The original source is located at:
http://wiki.lettvin.com/Jonathan/wiki/index.php/Python:rpn
"""

import sys,string,operator,scipy,scipy.special,exceptions

class RPN(object):
    """
    An RPN (Reverse Polish Notation) interpreter class.
    Single line strings are interpreted.  String is echoed, followed by '=' then result.
    Example: input "1 1 +" generates output 2 = "1 1 +"
    Example: input "9 sqrt" generates output 3 = "9 sqrt"
    Example: input "3 2 ^ 4 2 ^ + sqrt" generates output 5 = "3 2 ^ 4 2 ^ + sqrt"

    Enhancement: This version works on arrays of numbers.
    Arrays are shaped by the '#' prefix followed by positive integers separated by 'x'.
    The count of integers is the count of dimensions.
    The integer specifies the "radius" of the array from its center.
    """

    def __init__(self, verbose=False):
        """
        Initialize an interpreter.
        The interpreter keeps a current token, a register index, an operand pair, verbosity,
        an operand stack, 26 letter-named registers, and a keytable for launching functions.
        First letter of a token triggers a function from the keytable.
        Operands are to be separated by spaces.
        Top of stack can be stored and retrieved from letter-named registers.
        Numbers must begin with a digit.
        """
        self.radius, self.shape = 0, (1)
        self.a1, self.a2 = scipy.zeros(self.shape, float), scipy.zeros(self.shape, float)
        self.token, self.index, self.verbose = '', 0, verbose
        self.stack, self.register, self.key = [], [0.0]*26, [self.nop]*256
        self.dict, self.list, self.number = dict(), list(), dict()
        self.internal = { 'set': self.set, 'get': self.get, 'clr': self.clr }
        for k, v in {
            '+': self.add, '-': self.sub, '*': self.mul, '/': self.div, '^': self.pow,
            '$': self.reg, # choose a register by name (no operation)
            '#': self.arr, # declare an N-dimensional shape
            '|': self.vec, # declare a 1-dimensional vector
            '\\': self.out # perform outer-product of vectors
            }.iteritems(): self.key[ord(k)] = v
        for c in string.ascii_lowercase: self.key[ord(c)] = self.opr
        for c in string.digits: self.key[ord(c)] = self.num

    def call(self):
        """
        Call a scipy function.  If no direct link is local, find it in scipy and link it local.
        Pop the top of stack.  Run the single-parameter scipy function.  Push result on stack.
        """
        if self.token in self.internal: self.internal[self.token]()
        elif self.token not in self.dict:
            for module in (scipy, scipy.special):
                try: self.dict[self.token] = module.__dict__[self.token]
                except: pass
                if self.token in self.dict:
                    self.number[self.token] = len(self.list) # Enables future compilation
                    self.list.append(self.dict[self.token])  # Enables future compilation
                    break
            assert self.token in self.dict, 'Unable to use function: '+self.token
            if self.token in self.dict:
                self.stack.append(self.dict[self.token](self.stack.pop()))

    """Service functions used by keytable functions."""
    def regnum(self, letter): return ord(self.token[1])-ord('a')
    def limit(self,lo=1,hi=1): assert lo<=len(self.token)<=hi
    def pop2(self):
        self.a1 = self.stack.pop()
        self.a2 = self.stack.pop()

    """Functions to be driven from the keytable."""
    def clr(self): self.register = [0.0]*26; self.index = 0
    def nop(self): print self; assert False, 'nop'
    def reg(self): self.limit(2,2); self.index=self.regnum(self.token[1])
    def get(self): self.stack.append(self.register[self.index])
    def set(self): self.register[self.index] = self.stack.pop()
    def num(self): self.stack.append(float(self.token)*scipy.ones(self.shape))
    def opr(self): self.call()
    def add(self): self.pop2(); self.stack.append(self.a2  + self.a1)
    def sub(self): self.pop2(); self.stack.append(self.a2  - self.a1)
    def mul(self): self.pop2(); self.stack.append(self.a2  * self.a1)
    def div(self): self.pop2(); self.stack.append(self.a2  / self.a1)
    def pow(self): self.pop2(); self.stack.append(self.a1 ** self.a2)
    def out(self): self.pop2(); self.stack.append(scipy.outer(self.a1,self.a2))
    def vec(self):
        self.shape = (int(self.token[1:]))
        self.a1, self.a2 = scipy.zeros(self.shape, float), scipy.zeros(self.shape, float)
    def arr(self):
        self.radius = [int(d) for d in string.split(self.token[1:],'x')]
        self.shape = tuple([1 + 2 * int(d) for d in self.radius])
        self.a1, self.a2 = scipy.zeros(self.shape, float), scipy.zeros(self.shape, float)

    def __call__(self, expr):
        """
        Interpreter: When interpretation finishes, string is empty and stack has one item.
        State of interpreter has residue during next entry.
        A "clr" instruction in the expression restores registers to 0.
        Snapped links to scipy functions remain snapped during lifetime of interpreter object.
        """
        if self.verbose: print expr
        for self.token in string.split(expr):
            self.key[ord(self.token[0])]()
            if self.verbose: print self
        assert len(self.stack)==1
        value = self.stack.pop()
        print '"%s"' % (expr)
        print value[0] if self.shape == (1) else value
        return value

    def __repr__(self):
        """Generate viewable string showing interpreter state."""
        return 'token: "%s", stack: %s, register: %s' % (
            self.token, str(self.stack), chr(ord('a')+self.index))

if __name__ == "__main__":
    from optparse import OptionParser
    usage = """Usage: %prog [options]
    RPN (Reverse Polish Notation) calculator with full access to single-arg scipy functions."""
    parser = OptionParser(usage=usage, version="%prog 0.01", description="")
    parser.add_option("-v", "--verbose", action="store_true", default=False)
    parser.add_option("-p", "--pipe", action="store_true", default=False)
    (opts,args) = parser.parse_args()
    try:
        interpret = RPN(opts.verbose)
        if opts.pipe:
            for line in sys.stdin: interpret(line.strip())
        elif len(args) > 0:
            for arg in args: interpret(arg)
        else:
            interpret('2 2 +')
            interpret('%f $x set %f $y set $x get 2 ^ $y get 2 ^ + sqrt' % (3, 4))
            interpret('clr &_intentional_bad_character_to_illustrate_error_handling.')
    except Exception as e: print sys.exc_info()[0], e

