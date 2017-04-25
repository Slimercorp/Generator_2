#!/usr/bin/env python
# -*- coding: utf-8 -*-        
from MyControllers_lib import *
from MyFunctions import *

class ControllerStardom(Controller):
    u'''Контроллер Stardom'''
    def __init__(self, ControllerID, DataBase):
        Controller.__init__(self, ControllerID, DataBase)   
        self.Redundant = self.__CheckRedundant()
        self.Signals = self.__GetSignalsList(DataBase)  
        self.__SignalsByTypes()      
   
        self.COIL = 100
        self.HREG = 100
        self.MBSignals = {'COILS':{}, 'HREGS':{}}        
        
        self.VirtualSignals = []
        self.__MakeDiagnosticSignals()
        
        self.Engines = []
        self.Valves = []
        self.PIDs = []
        #self.__GetActMechList()  
        
    def __GetSignalsList(self, DataBase):
        List = []
        EquipmentACS_list = DataBase.Equipment.keys()
        #Block_list = DataBase.Blocks.keys()
        for equip in EquipmentACS_list: 
            ModuleID = DataBase.Equipment[equip]['Module']
            for module in self.Modules:
                if ModuleID == module.ID:
                    #print DataBase.Equipment[equip]['TagChannel']   
                    List.append(Signal(equip, module, DataBase)) 
        return List    
        
    def __CheckRedundant(self):
        Result = True
        for module in self.Modules:
            #print module.Carrier, module.Position
            if module.Carrier == 1 and (module.Position == '03' or module.Position == '04'):
                Result = False        
        return Result
        
    def __SignalsByTypes(self):
        self.AIs = []
        self.DIs = []
        self.AOs = []
        self.DOs = []
        for module in self.Modules:            
            module.Signals.sort(key = lambda x: x.Channel)
            for signal in module.Signals:
                #if signal.__dict__.get('Description_rus'):
                    #print self.Name
                    #print signal.TagChannel, signal.Ccontrol, signal.ControlledVariable 
                    #if signal.Ccontrol:
                        #print u'Fuck YEA'
                if signal.BlockType['Type'] == 'AI':
                    self.AIs.append(signal)                    
                elif signal.BlockType['Type'] == 'DI':
                    self.DIs.append(signal)
                elif signal.BlockType['Type'] == 'AO':
                    self.AOs.append(signal)
                elif signal.BlockType['Type'] == 'DO':
                    self.DOs.append(signal)        
        
    def GetHardWareTable(self):
        u'''Описание входов/выходов контроллера'''
        Rows = [[u'Device label name', u'Comment', u'I//O Category', u'Task', u'Scale Low Limit', u'Scale High Limit', u'Engineering Unit']]
        for module in self.Modules:            
            module.Signals.sort(key = lambda x: x.Channel)
            for signal in module.Signals:
                IO = 'XX'
                IOCategory = ''
                if signal.BlockType['Type']:
                    if signal.BlockType['Type'][1] == 'I':
                        IOCategory = 'I'
                        IO = 'I'
                    elif signal.BlockType['Type'][1] == 'O':
                        IOCategory = 'O'
                        IO = 'Q'     
                    else:
                        continue
                    if signal.BlockType['Type'][0] == 'A':
                        IOCategory = IOCategory + '_Anlg'
                        SH = u'20.0'
                        SL = u'4.0'
                        Unit = signal.Unit['unit'] if signal.__dict__.get('Unit') else ''
                    elif signal.BlockType['Type'][0] == 'D':
                        IOCategory = IOCategory + '_Sts'  
                        SH = u''
                        SL = u''
                        Unit = u''
                    else:
                        continue
                else:
                    print module.Carrier, module.Position, signal.Channel, u'Отсутсвует "Тип Блока"'
                DeviceTag = IO + '_' + str(module.Carrier).zfill(2) + '_' + str(module.Position).zfill(2) + '_' + str(signal.Channel).zfill(2) 
                signal.DeviceTag = DeviceTag
                Rows.append([DeviceTag, signal.Description_rus if signal.__dict__.get('Description_rus') else u'', IOCategory, u'', SL, SH, Unit])
        Table = {u'1|IOPoints':Rows}
        return Table   
    
    def GetIOFiles(self):
        GlobalColumns = [u'Name', u'Type', u'Usage', u'Description', u'Address', u'Init', u'Retain', u'PDD', u'OPC']
        LocalColumns = [u'Name', u'Type', u'Usage', u'Description', u'Address', u'Init', u'Retain']
        
        RowsAIglobal = [GlobalColumns]
        RowsAIlocal = [LocalColumns]
        RowsAIcode = []
        count = 1
        for AI in self.AIs:
            if AI.TagChannel:                 
                AI.VirtualSignals = []  
                AI.toHMI = True
                AI.toMB = True
                RowsAIlocal.append([AI.DeviceTag, 'DTag_I_Anlg', 'VAR_EXTERNAL', AI.Description_rus])                
                if AI.Ccontrol: # Проверка: яв-ся ли сигнало проверкой целостности цепи
                    RowsAIglobal.append([AI.TagChannel, 'BOOL', 'VAR_GLOBAL', AI.Description_rus, '', '', 0, 0, 1])
                    RowsAIlocal.append([AI.TagChannel, 'BOOL', 'VAR_EXTERNAL', AI.Description_rus])     
                    if AI.ControlledVariable: #Если есть "Регулируемый параметр", то контроль цепи дискретного ВЫХОДНОГО сигнала
                        for DO in self.DOs:
                            if AI.ControlledVariable == DO.TagChannel:
                                AI.ControlledVariable = DO
                                AI.InGroup = True
                                DO.InGroup = True
                                DO.ControlSignal = AI
                                break
                        else: 
                            print u'Регулируемый параметр ', AI.ControlledVariable, u'не найден у сигнала ', AI.TagChannel
                            RowsAIcode.append('(*Аналоговый вход ' + str(AI.DeviceTag) + ' Тег канала ' + str(AI.TagChannel) + ' *)\n')
                            RowsAIcode.append('\n')                            
                            continue # Если мы не нашли "Регулируемый параметр", то переходим к следующему AI сигналу во внешнем цикле                                    
                        
                        AI.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'В норме'}, 
                                       {'IT_ST':'BOOLEAN 1', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'SCC', 'SH_EN':'', 'AL_TXT': u'Обрыв или КЗ'}]
                        
                        RowsAIlocal.append([AI.ControlledVariable.TagChannel, 'BOOL', 'VAR_EXTERNAL', AI.ControlledVariable.Description_rus])                                                
                        RowsAIlocal.append(['AI_DO_' + str(count), 'AI_DO', 'VAR', u'Обработка AI в качестве контроля целостности цепи DO'])
                        
                        RowsAIcode.append('(*Аналоговый вход ' + str(AI.DeviceTag) + ' Тег канала ' + str(AI.TagChannel) + ' *)\n')
                        RowsAIcode.append('AI_DO_' + str(count) + '(IN_AI:=' + str(AI.DeviceTag) + ',IN_DO:=' + AI.ControlledVariable.TagChannel + ');\n')
                        RowsAIcode.append('(*[Paste tagname here for ma value]:=AI_DO_' + str(count) + '.OUT_AI;*)\n')
                        RowsAIcode.append(str(AI.TagChannel) + ':=AI_DO_' + str(count) + '.OUT_A;\n')
                        RowsAIcode.append('\n')                        
                    else: #Иначе если "Регулируемый параметр" отсутствует, то контроль цепи дискретного ВХОДНОГО сигнала    
                        attributes = {'Name': SCCsignal(AI), 
                                      'Description': AI.TagChannel + u' - Контроль целостности цепи', 
                                      'toHMI': True, 
                                      'toMB': True, 
                                      'Type': 'Bool', 
                                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'В норме'}, 
                                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'SCC', 'SH_EN':'', 'AL_TXT': u'Обрыв или КЗ'}],                                      
                                      'Editable': 'False'}
                        SCC = VirtualSignal(attributes)
                        AI.VirtualSignals.append(SCC)   
                        AI.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                       {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}]
                        
                        RowsAIglobal.append([SCC.Name, SCC.Type.upper(), 'VAR_GLOBAL',   SCC.Description, '', '', 0, 0, 1])
                        RowsAIlocal.append([ SCC.Name, SCC.Type.upper(), 'VAR_EXTERNAL', SCC.Description])    
                        RowsAIlocal.append(['AI_D1L_' + str(count), 'AI_D1L', 'VAR', u'Обработка AI в качестве контроля целостности цепи DI'])
                    
                        RowsAIcode.append('(*Аналоговый вход ' + str(AI.DeviceTag) + ' Тег канала ' + str(AI.TagChannel) + ' *)\n')
                        RowsAIcode.append('AI_D1L_' + str(count) + '(IN_AI:=' + str(AI.DeviceTag) + ',IN_L1H:=REAL#18.5,IN_L1L:=REAL#17.5);\n')
                        RowsAIcode.append('(*' + '[Paste tagname here for ma value]' + ':=AI_D1L_' + str(count) + '.OUT_AI;*)\n')
                        RowsAIcode.append(str(AI.TagChannel) + ':=AI_D1L_' + str(count) + '.OUT_B1;\n')
                        RowsAIcode.append(str(SCC.Name) + ':=AI_D1L_' + str(count) + '.OUT_A;\n')
                        RowsAIcode.append('\n')
                else: 
                    HHEnbl = False
                    HEnbl = False
                    LEnbl = False
                    LLEnbl = False 
                    AOFtoHMIMB = True
                    RowsAIglobal.append([AI.TagChannel, 'REAL', 'VAR_GLOBAL', AI.Description_rus, '', '', 0, 0, 1])
                    RowsAIlocal.append([AI.TagChannel, 'REAL', 'VAR_EXTERNAL', AI.Description_rus])
                    
                    if AI.Class:
                        if AI.Class['Class']:
                            LimitsString = AI.Class['Class']
                            if LimitsString == 'Nope':
                                AOFtoHMIMB = False
                            if 'HH' in LimitsString:
                                LimitsString = LimitsString.replace('HH', '')
                                HHEnbl = True                                                      
                            if 'LL' in LimitsString:
                                LimitsString = LimitsString.replace('LL', '')
                                LLEnbl = True 
                            if 'H' in LimitsString:
                                LimitsString = LimitsString.replace('H', '')
                                HEnbl = True                       
                            if 'L' in LimitsString:
                                LimitsString = LimitsString.replace('L', '')
                                LEnbl = True
                            
                    else:
                        HHEnbl = True
                        HEnbl = True
                        LEnbl = True
                        LLEnbl = True   
                        #print HHEnbl, HEnbl, LEnbl, LLEnbl 
                    
                    AI.Alarming = []
                    
                    attributes = {'Name': HHsignal(AI), 
                                  'Description': AI.TagChannel + u' - Уставка ВАУ', 
                                  'Type': 'Real', 
                                  'toHMI': HHEnbl, 
                                  'toMB': HHEnbl, 
                                  'Alarming': [],
                                  'Storage':'1',
                                  'ProcArea':'30', 
                                  'Editable': 'True'}
                    HH = VirtualSignal(attributes)
                    AI.VirtualSignals.append(HH)                    
                    
                    attributes = {'Name': HHEsignal(AI), 
                                  'Description': AI.TagChannel + u' - Состояние ВАУ', 
                                  'Type': 'Bool', 
                                  'toHMI': False, 
                                  'toMB': False, 
                                  'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'Выключен'}, 
                                               {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'Включен'}],                                  
                                  'Editable': 'True'}
                    HHstate = VirtualSignal(attributes)
                    AI.VirtualSignals.append(HHstate)                   
                    
                    attributes = {'Name': HHDsignal(AI), 
                                  'Description': AI.TagChannel + u' - Задержка ВАУ', 
                                  'Type': 'Time', 
                                  'toHMI': False, 
                                  'toMB': False, 
                                  'Alarming': [],
                                  'Editable': 'True'}
                    HHdelay = VirtualSignal(attributes)
                    AI.VirtualSignals.append(HHdelay)
                    
                    attributes = {'Name': Hsignal(AI), 
                                  'Description': AI.TagChannel + u' - Уставка ВПУ', 
                                  'Type': 'Real', 
                                  'toHMI': HEnbl, 
                                  'toMB': HEnbl, 
                                  'Alarming': [],
                                  'Storage':'1',
                                  'ProcArea':'30',
                                  'Editable': 'True'}
                    H = VirtualSignal(attributes)
                    AI.VirtualSignals.append(H) 
                    
                    attributes = {'Name': HEsignal(AI), 
                                  'Description': AI.TagChannel + u' - Включение ВПУ', 
                                  'Type': 'Bool', 
                                  'toHMI': False, 
                                  'toMB': False, 
                                  'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'Выключен'}, 
                                               {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'Включен'}],
                                  'Editable': 'True'}
                    Hstate = VirtualSignal(attributes)
                    AI.VirtualSignals.append(Hstate)
                    
                    attributes = {'Name': HDsignal(AI), 
                                  'Description': AI.TagChannel + u' - Задержка ВПУ', 
                                  'Type': 'Time', 
                                  'toHMI': False, 
                                  'toMB': False, 
                                  'Alarming': [],
                                  'Editable': 'True'}
                    Hdelay = VirtualSignal(attributes)
                    AI.VirtualSignals.append(Hdelay)
                    
                    attributes = {'Name': Lsignal(AI), 
                                  'Description': AI.TagChannel + u' - Уставка НПУ', 
                                  'Type': 'Real', 
                                  'toHMI': LEnbl, 
                                  'toMB': LEnbl,
                                  'Storage':'1',
                                  'ProcArea':'30', 
                                  'Alarming': [],
                                  'Editable': 'True'}
                    L = VirtualSignal(attributes)
                    AI.VirtualSignals.append(L) 
                    
                    attributes = {'Name': LEsignal(AI), 
                                  'Description': AI.TagChannel + u' - Включение НПУ', 
                                  'Type': 'Bool', 
                                  'toHMI': False, 
                                  'toMB': False, 
                                  'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'Выключен'}, 
                                               {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'Включен'}],
                                  'Editable': 'True'}
                    Lstate = VirtualSignal(attributes)
                    AI.VirtualSignals.append(Lstate) 
                    
                    attributes = {'Name': LDsignal(AI), 
                                  'Description': AI.TagChannel + u' - Задержка НПУ', 
                                  'Type': 'Time', 
                                  'toHMI': False, 
                                  'toMB': False, 
                                  'Alarming': [],
                                  'Editable': 'True'}
                    Ldelay = VirtualSignal(attributes)
                    AI.VirtualSignals.append(Ldelay) 
                    
                    attributes = {'Name': LLsignal(AI), 
                                  'Description': AI.TagChannel + u' - Уставка НАУ', 
                                  'Type': 'Real', 
                                  'toHMI': LLEnbl, 
                                  'toMB': LLEnbl, 
                                  'Alarming': [],
                                  'Storage':'1',
                                  'ProcArea':'30',
                                  'Editable': 'True'}
                    LL = VirtualSignal(attributes)
                    AI.VirtualSignals.append(LL)  
                    
                    attributes = {'Name': LLEsignal(AI), 
                                  'Description': AI.TagChannel + u' - Включение НАУ', 
                                  'Type': 'Bool',
                                  'toHMI': False, 
                                  'toMB': False, 
                                  'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'Выключен'}, 
                                               {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'Включен'}], 
                                  'Editable': 'True'}
                    LLstate = VirtualSignal(attributes)
                    AI.VirtualSignals.append(LLstate) 
                    
                    attributes = {'Name': LLDsignal(AI), 
                                  'Description': AI.TagChannel + u' - Задержка НАУ', 
                                  'Type': 'Time', 
                                  'toHMI': False, 
                                  'toMB': False, 
                                  'Alarming': [],
                                  'Editable': 'True'}
                    LLdelay = VirtualSignal(attributes)
                    AI.VirtualSignals.append(LLdelay)     
                    
                    attributes = {'Name': RSLsignal(AI), 
                                  'Description': AI.TagChannel + u' - Нижний порог сырого значения', 
                                  'Type': 'Real',
                                  'toHMI': False, 
                                  'toMB': False, 
                                  'Alarming': [], 
                                  'Editable': 'True'}
                    RSL = VirtualSignal(attributes)
                    AI.VirtualSignals.append(RSL) 
                    
                    attributes = {'Name': RSHsignal(AI), 
                                  'Description': AI.TagChannel + u' - Верхний порог сырого значения', 
                                  'Type': 'Real',
                                  'toHMI': False, 
                                  'toMB': False, 
                                  'Alarming': [], 
                                  'Editable': 'True'}
                    RSH = VirtualSignal(attributes)
                    AI.VirtualSignals.append(RSH) 
                    
                    attributes = {'Name': ESLsignal(AI), 
                                  'Description': AI.TagChannel + u' - Нижний порог значения в инженерных единицах', 
                                  'Type': 'Real',
                                  'toHMI': False, 
                                  'toMB': False, 
                                  'Alarming': [], 
                                  'Editable': 'True'}
                    ESL = VirtualSignal(attributes)
                    AI.VirtualSignals.append(ESL) 
                    
                    attributes = {'Name': ESHsignal(AI), 
                                  'Description': AI.TagChannel + u' - Верхний порог значения в инженерных единицах', 
                                  'Type': 'Real', 
                                  'toHMI': False, 
                                  'toMB': False, 
                                  'Alarming': [], 
                                  'Editable': 'True'}
                    ESH = VirtualSignal(attributes)
                    AI.VirtualSignals.append(ESH) 
                    
                    attributes = {'Name': ERRsignal(AI), 
                                  'Description': AI.TagChannel + u' - Возможное отклонение в процентах сырого значения от заданных порогов', 
                                  'Type': 'Real',
                                  'toHMI': False, 
                                  'toMB': False, 
                                  'Alarming': [], 
                                  'Editable': 'True'}
                    ERR = VirtualSignal(attributes)
                    AI.VirtualSignals.append(ERR) 
                    
                    attributes = {'Name': HYSsignal(AI), 
                                  'Description': AI.TagChannel + u' - Гистерезис', 
                                  'Type': 'Real',
                                  'toHMI': False, 
                                  'toMB': False, 
                                  'Alarming': [], 
                                  'Editable': 'True'}
                    HYS = VirtualSignal(attributes)
                    AI.VirtualSignals.append(HYS)  
                    
                    attributes = {'Name': AOFsignal(AI), 
                                  'Description': AI.TagChannel + u' - Отлючение сигнализаций', 
                                  'Type': 'Bool',
                                  'toHMI': AOFtoHMIMB, 
                                  'toMB': AOFtoHMIMB, 
                                  'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'Включены'}, 
                                               {'IT_ST':'BOOLEAN 1', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'Выключены'}],                                   
                                  'ProcArea':'30',
                                  'Editable': 'True'}
                    AOF = VirtualSignal(attributes)
                    AI.VirtualSignals.append(AOF)                     
                    
                    attributes = {'Name': AHHsignal(AI), 
                                  'Description': AI.TagChannel + u' - Аларм HH', 
                                  'Type': 'Bool',
                                  'toHMI': False, 
                                  'toMB': False, 
                                  'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                               {'IT_ST':'BOOLEAN 1', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'1'}], 
                                  'Editable': 'False'}
                    AHH = VirtualSignal(attributes)
                    AI.VirtualSignals.append(AHH) 
                    
                    attributes = {'Name': AHsignal(AI), 
                                  'Description': AI.TagChannel + u' - Аларм H', 
                                  'Type': 'Bool',
                                  'toHMI': False, 
                                  'toMB': False, 
                                  'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                               {'IT_ST':'BOOLEAN 1', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'1'}], 
                                  'Editable': 'False'}
                    AH = VirtualSignal(attributes)
                    AI.VirtualSignals.append(AH) 
                    
                    attributes = {'Name': ALsignal(AI), 
                                  'Description': AI.TagChannel + u' - Аларм L', 
                                  'Type': 'Bool',
                                  'toHMI': False, 
                                  'toMB': False, 
                                  'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                               {'IT_ST':'BOOLEAN 1', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'1'}], 
                                  'Editable': 'False'}
                    AL = VirtualSignal(attributes)
                    AI.VirtualSignals.append(AL) 
                    
                    attributes = {'Name': ALLsignal(AI), 
                                  'Description': AI.TagChannel + u' - Аларм LL', 
                                  'Type': 'Bool',
                                  'toHMI': False, 
                                  'toMB': False, 
                                  'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                               {'IT_ST':'BOOLEAN 1', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'1'}], 
                                  'Editable': 'False'}
                    ALL = VirtualSignal(attributes)
                    AI.VirtualSignals.append(ALL)  
                    
                    attributes = {'Name': IOPPsignal(AI), 
                                  'Description': AI.TagChannel + u' - Аларм КЗ', 
                                  'Type': 'Bool',
                                  'toHMI': False, 
                                  'toMB': False, 
                                  'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                               {'IT_ST':'BOOLEAN 1', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'1'}], 
                                  'Editable': 'False'}
                    IOPP = VirtualSignal(attributes)
                    AI.VirtualSignals.append(IOPP) 
                    
                    attributes = {'Name': IOPMsignal(AI), 
                                  'Description': AI.TagChannel + u' - Аларм обрыв', 
                                  'Type': 'Bool',
                                  'toHMI': False, 
                                  'toMB': False, 
                                  'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                               {'IT_ST':'BOOLEAN 1', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'1'}], 
                                  'Editable': 'False'}
                    IOPM = VirtualSignal(attributes)
                    AI.VirtualSignals.append(IOPM) 
                    
                    attributes = {'Name': Asignal(AI), 
                                  'Description': AI.TagChannel + u' - Аларм для FastTools', 
                                  'Type': 'DWORD', 
                                  'toHMI': True, 
                                  'toMB': True,
                                  'Representation': ['Alarm status word', 'Integer'],  
                                  'Alarming': [{'IT_ST':'OPEN INPUT+', 'AL_ST':'Alarm 1', 'PRIOR':'3', 'AL_CLR':'cyan',   'MNEM':'IOP+', 'SH_EN':'', 'AL_TXT': u'КЗ'},
                                               {'IT_ST':'OPEN INPUT-', 'AL_ST':'Alarm 1', 'PRIOR':'3', 'AL_CLR':'cyan',   'MNEM':'IOP-', 'SH_EN':'', 'AL_TXT': u'Обрыв'},
                                               {'IT_ST':'HIGH HIGH',   'AL_ST':'Alarm 3', 'PRIOR':'1', 'AL_CLR':'red',    'MNEM':'HH',   'SH_EN':'', 'AL_TXT': u'Верхний аварийный порог'},
                                               {'IT_ST':'HIGH',        'AL_ST':'Alarm 2', 'PRIOR':'2', 'AL_CLR':'yellow', 'MNEM':'HI',   'SH_EN':'', 'AL_TXT': u'Верхний предупредительный порог'},
                                               {'IT_ST':'LOW',         'AL_ST':'Alarm 2', 'PRIOR':'2', 'AL_CLR':'yellow', 'MNEM':'LO',   'SH_EN':'', 'AL_TXT': u'Нижний предупредительный порог'}, 
                                               {'IT_ST':'LOW LOW',     'AL_ST':'Alarm 3', 'PRIOR':'1', 'AL_CLR':'red',    'MNEM':'LL',   'SH_EN':'', 'AL_TXT': u'Нижний аварийный порог'}],
                                  'Editable': 'False'}
                    A = VirtualSignal(attributes)
                    AI.VirtualSignals.append(A)                    
                    
                    #print AI.TagChannel, AI.SL, AI.SH, AI.HH, AI.HI, AI.LO, AI.LL                    
                    try:
                        AI.SL = str(AI.SL).replace(',', '.') if AI.SL else '0.0'
                    except:
                        print u'Проблема с значением SL', AI.TagChannel, u' -> ', AI.SL, u'Значение взято по умолчанию'
                        AI.SL = '0.0'
                    
                    try:
                        AI.SH = str(AI.SH).replace(',', '.') if AI.SH else '100.0'
                    except:    
                        print u'Проблема с значением SH', AI.TagChannel, u' -> ', AI.SH, u'Значение взято по умолчанию'
                        AI.SH = '100.0'
                    
                    try:
                        AI.HH = str(float(str(AI.HH).replace(',', '.'))) if AI.HH else AI.SH
                    except:
                        print u'Проблема с значением HH', AI.TagChannel, u' -> ', AI.HH, u'Значение взято по умолчанию'
                        AI.HH = AI.SH
                        
                    try:
                        AI.HI = str(float(str(AI.HI).replace(',', '.'))) if AI.HI else AI.SH
                    except:
                        print u'Проблема с значением HI', AI.TagChannel, u' -> ', AI.HI, u'Значение взято по умолчанию'
                        AI.HI = AI.SH
                        
                    try:
                        AI.LO = str(float(str(AI.LO).replace(',', '.'))) if AI.LO else AI.SL
                    except:
                        print u'Проблема с значением LO', AI.TagChannel, u' -> ', AI.LO, u'Значение взято по умолчанию'
                        AI.LO = AI.SL
                    
                    try:
                        AI.LL = str(float(str(AI.LL).replace(',', '.'))) if AI.LL else AI.SL
                    except:
                        print u'Проблема с значением LL', AI.TagChannel, u' -> ', AI.LL, u'Значение взято по умолчанию'
                        AI.LL = AI.SL                    
                    #print AI.TagChannel, AI.SL, AI.SH, AI.HH, AI.HI, AI.LO, AI.LL    
                    
                    RowsAIlocal.append(['SENS_AI_' + str(count), 'SENS_AI', 'VAR', u'Обработка AI'])   
                   
                    if AI.Blocking:                    
                        attributes = {'Name': DBsignal(AI), 
                                      'Description': AI.TagChannel + u' - Деблокировка', 
                                      'Type': 'Bool', 
                                      'toHMI': True, 
                                      'toMB': True, 
                                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'Выключена'}, 
                                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'Включена'}],                                       
                                      'ProcArea':'31',  
                                      'Editable': 'True'}
                        DB = VirtualSignal(attributes)
                        AI.VirtualSignals.append(DB)
                        RowsAIglobal.append([DB.Name, DB.Type.upper(), 'VAR_GLOBAL', DB.Description, '', '', 0, 0, 1]) 
                    
                    RowsAIglobal.append([HH.Name,      HH.Type.upper(),      'VAR_GLOBAL',   HH.Description, '', AI.HH, 1, 0, 1])
                    #RowsAIglobal.append([HHstate.Name, HHstate.Type.upper(), 'VAR_GLOBAL',   HHstate.Description, '', '', 0, 0, 1])
                    #RowsAIglobal.append([HHdelay.Name, HHdelay.Type.upper(), 'VAR_GLOBAL',   HHdelay.Description, '', '', 0, 0, 1])                    
                    RowsAIlocal.append( [HH.Name,      HH.Type.upper(),      'VAR_EXTERNAL', HH.Description])  
                    RowsAIlocal.append( [HHstate.Name, HHstate.Type.upper(), 'VAR',          HHstate.Description, '', str(HHEnbl).upper(), 1])  
                    RowsAIlocal.append( [HHdelay.Name, HHdelay.Type.upper(), 'VAR',          HHdelay.Description, '', 'TIME#0s', 1])        
            
                    RowsAIglobal.append([H.Name,      H.Type.upper(),      'VAR_GLOBAL',   H.Description, '', AI.HI, 1, 0, 1])
                    #RowsAIglobal.append([Hstate.Name, Hstate.Type.upper(), 'VAR_GLOBAL',   Hstate.Description, '', '', 0, 0, 1])
                    #RowsAIglobal.append([Hdelay.Name, Hdelay.Type.upper(), 'VAR_GLOBAL',   Hdelay.Description, '', '', 0, 0, 1])                    
                    RowsAIlocal.append( [H.Name,      H.Type.upper(),      'VAR_EXTERNAL', H.Description])  
                    RowsAIlocal.append( [Hstate.Name, Hstate.Type.upper(), 'VAR',          Hstate.Description, '', str(HEnbl).upper(), 1])  
                    RowsAIlocal.append( [Hdelay.Name, Hdelay.Type.upper(), 'VAR',          Hdelay.Description, '', 'TIME#0s', 1])    
                    
                    RowsAIglobal.append([L.Name,      L.Type.upper(),      'VAR_GLOBAL',   L.Description, '', AI.LO, 1, 0, 1])
                    #RowsAIglobal.append([Lstate.Name, Lstate.Type.upper(), 'VAR_GLOBAL',   Lstate.Description, '', '', 0, 0, 1])
                    #RowsAIglobal.append([Ldelay.Name, Ldelay.Type.upper(), 'VAR_GLOBAL',   Ldelay.Description, '', '', 0, 0, 1])                    
                    RowsAIlocal.append( [L.Name,      L.Type.upper(),      'VAR_EXTERNAL', L.Description])  
                    RowsAIlocal.append( [Lstate.Name, Lstate.Type.upper(), 'VAR',          Lstate.Description, '', str(LEnbl).upper(), 1])  
                    RowsAIlocal.append( [Ldelay.Name, Ldelay.Type.upper(), 'VAR',          Ldelay.Description, '', 'TIME#0s', 1])  
                    
                    RowsAIglobal.append([LL.Name,      LL.Type.upper(),      'VAR_GLOBAL',   LL.Description, '', AI.LL, 1, 0, 1])
                    #RowsAIglobal.append([LLstate.Name, LLstate.Type.upper(), 'VAR_GLOBAL',   LLstate.Description, '', '', 0, 0, 1])
                    #RowsAIglobal.append([LLdelay.Name, LLdelay.Type.upper(), 'VAR_GLOBAL',   LLdelay.Description, '', '', 0, 0, 1])                    
                    RowsAIlocal.append( [LL.Name,      LL.Type.upper(),      'VAR_EXTERNAL', LL.Description])  
                    RowsAIlocal.append( [LLstate.Name, LLstate.Type.upper(), 'VAR',          LLstate.Description, '', str(LLEnbl).upper(), 1])  
                    RowsAIlocal.append( [LLdelay.Name, LLdelay.Type.upper(), 'VAR',          LLdelay.Description, '', 'TIME#0s', 1])  
                    
                    #RowsAIglobal.append([RSL.Name, RSL.Type.upper(), 'VAR_GLOBAL',   RSL.Description, '', '', 0, 0, 1])
                    #RowsAIglobal.append([RSH.Name, RSH.Type.upper(), 'VAR_GLOBAL',   RSH.Description, '', '', 0, 0, 1])
                    RowsAIglobal.append([ESL.Name, ESL.Type.upper(), 'VAR_GLOBAL',   ESL.Description, '', AI.SL, 1, 0, 1])                    
                    RowsAIglobal.append([ESH.Name, ESH.Type.upper(), 'VAR_GLOBAL',   ESH.Description, '', AI.SH, 1, 0, 1])    
                    RowsAIlocal.append( [RSL.Name, RSL.Type.upper(), 'VAR',          RSL.Description, '', 'REAL#4000.0', 1])  
                    RowsAIlocal.append( [RSH.Name, RSH.Type.upper(), 'VAR',          RSH.Description, '', 'REAL#20000.0', 1])  
                    RowsAIlocal.append( [ESL.Name, ESL.Type.upper(), 'VAR_EXTERNAL', ESL.Description])  
                    RowsAIlocal.append( [ESH.Name, ESH.Type.upper(), 'VAR_EXTERNAL', ESH.Description])  
                    
                    #RowsAIglobal.append([ERR.Name, ERR.Type.upper(), 'VAR_GLOBAL',   ERR.Description, '', '', 0, 0, 1])
                    #RowsAIglobal.append([HYS.Name, HYS.Type.upper(), 'VAR_GLOBAL',   HYS.Description, '', '', 0, 0, 1])
                    RowsAIlocal.append( [ERR.Name, ERR.Type.upper(), 'VAR', ERR.Description, '', 'REAL#2.0', 1])            
                    RowsAIlocal.append( [HYS.Name, HYS.Type.upper(), 'VAR', HYS.Description, '', 'REAL#2.0', 1])     
             
                    RowsAIglobal.append([AHH.Name,  AHH.Type.upper(),  'VAR_GLOBAL',   AHH.Description, '', '', 0, 0, 1])
                    RowsAIglobal.append([AH.Name,   AH.Type.upper(),   'VAR_GLOBAL',   AH.Description, '', '', 0, 0, 1])
                    RowsAIglobal.append([AL.Name,   AL.Type.upper(),   'VAR_GLOBAL',   AL.Description, '', '', 0, 0, 1])
                    RowsAIglobal.append([ALL.Name,  ALL.Type.upper(),  'VAR_GLOBAL',   ALL.Description, '', '', 0, 0, 1])
                    RowsAIglobal.append([IOPP.Name, IOPP.Type.upper(), 'VAR_GLOBAL',   IOPP.Description, '', '', 0, 0, 1])
                    RowsAIglobal.append([IOPM.Name, IOPM.Type.upper(), 'VAR_GLOBAL',   IOPM.Description, '', '', 0, 0, 1])
                    RowsAIglobal.append([A.Name,    A.Type.upper(),    'VAR_GLOBAL',   A.Description, '', '', 0, 0, 1])
                    RowsAIglobal.append([AOF.Name,  AOF.Type.upper(),  'VAR_GLOBAL',   AOF.Description, '', '', 0, 0, 1])
                    
                    RowsAIlocal.append( [AHH.Name,  AHH.Type.upper(),  'VAR_EXTERNAL', AHH.Description])            
                    RowsAIlocal.append( [AH.Name,   AH.Type.upper(),   'VAR_EXTERNAL', AH.Description])  
                    RowsAIlocal.append( [AL.Name,   AL.Type.upper(),   'VAR_EXTERNAL', AL.Description])            
                    RowsAIlocal.append( [ALL.Name,  ALL.Type.upper(),  'VAR_EXTERNAL', ALL.Description]) 
                    RowsAIlocal.append( [IOPP.Name, IOPP.Type.upper(), 'VAR_EXTERNAL', IOPP.Description])            
                    RowsAIlocal.append( [IOPM.Name, IOPM.Type.upper(), 'VAR_EXTERNAL', IOPM.Description]) 
                    RowsAIlocal.append( [A.Name,    A.Type.upper(),    'VAR_EXTERNAL', A.Description])            
                    RowsAIlocal.append( [AOF.Name,  AOF.Type.upper(),  'VAR_EXTERNAL', AOF.Description]) 
                
                    RowsAIcode.append('(*Аналоговый вход ' + str(AI.DeviceTag) + ' Тег канала ' + str(AI.TagChannel) + ' *)\n')
                    RowsAIcode.append('SENS_AI_' + str(count) + '(Raw_value:=UINT_TO_REAL(' + str(AI.DeviceTag) + '.Value),Raw_SH:=' + str(RSH.Name) + ',Raw_SL:=' + str(RSL.Name) + ',Eng_SH:=' + str(ESH.Name) + ',Eng_SL:=' + str(ESL.Name) + ',\n')
                    RowsAIcode.append('HH:=' + str(HH.Name) + ',HI:=' + str(H.Name) + ',LO:=' + str(L.Name) + ',LL:=' + str(LL.Name) + ',Hyst:=' + str(HYS.Name) + ',\n')
                    RowsAIcode.append('Enable_HH:=' + str(HHstate.Name) + ',Enable_HI:=' + str(Hstate.Name) + ',Enable_LO:=' + str(Lstate.Name) + ',Enable_LL:=' + str(LLstate.Name) + ',\n')
                    RowsAIcode.append('Delay_HH:=' + str(HHdelay.Name) + ',Delay_HI:=' + str(Hdelay.Name) + ',Delay_LO:=' + str(Ldelay.Name) + ',Delay_LL:=' + str(LLdelay.Name) + ',ErrorProc:=' + str(ERR.Name) + ');\n')
                    
                    RowsAIcode.append(str(AI.TagChannel) + ':=SENS_AI_' + str(count) + '.PV;\n')
                    RowsAIcode.append(str(AHH.Name)      + ':=SENS_AI_' + str(count) + '.Alarm_HH;\n')                    
                    RowsAIcode.append(str(AH.Name)       + ':=SENS_AI_' + str(count) + '.Alarm_HI;\n')
                    RowsAIcode.append(str(AL.Name)       + ':=SENS_AI_' + str(count) + '.Alarm_LO;\n')
                    RowsAIcode.append(str(ALL.Name)      + ':=SENS_AI_' + str(count) + '.Alarm_LL;\n')
                    RowsAIcode.append(str(IOPP.Name)     + ':=SENS_AI_' + str(count) + '.IOPP;\n')
                    RowsAIcode.append(str(IOPM.Name)     + ':=SENS_AI_' + str(count) + '.IOPM;\n')
                    RowsAIcode.append('(*Включение или отключение сигнализаций*)\n')
                    RowsAIcode.append(str(A.Name) + ':=DWORD#16#00000000;\n')
                    RowsAIcode.append(str(A.Name) + '.X20:=SENS_AI_' + str(count) + '.IOPM;\n')
                    RowsAIcode.append(str(A.Name) + '.X21:=SENS_AI_' + str(count) + '.IOPP;\n')
                    RowsAIcode.append('IF NOT(' + str(AOF.Name) + ') THEN\n')
                    RowsAIcode.append('  ' + str(A.Name) + '.X19:=SENS_AI_' + str(count) + '.Alarm_HH;\n')
                    RowsAIcode.append('  ' + str(A.Name) + '.X15:=SENS_AI_' + str(count) + '.Alarm_HI;\n')
                    RowsAIcode.append('  ' + str(A.Name) + '.X14:=SENS_AI_' + str(count) + '.Alarm_LO;\n')
                    RowsAIcode.append('  ' + str(A.Name) + '.X18:=SENS_AI_' + str(count) + '.Alarm_LL;\n')        
                    RowsAIcode.append('END_IF;\n')
                    RowsAIcode.append('\n')
                    
                count+=1
                #print AI.TagChannel, AI.Alarming
            else:
                RowsAIcode.append('(*Аналоговый вход ' + str(AI.DeviceTag) + ' Тег канала ОТСУТСВУЕТ *)\n')    
                RowsAIcode.append('\n') 
            
            
        TableAI = {u'1|GlobalTags':RowsAIglobal, u'2|LocalTags':RowsAIlocal} 
            
        RowsAOglobal = [GlobalColumns]
        RowsAOlocal = [LocalColumns]
        RowsAOcode = []
        count = 1
        for AO in self.AOs:
            if AO.TagChannel:  
                AO.VirtualSignals = []
                AO.SH = None
                AO.SL = None
                if AO.ControlledVariable: #Если есть "Регулируемый параметр", то указан PV
                    for AI in self.AIs:                        
                        if AO.ControlledVariable == AI.TagChannel:                            
                            AO.ControlledVariable = AI
                            AI.InGroup = True
                            break
                            
                attributes = {'Name': OOP_signal(AO), 
                              'Description': AO.TagChannel + u' - размыкание выхода регулятора', 
                              'Type': 'Bool', 
                              'toHMI': True, 
                              'toMB': True, 
                              'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                           {'IT_ST':'BOOLEAN 1', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'OOP', 'SH_EN':'', 'AL_TXT': u'1'}],                               
                              'Editable': 'False'}
                OOP = VirtualSignal(attributes)
                AO.VirtualSignals.append(OOP)
                
                RowsAOglobal.append([AO.TagChannel, 'CData_REAL', 'VAR_GLOBAL',   AO.Description_rus, '', '', 0, 0, 1])
                RowsAOlocal.append( [AO.TagChannel, 'CData_REAL', 'VAR_EXTERNAL', AO.Description_rus])
                                   
                RowsAOlocal.append([str(AO.DeviceTag), 'DTag_O_Anlg', 'VAR_EXTERNAL', AO.Description_rus])   
                RowsAOlocal.append([str(AO.DeviceTag) + '_RB', 'DTag_O_Anlg', 'VAR_EXTERNAL', u'Статус выхода'])   
                RowsAOlocal.append(['NPAS_AO_ANLG_' + str(count), 'NPAS_AO_ANLG', 'VAR', u'Обработка AO'])
                
                RowsAOglobal.append([OOP.Name, 'BOOL', 'VAR_GLOBAL', OOP.Description, '', '', 0, 0, 1])
                RowsAOlocal.append([OOP.Name, 'BOOL', 'VAR_EXTERNAL', OOP.Description])
                
                RowsAOcode.append('(*Аналоговый выход ' + str(AO.DeviceTag) + ' Тег канала ' + str(AO.TagChannel) + ' *)\n')
                RowsAOcode.append('NPAS_AO_ANLG_' + str(count) + '(IN:=' + str(AO.TagChannel) + ',IN_VAL:=' + str(AO.TagChannel) + '.value,TSFO_SW:=TRUE,TS:=REAL#-17.9,FO:=REAL#106.25);\n')               
                RowsAOcode.append(str(AO.DeviceTag) + ':=NPAS_AO_ANLG_' + str(count) + '.OUT;\n')
                RowsAOcode.append(str(OOP.Name) + ':=' + str(AO.DeviceTag) + '_RB.STATUS.X11;\n')
                #MOV055_01017_OOP := Q_02_06_01_RB.STATUS.X11;
                RowsAOcode.append('\n')               
                
                count+=1
            else:                
                RowsAOcode.append('(*Аналоговый выход ' + str(AO.DeviceTag) + ' Тег канала ОТСУТСВУЕТ *)\n')    
                RowsAOcode.append('\n') 
        TableAO = {u'1|GlobalTags':RowsAOglobal, u'2|LocalTags':RowsAOlocal} 
            
        RowsDIglobal = [GlobalColumns]
        RowsDIlocal = [LocalColumns]
        RowsDIcode = []
        count = 1
        for DI in self.DIs:            
            if DI.TagChannel:   
                DI.SH = None
                DI.SL = None
                DI.VirtualSignals = []
                DI.toHMI = True
                DI.toMB = True
                DI.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                               {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}]
                RowsDIglobal.append([DI.TagChannel, 'BOOL', 'VAR_GLOBAL', DI.Description_rus, '', '', 0, 0, 1])
                RowsDIlocal.append([DI.TagChannel, 'BOOL', 'VAR_EXTERNAL', DI.Description_rus])
                if DI.Blocking:                    
                    attributes = {'Name': DBsignal(DI), 
                                  'Description': DI.TagChannel + u' - Деблокировка', 
                                  'Type': 'Bool', 
                                  'toHMI': True, 
                                  'toMB': True, 
                                  'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'Выключена'}, 
                                               {'IT_ST':'BOOLEAN 1', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'DB', 'SH_EN':'', 'AL_TXT': u'Включена'}],
                                  'ProcArea':'31',    
                                  'Editable': 'True'}
                    DB = VirtualSignal(attributes)
                    DI.VirtualSignals.append(DB)
                    RowsDIglobal.append([DB.Name, 'BOOL', 'VAR_GLOBAL', DB.Description, '', '', 0, 0, 1])
                    #RowsDIlocal.append([DB.Name, 'BOOL', 'VAR_EXTERNAL', DB.Description])
                    
                RowsDIlocal.append([str(DI.DeviceTag), 'DTag_I_Sts', 'VAR_EXTERNAL', DI.Description_rus])
                RowsDIlocal.append(['TON_' + str(count), 'TON', 'VAR', u'Таймер от дребезга сигнала'])
                RowsDIlocal.append(['NPAS_DI_STS_' + str(count), 'NPAS_DI_STS', 'VAR', u'Обработка DI'])
                
                RowsDIcode.append('(*Дискретный вход ' + str(DI.DeviceTag) + ' Тег канала ' + str(DI.TagChannel) + ' *)\n')
                RowsDIcode.append('NPAS_DI_STS_' + str(count) + '(IN:=' + str(DI.DeviceTag) + ');\n')
                RowsDIcode.append('TON_' + str(count) + '(IN:=NPAS_DI_STS_' + str(count) + '.OUT_VAL,PT:=TIME#0s);\n')
                RowsDIcode.append(str(DI.TagChannel) + ':=TON_' + str(count) + '.Q;\n')
                RowsDIcode.append('\n')               
                
                count+=1
            else:                
                RowsDIcode.append('(*Дискретный вход ' + str(DI.DeviceTag) + ' Тег канала ОТСУТСВУЕТ *)\n')    
                RowsDIcode.append('\n') 
        TableDI = {u'1|GlobalTags':RowsDIglobal, u'2|LocalTags':RowsDIlocal}  
        
        RowsDOglobal = [GlobalColumns]
        RowsDOlocal = [LocalColumns]
        RowsDOcode = []
        count = 1
        for DO in self.DOs:            
            if DO.TagChannel:
                DO.SH = None
                DO.SL = None
                DO.VirtualSignals = []
                #DO.toHMI = False
                #DO.toMB = False
                DO.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                               {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}]
                RowsDOglobal.append([DO.TagChannel, 'BOOL', 'VAR_GLOBAL', DO.Description_rus, '', '', 0, 0, 1])
                RowsDOlocal.append([DO.TagChannel, 'BOOL', 'VAR_EXTERNAL', DO.Description_rus])
                                  
                attributes = {'Name': DBsignal(DO), 
                              'Description': DO.TagChannel + u' - Деблокировка выходного сигнала', 
                              'Type': 'Bool',
                              'toHMI': False, 
                              'toMB': False, 
                              'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'Выключена'}, 
                                           {'IT_ST':'BOOLEAN 1', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'DB', 'SH_EN':'', 'AL_TXT': u'Включена'}],
                              'ProcArea':'31',               
                              'Editable': 'True'}
                DB = VirtualSignal(attributes)
                DO.VirtualSignals.append(DB)
                RowsDOglobal.append([DB.Name, 'BOOL', 'VAR_GLOBAL', DB.Description, '', '', 0, 0, 1])
                RowsDOlocal.append([DB.Name, 'BOOL', 'VAR_EXTERNAL', DB.Description])
                  
                RowsDOlocal.append([str(DO.DeviceTag), 'DTag_O_Sts', 'VAR_EXTERNAL', DO.Description_rus])                  
                RowsDOlocal.append(['NPAS_DO_STS_' + str(count), 'NPAS_DO_STS', 'VAR', u'Обработка DO'])
                
                RowsDOcode.append('(*Дискретный выход ' + str(DO.DeviceTag) + ' Тег канала ' + str(DO.TagChannel) + ' *)\n')
                RowsDOcode.append('NPAS_DO_STS_' + str(count) + '(IN_VAL:=(' + str(DO.TagChannel) + ' & NOT(' + DB.Name + ')));\n')                
                RowsDOcode.append(str(DO.DeviceTag) + ':=NPAS_DO_STS_' + str(count) + '.OUT;\n')
                RowsDOcode.append('\n')               
                
                count+=1
            else:                
                RowsDOcode.append('(*Дискретный выход ' + str(DO.DeviceTag) + ' Тег канала ОТСУТСВУЕТ *)\n')    
                RowsDOcode.append('\n') 
        TableDO = {u'1|GlobalTags':RowsDOglobal, u'2|LocalTags':RowsDOlocal} 
        
        return (TableAI, RowsAIcode, TableAO, RowsAOcode, TableDI, RowsDIcode, TableDO, RowsDOcode)
    
    def __MakeDiagnosticSignals(self): 
        u'''Создаем диагностические сигналлы'''
        attributes = {'Name': 'GS_RAS_RDY0', 
                      'Description': u'Готовность контроллера (осн)', 
                      'Type': 'Bool', 
                      'toHMI': True, 
                      'toMB': True, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'Нет готовности'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'Есть готовность'}], 
                      'Editable': 'False'}
        self.VirtualSignals.append(VirtualSignal(attributes))
        self.__AddModbusVar(self.VirtualSignals[-1], 'COIL')
        
        if self.Redundant: 
            attributes = {'Name': 'GS_RAS_REDCY', 
                          'Description': u'Резервирование', 
                          'Type': 'Bool', 
                          'toHMI': True, 
                          'toMB': True,
                          'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'Отказ'}, 
                                       {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'Работает'}],
                          'Editable': 'False'}
            self.VirtualSignals.append(VirtualSignal(attributes))
            self.__AddModbusVar(self.VirtualSignals[-1], 'COIL')
            
            attributes = {'Name': 'GS_RAS_RDY1', 
                          'Description': u'Готовность контроллера (рез)', 
                          'Type': 'Bool', 
                          'toHMI': True, 
                          'toMB': True,
                          'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'Нет готовности'}, 
                                       {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'Есть готовность'}],
                          'Editable': 'False'}
            self.VirtualSignals.append(VirtualSignal(attributes))
            self.__AddModbusVar(self.VirtualSignals[-1], 'COIL')
            
        Carriers = []
        for module in self.Modules:
            if module.Carrier not in Carriers:
                attributes = {'Name': 'GS_RAS_PSU' + str(module.Carrier) + '_ACRDYL', 
                              'Description': u'Авария блок питания (левый) шасси ' + str(module.Carrier), 
                              'Type': 'Bool', 
                              'toHMI': True, 
                              'toMB': True,
                              'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'Неисправность'}, 
                                           {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'В норме'}], 
                              'Editable': 'False'}
                self.VirtualSignals.append(VirtualSignal(attributes))
                self.__AddModbusVar(self.VirtualSignals[-1], 'COIL')
                
                attributes = {'Name': 'GS_RAS_PSU' + str(module.Carrier) + '_DCRDYL', 
                              'Description': u'Авария блок питания (левый) шасси ' + str(module.Carrier), 
                              'Type': 'Bool', 
                              'toHMI': True, 
                              'toMB': True,
                              'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'Неисправность'}, 
                                           {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'В норме'}], 
                              'Editable': 'False'}
                self.VirtualSignals.append(VirtualSignal(attributes))
                self.__AddModbusVar(self.VirtualSignals[-1], 'COIL')
                
                attributes = {'Name': 'GS_RAS_PSU' + str(module.Carrier) + '_ACRDYR', 
                              'Description': u'Авария блок питания (правый) шасси ' + str(module.Carrier), 
                              'Type': 'Bool', 
                              'toHMI': True, 
                              'toMB': True,
                              'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'Неисправность'}, 
                                           {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'В норме'}], 
                              'Editable': 'False'}
                self.VirtualSignals.append(VirtualSignal(attributes))
                self.__AddModbusVar(self.VirtualSignals[-1], 'COIL')
                
                attributes = {'Name': 'GS_RAS_PSU' + str(module.Carrier) + '_DCRDYR', 
                              'Description': u'Авария блок питания (правый) шасси ' + str(module.Carrier), 
                              'Type': 'Bool', 
                              'toHMI': True, 
                              'toMB': True,
                              'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'Неисправность'}, 
                                           {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'В норме'}], 
                              'Editable': 'False'}
                self.VirtualSignals.append(VirtualSignal(attributes))
                self.__AddModbusVar(self.VirtualSignals[-1], 'COIL')
                                
                Carriers.append(module.Carrier)
                
            attributes = {'Name': 'FCN_' + str(module.Carrier) + '_' + str(module.Position) + '_ERR', 
                          'Description': u'Неисправность: шасси ' + str(module.Carrier) + u' слот ' +  str(module.Position), 
                          'Type': 'Bool', 
                          'toHMI': True, 
                          'toMB': True,
                          'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'В норме'}, 
                                       {'IT_ST':'BOOLEAN 1', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'Неисправность'}], 
                          'Editable': 'False'}
            self.VirtualSignals.append(VirtualSignal(attributes))
            self.__AddModbusVar(self.VirtualSignals[-1], 'COIL')   
        
    def __AddModbusVar(self, Signal, Type):   
        if Type == 'COIL':
            self.COIL += 1   
            self.MBSignals['COILS'][self.COIL] = Signal         
        elif Type == 'HREG':
            self.HREG += 2   
            self.MBSignals['HREGS'][self.HREG] = Signal 
        else:
            print u'Ошибка при добавлении сигнала в карту ModBus', Type, Signal.__dict__            
    
    def GetActMechList(self):
        Engines = {}
        Valves = {}
        PIDs = {}
        for signal in self.Signals:            
            if signal.__dict__.get('ActMechType') and signal.ActMechType:
                if signal.ActMechType.capitalize() == u'Engine':                     
                    if not Engines.get(signal.Tag):
                        #print u'Есть насос', signal.Tag
                        Engines[signal.Tag] = {}                        
                    Engines[signal.Tag][signal.BlockFunction.upper() if signal.BlockFunction else '']=signal
                if signal.ActMechType.capitalize() == u'Valve':                    
                    if not Valves.get(signal.Tag):
                        #print u'Есть задвижка', signal.Tag
                        Valves[signal.Tag] = {}                        
                    Valves[signal.Tag][signal.BlockFunction.upper() if signal.BlockFunction else '']=signal
                if signal.ActMechType.upper() == u'PID':
                    if not PIDs.get(signal.Tag):
                        #print u'Есть ПИД', signal.Tag
                        PIDs[signal.Tag] = {}                        
                    PIDs[signal.Tag][signal.BlockFunction.upper() if signal.BlockFunction else '']=signal
        Engine.number = 0
        EngineNames = Engines.keys()
        EngineNames.sort()
        for engine in EngineNames:
            self.Engines.append(Engine(engine, Engines[engine]))
        
        Valve.number = 0
        ValveNames = Valves.keys()
        ValveNames.sort()
        for valve in ValveNames:
            self.Valves.append(Valve(valve, Valves[valve]))
        
        PID.number = 0
        PIDNames = PIDs.keys()
        PIDNames.sort()
        for pid in PIDNames:
            self.PIDs.append(PID(pid, PIDs[pid]))

class Engine(object):    
    Name = u'Noname'
    Prefix = u'E_'
    CR = None
    CS = None
    SW = None  
    SD = None
    SL = None
    SG = None  
    SN = None  
    number = 0  
    def __init__(self, Name, Signals):
        self.Name = Name
        self.Signals = Signals
        self.VirtualSignals = []
        self.RowsGlobal = []
        self.RowsLocal = []
        self.RowsCode = []
        self.__class__.number += 1 
    
        if Signals.get('CR'):
            self.CR = Signals['CR']   
            self.CR.InGroup = True 
            self.CR.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u''}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'DO-R', 'SH_EN':'', 'AL_TXT': u'DO - Пуск'}]
            self.RowsLocal.append([self.CR.TagChannel, u'BOOL', 'VAR_EXTERNAL', self.CR.Description_rus])                   
        if Signals.get('CS'):
            self.CS = Signals['CS']      
            self.CS.InGroup = True            
            self.CS.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u''}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'DO-S', 'SH_EN':'', 'AL_TXT': u'DO - Стоп'}]
            self.RowsLocal.append([self.CS.TagChannel, u'BOOL', 'VAR_EXTERNAL', self.CS.Description_rus])
        if Signals.get('SW'):
            self.SW = Signals['SW']    
            self.SW.InGroup = True
            self.SW.toHMI = True
            self.SW.toMB = True
            self.SW.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'S', 'SH_EN':'', 'AL_TXT': u'Остановлен'}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'W', 'SH_EN':'', 'AL_TXT': u'Запущен'}]
            self.RowsLocal.append([self.SW.TagChannel, u'BOOL', 'VAR_EXTERNAL', self.SW.Description_rus])
        if Signals.get('SD'):
            self.SD = Signals['SD']   
            self.SD.InGroup = True
            self.SD.toHMI = True
            self.SD.toMB = True
            self.SD.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'L', 'SH_EN':'', 'AL_TXT': u'Местный'}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'R', 'SH_EN':'', 'AL_TXT': u'Дистанционный'}]
            self.RowsLocal.append([self.SD.TagChannel, u'BOOL', 'VAR_EXTERNAL', self.SD.Description_rus])
        if Signals.get('SL'):
            self.SL = Signals['SL'] 
            self.SL.InGroup = True
            self.SL.toHMI = True
            self.SL.toMB = True
            self.SL.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'R', 'SH_EN':'', 'AL_TXT': u'Дистанционный'}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'L', 'SH_EN':'', 'AL_TXT': u'Местный'}]
            self.RowsLocal.append([self.SL.TagChannel, u'BOOL', 'VAR_EXTERNAL', self.SL.Description_rus])
        if Signals.get('SG'):
            self.SG = Signals['SG']  
            self.SG.InGroup = True
            self.SG.toHMI = True
            self.SG.toMB = True
            self.SG.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'NRD', 'SH_EN':'', 'AL_TXT': u'Не готов'}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'RDY', 'SH_EN':'', 'AL_TXT': u'Готов'}]
            self.RowsLocal.append([self.SG.TagChannel, u'BOOL', 'VAR_EXTERNAL', self.SG.Description_rus])
        if Signals.get('SN'):
            self.SN = Signals['SN']
            self.SN.InGroup = True
            self.SN.toHMI = True
            self.SN.toMB = True
            self.SN.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'В норме'}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'Неисправность'}]
            self.RowsLocal.append([self.SN.TagChannel, u'BOOL', 'VAR_EXTERNAL', self.SN.Description_rus])
         
        attributes = {'Name': RTsignal(self), 
                      'Description': self.Name + u' - Флаг удержания управляющей команды после прихода концевика', 
                      'Type': 'Bool',
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u''}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u''}],
                      'Editable': 'True'}
        RT = VirtualSignal(attributes)
        self.VirtualSignals.append(RT)       
        
        attributes = {'Name': LBLsignal(self), 
                      'Description': self.Name + u' - Агрегатор причин для блокировки ИМ (локальный)', 
                      'Type': 'Bool', 
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u''}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u''}],
                      'Editable': 'True'}
        LBlock = VirtualSignal(attributes)
        self.VirtualSignals.append(LBlock) 
        
        attributes = {'Name': EBLsignal(self), 
                      'Description': self.Name + u' - Агрегатор причин для блокировки ИМ', 
                      'Type': 'Bool', 
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u''}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u''}],
                      'Editable': 'True'}
        EBlock = VirtualSignal(attributes)
        self.VirtualSignals.append(EBlock) 
        
        attributes = {'Name': TMsignal(self), 
                      'Description': self.Name + u' - Время на выполнение команды ИМом', 
                      'Type': 'Time', 
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u''}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u''}],
                      'Editable': 'True'}
        TM = VirtualSignal(attributes)
        self.VirtualSignals.append(TM) 
        
        attributes = {'Name': ModeAsignal(self), 
                      'Description': self.Name + u' - режим АВТОМАТ', 
                      'Type': 'Bool', 
                      'toHMI': True, 
                      'toMB': True, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'MAOFF', 'SH_EN':'', 'AL_TXT': u'Выключен'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'MAON', 'SH_EN':'', 'AL_TXT': u'Включен'}],
                      'Editable': 'True'}
        ModeA = VirtualSignal(attributes)
        self.VirtualSignals.append(ModeA) 
        
        attributes = {'Name': ModeMsignal(self), 
                      'Description': self.Name + u' - режим РУЧНОЙ', 
                      'Type': 'Bool', 
                      'toHMI': True, 
                      'toMB': True, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'MMOFF', 'SH_EN':'', 'AL_TXT': u'Выключен'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'MMON', 'SH_EN':'', 'AL_TXT': u'Включен'}],
                      'Editable': 'True'}
        ModeM = VirtualSignal(attributes)
        self.VirtualSignals.append(ModeM) 
        
        attributes = {'Name': ModeLsignal(self), 
                      'Description': self.Name + u' - режим ЛОКАЛЬНЫЙ', 
                      'Type': 'Bool',
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'MLOFF', 'SH_EN':'', 'AL_TXT': u'Выключен'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'MLON', 'SH_EN':'', 'AL_TXT': u'Включен'}], 
                      'Editable': 'True'}
        ModeL = VirtualSignal(attributes)
        self.VirtualSignals.append(ModeL) 
        
        attributes = {'Name': CMDstart_Asignal(self), 
                      'Description': self.Name + u' - Команда ПУСК от алгоритма', 
                      'Type': 'Bool', 
                      'toHMI': True, 
                      'toMB': True, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}],
                      'Editable': 'True'}
        ALGR = VirtualSignal(attributes)
        self.VirtualSignals.append(ALGR) 
        
        attributes = {'Name': CMDstop_Asignal(self), 
                      'Description': self.Name + u' - Команда СТОП от алгоритма', 
                      'Type': 'Bool', 
                      'toHMI': True, 
                      'toMB': True, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}],
                      'Editable': 'True'}
        ALGS = VirtualSignal(attributes)
        self.VirtualSignals.append(ALGS) 
        
        attributes = {'Name': CMDstart_Msignal(self), 
                      'Description': self.Name + u' - Команда ПУСК от оператора', 
                      'Type': 'Bool', 
                      'toHMI': True, 
                      'toMB': True, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}],
                      'Editable': 'True'}
        CMDR = VirtualSignal(attributes)
        self.VirtualSignals.append(CMDR) 
        
        attributes = {'Name': CMDstop_Msignal(self), 
                      'Description': self.Name + u' - Команда СТОП от оператора', 
                      'Type': 'Bool', 
                      'toHMI': True, 
                      'toMB': True, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}],
                      'Editable': 'True'}
        CMDS = VirtualSignal(attributes)
        self.VirtualSignals.append(CMDS)
        
        attributes = {'Name': CMDstart_Lsignal(self), 
                      'Description': self.Name + u' - Команда ПУСК от местного щита управления, если команды проходят через контроллер', 
                      'Type': 'Bool', 
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}],
                      'Editable': 'True'}
        LOCR = VirtualSignal(attributes)
        self.VirtualSignals.append(LOCR) 
        
        attributes = {'Name': CMDstop_Lsignal(self), 
                      'Description': self.Name + u' - Команда СТОП от местного щита управления, если команды проходят через контроллер', 
                      'Type': 'Bool', 
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}],
                      'Editable': 'True'}
        LOCS = VirtualSignal(attributes)
        self.VirtualSignals.append(LOCS)
        
        attributes = {'Name': IMstarting_signal(self), 
                      'Description': self.Name + u' - Флаг ИМ запускается', 
                      'Type': 'Bool', 
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}],
                      'Editable': 'False'}
        Starting = VirtualSignal(attributes)
        self.VirtualSignals.append(Starting) 
        
        attributes = {'Name': IMstoping_signal(self), 
                      'Description': self.Name + u' - Флаг ИМ останавливается', 
                      'Type': 'Bool', 
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}],
                      'Editable': 'False'}
        Stoping = VirtualSignal(attributes)
        self.VirtualSignals.append(Stoping)
        
        attributes = {'Name': IMstarted_signal(self), 
                      'Description': self.Name + u' - Флаг ИМ запущен', 
                      'Type': 'Bool', 
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}],
                      'Editable': 'False'}
        Started = VirtualSignal(attributes)
        self.VirtualSignals.append(Started) 
        
        attributes = {'Name': IMstoped_signal(self), 
                      'Description': self.Name + u' - Флаг ИМ остановлен', 
                      'Type': 'Bool', 
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}],
                      'Editable': 'False'}
        Stoped = VirtualSignal(attributes)
        self.VirtualSignals.append(Stoped)
                
        attributes = {'Name': ALMcmd_signal(self), 
                      'Description': self.Name + u' - ИМ не выполнил команду за отведённое время', 
                      'Type': 'Bool', 
                      'toHMI': True, 
                      'toMB': True, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}],
                      'Editable': 'False'}
        CMD_A = VirtualSignal(attributes)
        self.VirtualSignals.append(CMD_A) 
        
        attributes = {'Name': ALMhard_signal(self), 
                      'Description': self.Name + u' - ИМ физическая неисправность', 
                      'Type': 'Bool', 
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}],
                      'Editable': 'False'}
        HARD_A = VirtualSignal(attributes)
        self.VirtualSignals.append(HARD_A)
        
        self.RowsLocal.append(['ENGINE_DI_' + str(self.number), 'ENGINE_DI', 'VAR', u'Обработка ENGINE'])   
        
        #self.RowsGlobal.append([TM.Name,    TM.Type.upper(),    'VAR_GLOBAL',   TM.Description, '', '', 1, 0, 1])
        #self.RowsGlobal.append([RT.Name,    RT.Type.upper(),    'VAR_GLOBAL',   RT.Description, '', '', 1, 0, 1])
        self.RowsGlobal.append([EBlock.Name, EBlock.Type.upper(), 'VAR_GLOBAL',   EBlock.Description, '', '', 0, 0, 1])
        #self.RowsGlobal.append([LBlock.Name, LBlock.Type.upper(), 'VAR_GLOBAL',   LBlock.Description, '', '', 0, 0, 1])
        self.RowsLocal.append( [TM.Name,     TM.Type.upper(),     'VAR',          TM.Description, '', 'TIME#10s', 1])  
        self.RowsLocal.append( [RT.Name,     RT.Type.upper(),     'VAR',          RT.Description, '', '', 1])  
        self.RowsLocal.append( [EBlock.Name, EBlock.Type.upper(), 'VAR_EXTERNAL', EBlock.Description]) 
        self.RowsLocal.append( [LBlock.Name, LBlock.Type.upper(), 'VAR',          LBlock.Description]) 
        
        self.RowsGlobal.append([ModeA.Name, ModeA.Type.upper(), 'VAR_GLOBAL',   ModeA.Description, '', '', 1, 0, 1])
        self.RowsGlobal.append([ModeM.Name, ModeM.Type.upper(), 'VAR_GLOBAL',   ModeM.Description, '', '', 1, 0, 1])
        self.RowsGlobal.append([ModeL.Name, ModeL.Type.upper(), 'VAR_GLOBAL',   ModeL.Description, '', '', 1, 0, 1])
        self.RowsLocal.append( [ModeA.Name, ModeA.Type.upper(), 'VAR_EXTERNAL', ModeA.Description])  
        self.RowsLocal.append( [ModeM.Name, ModeM.Type.upper(), 'VAR_EXTERNAL', ModeM.Description])  
        self.RowsLocal.append( [ModeL.Name, ModeL.Type.upper(), 'VAR_EXTERNAL', ModeL.Description])  
        
        self.RowsGlobal.append([ALGR.Name, ALGR.Type.upper(), 'VAR_GLOBAL',   ALGR.Description, '', '', 0, 0, 1])
        self.RowsGlobal.append([ALGS.Name, ALGS.Type.upper(), 'VAR_GLOBAL',   ALGS.Description, '', '', 0, 0, 1])
        self.RowsLocal.append( [ALGR.Name, ALGR.Type.upper(), 'VAR_EXTERNAL', ALGR.Description])  
        self.RowsLocal.append( [ALGS.Name, ALGS.Type.upper(), 'VAR_EXTERNAL', ALGS.Description])  
        
        self.RowsGlobal.append([CMDR.Name, CMDR.Type.upper(), 'VAR_GLOBAL',   CMDR.Description, '', '', 0, 0, 1])
        self.RowsGlobal.append([CMDS.Name, CMDS.Type.upper(), 'VAR_GLOBAL',   CMDS.Description, '', '', 0, 0, 1])
        self.RowsLocal.append( [CMDR.Name, CMDR.Type.upper(), 'VAR_EXTERNAL', CMDR.Description])  
        self.RowsLocal.append( [CMDS.Name, CMDS.Type.upper(), 'VAR_EXTERNAL', CMDS.Description])  
        
        #self.RowsGlobal.append([LOCR.Name, LOCR.Type.upper(), 'VAR_GLOBAL',   LOCR.Description, '', '', 0, 0, 1])
        #self.RowsGlobal.append([LOCS.Name, CMDS.Type.upper(), 'VAR_GLOBAL',   LOCS.Description, '', '', 0, 0, 1])
        #self.RowsLocal.append( [LOCR.Name, LOCR.Type.upper(), 'VAR_EXTERNAL', LOCR.Description])  
        #self.RowsLocal.append( [LOCS.Name, CMDS.Type.upper(), 'VAR_EXTERNAL', LOCS.Description]) 
        
        self.RowsGlobal.append([Starting.Name, Starting.Type.upper(), 'VAR_GLOBAL',   Starting.Description, '', '', 0, 0, 1])
        self.RowsGlobal.append([Stoping.Name,  Stoping.Type.upper(),  'VAR_GLOBAL',   Stoping.Description, '', '', 0, 0, 1])
        self.RowsGlobal.append([Started.Name,  Started.Type.upper(),  'VAR_GLOBAL',   Started.Description, '', '', 0, 0, 1])
        self.RowsGlobal.append([Stoped.Name,   Stoped.Type.upper(),   'VAR_GLOBAL',   Stoped.Description, '', '', 0, 0, 1])
        self.RowsLocal.append( [Starting.Name, Starting.Type.upper(), 'VAR_EXTERNAL', Starting.Description])  
        self.RowsLocal.append( [Stoping.Name,  Stoping.Type.upper(),  'VAR_EXTERNAL', Stoping.Description])
        self.RowsLocal.append( [Started.Name,  Started.Type.upper(),  'VAR_EXTERNAL', Started.Description])  
        self.RowsLocal.append( [Stoped.Name,   Stoped.Type.upper(),   'VAR_EXTERNAL', Stoped.Description])
        
        self.RowsGlobal.append([CMD_A.Name,  CMD_A.Type.upper(),  'VAR_GLOBAL',   CMD_A.Description, '', '', 0, 0, 1])
        self.RowsGlobal.append([HARD_A.Name, HARD_A.Type.upper(), 'VAR_GLOBAL',   HARD_A.Description, '', '', 0, 0, 1])
        self.RowsLocal.append( [CMD_A.Name,  CMD_A.Type.upper(),  'VAR_EXTERNAL', CMD_A.Description])  
        self.RowsLocal.append( [HARD_A.Name, HARD_A.Type.upper(), 'VAR_EXTERNAL', HARD_A.Description])
        
        self.RowsCode.append('(*Исполнительный механизм ' + str(self.Name) + ' *)\n')
        self.RowsCode.append('Engine_DI_' + str(self.number) + '(DI_State:=' + (str(self.SW.TagChannel) if self.SW else 'False') + ',DI_Fault:=' + (str(self.SN.TagChannel) if self.SN else 'False') + ',RT:=' + str(RT.Name) + ',Time_RS:=' + str(TM.Name) + ',Block:=' + str(LBlock.Name) + ',\n')
        self.RowsCode.append('Mode_A:=' + str(ModeA.Name) + ',Mode_M:=' + str(ModeM.Name) + ',Mode_L:=' + str(ModeL.Name) + ',\n')
        self.RowsCode.append('Cmd_start_A:=' + str(ALGR.Name) + ',Cmd_stop_A:=' + str(ALGS.Name) + ',\n')
        #self.RowsCode.append('Cmd_start_L:=' + str(LOCR.Name) + ',Cmd_start_L:=' + str(LOCS.Name) + ',\n')
        self.RowsCode.append('Cmd_start_M:=' + str(CMDR.Name) + ',Cmd_start_M:=' + str(CMDS.Name) + ')\n')        
        
        self.RowsCode.append((str(self.CR.TagChannel) if self.CR else '(*[Paste TagName here]') + ':=Engine_DI_' + str(self.number) + '.DO_Start;' + ('*)' if not self.CR else '') + '\n')   
        self.RowsCode.append((str(self.CS.TagChannel) if self.CS else '(*[Paste TagName here]') + ':=Engine_DI_' + str(self.number) + '.DO_Stop;' + ('*)' if not self.CS else '') + '\n')   
        
        self.RowsCode.append(str(Starting.Name) + ':=Engine_DI_' + str(self.number) + '.Starting;\n')   
        self.RowsCode.append(str(Stoping.Name)  + ':=Engine_DI_' + str(self.number) + '.Stoping;\n')   
        self.RowsCode.append(str(Started.Name)  + ':=Engine_DI_' + str(self.number) + '.Started;\n')   
        self.RowsCode.append(str(Stoped.Name)   + ':=Engine_DI_' + str(self.number) + '.Stoped;\n')   
        self.RowsCode.append(str(CMD_A.Name)    + ':=Engine_DI_' + str(self.number) + '.Alarm_CMD;\n')   
        self.RowsCode.append(str(HARD_A.Name)   + ':=Engine_DI_' + str(self.number) + '.Alarm_HARD;\n')   
        self.RowsCode.append(str(CMDR.Name)     + ':=Engine_DI_' + str(self.number) + '.Cmd_start_M;\n')   
        self.RowsCode.append(str(CMDS.Name)     + ':=Engine_DI_' + str(self.number) + '.Cmd_stop_M;\n')  
        
        self.RowsCode.append('(*Сборка блокировочных параметров*)\n')        
        self.RowsCode.append(str(LBlock.Name) + ':=' + str(EBlock.Name) + (' OR NOT ' + str(self.SG.TagChannel) if self.SG else '') + (' OR NOT ' + str(self.SD.TagChannel) if self.SD else '') + (' OR ' + str(self.SL.TagChannel) if self.SL else '') + ';\n')        
        self.RowsCode.append('\n') 
    
    def SaySignals(self):       
        print self.Name, self.Signals.keys()
            
class Valve(object):
    Name = u'Noname'
    Prefix = u'V_'
    CO = None
    CC = None
    CS = None
    SO = None
    SC = None
    SOG = None
    SCG = None
    SD = None
    SL = None
    SG = None  
    SN = None 
    number = 0  
    def __init__(self, Name, Signals):
        self.Name = Name
        self.Signals = Signals
        self.VirtualSignals = []
        self.RowsGlobal = []
        self.RowsLocal = []
        self.RowsCode = []
        self.__class__.number += 1 
        if Signals.get('CO'):
            self.CO = Signals['CO']   
            self.CO.InGroup = True 
            self.CO.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u''}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'DO-CO', 'SH_EN':'', 'AL_TXT': u'DO - Открыть'}]
            self.RowsLocal.append([self.CO.TagChannel, u'BOOL', 'VAR_EXTERNAL', self.CO.Description_rus])
        if Signals.get('CC'):
            self.CC = Signals['CC']   
            self.CC.InGroup = True 
            self.CC.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u''}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'DO-CC', 'SH_EN':'', 'AL_TXT': u'DO - Закрыть'}]
            self.RowsLocal.append([self.CC.TagChannel, u'BOOL', 'VAR_EXTERNAL', self.CC.Description_rus])
        if Signals.get('CS'):
            self.CS = Signals['CS']    
            self.CS.InGroup = True 
            self.CS.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u''}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'DO-CS', 'SH_EN':'', 'AL_TXT': u'DO - Стоп'}]   
            self.RowsLocal.append([self.CS.TagChannel, u'BOOL', 'VAR_EXTERNAL', self.CS.Description_rus])
        if Signals.get('SO'):
            self.SO = Signals['SO']    
            self.SO.InGroup = True 
            self.SO.toHMI = True
            self.SO.toMB = True
            self.SO.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'OP', 'SH_EN':'', 'AL_TXT': u'1'}]  
            self.RowsLocal.append([self.SO.TagChannel, u'BOOL', 'VAR_EXTERNAL', self.SO.Description_rus])
        if Signals.get('SC'):
            self.SC = Signals['SC'] 
            self.SC.InGroup = True 
            self.SC.toHMI = True
            self.SC.toMB = True
            self.SC.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'CL', 'SH_EN':'', 'AL_TXT': u'1'}]  
            self.RowsLocal.append([self.SC.TagChannel, u'BOOL', 'VAR_EXTERNAL', self.SC.Description_rus])
        if Signals.get('SOG'):
            self.SOG = Signals['SOG'] 
            self.SOG.InGroup = True 
            self.SOG.toHMI = True
            self.SOG.toMB = True
            self.SOG.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'OPG', 'SH_EN':'', 'AL_TXT': u'1'}]  
        if Signals.get('SCG'):
            self.SCG = Signals['SCG'] 
            self.SCG.InGroup = True 
            self.SCG.toHMI = True
            self.SCG.toMB = True
            self.SCG.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'CLG', 'SH_EN':'', 'AL_TXT': u'1'}]  
        if Signals.get('SD'):
            self.SD = Signals['SD']        
            self.SD.InGroup = True 
            self.SD.toHMI = True
            self.SD.toMB = True
            self.SD.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'L', 'SH_EN':'', 'AL_TXT': u'Местный'}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'R', 'SH_EN':'', 'AL_TXT': u'Дистанционный'}]  
            self.RowsLocal.append([self.SD.TagChannel, u'BOOL', 'VAR_EXTERNAL', self.SD.Description_rus])
        if Signals.get('SL'):
            self.SL = Signals['SL']     
            self.SL.InGroup = True 
            self.SL.toHMI = True
            self.SL.toMB = True
            self.SL.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'R', 'SH_EN':'', 'AL_TXT': u'Дистанционный'}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'L', 'SH_EN':'', 'AL_TXT': u'Местный'}]    
            self.RowsLocal.append([self.SL.TagChannel, u'BOOL', 'VAR_EXTERNAL', self.SL.Description_rus])
        if Signals.get('SG'):
            self.SG = Signals['SG']  
            self.SG.InGroup = True 
            self.SG.toHMI = True
            self.SG.toMB = True
            self.SG.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'NRD', 'SH_EN':'', 'AL_TXT': u'Не готов'}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'RDY', 'SH_EN':'', 'AL_TXT': u'Готов'}]
            self.RowsLocal.append([self.SG.TagChannel, u'BOOL', 'VAR_EXTERNAL', self.SG.Description_rus])
        if Signals.get('SN'):
            self.SN = Signals['SN']
            self.SN.InGroup = True 
            self.SN.toHMI = True
            self.SN.toMB = True
            self.SN.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'В норме'}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'Неисправность'}]
            self.RowsLocal.append([self.SN.TagChannel, u'BOOL', 'VAR_EXTERNAL', self.SN.Description_rus])
         
        attributes = {'Name': RTsignal(self), 
                      'Description': self.Name + u' - Флаг удержания управляющей команды после прихода концевика', 
                      'Type': 'Bool', 
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u''}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u''}],
                      'Editable': 'True'}
        RT = VirtualSignal(attributes)
        self.VirtualSignals.append(RT)       
        
        attributes = {'Name': LBLsignal(self), 
                      'Description': self.Name + u' - Агрегатор причин для блокировки ИМ (локальный)', 
                      'Type': 'Bool', 
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u''}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u''}],
                      'Editable': 'True'}
        LBlock = VirtualSignal(attributes)
        self.VirtualSignals.append(LBlock) 
        
        attributes = {'Name': EBLsignal(self), 
                      'Description': self.Name + u' - Агрегатор причин для блокировки ИМ', 
                      'Type': 'Bool', 
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u''}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u''}],
                      'Editable': 'True'}
        EBlock = VirtualSignal(attributes)
        self.VirtualSignals.append(EBlock) 
        
        attributes = {'Name': TMsignal(self), 
                      'Description': self.Name + u' - Время на выполнение команды ИМом', 
                      'Type': 'Time', 
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u''}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u''}],
                      'Editable': 'True'}
        TM = VirtualSignal(attributes)
        self.VirtualSignals.append(TM) 
        
        attributes = {'Name': ModeAsignal(self), 
                      'Description': self.Name + u' - режим АВТОМАТ', 
                      'Type': 'Bool', 
                      'toHMI': True, 
                      'toMB': True, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'MAOFF', 'SH_EN':'', 'AL_TXT': u'Выключен'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'MAON', 'SH_EN':'', 'AL_TXT': u'Включен'}],
                      'Editable': 'True'}
        ModeA = VirtualSignal(attributes)
        self.VirtualSignals.append(ModeA) 
        
        attributes = {'Name': ModeMsignal(self), 
                      'Description': self.Name + u' - режим РУЧНОЙ', 
                      'Type': 'Bool',                       
                      'toHMI': True, 
                      'toMB': True, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'MMOFF', 'SH_EN':'', 'AL_TXT': u'Выключен'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'MMON', 'SH_EN':'', 'AL_TXT': u'Включен'}],
                      'Editable': 'True'}
        ModeM = VirtualSignal(attributes)
        self.VirtualSignals.append(ModeM) 
        
        attributes = {'Name': ModeLsignal(self), 
                      'Description': self.Name + u' - режим ЛОКАЛЬНЫЙ',                       
                      'Type': 'Bool', 
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'MLOFF', 'SH_EN':'', 'AL_TXT': u'Выключен'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'MLON', 'SH_EN':'', 'AL_TXT': u'Включен'}],
                      'Editable': 'True'}
        ModeL = VirtualSignal(attributes)
        self.VirtualSignals.append(ModeL) 
        
        attributes = {'Name': CMDopen_Asignal(self), 
                      'Description': self.Name + u' - Команда ОТКРЫТЬ от алгоритма', 
                      'Type': 'Bool', 
                      'toHMI': True, 
                      'toMB': True, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}],
                      'Editable': 'True'}
        ALGO = VirtualSignal(attributes)
        self.VirtualSignals.append(ALGO) 
        
        attributes = {'Name': CMDstop_Asignal(self), 
                      'Description': self.Name + u' - Команда СТОП от алгоритма', 
                      'Type': 'Bool', 
                      'toHMI': True, 
                      'toMB': True, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}],
                      'Editable': 'True'}
        ALGS = VirtualSignal(attributes)
        self.VirtualSignals.append(ALGS) 
        
        attributes = {'Name': CMDclose_Asignal(self), 
                      'Description': self.Name + u' - Команда ЗАКРЫТЬ от алгоритма', 
                      'Type': 'Bool', 
                      'toHMI': True, 
                      'toMB': True, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}],
                      'Editable': 'True'}
        ALGC = VirtualSignal(attributes)
        self.VirtualSignals.append(ALGC)
        
        attributes = {'Name': CMDopen_Msignal(self), 
                      'Description': self.Name + u' - Команда ОТКРЫТЬ от оператора', 
                      'Type': 'Bool', 
                      'toHMI': True, 
                      'toMB': True, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}],
                      'Editable': 'True'}
        CMDO = VirtualSignal(attributes)
        self.VirtualSignals.append(CMDO) 
        
        attributes = {'Name': CMDstop_Msignal(self), 
                      'Description': self.Name + u' - Команда СТОП от оператора', 
                      'Type': 'Bool', 
                      'toHMI': True, 
                      'toMB': True, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}],
                      'Editable': 'True'}
        CMDS = VirtualSignal(attributes)
        self.VirtualSignals.append(CMDS)
        
        attributes = {'Name': CMDclose_Msignal(self), 
                      'Description': self.Name + u' - Команда ЗАКРЫТЬ от оператора', 
                      'Type': 'Bool', 
                      'toHMI': True, 
                      'toMB': True, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}],
                      'Editable': 'True'}
        CMDC = VirtualSignal(attributes)
        self.VirtualSignals.append(CMDC) 
        
        attributes = {'Name': CMDopen_Lsignal(self), 
                      'Description': self.Name + u' - Команда ОТКРЫТЬ от местного щита управления, если команды проходят через контроллер', 
                      'Type': 'Bool', 
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}],
                      'Editable': 'True'}
        LOCO = VirtualSignal(attributes)
        self.VirtualSignals.append(LOCO) 
        
        attributes = {'Name': CMDstop_Lsignal(self), 
                      'Description': self.Name + u' - Команда СТОП от местного щита управления, если команды проходят через контроллер', 
                      'Type': 'Bool',
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}], 
                      'Editable': 'True'}
        LOCS = VirtualSignal(attributes)
        self.VirtualSignals.append(LOCS)
        
        attributes = {'Name': CMDclose_Lsignal(self), 
                      'Description': self.Name + u' - Команда ЗАКРЫТЬ от местного щита управления, если команды проходят через контроллер', 
                      'Type': 'Bool', 
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}],
                      'Editable': 'True'}
        LOCC = VirtualSignal(attributes)
        self.VirtualSignals.append(LOCC)
        
        attributes = {'Name': IMopening_signal(self), 
                      'Description': self.Name + u' - Флаг ИМ открывается', 
                      'Type': 'Bool', 
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}],
                      'Editable': 'False'}
        Opening = VirtualSignal(attributes)
        self.VirtualSignals.append(Opening) 
        
        attributes = {'Name': IMclosing_signal(self), 
                      'Description': self.Name + u' - Флаг ИМ закрывается', 
                      'Type': 'Bool', 
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}],
                      'Editable': 'False'}
        Closing = VirtualSignal(attributes)
        self.VirtualSignals.append(Closing)
        
        attributes = {'Name': IMopened_signal(self), 
                      'Description': self.Name + u' - Флаг ИМ открыт', 
                      'Type': 'Bool',
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}],
                      'Editable': 'False'}
        Opened = VirtualSignal(attributes)
        self.VirtualSignals.append(Opened) 
        
        attributes = {'Name': IMclosed_signal(self), 
                      'Description': self.Name + u' - Флаг ИМ закрыт', 
                      'Type': 'Bool', 
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}],
                      'Editable': 'False'}
        Closed = VirtualSignal(attributes)
        self.VirtualSignals.append(Closed)
        
        attributes = {'Name': IMbetween_signal(self), 
                      'Description': self.Name + u' - Флаг ИМ промежуточное положение', 
                      'Type': 'Bool', 
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'1'}],
                      'Editable': 'False'}
        Between = VirtualSignal(attributes)
        self.VirtualSignals.append(Between)
                
        attributes = {'Name': ALMcmd_signal(self), 
                      'Description': self.Name + u' - ИМ не выполнил команду за отведённое время', 
                      'Type': 'Bool',
                      'toHMI': True, 
                      'toMB': True, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'1'}], 
                      'Editable': 'False'}
        CMD_A = VirtualSignal(attributes)
        self.VirtualSignals.append(CMD_A) 
        
        attributes = {'Name': ALMhard_signal(self), 
                      'Description': self.Name + u' - ИМ физическая неисправность', 
                      'Type': 'Bool', 
                      'toHMI': True, 
                      'toMB': True, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'1'}], 
                      'Editable': 'False'}
        HARD_A = VirtualSignal(attributes)
        self.VirtualSignals.append(HARD_A)
        
        attributes = {'Name': ALMsens_signal(self), 
                      'Description': self.Name + u' - ИМ физическая неисправность', 
                      'Type': 'Bool', 
                      'toHMI': True, 
                      'toMB': True, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Alarm 1', 'PRIOR':'1', 'AL_CLR':'red', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'1'}], 
                      'Editable': 'False'}
        SENS_A = VirtualSignal(attributes)
        self.VirtualSignals.append(SENS_A)
        
        self.RowsLocal.append(['VALVE_DI_' + str(self.number), 'VALVE_DI', 'VAR', u'Обработка VALVE'])   
        
        #self.RowsGlobal.append([TM.Name,    TM.Type.upper(),    'VAR_GLOBAL',   TM.Description, '', '', 1, 0, 1])
        #self.RowsGlobal.append([RT.Name,    RT.Type.upper(),    'VAR_GLOBAL',   RT.Description, '', '', 1, 0, 1])
        self.RowsGlobal.append([EBlock.Name, EBlock.Type.upper(), 'VAR_GLOBAL',   EBlock.Description, '', '', 0, 0, 1])
        #self.RowsGlobal.append([LBlock.Name, LBlock.Type.upper(), 'VAR_GLOBAL',   LBlock.Description, '', '', 0, 0, 1])
        self.RowsLocal.append( [TM.Name,     TM.Type.upper(),     'VAR',          TM.Description, '', 'TIME#10s', 1])  
        self.RowsLocal.append( [RT.Name,     RT.Type.upper(),     'VAR',          RT.Description, '', '', 1])  
        self.RowsLocal.append( [EBlock.Name, EBlock.Type.upper(), 'VAR_EXTERNAL', EBlock.Description]) 
        self.RowsLocal.append( [LBlock.Name, LBlock.Type.upper(), 'VAR',          LBlock.Description]) 
        
        self.RowsGlobal.append([ModeA.Name, ModeA.Type.upper(), 'VAR_GLOBAL',   ModeA.Description, '', '', 1, 0, 1])
        self.RowsGlobal.append([ModeM.Name, ModeM.Type.upper(), 'VAR_GLOBAL',   ModeM.Description, '', '', 1, 0, 1])
        self.RowsGlobal.append([ModeL.Name, ModeL.Type.upper(), 'VAR_GLOBAL',   ModeL.Description, '', '', 1, 0, 1])
        self.RowsLocal.append( [ModeA.Name, ModeA.Type.upper(), 'VAR_EXTERNAL', ModeA.Description])  
        self.RowsLocal.append( [ModeM.Name, ModeM.Type.upper(), 'VAR_EXTERNAL', ModeM.Description])  
        self.RowsLocal.append( [ModeL.Name, ModeL.Type.upper(), 'VAR_EXTERNAL', ModeL.Description])  
        
        self.RowsGlobal.append([ALGO.Name, ALGO.Type.upper(), 'VAR_GLOBAL',   ALGO.Description, '', '', 0, 0, 1])
        self.RowsGlobal.append([ALGS.Name, ALGS.Type.upper(), 'VAR_GLOBAL',   ALGS.Description, '', '', 0, 0, 1])
        self.RowsGlobal.append([ALGC.Name, ALGC.Type.upper(), 'VAR_GLOBAL',   ALGC.Description, '', '', 0, 0, 1])
        self.RowsLocal.append( [ALGO.Name, ALGO.Type.upper(), 'VAR_EXTERNAL', ALGO.Description])  
        self.RowsLocal.append( [ALGS.Name, ALGS.Type.upper(), 'VAR_EXTERNAL', ALGS.Description]) 
        self.RowsLocal.append( [ALGC.Name, ALGC.Type.upper(), 'VAR_EXTERNAL', ALGC.Description])  
        
        self.RowsGlobal.append([CMDO.Name, CMDO.Type.upper(), 'VAR_GLOBAL',   CMDO.Description, '', '', 0, 0, 1])
        self.RowsGlobal.append([CMDS.Name, CMDS.Type.upper(), 'VAR_GLOBAL',   CMDS.Description, '', '', 0, 0, 1])
        self.RowsGlobal.append([CMDC.Name, CMDC.Type.upper(), 'VAR_GLOBAL',   CMDC.Description, '', '', 0, 0, 1])
        self.RowsLocal.append( [CMDO.Name, CMDO.Type.upper(), 'VAR_EXTERNAL', CMDO.Description])  
        self.RowsLocal.append( [CMDS.Name, CMDS.Type.upper(), 'VAR_EXTERNAL', CMDS.Description])  
        self.RowsLocal.append( [CMDC.Name, CMDC.Type.upper(), 'VAR_EXTERNAL', CMDC.Description])  
        
        #self.RowsGlobal.append([LOCO.Name, LOCO.Type.upper(), 'VAR_GLOBAL',   LOCO.Description, '', '', 0, 0, 1])
        #self.RowsGlobal.append([LOCS.Name, CMDS.Type.upper(), 'VAR_GLOBAL',   LOCS.Description, '', '', 0, 0, 1])
        #self.RowsGlobal.append([LOCC.Name, LOCC.Type.upper(), 'VAR_GLOBAL',   LOCC.Description, '', '', 0, 0, 1])
        #self.RowsLocal.append( [LOCO.Name, LOCO.Type.upper(), 'VAR_EXTERNAL', LOCO.Description])  
        #self.RowsLocal.append( [LOCS.Name, CMDS.Type.upper(), 'VAR_EXTERNAL', LOCS.Description]) 
        #self.RowsLocal.append( [LOCC.Name, LOCC.Type.upper(), 'VAR_EXTERNAL', LOCC.Description])  
        
        self.RowsGlobal.append([Opening.Name, Opening.Type.upper(), 'VAR_GLOBAL', Opening.Description, '', '', 0, 0, 1])
        self.RowsGlobal.append([Closing.Name, Closing.Type.upper(), 'VAR_GLOBAL', Closing.Description, '', '', 0, 0, 1])
        self.RowsGlobal.append([Opened.Name,  Opened.Type.upper(),  'VAR_GLOBAL', Opened.Description, '', '', 0, 0, 1])
        self.RowsGlobal.append([Closed.Name,  Closed.Type.upper(),  'VAR_GLOBAL', Closed.Description, '', '', 0, 0, 1])
        self.RowsGlobal.append([Between.Name, Between.Type.upper(), 'VAR_GLOBAL', Between.Description, '', '', 0, 0, 1])
        self.RowsLocal.append( [Opening.Name, Opening.Type.upper(), 'VAR_EXTERNAL', Opening.Description])  
        self.RowsLocal.append( [Closing.Name, Closing.Type.upper(), 'VAR_EXTERNAL', Closing.Description])
        self.RowsLocal.append( [Opened.Name,  Opened.Type.upper(),  'VAR_EXTERNAL', Opened.Description])  
        self.RowsLocal.append( [Closed.Name,  Closed.Type.upper(),  'VAR_EXTERNAL', Closed.Description])
        self.RowsLocal.append( [Between.Name, Between.Type.upper(), 'VAR_EXTERNAL', Between.Description])  
        
        self.RowsGlobal.append([CMD_A.Name,  CMD_A.Type.upper(),  'VAR_GLOBAL',   CMD_A.Description, '', '', 0, 0, 1])
        self.RowsGlobal.append([HARD_A.Name, HARD_A.Type.upper(), 'VAR_GLOBAL',   HARD_A.Description, '', '', 0, 0, 1])
        self.RowsGlobal.append([SENS_A.Name, SENS_A.Type.upper(), 'VAR_GLOBAL',   SENS_A.Description, '', '', 0, 0, 1])
        self.RowsLocal.append( [CMD_A.Name,  CMD_A.Type.upper(),  'VAR_EXTERNAL', CMD_A.Description])  
        self.RowsLocal.append( [HARD_A.Name, HARD_A.Type.upper(), 'VAR_EXTERNAL', HARD_A.Description])
        self.RowsLocal.append( [SENS_A.Name, SENS_A.Type.upper(), 'VAR_EXTERNAL', SENS_A.Description])    
        
        self.RowsCode.append('(*Исполнительный механизм ' + str(self.Name) + ' *)\n')
        self.RowsCode.append('VALVE_DI_' + str(self.number) + '(DI_Opened:=' + (str(self.SO.TagChannel) if self.SO else (' NOT ' + str(self.SC.TagChannel) if self.SC else 'False')) + ',DI_Closed:=' + (str(self.SC.TagChannel) if self.SC else (' NOT ' + str(self.SO.TagChannel) if self.SO else 'False')) + \
                             ',DI_Fault:=' + (str(self.SN.TagChannel) if self.SN else 'False') + ',RT:=' + str(RT.Name) + ',Time_OC:=' + str(TM.Name) + ',Block:=' + str(LBlock.Name) + ',\n')
        self.RowsCode.append('Mode_A:=' + str(ModeA.Name) + ',Mode_M:=' + str(ModeM.Name) + ',Mode_L:=' + str(ModeL.Name) + ',\n')
        self.RowsCode.append('Cmd_open_A:=' + str(ALGO.Name) + ',Cmd_close_A:=' + str(ALGC.Name) + ',Cmd_stop_A:=' + str(ALGS.Name) + ',\n')
        #self.RowsCode.append('Cmd_open_L:=' + str(LOCO.Name) + ',Cmd_close_L:=' + str(LOCC.Name) + ',Cmd_stop_L:=' + str(LOCS.Name) + ',\n')
        self.RowsCode.append('Cmd_open_M:=' + str(CMDO.Name) + ',Cmd_close_M:=' + str(CMDC.Name) + ',Cmd_stop_M:=' + str(CMDS.Name) + ')\n')        
        
        self.RowsCode.append((str(self.CO.TagChannel) if self.CO else '(*[Paste TagName here]') + ':=VALVE_DI_' + str(self.number) + '.DO_Open;' + ('*)' if not self.CO else '') + '\n')   
        self.RowsCode.append((str(self.CS.TagChannel) if self.CS else '(*[Paste TagName here]') + ':=VALVE_DI_' + str(self.number) + '.DO_Stop;' + ('*)' if not self.CS else '') + '\n')   
        self.RowsCode.append((str(self.CC.TagChannel) if self.CC else '(*[Paste TagName here]') + ':=VALVE_DI_' + str(self.number) + '.DO_Close;' + ('*)' if not self.CC else '') + '\n')   
        
        self.RowsCode.append(str(Opened.Name)  + ':=VALVE_DI_' + str(self.number) + '.Opened;\n')   
        self.RowsCode.append(str(Opening.Name) + ':=VALVE_DI_' + str(self.number) + '.Opening;\n')   
        self.RowsCode.append(str(Between.Name) + ':=VALVE_DI_' + str(self.number) + '.Between;\n')   
        self.RowsCode.append(str(Closing.Name) + ':=VALVE_DI_' + str(self.number) + '.Closing;\n')   
        self.RowsCode.append(str(Closed.Name)  + ':=VALVE_DI_' + str(self.number) + '.Closed;\n')   
        self.RowsCode.append(str(CMD_A.Name)   + ':=VALVE_DI_' + str(self.number) + '.Alarm_CMD;\n')
        self.RowsCode.append(str(SENS_A.Name)  + ':=VALVE_DI_' + str(self.number) + '.Alarm_SENS;\n')
        self.RowsCode.append(str(HARD_A.Name)  + ':=VALVE_DI_' + str(self.number) + '.Alarm_HARD;\n')   
        self.RowsCode.append(str(CMDO.Name)    + ':=VALVE_DI_' + str(self.number) + '.Cmd_open_M;\n')   
        self.RowsCode.append(str(CMDS.Name)    + ':=VALVE_DI_' + str(self.number) + '.Cmd_stop_M;\n') 
        self.RowsCode.append(str(CMDC.Name)    + ':=VALVE_DI_' + str(self.number) + '.Cmd_close_M;\n')  
        
        self.RowsCode.append('(*Сборка блокировочных параметров*)\n')        
        self.RowsCode.append(str(LBlock.Name) + ':=' + str(EBlock.Name) + (' OR NOT ' + str(self.SG.TagChannel) if self.SG else '') + (' OR NOT ' + str(self.SD.TagChannel) if self.SD else '') + (' OR ' + str(self.SL.TagChannel) if self.SL else '') + ';\n')        
        self.RowsCode.append('\n') 
            
    def SaySignals(self):
        print self.Name, self.Signals.keys()
        
class PID(object):
    Name = u'Noname'
    Prefix = u'P_'
    AO = None
    POS = None
    PV = None     
    SO = None
    SC = None
    SD = None
    SL = None
    SG = None  
    SN = None 
    number = 0  
    def __init__(self, Name, Signals):
        self.Name = Name
        self.Signals = Signals
        self.VirtualSignals = []
        self.RowsGlobal = []
        self.RowsLocal = []
        self.RowsCode = []
        self.__class__.number += 1    
      
        if Signals.get('AO'):
            self.AO = Signals['AO']
            self.AO.InGroup = True  
            self.RowsLocal.append([self.AO.TagChannel, u'CData_REAL', 'VAR_EXTERNAL', self.AO.Description_rus])
            if self.AO.ControlledVariable:
                self.PV = self.AO.ControlledVariable 
                if type(self.PV) == Signal:          
                    #self.PV.InGroup = True
                    #self.PV.toHMI = True
                    #self.PV.toMB = True     
                    #self.PV.Alarming = []
                    #self.RowsLocal.append([self.PV.TagChannel, u'REAL', 'VAR_EXTERNAL', self.PV.Description_rus])                
                    self.Signals['PV'] = self.PV
                else:
                    self.RowsGlobal.append([self.PV, u'REAL', 'VAR_GLOBAL',   u'Регулируемый параметр', '', '', 0, 0, 1])
                    self.RowsLocal.append( [self.PV, u'REAL', 'VAR_EXTERNAL', u'Регулируемый параметр'])                
        if Signals.get('POS'):
            self.POS = Signals['POS']  
            self.POS.InGroup = True
            self.POS.toHMI = True
            self.POS.toMB = True   
            self.POS.Alarming = []
        if Signals.get('PV'):
            self.PV = Signals['PV'] 
            self.PV.InGroup = True
            self.PV.toHMI = True
            self.PV.toMB = True  
            self.PV.Alarming = [] 
            self.RowsLocal.append([self.PV.TagChannel, u'REAL', 'VAR_EXTERNAL', self.PV.Description_rus]) 
        if Signals.get('SO'):
            self.SO = Signals['SO']   
            self.SO.InGroup = True 
            self.SO.toHMI = True
            self.SO.toMB = True
            self.SO.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'OP', 'SH_EN':'', 'AL_TXT': u'1'}]   
        if Signals.get('SC'):
            self.SC = Signals['SC']    
            self.SC.InGroup = True 
            self.SC.toHMI = True
            self.SC.toMB = True
            self.SC.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'CL', 'SH_EN':'', 'AL_TXT': u'1'}]  
        if Signals.get('SOG'):
            self.SOG = Signals['SOG']     
            self.SOG.InGroup = True 
            self.SOG.toHMI = True
            self.SOG.toMB = True
            self.SOG.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'OPG', 'SH_EN':'', 'AL_TXT': u'1'}]              
        if Signals.get('SCG'):
            self.SCG = Signals['SCG'] 
            self.SCG.InGroup = True 
            self.SCG.toHMI = True
            self.SCG.toMB = True
            self.SCG.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'', 'SH_EN':'', 'AL_TXT': u'0'}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'CLG', 'SH_EN':'', 'AL_TXT': u'1'}] 
        if Signals.get('SD'):
            self.SD = Signals['SD'] 
            self.SD.InGroup = True 
            self.SD.toHMI = True
            self.SD.toMB = True
            self.SD.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'L', 'SH_EN':'', 'AL_TXT': u'Местный'}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'R', 'SH_EN':'', 'AL_TXT': u'Дистанционный'}]   
        if Signals.get('SL'):
            self.SL = Signals['SL'] 
            self.SL.InGroup = True 
            self.SL.toHMI = True
            self.SL.toMB = True
            self.SL.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'R', 'SH_EN':'', 'AL_TXT': u'Дистанционный'}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'L', 'SH_EN':'', 'AL_TXT': u'Местный'}] 
        if Signals.get('SG'):
            self.SG = Signals['SG'] 
            self.SG.InGroup = True 
            self.SG.toHMI = True
            self.SG.toMB = True
            self.SG.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'NRD', 'SH_EN':'', 'AL_TXT': u'Не готов'}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'RDY', 'SH_EN':'', 'AL_TXT': u'Готов'}] 
        if Signals.get('SN'):
            self.SN = Signals['SN']
            self.SN.InGroup = True 
            self.SN.toHMI = True
            self.SN.toMB = True
            self.SN.Alarming = [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'NR', 'SH_EN':'', 'AL_TXT': u'В норме'}, 
                                {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'ALR', 'SH_EN':'', 'AL_TXT': u'Неисправность'}]
         
        attributes = {'Name': SV_signal(self), 
                      'Description': self.Name + u' - Уставка для ПИД', 
                      'Type': 'Real', 
                      'toHMI': True, 
                      'toMB': True, 
                      'Alarming': [],
                      'Editable': 'True'}
        SV = VirtualSignal(attributes)
        self.VirtualSignals.append(SV)       
        
        attributes = {'Name': MV_signal(self), 
                      'Description': self.Name + u' - Положение от оператора для ПИД', 
                      'Type': 'Real', 
                      'toHMI': True, 
                      'toMB': True, 
                      'Alarming': [],
                      'Editable': 'True'}
        MV = VirtualSignal(attributes)
        self.VirtualSignals.append(MV) 
        
        attributes = {'Name': KP_signal(self), 
                      'Description': self.Name + u' - Пропорциональный коэффициент для ПИД', 
                      'Type': 'Real', 
                      'toHMI': True, 
                      'toMB': True, 
                      'Alarming': [],
                      'Editable': 'True'}
        KP = VirtualSignal(attributes)
        self.VirtualSignals.append(KP) 
        
        attributes = {'Name': KI_signal(self), 
                      'Description': self.Name + u' - Интегральный коэффициент для ПИД', 
                      'Type': 'Real', 
                      'toHMI': True, 
                      'toMB': True, 
                      'Alarming': [],
                      'Editable': 'True'}
        KI = VirtualSignal(attributes)
        self.VirtualSignals.append(KI) 
        
        attributes = {'Name': KD_signal(self), 
                      'Description': self.Name + u' - Дифференциальный коэффициент для ПИД', 
                      'Type': 'Real', 
                      'toHMI': True, 
                      'toMB': True, 
                      'Alarming': [],
                      'Editable': 'True'}
        KD = VirtualSignal(attributes)
        self.VirtualSignals.append(KD) 
        
        attributes = {'Name': MA_signal(self), 
                      'Description': self.Name + u' - Режим (ручной/автомат) для ПИД', 
                      'Type': 'Bool', 
                      'toHMI': True, 
                      'toMB': True, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'M', 'SH_EN':'', 'AL_TXT': u'Ручной'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'A', 'SH_EN':'', 'AL_TXT': u'Автомат'}],
                      'Editable': 'True'}
        Mode = VirtualSignal(attributes)
        self.VirtualSignals.append(Mode) 
        
        attributes = {'Name': DN_signal(self), 
                      'Description': self.Name + u' - Закон (прямой/обратный) для ПИД', 
                      'Type': 'Bool', 
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'F', 'SH_EN':'', 'AL_TXT': u'Прямой'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'B', 'SH_EN':'', 'AL_TXT': u'Обратный'}],
                      'Editable': 'True'}
        DN = VirtualSignal(attributes)
        self.VirtualSignals.append(DN) 
        
        attributes = {'Name': TG_signal(self), 
                      'Description': self.Name + u' - Слежение за PV в SV для безударного переключения режима Р->А для ПИД', 
                      'Type': 'Bool', 
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [{'IT_ST':'BOOLEAN 0', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'gray', 'MNEM':'ON', 'SH_EN':'', 'AL_TXT': u'Выключен'}, 
                                   {'IT_ST':'BOOLEAN 1', 'AL_ST':'Normal', 'PRIOR':'0', 'AL_CLR':'green', 'MNEM':'OFF', 'SH_EN':'', 'AL_TXT': u'Включён'}],
                      'Editable': 'True'}
        TG = VirtualSignal(attributes)
        self.VirtualSignals.append(TG) 
        
        attributes = {'Name': DD_signal(self), 
                      'Description': self.Name + u' - Мёртвая зона PV для ПИД', 
                      'Type': 'Real', 
                      'toHMI': False, 
                      'toMB': False, 
                      'Alarming': [],
                      'Editable': 'True'}
        DD = VirtualSignal(attributes)
        self.VirtualSignals.append(DD)   
        
        self.RowsLocal.append(['PID_Inc_' + str(self.number), 'PID_Inc', 'VAR', u'Обработка PID'])   
        
        self.RowsGlobal.append([SV.Name, SV.Type.upper(), 'VAR_GLOBAL', SV.Description, '', '', 1, 0, 1])
        self.RowsGlobal.append([MV.Name, MV.Type.upper(), 'VAR_GLOBAL', MV.Description, '', '', 1, 0, 1])  
        self.RowsLocal.append( [SV.Name, SV.Type.upper(), 'VAR',        SV.Description])  
        self.RowsLocal.append( [MV.Name, MV.Type.upper(), 'VAR',        MV.Description]) 
        
        self.RowsGlobal.append([KP.Name, KP.Type.upper(), 'VAR_GLOBAL',   KP.Description, '', '', 1, 0, 1])
        self.RowsGlobal.append([KI.Name, KI.Type.upper(), 'VAR_GLOBAL',   KI.Description, '', '', 1, 0, 1])
        self.RowsGlobal.append([KD.Name, KD.Type.upper(), 'VAR_GLOBAL',   KD.Description, '', '', 1, 0, 1])
        self.RowsLocal.append( [KP.Name, KP.Type.upper(), 'VAR_EXTERNAL', KP.Description])  
        self.RowsLocal.append( [KI.Name, KI.Type.upper(), 'VAR_EXTERNAL', KI.Description])  
        self.RowsLocal.append( [KD.Name, KD.Type.upper(), 'VAR_EXTERNAL', KD.Description])  
        
        #self.RowsGlobal.append([DN.Name, DN.Type.upper(), 'VAR_GLOBAL',   DN.Description, '', '', 0, 0, 1])
        #self.RowsGlobal.append([TG.Name, TG.Type.upper(), 'VAR_GLOBAL',   TG.Description, '', '', 0, 0, 1])
        #self.RowsGlobal.append([DD.Name, DD.Type.upper(), 'VAR_GLOBAL',   DD.Description, '', '', 0, 0, 1])        
        self.RowsLocal.append( [DN.Name, DN.Type.upper(), 'VAR', DN.Description, '', '', 1])  
        self.RowsLocal.append( [TG.Name, TG.Type.upper(), 'VAR', TG.Description, '', '', 1]) 
        self.RowsLocal.append( [DD.Name, DD.Type.upper(), 'VAR', DD.Description, '', '', 1])   
        
        self.RowsGlobal.append([Mode.Name, Mode.Type.upper(), 'VAR_GLOBAL',   Mode.Description, '', '', 0, 0, 1])
        self.RowsLocal.append( [Mode.Name, Mode.Type.upper(), 'VAR_EXTERNAL', Mode.Description])   
        
        self.RowsCode.append('(*ПИД регулятор ' + str(self.Name) + ' *)\n')
        self.RowsCode.append('PID_Inc_' + str(self.number) + '(PV:=' + (str(self.PV.TagChannel) if type(self.PV) == Signal else (self.PV if self.PV else 'REAL#0.0')) + ',SV:=' +  str(SV.Name) + ',MV_MAN:=' + str(MV.Name) + ',\n')
        self.RowsCode.append('Kp:=' + str(KP.Name) + ',Ki:=' + str(KI.Name) + ',Kd:=' + str(KD.Name) + ',\n')        
        self.RowsCode.append('MODE_MAN:=' + str(Mode.Name) + ',DIRECTION:=' + str(DN.Name) + ',TRACKING:=' + str(TG.Name) + ',Dopusk:=' + str(DD.Name) + ')\n')        
        
        self.RowsCode.append((str(self.AO.TagChannel) if self.AO else '(*[Paste TagName here]') + ':=PID_Inc_' + str(self.number) + '.MV_CDATA;' + ('*)' if not self.AO else '') + '\n')         
        
        self.RowsCode.append(str(SV.Name)  + ':=PID_Inc_' + str(self.number) + '.SV;\n')   
        self.RowsCode.append(str(MV.Name) + ':=PID_Inc_' + str(self.number) + '.MV_MAN;\n')   
        #self.RowsCode.append(str(_____) + ':=PID_Inc_' + str(self.number) + '.MV;\n')           
        self.RowsCode.append('\n') 
            
    def SaySignals(self):
        print self.Name, self.Signals.keys()
    
