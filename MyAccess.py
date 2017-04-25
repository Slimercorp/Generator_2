#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pyodbc
from MyStardom_lib import ControllerStardom

class AccessBase(object):
    u'''Сбор и обработка данных'''
    
    __args_Chanels = [u'Channel as key' ,  u'Channel']
    
    __args_Controllers = [u'ControllerID as key', u'Rackroom', u'[Система] as System', u'Controller', u'ControllerNo']
    
    __args_Types_of_modules = [u'CardID as key', u'[Система автоматизации] as AutoSystem', \
                               u'CardType', u'CardDescription', u'FRSCode']    
                               
    __args_Table_of_modules = [u'ModuleID as key', u'[Шкаф контроллера] as Cabinet', \
                               u'ControllerID', u'Carrier', u'Position' , u'CardID']    
    
    __args_Type_of_system = [u'[Код системы] as key', u'[Название системы] as Description', u'[ENG_Название системы] as Eng_description', \
                             u'[Номер системы] as System_number', u'[Номер проекта] as ProjectNumber', u'[Система автоматизации] as SysAutomatization']
    
    __args_Types_of_blocks = [u'[Код типа блока] as key', u'[Тип блока] as BlockType', \
                              u'[Тип] as Type', u'[Примечание] as Notation', u'[Система] as System'] 
                              
    __args_Class = [u'[Код] as key', u'[Класс] as Class', \
                    u'[Описание] as Description', u'[Выполнено] as Done'] 
    
    __args_System_automatization = [u'[Код СА] as key', u'[Название СА] as NameSA', u'[Номер СА] as NumberSA']
    
    __args_Unit = [u'[Код единицы измерения] as key', u'[Единица измерения] as unit', \
                   u'[ENG_Единица измерения] as eng_unit', u'[Примечание] as notation']  
                   
    __args_Cabinet = [u'[Код Шкаф] as key', u'[Объект] as Object', \
                      u'[Аппаратная] as equiproom', u'[Шкаф] as Cabinet', u'[Тип шкафа] as CabinetType']    
    
    __args_CabinetType = [u'[Код шкафа] as key', u'[Тип шкафа] as CabinetType']
    
    __args_ObjLevel_1 = [u'[Код объекта1] as key', u'[Объект1] as Object', u'[ENG_Объект1] as Object_eng', \
                         u'[НомерОбъект1] as Num', u'[Примечание] as Notation', u'AOI']
    
    __args_ObjLevel_2 = [u'[Код объекта2] as key', u'[Объект2] as Object', u'[ENG_Объект2] as Object_eng', \
                         u'[НомерОбъект2] as Num', u'[Примечание] as Notation', u'AOI']
                         
    __args_ObjLevel_3 = [u'[Код объекта3] as key', u'[Объект2] as ObjectPrev', u'[Объект3] as Object', \
                         u'[ENG_Объект3] as Object_eng', u'[НомерОбъект3] as Num', u'[Примечание] as Notation', u'AOI']
    
    __args_Displays = [u'[ID] as key', u'[Мнемосхемы] as Displays', u'[Описание] as Description_rus']    
    
    __args_Equipment = [u'[Код] as key', u'[Тег канала] as TagChannel', u'[ШкафКонтролера] as Cabinet', \
                        u'[Модуль] as Module', u'[Канал] as Channel', u'[Тип блока] as BlockType']   
    
    __args_Blocks = [u'[Код] as key', u'[Тег канала] as TagChannel', u'[Позиция по проекту] as PosProject', u'[Тег] as Tag', \
                     u'[Тип блока] as BlockType', u'[Объект1] as Obj1', u'[Объект2] as Obj2', u'[Объект3] as Obj3', \
                     u'[Наименование параметра] as Description_rus', u'[ENG_Наименование параметра] as Description_eng', u'[Дескриптор] as Descriptor', \
                     u'[Нижний ПИП] as SL', u'[Верхний ПИП] as SH', u'LoLo2', u'LoLo', u'Lo1', u'Lo', u'Hi', u'Hi1', u'HiHi', u'HiHi2',\
                     u'[НО/НЗ] as NONC', u'[Сигнализация] as Signalization', u'[Класс] as Class', u'[Мнемосхема] as Display', u'[КонтрольЦепи] as Ccontrol', \
                     u'[Регулируемый параметр] as ControlledVariable', u'[Блокировки] as Blocking', u'[Примечание] as Notation', \
                     u'[Функция блока] as BlockFunction', u'[Тип ИМ] as ActMechType', u'[Единица измерения] as Unit']   
    
    def __init__(self, filepath):
        #print u'Инициализация Базы'
        connStr = u"""
        DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};
        DBQ=
        """
        connStr = connStr + filepath + u';'
        
        db = pyodbc.connect(connStr)
        self.__dbc = db.cursor()
        
        self.System_automatization = self.__GetDataFromBase(u'[Тип Системы Автоматизации]', self.__args_System_automatization)
        self.Type_of_system        = self.__GetDataFromBase(u'[Тип Системы]', self.__args_Type_of_system) 
        self.Types_of_blocks       = self.__GetDataFromBase(u'[Типы блоков]', self.__args_Types_of_blocks) 
        
        self.Channels              = self.__GetDataFromBase(u'[Channels]', self.__args_Chanels) 
        self.Controllers           = self.__GetDataFromBase(u'[Контроллеры]', self.__args_Controllers) 
        self.Types_of_modules      = self.__GetDataFromBase(u'[Типы модулей]', self.__args_Types_of_modules)  
        self.Table_of_modules      = self.__GetDataFromBase(u'[Таблица модулей]', self.__args_Table_of_modules)  
        self.Class                 = self.__GetDataFromBase(u'[Класс]', self.__args_Class)  
        
        self.Cabinet               = self.__GetDataFromBase(u'[Шкафы]', self.__args_Cabinet)  
        self.CabinetType           = self.__GetDataFromBase(u'[Тип шкафа]', self.__args_CabinetType)  
        
        self.ObjLevel1             = self.__GetDataFromBase(u'[Объекты (уровень 1)]', self.__args_ObjLevel_1)  
        self.ObjLevel2             = self.__GetDataFromBase(u'[Объекты (уровень 2)]', self.__args_ObjLevel_2)  
        self.ObjLevel3             = self.__GetDataFromBase(u'[Объекты (уровень 3)]', self.__args_ObjLevel_3)  
        self.Displays              = self.__GetDataFromBase(u'[Мнемосхемы]', self.__args_Displays)  
        
        self.Unit                  = self.__GetDataFromBase(u'[Единицы измерения]', self.__args_Unit) 
        
        self.Equipment             = self.__GetDataFromBase(u'[Оборудование АСУТП]', self.__args_Equipment) 
        self.Blocks                = self.__GetDataFromBase(u'[Блоки]', self.__args_Blocks) 
        
        self.__dbc.close()    
        db.close()  
        
    def __GetDataFromBase(self, table, args):
        u'''Структуризация данных из заданной таблицы'''
        ResultDict = {}        
        DictKey = args.pop(0) #if len(args)>1 else args[0]
        print u'Обработка таблицы', table
        for arg in args: 
            #print arg
            if u' as ' in arg:
                tmp = arg.split(u' as ')
                if len(tmp) != 2:
                    print u'Ошибка с аргументом', arg
                key = tmp[1].strip()                
            else:
                key = arg.strip()
            query = unicode(u'SELECT ' + DictKey + u',' + arg + u' FROM ' + table + u';')                
            try:                
                self.__dbc.execute(query.encode('cp1251'))                
                rows = self.__dbc.fetchall()                
                for row in rows:                   
                    if not ResultDict.get(row.key):
                        ResultDict[row.key] = {}                        
                    ResultDict[row.key][key]=row[1]
            except Exception as ex:
                print u'Ошибка в запросе', query
                print ex
        return ResultDict 
        
    def GiveMeControllers(self):
        #print Base.Controllers
        keys = self.Controllers.keys()
        List = []
        for key in keys:
            b = self.Controllers[key]['System']
            d = self.Type_of_system[b]['SysAutomatization']
            SystemACS = self.System_automatization[d]['NameSA'] 
            if SystemACS == 'Stardom':
                List.append(ControllerStardom(key, self))
            List.sort(key = lambda x: x.Name)
        return List 
    
if __name__ == "__main__":
    Base = AccessBase(u'C:\\Share\\База ИСУБ ЮТГКМ_rev.5.accdb')
    
    Controllers = Base.GiveMeControllers()
    for controller in Controllers:        
        controller.SayParameters()        
        for module in controller.Modules:
            module.SayParameters()
        for signal in controller.Signals:
            signal.SayParameters()
            
            
