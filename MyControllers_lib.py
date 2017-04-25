#!/usr/bin/env python
# -*- coding: utf-8 -*-     
#import MyStardom_lib
from MyFunctions import *
        
class Controller(object):
    u'''Контроллер)'''
    Name = u'' #Имя контроллера 
    SystemACS = u''#Тип системы АСУ ТП
    System = u'' #Тип системы (РСУ ИЛИ ПАЗ)
    Modules = u'' #Модули     
    Signals = u'' #Сигналы
    def __init__(self, ControllerID, DataBase):
        self.Name = DataBase.Controllers[ControllerID]['Controller']
        b = DataBase.Controllers[ControllerID]['System']
        self.System = DataBase.Type_of_system[b]['Description']
        d = DataBase.Type_of_system[b]['SysAutomatization']
        self.SystemACS = DataBase.System_automatization[d]['NameSA']     
        #f = DataBase.Controllers[ControllerID]['Rackroom']
        #g = DataBase.ObjLevel2[f]['Object']    
        self.Modules = self.__GetModulesList(DataBase, ControllerID)
        #self.Signals = self.__GetSignalsList(DataBase)
        #self.__GetActMechList()
        
    def __GetModulesList(self, DataBase, ControllerID):
        List = []
        ModuleID_list = DataBase.Table_of_modules.keys()
        for ModuleID in ModuleID_list:
            if ControllerID ==DataBase.Table_of_modules[ModuleID]['ControllerID']:
                List.append(Module(ModuleID, DataBase))    
        List.sort(key = lambda x: str(x.Carrier) + str(x.Position) )                
        return List   
        
    def SayParameters(self):
        modules = []
        for module in self.Modules:
            modules.append(module.Card)
        print self.Name, self.SystemACS, self.System, modules  

class Module(object):
    u'''Модули'''
    def __init__(self, ModuleID, DataBase):        
        self.ID = ModuleID
        self.Carrier = DataBase.Table_of_modules[ModuleID]['Carrier']
        self.Position = DataBase.Table_of_modules[ModuleID]['Position']
        self.Signals = []
        CardID = DataBase.Table_of_modules[ModuleID]['CardID']
        self.Card = DataBase.Types_of_modules[CardID]['CardType']
        self.CardDescription = DataBase.Types_of_modules[CardID]['CardDescription']
        self.FRSCode = DataBase.Types_of_modules[CardID]['FRSCode']
    def SayParameters(self):
        print self.Carrier, self.Position, self.Card, self.FRSCode, self.CardDescription     
    
class Signal(object):
    u'''Сигналы'''
    def __init__(self, equipID, module, DataBase):
        self.Module = module
        module.Signals.append(self)
        self.Channel = DataBase.Equipment[equipID]['Channel']
        self.TagChannel = DataBase.Equipment[equipID]['TagChannel']     
        BlockType_key = DataBase.Equipment[equipID]['BlockType']     
        self.BlockType = DataBase.Types_of_blocks[BlockType_key]
        
        self.InGroup = False
        self.toHMI = False
        self.toMB = False
        self.Alarming = []
        
        if self.TagChannel:
            blocksIDs = DataBase.Blocks.keys()
            for key in blocksIDs:
                if DataBase.Blocks[key]['TagChannel'] == self.TagChannel:
                    if BlockType_key != DataBase.Blocks[key]['BlockType']:
                        print u'Разные типы блоках в таблицах "Блоки" и "Оборудование АСУ ТП" для:', self.TagChannel
                    self.PosProject = DataBase.Blocks[key]['PosProject']
                    self.Tag = DataBase.Blocks[key]['Tag']
                    self.Description_rus = DataBase.Blocks[key]['Description_rus']
                    self.Description_eng = DataBase.Blocks[key]['Description_eng']
                    self.Descriptor      = DataBase.Blocks[key]['Descriptor']
                    
                    self.Description_rus = self.Description_rus.replace('"', "'") if self.Description_rus else self.Description_rus
                    self.Description_eng = self.Description_eng.replace('"', "'") if self.Description_eng else self.Description_eng
                    self.Descriptor      = self.Descriptor.replace('"', "'")      if self.Descriptor      else self.Descriptor   
                    
                    self.SH = DataBase.Blocks[key]['SH']
                    self.SL = DataBase.Blocks[key]['SL']                    
                    self.HH = DataBase.Blocks[key]['HiHi']
                    self.HI = DataBase.Blocks[key]['Hi']
                    self.LO = DataBase.Blocks[key]['Lo']
                    self.LL = DataBase.Blocks[key]['LoLo']  
                    
                    self.NONC = DataBase.Blocks[key]['NONC']  
                    
                    Obj1_key = DataBase.Blocks[key]['Obj1']   
                    if Obj1_key:
                        self.Obj1 = DataBase.ObjLevel1[Obj1_key]
                    else:
                        self.Obj1 = None
                    
                    Obj2_key = DataBase.Blocks[key]['Obj2']
                    if Obj2_key:
                        self.Obj2 = DataBase.ObjLevel2[Obj2_key]
                    else:
                        self.Obj2 = None
                    
                    Obj3_key = DataBase.Blocks[key]['Obj3']
                    if Obj3_key:
                        self.Obj3 = DataBase.ObjLevel3[Obj3_key]
                    else:
                        self.Obj3 = None
                    
                    Class_key = DataBase.Blocks[key]['Class'] 
                    if Class_key:
                        self.Class = DataBase.Class[Class_key]
                    else:
                        self.Class = None
                    
                    Display_key = DataBase.Blocks[key]['Display']  
                    if Display_key:
                        self.Display = DataBase.Displays[Display_key]
                        
                    Unit_key = DataBase.Blocks[key]['Unit']
                    if Unit_key:
                        self.Unit = DataBase.Unit[Unit_key]
                    else:
                        self.Unit = None
                    
                    self.Blocking = DataBase.Blocks[key]['Blocking']  
                    
                    self.Ccontrol = DataBase.Blocks[key]['Ccontrol']     
                    self.ControlledVariable = DataBase.Blocks[key]['ControlledVariable']     
                    self.Notation = DataBase.Blocks[key]['Notation']   
                    
                    self.BlockFunction = DataBase.Blocks[key]['BlockFunction']   
                    self.ActMechType = DataBase.Blocks[key]['ActMechType']                       
                    
                
    def SayParameters(self):
        print self.TagChannel, self.Module.Card, self.Module.Carrier, self.BlockType['Type'], self.Module.Position, self.Channel
        #print self.__dict__
        
class VirtualSignal(object):
    u'''Виртуальный сигнал'''
    def __init__(self, Attributes):
        u'''Создаем виртуальный сигнал с переданными аттрибутами'''
        for attr, value in Attributes.items():
            self.__dict__[attr] = value

