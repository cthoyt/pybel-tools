# -*- coding: utf-8 -*-

"""

PyBEL Tools is tested on Python3 on Linux on
`Travis CI <https://travis-ci.org/pybel/pybel-tools>`_.

Installation
------------

Easiest
~~~~~~~
Download the latest stable code from `PyPI <https://pypi.python.org/pypi/pybel-tools>`_ with:

.. code-block:: sh

   $ pip install pybel_tools

Get the Latest
~~~~~~~~~~~~~~~
Download the most recent code from `GitHub <https://github.com/pybel/pybel-tools>`_ with:

.. code-block:: sh

   $ pip install git+https://github.com/pybel/pybel-tools.git
   
   
For Developers
~~~~~~~~~~~~~~
Clone the repository from `GitHub <https://github.com/pybel/pybel-tools>`_ and install in editable mode with:

.. code-block:: sh

   $ git clone https://github.com/pybel/pybel-tools.git
   $ cd pybel-tools
   $ pip install -e .
   
Caveats
-------
PyBEL Tools contains many dependencies, including the scientific Python Stack (numpy, scipy, etc.). This makes 
installation difficult for Windows users, for whom Python cannot easily build C extensions. We recommend using an 
`Anaconda <https://www.continuum.io/downloads>`_ distribution of Python, which includes these precompiled.
"""

from .utils import get_version

__version__ = '0.7.1-dev'

__title__ = 'pybel_tools'
__description__ = 'Tools for using BEL documents in Python'
__url__ = 'https://github.com/pybel/pybel-tools'

__author__ = 'Charles Tapley Hoyt'
__email__ = 'cthoyt@gmail.com'

__license__ = 'Apache License 2.0'
__copyright__ = 'Copyright (c) 2016-2018 Charles Tapley Hoyt'
