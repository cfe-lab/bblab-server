# Testing Instructions

## Sequencing layout designer

See `sequencing_layout/Sequencing_Layout_template.xlsx` for an example of data
to be used with this tool. Copy the `Sample ID` column (8 rows) into the leftmost
text box and the `Primer` column (8 rows) into the middle text box.

Complete the `User Information` fields, using some `<your_test>` identifier for `Plate ID`.
Then press `Populate`, followed by `Update FROM table`. Leave `Horizontal` selected
in `Layout Parameters`. Then press `Submit`. You should recieve an email with two files:
`<your_test>.plt` and `<your_test>.html`.

The output file data should match `sequencing_layout/sequencing_output.plt` and 
`sequencing_layout/sequencing_output.html`.


## Guava layout designer

Fill the leftmost table with
```
ctrl1
ctrl2
ctrl3
ctrl4
ctrl5
ctrl6
ctrl7
ctrl8
```
And the center table with
```
samp1
samp2
samp3
samp4
samp5
samp6
samp7
samp8
```

Instructions will be in the rightmost table. Using default settings, with `ExperimentID=<your_test>`,
press `Populate`, followed by `Update FROM table`. Then press `Submit`. You should recieve an email 
with two files: `<your_test>.csv` and `<your_test>.html`.


The output file data should match `guava_layout/guava_output.csv` and 
`guava_layout/guava_output.html`.


## Fasta Converter

Upload or copy-and-paste the `test.fasta` file, and you should get a CSV file that matches
`fasta_converter/converted.csv`.

NOTE: the CSV-to-Fasta conversion currently has an issue, which is open in this repo.

## Text-to-Columns

Copy-and-paste the contents of `text_to_columns/ttc_input.csv`, and you should be able to download
a file which matches `text_to_columns/ttc_output.csv`.

NOTE: there is an issue in the current version - if each row in the input file is not the same
length the result will be a `500 Server Error` message. This is fixed in the `test` branch,
as seen here: https://github.com/cfe-lab/bblab-server/issues/2

## False discovery q-value
This tool does not need a test input file. By default, the following values are 
populated in the text field:
```
0.51
0.01
0.12
0.16
0.92
0.16
0.01
0.51
0.62
```
The output file is located in `qvalue/q-values_output.xlsx`

## HXB2 Genome map
No testing should be needed. The page will load, or it won't. The contents shouldn't change.

A copy of the HTML page is located in `HIV_genome/HIV-I HXB2 Genome.html`.

## DNA translator
Copy-and-paste the input file `translate_DNA/test_translate_DNA.fasta` into the text field,
with the default settings, and you should get the output found in 
`translate_DNA/test_translate_DNA_output.txt`.

## Quality Check

The `test.fasta` file, with all analysis entries checked (default), should produce an 
output file which matches `quality_check/quality_check_data_test.xlsx`.

## Unique Sequence Finder

The `test.fasta` file should produce an output file identical to 
`unique_sequence/unique_sequence_data_noduplicate.csv`.

The `unique_sequence/test_duplicate.fasta` file should match 
`unique_sequence/unique_sequence_data_duplicate.csv`.

## Variable function analyzer - doesn't need test data, but save output file
This tool does not need test input data. To test, the following values in the 
page text should be copied into the text input field:
```
A02:26	A03:01:01G	B07:02:01G	B40:01:01G	C03:04:01G	C07:02:01G	0.3
A01:01:01G	A02:01:01G	B08:01:01G	B15:01:01G	C03:04:01G	C07:01:01G	0.7
A01:01:01G	A02:01:01G	B08:01:01G	B57:01:01G	C06:02:01G	C07:01:01G	0.8
A02:01:01G	A03:01:01G	B14:02:01	B15:34	C03:04:01G	C08:02:01	0.3
A02:01:01G	A24:03:01G	B38:01:01	B51:01:01G	C12:03:01G	C14:02:01	0.45
A02:01:01G	A02:01:01G	B14:02:01	B40:01:01G	C03:04:01G	C08:02:01	0.3
A01:01:01G	A01:01:01G	B08:01:01G	B57:01:01G	C06:02:01G	C07:01:01G	0.75
A11:01:01G	A23:01:01G	B07:02:01G	B51:01:01G	C04:01:01G	C15:02:01G	0.2
A01:01:01G	A03:01:01G	B27:05:02G	B57:01:01G	C01:02:01G	C06:02:01G	0.8
A01:01:01G	A02:01:01G	B08:01:01G	B44:02:01G	C02:02:02G	C07:01:01G	0.7
A01:01:01G	A11:01:01G	B08:01:01G	B35:01:01G	C04:01:01G	C07:64	0.9
A02:01:01G	A24:02:01G	B15:01:01G	B15:07:01G	C01:02:01G	C03:03:01G	0.4
A01:01:01G	A25:01:01G	B08:01:01G	B39:01:01G	C07:01:01G	C12:03:01G	0.6
```
The output file is located in `variable_function/variable_function_output.csv`

## Codon-by-Codon
This tool does not need a test input file. By default, the following values are 
populated in the text field:
```
0.786	MGGKWSKRNVVEWPTVRERMRRAEPAADGVGAVSRDLEKHGAITSSNTATNNAACAWLEAQEEEEVGFPVRPQVPLRPMTYRAAVDLSHFLKEKGGLGGLIHSQKRQDILDLWVYHTQGYFPDWQNYTPGPGIRYPLCFGWCFKLVPVEPDKVEEANEGENNSLLHPMSLHGMEDPEGEVLMWKFDSRLAFHHMARELHPEYYKDC
0.982	MGGKWSKSSMVGWPKVRERMRRAEPAADGVGAVSRDLEKHGAITSSNTAANNAACAWLEAQEDEEVGFPVRPQVPLRPMTYKAAIDLSHFLKEKGGLEGLIYSQKRQDILDLWVYHTQGFFPDWQNYTPGPGVRYPLTFGWCFKLVPVDPEKVEEANEGENNSLLHPMSLHGMEDTEKEVLAWRFDSLLAFRHMAREVHPEYYKDC
1.021	MGSKWSKSSVVGWPDVRERMRRAEPAADGVGAVSRDLERHGAITSGNTATNNADCAWLEAQEDEEVGFPVRPQVPLRPMTHRAAMDLSHFLRDKGGLDGLIWSQKRQDILDLWVYHTQGFFPDWQNYTPGPGTRFPLTFGWCFKLVPVELEKVEEANEGENNSLLHPMSQHGMEDPEKEVLAWRFDSRLAFQHMARELHPEYYKDC
0.214	MGGKWSKCSTPGWSTIRERMRRAEPAADGVGPASRDLEKHGALTSSNTAANNAACAWLEAQEEEEVGFPVRPQVPLRPMTYKGALDLSHFLNEKGGLEGLIYSQKRQDILDLWVYNTQGFFPDWQNYTPGPGVRYPLCFGWCFKLVPVESEKVEEATEGENNSLLHPVCLHGMDDPEGEVLVWKFDSKLAFHHMAREMHPEYYKNC
0.467	MGGKWSKCSMGGWPSVRERMRRTEPAAEGVGAASRDLERHGALTSNNTPTNNAACAWLEAQEEEEVGFPVRPQVPLRPMTYKGALDLSHFLKEKGGLEGLVYSQKRQDILDLWVFNTQGFFPDWQGYTPGPGIRYPLTFGWCFKLVPMEPDKVEEANEGENNSLLHPVSLHGMEDPEREVLVWRFDSRLAFRHVAQELHPEYYKNR
0.801	MGGKWSKLS--GWHTIRERMRRAEPAADGVGATSRDLERHGAVTSSNTATNNGACARPEAQENDEVGFPVRPQVPLRPMTFKAAFDLSHFLKEKGGLDGLVYSQKRQEILDLWVYHTQGYLPDWQNYTPGPGTRYPLCFGWCFKLVPMEQEKVEEANEGENNRLLHPISQHGMEDPEREVLVWKFDSSLAFHHRARELHPEFYKDC
```
The output should match the data in `codon_by_codon/test_codon_by_codon.xlsx`.

## Phylodating

Testing instructions for this tool are thoroughly described on the [`Phylodating page`].

[`Phylodating page`]: https://bblab-hivresearchtools.ca/django/tools/phylodating/

## HLA Class(ification Tool)

Use `test.fasta` for this tool, in `Batch Mode`, with `HLA Locus: C`.

The results should match `hla_class/HLA-C batch mode test data OUTPUT.csv`.

If you select `HLA Locus: A` or `B`, you should get an error message about 
invalid sequences (or if in `Single Sequence Mode`, about the length of the sequences.)

## PHAGE-I-Expanded

This tool does not need a test input file. Press `Load Sample` and select `Gag` as `Protein of Interest`.

The output TSV (tab separated values) file should match `phage_i_expanded/phage_i_expanded_results_gag_test.tsv`.

## TCR Distance

TBD - test data pending

## TCR Visualizer

TBD - test data pending