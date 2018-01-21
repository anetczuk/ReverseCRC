## ReverseCRC
Finding polynomial, init and xor values of CRC.


### Algorithms

Repository contains followint implementations of CRC:
* _DivisionCRC_ - standard shift register implementation,
* _HwCRC_ - implementation popular in hardware (according to Wikipedia),
* _LookupCRC_ - implementation based on lookup tables,
* _ModCRC_ - implementation compatible with _crcmod_ library.

_DivisionCRC_ and _HwCRC_ have its backward versions which allows to find polynomials from input messages.


### Code additional features

Following techniques were used in the project:
* Unit testing 
* Code profiling (cProfile)
* Code coverage (Coverage.py)


### References

* https://en.wikipedia.org/wiki/Cyclic_redundancy_check - general description of CRC algorithm
* https://en.wikipedia.org/wiki/Computation_of_cyclic_redundancy_checks - general description of CRC algorithm
* http://www.sunshine2k.de/articles/coding/crc/understanding_crc.html - 
* http://www.infradead.org/~mchehab/kernel_docs/unsorted/crc32.html - opimised shift register algorithm,
* http://www.cosc.canterbury.ac.nz/greg.ewing/essays/CRC-Reverse-Engineering.html - reverse engineering of CRC.
