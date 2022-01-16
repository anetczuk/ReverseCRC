///

#include "crchw.h"

// #include <stdio.h>


/**
 * Implementation based on:
 *      https://en.wikipedia.org/wiki/Computation_of_cyclic_redundancy_checks
 *      http://www.sunshine2k.de/articles/coding/crc/understanding_crc.html
 *
 * Performance can be improved by replacing inner loop with "lookup table" for all 256 combinations of "reg" for each polynomial.
 * It can be especially beneficial if the polynomial is fixed or handling large input data.
 */
uint8 hw_crc8_calculate( const uint8* data_buffer, const size_t data_size, const uint8 polynomial, const uint8 init_reg, const uint8 xor_val ) {
    uint8 reg = init_reg;
    for ( size_t i = 0; i < data_size; ++i ) {
        reg ^= data_buffer[i];
        for ( size_t j = 0; j < 8; ++j ) {
            if ( (reg & 0x80) != 0 ) {
                reg = (reg << 1) ^ polynomial;
            } else {
                reg <<= 1;
            }
        }
    }
    return reg ^ xor_val;    /// & ((1 << 8) - 1)
}
