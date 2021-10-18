# bagvalal morphology
## Background
Bagvalal is an endangered language from the Nakh-Daghestanian family.
This repository contains a prototype for a Bagvalal morphological analyzer.
## Usage
### Making the analyzers
* run make merged.ana.hfst for cyrillic version
* run make merged.tr.hfstol or just make for Caucasiologist transcription version
### Running the analyzers
* run make check-coverage-stats to view the statistics
* cd to corpora & run make \*corpus name\*.analyzed to analyze with the cyrillic transducer
* cd to corpora & run make \*corpus name\*.tr.analyzed to analyze with the IPA transducer

### Examples:
* make check-coverage-stats
* cd corpora
* make k_newline.tr.analyzed

Current performance: Naive Coverage ~82%