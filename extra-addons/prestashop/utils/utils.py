# -*- coding: utf-8 -*-
##############################################################################
#
#    Tech Receptives, Open Source For Ideas
#    Copyright (C) 2009-TODAY Tech-Receptives Solutions Pvt. Ltd.
#                            (<http://www.techreceptives.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from xml.etree import ElementTree

# calling example
'''
    ref taken from http://code.activestate.com/
    recipes/573463-converting-xml-to-dictionary-and-back/
    
'''

def main():
    
    configdict = ConvertXmlToDict('test1.xml')

    root = ConvertDictToXml(configdict)

    tree = ElementTree.ElementTree(root)
    
    tree.write('config.new.xml')


# Module Code:

class XmlDictObject(dict):
    
    """
    
    Adds object like functionality to the standard dictionary.
    
    """

    def __init__(self, initdict=None):
        
        if initdict is None:
            
            initdict = {}
            
        dict.__init__(self, initdict)

    def __getattr__(self, item):
        
        return self.__getitem__(item)

    def __setattr__(self, item, value):
        
        self.__setitem__(item, value)

    def __str__(self):
        
        if self.has_key('_text'):
            
            return self.__getitem__('_text')
        
        else:
            
            return ''


def _ConvertDictToXmlRecurse(parent, dictitem):
    
    assert type(dictitem) is not type([])

    if isinstance(dictitem, dict):
        
        for (tag, child) in dictitem.iteritems():
            
            if str('{http://www.w3.org/1999/xlink}href') == str(tag):
                
                continue

            if str(tag) == '_text':
                
                parent.text = unicode(child)

            if str(tag) == 'id' and str(parent.tag) == 'language':
                
                parent.set('id', unicode(child))

            elif type(child) is type([]):
                # iterate through the array and convert
                for listchild in child:
                    
                    elem = ElementTree.Element(tag)
                    parent.append(elem)
                    _ConvertDictToXmlRecurse(elem, listchild)
                    
            else:
                
                if str(tag) == '_text':
                    continue
                
                if str(tag) == 'id' and str(parent.tag) == 'language':
                    continue
                
                elem = ElementTree.Element(tag)
                parent.append(elem)
                _ConvertDictToXmlRecurse(elem, child)
                
    else:
        
        parent.text = unicode(dictitem)

def ConvertDictToXml(xmldict):
    
    """
    
    Converts a dictionary to an XML ElementTree Element
    
    """

    roottag = xmldict.keys()[0]
    root = ElementTree.Element(roottag)
    
    _ConvertDictToXmlRecurse(root, xmldict[roottag])
    
    ret = ElementTree.tostring(root)
    
    return ret

def _ConvertXmlToDictRecurse(node, dictclass):
    
    nodedict = dictclass()

    if len(node.items()) > 0:
        # if we have attributes, set them
        nodedict.update(dict(node.items()))

    for child in node:
        
        # recursively add the element's children
        newitem = _ConvertXmlToDictRecurse(child, dictclass)
        
        if nodedict.has_key(child.tag):
            
            # found duplicate tag, force a list
            if type(nodedict[child.tag]) is type([]):
                # append to existing list
                nodedict[child.tag].append(newitem)
            else:
                # convert to list
                nodedict[child.tag] = [nodedict[child.tag], newitem]
        else:
            # only one, directly set the dictionary
            nodedict[child.tag] = newitem

    if node.text is None:
        text = ''
    else:
        text = node.text.strip()

    if len(nodedict) > 0:
        # if we have a dictionary add the text as a dictionary value (if there is any)
        
        if len(text) > 0:
            nodedict['_text'] = text
    else:
        
        # if we don't have child nodes or attributes, just set the text
        nodedict = text

    return nodedict

def ConvertXmlToDict(root, dictclass=dict):
     
     
    """
    Converts an XML file or ElementTree Element to a dictionary
    
    """
    # If a string is passed in, try to open it as a file
    
    if type(root) == type('') or type(root) == type(u''):
        root = ElementTree.fromstring(root)

    elif not isinstance(root, ElementTree.Element):
        raise TypeError, 'Expected ElementTree.Element or file path string'

    return {root.tag: _ConvertXmlToDictRecurse(root, dictclass)}



def connection(server,object):
    
    if server_check(server):
        
        return True
    
    else:
        
        False
        
    return True

