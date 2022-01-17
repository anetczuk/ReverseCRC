///

#ifndef CRCHW_H_
#define CRCHW_H_

#include <stddef.h>                            /// NULL, size_t


typedef unsigned char uint8;


/// =====================================================


typedef struct {
    uint8 reg;              /// registry initial value
    uint8 xor;              /// xor-red result
    uint8 crc;              /// crc
} CRC8Result;

// CRC8Result_init( CRC8Result* data ) {
//     data->reg = 0;
//     data->xor = 0;
// }

typedef struct {
    size_t size;
    size_t capacity;
    CRC8Result* data;
} CRC8ResultArray;

CRC8ResultArray* CRC8ResultArray_alloc( const size_t capacity );

void CRC8ResultArray_init( CRC8ResultArray* array, const size_t capacity );

void CRC8ResultArray_free( CRC8ResultArray* array );

void CRC8ResultArray_pushback( CRC8ResultArray* array, const CRC8Result item );

CRC8Result* CRC8ResultArray_get( CRC8ResultArray* array, const size_t index );


/// =====================================================


/**
 * Calculates CRC starting from least significant bit in first item of data buffer.
 *
 * Compatible with http://www.sunshine2k.de/coding/javascript/crc/crc_js.html
 */
uint8 hw_crc8_calculate( const uint8* data_buffer, const size_t data_size, const uint8 polynomial, const uint8 init_reg, const uint8 xor_val );

CRC8ResultArray* hw_crc8_calculate_range( const uint8* data_buffer, const size_t data_size, const uint8 data_crc, 
                                          const uint8 polynomial, const uint8 init_reg, 
                                          const uint8 xor_start, const uint8 xor_end );


#endif /* CRCHW_H_ */
