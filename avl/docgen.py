#! /usr/bin/env python

class Tree(object):
    def __init__(self, value, children=[], parent=None):
        self.value = value
        self.parent = parent
        self.children = children
    
    def add_child(self, child):
        self.children.append(Tree(child,[],self))
    
    def __str__(self):
        return self.value
    
    def __repr__(self):
        if not self.children:
            return repr(self.value)
            return repr({self.value:[]})
        else:
            return repr({self.value:[repr(child) for child in self.children]})

t = Tree('root')
t.add_child('aa')
t.add_child('ab')
#print repr(t)

#s = open('avl_doc.txt').readlines()
#o = []
#for line in s:

headers = []

#section functions determine if the given line starts a section and if yes returns the depth to be outputted and also changes the depth accordingly
def section1(text, i):
    #'''assertion :len(output) == i-1)'''
    if len(text[i])>0 and len(text[i])==len(text[i+1]) and text[i+1]=='='*len(text[i]):
        headers.append(text[i])
        return 1
    else:
        return 0

def default_section(text, i):
    return 0

sectionizers = [section1, default_section]


def parse(lines):
    output = range(len(lines))
    op = None
    for i in xrange(len(lines)):
        for sectionizer in sectionizers:
            op = sectionizer(lines, i)
            if op is not None:
                break
        output[i] = op
    return output, lines

def section1_render(text, i):
    return '<h1><a name="%s">%s</a></h1><a href="#toc">TOC</a>' % (text[i],text[i])

def default_render(text,i):
    return text[i]

section_renderers = [default_render, section1_render]

def render(text, depth):
    li = ['<a href="#%s">%s</a>' %(t,t) for t in headers]
    toc = '<a name="toc">TOC</a><ul><li>%s</li></ul>' % '</li>\n<li>'.join(li)
    s = []
    for i in xrange(len(depth)):
        s.append(section_renderers[depth[i]](text,i))
    output = '''<html>
<head>
<title>AVL Documentation</title>
</head>
<body>
%s
<br>
%s
</body>
</html>
''' % (toc, '<br>\n'.join(s))
    return output
    
if __name__ == '__main__':
    s = open('avl_doc.txt').readlines()
    s = [l.strip() for l in s]
    o = []
    output, lines = parse(s)
    for i in xrange(len(lines)):
        print output[i], lines[i]
    of = open('avl_doc.html','w')
    of.write(render(lines, output))
    of.close()
