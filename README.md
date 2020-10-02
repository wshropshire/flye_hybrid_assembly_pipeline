# flye_hybrid_assembly_pipeline

Consensus bacterial genome assembly pipeline that utilizes the Flye assembler (https://github.com/fenderglass/Flye) with downstream short-read and long-read correction tools to provide contiguous, circularized replicons with low error rates. 

## Author

[William Shropshire](https://twitter.com/The_Real_Shrops)


## Dependencies

* Flye (≥ 2.7)
* BEDtools (≥ 2.29.2)
* VCFtools (≥ 0.1.15)
* berokka (≥ 0.2)
* perl (≥ 5.28.0)
* ncbi-blast+ (≥ 2.10.0)
* Python (≥ 3.6.0)
* MUMmer (≥ 3.23)
* Prodigal (≥ 2.6.3)
* Minimap2 (≥ 2.17-r974)
* Racon (≥ 1.4.5)
* bwa (≥ 0.7.17)
* SAMtools (≥ 1.10)
* Parallel (≥ 201807022)
* BCFtools (≥ 1.10.2)
* htslib (≥ 1.10.2)

Versions above have been tested. Older or newer versions may work, but could create conflicts. Suggestion is to create a virtual environment with these dependencies.

## Input

Required input are: 
(1) out-directory (**outdir**) 
(2) database of *dnaA* genes or other genes of inteerest for orientation (e.g. *repA* genes for plasmids) - (**uniport_dnaA.nucleotides.fa** is provided in this repository
(3) ONT long-reads (either gzip or non-compressed files will work)
(4) Interleaved paired-end short-reads (either gzip or non-compressed files will work)
(5) **genome_size** estimated genome size based on previous knowledge of species (+/- 1 Mb genome size estimate is fine for flye k-mer selection)

Note that you can interleave short-read data using the `bbmap` tool `reformat.sh`. For racon to work properly, make sure there are underscores in lieu of white-space in headers of short-read fastq files by using the `underscore=t` option in `reformat.sh`


## Usage

Usage with Flye assembler:
```
$python3 flye_pipeline.py -t 2 -s sample_name -o outdir -d uniprot_dnaA.nucleotides.fa -pe interleaved_pe_reads.fastq.gz -l long_reads.fastq.gz --genome_size 5.3m
```

Usage for error correction of previously assembled genome:
```
$python3 flye_pipeline.py -t 2 -s sample_name -o outdir -d uniport_dnaA.nucleotides.fa -x -c assembly.fasta -pe interleaved_pe_reads.fastq.gz -l long_reads.fastq.gz
```


