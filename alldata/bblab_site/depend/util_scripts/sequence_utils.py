# do not encode utf-8 -*- coding: utf-8 -*-
##This has been check for python 3.6##

# See: ( https://github.com/emartin-cfe/emartin-personal/blob/master/PYTHON/miseqUtils.py ) for original file.  (More functions but in 2.7)

from datetime import datetime
import sys, re, math
import random

# I found this function -gabe
def xrange(x, y, z):
    return iter(range(x, y, z))

def sam2fasta (infile, cutoff=10, mapping_cutoff = 5, max_prop_N=0.5):
    """
    Parse SAM file contents and return FASTA. For matched read pairs,
    merge the reads together into a single sequence
    """
    fasta = []
    lines = infile.readlines()

    # If this is a completely empty file, return
    if len(lines) == 0:
        return None

    # Skip top SAM header lines
    for start, line in enumerate(lines):
        if not line.startswith('@'):
            break   # exit loop with [start] equal to index of first line of data

    # If this is an empty SAM, return
    if start == len(lines)-1:
        return None

    i = start
    while i < len(lines):
        qname, flag, refname, pos, mapq, cigar, rnext, pnext, tlen, seq, qual = lines[i].strip('\n').split('\t')[:11]

        # If read failed to map or has poor mapping quality, skip it
        if refname == '*' or cigar == '*' or int(mapq) < mapping_cutoff:
            i += 1
            continue

        pos1 = int(pos)
        # shift = offset of read start from reference start
        shift, seq1, qual1 = apply_cigar(cigar, seq, qual)

        if not seq1:
            # failed to parse CIGAR string
            i += 1
            continue

        #seq1 = '-'*pos1 + censor_bases(seq1, qual1, cutoff)
        seq1 = '-'*pos1 + seq1     # FIXME: We no longer censor bases up front
        qual1 = '-'*pos1 + qual1    # FIXME: Give quality string the same offset


        # No more lines
        if (i+1) == len(lines):
            break

        # Look ahead in the SAM for matching read
        qname2, flag, refname, pos, mapq, cigar, rnext, pnext, tlen, seq, qual = lines[i+1].strip('\n').split('\t')[:11]

        if qname2 == qname:
            if refname == '*' or cigar == '*':
                # Second read failed to map - add unpaired read to FASTA and skip this line
                fasta.append([qname, seq1])
                i += 2
                continue

            pos2 = int(pos)
            shift, seq2, qual2 = apply_cigar(cigar, seq, qual)

            if not seq2:
                # Failed to parse CIGAR
                fasta.append([qname, seq1])
                i += 2
                continue

            #seq2 = '-'*pos2 + censor_bases(seq2, qual2, cutoff)
            seq2 = '-'*pos2 + seq2      # FIXME: We no longer censor bases up front
            qual2 = '-'*pos2 + qual2     # FIXME: Give quality string the same offset

            mseq = merge_pairs(seq1, seq2, qual1, qual2, cutoff)    # FIXME: We now feed these quality data into merge_pairs

            # Sequence must not have too many censored bases
            # TODO: garbage reads should probably be reported
            if mseq.count('N') / float(len(mseq)) < max_prop_N:
                fasta.append([qname, mseq])

            i += 2
            continue

        # ELSE no matched pair
        fasta.append([qname, seq1])
        i += 1

    return fasta


def timestamp(message):
	'''This probably prints the current time.'''
	curr_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
	output = ' {} {}'.format(curr_time,message)
	print ( output )
	sys.stdout.flush()
	return "{}\n".format(output)


def convert_csf (csf_handle):
    """
    Extract header, offset, and seq from the CSF.
    The header is qname for Nextera, and rank_count for Amplicon.
    """
    left_gap_position = {}
    right_gap_position = {}

    fasta = []
    for line in csf_handle:
        fields = line.strip('\n').split(',')
        CSF_header, offset, seq = fields[0], fields[1], fields[2]
        fasta.append([CSF_header, seq])
        left_gap_position[CSF_header] = int(offset)
        right_gap_position[CSF_header] = left_gap_position[CSF_header] + len(seq)

    return fasta,left_gap_position,right_gap_position


def convert_fasta (lines):	
    blocks = []
    sequence = ''
    for i in lines:
        if i[0] == '$': # skip h info
            continue
        elif i[0] == '>' or i[0] == '#':
            if len(sequence) > 0:
                blocks.append([h,sequence])
                sequence = ''	# reset containers
                h = i.strip('\n')[1:]
            else:
                h = i.strip('\n')[1:]
        else:
            sequence += i.strip('\n')
    try:
        blocks.append([h,sequence])	# handle last entry
    except:
        #raise Exception("convert_fasta(): Error appending to blocks [{},{}]".format(h, sequence))
        raise Exception("convert_fasta(): Had error with list : {}".format(lines))
    return blocks


complement_dict = {'A':'T', 'C':'G', 'G':'C', 'T':'A', 
                    'W':'S', 'R':'Y', 'K':'M', 'Y':'R', 'S':'W', 'M':'K',
                    'B':'V', 'D':'H', 'H':'D', 'V':'B',
                    '*':'*', 'N':'N', '-':'-'}

def reverse_and_complement(seq):
    rseq = seq[::-1]
    rcseq = ''
    for i in rseq:	# reverse order
        rcseq += complement_dict[i]
    return rcseq



codon_dict = {'TTT':'F', 'TTC':'F', 'TTA':'L', 'TTG':'L',
                'TCT':'S', 'TCC':'S', 'TCA':'S', 'TCG':'S',
                'TAT':'Y', 'TAC':'Y', 'TAA':'*', 'TAG':'*',
                'TGT':'C', 'TGC':'C', 'TGA':'*', 'TGG':'W',
                'CTT':'L', 'CTC':'L', 'CTA':'L', 'CTG':'L',
                'CCT':'P', 'CCC':'P', 'CCA':'P', 'CCG':'P',
                'CAT':'H', 'CAC':'H', 'CAA':'Q', 'CAG':'Q',
                'CGT':'R', 'CGC':'R', 'CGA':'R', 'CGG':'R',
                'ATT':'I', 'ATC':'I', 'ATA':'I', 'ATG':'M',
                'ACT':'T', 'ACC':'T', 'ACA':'T', 'ACG':'T',
                'AAT':'N', 'AAC':'N', 'AAA':'K', 'AAG':'K',
                'AGT':'S', 'AGC':'S', 'AGA':'R', 'AGG':'R',
                'GTT':'V', 'GTC':'V', 'GTA':'V', 'GTG':'V',
                'GCT':'A', 'GCC':'A', 'GCA':'A', 'GCG':'A',
                'GAT':'D', 'GAC':'D', 'GAA':'E', 'GAG':'E',
                'GGT':'G', 'GGC':'G', 'GGA':'G', 'GGG':'G',
                '---':'-', 'XXX':'?'}

mixture_regex = re.compile('[WRKYSMBDHVN-]')

mixture_dict = {'W':'AT', 'R':'AG', 'K':'GT', 'Y':'CT', 'S':'CG', 
                'M':'AC', 'V':'AGC', 'H':'ATC', 'D':'ATG',
                'B':'TGC', 'N':'ATGC', '-':'ATGC'}

#mixture_dict_2 =  [ (set(v), k) for k, v in mixture_dict.iteritems() ]
ambig_dict = dict(("".join(sorted(v)), k) for k, v in mixture_dict.items())


def translate_nuc (seq, offset, resolve=False):
    """
    Translate nucleotide sequence into amino acid sequence.
        offset by X shifts sequence to the right by X bases
    Synonymous nucleotide mixtures are resolved to the corresponding residue.
    Nonsynonymous nucleotide mixtures are encoded with '?'
    """

    seq = '-'*offset + seq

    aa_list = []
    aa_seq = ''	# use to align against reference, for resolving indels

    # loop over codon sites in nucleotide sequence
    for codon_site in xrange(0, len(seq), 3):
        codon = seq[codon_site:codon_site+3]

        if len(codon) < 3:
            break

        # note that we're willing to handle a single missing nucleotide as an ambiguity
        if codon.count('-') > 1 or '?' in codon:
            if codon == '---':	# don't bother to translate incomplete codons
                aa_seq += '-'
            else:
                aa_seq += '?'
            continue

        # look for nucleotide mixtures in codon, resolve to alternative codons if found
        num_mixtures = len(mixture_regex.findall(codon))

        if num_mixtures == 0:
            aa_seq += codon_dict[codon]

        elif num_mixtures == 1:
            resolved_AAs = []
            for pos in range(3):
                if codon[pos] in mixture_dict.keys():
                    for r in mixture_dict[codon[pos]]:
                        rcodon = codon[0:pos] + r + codon[(pos+1):]
                        if codon_dict[rcodon] not in resolved_AAs:
                            resolved_AAs.append(codon_dict[rcodon])
            if len(resolved_AAs) > 1:
                if resolve:
                    # for purposes of aligning AA sequences
                    # it is better to have one of the resolutions
                    # than a completely ambiguous '?'
                    aa_seq += resolved_AAs[0]
                else:
                    aa_seq += '?'
            else:
                aa_seq += resolved_AAs[0]

        else:
            aa_seq += '?'

    return aa_seq



def consensus(column, alphabet='ACGT', resolve=False):
    """
    Plurality consensus - nucleotide with highest frequency.
    In case of tie, report mixtures.
    """
    freqs = {}

    # Populate possible bases from alphabet
    for char in alphabet:
        freqs.update({char: 0})

    # Traverse the column...
    for char in column:

        # If the character is within the alphabet, keep it
        if char in alphabet:
            freqs[char] += 1

        # If there exists an entry in mixture_dict, take that
        # mixture_dict maps mixtures to bases ('-' maps to 'ACGT')
        elif mixture_dict.has_key(char):

            # Handle ambiguous nucleotides with equal weighting
            # (Ex: for a gap, add 1/4 to all 4 chars)
            resolutions = mixture_dict[char]
            for char2 in resolutions:
                freqs[char2] += 1./len(resolutions)
        else:
            pass

    # AT THIS POINT, NO GAPS ARE RETAINED IN FREQS - TRUE GAPS ARE REPLACED WITH 'ACGT' (N)


    # Get a base with the highest frequency
    # Note: For 2 identical frequencies, it will only return 1 base
    base = max(freqs, key=lambda n: freqs[n])
    max_count = freqs[base]

    # Return all bases (elements of freqs) such that the freq(b) = max_count
    possib = filter(lambda n: freqs[n] == max_count, freqs)

    # If there is only a single base with the max_count, return it
    if len(possib) == 1:
        return possib[0]

    # If a gap is in the list of possible bases... remove it unless it is the only base
    # CURRENTLY, THIS BRANCH IS NEVER REACHED
    elif "-" in possib:
        if resolve:
            possib.remove("-")
            if len(possib) == 0:
                return "-"
            elif len(possib) == 1:
                return possib[0]
            else:
                return ambig_dict["".join(sorted(possib))]

        # If resolve is turned off, gap characters override all ties
        else:
            return "-"
    else:
        return ambig_dict["".join(sorted(possib))]


def parse_fasta (handle):
    """
    Read lines from a FASTA file and return as a list of
    header, sequence tuples.
    """
    res = []
    sequence = ''
    for line in handle:
        if line.startswith('$'): # skip annotations
            continue
        elif line.startswith('>') or line.startswith('#'):
            if len(sequence) > 0:
                res.append((h, sequence))
                sequence = ''   # reset containers
            h = line.lstrip('>#').rstrip('\n')
        else:
            sequence += line.strip('\n')

    res.append((h, sequence)) # handle last entry
    return res


# A list of all valid characters in a DNA sequence.
valid_char_list = ['A', 'C', 'T', 'G', 'R', 'Y', 'K', 'M', 'S', 'W', 'B', 'D', 'H', 'V', 'N', "-"]

def invalid_in_sequence (sequence):
	"""
	Check for any invalid characters in the dna sequence.
	Reports a tuple with (is_valid, (invalid_char, position), ...)  [position starts from 0, not 1.]
	"""
	is_valid = True
	results = ()
	
	index = 0
	for char in sequence:
		if (char in valid_char_list) == False:  # Case: invalid character.
			is_valid = False
			results += ((char, index),)
		index += 1

	return (is_valid,) + results



# A list of all valid characters in a DNA sequence.
mixture_list = ['R', 'Y', 'K', 'M', 'S', 'W', 'B', 'D', 'H', 'V', 'N']

def mixtures_in_sequence (sequence):
	"""
	Checks for mixtures in the dna sequence.
	Reports a tuple with (contains_mixtures, (mixture_value, position), ...)  [position starts from 0, not 1.]

	"""
	contains_mixtures = False
	results = ()
	
	index = 0
	for char in sequence:
		if char in mixture_list:  # Case: character is a mixture.
			contains_mixtures = True
			results += ((char, index),)
		index += 1

	return (contains_mixtures,) + results

protein_mixture_list = ['X', '-', '_']  # I guess it's just three.
valid_protein_character_list = [ 'A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'X', 'Y', '-', '_' ]  # This does not include B, J, O, U, or Z. 


def seq_validity_test(in_sequence):
	'''
	This function checks the validity of the sequence and returns the boolean value 'is_valid'.
	'''
	if len(in_sequence >=3):
		report = invalid_in_sequence(in_sequence)  # Searches for invalid characters in sequence.
		return report[0]  # Return the report's validity.
	else:
		return (False,)

def seq_div3_test(in_sequence):
	'''
	This function runs the divisible by 3 test on the sequence and returns success as a bool in a tuple.  (For some reason...)
	'''
	return (True,) if len(in_sequence) % 3 == 0 else (False,)


def seq_start_test(in_sequence):
	'''
	This function runs the "check for start codon" test on the sequence and returns success as a bool in a tuple.  (For some reason...)
	
	len(in_sequence) must be larger than or equal to 3 before running this function.
	'''
	first_char = translate_nuc(in_sequence[0:3], 0)[0]
	return (True,) if first_char == 'M' else (False,)


def seq_stop_test(in_sequence):
	'''
	This function runs the "check for end codon" test on the sequence and returns success as a bool in a tuple.
	
	len(in_sequence) must be divisible by 3 before running this function.
	'''
	last_char = translate_nuc(in_sequence, 0)[-1]
	return (True,) if last_char == '*' else (False,)


def seq_internal_test(in_sequence):
	'''
	This function runs the "check for internal end codons" test on the sequence and returns 
	(True,) if there are no internal and (False, position, ...) if there are internal end codons.  
	
	len(in_sequence) must be larger than 6 to run this sequence.
	'''
	endpoint = -1 if len(in_sequence) % 3 == 0 else None # exclude stop codon if translate_nuc doesn't automatically. Added (2020-03-06)
	nuc_seq = translate_nuc(in_sequence, 0)[0:endpoint] # Convert the dna seq to nuc. 

	no_internal = True  # No internal end codons.
	position_list = ()  # This holds the positions of any internal end codons.	

	# Find all instances of '*' in the nuc_seq and collect all that are not at the end.
	for match in re.finditer('\\x2a', nuc_seq):
		#if match.start() != len(nuc_seq)-1: # IF NOT DIVISIBLE BY 3, LAST CODON IS SKIPPED # this broke it in a different way. (2020-03-06)
		no_internal = False
		position_list += (match.start()+1,) # +1 because arrays start at zero and humans start at 1.

	return (no_internal,) + position_list


def seq_mixture_test(in_sequence):
	'''
	This function runs the "check for mixtures" test on the sequence and returns (False,) if there are
	no mixtures, and (True, mixture_percent_comp, dict_of_the_variety_of_mixtures) 
	()[2] -> a dict of all the different mixtures that are in the sequence
	'''
	report = mixtures_in_sequence(in_sequence)  # Searches for mixture characters in the sequence.

	# Case: There are no mixtures. 
	if report[0] == False:  
		return (True, 0)
	
	mixture_dict = {}
	mixture_counter = 0	

	# Init the dictionary with 0s for each mixture.
	for mixture_item in mixture_list: 
		mixture_dict[mixture_item] = 0

	# Count the occurance of each mixture and total mixture count.
	for mixture_item in report[1:]:
		mixture_dict[mixture_item[0]] += 1
		mixture_counter += 1
	
	percent_comp = int( float(mixture_counter) / float(len(in_sequence)) * (100**2) ) / 100.0
	return (False, percent_comp, mixture_dict)

