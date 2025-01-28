# Table of Contents

- [List of BBLab tools with existing repos](#list-of-bblab-tools-with-existing-repos)
- [List of unavailable tools](#list-of-unavailable-tools)
- [Misc To-Do](#misc-to-do)
- [Further Notes](#further-notes)
    - [Phylodating](#phlodating)
    - [Blind Dating](#blind-dating) 
    - [PHAGE-I-expanded](#phage-i-expanded)
    - [HLA Class](#hla-class)
- [Web Links](#web-links)


# List of BBLab tools

A list of avaliable tools. Several tools exist in their own repos (and are included in the `test` branch as Git submodules). See [Further Notes](#further-notes) for more information.

## Layout Generators

- __Sequencing layout designer__ 
- __Guava layout designer__ 

## QC and data processing

- __Fasta Converter__ 
- __Text to columns__ 
- __False discovery rate q-value calculator__ 


## HIV sequence/function analyses

- __HXB2 Genome genome map__
- __DNA translator__ 
- __Quality Check Tool__
- __Unique Sequence Finder (USF)__ 
- __Variable Function Analysis: in house variable-function analyzer__ 
- __Codon by codon in house analysis tool__ 
- __Phylogenetic Dating__ : tracking [`cfe-lab/phylodating`], missing some recent commits which update documentation
    - __Blind Dating__ : old version of Pylogenetic Dating, also on Git at [`cfe-lab/blind-dating`] (tracking the `web` branch). Git structure is messy.

[`cfe-lab/phylodating`]: https://github.com/cfe-lab/phylodating
[`cfe-lab/blind-dating`]: https://github.com/cfe-lab/blind-dating/tree/web


## HLA interpretation and analyses

- __HLA class I sequence-based typing interpretation tool__
- __PHAGE-I-expanded__: should be tracking [`cfe-lab/PHAGE-I-expanded`], needs some repo cleanup on the server.

[`cfe-lab/PHAGE-I-expanded`]: https://github.com/cfe-lab/PHAGE-I-expanded


## TCR interpretation and analysis   

- __TCR Distance__ : this tool uses the repo [`tcr-dist`]    
- __TCR Visualizer__ 

[`tcr-dist`]: https://github.com/phbradley/tcr-dist


# List of unavailable tools
These tools will not be hosted on the server. They exist in the BBLab-Wiki backup (MDF) but have not been ported to Python 3/Django. They are all under source control from deleted repos, dating from 2014-2017.
- __Best Probability (BPHI)__ - Get the best probabilities only from HLA Imputation 
- __HAPC__ - HLA Associated Polymorphism Counter HAPC
- __HAPA__ - HLA Associated Polymorphism Analyzer HAPA
- __PHAGE-I__ - Proportion of HLA Associated Genomic Escape (individual) 
- __PHAGE-P__ - Proportion of HLA Associated Genomic Escape (population) PHAGE-P
- __HAPLOID__ - HLA Associated PoLymOrphism IDentifier HAPLOID
- __CLEF__ - CTL Epitope Finder CLEF

# Misc To-Do

- Update Django from 2.2.0 to 2.2.26
- (Longer term) Migrate to a newer Django version as 2.2 is losing support in April 2022.

# Further Notes

Further explanation for some specific tools as needed.

# Phylodating
- This is tracking the Git repo [`cfe-lab/phylodating`]
- There is also a version of this in `alldata/bblab_site/tools/test/phylodating`, which can probably be removed.
# Blind Dating
- An earlier version of [Phylodating](#phlodating)
- This is not linked on the BBLab wiki page, however it is stored on the server. There is a `tools/blind_dating/repo` directory which is tracking the `web` branch of [`cfe-lab/blind-dating`], though it is 7 commits behind. 
- There is another Git repo in the `tools/blind_dating` directory that is tracking a non-existent repository called `cfe-lab/web_blind_dating.git`. This one is integrated with Django and contains a Python script `blind_dating.py` which calls the R scripts located in `repo/src`.
    - (Note: the R scripts `root_and_regress.R` and `plot_divergence_vs_time.R` are also located in `tools/phylodating`, which is tracking [`cfe-lab/phylodating`].)
    
[`cfe-lab/blind-dating`]: https://github.com/cfe-lab/blind-dating/tree/web
[`cfe-lab/phylodating`]: https://github.com/cfe-lab/phylodating


# PHAGE-I-expanded
The main directory is not under source control. But there is a `tools/phage_i_expanded/repo` folder which is the whole repo but still points to `https://github.com/dmacmillan/PHAGE-I-expanded.git` (now deleted). I suggest we remove `tools/phage_i_expanded/repo` and set page to track the copy hosted at [`cfe-lab/PHAGE-I-expanded`].

[`cfe-lab/PHAGE-I-expanded`]: https://github.com/cfe-lab/PHAGE-I-expanded

# HLA Class
This tool is not part of the Django framework, as it's written in Ruby and PHP and wasn't ported. It is aliased in the Apache config file (`httpd/conf/httpd.conf (385-392)`). Porting to Python seems possible but non-trivial -- `hla-easy.rb` is 500+ lines and relies on at least one method from BioRuby (`Bio::FlatFile.auto`)


# Web Links

Under the `Other useful resources` section of the Wiki

- ['Primer tables'] for sequencing or PCR
    - Link is working.
- ['Papers'] about HIV virology, epidemiology, immunology
    - Link is working.
- Stanford Drug Resistance Database: https://hivdb.stanford.edu/
    - Link is working.
- LANL HIV Sequence database: https://www.hiv.lanl.gov/content/sequence/HIV/mainpage.html/
    - Link is working.
- LANL HIV Immunology Database: https://www.hiv.lanl.gov/content/immunology/index.html/
    - Link is working.

['Primer tables']: https://hivresearchtools.bccfe.ca/django/wiki/misc/primer-list/
['Papers']: https://hivresearchtools.bccfe.ca/django/wiki/misc/papers/

