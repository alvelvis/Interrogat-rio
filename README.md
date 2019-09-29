# Interrogatório

Interrogatório (Interrogatory) is an enviroment developed and used by the research group ComCorHd (Computational Linguistics, Corpus and Digital Humanities), from the Linguistics Department of PUC-Rio, in Brazil, in the scope of the project Linguistic resources for Portuguese Natural Language Processing (loose translation).

Interrogatório is meant to be used for making refined queries and revising annotated corpora in the [Universal Dependencies](http://universaldependencies.org) format, and it requires a computer running Linux and Python 3 at least in order to run your own version of it.

To understand better how the tools work, check our Wiki in the tab above.

You can also use Interrogatorio at the website [https://comcorhd.letras.puc-rio.br/interrogatorio/](https://comcorhd.letras.puc-rio.br/interrogatorio/).

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
