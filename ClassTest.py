#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Навальный пидор
class TestClass(object):
    __first = 1
    first = 0
    def __init__(self, name):
        self.name = name 
        self.first = self.__first
        self.__class__.__first += 1
        print self.__first
    def change(self, n):
        self.__first = n
    def changeClass(self, n):
        self.__class__.__first = n
    def display(self):        
        return self.__first, self.first
        
one = TestClass('suka')
two = TestClass('nahu')
three = TestClass('shluha')

print one.name, one.display()
print two.name, two.display()
print three.name, three.display()
print '******************'
#one.first = 23
one.change(7)
print one.name, one.display()
print two.name, two.display()
print three.name, three.display()
print '******************'
one.changeClass(5)
print one.name, one.display()
print two.name, two.display()
print three.name, three.display()
print '******************'
print three.__dict__

class Student(object):
    def __init__ (self, c) :
        self.__city=c
    def __f (self, n, y) :
        self.name=n
        self.year=y
        print self.name, "is on the", self.year, "-th year" 

s1=Student("St.Petersburg")
#print s1.__city
#s1.__f ("Vanya", "5")
print s1._Student__city
s1._Student__f("Vanya", "5")
print s1.__dict__

print u'**********************************************************************'

class megatest(object):
    d = {}
    a = []
    def __init__(self, a, b):
        self.d[a] = b
        for i in range(a):
            self.a.append(b)
    def piz(self):
        return megahuega(self.a)        
    def jep(self):
        return mega(self)
    
class megahuega(object):
    a = []    
    def __init__(self, var):
        self.a.append(var)
        self.b = var
        
class mega(object):
    def __init__(self, oc):
        self.oc = oc
        
v1 = megatest(23, 1)
print v1.d, v1.a

v2 = v1.piz()
print v2.a, v2.b
v1.a[1] = 1234

print v1.a
print v2.a, v2.b

v2.b[4] = 'test'

print v1.a
print v2.a, v2.b

print u'**************************************************************************'
v3 = v1.jep()
v3.oc.d['newver'] = '1234wer'
print v3.oc.d, v1.d

print u'****************************************************************************'

#AIs = ['test1', 'test10', 'test2', 'test3']
#DOs = ['test1', 'test2', 'test3']
#
#for AI in AIs:
#    if len(AI)>1:   
#        HHEnbl = True
#        #HEnbl = True
#        #LEnbl = True
#        #LLEnbl = True
#        if len(AI)>2:
#            if len(AI)>3:
#                for DO in DOs:
#                    print DO
#                    if AI == DO:
#                        AI = DO
#                        break                    
#                else:
#                    print u'Регулируемый параметр ', u'не найден у сигнала '
#                    continue
#                print u'do something', AI
#            else:
#                pass
#        else:
#            pass
#    else:
#        print u'Маленькая длина'

        
class NNN(object):
    __n = 0
    a = 1
    def __init__(self):
        self.__class__.__n+=1
        
    def ttt(self):
        self.__class__.__n = 0
        
    def sss(self):
        print self.__n, self.a
        
NNN.a = 3
a = NNN()
a.sss()  
b = NNN()
a.sss()
b.sss()
NNN().ttt()
NNN.a = 0
a.sss()
b.sss()


