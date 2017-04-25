#!/usr/bin/env python
# -*- coding: utf-8 -*-        
#from MyControllers_lib import Signal, VirtualSignal
from MyFunctions import GiveMeLoopName

class FastTools(object):    
    u'''Фаст тулс )'''
    ProcAreas = 0
    ACKN_TYPE = "PROCESS_ACK"
    COL_GROUP = "ALL_ITEMS"    
    def __init__(self, Controller):
        self.Controller = Controller
        self.__class__.ProcAreas += 1
        self.ProcArea = self.ProcAreas
        
        self.Sections = [self.Controller.Name.upper()]
        self.AOIs = []
        
        self.CMD_i_Rows = []
        self.CMD_r_Rows = []
        self.LineRows = []
        self.COMstatusRows = []
        self.StationRows = []
        self.SectionsRows = []
        self.AOIRows = []
        
        self.PointRows = ['@LANGUAGE\n', \
                          'ENGLISH\n', \
                          '!===========================================================================================================\n', \
                          '@FIELDS\n', \
                          'NAME,DESCRIPTION,IO_ADDRESS,EXTERNAL_RELATION,CONV_SUB_TYPE\n', \
                          '@stardomfcx_point_df\n']
                          
        self.ItemtRows = ['@LANGUAGE\n', \
                          'ENGLISH\n', \
                          '!===========================================================================================================\n', \
                          '@FIELDS\n', \
                          'NAME,DESCRIPTION,COMMENT_1,COMMENT_2,ENG_UNIT,VALUE_FORMAT,ITEM_REP\n', \
                          'POINT_NAME,ALARMING,STORAGE,OPC_VISIBLE,OPC_READ,OPC_WRITE,SCALE_LOW_LIMIT,SCALE_HIGH_LIMIT\n', \
                          'ACKN_TYPE, COL_GROUP,PROCESS_LIST,HIGH_HIGH_LIMIT,HIGH_LIMIT,LOW_LIMIT,LOW_LOW_LIMIT\n', \
                          'ITEM_STAT_1,ITEM_STAT_2,ITEM_STAT_3,ITEM_STAT_4,ITEM_STAT_5,ITEM_STAT_6\n', \
                          'ALARM_STATE_1,ALARM_STATE_2,ALARM_STATE_3,ALARM_STATE_4,ALARM_STATE_5,ALARM_STATE_6\n', \
                          'PRIORITY_1,PRIORITY_2,PRIORITY_3,PRIORITY_4,PRIORITY_5,PRIORITY_6\n', \
                          'ALARM_TEXT_1,ALARM_TEXT_2,ALARM_TEXT_3,ALARM_TEXT_4,ALARM_TEXT_5,ALARM_TEXT_6\n', \
                          'ALARM_COLOR_1,ALARM_COLOR_2,ALARM_COLOR_3,ALARM_COLOR_4,ALARM_COLOR_5,ALARM_COLOR_6\n', \
                          'MNEMONIC_1,MNEMONIC_2,MNEMONIC_3,MNEMONIC_4,MNEMONIC_5,MNEMONIC_6\n', \
                          'SHELVE_ENABLED_1,SHELVE_ENABLED_2,SHELVE_ENABLED_3,SHELVE_ENABLED_4,SHELVE_ENABLED_5,SHELVE_ENABLED_6\n', \
                          'AOI_1,AOI_2,AOI_3,AOI_4,AOI_5,AOI_6\n', \
                          'AOI_7,AOI_8,AOI_9,AOI_10,AOI_11,AOI_12\n', \
                          'AOI_13,AOI_14,AOI_15,AOI_16\n', \
                          '@ITEM_DF\n']
        
        self.Points = {}
        self.Items = {}
        
        self.MakeLineFile()
        self.MakeCOMstatusFile()
        self.MakeStationFile()
        self.MakePointsAndItems()
        
        self.MakeSectionsFile()
        self.MakeAOIfile()
        self.MakeCMDfiles()
        
    def MakeCMDfiles(self):    
        self.CMD_i_Rows.append('echo off\n')
        self.CMD_i_Rows.append('COPY /Y Displays\*.* "%TLS_ALLUSERS_PATH%\wap\cfg\operatorInterfaces\DEPLOY\displays"\n')
        self.CMD_i_Rows.append('dssqld -i ' + self.LineName + ' -l\n')
        self.CMD_i_Rows.append('attrib *.qlo -R\n')
        self.CMD_i_Rows.append('del *.qlo\n')
        self.CMD_i_Rows.append('dssqld -i "Sections.qli" -l\n')
        self.CMD_i_Rows.append('dssqld -i "AOIs.qli" -l\n')
        self.CMD_i_Rows.append('dssqld -i "COMstatus.qli" -l\n')
        self.CMD_i_Rows.append('dssqld -i "Station.qli" -l\n')
        self.CMD_i_Rows.append('dssqld -i "Points.qli" -l\n')
        self.CMD_i_Rows.append('dssqld -i "Items.qli" -l\n')
        self.CMD_i_Rows.append('Exit\n')                
        
        self.CMD_r_Rows.append('attrib *.qlo -R\n')
        self.CMD_r_Rows.append('del *.qlo\n')
        self.CMD_r_Rows.append('dssqld -r "Items.qli" -l\n')
        self.CMD_r_Rows.append('dssqld -r "Points.qli" -l\n')
        self.CMD_r_Rows.append('dssqld -r "Station.qli" -l\n')
        self.CMD_r_Rows.append('dssqld -r "COMstatus.qli" -l\n')
        self.CMD_r_Rows.append('dssqld -r "AOIs.qli" -l\n')  
        self.CMD_r_Rows.append('dssqld -r "Sections.qli" -l\n') 
        self.CMD_r_Rows.append('dssqld -r ' + self.LineName + ' -l\n')
        self.CMD_r_Rows.append('Exit\n')
    
    def MakeSectionsFile(self):
        CreatedSections = []
        self.SectionsRows.append('@LANGUAGE\n')
        self.SectionsRows.append('ENGLISH\n')
        self.SectionsRows.append('!==================================================================================================================================\n')
        self.SectionsRows.append('@FIELDS\n')
        self.SectionsRows.append('NAME\n')        
        self.SectionsRows.append('@SECTION_DF\n')
        for sections in self.Sections:
            section = ''
            for sect in sections.split('.'):
                section = section + (sect if section == '' else '.' + sect)
                if section not in CreatedSections:
                    self.SectionsRows.append('"' + section + '"\n')
                    CreatedSections.append(section)
                    
    def MakeAOIfile(self):
        CreatedAOIs = []
        self.AOIRows.append('@LANGUAGE\n')
        self.AOIRows.append('ENGLISH\n')
        self.AOIRows.append('!==================================================================================================================================\n')
        self.AOIRows.append('@FIELDS\n')
        self.AOIRows.append('NAME,DESCRIPTION\n')        
        self.AOIRows.append('@ALARM_AOI_DF\n')
        for AOI in self.AOIs:
            if AOI not in CreatedAOIs:
                self.AOIRows.append('"' + AOI + '","' + AOI + '"\n')
                CreatedAOIs.append(AOI)
    
    def MakeLineFile(self):
        self.LineName = 'EQP' + self.Controller.Name.upper()         
        self.LineRows.append('@LANGUAGE\n')
        self.LineRows.append('ENGLISH\n')
        self.LineRows.append('!==================================================================================================================================\n')
        self.LineRows.append('@FIELDS\n')
        self.LineRows.append('NAME, DESCRIPTION, LINE_1_DEVICE,  LINE_2_DEVICE, EQUIPMENT_NODE, EQUIPMENT_MAN, HEART_BEAT, PERIODIC_TIME, REDUN_LINE\n')
        self.LineRows.append('\n')
        self.LineRows.append('@stardomfcx_line_df\n')
        self.LineRows.append('"' + str(self.LineName) + '", "The ' + str(self.LineName) + ' line", "localhost", "", 0, "' + str(self.LineName) + '", 100, 0, 0')
        
    def MakeCOMstatusFile(self):        
        self.COMstatus     = 'STATIONS.COMMUNICATION.' + str(self.Controller.Name).upper()
        self.COMstatusTCP1 = 'STATIONS.COMMUNICATION.' + str(self.Controller.Name).upper() + '_TCP1'
        self.COMstatusTCP2 = 'STATIONS.COMMUNICATION.' + str(self.Controller.Name).upper() + '_TCP2'
        self.Sections.append('STATIONS.COMMUNICATION')
        self.COMstatusRows.append('@LANGUAGE\n')
        self.COMstatusRows.append('ENGLISH\n')
        self.COMstatusRows.append('!==================================================================================================================================\n')
        self.COMstatusRows.append('@FIELDS\n')
        self.COMstatusRows.append('NAME,DESCRIPTION,ITEM_REP,ACKN_TYPE,COL_GROUP,ALARMING,OPC_VISIBLE,OPC_READ,OPC_WRITE\n')
        self.COMstatusRows.append('ITEM_STAT_1,ITEM_STAT_2,ALARM_STATE_1,ALARM_STATE_2,PRIORITY_1,PRIORITY_2,ALARM_COLOR_1,ALARM_COLOR_2,MNEMONIC_1,MNEMONIC_2\n')
        self.COMstatusRows.append('ALARM_TEXT_1,ALARM_TEXT_2\n')
        self.COMstatusRows.append('@ITEM_DF\n')
        self.COMstatusRows.append('"' + self.COMstatus + '","Статус связи","Boolean","' + self.ACKN_TYPE + '","' + self.COL_GROUP + '","1","1","1","0",\\\n')
        self.COMstatusRows.append('"BOOLEAN 1","BOOLEAN 0","Normal","Alarm 1","0","1","limegreen","red","NR","ALR",\\\n')
        self.COMstatusRows.append('"Связь в норме","Нет связи"\n')
        self.COMstatusRows.append('\n')
        self.COMstatusRows.append('"' + self.COMstatusTCP1 + '","статус линии связи TCP1","Boolean","' + self.ACKN_TYPE + '","' + self.COL_GROUP + '","1","1","1","0",\\\n')
        self.COMstatusRows.append('"BOOLEAN 1","BOOLEAN 0","Normal","Alarm 1","0","1","limegreen","red","NR","ALR",\\\n')
        self.COMstatusRows.append('"' + str(self.Controller.Name) + ' TCP1 линия связи в норме","' + str(self.Controller.Name) + ' TCP1 отказ линии связи"\n')
        self.COMstatusRows.append('\n')
        self.COMstatusRows.append('"' + self.COMstatusTCP2 + '","статус линии связи TCP2","Boolean","' + self.ACKN_TYPE + '","' + self.COL_GROUP + '","1","1","1","0",\\\n')
        self.COMstatusRows.append('"BOOLEAN 1","BOOLEAN 0","Normal","Alarm 1","0","1","limegreen","red","NR","ALR",\\\n')
        self.COMstatusRows.append('"' + str(self.Controller.Name) + ' TCP2 линия связи в норме","' + str(self.Controller.Name) + ' TCP2 отказ линии связи"\n')
        
    def MakeStationFile(self):
        self.StationRows.append('@LANGUAGE\n')
        self.StationRows.append('ENGLISH\n')
        self.StationRows.append('!==================================================================================================================================\n')
        self.StationRows.append('@FIELDS\n')
        self.StationRows.append('NAME,DESCRIPTION,REDUN_LINE,LINE\n')
        self.StationRows.append('STATUS_ITEM,LINE_1_ITEM,LINE_2_ITEM\n')
        self.StationRows.append('ON_SCAN,LINE_1_DEVICE\n')
        self.StationRows.append('@stardomfcx_station_df\n')
        self.StationRows.append('"' + str(self.Controller.Name).upper() + '","","0","' + self.LineName + '",\\\n')
        self.StationRows.append('"' + self.COMstatus + '","' + self.COMstatusTCP1 + '","' + self.COMstatusTCP2 + '",\\\n')
        self.StationRows.append('"1","localhost"\n')  
        
    def MakePoint(self, Point, Description, Tag, Editable = 'False', Representation = 'Normal'):        
        self.PointRows.append('"' + Point + '","' + Description + '","@GV.' + str(Tag) + '","' + ('Input' if Editable == 'False' else 'Input + Output') +'","' + Representation + '"\n')        
         
    def MakeItem(self, Frow, Srow = {}, Trow = {}, ALR = {}, AOIs = ['']):
        IT_ST = ['']*6
        AL_ST = ['']*6
        PRIOR = ['']*6
        AL_TXT = ['']*6
        AL_CLR = ['']*6
        MNEM = ['']*6
        SH_EN = ['']*6                
        for i in range(len(ALR)):
            IT_ST[i]  = ALR[i]['IT_ST']
            AL_ST[i]  = ALR[i]['AL_ST']
            PRIOR[i]  = ALR[i]['PRIOR']                
            AL_CLR[i] = ALR[i]['AL_CLR']
            MNEM[i]   = ALR[i]['MNEM']
            SH_EN[i]  = ALR[i]['SH_EN']                
            if type(ALR[i]['AL_TXT']) == unicode:
                AL_TXT[i] = ALR[i]['AL_TXT'].encode('utf-8')
            elif type(ALR[i]['AL_TXT']) == str:
                AL_TXT[i] = ALR[i]['AL_TXT']            
        
        aoi = ['']*16
        for i in range(len(AOIs)):
            aoi[i] = AOIs[i]
            
        frow = ['']*7
        frow[0] = Frow['Name']        if Frow.get('Name')        else 'DUMBitem'
        frow[1] = Frow['Description'] if Frow.get('Description') else ''
        frow[2] = Frow['Com_1']       if Frow.get('Com_1')       else ''
        frow[3] = Frow['Com_2']       if Frow.get('Com_2')       else ''
        frow[4] = Frow['EU']          if Frow.get('EU')          else ''
        frow[5] = Frow['V_format']    if Frow.get('V_format')    else ''
        frow[6] = Frow['It_repr']     if Frow.get('It_repr')     else 'Boolean'
        
        srow = ['']*8
        srow[0] = Srow['P_Name']  if Srow.get('P_Name')   else ''
        srow[1] = '1' if len(ALR)>0 else ''
        srow[2] = Srow['Storage'] if Srow.get('Storage')  else '0'
        srow[3] = Srow['OPC_Vis'] if Srow.get('OPC_Vis')  else '1'
        srow[4] = Srow['OPC_Rd']  if Srow.get('OPC_Rd')   else '1'
        srow[5] = Srow['OPC_Wt']  if Srow.get('OPC_Wt')   else '0'
        srow[6] = Srow['SL']      if Srow.get('SL')       else ''
        srow[7] = Srow['SH']      if Srow.get('SH')       else ''
        
        trow = ['']*7
        trow[0] = Trow['ACKN_TYPE']    if Trow.get('ACKN_TYPE')    else self.ACKN_TYPE
        trow[1] = Trow['COL_GROUP']    if Trow.get('COL_GROUP')    else self.COL_GROUP
        trow[2] = Trow['PROCESS_LIST'] if Trow.get('PROCESS_LIST') else str(self.ProcArea)
        trow[3] = Trow['HH']           if Trow.get('HH')           else ''
        trow[4] = Trow['H']            if Trow.get('H')            else ''
        trow[5] = Trow['L']            if Trow.get('L')            else ''
        trow[6] = Trow['LL']           if Trow.get('LL')           else ''
        
        self.ItemtRows.append('"{}","{}","{}","{}","{}","{}","{}",\\\n'.format(frow[0], frow[1], frow[2], frow[3], frow[4], frow[5], frow[6] ) )              #NAME,  DESCRIPTION,  COMMENT_1,  COMMENT_2,  ENG_UNIT,  VALUE_FORMAT,  ITEM_REP  
        self.ItemtRows.append('"{}","{}","{}","{}","{}","{}","{}","{}",\\\n'.format(srow[0], srow[1], srow[2], srow[3], srow[4], srow[5], srow[6], srow[7]) ) #POINT_NAME,  ALARMING,  STORAGE,  OPC_VISIBLE,  OPC_READ,  OPC_WRITE,  SCALE_LOW_LIMIT,  SCALE_HIGH_LIMIT  
        self.ItemtRows.append('"{}","{}","{}","{}","{}","{}","{}",\\\n'.format(trow[0], trow[1], trow[2], trow[3], trow[4], trow[5], trow[6]) )               #ACKN_TYPE,   COL_GROUP,  PROCESS_LIST,  HIGH_HIGH_LIMIT,  HIGH_LIMIT,  LOW_LIMIT,  LOW_LOW_LIMIT
        
        self.ItemtRows.append('"{}","{}","{}","{}","{}","{}",\\\n'.format(IT_ST[0], IT_ST[1], IT_ST[2], IT_ST[3], IT_ST[4], IT_ST[5]))       #ITEM_STAT_1,  ITEM_STAT_2,  ITEM_STAT_3,  ITEM_STAT_4,  ITEM_STAT_5,  ITEM_STAT_6  
        self.ItemtRows.append('"{}","{}","{}","{}","{}","{}",\\\n'.format(AL_ST[0], AL_ST[1], AL_ST[2], AL_ST[3], AL_ST[4], AL_ST[5]))       #ALARM_STATE_1,  ALARM_STATE_2,  ALARM_STATE_3,  ALARM_STATE_4,  ALARM_STATE_5,  ALARM_STATE_6        
        self.ItemtRows.append('"{}","{}","{}","{}","{}","{}",\\\n'.format(PRIOR[0], PRIOR[1], PRIOR[2], PRIOR[3], PRIOR[4], PRIOR[5]))       #PRIORITY_1,  PRIORITY_2,  PRIORITY_3,  PRIORITY_4,  PRIORITY_5,  PRIORITY_6 
        self.ItemtRows.append('"{}","{}","{}","{}","{}","{}",\\\n'.format(AL_TXT[0], AL_TXT[1], AL_TXT[2], AL_TXT[3], AL_TXT[4], AL_TXT[5])) #ALARM_TEXT_1,  ALARM_TEXT_2,  ALARM_TEXT_3,  ALARM_TEXT_4,  ALARM_TEXT_5,  ALARM_TEXT_6  
        self.ItemtRows.append('"{}","{}","{}","{}","{}","{}",\\\n'.format(AL_CLR[0], AL_CLR[1], AL_CLR[2], AL_CLR[3], AL_CLR[4], AL_CLR[5])) #ALARM_COLOR_1,  ALARM_COLOR_2,  ALARM_COLOR_3,  ALARM_COLOR_4,  ALARM_COLOR_5,  ALARM_COLOR_6  
        self.ItemtRows.append('"{}","{}","{}","{}","{}","{}",\\\n'.format(MNEM[0], MNEM[1], MNEM[2], MNEM[3], MNEM[4], MNEM[5]))             #MNEMONIC_1,  MNEMONIC_2,  MNEMONIC_3,  MNEMONIC_4,  MNEMONIC_5,  MNEMONIC_6  
        self.ItemtRows.append('"{}","{}","{}","{}","{}","{}",\\\n'.format(SH_EN[0], SH_EN[1], SH_EN[2], SH_EN[3], SH_EN[4], SH_EN[5]))       #SHELVE_ENABLED_1,  SHELVE_ENABLED_2,  SHELVE_ENABLED_3,  SHELVE_ENABLED_4,  SHELVE_ENABLED_5,  SHELVE_ENABLED_6  
        
        self.ItemtRows.append('"{}","{}","{}","{}","{}","{}",\\\n'.format(aoi[0], aoi[1], aoi[2], aoi[3], aoi[4], aoi[5]))   #AOI_1,  AOI_2,  AOI_3,  AOI_4,   AOI_5,   AOI_6  
        self.ItemtRows.append('"{}","{}","{}","{}","{}","{}",\\\n'.format(aoi[6], aoi[7], aoi[8], aoi[9], aoi[10], aoi[11])) #AOI_7,  AOI_8,  AOI_9,  AOI_10,  AOI_11,  AOI_12
        self.ItemtRows.append('"{}","{}","{}","{}"\n'.format(aoi[12], aoi[13], aoi[14], aoi[15]))                            #AOI_13, AOI_14, AOI_15, AOI_16
        self.ItemtRows.append('\n')
        
    def PaIforVirtualSignal(self, signal, section, AOIs):
        Frow = {}
        Srow = {}
        Trow = {}
        
        for aoi in AOIs:
            if aoi not in self.AOIs:
                self.AOIs.append(aoi)
        
        if section not in self.Sections:
            self.Sections.append(section) 
        
        signal.Point = signal.Name.upper() + '_POINT'          
        self.Points[signal.Point] = signal
            
        Description = ''
        if type(signal.Description) == unicode:
            Description = signal.Description[:40].encode('utf-8')
        elif type(signal.Description) == str:
            Description = signal.Description[:40]
            
        if signal.__dict__.get('Representation'):
            conv = signal.Representation[0]
            repr = signal.Representation[1]
        else:
            conv = 'Normal'
            repr = 'Boolean' if signal.Type == 'Bool' else 'Integer' if signal.Type == 'Int' else signal.Type
        
        Point = str(self.Controller.Name).upper() + ':' + str(signal.Point)
        self.MakePoint(Point, Description, signal.Name, signal.Editable, conv)            
        
        signal.Item = section + '.' + str(signal.Name)    
        self.Items[signal.Item] = signal        
        Frow['Name']        = signal.Item
        Frow['Description'] = Description           
        Frow['It_repr']     = repr
        
        Srow['P_Name']  = Point
        Srow['Storage'] = signal.Storage if signal.__dict__.get('Storage') else '0'      
        
        Trow['PROCESS_LIST'] = (str(self.ProcArea) + ' ' + signal.ProcArea) if signal.__dict__.get('ProcArea') else str(self.ProcArea) 
        self.MakeItem(Frow, Srow, Trow, signal.Alarming, AOIs)
        
    def PaIforSignal(self, signal, section, aois = [], makeVS = False):
        Frow = {}
        Srow = {}
        Trow = {}
        if type(signal.BlockType['Type']) == unicode:
            BlockType = signal.BlockType['Type'].encode('utf-8')
        elif type(signal.BlockType['Type']) == str:
            BlockType = signal.BlockType['Type']            
        else:
            print 'Не указан тип сигнала ', signal.TagChannel
        
        AOIs = aois[:]
        AOIs.append(BlockType)
            
        signal.Point = signal.TagChannel.upper() + '_POINT'         
        self.Points[signal.Point] = signal
        
        if type(signal.Description_rus) == unicode:
            Comment_1 = signal.Description_rus[:20].encode('utf-8')
            Comment_2 = signal.Description_rus[20:40].encode('utf-8')
            Description = signal.Description_rus[:40].encode('utf-8')
        elif type(signal.Description_rus) == str:
            Description = signal.Description_rus[:40]
        else:
            Description = ''
            Comment_1 = ''     
            Comment_2 = ''
        
        if type(signal.Descriptor) == unicode:
            Descriptor = signal.Descriptor[:41].encode('utf-8')
        elif type(signal.Descriptor) == str:
            Descriptor = signal.Descriptor[:41]                 
        else:
            Descriptor = None
        
        if Descriptor and '|' in Descriptor:
            Comment_1, Comment_2 = Descriptor.split('|')
            Comment_1 = Comment_1.strip()
            Comment_2 = Comment_2.strip()
            Description = Comment_1 + ' ' + Comment_2                        
        
        if signal.SH and signal.SL:
            if max(abs(float(signal.SH )), abs(float(signal.SL)))>0:
                Value_Format = '9.999'
            if max(abs(float(signal.SH )), abs(float(signal.SL)))>10:
                Value_Format = '99.99'   
            if max(abs(float(signal.SH )), abs(float(signal.SL)))>100:
                Value_Format = '999.9'  
            if max(abs(float(signal.SH )), abs(float(signal.SL)))>1000:
                Value_Format = '9999'   
        else:
            Value_Format = ''   
        
        if signal.Unit and type(signal.Unit['unit']) == unicode:
            Eng_Un = signal.Unit['unit'][:3].encode('utf-8')
        elif signal.Unit and type(signal.Unit['unit']) == str:
            Eng_Un = signal.Unit['unit'][:3] 
        else:
            Eng_Un = '' 
            
        if signal.Obj1 and signal.Obj1.get('AOI'):
            if type(signal.Obj1['AOI']) == unicode:
                AOIs.append(signal.Obj1['AOI'].encode('utf-8'))
            elif type(signal.Obj1['AOI']) == str:
                AOIs.append(signal.Obj1['AOI'])
                
        if signal.Obj2 and signal.Obj2.get('AOI'):
            if type(signal.Obj2['AOI']) == unicode:
                AOIs.append(signal.Obj2['AOI'].encode('utf-8'))
            elif type(signal.Obj2['AOI']) == str:
                AOIs.append(signal.Obj2['AOI'])
                
        if signal.Obj3 and signal.Obj3.get('AOI'):
            if type(signal.Obj3['AOI']) == unicode:
                AOIs.append(signal.Obj3['AOI'].encode('utf-8'))
            elif type(signal.Obj3['AOI']) == str:
                AOIs.append(signal.Obj3['AOI'])
                
        for aoi in AOIs:
            if aoi not in self.AOIs:
                self.AOIs.append(aoi)
        
        if section not in self.Sections:
            self.Sections.append(section)            
        
        Point = str(self.Controller.Name).upper() + ':' + str(signal.Point)
        self.MakePoint(Point, Description, signal.TagChannel)            
        
        signal.Item = section + '.' + str(signal.TagChannel)  
        self.Items[signal.Item] = signal
        Frow['Name']        = signal.Item
        Frow['Description'] = Description  
        Frow['Com_1']       = Comment_1
        Frow['Com_2']       = Comment_2
        Frow['EU']          = Eng_Un
        Frow['V_format']    = Value_Format  
        Frow['It_repr']     = 'Boolean' if BlockType[:1] == 'D' or signal.Ccontrol else 'Real'
        
        Srow['P_Name']  = Point  
        Srow['SL']      = signal.SL if signal.SL else ''
        Srow['SH']      = signal.SH if signal.SH else ''           
        self.MakeItem(Frow, Srow, Trow, signal.Alarming, AOIs) 
        
        if makeVS:
            for v_signal in signal.VirtualSignals:
                if not v_signal.toHMI:
                    continue
                self.PaIforVirtualSignal(v_signal, section, AOIs)

    def MakePointsAndItems(self):
        AOIs = ['DIAGNOSTIC']
        section = str(self.Controller.Name).upper() + '.DIAGNOSTIC'
        for signal in self.Controller.VirtualSignals:  
            self.PaIforVirtualSignal(signal, section, AOIs)
            
            
        for signal in self.Controller.Signals:
            if not signal.TagChannel or signal.InGroup or not signal.toHMI:
                continue                
            if type(signal.BlockType['Type']) == unicode:
                BlockType = signal.BlockType['Type'].encode('utf-8')
            elif type(signal.BlockType['Type']) == str:
                BlockType = signal.BlockType['Type']            
            else:
                print 'Не указан тип сигнала ', signal.TagChannel
                continue 
            section = str(self.Controller.Name).upper() + '.' + BlockType + '.' + signal.TagChannel
            self.PaIforSignal(signal, section, [], True)
                 
        for Engine in self.Controller.Engines:
            #print Engine.Name
            AOIs = ['ENGINES']   
            section = str(self.Controller.Name).upper() + '.ENGINES.' + GiveMeLoopName(Engine.Name)
            for signal in Engine.Signals.values():                
                if not signal.toHMI:
                    continue                
                self.PaIforSignal(signal, section, AOIs, True)     
            else:
                if signal.Obj1 and signal.Obj1.get('AOI'):
                    if type(signal.Obj1['AOI']) == unicode:
                        AOIs.append(signal.Obj1['AOI'].encode('utf-8'))
                    elif type(signal.Obj1['AOI']) == str:
                        AOIs.append(signal.Obj1['AOI'])
                        
                if signal.Obj2 and signal.Obj2.get('AOI'):
                    if type(signal.Obj2['AOI']) == unicode:
                        AOIs.append(signal.Obj2['AOI'].encode('utf-8'))
                    elif type(signal.Obj2['AOI']) == str:
                        AOIs.append(signal.Obj2['AOI'])
                        
                if signal.Obj3 and signal.Obj3.get('AOI'):
                    if type(signal.Obj3['AOI']) == unicode:
                        AOIs.append(signal.Obj3['AOI'].encode('utf-8'))
                    elif type(signal.Obj3['AOI']) == str:
                        AOIs.append(signal.Obj3['AOI'])
            for signal in Engine.VirtualSignals:
                if not signal.toHMI:
                    continue
                self.PaIforVirtualSignal(signal, section, AOIs)
            
        for Valve in self.Controller.Valves:
            #print Valve.Name
            AOIs = ['VALVES']   
            section = str(self.Controller.Name).upper() + '.VALVES.' + GiveMeLoopName(Valve.Name)
            for signal in Valve.Signals.values():
                if not signal.toHMI:
                    continue                
                self.PaIforSignal(signal, section, AOIs, True)
            else:
                if signal.Obj1 and signal.Obj1.get('AOI'):
                    if type(signal.Obj1['AOI']) == unicode:
                        AOIs.append(signal.Obj1['AOI'].encode('utf-8'))
                    elif type(signal.Obj1['AOI']) == str:
                        AOIs.append(signal.Obj1['AOI'])
                        
                if signal.Obj2 and signal.Obj2.get('AOI'):
                    if type(signal.Obj2['AOI']) == unicode:
                        AOIs.append(signal.Obj2['AOI'].encode('utf-8'))
                    elif type(signal.Obj2['AOI']) == str:
                        AOIs.append(signal.Obj2['AOI'])
                        
                if signal.Obj3 and signal.Obj3.get('AOI'):
                    if type(signal.Obj3['AOI']) == unicode:
                        AOIs.append(signal.Obj3['AOI'].encode('utf-8'))
                    elif type(signal.Obj3['AOI']) == str:
                        AOIs.append(signal.Obj3['AOI'])
            for signal in Valve.VirtualSignals:
                if not signal.toHMI:
                    continue
                self.PaIforVirtualSignal(signal, section, AOIs)
                
        for PID in self.Controller.PIDs:            
            #print PID.Name
            AOIs = ['PIDs'] 
            section = str(self.Controller.Name).upper() + '.PIDs.' + GiveMeLoopName(PID.Name)
            for func, signal in PID.Signals.items():                
                if not signal.toHMI:
                    continue  
                self.PaIforSignal(signal, section, AOIs, True)
            else:
                if signal.Obj1 and signal.Obj1.get('AOI'):
                    if type(signal.Obj1['AOI']) == unicode:
                        AOIs.append(signal.Obj1['AOI'].encode('utf-8'))
                    elif type(signal.Obj1['AOI']) == str:
                        AOIs.append(signal.Obj1['AOI'])
                        
                if signal.Obj2 and signal.Obj2.get('AOI'):
                    if type(signal.Obj2['AOI']) == unicode:
                        AOIs.append(signal.Obj2['AOI'].encode('utf-8'))
                    elif type(signal.Obj2['AOI']) == str:
                        AOIs.append(signal.Obj2['AOI'])
                        
                if signal.Obj3 and signal.Obj3.get('AOI'):
                    if type(signal.Obj3['AOI']) == unicode:
                        AOIs.append(signal.Obj3['AOI'].encode('utf-8'))
                    elif type(signal.Obj3['AOI']) == str:
                        AOIs.append(signal.Obj3['AOI'])            
            for signal in PID.VirtualSignals:
                if not signal.toHMI:
                    continue
                self.PaIforVirtualSignal(signal, section, AOIs)

