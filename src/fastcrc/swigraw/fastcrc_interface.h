
#include <stdbool.h>                            /// bool
#include <stdint.h>                             /// int types


typedef struct {
    uint8_t reginit;              /// registry initial value
    uint8_t xorout;               /// xor-red result
} CRC8Result;

typedef struct {                                                                                            
    size_t size;                                                                                            
    size_t capacity;                                                                                        
    CRC8Result* data;                                                                                   
} CRC8ResultArray; 


CRC8Result* CRC8ResultArray_getptr( CRC8ResultArray* array, const size_t index );

void CRC8ResultArray_free( CRC8ResultArray* array );


/// ===============================================


uint8_t hw_crc8_calculate( const uint8_t* data_buffer, const size_t data_size, const uint8_t polynomial, const uint8_t init_reg, const uint8_t xor_val );


uint8_t hw_crc8_calculate_param( const uint8_t* data_buffer, const size_t data_size, 
                                 const uint8_t polynomial, const uint8_t init_reg, const uint8_t xor_val,
                                 const bool reverse_order_flag, const bool reflect_bits_flag );


CRC8ResultArray* hw_crc8_calculate_range( const uint8_t* data_buffer, const size_t data_size, const uint8_t data_crc, 
                                          const uint8_t polynomial, 
                                          const uint8_t init_start, const uint8_t init_end, 
                                          const uint8_t xor_start, const uint8_t xor_end );


/// ==============================================================================================
/// ==============================================================================================


typedef struct {
    uint16_t reginit;              /// registry initial value
    uint16_t xorout;               /// xor-red result
} CRC16Result;

typedef struct {                                                                                            
    size_t size;                                                                                            
    size_t capacity;                                                                                        
    CRC16Result* data;                                                                                   
} CRC16ResultArray; 

CRC16Result* CRC16ResultArray_getptr( CRC16ResultArray* array, const size_t index );

void CRC16ResultArray_free( CRC16ResultArray* array );


/// ===============================================


uint16_t hw_crc16_calculate( const uint8_t* data_buffer, const size_t data_size, const uint16_t polynomial, const uint16_t init_reg, const uint16_t xor_val );


uint16_t hw_crc16_calculate_param( const uint8_t* data_buffer, const size_t data_size, 
                                   const uint16_t polynomial, const uint16_t init_reg, const uint16_t xor_val,
                                   const bool reverse_order_flag, const bool reflect_bits_flag );


CRC16ResultArray* hw_crc16_calculate_range( const uint8_t* data_buffer, const size_t data_size, const uint16_t data_crc, 
                                            const uint16_t polynomial, 
                                            const uint16_t init_start, const uint16_t init_end, 
                                            const uint16_t xor_start, const uint16_t xor_end );


/// ==============================================================================================
/// ==============================================================================================


typedef struct {                                                                                            
    size_t size;                                                                                            
    size_t capacity;                                                                                        
    uint16_t* data;                                                                                   
} uint16_array; 

    
uint16_t uint16_array_getvalue( uint16_array* array, const size_t index );

void uint16_array_free( uint16_array* array );


/// ===============================================


uint16_array* hw_crc16_invert( const uint8_t* data_buffer, const size_t data_size, const uint16_t polynomial, const uint16_t reg );


CRC16ResultArray* hw_crc16_invert_range( const uint8_t* data_buffer, const size_t data_size, const uint16_t crc_num, const uint16_t polynomial, const uint16_t xor_start, const uint16_t xor_end );
