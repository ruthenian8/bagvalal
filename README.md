# bagvalal morphology
## Background
Bagvalal is an endangered language from the Nakh-Daghestanian family.
This repository contains a prototype for a Bagvalal morphological analyzer.
## Usage
### Making the analyzers
* run translit/make
* run make merged.ana.hfst for cyrillic version
* run make merged.tr.hfst for simplified IPA version
### Running the analyzers
* run make corpora/\*corpus name\*.analyzed to analyze with the cyrillic transducer
* run make corpora/\*corpus name\*.tr.analyzed to analyze with the IPA transducer
* run bash corpora/tr_stats.sh \*corpus name\*.analyzed to view the statistics

###Example:
* cd corpora
* make k_newline.tr.analyzed
* bash tr_stats.sh k_newline.tr.analyzed

Current performance: ~65%