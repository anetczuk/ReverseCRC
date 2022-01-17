///

#ifndef CRC8HW_H_
#define CRC8HW_H_

#include <stddef.h>                             /// NULL, size_t
#include <stdint.h>                             /// int types


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
/// 'data_buffer' -- container for data -- first dataframe bit is in MSB of buffer first item
uint8_t hw_crc8_calculate( const uint8_t* data_buffer, const size_t data_size, const uint8_t polynomial, const uint8_t init_reg, const uint8_t xor_val );

CRC8ResultArray* hw_crc8_calculate_range( const uint8_t* data_buffer, const size_t data_size, const uint8_t data_crc, 
                                          const uint8_t polynomial, 
                                          const uint8_t init_start, const uint8_t init_end, 
                                          const uint8_t xor_start, const uint8_t xor_end );


#endif /* CRC8HW_H_ */
