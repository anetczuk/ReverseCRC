///

#ifndef CRC16HW_INVERT_H_
#define CRC16HW_INVERT_H_

#include "crc16hw.h"


GENERATE_VECTOR_HEADER( uint16_array, uint16_t )


uint16_array* hw_crc16_invert( const uint8_t* data_buffer, const size_t data_size, const uint16_t polynomial, const uint16_t reg );


CRC16ResultArray* hw_crc16_invert_range( const uint8_t* data_buffer, const size_t data_size, const uint16_t crc_num, const uint16_t polynomial, const uint16_t xor_start, const uint16_t xor_end );


#endif /* CRC16HW_INVERT_H_ */
