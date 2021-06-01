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
* run corpora/stats.sh
* run \*corpus name\*.analyzed to analyze with the cyrillic transducer
* run \*corpus name\*.tr.analyzed to analyze with the IPA transducer
* run bash tr_stats.sh \*corpus name\*.analyzed to view the statistics

Current performance: ~65%