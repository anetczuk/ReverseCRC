## ReverseCRC
Finding polynomial, init and xor values of CRC.


### Algorithms

Repository contains followint implementations of CRC:
* _DivisionCRC_ - standard shift register implementation,
* _HwCRC_ - implementation popular in hardware (according to Wikipedia),
* _LookupCRC_ - implementation based on lookup tables,
* _ModCRC_ - implementation compatible with _crcmod_ library.

_DivisionCRC_ and _HwCRC_ have its backward versions which allows to find polynomials from input messages.


### Running

For run parameters execute `src/find.sh --help`

Running computation: `src/find.sh --file in.txt --outfile results.txt --mode BF_PAIRS --algo MOD`

Example of *in.txt* file:
`#comment
0020FCFF 11
0120FCFF 8C
0220FCFF 36
`
where first hex number in row is data and second number is calculated CRC.


### Code features examples

Following techniques were used in the project:
* Unit testing 
* Code profiling (cProfile)
* Code coverage (Coverage.py)


#### Profiler

To run main application it needs to run one of following comands:
* *find.sh {params} --profile*
* *find.sh {params} --pfile={output file}*

In first case output will be displayed on stdout. In second case output will be stored inside *{output file}*. 

Tests can be run with profiler by one of following commands:
* *test_runner.py {params} --profile*
* *test_runner.py {params} --pfile={output file}*


#### Code coverage

Executing application with code coverage can be done by following call: *find.sh {params} --coverage*.

After the call _htmlcov_ directory will be created inside run directory.

Running code coverage on tests is done by *test_runner.py*.

Call command: *test_runner.py --coverage*.

As a result *htmlcov* directory will be created inside run directory.



### References

* https://en.wikipedia.org/wiki/Cyclic_redundancy_check - general description of CRC algorithm,
* https://en.wikipedia.org/wiki/Computation_of_cyclic_redundancy_checks - general description of CRC algorithm,
* http://www.sunshine2k.de/articles/coding/crc/understanding_crc.html - description of CRC algorithm,
* http://www.infradead.org/~mchehab/kernel_docs/unsorted/crc32.html - opimised shift register algorithm,
* http://www.cosc.canterbury.ac.nz/greg.ewing/essays/CRC-Reverse-Engineering.html - reverse engineering of CRC.
