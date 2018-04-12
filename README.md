# rpna
## Reverse Polish Notation Array calculator
### (Python gpgpu kernel to support the entire cmath library)

This project installs a resident language kernel in the gpgpu.
The language explicitly supports use of the cmath library API.

Most math libraries use 1 CPU in linear, pipelined, or vector mode.
Most modern computers have multiple CPUs and at least one GPU.
Managing distribution of a calculation over these resources is useful.
A lightly loaded 4 CPU machine can support higher calculation velocity.
Sharing the load onto a GPU should increase velocity further
despite DMA transfer costs associated with sharing between CPU and GPU.
The result should be a potential order of magnitude velocity increase.
Perhaps even more if shmath is carefully designed.
Even context-switching costs are reduced when run on multiple CPUs.  

The proposed approach is a resident RPN interpreter in the gpgpu
which compiles into locally specialized code to distribute load.
The client can perform follow-on operations like display.

Data arrays may be accessed within the gpgpu kernel using coordinates so that
convolution and correlation may be performed on data other than the center.

### Example: (human.rpn module)

    "Capture desktop, apply human optics filter, display retinal image of desktop.
    (8.1e-3|@pupil)         # Specify aperture size.
    !optics                 # Load optics function from its file.
    (Rs| Rw| &optics| @Rt)  # Process R plane with function.
    (Gs| Gw| &optics| @Gt)  # Process G plane with function.
    (Bs| Bw| &optics| @Bt)  # Process B plane with function.

This program performs several array processing steps on live camera images:
It models the human eye with typical dimensions, and sets the pupil to 8.1mm.
For the R plane of the RGB image data, the following steps are executed:

    @pupil     Store the pupil size in a named variable
    Rs         Push Rs, the R source data plane, on the stack
	Rw         Push the peak wavelength for R data on the stack
	&optics    Call the optics function
	@Rt        Store the processed R target data in named variable Rt

The rpn program uses an RPN module called optics.
The optics.rpn module defines a single function in one line:

    (:optics| Iw| divide| zoom| sqrt| pupil| diffract| square)

This normalizes the input intensity with Iw
then uses the normalized value as a zoom factor (to emulate refraction)
then takes the square root to convert intensity to wave amplitude
then applies the diffraction function using the pupil size
then squares the result to restore the image to an intensity map.

Additional modules are used (such as diffract) which use similar methods.

    (:Rwave| Rs| sqrt| pupil| diffract| square| @Rt)
    (:Gwave| Gs| sqrt| pupil| diffract| square| @Gt)
    (:Bwave| Bs| sqrt| pupil| diffract| square| @Bt)
    (1e-3| Iw| Rw| /| *| @pupil)
    &Rwave
    (1e-3| Iw| Gw| /| *| @pupil)
    &Gwave
    (1e-3| Iw| Bw| /| *| @pupil)
    &Bwave
