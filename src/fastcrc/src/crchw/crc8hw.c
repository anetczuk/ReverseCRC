///

#include "crc8hw.h"

#include "crcutils.h"

#include <string.h>                 /// memcpy
/// #include <stdio.h>


/// =====================================================


GENERATE_VECTOR_BODY( CRC8ResultArray, CRC8Result )


#define USE_LOOKUP


#ifndef USE_LOOKUP
    /// standard implementation
    
    /**
     * Implementation based on:
     *      https://en.wikipedia.org/wiki/Computation_of_cyclic_redundancy_checks
     *      http://www.sunshine2k.de/articles/coding/crc/understanding_crc.html
     */
    /// 'data_buffer' -- container for data -- first dataframe bit is in MSB of buffer first item
    uint8_t hw_crc8_calculate( const uint8_t* data_buffer, const size_t data_size, const uint8_t polynomial, const uint8_t init_reg, const uint8_t xor_val ) {
        uint8_t reg = init_reg;
        for ( size_t i = 0; i < data_size; ++i ) {
            reg ^= data_buffer[i];                      /// xor
            
            if ( (reg & 0xFF) == 0 ) {
                /// there will be no xor-ring with poly -- just shift
                reg <<= 8;
                continue ;
            }
            
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

#else
    /// lookup table implementation
    
    #include "crc8lookup.h"
    
    
    /**
     * Implementation based on:
     *      https://en.wikipedia.org/wiki/Computation_of_cyclic_redundancy_checks
     *      http://www.sunshine2k.de/articles/coding/crc/understanding_crc.html
     */
    /// 'data_buffer' -- container for data -- first dataframe bit is in MSB of buffer first item
    uint8_t hw_crc8_calculate( const uint8_t* data_buffer, const size_t data_size, const uint8_t polynomial, const uint8_t init_reg, const uint8_t xor_val ) {
//         printf( "hw_crc8_calculate: size: %zu poly: 0x%X init: 0x%X xor: 0x%X\n", data_size, polynomial, init_reg, xor_val );
        uint8_t reg = init_reg;
        for ( size_t i = 0; i < data_size; ++i ) {
            reg ^= data_buffer[i];                      /// xor
            reg = CRC8_LookupTable[ polynomial ][ reg ];
        }
    //     printf( "calculation: poly: 0x%X init: 0x%X xor: 0x%X crc: 0x%X\n", polynomial, init_reg, xor_val, reg ^ xor_val );
        return reg ^ xor_val;    /// & ((1 << 8) - 1)
    }

#endif


uint8_t hw_crc8_calculate_param( const uint8_t* data_buffer, const size_t data_size, 
                                 const uint8_t polynomial, const uint8_t init_reg, const uint8_t xor_val,
                                 const bool reverse_order_flag, const bool reflect_bits_flag ) 
{
//     printf( "flags: %i %i\n", reverse_order_flag, reflect_bits_flag );
    
    uint8_t* data_copy = NULL;
    if ( reverse_order_flag || reflect_bits_flag ) {
        const size_t totalSize = sizeof(uint8_t) * data_size;
        data_copy = malloc( totalSize );
        memcpy( data_copy, data_buffer, totalSize );
    }
    
    if ( reverse_order_flag ) {
        reverse_order( data_copy, data_size );
    }
    if ( reflect_bits_flag ) {
        reflect_bits_array( data_copy, data_size );
    }
    
    if ( data_copy == NULL ) {
        return hw_crc8_calculate( data_buffer, data_size, polynomial, init_reg, xor_val );
    } else {
        const uint8_t crc = hw_crc8_calculate( data_copy, data_size, polynomial, init_reg, xor_val );
        free( data_copy );
        return crc;
    }
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
                data.reg = init_reg;
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
