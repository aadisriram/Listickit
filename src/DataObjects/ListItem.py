'''
Created on Feb 9, 2013

@author: aadityasriram
'''
class ListItem:
    items =''
 
    def __init__(self):
        self.items = []

    def addItem(self,item):
        self.items.append(item)

    def retItem(self):
        return self.items