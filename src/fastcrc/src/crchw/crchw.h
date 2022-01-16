///

#ifndef CRCHW_H_
#define CRCHW_H_

#include <stddef.h>                            /// NULL, size_t


typedef unsigned char uint8;


/**
 * Calculates CRC starting from least significant bit in first item of data buffer.
 *
 * Compatible with http://www.sunshine2k.de/coding/javascript/crc/crc_js.html
 */
uint8 hw_crc8_calculate( const uint8* data_buffer, const size_t data_size, const uint8 polynomial, const uint8 init_reg, const uint8 xor_val );

#endif /* CRCHW_H_ */
