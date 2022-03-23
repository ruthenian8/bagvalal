# Bagvalal Morphology
## Background
[Bagvalal](https://en.wikipedia.org/wiki/Bagvalal_language) is an endangered language from the Nakh-Daghestanian family.
This repository contains a prototype for a Bagvalal morphological analyzer. It is a part of a larger project by the students of the [School of Linguistics](https://ling.hse.ru/en/) at the NRU HSE that aims to provide digital tools for endangered languages.
See the [paper draft](https://docs.google.com/document/d/1-jmHmJKq803GnBjPasgo-X8pdjsX88qaX1eYLcp17Og/edit?usp=sharing) for a detailed description.

You can cite the paper draft using one of the forms listed below:

* Daria Arakelova, Daniil Ignatiev. “Developing morphological analyzers for low-resource languages of the Caucasus”. NRU HSE (2021): 22. pag.
* Аракелова Д., Игнатьев Д. Разработка морфологических анализаторов для малоресурсных языков Кавказа. НИУ ВШЭ. Москва, 2021. 22 с.

A working project demo can be found [here](http://87.247.157.119:5000/parsers). It includes a full-fledge GUI and an API for parsing user-provided texts.

The API specs are available [here](https://github.com/field-nlp-hse/web-project).

The project is distributed under the [GNU General Public License v3.0](https://github.com/ruthenian8/bagvalal/blob/preprocessing/LICENSE).

## Sources

### Grammar

The current work is based on the linguistic description of Bagvalal by A. E. Kibrik et al. (2001) and the Bagvalal dictionary by P. T. Magomedova (2005).

### Texts

The used texts were collected and annotated by a group of MSU students under A. E. Kibrik during field trips to Daghestan that took place in 1997 and 1998.

The texts were transcribed after oral narration and include folk tales and anecdotes. See the [paper draft](https://docs.google.com/document/d/1-jmHmJKq803GnBjPasgo-X8pdjsX88qaX1eYLcp17Og/edit?usp=sharing) for more information.

The texts can be found in the [corpora directory](https://github.com/ruthenian8/bagvalal/tree/preprocessing/corpora). They have been lemmatized with each lemma positioned on a separate line, so as to simplify the measures.

## Usage

To use or extend the analyzer, pull the repository and use the makefile commands described below.

[lexd](https://github.com/apertium/lexd) and [hfst](https://github.com/hfst/hfst) are required to build the project. You can get them by adding Apertium to your apt repositories.
```bash
curl -sS https://apertium.projectjj.com/apt/install-nightly.sh | sudo bash
apt install lexd
apt install hfst
```

You can also build a docker image with all the dependencies, using the provided dockerfile.

### Making the analyzers
cyrillic version:
```bash
make merged.ana.hfst
```
Caucasiologist transcription version
```bash
make merged.tr.hfstol
```

### Running the analyzers
View the statistics:
```bash
make check-coverage-stats
```
* cd to corpora & run make \*corpus name\*.analyzed to analyze with the cyrillic transducer
* cd to corpora & run make \*corpus name\*.tr.analyzed to analyze with the IPA transducer

### Examples:
check and analyze
```bash
make check-coverage-stats
cd corpora
make k_newline.tr.analyzed
```

Current performance: Naive Coverage ~82%

### Platforms:
The project has been tested and is guaranteed to run on Debian and Ubuntu. We make no promises regarding the performance on other platforms.