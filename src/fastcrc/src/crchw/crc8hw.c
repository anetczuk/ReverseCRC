///

#include "crc8hw.h"

#include <stdlib.h>
#include <stdio.h>


/// =====================================================


CRC8ResultArray* CRC8ResultArray_alloc( const size_t capacity ) {
    CRC8ResultArray* array = malloc( sizeof(CRC8ResultArray) );
    CRC8ResultArray_init( array, capacity );
    return array;
}

void CRC8ResultArray_init( CRC8ResultArray* array, const size_t capacity ) {
    array->size = 0;
    array->capacity = capacity;
    array->data = malloc( capacity * sizeof(CRC8Result) );
}

void CRC8ResultArray_free( CRC8ResultArray* array ) {    
    free( array->data );
    array->capacity = array->size = 0;
    array->data = NULL;
}

void CRC8ResultArray_pushback( CRC8ResultArray* array, const CRC8Result item ) { 
    if (array->size == array->capacity) {
        if ( array->capacity < 1 ) {
            array->capacity = 1;
        } else {
            array->capacity *= 2;
        }
        array->data = realloc( array->data, array->capacity * sizeof(CRC8Result) );     /// copies memory if needed
    }
    array->data[ array->size++ ] = item;
}

CRC8Result* CRC8ResultArray_get( CRC8ResultArray* array, const size_t index ) {
    return &array->data[ index ];
}


/// =====================================================


/**
 * Implementation based on:
 *      https://en.wikipedia.org/wiki/Computation_of_cyclic_redundancy_checks
 *      http://www.sunshine2k.de/articles/coding/crc/understanding_crc.html
 *
 * Performance can be improved by replacing inner loop with "lookup table" for all 256 combinations of "reg" for each polynomial.
 * It can be especially beneficial if the polynomial is fixed or handling large input data.
 */
/// 'data_buffer' -- container for data -- first dataframe bit is in MSB of buffer first item
uint8_t hw_crc8_calculate( const uint8_t* data_buffer, const size_t data_size, const uint8_t polynomial, const uint8_t init_reg, const uint8_t xor_val ) {
    uint8_t reg = init_reg;
    for ( size_t i = 0; i < data_size; ++i ) {
        reg ^= data_buffer[i];                      /// xor
        for ( uint8_t j = 0; j < 8; ++j ) {
            if ( (reg & 0x80) != 0 ) {
                reg = (reg << 1) ^ polynomial;
            } else {
                reg <<= 1;
            }
        }
    }
//     printf( "calculation: poly: 0x%X init: 0x%X xor: 0x%X crc: 0x%X\n", polynomial, init_reg, xor_val, reg ^ xor_val );
    return reg ^ xor_val;    /// & ((1 << 8) - 1)
}

CRC8ResultArray* hw_crc8_calculate_range( const uint8_t* data_buffer, const size_t data_size, const uint8_t data_crc, 
                                          const uint8_t polynomial, 
                                          const uint8_t init_start, const uint8_t init_end, 
                                          const uint8_t xor_start, const uint8_t xor_end ) 
{
    CRC8ResultArray* crc_array = CRC8ResultArray_alloc( 0 );
    for ( uint8_t init_reg = init_start; init_reg <= init_end; ++init_reg ) {
        for ( uint8_t xor_val = xor_start; xor_val <= xor_end; ++xor_val ) {
            const uint8_t curr_crc = hw_crc8_calculate( data_buffer, data_size, polynomial, init_reg, xor_val );
            if ( curr_crc == data_crc ) {
                CRC8Result data;
                data.reg = 0;
                data.xor = xor_val;
                CRC8ResultArray_pushback( crc_array, data );
            }
            if ( xor_val == 0xFF) {
                /// after last value -- 'xor_val' will overflow
                break;
            }
        }
        if ( init_reg == 0xFF) {
            /// after last value -- 'xor_val' will overflow
            break;
        }
    }

    return crc_array;
}
