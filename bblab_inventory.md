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
- __Phylogenetic Dating__ : tracking [`cfe-lab/phylodating`], missing some recent commits which update documentation
    - __Blind Dating__ : old version of Pylogenetic Dating, also on Git at [`cfe-lab/blind-dating`] (tracking the `web` branch). Git structure is messy.

- __PHAGE-I-expanded__: should be tracking [`cfe-lab/PHAGE-I-expanded`], needs some repo cleanup on the server.

- __Fasta Converter__ : tracking [`cfe-lab/fasta_converter`], reconstructed history from Python 2.7 to Python 3 and Django. Awaiting a `git checkout` before any new update.

- __DNA translator__ : tracking [`cfe-lab/translate_DNA`], reconstructed history from Python 2.7 to Python 3 and Django. Awaiting a `git checkout` before any new update.

- __HXB2 Genome genome map__ : tracking [`cfe-lab/HIV_genome`], reconstructed minor changes and move to Django. Awaiting a `git checkout` before any new update.

- __False discovery rate q-value calculator__ : tracking [`cfe-lab/qvalue`], reconstructed history from Perl, Python 2.7 to Python 3 and Django. Awaiting a `git checkout` before any new update.


[`cfe-lab/phylodating`]: https://github.com/cfe-lab/phylodating
[`cfe-lab/blind-dating`]: https://github.com/cfe-lab/blind-dating/tree/web
[`cfe-lab/PHAGE-I-expanded`]: https://github.com/cfe-lab/PHAGE-I-expanded
[`cfe-lab/fasta_converter`]: https://github.com/cfe-lab/fasta_converter
[`cfe-lab/translate_DNA`]: https://github.com/cfe-lab/translate_DNA
[`cfe-lab/HIV_genome`]: https://github.com/cfe-lab/HIV_genome
[`cfe-lab/qvalue`]: https://github.com/cfe-lab/qvalue


# List of BBLab tools that need source control

## Layout Generators

- __Sequencing layout designer__ 
    - Has no source control. Previous Python 3 (CGI) and Perl versions are located on the server at `/alldata/WebContent/codelink` and on the MDF under `Eric_server_tools/Sites/cgi-bin/`. 
- __Sequencing plate layout archive__ 
    - links to `tools/sequencing_layout/output/`, requires authentication to access.

- __Guava layout designer__ 
    - Has no source control. Previous Python 3 (CGI) and Perl versions are located on the server at `/alldata/WebContent/codelink` and on the MDF under `Eric_server_tools/Sites/cgi-bin/`. 

- __Guava plate layout archive__ 
    - links to `tools/guava_layout/output/`, requires authentication to access.

## QC and data processing

- __Text to columns__ 
    - No source control and does not appear on the MDF. A text manipulation tool which counts the characters in each column in the input text field.

## HIV sequence/function analyses

- __Quality Check Tool__
    - There are multiple revisions of the Python script `quality_check.py` located on the server in `bblab_site/WebContent/codelink/legacy_code` and on the MDF in `/Eric_server_tools/Sites/`. A history could probably be reconstructed.

- __Unique Sequence Finder (USF)__
    - There is an older Python script `unique_sequence_checker.py` located in `bblab_site/WebContent/codelink/`, and in `Eric_server_tools/Sites/cgi_bin/python/`. A history could probably be reconstructed.

- __Variable Function Analysis: in house variable-function analyzer__
    - There is an old version (Python 2.7) of the Python script `variable_function.py` in `SFU_BBlabWiki_tools/Eric_server_tools/Sites/dan/webtools/VFA/cgi-bin/`. A history could probably be reconstructed. 

- __Codon by codon in house analysis tool__:
    - There are multiple revisions of the Python script `codon_by_codon.py` located in `bblab_site/WebContent/codelink/legacy_code`. We also have the original Perl scripts in `Eric_server_tools/Sites/cgi_bin/codon_by_codon.pl`. A history could probably be reconstructed. 


## HLA interpretation and analyses

- __HLA class I sequence-based typing interpretation tool__ 
    - Located on the server in `/alldata/hla_class`, and on the MDF in `/McCloskey_server_tools/McCloskeySites/hla`

- __Best Probability Get the best probabilities only from HLA Imputation__ 
    - Untested tool. It also doesn't exist in the MDF folder. Dates to August 2019.


## TCR interpretation and analysis   

- __TCR Distance__
    - This tool is fairly recent, and uses `alldata/bblab_site/tools/tcr_distance/tcr_distance.py` as well as `bblab_site/static/tcr_dist.js`
- __TCR Visualizer__
    - This tool does not contain a Python script, but uses `bblab_site/static/tcr_vis.js`.


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


