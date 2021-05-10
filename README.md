# bagvalal morphology
## Background
Bagvalal is an endangered language from the Nakh-Daghestanian family.
This repository contains a prototype for a Bagvalal morphological analyzer.
## Usage
* run translit/make
* run make merged.ana.hfst
* run corpora/stats.sh

Currently the 300-token corpora is transliterated into a
778-token file due to the ambiguity. The analyzer recognizes
400 tokens including duplicates.