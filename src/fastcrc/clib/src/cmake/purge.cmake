##
## Copy files with subdirectories without deleting target directory before the operation.
##

file( GLOB project_files * )

foreach( file ${project_files} )
    if ( NOT EXISTS ${file} )
        continue()
    endif()

    get_filename_component( file_name ${file} NAME )
    if ( file_name STREQUAL "CMakeCache.txt" )
        continue()
    endif()

    message( STATUS "removing ${file}" )
    file( REMOVE_RECURSE ${file} )
endforeach( file )
