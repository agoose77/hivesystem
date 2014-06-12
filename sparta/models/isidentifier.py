import sys

if (sys.version_info[0] == 3):
    def isidentifier(s):
        return s.isidentifier()
else:
    import re, tokenize, keyword

    def isidentifier(s):
        if keyword.iskeyword(s): return False
        return re.match('^' + tokenize.Name + '$', s) is not None