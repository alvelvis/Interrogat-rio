# Interrogatório

Interrogatório (Interrogatory) is an enviroment for querying and revising annotated corpora in the [CoNLL-U](https://universaldependencies.org/format.html) format. It is available in Portuguese and English, depending on the user's web browser language, and it's being developed and used by the research group [ComCorHd (Computational Linguistics, Corpus and Digital Humanities)](http://comcorhd.letras.puc-rio.br), from the Linguistics Department of PUC-Rio, in Brazil, for the project Linguistic resources for Portuguese Natural Language Processing.

Interrogatório is part of [ET: a workstation for querying, revising and evaluating annotated corpora](http://comcorhd.letras.puc-rio.br/ET). Consider also installing [Julgamento](https://github.com/alvelvis/Julgamento), an enviroment for evaluating annotated corpora, in the same folder as Interrogatório to integrate both.

If you wish to deploy Interrogatório to a web server, using Ubuntu/Apache2, check [Deploying with Ubuntu/Apache2](https://github.com/alvelvis/Interrogat-rio/wiki/Deploying-with-Ubuntu-Apache2).

Check the [Wiki](https://github.com/alvelvis/Interrogat-rio/wiki) for a broader understanding of Interrogatório tools.

<!---You can also use Interrogatório at the website [http://comcorhd.letras.puc-rio.br/interrogatorio/](http://comcorhd.letras.puc-rio.br/interrogatorio/), where you are able to query the already available corpora, or upload your own, be it in the UD format or in plain text to be annotated (in Portuguese).-->

# How to install in a local server: 4-steps Tutorial

If you wish to run Interrogatório in a local server, a Linux computer (or Windows with [Windows Subsystem for Linux](https://docs.microsoft.com/pt-br/windows/wsl/install-win10)), `python3` and `virtualenv` are needed.

1) The recommended way to download the repository is by cloning it. In a terminal, execute the following command:

	$ git clone https://github.com/alvelvis/Interrogat-rio.git

2) Change to the newly created directory:

	$ cd Interrogat-rio

3) After downloading the repository, run the command below, and it will then create a Python 3 virtual environment and install the requirements in order to run Interrogatório.

	$ sh install_interrogatorio.sh
	
4) Then, whenever you intend to run Interrogatório locally, run the command below and it will also auto-update when necessary if you cloned the repo using Git:

	$ sh run_interrogatorio.sh

All set, you'll be able to access Interrogatório by the local page [http://localhost:8000/](http://localhost:8000/). End the server by pressing "Ctrl+C" in the terminal window.

# How to cite

```
@inproceedings{ETtilic,
  title={ET: uma Estação de Trabalho para revisão, edição e avaliação de corpora anotados morfossintaticamente},
  author={de Souza, Elvis and Freitas, Cl{\'a}udia},
  booktitle={VI Workshop de Iniciação Científica em Tecnologia da Informação e da Linguagem Humana (TILic 2019)},
  place={Salvador, BA, Brazil, Outubro, 15-18, 2019},
  year={2019}
}
```

