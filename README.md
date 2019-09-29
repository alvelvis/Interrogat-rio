# Interrogatório

Interrogatório (Interrogatory) is an enviroment for querying and revising annotated corpora in the [Universal Dependencies](http://universaldependencies.org) format. It is being developed and used by the research group [ComCorHd (Computational Linguistics, Corpus and Digital Humanities)](http://comcorhd.letras.puc-rio.br), from the Linguistics Department of PUC-Rio, in Brazil, for the project Linguistic resources for Portuguese Natural Language Processing.

Interrogatório is part of [ET: a workstation for searching, revising and evaluating annotated corpora](http://comcorhd.letras.puc-rio.br/ET).

If you want to run your own version of Interrogatório, a Linux computer and Python 3 are needed. Check our Wiki in the tab above to a deep understanding of Interrogatório tools.

You can also use Interrogatorio at the website [http://comcorhd.letras.puc-rio.br/interrogatorio/](http://comcorhd.letras.puc-rio.br/interrogatorio/), where you are able to query the already available corpora, or upload your own, be it in the UD format or in plain text to be annotated (in Portuguese).

# 4-steps Tutorial

The recommended way to download the repository is by simply cloning it. In a terminal, 1) execute the following command:

	$ git clone https://github.com/alvelvis/Interrogat-rio.git

and 2) change to the newly created directory:

	$ cd Interrogat-rio

That way, whenever you want to update the repository, you can simply pull the updates inside the folder:

	$ git pull

After downloading the repository, 3) open a terminal inside it. Make two links before you can start the server and give them reading and writing permission:

	$ sudo ln -rs www/interrogar-ud/ .; sudo ln -rs www/cgi-bin/ .; sudo chmod -R a+rwx www

Then, if you don't intend to publish the platform in a remote server, 4) you can simply initialize the machine by opening a terminal inside the Interrogatório folder and executing the command:

	$ cd www; python3 -m http.server --cgi; cd ..

All set, you'll be able to access Interrogatório by the local page [http://localhost:8000/interrogar-ud/](http://localhost:8000/interrogar-ud/). End the server by pressing "Ctrl+C" in the terminal window.
