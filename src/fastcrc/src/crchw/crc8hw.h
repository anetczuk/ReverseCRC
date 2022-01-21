///

#ifndef CRC8HW_H_
#define CRC8HW_H_

#include "vector.h"

#include <stddef.h>                             /// NULL, size_t
#include <stdint.h>                             /// int types
#include <stdbool.h>                            /// bool


// typedef unsigned char uint8_t;
// typedef unsigned short uint16_t;


/// =====================================================


typedef struct {
    uint8_t reg;              /// registry initial value
    uint8_t xor;              /// xor-red result
} CRC8Result;

// CRC8Result_init( CRC8Result* data ) {
//     data->reg = 0;
//     data->xor = 0;
// }


GENERATE_VECTOR_HEADER( CRC8ResultArray, CRC8Result )


/// =====================================================


/**
 * Calculates CRC starting from least significant bit in first item of data buffer.
 *
 * Compatible with http://www.sunshine2k.de/coding/javascript/crc/crc_js.html
 */
/// 'data_buffer' -- container for data -- first dataframe bit is in MSB of buffer first item
uint8_t hw_crc8_calculate( const uint8_t* data_buffer, const size_t data_size, const uint8_t polynomial, const uint8_t init_reg, const uint8_t xor_val );


uint8_t hw_crc8_calculate_param( const uint8_t* data_buffer, const size_t data_size, 
                                 const uint8_t polynomial, const uint8_t init_reg, const uint8_t xor_val,
                                 const bool reverse_order_flag, const bool reflect_bits_flag );


CRC8ResultArray* hw_crc8_calculate_range( const uint8_t* data_buffer, const size_t data_size, const uint8_t data_crc, 
                                          const uint8_t polynomial, 
                                          const uint8_t init_start, const uint8_t init_end, 
                                          const uint8_t xor_start, const uint8_t xor_end );


#endif /* CRC8HW_H_ */
