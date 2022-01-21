///

#ifndef VECTOR_H_
#define VECTOR_H_

#include "concat.h"

#include <stddef.h>                             /// NULL, size_t
#include <stdlib.h>                             /// malloc


#define GENERATE_VECTOR_HEADER( VECTOR_TYPE_NAME, ITEM_TYPE_NAME )                                              \
                                                                                                                \
    typedef struct {                                                                                            \
        size_t size;                                                                                            \
        size_t capacity;                                                                                        \
        ITEM_TYPE_NAME* data;                                                                                   \
    } VECTOR_TYPE_NAME;                                                                                         \
                                                                                                                \
    void CONCAT( VECTOR_TYPE_NAME, _init )( VECTOR_TYPE_NAME* array, const size_t capacity );                   \
                                                                                                                \
    VECTOR_TYPE_NAME* CONCAT( VECTOR_TYPE_NAME, _alloc )( const size_t capacity );                              \
                                                                                                                \
    void CONCAT( VECTOR_TYPE_NAME, _free )( VECTOR_TYPE_NAME* array );                                          \
                                                                                                                \
    void CONCAT( VECTOR_TYPE_NAME, _pushback )( VECTOR_TYPE_NAME* array, const ITEM_TYPE_NAME item );           \
                                                                                                                \
    ITEM_TYPE_NAME* CONCAT( VECTOR_TYPE_NAME, _get )( VECTOR_TYPE_NAME* array, const size_t index );


#define GENERATE_VECTOR_BODY( VECTOR_TYPE_NAME, ITEM_TYPE_NAME )                                                \
                                                                                                                \
    void CONCAT( VECTOR_TYPE_NAME, _init )( VECTOR_TYPE_NAME* array, const size_t capacity ) {                  \
        array->size = 0;                                                                                        \
        array->capacity = capacity;                                                                             \
        array->data = malloc( capacity * sizeof(ITEM_TYPE_NAME) );                                              \
    }                                                                                                           \
                                                                                                                \
    VECTOR_TYPE_NAME* CONCAT( VECTOR_TYPE_NAME, _alloc )( const size_t capacity ) {                             \
        VECTOR_TYPE_NAME* array = malloc( sizeof(VECTOR_TYPE_NAME) );                                           \
        CONCAT( VECTOR_TYPE_NAME, _init )( array, capacity );                                                   \
        return array;                                                                                           \
    }                                                                                                           \
                                                                                                                \
    void CONCAT( VECTOR_TYPE_NAME, _free )( VECTOR_TYPE_NAME* array ) {                                         \
        free( array->data );                                                                                    \
        array->capacity = array->size = 0;                                                                      \
        array->data = NULL;                                                                                     \
    }                                                                                                           \
                                                                                                                \
    void CONCAT( VECTOR_TYPE_NAME, _pushback )( VECTOR_TYPE_NAME* array, const ITEM_TYPE_NAME item ) {          \
        if (array->size == array->capacity) {                                                                   \
            if ( array->capacity < 1 ) {                                                                        \
                array->capacity = 1;                                                                            \
            } else {                                                                                            \
                array->capacity *= 2;                                                                           \
            }                                                                                                   \
            /* copies memory if needed */                                                                       \
            array->data = realloc( array->data, array->capacity * sizeof(ITEM_TYPE_NAME) );                     \
        }                                                                                                       \
        array->data[ array->size++ ] = item;                                                                    \
    }                                                                                                           \
                                                                                                                \
    ITEM_TYPE_NAME* CONCAT( VECTOR_TYPE_NAME, _get )( VECTOR_TYPE_NAME* array, const size_t index ) {           \
        return &array->data[ index ];                                                                           \
    }


#endif /* VECTOR_H_ */
