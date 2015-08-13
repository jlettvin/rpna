# rpna
## Reverse Polish Notation Array calculator ##

### (Python gpgpu kernel to support the entire cmath language) ###

shmath is daemon providing generic math services to client programs.  The
result of shmath is massive calculations being performed efficiently using more
of the calculation resources available on the computer.

Most math libraries use 1 CPU in linea, pipelined, or vector mode.  Most modern
computers have multiple CPUs and at least one GPU.  Managing distribution of a
calculation over these resources is useful.  A lightly loaded 4 CPU machine can
support higher calculation velocity.  Sharing the load onto a GPU should
increase velocity further despite DMA transfer costs associated with sharing
between CPU and GPU.  The result should be a potential order of magnitude
velocity increase.  Perhaps even more if shmath is carefully designed.  Even
context-switching costs are reduced when run on multiple CPUs.  

The approach I am proposing is to write an RPN interpreter in shmath which
compiles into locally specialized shmath code to distribute load.  The client
program sends the RPN and shared memory keys to shmath then executes the code
by filling source operand buffers and triggering a shmath execution round to
fill the target buffer after which the client can perform follow-on operations
like display.  

I would expect that heavy use of shmath would cause a computer to heat up
substantially due to efficient use.

A cool computer is an idle computer.
