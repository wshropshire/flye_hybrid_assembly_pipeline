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
* Medaka (≥ 0.11.5)
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
(2) ONT long-reads (either gzip or non-compressed files will work)
(3) Interleaved paired-end short-reads (either gzip or non-compressed files will work)
(4) **genome_size** estimated genome size based on previous knowledge of species (+/- 1 Mb genome size estimate is fine for flye k-mer selection)

**Note that paired-end reads MUST be interleaved for racon to work. You can interleave short-read data using the `bbmap` tool `reformat.sh`. For racon to work properly, make sure there are underscores in lieu of white-space in headers of short-read fastq files by using the `underscore=t` option in `reformat.sh`**

## Usage

Usage with Flye assembler:
```
$python3 flye_pipeline.py -t 2 -s sample_name -o outdir -pe interleaved_pe_reads.fastq.gz -l long_reads.fastq.gz --genome_size 5.3m -d dnaA_file.fasta
```

Usage for error correction of previously assembled genome:
```
$python3 flye_pipeline.py -t 2 -s sample_name -o outdir -x -c assembly.fasta -pe interleaved_pe_reads.fastq.gz -l long_reads.fastq.gz -d dnaA_file.fasta
```

## Output

Final assembly can be found in `outdir_name/shortRead_polish_results/` and will be named **SAMPLENAME_final.fasta**

## Usage tips

(1) Note that any database of genes of interest to orient contigs can be used for the purposes of orienting any linear or circular DNA structure when using the `-d` paramter in pipeline. For example, if assembling *K. pneumoniae* genomes, one can use the manually curated, database of commonly observed F-type replication initiation protein genes found in plasmids as well as the *dnaA* gene for *K. pneumoniae* in the db directory with the file name **dnaA_and_plasmid_startSites.fasta**. 

If one wants to use `--meta` and `--plasmid` options for their flye assemblies, please use the `-mp` argument in the pipeline. 

