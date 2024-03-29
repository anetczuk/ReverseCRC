///

#include "crc16hw.h"

#include "crcutils.h"

#include <string.h>                 /// memcpy


/// =====================================================


GENERATE_VECTOR_BODY( CRC16ResultArray, CRC16Result )


#define USE_LOOKUP


#ifndef USE_LOOKUP
    /// standard implementation

    /**
     * Implementation based on:
     *      https://en.wikipedia.org/wiki/Computation_of_cyclic_redundancy_checks
     *      http://www.sunshine2k.de/articles/coding/crc/understanding_crc.html
     */
    /// 'data_buffer' -- container for data -- first dataframe bit is in MSB of buffer first item
    uint16_t hw_crc16_calculate( const uint8_t* data_buffer, const size_t data_size, const uint16_t polynomial, const uint16_t init_reg, const uint16_t xor_val ) {
        uint16_t reg = init_reg;
        for ( size_t i = 0; i < data_size; ++i ) {
            reg ^= data_buffer[i] << 8;                      /// xor into MSB
            
            if ( (reg & 0xFF00) == 0 ) {
                /// there will be no xor-ring with poly -- just shift
                reg <<= 8;
                continue ;
            }
            
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

#else
    /// lookup table implementation
    
    #include "crc16lookup.h"
    
    
    /**
     * Implementation based on:
     *      https://en.wikipedia.org/wiki/Computation_of_cyclic_redundancy_checks
     *      http://www.sunshine2k.de/articles/coding/crc/understanding_crc.html
     */
    /// 'data_buffer' -- container for data -- first dataframe bit is in MSB of buffer first item
    uint16_t hw_crc16_calculate( const uint8_t* data_buffer, const size_t data_size, const uint16_t polynomial, const uint16_t init_reg, const uint16_t xor_val ) {
        uint16_t reg = init_reg;
        for ( size_t i = 0; i < data_size; ++i ) {
            const uint8_t pos = (reg >> 8) ^ data_buffer[i];                /// MSB
            /// low byte goes directly from table
            /// high byte is result of xorring table's high byte and reg's low byte
            reg = (reg << 8) ^ CRC16_LookupTable[ polynomial ][ pos ];
        }
    //     printf( "calculation: poly: 0x%X init: 0x%X xor: 0x%X crc: 0x%X\n", polynomial, init_reg, xor_val, reg ^ xor_val );
        return reg ^ xor_val;    /// & ((1 << 8) - 1)
    }

#endif


uint16_t hw_crc16_calculate_param( const uint8_t* data_buffer, const size_t data_size, 
                                   const uint16_t polynomial, const uint16_t init_reg, const uint16_t xor_val,
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
        return hw_crc16_calculate( data_buffer, data_size, polynomial, init_reg, xor_val );
    } else {
        const uint16_t crc = hw_crc16_calculate( data_copy, data_size, polynomial, init_reg, xor_val );
        free( data_copy );
        return crc;
    }
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
                data.reginit = init_reg;
                data.xorout  = xor_val;
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
