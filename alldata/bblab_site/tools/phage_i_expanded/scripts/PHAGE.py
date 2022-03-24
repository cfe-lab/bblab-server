import sys
import math
import os
import datetime
from .Codon import *
from .Epitope import *
import logging
from itertools import *

output_cols = (
    'patient_id',
    'hiv_protein',
    'hla_allele',
    'hiv_codon',
    'patient_aa',
    'state',
    'ctl_epitope',
    'hla_restriction',
    'epitope_coordinates',
    'epitope_source',
    'expanded_hla_definition',
    'epitope_position'
)

def printHtmlHeaders():
    headers = """<!DOCTYPE html><html><head>
    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
    </head><body>"""
    return headers

def printFileHeaders(filename):
    print("Content-Disposition: attachment; filename=\""+filename+"\"")
    print("Content-Type:application/octet-stream; name=\""+filename+"\"")
    print()

# Flag can be 0, 1, or 2 depending on the desired output
# Flag = 1 will output all mixtures as "X"
# Flag = 2 will output all synonymous mixtures as they are and all non-synonymous mixtures as "X"
# Flag = 3 will output all mixtures in the format [A/B] if a mixture encodes for amino acid A or B
def translateDNA(sequence, resolvecharacter="X", flag=3):
    chars = [' ', '\r\n', '\n', '\r']
    for char in chars:
        if char in sequence:
            sequence = sequence.replace(char, '')
    sequence = sequence.upper()
    aaseq = []
    i = 0
    while i < len(sequence):
        try:
            codon = Codon.resolveCodon(sequence[i:i+3])
        except IndexError:
            codon = Codon.resolveCodon('???')
        # If the codon has no mixture bases just add it to the amino acid chain
        if len(codon) <= 1:
            try:
                aaseq.append(Codon.codon_dict[codon[0]])
            except KeyError:
                logging.error(f'Could not resolve codon: "{codon}"')
        # Codon contains mixture base
        else:
            # If flag is set to 1
            if (flag == 1):
                aaseq.append(resolvecharacter)
            # If flag is set to 2
            elif (flag == 2):
                unique = set([Codon.codon_dict[potential] for potential in codon])
                # If there is more than resolved one amino acid
                if (len(unique) > 1):
                    aaseq.append(resolvecharacter)
                else:
                    aaseq.append(unique.pop())
            # If flag is set to 3
            else:
                try:
                    unique = set([Codon.codon_dict[potential] for potential in codon])
                except KeyError:
                    print('Could not map one of the codons in: {}'.format(codon))
                    print('Sequence was: {}'.format(sequence[i:i+3]))
                    sys.exit(1)
                # If there is more than resolved one amino acid
                if (len(unique) > 1):
                    aaseq.append('['+('/').join(unique)+']')
                else:
                    aaseq.append(unique.pop())
        i += 3
    return aaseq

def parse(input):
    val = [x.split('\t') for x in input.splitlines()]
    return val

def parseHLA(hla, res=4):
    rval = hla.strip()
    chars = ['*', ':', '(', ')']
    for char in chars:
        if char in rval:
            rval = rval.replace(char, '')
    rval = rval.upper()
    try:
        int(rval[-1])
    except (ValueError, IndexError) as e:
        rval = rval[:-1]
    return rval[:res+1]

def parseSeqs(sequences):
    return [translateDNA(x) for x in sequences.splitlines()]

def groupHLA(hlas):
    rdic = {}
    for pair in hlas:
        hla = parseHLA(pair[0])
        pos = int(pair[1][:-1])
        aa = pair[1][-1].upper()
        state = pair[2].lower()
        if hla not in rdic:
            rdic[hla] = {}
        if state not in rdic[hla]:
            rdic[hla][state] = {}
        if pos not in rdic[hla][state]:
            rdic[hla][state][pos] = set(aa)
        rdic[hla][state][pos].add(aa)
    return rdic

def getPatients(patients, simple=0):
    d = {}
    i = 0
    for patient in patients:
        pid = patient[0]
        if (simple == 0):
            d[pid] = {'hlas': set(), 'i': i}
        else:
            d[pid] = {'hlas': set(), 'i': i, 'seq': translateDNA(patient[-1])}
        for hla in patient[1:-1]:
            hla = parseHLA(hla)
            if (hla == ""):
                continue
            d[pid]['hlas'].add(hla)
        i += 1
    return d

def parseEpitopes(epitopes_file):
    results = {}
    with open(epitopes_file, 'r') as f:
        lines = [x.strip().split('\t') for x in f.readlines()]
        results = lines
    return results

def getState(hla, pos, patient_aa):
    na = ('nonadapted') in hla and (pos in hla['nonadapted'])
    a = ('adapted') in hla and (pos in hla['adapted'])
    if na and a:
        if any(x in hla['adapted'][pos] for x in patient_aa):
            return 'adapted'
        elif any(x in hla['nonadapted'][pos] for x in patient_aa):
            return 'nonadapted'
        else:
            return 'possible_adapted'
    elif na:
        if any(x in hla['nonadapted'][pos] for x in patient_aa):
            return 'nonadapted'
        else:
            return 'possible_adapted'
    else:
        if any(x in hla['adapted'][pos] for x in patient_aa):
            return 'adapted'
        else:
            return 'possible_nonadapted'

def analyzePatient(patient, patient_id, protein, grouped_hlas, epitopes):
    results = []
    ghlas = grouped_hlas
    for hla in patient['hlas']:
        compare_hlas = [x[:len(hla)] for x in ghlas]
        try:
            compare_index = list(ghlas.keys()).index(hla[:len(hla)])
        except ValueError:
            continue
        compare_hla = compare_hlas[compare_index]
        done = set()
        for state in ghlas[compare_hla]:
            for pos in ghlas[compare_hla][state]:
                for aa in ghlas[compare_hla][state][pos]:
                    try:
                        patient_aa = patient['seq'][pos-1]
                    except IndexError:
                        continue
                    if patient_aa[0] == '[':
                        patient_aa = tuple(patient_aa[1:-1].split('/'))
                    if (pos, patient_aa) in done:
                        continue
                    result_state = getState(ghlas[compare_hla], pos, patient_aa)
                    if not result_state:
                        continue
                    result = {
                        'pid': patient_id,
                        'hla': compare_hla,
                        'state': result_state,
                        'pos': pos,
                        'aa': aa,
                        'patient_aa': patient_aa,
                        'epitope': set(),
                        'type': False
                    }
                    _min = None
                    for epitope in epitopes:
                        if (epitope.protein == protein) and ((hla in epitope.hlas)):
                            if ((epitope.start - 3) <= result['pos'] <= (epitope.end + 3)):
                                result['epitope'].add(epitope)
                    if not result['epitope']:
                        for epitope in epitopes:
                            if (epitope.protein == protein) and ((hla in epitope.r4) or (hla in epitope.r2)):
                                if ((epitope.start - 3) <= result['pos'] <= (epitope.end + 3)):
                                    result['epitope'].add(epitope)
                                    result['type'] = True
                    #print(result['epitope'])
                    results.append(result)
                    done.add((pos, patient_aa))
    return results

def htmlResults(results, protein):
    html = printHtmlHeaders()
    html += '<table id="output_table">'
    html += '<th>{}</th>'.format('</th><th>'.join(output_cols))
    for result in results:
        html += ('<tr>'
              '<td>{}</td>'
              '<td>{}</td>'
              '<td>{}</td>'
              '<td>{}</td>'
              '<td>{}</td>'
              '<td>{}</td>').format(result['pid'],
                                   protein,
                                   result['hla'],
                                   str(result['pos']),
                                   result['patient_aa'],
                                   result['state'])
        first = (',').join(['('+(',').join(x.epitope)+')' for x in result['epitope']])
        if first:
            html += ('<td>{}</td>'
                  '<td>{}</td>'
                  '<td>{}</td>'
                  '<td>{}</td>'
                  '<td>{}</td>'
                  '<td>{}</td>').format(first,
                                       (',').join(['('+(',').join(x.hlas)+')' for x in result['epitope']]),
                                       (',').join(['({}-{})'.format(x.start, x.end) for x in result['epitope']]),
                                       (',').join(['({})'.format(x.source) for x in result['epitope']]),
                                       'Y' if result['type'] else 'NA',
                                       '('+(',').join([x.getPos(result['pos'])for x in result['epitope']])+')')
        else:
            html += ('<td>NA</td>' * 6)
            continue
        html += ('</tr>')
    html += '</table></body></html>'
    return html

def tsvResults(results, protein, delim='\t'):
    tsv = []
    tsv.append(delim.join(output_cols))
    for result in results:
        temp = [
            result['pid'],
            protein,
            result['hla'],
            str(result['pos']),
            str(result['patient_aa']),
            result['state']
        ]

        first = ','.join(['({})'.format(','.join(x.epitope)) for x in result['epitope']])
        if first:
            temp.extend([
                first,
                ','.join(['({})'.format(','.join(x.hlas)) for x in result['epitope']]),
                ','.join(['({}-{})'.format(x.start, x.end) for x in result['epitope']]),
                ','.join(['({})'.format(x.source) for x in result['epitope']]),
                'Y' if result['type'] else 'NA',
                ','.join([x.getPos(result['pos'])for x in result['epitope']])
            ])
        else:
            temp.extend(('NA',)*6)
        temp = delim.join(temp)
        tsv.append(temp)
    return '\n'.join(tsv)

def get_current_datetime():
    return datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

def run(hlas, patients, protein, button):
    current_path = os.path.dirname(os.path.realpath(__file__))
    epitopes_file = os.path.join(current_path, '..', 'epitopes_v1.0.3.txt')

    epitopes = Epitope.parseEpitopes(epitopes_file)
    for e in epitopes:
        for i,hla in enumerate(e.hlas):
            e.hlas[i] = parseHLA(hla)
        for i,hla in enumerate(e.r2):
            e.r2[i] = parseHLA(hla)
        for i,hla in enumerate(e.r4):
            e.r4[i] = parseHLA(hla)
        e.hlas = set(e.hlas)
        e.r2 = set(e.r2)
        e.r4 = set(e.r4)

    hlas = parse(hlas)
    for hla in hlas:
        hla[0] = parseHLA(hla[0])
    grouped_hlas = groupHLA(hlas)

    patients = getPatients(parse(patients), 1)

    results = []
    done = set()
    for patient in patients:
        patient_results = analyzePatient(patients[patient], patient, protein, grouped_hlas, epitopes)
        results += patient_results

    results = sorted(results, key = lambda x: (x['pid'], x['pos'], x['hla']))

    if button == 'run':
        return (False, htmlResults(results, protein))
    elif button == 'dl':
        return (True, tsvResults(results, protein), 'phage_i_expanded_results_{}_{}.tsv'.format(protein.lower(), get_current_datetime()))