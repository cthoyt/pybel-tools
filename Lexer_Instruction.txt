To add and test new lexer :

1)Get the pygment source code from bitbucket repo:
hg clone http://bitbucket.org/birkenfeld/pygments-main pygments

2)To make Pygments aware of your new lexer, you have to perform the following steps:

i)First, change to the current directory containing the Pygments source code:

$ cd .../pygments

Select a matching module under pygments/lexers, or create a new module for your lexer class.Copy the BELLexer.py in that module


ii)The lexer can be made publicly known by rebuilding the lexer mapping:

$ make mapfiles

3)To test the new lexer, store an example file with the proper extension in tests/examplefiles. For example, to test the BELLexer, add a tests/examplefiles/Example.bel containing a sample bel code.

Now you can use pygmentize to render your example to HTML:

$ ./pygmentize -O full -f html -o /tmp/example.html tests/examplefiles/Example.bel

To view the result, open ./example.html in your browser.
