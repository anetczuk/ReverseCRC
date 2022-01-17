///

#include "crc16hw.h"

#include <stdlib.h>
#include <stdio.h>


/// =====================================================


CRC16ResultArray* CRC16ResultArray_alloc( const size_t capacity ) {
    CRC16ResultArray* array = malloc( sizeof(CRC16ResultArray) );
    CRC16ResultArray_init( array, capacity );
    return array;
}

void CRC16ResultArray_init( CRC16ResultArray* array, const size_t capacity ) {
    array->size = 0;
    array->capacity = capacity;
    array->data = malloc( capacity * sizeof(CRC16Result) );
}

void CRC16ResultArray_free( CRC16ResultArray* array ) {    
    free( array->data );
    array->capacity = array->size = 0;
    array->data = NULL;
}

void CRC16ResultArray_pushback( CRC16ResultArray* array, const CRC16Result item ) { 
    if (array->size == array->capacity) {
        if ( array->capacity < 1 ) {
            array->capacity = 1;
        } else {
            array->capacity *= 2;
        }
        array->data = realloc( array->data, array->capacity * sizeof(CRC16Result) );     /// copies memory if needed
    }
    array->data[ array->size++ ] = item;
}

CRC16Result* CRC16ResultArray_get( CRC16ResultArray* array, const size_t index ) {
    return &array->data[ index ];
}


/// =====================================================


/**
 * Implementation based on:
 *      https://en.wikipedia.org/wiki/Computation_of_cyclic_redundancy_checks
 *      http://www.sunshine2k.de/articles/coding/crc/understanding_crc.html
 */
/// 'data_buffer' -- container for data -- least significant byte first
uint16_t hw_crc16_calculate( const uint8_t* data_buffer, const size_t data_size, const uint16_t polynomial, const uint16_t init_reg, const uint16_t xor_val ) {
    uint16_t reg = init_reg;
    for ( size_t i = 0; i < data_size; ++i ) {
        reg ^= data_buffer[i] << 8;                      /// xor into MSB
        for ( uint8_t j = 0; j < 8; ++j ) {
            if ( (reg & 0x8000) != 0 ) {
                reg = (reg << 1) ^ polynomial;
            } else {
                reg <<= 1;
            }
        }
    }
    return reg ^ xor_val;    /// & ((1 << 8) - 1)
}

CRC16ResultArray* hw_crc16_calculate_range( const uint8_t* data_buffer, const size_t data_size, const uint16_t data_crc, 
                                            const uint16_t polynomial, 
                                            const uint16_t init_start, const uint16_t init_end, 
                                            const uint16_t xor_start, const uint16_t xor_end ) 
{
    CRC16ResultArray* crc_array = CRC16ResultArray_alloc( 0 );
    for ( uint16_t init_reg = init_start; init_reg <= init_end; ++init_reg ) {
        for ( uint16_t xor_val = xor_start; xor_val <= xor_end; ++xor_val ) {
            const uint16_t curr_crc = hw_crc16_calculate( data_buffer, data_size, polynomial, init_reg, xor_val );
            if ( curr_crc == data_crc ) {
                CRC16Result data;
                data.reg = init_reg;
                data.xor = xor_val;
                CRC16ResultArray_pushback( crc_array, data );
            }
            if ( xor_val == 0xFFFF) {
                /// after last value -- 'xor_val' will overflow
                break;
            }
        }
        if ( init_reg == 0xFFFF) {
            /// after last value -- 'xor_val' will overflow
            break;
        }
    }

    return crc_array;
}
