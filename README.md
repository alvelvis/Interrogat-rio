# Interrogatório

Interrogatório (Interrogatory) is an enviroment developed and used by the research group ComCorHd (Computational Linguistics, Corpus and Digital Humanities), from the Linguistics Department of PUC-Rio (Brazil) in the scope of the project Linguistic resources for Portuguese Natural Language Processing (loose translation).

Interrogatório is meant to be used for refined queries and revising annotated corpora in the [Universal Dependencies](http://universaldependencies.org) format, and it requires a computer running Linux and Python 3 at least.

To understand better how to use the tools, check our Wiki in the tab above.

You can find a demo of the website at [http://comcorhd.tronco.me/](http://comcorhd.tronco.me/).

# How to install

After downloading the repository and extracting it to a local folder, open a terminal inside it. In order to easen the process of installation, create links for two of the folders to your root folder:

	# sudo ln -rs cgi-bin/ /; sudo ln -rs interrogar-ud/ /

Then, if you don't have a server installed in your computer, you can simply initialize the machine by opening a terminal in the Interrogatório folder and executing the command:

	$ python3 -m http.server --cgi

and accessing the local site [http://localhost:8000/interrogar-ud/](http://localhost:8000/interrogar-ud/).