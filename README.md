# Nau Engine Documentation

Nau Engine is a free open-source game engine that's designed to be versatile and accessible to everyone. 

It's free: no limitations, royalties or other fees apply. Nau Engine will always be free for any purpose, including commercial use.
It's open: the entire source code is stored in a GIT repository. Anyone is able to use it for educational purposes or work with it as they wish.
It's open-source: anyone has the opportunity to participate in developing the engine without restrictions, creating forks and add-ons based on it.

[Engine build instructions](https://nauengine.org/docs/beta/user-doc/introduction_to_nau/install_nau/install_nau_doc.html)

## Documentation

Nau Engine has open API documentation and user documentation, describing the engine, its interface, workflow and all core modules. You can edit and build documentation using Sphinx.

## Installing Sphinx

In order to install Sphinx, you first need to install:

 - Python (3.10 or later version is required for installing Nau Engine as well),
 - Pip package manager.
 
Additionally, for API documentantion you will require **anytree** package:

> pip install anytree

Then, run the following command:

> pip install -U sphinx

After this, you will need to install additional Sphinx packages:

> pip install sphinx-copybutton
> pip install sphinx-design
> pip install furo
> pip install sphinx-inline-tabs
> pip install breathe

For more information, see [Sphinx Installation guide.](https://www.sphinx-doc.org/en/master/usage/installation.html)

## API documentation

Clone the documentation repository. In order for API to be built correctly, you need to place NauDocs and NauEngine folders on the same level. In NauDocs folder you will see a variety of scripts for building documentation.

Run **update_api** first, either by double clicking on it, or running it from terminal. You will need to specify the version of the documentation you wish to build. Then, run **build_api** the same way.

The HTML pages for API documentation will be placed into "build/[version]/api-doc/generated_content" folder.

## User documentation



In order to build user documentation, run **build_user** script and specify the version of user documentation. The HTML pages for user documentation will be placed into "build/[version]/user-doc" folder.  

Alternatively, open Terminal and change directory path to NauDocs. Then, run:

> sphinx-build -M html source/dev/user-doc build
