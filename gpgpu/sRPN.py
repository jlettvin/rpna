#!/usr/bin/env python

"""sRPN.

Usage:
    sRPN.py
    sRPN.py (-v | --verbose)
    sRPN.py (-h | --help)
    sRPN.py --version
    sRPN.py --sample

Options:
    -v --verbose    Turn on extra output
    -h --help       Show this text
    --version       Show version
    --sample        Output sample text

Example: (see class sRPN, method sample() for input test data.
    ./sRPN.py --sample | ./sRPN.py

"""

#TODO Make a function definition capability.

import os, sys, scipy, inspect, time, traceback, types, scipy.constants
from pprint import pprint
from docopt import docopt

class sRPN(dict):

    def whoami(self):
        if self.verbose:
            print '\n%s' % (inspect.stack()[1][3])

    def showInternals(self):
        if self.verbose:
            print '\tsRPN keys:'
            pprint(self.keys())
            print '\tscipy constants:'
            pprint(self['scipyc'])
            print '\tscipy funs of 1 arg:'
            pprint(self['scipy1'])
            print '\tscipy funs of 2 args:'
            pprint(self['scipy2'])
            print self.symbol, self.stack

    def sample(self):
        print \
"""
.code
"Double-quoted strings are comments."
{"Lines beginning with comma are treated as code"}
{"Everything after a close bracket is RSVPed."} hello world.
.data
Lines without comma prefix are RSVPed.
.code
"1.0 @hi stores 1.0 in the local dictionary under the name hi."
"1.0 &hi stores 1.0 in whatever dictionary has the name hi."
{"Lines enclosed in brackets push/pop a new local dictionary."}
{10 5 / "leaves the value 2 pushed on the stack.  But then dict is popped."}
10 5 / "leaves the value 2 pushed on the stack."
0 cos "leaves the value 1 pushed on the stack."
"A keyword is assumed to be something to lookup."
"1) It is tried as a value looked up from the dictionary."
"2) It is tried as a linked native method name."
"3) It is tried as a scipy constant."
"4) It is tried as a scipy function of 1 parameter."
"5) It is tried as a scipy function of 2 parameters."
"An unquoted '.' character in code invokes a native method which quits."
"So do the keywords quit, done, exit, stop, kill, and die."
"Anything else causes a fatal assertion."
.data
Isn't this great?
A short word and one of an extremely overextended length should work.
.code
{"Another comment" 2 2 * @a} Let's test complex lines.
1.10 @hi 0.90 @lo
.data
Slow down (about 1/sec).
.code
{0.03 &hi 0.01 &lo}
.data
Speed up (about 50/sec).
.code
{0.30 &hi 0.10 &lo}
.data
Normal speed (about 5/sec).

I cdnuolt blveiee taht I cluod
aulaclty uesdnatnrd waht I was
rdanieg.  The phaonmneal pweor of
the hmuan mnid, aoccdrnig to a
rscheearch at Cmbrigde
Uinervtisy, it deosn't mttaer in
waht oredr the ltteers
in a wrod are, the olny iprmoatnt
tihng is taht the frist and lsat
ltteer be in the rghit pclae. Then
rset can be a taotl mses and you
can still raed it wouthit a
porbelm.

Tihs is bcuseae the huamn mnid
deos not raed ervey lteter by
istlef, but the wrod as a wlohe.
Amzanig huh? Yaeh and I awlyas
tghuhot slpeling was ipmorantt!
If you can raed tihs psas it on!!

.code
{.} Final text.

Any old garbage may follow a quit.
!#$$#@%*^(*)(*_)(*:{}><>|>:
Everything else is ignored after the '.' termination request and "Final text."
,   quit 2 sin "All this is ignored."
"""

    def getSymbol(self, key):
        for d in self.symbol:
            if key in d.keys():
                return d[key]
        return None

    def putSymbol(self, key, value):
        self.symbol[0][key] = value

    def modSymbol(self, key, value):
        for d in self.symbol:
            if key in d.keys():
                d[key] = value
                return
        # If no existing symbol, it must be local
        self.symbol[0][key] = value

    def makeNumber(self, value):
        return scipy.ones((1), dtype=float) * value

    def takeNumber(self, sarray):
        return sarray[0]

    def __init__(self, **kw):
        """
        Initialize the interpreter prior to execution.
        """
        self.update(kw)
        self.symbol = [{}, self]
        self.stack = []

        self.fixations = []
        self.reticle = {'x0':0, 'y0':0, 'x1':350, 'y1':20}
        self.width = 15
        self.hash = 7
        self.segment, self.offset, self.tparam = '', 0.5, 0.1
        self.putSymbol('hi', self.makeNumber(0.15))
        self.putSymbol('lo', self.makeNumber(0.05))
        self.lineString = ""
        self.lineNumber = 0
        self.verbose = False
        self.states = { '.data':0, '.code':1, }
        self.setats = {val:key for key, val in self.states.iteritems()}
        self.state = self.states['.code']
        self.run = True

        # Allow any of a number of keys to cause RPN termination.
        for quit in ['quit', 'done', 'exit', 'stop', 'kill', 'die', '.']:
            self[quit] = self.quit
        # Add the names  of local methods to the interpreter.
        for key, val in {
                # Arithmetic.
                '+':self.add, '-':self.sub, '*':self.mul, '/':self.div,
                'add':self.add, 'sub':self.sub, 'mul':self.mul, 'div':self.div,
                '^':self.pow, '~':self.neg, 'pow':self.pow, 'neg':self.neg,
                # Show the current state of the stack.
                '!':self.showStack, 'show':self.showStack,
                # Set internal RSVP values from the stack.
                'dt':self.dur, 'off':self.off,
                #'hi':self.fhi, 'lo':self.flo,
                # Start or end a stack frame.
                '{':self.init, '}':self.fini,
                'init':self.init, 'fini':self.fini,
                }.iteritems():
            self[key] = val
        # Add the names of scipy constants and functions to the interpreter.
        self['scipyc'], self['scipy1'], self['scipy2'] = {}, {}, {}
        for key in [ # Constants
                'c', 'e', 'pi', 'mu_0', 'epsilon_0', 'h', 'hbar', ]:
            self['scipyc'][key] = eval('scipy.constants.%s' % key)
        for key in [ # Functions of 1 parameter
                'nan_to_num', 'sin', 'cos', 'tan',
                'arcsin', 'arccos', 'arctan',
                'sinh', 'cosh', 'tanh', 'arcsinh', 'arccosh', 'arctanh',
                'degrees', 'radians', 'deg2rad', 'rad2deg',
                'around', 'round_', 'rint', 'fix', 'floor', 'ceil', 'trunc',
                'exp', 'expm1', 'exp2', 'log', 'log10', 'log2', 'log1p',
                'i0', 'sinc', 'negative', 'sqrt', 'square', 'absolute', 'fabs',
                'sign',
                # http://docs.scipy.org/doc/numpy/reference/routines.statistics.html
                'amin', 'amax', 'nanmax', 'nanmin',
                'average', 'mean', 'median', 'std', 'var', ]:
            self['scipy1'][key] = eval('scipy.%s' % key)
        for key in [ # Functions of 2 parameters
                # http://docs.scipy.org/doc/numpy/reference/routines.math.html
                'hypot', 'logaddexp', 'logaddexp2', 'copysign',
                'add', 'multiply', 'divide', 'power', 'subtract',
                'true_divide', 'floor_divide', 'fmod', 'mod', 'remainder',
                'maximum', 'minimum', ]:
            self['scipy2'][key] = eval('scipy.%s' % key)

    def sAssert(self, mustBeTrue, msg):
        """
        Give some kind of line number and contents output when error occur.
        """
        if not mustBeTrue:
            print '%5d: %s' % (self.lineNumber, msg)
            print self.lineString
            sys.exit(1)

    def unimplemented(self, name, msg=""):
        self.sAssert(True, '%s: Method unimplemented.  %s' % (name, msg))

    # These are the internal methods runnable by name from the interpreter.
    def push(self, value): self.stack = [value] + self.stack
    def pop(self, N=1): v,self.stack = self.stack[0:N],self.stack[N:]; return v
    def top(self, N=1): v= self.stack[0:N]; return v
    def noop(self): pass
    def showStack(self): print self.stack
    def quit(self): self.run = False; # sys.exit(0)
    def add(self): [a, b] = self.pop(2); self.push(a+b );
    def sub(self): [a, b] = self.pop(2); self.push(a-b );
    def mul(self): [a, b] = self.pop(2); self.push(a*b );
    def div(self): [a, b] = self.pop(2); self.push(a/b );
    def pow(self): [a, b] = self.pop(2); self.push(a**b);
    def neg(self): [a   ] = self.pop(1); self.push(-a  );
    def dur(self): [a   ] = self.pop(1); self.tparam = min(-1.0,max(+1.0,a))
    def off(self): [a   ] = self.pop(1); self.offset = min(1.0,max(0,a))
    #def fhi(self): [a   ] = self.pop(1); self.modSymbol('vhi', min(1.0,max(0,a)))
    #def flo(self): [a   ] = self.pop(1); self.modSymbol('vlo', min(1.0,max(0,a)))

    def init(self):
        """open a new stack frame"""
        self.symbol = [{}] + self.symbol
    def fini(self):
        """close the existing stack frame"""
        self.symbol = self.symbol[1:]

    def ampers(self, atName):
        """Modify existing value, in whatever dictionary down the list."""
        [a] = self.pop()
        self.modSymbol(atName[1:], a)

    def atsign(self, atName):
        """Put key:value in local dictionary."""
        [a] = self.pop()
        self.putSymbol(atName[1:], a)

    def pushValue(self, token):
        self.push(self.makeNumber(float(eval(token))))

    def code(self, *tokens, **kw):
        """
        This is the entire execution loop.
        """
        for token in tokens:
            if token[0] == '@': self.atsign(token); continue
            if token[0] == '&': self.ampers(token); continue
            #if token[0] in '0123456789': self.push(float(eval(token))); continue
            if token[0] in '0123456789': self.pushValue(token); continue
            fun = self.get(token, None)
            if isinstance(fun, float): self.push(fun); continue
            elif fun: fun(); continue
            val = self['scipyc'].get(token, None)
            if val: self.push(val); continue
            fun = self['scipy1'].get(token, None)
            if fun: self.push(fun(self.takeNumber(self.pop()))); continue
            #if fun: [a] = self.pop(); self.push(fun(a)); continue
            fun = self['scipy2'].get(token, None)
            if fun: self.push(fun(*tuple(self.pop(2)))); continue
            #if fun: [a, b] = self.pop(2); self.push(fun(a, b)); continue
            value = self.getSymbol(token)
            if value: self.push(value); continue
            self.sAssert(False, 'Token "%s" is unimplemented.' % (token))

    def tokenize(self, line):
        """
        This is the entire lexical analysis.
        """

        tokens = []
        token = ""
        comment = False
        bracket = False
        context = 0
        segment = ""
        self.lineString = line

        # Tokenize the line, removing comments
        for i in range(len(line)):
            c = line[i]
            if c == '"':
                # Eliminate comments.
                comment ^= True
                continue
            if comment:
                continue

            if c in ' \t':
                # Whitespace separates tokens.
                if token:
                    tokens += [token,]
                    token = ""
            elif c == '{':
                # Brackets define local context.
                context += 1
                tokens += ['init',]
            elif c == '}':
                # Close bracket ends a local context.
                context -= 1
                self.sAssert(context >= 0, "too many close brackets")
                if token:
                    tokens += [token,]
                    token = ""
                tokens += ['fini',]
                if context == 0:
                    segment = line[i+1:].strip()
                    break
            else:
                # Anything else must be part of a token.
                token += c
        self.sAssert(context == 0, "Unclosed context")
        self.sAssert(not comment, "Unclosed double-quote comment")
        if token:
            tokens += [token,]
        if segment:
            self.displaySegments(segment)
        self.code(*tokens)

    def showFor(self, segment, multiplier=1.0):
        nhi = self.takeNumber(self.getSymbol('hi'))
        nlo = self.takeNumber(self.getSymbol('lo'))
        hi = max(nlo+1.0, nhi)
        lo = min(nhi-1.0, nlo)
        self.modSymbol('hi', self.makeNumber(hi))
        self.modSymbol('lo', self.makeNumber(lo))
        duration = abs(hi + lo) / 2.0
        duration += (abs(hi - lo) / 2.0) * scipy.tanh(self.tparam)
        print segment + '\r',
        sys.stdout.flush()
        time.sleep(duration * multiplier)

    def __call__(self, line):
        """
        This is called for every input line.
        """
        line = line.strip()
        self.lineNumber += 1
        if line in ['.code', '.data']:
            self.state = self.states[line]
        elif self.state == self.states['.code']:
            if line:
                self.tokenize(line)
        elif line:
            self.displaySegments(line)
        else:
            #TODO put in extra delay for paragraph.
            self.showFor(' ' * self.width, 2.0)

    def displayGIF(self, f):
        img, [x, y] = f.get('img', None), f.get('ul', (0,0))
        self.unimplemented("displayGIF", "Image to show at fixation point")
        # TODO display the image at the specified location

    def displaySegments(self, line):
        for segment in line.split():
            w = len(segment)
            self.sAssert(
                    w < self.width,
                    "Words must be less than %d chars (%s)" %
                    (self.width, segment))
            left = int(float(w) * self.offset)
            delta = (left & 1)
            output = " " * int(delta + self.width/2.0 - left)
            output += segment
            output += " " * int(1 + self.width - len(output))
            self.showFor(output)

    def displayReticle(self, f):
        [x0, y0], [x1, y1] = f.get('ul', (0,0)), f.get('lr', (350, 20))
        self.unimplemented("displayReticle")
        # TODO display the reticle at the specified location

    def displayHash(self, f):
        self.unimplemented("displayHash")

    def fixation(self, **kw):
        self.unimplemented("fixation", "Display external fixation points.")
        for f in fixations:
            self.displayGIF(f)

if __name__ == "__main__":
    args = docopt(__doc__, version='sRPN.py 1.0')
    srpn = sRPN(**args)
    if args['--sample']:
        srpn.sample()
        sys.exit(0)
    print ' '*srpn.hash + '|'
    while srpn.run:
        try:
            line = raw_input('')
            srpn(line)
        except:
            break
    srpn.showInternals()
