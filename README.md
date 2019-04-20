# Interrogatório

Interrogatório (Interrogatory) is an enviroment developed and used by the research group ComCorHd (Computational Linguistics, Corpus and Digital Humanities), from the Linguistics Department of PUC-Rio (Brazil) in the scope of the project Linguistic resources for Portuguese Natural Language Processing (loose translation).

Interrogatório is meant to be used for making refined queries and revising annotated corpora in the [Universal Dependencies](http://universaldependencies.org) format, and it requires a computer running Linux and Python 3 at least.

To understand better how to use the tools, check our Wiki in the tab above.

You can find a demo of the website at [http://comcorhd.tronco.me/](http://comcorhd.tronco.me/).

# How to install

The recommended way to download the repository is by simply cloning it. In a terminal, execute:

	$ git clone https://github.com/alvelvis/Interrogat-rio.git

That way, whenever you want to update the repository, you can simply pull the updates inside the folder:

	$ git pull

After downloading the repository, open a terminal inside it. In order to easen the process of installation, create symbolic links for two of the folders to your root folder:

	$ sudo ln -rs cgi-bin/ /; sudo ln -rs interrogar-ud/ /

Then, if you don't have a server installed in your computer, you can simply initialize the machine by opening a terminal in the Interrogatório folder and executing the command:

	$ python3 -m http.server --cgi

All set, you'll be able to access Interrogatório by the local page [http://localhost:8000/interrogar-ud/](http://localhost:8000/interrogar-ud/).
