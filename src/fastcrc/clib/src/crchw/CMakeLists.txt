#
#
#

set( TARGET_NAME fastcrc )


set( EXT_LIBS  )


file(GLOB_RECURSE cpp_files *.c )


add_custom_command(
    OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/crc8lookup.h
    COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/generate_lookup8.py ARGS --silent
    DEPENDS generate_lookup8.py
)

add_custom_command(
    OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/crc16lookup.h
    COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/generate_lookup16.py ARGS --silent
    DEPENDS generate_lookup16.py
)


add_library( ${TARGET_NAME} SHARED ${cpp_files} ${CMAKE_CURRENT_SOURCE_DIR}/crc8lookup.h ${CMAKE_CURRENT_SOURCE_DIR}/crc16lookup.h )
target_link_libraries( ${TARGET_NAME} ${EXT_LIBS} )


install( TARGETS ${TARGET_NAME} DESTINATION "." )
