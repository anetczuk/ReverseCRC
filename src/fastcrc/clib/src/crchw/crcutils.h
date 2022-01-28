///

#ifndef CRCUTILS_H_
#define CRCUTILS_H_

#include <stddef.h>                             /// NULL, size_t
#include <stdint.h>                             /// int types


// typedef unsigned char uint8_t;
// typedef unsigned short uint16_t;


/// reverse order of bytes in array
inline void reverse_order( uint8_t* data_buffer, const size_t data_size ) {
    const size_t half = data_size / 2;
    for ( size_t i=0; i<half; ++i ) {
        const size_t other = data_size - 1 - i;
        const size_t temp = data_buffer[ i ];
        data_buffer[ i ] = data_buffer[ other ];
        data_buffer[ other ] = temp;
    }
}


/// reverse order of bits in byte
inline uint8_t reflect_bits( uint8_t data ) {
    data = (data & 0xF0) >> 4 | (data & 0x0F) << 4;
    data = (data & 0xCC) >> 2 | (data & 0x33) << 2;
    data = (data & 0xAA) >> 1 | (data & 0x55) << 1;
    return data;
}

inline void reflect_bits_array( uint8_t* data_buffer, const size_t data_size ) {
    for ( size_t i=0; i<data_size; ++i ) {
        data_buffer[ i ] = reflect_bits( data_buffer[ i ] );
    }
}


#endif /* CRCUTILS_H_ */
