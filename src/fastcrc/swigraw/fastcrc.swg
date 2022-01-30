/// will create swigraw_fastcrc.py
%module swigraw_fastcrc

/// declarations for C/C++ side binding
%{
#include "fastcrc_interface.h"
%}


/// declarations for Python side binding

%pythoncode %{##================================================##%}


%include "stdint.i"             /// uint8_t
%include "carrays.i"            /// C array wrappers


%array_functions( uint8_t, Uint8Array );


%include "fastcrc_interface.h"
