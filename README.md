# MessengerParser
A parser and regex and date search for the messages.htm files that facebook allows you to download.

## Instructions for use
Have the messages.htm file in the same directory.
### Windows
Open dist/parser.exe.
### Mac/Unix/Linux/Anything else with python and no exe support
You'll need Python 3 and the BeautifulSoup html module. Run parser.py.

## Things you should probably know
It can take (depending on amount of messages and computer CPU) quite a while to parse all the messages, but once it does you can cache them with the fourth option in the search menu. To load from the cache file, select the 'load from cache' option on the first menu.
