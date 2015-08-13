DATETIME=`date +%Y%m%d%H%M%S`
MODULE=RPN
MAIN=${MODULE}.py

# Makefile
# __date__       = "20130101"
# __author__     = "jlettvin"
# __maintainer__ = "jlettvin"
# __email__      = "jlettvin@gmail.com"
# __copyright__  = "Copyright(c) 2013 Jonathan D. Lettvin, All Rights Reserved"
# __license__    = "Trade Secret"
# __status__     = "Production"
# __version__    = "0.0.1"

all:	Makefile
	@echo "Demonstration of the Reverse Polish Notation for human optics."
	@echo "Hit <Esc> to quit."
	@echo "Ignore the 7 VIDIOC_QUERYMENU: Invalid argument messages"
	@echo "A number of requirements must be satisfied before running this."
	@./__main__.py --rpn=rpn/human.rpn

.PHONY: tgz
tgz:
	@echo ${DATETIME} incremental backup
	@mkdir -p tgz
	@tar cvzf tgz/${MODULE}.src.${DATETIME}.tgz . \
	  --exclude="*.tgz" \
	  --exclude="*.pyc" \
	  --exclude="*.perf" \
	  --exclude="*.prof" \
	  --exclude="tgz/*" \
	  --exclude="unsorted/*" \
	  --exclude="download/*" \
	  --exclude="kernels/*" \
	  --exclude=".git" \
	  --exclude=".git/*" \
	  --exclude="log" \
	  --exclude="log/*" \
	  --exclude="tgz" \
	  --exclude="tgz/*" \
	  --exclude="tmp" \
	  --exclude="tmp/*" \
	  --exclude="img" \
	  --exclude="img/*" \
	  --exclude="graph/*" \
	  --exclude="spine/*" \
	  --exclude="*.swp"


