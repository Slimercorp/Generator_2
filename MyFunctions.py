#!/usr/bin/env python
# -*- coding: utf-8 -*-      
from Transliterate import transliterate
import re

def SplitTagName(TagChannel):  
    TagChannel = TagChannel.replace(' ', '')
    result = None    
    #PT
    pattern = re.compile('^S([0-9]{3,4})(I|P|Z|T|L|F|PD)I(.*)')
    if pattern.match(TagChannel):  
        match = pattern.findall(TagChannel)
        result = match[0]         
    #PZT
    pattern = re.compile('^S([0-9]{3,4})(PZ|TZ|LZ|FZ|PDZ)I(.*)')
    if pattern.match(TagChannel):  
        match = pattern.findall(TagChannel)
        result = match[0]    
    #LS
    pattern = re.compile('^S([0-9]{3,4})(LZ|L)S(.*)')
    if pattern.match(TagChannel):  
        match = pattern.findall(TagChannel)
        result = match[0]        
    #PV
    pattern = re.compile('^S([0-9]{3,4})(L|P|PD|T|F)V(.*)')
    if pattern.match(TagChannel):  
        match = pattern.findall(TagChannel)
        result = match[0]         
    return result

def DBsignal(signal):    
    u'Деблокировка'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'MI' + ListOfParts[2]
    else:
        return signal.TagChannel + '_DB'
        
def OOP_signal(signal):
    u'Сигнал размыкание выхода регулятора'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'OOP' + ListOfParts[2]
    else:
        return signal.TagChannel + '_OOP'
    
def SCCsignal(signal):   
    u'Контроль целостности цепи' 
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'AF' + ListOfParts[2]
    else:
        return signal.TagChannel + '_SCC'
    
def HHsignal(signal):    
    u'Верхний аварийный предел'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'G' + ListOfParts[2]
    else:
        return signal.TagChannel + '_HH'
    
def HHEsignal(signal):    
    u'Включение ВАУ'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'GE' + ListOfParts[2]
    else:
        return signal.TagChannel + '_HHE'

def HHDsignal(signal):    
    u'Задержка ВАУ'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'GD' + ListOfParts[2]
    else:
        return signal.TagChannel + '_HHD'
    
def Hsignal(signal):    
    u'Верхний предупредительный предел'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'H' + ListOfParts[2]
    else:
        return signal.TagChannel + '_H'
    
def HEsignal(signal):
    u'Включение ВПУ'  
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'HE' + ListOfParts[2]
    else:
        return signal.TagChannel + '_HE'

def HDsignal(signal):    
    u'Задержка ВПУ'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'HD' + ListOfParts[2]
    else:
        return signal.TagChannel + '_HD'
    
def Lsignal(signal):    
    u'Нижний предупредительынй предел'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'L' + ListOfParts[2]
    else:
        return signal.TagChannel + '_L'
    
def LEsignal(signal):    
    u'Включение НПУ'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'LE' + ListOfParts[2]
    else:
        return signal.TagChannel + '_LE'
    
def LDsignal(signal):    
    u'Задержка НПУ'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'LD' + ListOfParts[2]
    else:
        return signal.TagChannel + '_LD'
    
def LLsignal(signal):    
    u'Нижний аварийный предел'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'M' + ListOfParts[2]
    else:
        return signal.TagChannel + '_LL'
    
def LLEsignal(signal):    
    u'Включение НАУ'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'ME' + ListOfParts[2]
    else:
        return signal.TagChannel + '_LLE'
    
def LLDsignal(signal):    
    u'Задержка НАУ'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'MD' + ListOfParts[2]
    else:
        return signal.TagChannel + '_LLD'
    
def RSLsignal(signal):    
    u'Нижний порог сырого значения'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'RSL' + ListOfParts[2]
    else:
        return signal.TagChannel + '_RSL'
    
def RSHsignal(signal):    
    u'Верхний порог сырого значения'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'RSH' + ListOfParts[2]
    else:
        return signal.TagChannel + '_RSH'
    
def ESLsignal(signal):    
    u'Нижний порог значения в инженерных единицах'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'ESL' + ListOfParts[2]
    else:
        return signal.TagChannel + '_ESL'
    
def ESHsignal(signal):    
    u'Верхний порог значения в инженерных единицах'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'ESH' + ListOfParts[2]
    else:
        return signal.TagChannel + '_ESH'
    
def ERRsignal(signal):    
    u'Возможное отклонение в процентах сырого значения от заданных порогов'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'ERR' + ListOfParts[2]
    else:
        return signal.TagChannel + '_ERR'
    
def HYSsignal(signal):    
    u'Гистерезис'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'HYS' + ListOfParts[2]
    else:
        return signal.TagChannel + '_HYS'
    
def AOFsignal(signal):    
    u'Отлючение сигнализаций'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'AOF' + ListOfParts[2]
    else:
        return signal.TagChannel + '_AOF'
    
def AHHsignal(signal):    
    u'Аларм HH'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'AHH' + ListOfParts[2]
    else:
        return signal.TagChannel + '_A_HH'
    
def AHsignal(signal):    
    u'Аларм H'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'AH' + ListOfParts[2]
    else:
        return signal.TagChannel + '_A_H'
    
def ALsignal(signal):    
    u'Аларм L'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'AL' + ListOfParts[2]
    else:
        return signal.TagChannel + '_A_L'
    
def ALLsignal(signal):    
    u'Аларм LL'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'ALL' + ListOfParts[2]
    else:
        return signal.TagChannel + '_A_LL'
    
def IOPPsignal(signal):    
    u'Аларм КЗ'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'IOPP' + ListOfParts[2]
    else:
        return signal.TagChannel + '_IOPP'
    
def IOPMsignal(signal):    
    u'Аларм обрыв'
    ListOfParts = SplitTagName(signal.TagChannel)
    if ListOfParts:
        return 'S' + ListOfParts[0] + ListOfParts[1] + 'IOPM' + ListOfParts[2]
    else:
        return signal.TagChannel + '_IOPM'
    
def Asignal(signal):    
    u'Аларм для FastTools'
    return signal.TagChannel + '_A'
    
#Сигналы ИМ
def GiveMeLoopName(Name, prefix = u''):
    if type(Name) == str:
        Name = Name.decode('utf-8')
    result = re.sub(u'\W', u'', transliterate(Name))
    return (prefix + result).upper()

def RTsignal(im):
    u'Флаг удержания управляющей команды после прихода концевика'
    return GiveMeLoopName(im.Name, im.Prefix) + '_RT'

def EBLsignal(im):
    u'Агрегатор причин для блокировки ИМ. (Например отработка ПАЗ)'
    return GiveMeLoopName(im.Name, im.Prefix) + '_EBL'
    
def LBLsignal(im):
    u'Агрегатор причин для блокировки ИМ. (Например, локальный режим, ремонт и т.п.)'
    return GiveMeLoopName(im.Name, im.Prefix) + '_LBL'
    
def TMsignal(im):
    u'Время на выполнение команды ИМом'
    return GiveMeLoopName(im.Name, im.Prefix) + '_TM'
    
def ModeAsignal(im):
    u'Флаг режима АВТОМАТ'
    return GiveMeLoopName(im.Name, im.Prefix) + '_AUT'
    
def ModeMsignal(im):
    u'Флаг режима РУЧНОЙ'
    return GiveMeLoopName(im.Name, im.Prefix) + '_MAN'
    
def ModeLsignal(im):
    u'Флаг режима ЛОКАЛЬНЫЙ'
    return GiveMeLoopName(im.Name, im.Prefix) + '_LOC'
    
def CMDstart_Asignal(im):
    u'Команда ПУСК от алгоритма'
    return GiveMeLoopName(im.Name, im.Prefix) + '_ALGR'
    
def CMDstop_Asignal(im):
    u'Команда СТОП от алгоритма'
    return GiveMeLoopName(im.Name, im.Prefix) + '_ALGS'
    
def CMDopen_Asignal(im):
    u'Команда ОТКРЫТЬ от алгоритма'
    return GiveMeLoopName(im.Name, im.Prefix) + '_ALGO'
    
def CMDclose_Asignal(im):
    u'Команда ЗАКРЫТЬ от алгоритма'
    return GiveMeLoopName(im.Name, im.Prefix) + '_ALGC'
    
def CMDstart_Msignal(im):
    u'Команда ПУСК от оператора'
    return GiveMeLoopName(im.Name, im.Prefix) + '_CMDR'
    
def CMDstop_Msignal(im):
    u'Команда СТОП от оператора'
    return GiveMeLoopName(im.Name, im.Prefix) + '_CMDS'
    
def CMDopen_Msignal(im):
    u'Команда ОТКРЫТЬ от оператора'
    return GiveMeLoopName(im.Name, im.Prefix) + '_CMDO'
    
def CMDclose_Msignal(im):
    u'Команда ЗАКРЫТЬ от оператора'
    return GiveMeLoopName(im.Name, im.Prefix) + '_CMDC'
    
def CMDstart_Lsignal(im):
    u'Команда ПУСК от местного щита управления, если команды проходят через контроллер'
    return GiveMeLoopName(im.Name, im.Prefix) + '_LOCR'
    
def CMDstop_Lsignal(im):
    u'Команда СТОП от местного щита управления, если команды проходят через контроллер'
    return GiveMeLoopName(im.Name, im.Prefix) + '_LOCS'
    
def CMDopen_Lsignal(im):
    u'Команда ОТКРЫТЬ от местного щита управления, если команды проходят через контроллер'
    return GiveMeLoopName(im.Name, im.Prefix) + '_LOCO'
    
def CMDclose_Lsignal(im):
    u'Команда ЗАКРЫТЬ от местного щита управления, если команды проходят через контроллер'
    return GiveMeLoopName(im.Name, im.Prefix) + '_LOCC'    
    
def IMstarting_signal(im):
    u'Флаг - ИМ запускается'
    return GiveMeLoopName(im.Name, im.Prefix) + '_FRG'
    
def IMstoping_signal(im):
    u'Флаг - ИМ останавливается'
    return GiveMeLoopName(im.Name, im.Prefix) + '_FSG'
    
def IMstarted_signal(im):
    u'Флаг - ИМ запущен'
    return GiveMeLoopName(im.Name, im.Prefix) + '_FRD'
    
def IMstoped_signal(im):
    u'Флаг - ИМ остановлен'
    return GiveMeLoopName(im.Name, im.Prefix) + '_FSD'
    
def IMopening_signal(im):
    u'Флаг - ИМ открыватеся'
    return GiveMeLoopName(im.Name, im.Prefix) + '_FOG'
    
def IMclosing_signal(im):
    u'Флаг - ИМ закрывается'
    return GiveMeLoopName(im.Name, im.Prefix) + '_FCG'
    
def IMopened_signal(im):
    u'Флаг - ИМ открыт'
    return GiveMeLoopName(im.Name, im.Prefix) + '_FOD'
    
def IMclosed_signal(im):
    u'Флаг - ИМ закрыт'
    return GiveMeLoopName(im.Name, im.Prefix) + '_FCD'
    
def IMbetween_signal(im):
    u'Флаг - ИМ промежуточное положение'
    return GiveMeLoopName(im.Name, im.Prefix) + '_FBW'
    
def ALMcmd_signal(im):
    u'Флаг - ИМ не выполнил команду за отведённое время'
    return GiveMeLoopName(im.Name, im.Prefix) + '_ATM'
    
def ALMhard_signal(im):
    u'Флаг - ИМ физическая неисправность'
    return GiveMeLoopName(im.Name, im.Prefix) + '_SN'    
    
def ALMsens_signal(im):
    u'Флаг - ИМ одновременное присутствие двух концевиков'
    return GiveMeLoopName(im.Name, im.Prefix) + '_AS'
    
def SV_signal(im):
    u'Уставка для ПИД'
    return GiveMeLoopName(im.Name, im.Prefix) + '_SV'
    
def MV_signal(im):
    u'Положение от оператора для ПИД'
    return GiveMeLoopName(im.Name, im.Prefix) + '_MV'
    
def KP_signal(im):
    u'Пропорциональный коэффициент для ПИД'
    return GiveMeLoopName(im.Name, im.Prefix) + '_KP'
    
def KI_signal(im):
    u'Интегральный коэффициент для ПИД'
    return GiveMeLoopName(im.Name, im.Prefix) + '_KI'
    
def KD_signal(im):
    u'Дифференциальный коэффициент для ПИД'
    return GiveMeLoopName(im.Name, im.Prefix) + '_KD'
    
def MA_signal(im):
    u'Режим (ручной/автомат) для ПИД'
    return GiveMeLoopName(im.Name, im.Prefix) + '_MA'
    
def DN_signal(im):
    u'Закон (прямой/обратный) для ПИД'
    return GiveMeLoopName(im.Name, im.Prefix) + '_DN'
    
def TG_signal(im):
    u'Слежение за PV в SV для безударного переключения режима Р->А для ПИД'
    return GiveMeLoopName(im.Name, im.Prefix) + '_TG'
    
def DD_signal(im):
    u'Мёртвая зона PV для ПИД'
    return GiveMeLoopName(im.Name, im.Prefix) + '_DD'
    
if __name__ == "__main__":
    print GiveMeLoopName(u'  934-ВЕЩ23..MM123_A 3', u'i_')
    


    
    
    
    
