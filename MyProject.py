#!/usr/bin/env python
# -*- coding: utf-8 -*-
from MyAccess import AccessBase
from MyFastTools_lib import FastTools
import os
import xlwt

class Project(object):
    u'''Проект!! Здесь всё тело программы'''
    def __init__(self, BasePath, ProjectPath):
        self.Base = AccessBase(BasePath)
        self.ProjectPath = ProjectPath
        self.__CheckPath()
        self.FastTools_list = []
     
    def __CheckPath(self, Path = []): 
        u'''Проверяет путь указанный как "путь проекта" и если данная папка не создана - создаёт'''
        folders = self.ProjectPath.split('\\')
        folders = folders + Path
        path = ''
        for folder in folders:
            path = path + folder if path == '' else path + '\\' + folder
            if not os.path.exists(path):
                os.mkdir(path)    
        
    def MakeXLS(self, Path, Table, FileName):
        u'''Запись значений переданных в двумерном массиве в таблицу по указанному пути в папке проекта'''
        try:
            self.__CheckPath(Path)
            wb = xlwt.Workbook()
            sheets = Table.keys()
            sheets.sort(key = lambda x: x.split('|')[0])        
            for sheet in sheets:
                ws = wb.add_sheet(sheet.split('|')[1])
                count_row = 0            
                for row in Table[sheet]:  
                    count_column = 0
                    for column in row:
                        ws.write(count_row,count_column, column)    
                        count_column += 1
                    count_row += 1   
            Path.append(FileName)
            wb.save(self.ProjectPath + '\\' + '\\'.join(Path))    
        except Exception as ex:
            print u'Проблемы с записью файла Excel', Path, row,  ex
        
    def MakeTextFile(self, Path, Rows, FileName):
        u'''Запись строк переданных в списке в текстовый файл по указанному пути в папке проекта'''
        row = ''
        try:
            self.__CheckPath(Path)
            Path.append(FileName)
            f = open(self.ProjectPath + '\\' + '\\'.join(Path),'w')        
            for row in Rows:
                f.write(row)
            f.close()    
        except Exception as ex:
            print u'Проблемы с записью файла txt', Path, row,  ex
        
    def main(self):        
        self.Controllers = self.Base.GiveMeControllers()
        for controller in self.Controllers:
            print u'Обрабатываю контроллер', controller.Name
            #controller.SayParameters()  
            #for v in controller.VirtualSignals:
            #    print v.Name, v.Description  
            #print '****************  ', controller.Name, controller.Redundant, '  ****************'
            #for adress, signal in controller.MBSignals['COILS'].items():
                #print adress, signal.Name, signal.Description
            if controller.Name != 'FCN09':
                print u'Пропускаю'
                continue
                
            
                
            print u'Создаю карту физических входов/выходов'
            self.MakeXLS([controller.Name], controller.GetHardWareTable(), 'DeviceLabelDefinition.xls')              
            
            print u'Создаю программы обработки физических входов/выходов'
            t1AI, t2AI, t1AO, t2AO, t1DI, t2DI, t1DO, t2DO = controller.GetIOFiles()
            
            if len(t2AI)>0:
                self.MakeXLS([controller.Name], t1AI, 'AI.xls')    
                self.MakeTextFile([controller.Name], t2AI, 'AIcode.txt')
            if len(t2AO)>0:
                self.MakeXLS([controller.Name], t1AO, 'AO.xls')    
                self.MakeTextFile([controller.Name], t2AO, 'AOcode.txt') 
            if len(t2DI)>0:
                self.MakeXLS([controller.Name], t1DI, 'DI.xls')    
                self.MakeTextFile([controller.Name], t2DI, 'DIcode.txt')  
            if len(t2DO)>0:    
                self.MakeXLS([controller.Name], t1DO, 'DO.xls')    
                self.MakeTextFile([controller.Name], t2DO, 'DOcode.txt')            
                               
            controller.GetActMechList()
            if len(controller.Engines) > 0:
                print u'Создаю программу обработку Двигателей'
                RowsGlobal = [[u'Name', u'Type', u'Usage', u'Description', u'Address', u'Init', u'Retain', u'PDD', u'OPC']]
                RowsLocal = [[u'Name', u'Type', u'Usage', u'Description', u'Address', u'Init', u'Retain']]
                RowsCode = []
                for engine in controller.Engines:                    
                    RowsGlobal = RowsGlobal + engine.RowsGlobal
                    RowsLocal = RowsLocal + engine.RowsLocal
                    RowsCode = RowsCode + engine.RowsCode
                Table = {u'1|GlobalTags':RowsGlobal, u'2|LocalTags':RowsLocal} 
                self.MakeXLS([controller.Name], Table, 'ENGINE.xls')    
                self.MakeTextFile([controller.Name], RowsCode, 'ENGINEcode.txt')  
                        
            if len(controller.Valves) > 0:
                print u'Создаю программу обработку Задвижек'
                RowsGlobal = [[u'Name', u'Type', u'Usage', u'Description', u'Address', u'Init', u'Retain', u'PDD', u'OPC']]
                RowsLocal = [[u'Name', u'Type', u'Usage', u'Description', u'Address', u'Init', u'Retain']]
                RowsCode = []
                for valve in controller.Valves:                    
                    RowsGlobal = RowsGlobal + valve.RowsGlobal
                    RowsLocal = RowsLocal + valve.RowsLocal
                    RowsCode = RowsCode + valve.RowsCode
                Table = {u'1|GlobalTags':RowsGlobal, u'2|LocalTags':RowsLocal} 
                self.MakeXLS([controller.Name], Table, 'VALVE.xls')    
                self.MakeTextFile([controller.Name], RowsCode, 'VALVEcode.txt')
                           
            if len(controller.PIDs) > 0:
                print u'Создаю программу обработку ПИД'   
                RowsGlobal = [[u'Name', u'Type', u'Usage', u'Description', u'Address', u'Init', u'Retain', u'PDD', u'OPC']]
                RowsLocal = [[u'Name', u'Type', u'Usage', u'Description', u'Address', u'Init', u'Retain']]
                RowsCode = []
                for pid in controller.PIDs:                    
                    RowsGlobal = RowsGlobal + pid.RowsGlobal
                    RowsLocal = RowsLocal + pid.RowsLocal
                    RowsCode = RowsCode + pid.RowsCode
                Table = {u'1|GlobalTags':RowsGlobal, u'2|LocalTags':RowsLocal} 
                self.MakeXLS([controller.Name], Table, 'PID.xls')    
                self.MakeTextFile([controller.Name], RowsCode, 'PIDcode.txt')          
            
            
            FT = FastTools(controller)
            self.FastTools_list.append(FT)
            
            self.MakeTextFile([controller.Name, 'FastTools'], FT.LineRows, FT.LineName + '.qli')
            self.MakeTextFile([controller.Name, 'FastTools'], FT.COMstatusRows, 'COMstatus.qli')
            self.MakeTextFile([controller.Name, 'FastTools'], FT.StationRows, 'Station.qli')
            self.MakeTextFile([controller.Name, 'FastTools'], FT.SectionsRows, 'Sections.qli')
            self.MakeTextFile([controller.Name, 'FastTools'], FT.AOIRows, 'AOIs.qli')
        
            self.MakeTextFile([controller.Name, 'FastTools'], FT.PointRows, 'Points.qli')
            self.MakeTextFile([controller.Name, 'FastTools'], FT.ItemtRows, 'Items.qli')
            
            self.MakeTextFile([controller.Name, 'FastTools'], FT.CMD_i_Rows, '_NewTags.cmd')
            self.MakeTextFile([controller.Name, 'FastTools'], FT.CMD_r_Rows, '_REMOVE_ALL.cmd')
            
            #break
           
     
   
