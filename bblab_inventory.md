# Table of Contents

- [List of BBLab tools with existing repos](#list-of-bblab-tools-with-existing-repos)
- [List of BBLab tools that need source control](#list-of-bblab-tools-that-need-source-control)
- [List of unavailable tools](#list-of-unavailable-tools)
- [Misc To-Do](#misc-to-do)
- [Further Notes](#further-notes)
    - [Blind Dating](#blind-dating) 
    - [PHAGE-I-expanded](#phage-i-expanded)
    - [HLA Class](#hla-class)
- [Web Links](#web-links)


# List of BBLab tools with existing repos


## Layout Generators

- __Sequencing layout designer__ : tracking [`cfe-lab/sequencing-layout`]. Awaiting a `git checkout` before any new update.
- __Guava layout designer__ : tracking [`cfe-lab/guava-layout`]. Awaiting a `git checkout` before any new update.

 [`cfe-lab/sequencing-layout`]: https://github.com/cfe-lab/sequencing-layout
 [`cfe-lab/guava-layout`]: https://github.com/cfe-lab/guava-layout


## QC and data processing

- __Fasta Converter__ : tracking [`cfe-lab/fasta-converter`]. Awaiting a `git checkout` before any new update.

- __Text to columns__ : tracking [`cfe-lab/text-to-columns`]. Awaiting a `git checkout` before any new update.
    
- __False discovery rate q-value calculator__ : tracking [`cfe-lab/qvalue`]. Awaiting a `git checkout` before any new update.

[`cfe-lab/fasta-converter`]: https://github.com/cfe-lab/fasta-converter
[`cfe-lab/text-to-columns`]: https://github.com/cfe-lab/text-to-columns
[`cfe-lab/qvalue`]: https://github.com/cfe-lab/qvalue


## HIV sequence/function analyses

- __HXB2 Genome genome map__ : tracking [`cfe-lab/HIV-genome`]. Awaiting a `git checkout` before any new update.

- __DNA translator__ : tracking [`cfe-lab/translate-DNA`]. Awaiting a `git checkout` before any new update.

- __Quality Check Tool__ : tracking [`cfe-lab/quality-check`]. Awaiting a `git checkout` before any new update.

- __Unique Sequence Finder (USF)__ : tracking [`cfe-lab/unique-sequence`]. Awaiting a `git checkout` before any new update.

- __Variable Function Analysis: in house variable-function analyzer__ : tracking [`cfe-lab/variable-function`]. Awaiting a `git checkout` before any new update.

- __Codon by codon in house analysis tool__ : tracking [`cfe-lab/codon-by-codon`]. Awaiting a `git checkout` before any new update. 

- __Phylogenetic Dating__ : tracking [`cfe-lab/phylodating`], missing some recent commits which update documentation
    - __Blind Dating__ : old version of Pylogenetic Dating, also on Git at [`cfe-lab/blind-dating`] (tracking the `web` branch). Git structure is messy.

[`cfe-lab/HIV-genome`]: https://github.com/cfe-lab/HIV-genome
[`cfe-lab/translate-DNA`]: https://github.com/cfe-lab/translate-DNA
[`cfe-lab/quality-check`]: https://github.com/cfe-lab/quality-check
[`cfe-lab/unique-sequence`]: https://github.com/cfe-lab/unique-sequence
[`cfe-lab/variable-function`]: https://github.com/cfe-lab/variable-function
[`cfe-lab/codon-by-codon`]: https://github.com/cfe-lab/codon-by-codon
[`cfe-lab/phylodating`]: https://github.com/cfe-lab/phylodating
[`cfe-lab/blind-dating`]: https://github.com/cfe-lab/blind-dating/tree/web


## HLA interpretation and analyses

- __HLA class I sequence-based typing interpretation tool__ : tracking [`cfe-lab/hla-class`]. Awaiting a `git checkout` before any new update. 

- __PHAGE-I-expanded__: should be tracking [`cfe-lab/PHAGE-I-expanded`], needs some repo cleanup on the server.

[`cfe-lab/hla-class`]: https://github.com/cfe-lab/hla-class
[`cfe-lab/PHAGE-I-expanded`]: https://github.com/cfe-lab/PHAGE-I-expanded


## TCR interpretation and analysis   

- __TCR Distance__ : tracking [`cfe-lab/tcr-distance`]. Awaiting a `git checkout` before any new update. 
Note: this tool uses the repo [`tcr-dist`] which is currently out of date on thes server.
    
- __TCR Visualizer__ : tracking [`cfe-lab/tcr-visualizer`]. Awaiting a `git checkout` before any new update.

[`cfe-lab/tcr-distance`]: https://github.com/cfe-lab/tcr-distance
[`cfe-lab/tcr-visualizer`]: https://github.com/cfe-lab/tcr-visualizer
[`tcr-dist`]: https://github.com/phbradley/tcr-dist


# List of BBLab tools that need source control

## HLA interpretation and analyses

- __Best Probability Get the best probabilities only from HLA Imputation__ 
    - Untested tool. It also doesn't exist in the MDF folder. Dates to August 2019.


# List of unavailable tools
These tools will not be hosted on the server. They exist in the BBLab-Wiki backup (MDF) but have not been ported to Python 3/Django. They are all under source control from deleted repos, dating from 2014-2017.
- __HAPC__ - HLA Associated Polymorphism Counter HAPC
- __HAPA__ - HLA Associated Polymorphism Analyzer HAPA
- __PHAGE-I__ - Proportion of HLA Associated Genomic Escape (individual) 
- __PHAGE-P__ - Proportion of HLA Associated Genomic Escape (population) PHAGE-P
- __HAPLOID__ - HLA Associated PoLymOrphism IDentifier HAPLOID
- __CLEF__ - CTL Epitope Finder CLEF

# Misc To-Do

- Update Django from 2.2.0 to 2.2.26
- (Longer term) Migrate to a newer Django as 2.2 is losing support in April 2022.

# Further Notes

Further explanation for some specific tools as needed.

# Blind Dating
- An earlier version of __Phylogenetic Dating__
- This is not linked on the BBLab wiki page, however it is stored on the server. There is a `tools/blind_dating/repo` directory which is tracking the `web` branch of [`cfe-lab/blind-dating`], though it is 7 commits behind. 
- There is another Git repo in the `tools/blind_dating` directory that is tracking a non-existent repository called `cfe-lab/web_blind_dating.git`. This one is integrated with Django and contains a Python script `blind_dating.py` which calls the R scripts located in `repo/src`.
    - (Note: the R scripts `root_and_regress.R` and `plot_divergence_vs_time.R` are also located in `tools/phylodating`, which is tracking [`cfe-lab/phylodating`].)
    
[`cfe-lab/blind-dating`]: https://github.com/cfe-lab/blind-dating/tree/web
[`cfe-lab/phylodating`]: https://github.com/cfe-lab/phylodating


# PHAGE-I-expanded
The source control is a bit of a mess. The main directory is not under source control. But there is a `tools/phage_i_expanded/repo` folder which is the whole repo but still points to `https://github.com/dmacmillan/PHAGE-I-expanded.git` (now deleted). I suggest we remove `tools/phage_i_expanded/repo` and set page to track the copy hosted at [`cfe-lab/PHAGE-I-expanded`].

[`cfe-lab/PHAGE-I-expanded`]: https://github.com/cfe-lab/PHAGE-I-expanded

# HLA Class
This tool is not part of the Django framework, as it's written in Ruby and PHP and wasn't ported. It is aliased in the Apache config file (`httpd/conf/httpd.conf (385-392)`). Porting to Python seems possible but non-trivial -- `hla-easy.rb` is 500+ lines and relies on at least one method from BioRuby (`Bio::FlatFile.auto`)


# Web Links

Under the `Other useful resources` section of the Wiki

- ['Primer tables'] for sequencing or PCR
    - Link is working.
- ['Papers'] about HIV virology, epidemiology, immunology
    - Link is working.
- Microsoft collaborator tools: http://research.microsoft.com/en-us/um/redmond/projects/MSCompBio
    - __Link redirects to landing page: ['Microsoft Research Lab - Redmond']__ Needs an update. 
- Stanford Drug Resistance Database: https://hivdb.stanford.edu/
    - Link is working.
- LANL HIV Sequence database: https://www.hiv.lanl.gov/content/sequence/HIV/mainpage.html/
    - Link is working.
- LANL HIV Immunology Database: https://www.hiv.lanl.gov/content/immunology/index.html/
    - Link is working.

['Primer tables']: https://bblab-hivresearchtools.ca/django/wiki/misc/primer-list/
['Papers']: https://bblab-hivresearchtools.ca/django/wiki/misc/papers/
['Microsoft Research Lab - Redmond']: https://www.microsoft.com/en-us/research/lab/microsoft-research-redmond/

## Legacy Resources

- Old Webserver: http://brockman-srv.mbb.sfu.ca/~B_Team_iMac/wiki/index.php
    - __This page is down, probably should remove this link.__ Or should direct somewhere else.


