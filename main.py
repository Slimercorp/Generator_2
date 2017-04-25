#!/usr/bin/env python
# -*- coding: utf-8 -*-
from MyProject import Project

#Путь к базе проекта. Одинарный слеш "\", заменяется на двойной "\"
BasePath = u'C:\\Share\\test.accdb'
#Путь к папке прокта. Одинарный слеш "\", заменяется на двойной "\"
ProjectPath = u'C:\\Share\\TestPrj\\'

Isub = Project(BasePath, ProjectPath)
Isub.main()

print (u'Обработка закончена')
