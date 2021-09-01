#!/usr/bin/env python

import os
import subprocess
import argparse
import fix_repeats

"""Notes for an eventual protocol for this pipeline"""
# Note that you need a local install of flye to properly run the make_flye_command() function.
# Note that you need a local install of berokka to properly run the make_berokka_command() function.
# Note that you need a local install of circlator to properly run the circlator_fixstart_command() function.
# Note that you need a local install of bwa to properly run the racon_command() function.
# Note that you need a local install of racon to properly run the racon_command() function.
# Note that you need a local install of minimap2 to properly run the minimap2_command() function.
# Note that you need a local install of medaka to properly run the medaka_command() function. Note that this only runs
# in <Python3.7 as version of tensorflow not supported by medaka. Other installation issues so be sure to check
# GitHub page if problems with running (e.g. readlink -f not supported by iOS, need to download coreutils v8.25). If
# errors persist

# Common Functions -- Future pipeline will likely create a separate common module where these functions
# could be separated into common classes.

# create_directory() accepts one absolute or relative output directory, 'outdir', that makes directory for output files
# if that current directory doesn't exist for the purposes of not accidentally removing a prior directory.
def create_directory(outdir):
    """Function to create the output directory"""
    if os.path.isdir(outdir):
        raise Exception("Directory already exists")
    if not os.path.isdir(outdir):
        os.system("mkdir -p %s" % outdir)
    return

# make_flye_command() passes 7 arguments, creates a simple flye command to be executed through the os by the subprocess
# module, and sends output into the outdir provided in the command prompt.

def make_flye_command(flye_path, long_reads, outdir, sample_name, threads):
    # Fix the random seed so the program produces the same output every time it's run.
    # random.seed(1987)
    # Note, in order to use subprocess, you cannot use integer or float arguments, thus all arguments passed to subprocess
    # must be strings
    flye_cmd = [flye_path, "--nano-raw", long_reads, "-o", "{0}/flye_assembly".format(outdir), "--threads", threads]
    print("Performing Flye Assembly")
    subprocess.run(flye_cmd)
    print("Flye Assembly Finished")
    flye_directory = "{0}/flye_assembly".format(outdir)
    return flye_directory

def make_flye_command_alt(flye_path, long_reads, outdir, sample_name, threads):
    # Fix the random seed so the program produces the same output every time it's run.
    # random.seed(1987)
    # Note, in order to use subprocess, you cannot use integer or float arguments, thus all arguments passed to subprocess
    # must be strings
    flye_cmd = [flye_path, "--nano-raw", long_reads, "-o", "{0}/flye_assembly".format(outdir), "--plasmids", "--meta", "--threads", threads]
    print("Performing Flye Assembly")
    subprocess.run(flye_cmd)
    print("Flye Assembly Finished")
    flye_directory = "{0}/flye_assembly".format(outdir)
    return flye_directory

# simple execution of berokka through subprocess module
def make_berokka_command(berokka_path, infile, outdir):
    berokka_command = [berokka_path, infile, '--outdir', '{0}/berokka_results'.format(outdir)]
    subprocess.run(berokka_command)
    return


def make_minimap2_command(minimap2_path, reference, long_reads, threads, outdir, racon_polish_number):
    minimap2_cmd = ['{0}'.format(minimap2_path), '-t', threads, '-ax', 'map-ont', reference, long_reads]
    result = subprocess.run(minimap2_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    minimap2 = result.stdout.decode('utf-8')
    minimap2_align = "{0}/align_{1}.sam".format(outdir, racon_polish_number)
    minimap2_align_file = open(minimap2_align, 'w')
    minimap2_align_file.write(minimap2)
    minimap2_align_file.close()
    return


def make_racon_longRead_command(racon_path, long_reads, overlaps, target_sequences, outdir,
                                sample_name, threads, racon_polish_number):
    racon_cwd = ['{0}'.format(racon_path), '-t', threads, '-m', '8', '-x', '-6', '-g', '-8', '-w', '500',
                 long_reads, overlaps, target_sequences]
    result = subprocess.run(racon_cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    racon = result.stdout.decode('utf-8')
    racon_fasta = "{0}/longRead_polish_results/{1}_racon{2}.fasta".format(outdir, sample_name, racon_polish_number)
    racon_fasta_file = open(racon_fasta, 'w')
    racon_fasta_file.write(racon)
    racon_fasta_file.close()
    return


# circlator fixstart execution through subprocess module
def make_circlator_fixstart_command(circlator_path, dnaA_file, infile, sample_name):
    circlator_fixstart_command = [circlator_path, 'fixstart', '--genes_fa', dnaA_file, infile, sample_name, '--verbose']
    subprocess.run(circlator_fixstart_command)
    return


def make_circlator_clean_command(circlator_path, infile, sample_name):
    circlator_clean_command = [circlator_path, 'clean', '--min_contig_length', '500', '--verbose', infile, sample_name]
    subprocess.run(circlator_clean_command)
    return


# Need to make an alignment tool class
# Need to make a polish tool class

def make_medaka_command(medaka_path, long_reads, contigs, outdir, threads):
# Note that the '-m' parameter is important to specify since medaka polishing is based on training the algorithm on particular
# Guppy basecalling algorithms.
# Add This '-m' parameter as arugment and set 'r941_min_high' as default, which is the medaka default as well and what
# we usually use to train our algorithms.
    medaka_cmd = ['{0}'.format(medaka_path), '-i', long_reads, '-d', contigs, '-o',
                  '{0}/medaka_results'.format(outdir), '-m', 'r941_min_high_g360', '-t', threads]
    subprocess.run(medaka_cmd)
    return


def make_bwa_command(bwa_path, assembly_reference, pe_reads, outdir, threads, racon_polish_number):
    print("Indexing assembly reference for bwa alignment")
    bwa_index_cmd = ['{0}'.format(bwa_path), 'index', assembly_reference]
    subprocess.run(bwa_index_cmd)
    print("bwa-mem alignment with assembly reference and paired-end short-reads")
    bwa_align_cmd = ['{0}'.format(bwa_path), 'mem', '-t', threads, '-o',
                     '{0}/align_{1}.sam'.format(outdir, racon_polish_number), assembly_reference, pe_reads]
    subprocess.run(bwa_align_cmd)
    return


def make_racon_shortRead_command(racon_path, pe_reads, overlaps, target_sequences, outdir, sample_name,
                                 threads, racon_polish_number):
    racon_cwd = ['{0}'.format(racon_path), '-t', threads, pe_reads, overlaps, target_sequences]
    result = subprocess.run(racon_cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    racon = result.stdout.decode('utf-8')
    racon_fasta = "{0}/shortRead_polish_results/{1}_racon{2}.fasta".format(outdir, sample_name, racon_polish_number)
    racon_fasta_file = open(racon_fasta, 'w')
    racon_fasta_file.write(racon)
    racon_fasta_file.close()
    return


def get_arguments():
    """Parse assembler arguments"""
    parser = argparse.ArgumentParser(description="ONT plus Illumina consensus assembler", add_help=False)

    # Help arguments
    help_group = parser.add_argument_group("Help")
    help_group.add_argument('-h', '--help', action='help', help='Show this help message and exit')
    help_group.add_argument('-V', '--version', action='version', version='%(prog)s version 0.6',
                            help="Show Assembler's version number")

    # input_arguments
    input_group = parser.add_argument_group("Inputs")
    input_group.add_argument('-pe', '--pe_reads', required=True, help='interleave paired-end reads', type=str,
                             default=None)
    input_group.add_argument('-l', '--long_reads', required=True, help="Path to the ONT long reads", type=str,
                             default=None)
    input_group.add_argument('-d', '--dnaA_file', required=False, help="dnaA (default) start sites", type=str,
                            default=None)
    input_group.add_argument('-o', '--outdir', required=True, help="Name of the output directory", type=str,
                                default=None)
    
    # Optional arguments
    optional_group = parser.add_argument_group("Optional inputs")
    optional_group.add_argument('-s', '--sample_name', required=False, help="Name of the sample to use in the "
                                "outdir/outfiles as prefix", type=str, default='SAMPLE')
    optional_group.add_argument('-mp', help="add \'meta\' and \'plasmid\' Flye options", action ='store_true')
    optional_group.add_argument('-x', '--existing_contigs', required=False, action="store_true",
                             help='indicate if existing contigs are going to be used from previous assembly.',
                             default=False)
    optional_group.add_argument('-c', '--contigs', required=False, help="existing contigs fasta file", type=str,
                             default=None)
    optional_group.add_argument('-t', '--threads', required=False, help="Number of threads to run program", type=str,
                                default='1')
    # Pipeline arguments
    pipeline_group = parser.add_argument_group("Pipeline Arguments")
    pipeline_group.add_argument('--flye_path', required=False, help="Path to flye executable; please use \'flye\' if"
                                "with path", type=str, default='flye')
    pipeline_group.add_argument('--berokka_path', required=False, help="Path to berokka executable. Please use "
                                "\'berokka\' with path", type=str, default='berokka')
    pipeline_group.add_argument('--circlator_path', required=False, help="Path to circlator executable; "
                                "only for use to fix start position. Please use \'circlator\' in the pathway",
                                type=str, default='circlator')
    pipeline_group.add_argument('--minimap2_path', required=False, help='Path to minimap2 executable. Need to include'
                                '\'minimap2\' in pathway', type=str, default='minimap2')
    pipeline_group.add_argument('--bwa_path', required=False, help="Path to bwa executable. Please use \'bwa\' in "
                                "the pathway if provided", type=str, default='bwa')
    pipeline_group.add_argument('--racon_path', required=False, help='Path to racon executable. Please use'
                                '\'racon\' in the pathway', type=str, default='racon')
    pipeline_group.add_argument('--medaka_path', required=False, help='Path to medaka executable. Please use'
                                '\'medaka_consensus\' in the pathway', type=str, default='medaka_consensus')


    args = parser.parse_args()
    return args


# Main function that takes argparse arguments and can be passed via a command line prompt.
def run_conditions():
    args = get_arguments()
    long_reads = args.long_reads
    outdir = args.outdir
    sample_name = args.sample_name
    threads = args.threads
    pe_reads = args.pe_reads
    create_directory(args.outdir)
    dir = os.path.dirname(__file__)
    default_db = os.path.join(dir, './../db/uniprot_dnaA.nucleotides.fa')

    # conditional argument that executes assembly + circularization check
    if not args.existing_contigs:
        if args.mp is True:
            make_flye_command_alt(args.flye_path, long_reads, outdir, sample_name, threads)
            os.system("mv %s %s" % ("{0}/flye_assembly/assembly.fasta".format(outdir, sample_name),
                                    "{0}/flye_assembly/{1}_assembly.fasta".format(outdir, sample_name)))
            infile0 = "{0}/flye_assembly/{1}_assembly.fasta".format(outdir, sample_name)
        else:
            make_flye_command(args.flye_path, long_reads, outdir, sample_name, threads)
            os.system("mv %s %s" % ("{0}/flye_assembly/assembly.fasta".format(outdir, sample_name),
                                "{0}/flye_assembly/{1}_assembly.fasta".format(outdir, sample_name)))
            infile0 = "{0}/flye_assembly/{1}_assembly.fasta".format(outdir, sample_name)
        print("Circularization check with berokka and creating input for long-read initial round of polishing")
        make_berokka_command(args.berokka_path, infile0, args.outdir)
        infile1 = "{0}/berokka_results/02.trimmed.fa".format(outdir)
        print("Removing potential self-contained contigs")
        circlator_clean_outfile_prefix = "{0}/berokka_results/{1}_clean".format(outdir, sample_name)
        make_circlator_clean_command(args.circlator_path, infile1, circlator_clean_outfile_prefix)
        infile2 = "{0}/berokka_results/{1}_clean.fasta".format(outdir, sample_name)
        print("Performing iterative long-read polishes with contig turning using Circlator Fixstart")
        print("Perform Racon Polish #1")
        longRead_outdir = '{0}/longRead_polish_results'.format(outdir)
        create_directory(longRead_outdir)
        racon1_polish = 1
        make_minimap2_command(args.minimap2_path, infile2, long_reads, threads, longRead_outdir, racon1_polish)
        sam_file1 = '{0}/longRead_polish_results/align_{1}.sam'.format(outdir, racon1_polish)
        make_racon_longRead_command(args.racon_path, long_reads, sam_file1, infile2, outdir, sample_name, threads,
                                    racon1_polish)
        infile3 = "{0}/longRead_polish_results/{1}_racon{2}.fasta".format(outdir, sample_name, racon1_polish)
        os.system('rm -r %s' % sam_file1)
        print("Executing Circlator Fixstart to obtain start position(s)")
        circlator_outfile_prefix = "{0}/longRead_polish_results/{1}_circlator".format(outdir, sample_name)
        circlator_outfile = "{0}/longRead_polish_results/{1}_circlator.fasta".format(outdir, sample_name)
        if args.dnaA_file is None:
            make_circlator_fixstart_command(args.circlator_path, default_db, infile3, circlator_outfile_prefix)
        else:
            make_circlator_fixstart_command(args.circlator_path, args.dnaA_file, infile3, circlator_outfile_prefix)
        print("Perform Racon Polish #2")
        racon2_polish = 2
        make_minimap2_command(args.minimap2_path, circlator_outfile, long_reads, threads, longRead_outdir,
                              racon2_polish)
        sam_file2 = '{0}/longRead_polish_results/align_{1}.sam'.format(outdir, racon2_polish)
        make_racon_longRead_command(args.racon_path, long_reads, sam_file2, circlator_outfile, outdir, sample_name,
                                    threads, racon2_polish)
        os.system('rm -r %s' % sam_file2)
        print("Perform long read polishes with Medaka")
        medaka_input = "{0}/longRead_polish_results/{1}_racon{2}.fasta".format(outdir, sample_name, racon2_polish)
        make_medaka_command(args.medaka_path, long_reads, medaka_input, outdir, threads)
        print("Executing shortRead polishes with Racon")
        infile4 = "{0}/medaka_results/consensus.fasta".format(outdir)
        shortRead_polish_outdir = "{0}/shortRead_polish_results".format(outdir)
        create_directory(shortRead_polish_outdir)
        racon3_polish = 3
        make_bwa_command(args.bwa_path, infile4, pe_reads, shortRead_polish_outdir, threads, racon3_polish)
        print("Executing Racon for third round of polishing")
        sam_file3 = "{0}/shortRead_polish_results/align_{1}.sam".format(outdir, racon3_polish)
        make_racon_shortRead_command(args.racon_path, pe_reads, sam_file3, infile4, outdir, sample_name,
                                     threads, racon3_polish)
        os.system('rm -r %s' % sam_file3)
        infile5 = "{0}/shortRead_polish_results/{1}_racon{2}.fasta".format(outdir, sample_name, racon3_polish)
        print("Executing circulating fixstart to rotate #2 and orient properly")
        circlator_outfile_prefix2 = "{0}/shortRead_polish_results/{1}_circlator2".format(outdir, sample_name)
        circlator_outfile2 = "{0}/shortRead_polish_results/{1}_circlator2.fasta".format(outdir, sample_name)
        if args.dnaA_file is None:
            make_circlator_fixstart_command(args.circlator_path, default_db, infile5, circlator_outfile_prefix2)
        else:
            make_circlator_fixstart_command(args.circlator_path, args.dnaA_file, infile5, circlator_outfile_prefix2)
        print("Executing Racon for fourth round of polishing")
        racon4_polish = 4
        make_bwa_command(args.bwa_path, circlator_outfile2, pe_reads, shortRead_polish_outdir, threads, racon4_polish)
        sam_file4 = "{0}/shortRead_polish_results/align_{1}.sam".format(outdir, racon4_polish)
        make_racon_shortRead_command(args.racon_path, pe_reads, sam_file4, circlator_outfile2, outdir, sample_name,
                                     threads, racon4_polish)
        os.system('rm -r %s' % sam_file4)
        infile6 = "{0}/shortRead_polish_results/{1}_racon{2}.fasta".format(outdir, sample_name, racon4_polish)
        print("Executing fix repeat script for final assembly")
        subprocess.Popen("sed '/^>/ s/ .*//' -i " + infile6, shell=True).wait()
        subprocess.Popen('bwa index ' + infile6, shell=True).wait()
        bam_infile6 = "{0}/shortRead_polish_results/{1}_racon{2}_sort.bam".format(outdir, sample_name, racon4_polish)
        subprocess.Popen('bwa mem -t ' + threads + ' ' + infile6 + ' ' + pe_reads + \
                         ' | samtools sort -@ ' + threads + ' > ' + bam_infile6, shell=True).wait()
        coverage_file = "{0}/shortRead_polish_results/coverage.txt".format(outdir)
        subprocess.Popen('bedtools genomecov -d -ibam ' + bam_infile6 + ' > ' + coverage_file, shell=True).wait()
        infile7 = "{0}/shortRead_polish_results/{1}_final.fasta".format(outdir, sample_name)
        tmp_directory = "{0}/shortRead_polish_results/tmp".format(outdir)
        os.makedirs(tmp_directory)
        read_length = 300
        fix_repeats.correct_regions(infile6, pe_reads, coverage_file, tmp_directory, infile7, read_length, threads)
        os.system('rm -r %s' % tmp_directory)
        print("Fin! Enjoy your day!")
    if args.existing_contigs:
        print("Circularization check with berokka and creating input for long-read initial round of polishing")
        make_berokka_command(args.berokka_path, args.contigs, args.outdir)
        infile1 = "{0}/berokka_results/02.trimmed.fa".format(outdir)
        print("Removing potential self-contained contigs")
        circlator_clean_outfile_prefix = "{0}/berokka_results/{1}_clean".format(outdir, sample_name)
        make_circlator_clean_command(args.circlator_path, infile1, circlator_clean_outfile_prefix)
        infile2 = "{0}/berokka_results/{1}_clean.fasta".format(outdir, sample_name)
        print("Performing iterative long-read polishes with contig turning using Circlator Fixstart")
        print("Perform Racon Polish #1")
        longRead_outdir = '{0}/longRead_polish_results'.format(outdir)
        create_directory(longRead_outdir)
        racon1_polish = 1
        make_minimap2_command(args.minimap2_path, infile2, long_reads, threads, longRead_outdir, racon1_polish)
        sam_file1 = '{0}/longRead_polish_results/align_{1}.sam'.format(outdir, racon1_polish)
        make_racon_longRead_command(args.racon_path, long_reads, sam_file1, infile2, outdir, sample_name, threads,
                                    racon1_polish)
        infile3 = "{0}/longRead_polish_results/{1}_racon{2}.fasta".format(outdir, sample_name, racon1_polish)
        os.system('rm -r %s' % sam_file1)
        print("Executing Circlator Fixstart to obtain start position(s)")
        circlator_outfile_prefix = "{0}/longRead_polish_results/{1}_circlator".format(outdir, sample_name)
        circlator_outfile = "{0}/longRead_polish_results/{1}_circlator.fasta".format(outdir, sample_name)
        if args.dnaA_file is None:
            make_circlator_fixstart_command(args.circlator_path, default_db, infile3, circlator_outfile_prefix)
        else:
            make_circlator_fixstart_command(args.circlator_path, args.dnaA_file, infile3, circlator_outfile_prefix)
        print("Perform Racon Polish #2")
        racon2_polish = 2
        make_minimap2_command(args.minimap2_path, circlator_outfile, long_reads, threads, longRead_outdir,
                              racon2_polish)
        sam_file2 = '{0}/longRead_polish_results/align_{1}.sam'.format(outdir, racon2_polish)
        make_racon_longRead_command(args.racon_path, long_reads, sam_file2, circlator_outfile, outdir, sample_name,
                                    threads, racon2_polish)
        os.system('rm -r %s' % sam_file2)
        print("Perform long read polishes with Medaka")
        medaka_input = "{0}/longRead_polish_results/{1}_racon{2}.fasta".format(outdir, sample_name, racon2_polish)
        make_medaka_command(args.medaka_path, long_reads, medaka_input, outdir, threads)
        print("Executing shortRead polishes with Racon")
        infile4 = "{0}/medaka_results/consensus.fasta".format(outdir)
        shortRead_polish_outdir = "{0}/shortRead_polish_results".format(outdir)
        create_directory(shortRead_polish_outdir)
        racon3_polish = 3
        make_bwa_command(args.bwa_path, infile4, pe_reads, shortRead_polish_outdir, threads, racon3_polish)
        print("Executing Racon for third round of polishing")
        sam_file3 = "{0}/shortRead_polish_results/align_{1}.sam".format(outdir, racon3_polish)
        make_racon_shortRead_command(args.racon_path, pe_reads, sam_file3, infile4, outdir, sample_name,
                                     threads, racon3_polish)
        os.system('rm -r %s' % sam_file3)
        infile5 = "{0}/shortRead_polish_results/{1}_racon{2}.fasta".format(outdir, sample_name, racon3_polish)
        print("Executing circulating fixstart to rotate #2 and orient properly")
        circlator_outfile_prefix2 = "{0}/shortRead_polish_results/{1}_circlator2".format(outdir, sample_name)
        circlator_outfile2 = "{0}/shortRead_polish_results/{1}_circlator2.fasta".format(outdir, sample_name)
        if args.dnaA_file is None:
            make_circlator_fixstart_command(args.circlator_path, default_db, infile5, circlator_outfile_prefix2)
        else:
            make_circlator_fixstart_command(args.circlator_path, args.dnaA_file, infile5, circlator_outfile_prefix2)
        print("Executing Racon for fourth round of polishing")
        racon4_polish = 4
        make_bwa_command(args.bwa_path, circlator_outfile2, pe_reads, shortRead_polish_outdir, threads, racon4_polish)
        sam_file4 = "{0}/shortRead_polish_results/align_{1}.sam".format(outdir, racon4_polish)
        make_racon_shortRead_command(args.racon_path, pe_reads, sam_file4, circlator_outfile2, outdir, sample_name,
                                     threads, racon4_polish)
        os.system('rm -r %s' % sam_file4)
        infile6 = "{0}/shortRead_polish_results/{1}_racon{2}.fasta".format(outdir, sample_name, racon4_polish)
        print("Executing fix repeat script for final assembly")
        subprocess.Popen("sed '/^>/ s/ .*//' -i " + infile6, shell=True).wait()
        subprocess.Popen('bwa index ' + infile6, shell=True).wait()
        bam_infile6 = "{0}/shortRead_polish_results/{1}_racon{2}_sort.bam".format(outdir, sample_name, racon4_polish)
        subprocess.Popen('bwa mem -t ' + threads + ' ' + infile6 + ' ' + pe_reads + \
                         ' | samtools sort -@ ' + threads + ' > ' + bam_infile6, shell=True).wait()
        coverage_file = "{0}/shortRead_polish_results/coverage.txt".format(outdir)
        subprocess.Popen('bedtools genomecov -d -ibam ' + bam_infile6 + ' > ' + coverage_file, shell=True).wait()
        infile7 = "{0}/shortRead_polish_results/{1}_final.fasta".format(outdir, sample_name)
        tmp_directory = "{0}/shortRead_polish_results/tmp".format(outdir)
        os.makedirs(tmp_directory)
        read_length = 300
        fix_repeats.correct_regions(infile6, pe_reads, coverage_file, tmp_directory, infile7, read_length, threads)
        os.system('rm -r %s' % tmp_directory)
        print("Fin! Enjoy your day!")

if __name__ == '__main__': run_conditions()
