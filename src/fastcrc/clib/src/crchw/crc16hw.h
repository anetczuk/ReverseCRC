///

#ifndef CRC16HW_H_
#define CRC16HW_H_

#include "vector.h"

#include <stdint.h>                             /// int types
#include <stdbool.h>                            /// bool


// typedef unsigned char uint8_t;
// typedef unsigned short uint16_t;


/// =====================================================


typedef struct {
    uint16_t reginit;              /// registry initial value
    uint16_t xorout;               /// xor-red result
} CRC16Result;

// CRC16Result_init( CRC16Result* data ) {
//     data->reginit = 0;
//     data->xorout  = 0;
// }


GENERATE_VECTOR_HEADER( CRC16ResultArray, CRC16Result )


/// =====================================================


/**
 * Calculates CRC starting from least significant bit in first item of data buffer.
 *
 * Compatible with http://www.sunshine2k.de/coding/javascript/crc/crc_js.html
 */
/// 'data_buffer' -- container for data -- first dataframe bit is in MSB of buffer first item
uint16_t hw_crc16_calculate( const uint8_t* data_buffer, const size_t data_size, const uint16_t polynomial, const uint16_t init_reg, const uint16_t xor_val );


uint16_t hw_crc16_calculate_param( const uint8_t* data_buffer, const size_t data_size, 
                                   const uint16_t polynomial, const uint16_t init_reg, const uint16_t xor_val,
                                   const bool reverse_order_flag, const bool reflect_bits_flag );


CRC16ResultArray* hw_crc16_calculate_range( const uint8_t* data_buffer, const size_t data_size, const uint16_t data_crc, 
                                            const uint16_t polynomial, 
                                            const uint16_t init_start, const uint16_t init_end, 
                                            const uint16_t xor_start, const uint16_t xor_end );


#endif /* CRC16HW_H_ */
