#!/usr/bin/env python3

#
# Generates a small synthetic VCF sample based on a simple template.
#

import random
import sys

header = """##fileformat=VCFv4.1
##FILTER=<ID=PASS,Description="All filters passed">
##ALT=<ID=NON_REF,Description="Represents any possible alternative allele at this location">
##FILTER=<ID=LowQual,Description="Low quality">
##FORMAT=<ID=AD,Number=.,Type=Integer,Description="Allelic depths for the ref and alt alleles in the order listed">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Approximate read depth (reads with MQ=255 or with bad mates are filtered)">
##FORMAT=<ID=GQ,Number=1,Type=Integer,Description="Genotype Quality">
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=MIN_DP,Number=1,Type=Integer,Description="Minimum DP observed within the GVCF block">
##FORMAT=<ID=PL,Number=G,Type=Integer,Description="Normalized, Phred-scaled likelihoods for genotypes as defined in the VCF specification">
##FORMAT=<ID=SB,Number=4,Type=Integer,Description="Per-sample component statistics which comprise the Fisher's Exact Test to detect strand bias.">
##GATKCommandLine=<ID=HaplotypeCaller,Version=3.1-1-g07a4bf8,Date="Fri Apr 04 23:00:16 EDT 2014",Epoch=1396666816112,CommandLineOptions="analysis_type=HaplotypeCaller input_file=[/seq/external-data/1kg/IBS/exome/HG01762/HG01762.bam] showFullBamList=false read_buffer_size=null phone_home=AWS gatk_key=null tag=NA read_filter=[] intervals=[/seq/picardtemp3/seq/sample_vcf/1kg_IBS/Exome/Homo_sapiens_assembly19/5a9e8c5a-4b71-34c7-abc1-d9f3c1bb2f45/scattered/temp_0001_of_10/scattered.intervals] excludeIntervals=null interval_set_rule=UNION interval_merging=ALL interval_padding=0 reference_sequence=/seq/references/Homo_sapiens_assembly19/v1/Homo_sapiens_assembly19.fasta nonDeterministicRandomSeed=false disableDithering=false maxRuntime=-1 maxRuntimeUnits=MINUTES downsampling_type=BY_SAMPLE downsample_to_fraction=null downsample_to_coverage=250 baq=OFF baqGapOpenPenalty=40.0 fix_misencoded_quality_scores=false allow_potentially_misencoded_quality_scores=false useOriginalQualities=false defaultBaseQualities=-1 performanceLog=null BQSR=null quantize_quals=0 disable_indel_quals=false emit_original_quals=false preserve_qscores_less_than=6 globalQScorePrior=-1.0 validation_strictness=SILENT remove_program_records=false keep_program_records=false sample_rename_mapping_file=null unsafe=null disable_auto_index_creation_and_locking_when_reading_rods=true num_threads=1 num_cpu_threads_per_data_thread=1 num_io_threads=0 monitorThreadEfficiency=false num_bam_file_handles=null read_group_black_list=null pedigree=[] pedigreeString=[] pedigreeValidationType=STRICT allow_intervals_with_unindexed_bam=false generateShadowBCF=false variant_index_type=LINEAR variant_index_parameter=128000 logging_level=INFO log_to_file=null help=false version=false likelihoodCalculationEngine=PairHMM heterogeneousKmerSizeResolution=COMBO_MIN graphOutput=null bamOutput=null bam_compression=null disable_bam_indexing=null generate_md5=null simplifyBAM=null bamWriterType=CALLED_HAPLOTYPES dbsnp=(RodBinding name= source=UNBOUND) dontTrimActiveRegions=false maxDiscARExtension=25 maxGGAARExtension=300 paddingAroundIndels=150 paddingAroundSNPs=20 comp=[] annotation=[ClippingRankSumTest, DepthPerSampleHC, StrandBiasBySample] excludeAnnotation=[SpanningDeletions, TandemRepeatAnnotator, ChromosomeCounts, FisherStrand, QualByDepth] heterozygosity=0.001 indel_heterozygosity=1.25E-4 genotyping_mode=DISCOVERY standard_min_confidence_threshold_for_calling=-0.0 standard_min_confidence_threshold_for_emitting=-0.0 alleles=(RodBinding name= source=UNBOUND) max_alternate_alleles=3 input_prior=[] contamination_fraction_to_filter=0.0 contamination_fraction_per_sample_file=null p_nonref_model=EXACT_INDEPENDENT exactcallslog=null kmerSize=[10, 25] dontIncreaseKmerSizesForCycles=false numPruningSamples=1 recoverDanglingHeads=false dontRecoverDanglingTails=false consensus=false emitRefConfidence=GVCF GVCFGQBands=[5, 20, 60] indelSizeToEliminateInRefModel=10 min_base_quality_score=10 minPruning=3 gcpHMM=10 includeUmappedReads=false useAllelesTrigger=false useFilteredReadsForAnnotations=false phredScaledGlobalReadMismappingRate=45 maxNumHaplotypesInPopulation=200 mergeVariantsViaLD=false pair_hmm_implementation=VECTOR_LOGLESS_CACHING keepRG=null justDetermineActiveRegions=false dontGenotype=false errorCorrectKmers=false debug=false debugGraphTransformations=false dontUseSoftClippedBases=false captureAssemblyFailureBAM=false allowCyclesInKmerGraphToGeneratePaths=false noFpga=false errorCorrectReads=false kmerLengthForReadErrorCorrection=25 minObservationsForKmerToBeSolid=20 pcr_indel_model=CONSERVATIVE activityProfileOut=null activeRegionOut=null activeRegionIn=null activeRegionExtension=null forceActive=false activeRegionMaxSize=null bandPassSigma=null min_mapping_quality_score=20 filter_reads_with_N_cigar=false filter_mismatching_base_and_quals=false filter_bases_not_stored=false">
##GVCFBlock=minGQ=0(inclusive),maxGQ=5(exclusive)
##GVCFBlock=minGQ=20(inclusive),maxGQ=60(exclusive)
##GVCFBlock=minGQ=5(inclusive),maxGQ=20(exclusive)
##GVCFBlock=minGQ=60(inclusive),maxGQ=2147483647(exclusive)
##INFO=<ID=BaseQRankSum,Number=1,Type=Float,Description="Z-score from Wilcoxon rank sum test of Alt Vs. Ref base qualities">
##INFO=<ID=ClippingRankSum,Number=1,Type=Float,Description="Z-score From Wilcoxon rank sum test of Alt vs. Ref number of hard clipped bases">
##INFO=<ID=DP,Number=1,Type=Integer,Description="Approximate read depth; some reads may have been filtered">
##INFO=<ID=DS,Number=0,Type=Flag,Description="Were any of the samples downsampled?">
##INFO=<ID=END,Number=1,Type=Integer,Description="Stop position of the interval">
##INFO=<ID=HaplotypeScore,Number=1,Type=Float,Description="Consistency of the site with at most two segregating haplotypes">
##INFO=<ID=InbreedingCoeff,Number=1,Type=Float,Description="Inbreeding coefficient as estimated from the genotype likelihoods per-sample when compared against the Hardy-Weinberg expectation">
##INFO=<ID=MLEAC,Number=A,Type=Integer,Description="Maximum likelihood expectation (MLE) for the allele counts (not necessarily the same as the AC), for each ALT allele, in the same order as listed">
##INFO=<ID=MLEAF,Number=A,Type=Float,Description="Maximum likelihood expectation (MLE) for the allele frequency (not necessarily the same as the AF), for each ALT allele, in the same order as listed">
##INFO=<ID=MQ,Number=1,Type=Float,Description="RMS Mapping Quality">
##INFO=<ID=MQ0,Number=1,Type=Integer,Description="Total Mapping Quality Zero Reads">
##INFO=<ID=MQRankSum,Number=1,Type=Float,Description="Z-score From Wilcoxon rank sum test of Alt vs. Ref read mapping qualities">
##INFO=<ID=ReadPosRankSum,Number=1,Type=Float,Description="Z-score from Wilcoxon rank sum test of Alt vs. Ref read position bias">
##contig=<ID=1,length=249250621>
##contig=<ID=2,length=243199373>
##contig=<ID=3,length=198022430>
##contig=<ID=4,length=191154276>
##contig=<ID=5,length=180915260>
##contig=<ID=6,length=171115067>
##contig=<ID=7,length=159138663>
##contig=<ID=8,length=146364022>
##contig=<ID=9,length=141213431>
##contig=<ID=10,length=135534747>
##contig=<ID=11,length=135006516>
##contig=<ID=12,length=133851895>
##contig=<ID=13,length=115169878>
##contig=<ID=14,length=107349540>
##contig=<ID=15,length=102531392>
##contig=<ID=16,length=90354753>
##contig=<ID=17,length=81195210>
##contig=<ID=18,length=78077248>
##contig=<ID=19,length=59128983>
##contig=<ID=20,length=63025520>
##contig=<ID=21,length=48129895>
##contig=<ID=22,length=51304566>
##contig=<ID=X,length=155270560>
##contig=<ID=Y,length=59373566>
##contig=<ID=MT,length=16569>
##contig=<ID=GL000207.1,length=4262>
##contig=<ID=GL000226.1,length=15008>
##contig=<ID=GL000229.1,length=19913>
##contig=<ID=GL000231.1,length=27386>
##contig=<ID=GL000210.1,length=27682>
##contig=<ID=GL000239.1,length=33824>
##contig=<ID=GL000235.1,length=34474>
##contig=<ID=GL000201.1,length=36148>
##contig=<ID=GL000247.1,length=36422>
##contig=<ID=GL000245.1,length=36651>
##contig=<ID=GL000197.1,length=37175>
##contig=<ID=GL000203.1,length=37498>
##contig=<ID=GL000246.1,length=38154>
##contig=<ID=GL000249.1,length=38502>
##contig=<ID=GL000196.1,length=38914>
##contig=<ID=GL000248.1,length=39786>
##contig=<ID=GL000244.1,length=39929>
##contig=<ID=GL000238.1,length=39939>
##contig=<ID=GL000202.1,length=40103>
##contig=<ID=GL000234.1,length=40531>
##contig=<ID=GL000232.1,length=40652>
##contig=<ID=GL000206.1,length=41001>
##contig=<ID=GL000240.1,length=41933>
##contig=<ID=GL000236.1,length=41934>
##contig=<ID=GL000241.1,length=42152>
##contig=<ID=GL000243.1,length=43341>
##contig=<ID=GL000242.1,length=43523>
##contig=<ID=GL000230.1,length=43691>
##contig=<ID=GL000237.1,length=45867>
##contig=<ID=GL000233.1,length=45941>
##contig=<ID=GL000204.1,length=81310>
##contig=<ID=GL000198.1,length=90085>
##contig=<ID=GL000208.1,length=92689>
##contig=<ID=GL000191.1,length=106433>
##contig=<ID=GL000227.1,length=128374>
##contig=<ID=GL000228.1,length=129120>
##contig=<ID=GL000214.1,length=137718>
##contig=<ID=GL000221.1,length=155397>
##contig=<ID=GL000209.1,length=159169>
##contig=<ID=GL000218.1,length=161147>
##contig=<ID=GL000220.1,length=161802>
##contig=<ID=GL000213.1,length=164239>
##contig=<ID=GL000211.1,length=166566>
##contig=<ID=GL000199.1,length=169874>
##contig=<ID=GL000217.1,length=172149>
##contig=<ID=GL000216.1,length=172294>
##contig=<ID=GL000215.1,length=172545>
##contig=<ID=GL000205.1,length=174588>
##contig=<ID=GL000219.1,length=179198>
##contig=<ID=GL000224.1,length=179693>
##contig=<ID=GL000223.1,length=180455>
##contig=<ID=GL000195.1,length=182896>
##contig=<ID=GL000212.1,length=186858>
##contig=<ID=GL000222.1,length=186861>
##contig=<ID=GL000200.1,length=187035>
##contig=<ID=GL000193.1,length=189789>
##contig=<ID=GL000194.1,length=191469>
##contig=<ID=GL000225.1,length=211173>
##contig=<ID=GL000192.1,length=547496>
##contig=<ID=NC_007605,length=171823>
##reference=file:///seq/references/Homo_sapiens_assembly19/v1/Homo_sapiens_assembly19.fasta
##bcftools_viewVersion=1.8+htslib-1.8
##bcftools_viewCommand=view -O b -o /Users/tyler/tiledb/TileDB-Genomics/test/inputs/HG01762.20140404.bcf /Users/tyler/tiledb/TileDB-Genomics/test/inputs/HG01762.20140404.vcf.gz; Date=Mon Jul  2 15:04:46 2018
##bcftools_viewCommand=view -r 1:10000-13354 /Users/tyler/tiledb/TileDB-Genomics/test/inputs/HG01762.20140404.bcf; Date=Mon Jul  2 15:16:54 2018
##bcftools_viewCommand=view -O z -o small.vcf.gz small.vcf; Date=Thu Jul 12 13:42:53 2018
##bcftools_viewCommand=view -O b inputs/small.vcf.gz; Date=Fri Jul 13 11:40:03 2018
##bcftools_viewCommand=view inputs/small.bcf; Date=Fri Jul 13 11:51:09 2018
"""

# Example records:
# #CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	HG01762
# 1	12141	.	C	<NON_REF>	.	.	END=12277	GT:DP:GQ:MIN_DP:PL	0/0:0:0:0:0,0,0
# 1	12546	.	G	<NON_REF>	.	.	END=12771	GT:DP:GQ:MIN_DP:PL	0/0:0:0:0:0,0,0
# 1	13354	.	T	<NON_REF>	.	.	END=13389	GT:DP:GQ:MIN_DP:PL	0/0:64:99:30:0,66,990

if len(sys.argv) < 2:
    print("USAGE: {} N".format(sys.argv[0]))
    print(
        'Generates a small synthetic sample named "G<N>" '
        'and writes it to a new file "G<N>.vcf".'
    )
    sys.exit(1)

sample_name = "G{}".format(sys.argv[1])
contigs = list(map(str, range(1, 23)))

with open("{}.vcf".format(sample_name), "w") as f:
    f.write(header)
    f.write(
        "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t{}\n".format(
            sample_name
        )
    )
    for contig in contigs:
        # Random start within the contig
        start = random.randint(10000, 15000)
        # Randon number of records in the contig
        nrecs = random.randint(3, 15)
        for i in range(0, nrecs):
            # Random record length
            end = start + random.randint(1, 100000)

            # Random attribute values
            ref = random.choice(["A", "G", "T", "C"])
            alt = "<NON_REF>"
            gt = "{}/{}".format(random.randint(0, 1), random.randint(0, 1))
            dp = random.randint(0, 99)
            gq = random.randint(0, 99)
            min_dp = random.randint(0, 99)
            pl = "{},{},{}".format(*[random.randint(0, 99) for i in range(0, 3)])
            format = "{}:{}:{}:{}:{}".format(gt, dp, gq, min_dp, pl)

            # Write record
            f.write(
                "{}\t{}\t.\t{}\t{}\t.\t.\tEND={}\tGT:DP:GQ:MIN_DP:PL\t{}\n".format(
                    contig, start, ref, alt, end, format
                )
            )

            # Add random gap
            start = end + random.randint(1, 10000)
