///

#ifndef CRC16HW_H_
#define CRC16HW_H_

#include <stddef.h>                             /// NULL, size_t
#include <stdint.h>                             /// int types


// typedef unsigned char uint8_t;
// typedef unsigned short uint16_t;


/// =====================================================


typedef struct {
    uint16_t reg;              /// registry initial value
    uint16_t xor;              /// xor-red result
} CRC16Result;

// CRC16Result_init( CRC16Result* data ) {
//     data->reg = 0;
//     data->xor = 0;
// }

typedef struct {
    size_t size;
    size_t capacity;
    CRC16Result* data;
} CRC16ResultArray;

CRC16ResultArray* CRC16ResultArray_alloc( const size_t capacity );

void CRC16ResultArray_init( CRC16ResultArray* array, const size_t capacity );

void CRC16ResultArray_free( CRC16ResultArray* array );

void CRC16ResultArray_pushback( CRC16ResultArray* array, const CRC16Result item );

CRC16Result* CRC16ResultArray_get( CRC16ResultArray* array, const size_t index );


/// =====================================================


/**
 * Calculates CRC starting from least significant bit in first item of data buffer.
 *
 * Compatible with http://www.sunshine2k.de/coding/javascript/crc/crc_js.html
 */
/// 'data_buffer' -- container for data -- first dataframe bit is in MSB of buffer first item
uint16_t hw_crc16_calculate( const uint8_t* data_buffer, const size_t data_size, const uint16_t polynomial, const uint16_t init_reg, const uint16_t xor_val );

CRC16ResultArray* hw_crc16_calculate_range( const uint8_t* data_buffer, const size_t data_size, const uint16_t data_crc, 
                                            const uint16_t polynomial, 
                                            const uint16_t init_start, const uint16_t init_end, 
                                            const uint16_t xor_start, const uint16_t xor_end );


#endif /* CRC16HW_H_ */
