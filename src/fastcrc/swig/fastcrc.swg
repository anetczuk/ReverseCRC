/// will create swig_fastcrc.py
%module swig_fastcrc

/// declarations for C/C++ side binding
%{
#include "fastcrc_interface.h"
%}


/// declarations for Python side binding

%pythoncode %{##================================================##%}


%include "stdint.i"             /// uint8_t
%include "carrays.i"            /// C array wrappers
%include "cpointer.i"


%array_functions( uint8_t, Uint8Array );


////// following extensions are very handy (e.g. RAII), but give some computation overhead

/// wraps raw array in RAII class
// %array_class( uint8_t, Uint8Array )


/// create getter, setter, new and free for type
// %array_functions( uint8_t, Uint8Array );


// /// custom "free" function (delete, release memory)
// %extend CRC8ResultArray {
//     ~CRC8ResultArray() {
//         CRC8ResultArray_free( $self );
//     }
//     
// //     /// to add custom code to Python wrapper class do following:
// //     %pythoncode %{
// //         def customMethod(self):
// //             pass
// //     %}
// }

// /// set object returned by function managed by Python
// %pythonappend hw_crc8_calculate_range %{
//     val.thisown = True
// %}


// /// custom "free" function (delete, release memory)
// %extend CRC16ResultArray {
//     ~CRC16ResultArray() {
//         CRC16ResultArray_free( $self );
//     }
// }

// /// set object returned by function managed by Python
// %pythonappend hw_crc16_calculate_range %{
//     val.thisown = True
// %}
// 
// /// set object returned by function managed by Python
// %pythonappend hw_crc16_invert_range %{
//     val.thisown = True
// %}


%include "fastcrc_interface.h"
