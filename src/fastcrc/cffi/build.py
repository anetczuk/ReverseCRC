#!/usr/bin/env python2
##
##
##
##

import os
from cffi import FFI


SCRIPT_DIR      = os.path.realpath( os.path.dirname( __file__ ) )
FASTCRC_ROOT    = os.path.join( SCRIPT_DIR, os.pardir )

FASTCRC_SRC_DIR = os.path.join( FASTCRC_ROOT, "src", "crchw" )
FASTCRC_LIB_DIR = os.path.join( FASTCRC_ROOT, "build", "install" )
CFFI_BUILD_DIR  = os.path.join( SCRIPT_DIR, "build" )


ffibuilder = FFI()


ffibuilder.cdef( r"""
typedef struct {
    uint8_t reginit;              /// registry initial value
    uint8_t xorout;               /// xor-red result
} CRC8Result;

typedef struct {                                                                                            
    size_t size;                                                                                            
    size_t capacity;                                                                                        
    CRC8Result* data;                                                                                   
} CRC8ResultArray; 
    
void CRC8ResultArray_free( CRC8ResultArray* array );


/// ===============================================


uint8_t hw_crc8_calculate( const uint8_t* data_buffer, const size_t data_size, const uint8_t polynomial, const uint8_t init_reg, const uint8_t xor_val );


uint8_t hw_crc8_calculate_param( const uint8_t* data_buffer, const size_t data_size, 
                                 const uint8_t polynomial, const uint8_t init_reg, const uint8_t xor_val,
                                 const bool reverse_order_flag, const bool reflect_bits_flag );


CRC8ResultArray* hw_crc8_calculate_range( const uint8_t* data_buffer, const size_t data_size, const uint8_t data_crc, 
                                          const uint8_t polynomial, 
                                          const uint8_t init_start, const uint8_t init_end, 
                                          const uint8_t xor_start, const uint8_t xor_end );


/// ==============================================================================================
/// ==============================================================================================


typedef struct {
    uint16_t reginit;              /// registry initial value
    uint16_t xorout;               /// xor-red result
} CRC16Result;

typedef struct {                                                                                            
    size_t size;                                                                                            
    size_t capacity;                                                                                        
    CRC16Result* data;                                                                                   
} CRC16ResultArray; 
    
void CRC16ResultArray_free( CRC16ResultArray* array );


/// ===============================================


uint16_t hw_crc16_calculate( const uint8_t* data_buffer, const size_t data_size, const uint16_t polynomial, const uint16_t init_reg, const uint16_t xor_val );


uint16_t hw_crc16_calculate_param( const uint8_t* data_buffer, const size_t data_size, 
                                   const uint16_t polynomial, const uint16_t init_reg, const uint16_t xor_val,
                                   const bool reverse_order_flag, const bool reflect_bits_flag );


CRC16ResultArray* hw_crc16_calculate_range( const uint8_t* data_buffer, const size_t data_size, const uint16_t data_crc, 
                                            const uint16_t polynomial, 
                                            const uint16_t init_start, const uint16_t init_end, 
                                            const uint16_t xor_start, const uint16_t xor_end );


/// ==============================================================================================
/// ==============================================================================================


typedef struct {                                                                                            
    size_t size;                                                                                            
    size_t capacity;                                                                                        
    uint16_t* data;                                                                                   
} uint16_array; 
    
void uint16_array_free( uint16_array* array );


/// ===============================================


uint16_array* hw_crc16_invert( const uint8_t* data_buffer, const size_t data_size, const uint16_t polynomial, const uint16_t reg );


CRC16ResultArray* hw_crc16_invert_range( const uint8_t* data_buffer, const size_t data_size, const uint16_t crc_num, const uint16_t polynomial, const uint16_t xor_start, const uint16_t xor_end );

""")

# with open( os.path.join( FASTCRC_SRC_DIR, "crc8hw.h"  )) as f:
#     ffibuilder.cdef( f.read() )


ffibuilder.set_source(
    "cffi_fastcrc",
    ## no source neede, because linking to existing library
    r"""
#include "crc8hw.h"
#include "crc16hw.h"
#include "crc16hwinvert.h"
""",
    include_dirs=[ FASTCRC_SRC_DIR ],

    libraries=["fastcrc"],
    library_dirs=[ FASTCRC_LIB_DIR ],
    extra_link_args=[ '-Wl,-rpath=' + FASTCRC_LIB_DIR ]
)


ffibuilder.compile( tmpdir=CFFI_BUILD_DIR )


print "build completed"
