#!/usr/bin/env python

import          os
import          sys
import          gc

from optparse   import OptionParser

#from scipy      import zeros, ones, array, asarray, arange, uint8, around
from scipy      import zeros
from scipy      import asarray
from scipy      import dstack
from scipy      import rollaxis

# Imports from OpenCV
#from cv2        import getAffineTransform, warpAffine, filter2D
from cv2.cv     import GetSubRect
from cv2.cv     import NamedWindow
from cv2.cv     import GetCaptureProperty
from cv2.cv     import CaptureFromCAM
from cv2.cv     import CreateMat
from cv2.cv     import GetMat
from cv2.cv     import QueryFrame
from cv2.cv     import ShowImage
from cv2.cv     import WaitKey
from cv2.cv     import DestroyAllWindows
from cv2.cv     import CV_8UC3
#from cv2.cv     import CV_32FC1
from cv2.cv     import CV_CAP_PROP_FRAME_WIDTH
from cv2.cv     import CV_CAP_PROP_FRAME_HEIGHT

import hotshot, hotshot.stats

from RPN        import RPN

class RedirectStdStreams(object):
    def __init__(self, stdout=None, stderr=None):
        self._stdout = stdout or sys.stdout
        self._stderr = stderr or sys.stderr

    def __enter__(self):
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        self.old_stdout.flush(); self.old_stderr.flush()
        sys.stdout, sys.stderr = self._stdout, self._stderr

    def __exit__(self, exc_type, exc_value, traceback):
        self._stdout.flush(); self._stderr.flush()
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr

class Interface(object):
    def __init__(self, **kw):
        self.kw = kw
        self.iteration = 0
        self.scale = 255.0
        self.active = False
        self.msg = ''
        self.rpn = RPN(**self.kw)
        self.dtype = float
        self.keys = {
                ' ': self.noop,
                '-': self.down,
                '+': self.up,
                '.': self.toggleTest,
                '!': self.toggleDeep,
                }

        devnull = open(os.devnull, 'w')
        with RedirectStdStreams(stdout=devnull, stderr=devnull):
            self.initOpenCV()

    def __call__(self):
        self.collect()
        self.process()
        self.project()
        return self.listen()

    #vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def collect(self):
        self.iteration += 1
        # Fetch and normalize the camera image.
        self.camera = rollaxis(
                asarray(GetMat(QueryFrame(self.capture))).astype(self.dtype) /
                self.scale,
                2,
                0)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def process(self):
        """
        Input/output buffers are expected to be normalized in range 0.0-1.0.
        Their shape is (3,Y,X)

        Push self.camera onto the RPN stack.
        Run the RPN instructions.
        Pop self.target from the RPN stack.
        """
        self.target = self.rpn(self.camera, **self.kw)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def project(self):
        self.copy(self.screen, dstack(self.scale * self.target))
        if kw.get('verbose', False):
            self.tell(self.screen)
            self.tell()
        ShowImage("RPN", self.paste)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def copy(self, tgt, src):
        tgt[:,:,:] = src[:,:,:]
        return tgt

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def report(self, msg):
        print ' '*79 + '\r' + msg

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def tell(self, data = None):
        if data == None:
            print self.msg, self.iteration, '\r',
            self.msg = ''
            sys.stdout.flush()
        else:
            pass

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def parameters(self, **kw):
        self.kw.update(kw)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def aboutKey(self, c):
        lines = self.keys.get(c, self.keys[c])['act'].__doc__.split('\n')
        self.report("\t"+c+": "+str.strip(lines[1] if len(lines) > 1 else lines[0]))

    def noop(self):
        pass

    def down(self):
        pass

    def up(self):
        pass

    def toggleTest(self):
        pass

    def toggleDeep(self):
        pass

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def listen(self):
        result = True
        # Check for keyboard input.
        key = WaitKey(6)    # milliseconds between polling (-1 if none).

        if key == -1:
            self.parameters()
            gc.collect()
            return result

        key %= 256

        print int(key)

        if key == 27:
            result = False
        elif ord(' ') == key:
            self.active ^= True
            self.report('processing' if self.active else 'noop')
            """
            # See Eye.py for origin of the commented-out code
        elif ord('-') == key:
            if self.slope > 1.0: self.slope /= 1.1
            print 'slope', self.slope
        elif ord('+') == key or ord('=') == key:
            if self.slope < 1e3: self.slope *= 1.1
            print 'slope', self.slope
        elif ord('.') == key:
            self.test ^= True
            self.report('test pattern: ' + str(self.test))
        elif ord('!') == key and not self.newparams:
            self.saturate ^= True
            self.report('saturate: ' + str(self.saturate))
        elif ord('a') <= key <= ord('z'):
            c = chr(key - ord(' '))
            if c in self.keys.keys():
                self.char = c
                self.aboutKey(c)
        elif ord('1') <= key <= ord('8') and not self.newparams:
            self.pupil = key - ord('0')
            self.aperture = self.pupil * 1e-3
            self.report(
                    'Pupil: %d millimeters = %f' %
                    (self.pupil, self.aperture))
            """
        else:
            #self.report('Unknown: %d' % (key))
            pass
        return result

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def initOpenCV(self):
        """
        Prepare camera input and video output.
        This is run once at the beginning of the program.
        """
        # Setup OpenCV
        self.camera     = self.kw.get("camera", 0)
        self.capture    = CaptureFromCAM(self.camera)
        #self.capture.set(3, 640)
        #self.capture.set(4, 480)

        # A hack to prevent saturation.
        self.decay1     = 3e-1
        self.diffusion  = 4e+0
        self.dsize      = tuple(int(GetCaptureProperty(self.capture, p))
                for p in (CV_CAP_PROP_FRAME_WIDTH, CV_CAP_PROP_FRAME_HEIGHT))
        self.X, self.Y  = self.dsize
        self.shape      = (self.Y, self.X, 3)
        self.paste      = CreateMat(self.Y, self.X, CV_8UC3)
        self.screen     = asarray(GetSubRect(self.paste, (0,0, self.X,self.Y)))

        # Associate color planes with correct letter.
        self.plane      = {c:n for n,c in enumerate('BGR')}
        self.target     = zeros((self.Y,self.X,3), dtype=self.dtype)

#MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
if __name__ == "__main__":

    #PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
    # Command-line parsing
    parser = OptionParser()
    parser.add_option(
            '-r', '--rpn', type=str, default='capture.rpn',
            help='name of a .rpn file with code')
    parser.add_option(
            '-p', '--profiling', action="store_true", default=False, help="time")
    parser.add_option(
            '-v', '--verbose', action="store_true", default=False, help="test")
    (opts, args) = parser.parse_args()
    kw = vars(opts)

    profiling = kw.get('profiling', False)
    if profiling:
        kw['profile'] = hotshot.Profile('__main__.prof')

    def mainloop(**kw):
        interface = Interface(**kw)
        while interface(): pass

    try:
        NamedWindow("RPN", 1)
        if profiling:
            kw['profile'].runcall(mainloop, **kw)
        else:
            mainloop(**kw)
    finally:
        DestroyAllWindows()
        if profiling:
            kw['profile'].close()
            stats = hotshot.stats.load('__main__.prof')
            stats.strip_dirs()
            stats.sort_stats('cumulative', 'time')
            stats.print_stats(20)
