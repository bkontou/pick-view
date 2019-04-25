# pick-view
A supplement to S-SNAP (or any similar picker) to quickly and efficiently view acquired picks and determine their validity

pick-view reads a csv file in the form of:

| net        | sta           | datetime  | phase | orid | arrival_time | lon | lat |
| -----------|:-------------:| ---------:| -----:| ----:| ------------:| ---:| ---:|
| CN     | STA1 | 2018-01-01 23:44:44.444 | P | 20180101001 | 1234 | -115.5 | 55.5 |
| CN     | STA2 | 2018-01-01 23:44:47.123 | S | 20180101001 | 1235 | -155.6 | 55.6 |
