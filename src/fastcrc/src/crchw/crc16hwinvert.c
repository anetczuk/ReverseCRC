///

#include "crc16hwinvert.h"

#include <stdio.h>


GENERATE_VECTOR_BODY( uint16_array, uint16_t )


uint16_array* hw_crc16_invert( const uint8_t* data_buffer, const size_t data_size, const uint16_t polynomial, const uint16_t reg ) {
//     printf( "hw_crc16_invert: %i\n", reg );
    
    uint16_array* reg_list_1 = uint16_array_alloc( 1 );
    uint16_array* reg_list_2 = uint16_array_alloc( 1 );     /// create temporary list
    
    uint16_array_pushback( reg_list_1, reg );
    
    for ( size_t i = 0; i < data_size; ++i ) {
        uint8_t data = data_buffer[i];
        for ( uint8_t j = 0; j < 8; ++j ) {
            const uint8_t data_bit = data & 1;
            data >>= 1;
            
            for ( size_t r = 0; r<reg_list_1->size; ++r ) {
                uint16_t reg_item_one = reg_list_1->data[ r ];
//                 printf("c data: 0x%X %i %i\n", data_buffer[i], data_bit, reg_item_one );
                
                if ( (reg_item_one & 1) == 0 ) {
                    /// shift zero
                    uint16_t reg_item_zero = reg_item_one >> 1;
                    if ( data_bit > 0 ) {
                        reg_item_zero ^= 0x8000;
//                         maybe: reg_item_zero |= 0x8000;
                    }
//                     printf("c pushing 0: 0x%X\n", reg_item_zero );
                    uint16_array_pushback( reg_list_2, reg_item_zero );
                }
                
                /// shift one                
                reg_item_one ^= polynomial;
                if ( (reg_item_one & 1) == 0 ) {
                    /// shift one
                    reg_item_one >>= 1;
                    if ( data_bit == 0 ) {
                        reg_item_one |= 0x8000;
                    } 
//                     printf("c pushing 1: 0x%X\n", reg_item_one );
                    uint16_array_pushback( reg_list_2, reg_item_one );
                }
            }

            if (reg_list_2->size < 1) {
                /// no items to search -- return
                uint16_array_free( reg_list_1 );
                return reg_list_2;
            }

            /// swap buffers
            uint16_array* tmp = reg_list_2;
            reg_list_2 = reg_list_1;
            reg_list_1 = tmp;
            /// clear temporary list
            reg_list_2->size = 0;
        }
    }
    
    uint16_array_free( reg_list_2 );
    return reg_list_1;
}

CRC16ResultArray* hw_crc16_invert_range( const uint8_t* data_buffer, const size_t data_size, const uint16_t crc_num, const uint16_t polynomial, const uint16_t xor_start, const uint16_t xor_end ) {
//     printf( "ccccccccc %i %i %i %i %i\n", data_size, crc_num, polynomial, xor_start, xor_end );
    CRC16ResultArray* result_list = CRC16ResultArray_alloc( 0 );
    for ( uint16_t xor_val=xor_start; xor_val<xor_end; ++xor_val ) {
        const uint16_t crc_raw = crc_num ^ xor_val;
        uint16_array* reg_list = hw_crc16_invert( data_buffer, data_size, polynomial, crc_raw );
        for ( size_t i=0; i<reg_list->size; ++i ) {
            CRC16Result item;
            item.reg = reg_list->data[i];
            item.xor = xor_val;
            CRC16ResultArray_pushback( result_list, item );
        }
        uint16_array_free( reg_list );
    }

    return result_list;
}
