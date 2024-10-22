#
# FRN Client Console - Dashboard © 13MAD86 / Martin
# powered by www.sdr-mkk.de
#

import urllib.parse as urlparse
from urllib.parse import parse_qs
import platform 
import configparser
import http.server
import socketserver
import socket
import cgi
import os
import subprocess
from os import path
import json
import psutil
from gpiozero import CPUTemperature
import re

config = configparser.RawConfigParser()
config.read(r'/home/pi/frnconsole.cfg')

PASS = str(config['Auth']['Password'])
PORT = 80
WEBPATH = "/home/pi/dashboard"

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        try:
            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))

            if ctype == 'multipart/form-data':
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                content_len = int(self.headers.get('Content-length'))
                pdict['CONTENT-LENGTH'] = content_len

                fields = cgi.parse_multipart(self.rfile, pdict)
                if fields.get('config_password')[0] == PASS:
                    config['Auth'] = { \
                        'Callsign': str(fields.get('Auth_Callsign')).replace('[\'', '').replace('\']', ''), \
                        'OperatorName': str(fields.get('Auth_OperatorName')).replace('[\'', '').replace('\']', ''), \
                        'EMailAddress': str(fields.get('Auth_EMailAddress')).replace('[\'', '').replace('\']', ''), \
                        'City': str(fields.get('Auth_City')).replace('[\'', '').replace('\']', ''), \
                        'CityPart': str(fields.get('Auth_CityPart')).replace('[\'', '').replace('\']', ''), \
#                        'Password': str(fields.get('Auth_Password')).replace('[\'', '').replace('\']', ''), \
                        'Password': str(config['Auth']['Password']), \
                        'Country': str(fields.get('Auth_Country')).replace('[\'', '').replace('\']', ''), \
                        'Description': str(fields.get('Auth_Description')).replace('[\'', '').replace('\']', ''), \
                        'BandChannel': str(fields.get('Auth_BandChannel')).replace('[\'', '').replace('\']', ''), \
                        'ClientType': str(fields.get('Auth_ClientType')).replace('[\'', '').replace('\']', ''), \
                        'CharsetName': str(fields.get('Auth_CharsetName')).replace('[\'', '').replace('\']', '') \
                        }
                    config['Audio'] = { \
                        'InDevice': str(fields.get('Audio_InDevice')).replace('[\'', '').replace('\']', ''), \
                        'InSampleRate': str(fields.get('Audio_InSampleRate')).replace('[\'', '').replace('\']', ''), \
                        'InQuality': str(fields.get('Audio_InQuality')).replace('[\'', '').replace('\']', ''), \
                        'InFactor': str(fields.get('Audio_InFactor')).replace('[\'', '').replace('\']', ''), \
                        'InPreCapturedTime': str(fields.get('Audio_InPreCapturedTime')).replace('[\'', '').replace('\']', ''), \
                        'InAgcEnabled': str(fields.get('Audio_InAgcEnabled')).replace('[\'', '').replace('\']', ''), \
                        'InAgcMaxGain': str(fields.get('Audio_InAgcMaxGain')).replace('[\'', '').replace('\']', ''), \
                        'InAgcLevel': str(fields.get('Audio_InAgcLevel')).replace('[\'', '').replace('\']', ''), \
                        'InHpfEnabled': str(fields.get('Audio_InHpfEnabled')).replace('[\'', '').replace('\']', ''), \
                        'InHpfOrder': str(fields.get('Audio_InHpfOrder')).replace('[\'', '').replace('\']', ''), \
                        'InDtmfEnabled': str(fields.get('Audio_InDtmfEnabled')).replace('[\'', '').replace('\']', ''), \
                        'OutDevice': str(fields.get('Audio_OutDevice')).replace('[\'', '').replace('\']', ''), \
                        'OutSampleRate': str(fields.get('Audio_OutSampleRate')).replace('[\'', '').replace('\']', ''), \
                        'OutQuality': str(fields.get('Audio_OutQuality')).replace('[\'', '').replace('\']', ''), \
                        'OutFactor': str(fields.get('Audio_OutFactor')).replace('[\'', '').replace('\']', ''), \
                        'OutAgcEnabled': str(fields.get('Audio_OutAgcEnabled')).replace('[\'', '').replace('\']', ''), \
                        'OutAgcLevel': str(fields.get('Audio_OutAgcLevel')).replace('[\'', '').replace('\']', ''), \
                        'OutAgcMaxGain': str(fields.get('Audio_OutAgcMaxGain')).replace('[\'', '').replace('\']', ''), \
                        'OutHpfEnabled': str(fields.get('Audio_OutHpfEnabled')).replace('[\'', '').replace('\']', ''), \
                        'OutHpfOrder': str(fields.get('Audio_OutHpfOrder')).replace('[\'', '').replace('\']', ''), \
                        'OutDelayConst': str(fields.get('Audio_OutDelayConst')).replace('[\'', '').replace('\']', ''), \
                        'ReInitAudioEngine': str(fields.get('Audio_ReInitAudioEngine')).replace('[\'', '').replace('\']', '') \
                        }
                    config['Radio'] = { \
                        'PttEnabled': str(fields.get('Radio_PttEnabled')).replace('[\'', '').replace('\']', ''), \
                        'CosEnabled': str(fields.get('Radio_CosEnabled')).replace('[\'', '').replace('\']', ''), \
                        'PTT': str(fields.get('Radio_PTT')).replace('[\'', '').replace('\']', ''), \
                        'COS': str(fields.get('Radio_COS')).replace('[\'', '').replace('\']', ''), \
                        'LIGHT': str(fields.get('Radio_LIGHT')).replace('[\'', '').replace('\']', ''), \
                        'STATIC': str(fields.get('Radio_STATIC')).replace('[\'', '').replace('\']', ''), \
                        'CONNECT': str(fields.get('Radio_CONNECT')).replace('[\'', '').replace('\']', ''), \
                        'CTCSSWakeTime': str(fields.get('Radio_CTCSSWakeTime')).replace('[\'', '').replace('\']', ''), \
                        'CarrierCatchTime': str(fields.get('Radio_CarrierCatchTime')).replace('[\'', '').replace('\']', ''), \
                        'CarrierLostTime': str(fields.get('Radio_CarrierLostTime')).replace('[\'', '').replace('\']', ''), \
                        'SquelchSettlingTime': str(fields.get('Radio_SquelchSettlingTime')).replace('[\'', '').replace('\']', ''), \
                        'DtmfTimeout': str(fields.get('Radio_DtmfTimeout')).replace('[\'', '').replace('\']', ''), \
                        'DtmfCommands': str(fields.get('Radio_DtmfCommands')).replace('[\'', '').replace('\']', ''), \
                        'IdNoSoundListFileName': str(fields.get('Radio_IdNoSoundListFileName')).replace('[\'', '').replace('\']', '') \
                        }
                    config['Manager'] = { \
                        'ManagerAddress': str(fields.get('Manager_ManagerAddress')).replace('[\'', '').replace('\']', ''), \
                        'ManagerPort': str(fields.get('Manager_ManagerAddress')).replace('[\'', '').replace('\']', ''), \
                        'DynamicPasswordMode': str(fields.get('Manager_ManagerAddress')).replace('[\'', '').replace('\']', '') \
                        }
                    config['Server'] = { \
                        'ServerReconnectCount': str(fields.get('Server_ServerReconnectCount')).replace('[\'', '').replace('\']', ''), \
                        'ServerReconnectInterval': str(fields.get('Server_ServerReconnectInterval')).replace('[\'', '').replace('\']', ''), \
                        'ServerAddress': str(fields.get('Server_ServerAddress')).replace('[\'', '').replace('\']', ''), \
                        'ServerPort': str(fields.get('Server_ServerPort')).replace('[\'', '').replace('\']', ''), \
                        'VisibleStatus': str(fields.get('Server_VisibleStatus')).replace('[\'', '').replace('\']', ''), \
                        'Network': str(fields.get('Server_Network')).replace('[\'', '').replace('\']', ''), \
                        'BackupServerMode': str(fields.get('Server_BackupServerMode')).replace('[\'', '').replace('\']', ''), \
                        'ForcedBackupServerAddress': str(fields.get('Server_ForcedBackupServerAddress')).replace('[\'', '').replace('\']', ''), \
                        'ForcedBackupServerPort': str(fields.get('Server_ForcedBackupServerPort')).replace('[\'', '').replace('\']', ''), \
                        'ForcedBackupServerNetwork': str(fields.get('Server_ForcedBackupServerNetwork')).replace('[\'', '').replace('\']', ''), \
                        'RxTxHookScript': str(fields.get('Server_RxTxHookScript')).replace('[\'', '').replace('\']', ''), \
                        'InvalidStaticPasswordScript': str(fields.get('Server_InvalidStaticPasswordScript')).replace('[\'', '').replace('\']', ''), \
                        'ProtoListFormat': str(fields.get('Server_ProtoListFormat')).replace('[\'', '').replace('\']', ''), \
                        'ProtoSpeakerInfo': str(fields.get('Server_ProtoSpeakerInfo')).replace('[\'', '').replace('\']', ''), \
                        'ProtoMessagesFromServer': str(fields.get('Server_ProtoMessagesFromServer')).replace('[\'', '').replace('\']', ''), \
                        'ProtoShortFrames': str(fields.get('Server_ProtoShortFrames')).replace('[\'', '').replace('\']', '') \
                        }
                    config['Internet'] = { \
                        'PreferIPv4': str(fields.get('Internet_PreferIPv4')).replace('[\'', '').replace('\']', '') \
                        }
                    config['Message'] = { \
                        'PrivateAutoResponse': str(fields.get('Message_PrivateAutoResponse')).replace('[\'', '').replace('\']', ''), \
                        'MessageHookScript': str(fields.get('Message_MessageHookScript')).replace('[\'', '').replace('\']', '') \
                        }
                    config['System'] = { \
                        'WriteDir': str(fields.get('System_WriteDir')).replace('[\'', '').replace('\']', ''), \
                        'CharsetName': str(fields.get('System_CharsetName')).replace('[\'', '').replace('\']', ''), \
                        'PidFile': str(fields.get('System_PidFile')).replace('[\'', '').replace('\']', ''), \
                        'LogFile': str(fields.get('System_LogFile')).replace('[\'', '').replace('\']', ''), \
                        'LogControlSound': str(fields.get('System_LogControlSound')).replace('[\'', '').replace('\']', ''), \
                        'LogExternalSound': str(fields.get('System_LogExternalSound')).replace('[\'', '').replace('\']', ''), \
                        'LogClientList': str(fields.get('System_LogClientList')).replace('[\'', '').replace('\']', ''), \
                        'LogCarrier': str(fields.get('System_LogCarrier')).replace('[\'', '').replace('\']', ''), \
                        'LogTiming': str(fields.get('System_LogTiming')).replace('[\'', '').replace('\']', ''), \
                        'LogBackupServerMode': str(fields.get('System_LogBackupServerMode')).replace('[\'', '').replace('\']', ''), \
                        'LogCheckServer': str(fields.get('System_LogCheckServer')).replace('[\'', '').replace('\']', ''), \
                        'LogDtmfTones': str(fields.get('System_LogDtmfTones')).replace('[\'', '').replace('\']', ''), \
                        'LogDtmfCommands': str(fields.get('System_LogDtmfCommands')).replace('[\'', '').replace('\']', ''), \
                        'LogClientListDelimiter': str(fields.get('System_LogClientListDelimiter')).replace('[\'', '').replace('\']', ''), \
                        'LogCache': str(fields.get('System_LogCache')).replace('[\'', '').replace('\']', ''), \
                        'LogPTT': str(fields.get('System_LogPTT')).replace('[\'', '').replace('\']', ''), \
                        'LogExec': str(fields.get('System_LogExec')).replace('[\'', '').replace('\']', ''), \
                        'LogRecorder': str(fields.get('System_LogRecorder')).replace('[\'', '').replace('\']', '') \
                        }
                    config['Sounds'] = { \
                        'SoundsDir': str(fields.get('Sounds_SoundsDir')).replace('[\'', '').replace('\']', ''), \
                        'SoundCourtesy': str(fields.get('Sounds_SoundCourtesy')).replace('[\'', '').replace('\']', ''), \
                        'EnableCourtesy': str(fields.get('Sounds_EnableCourtesy')).replace('[\'', '').replace('\']', ''), \
                        'SoundCourtesyEmptyNet': str(fields.get('Sounds_SoundCourtesyEmptyNet')).replace('[\'', '').replace('\']', ''), \
                        'EnableCourtesyEmptyNet': str(fields.get('Sounds_EnableCourtesyEmptyNet')).replace('[\'', '').replace('\']', ''), \
                        'SoundRoger': str(fields.get('Sounds_SoundRoger')).replace('[\'', '').replace('\']', ''), \
                        'EnableRoger': str(fields.get('Sounds_EnableRoger')).replace('[\'', '').replace('\']', ''), \
                        'SoundNoConnection': str(fields.get('Sounds_SoundNoConnection')).replace('[\'', '').replace('\']', ''), \
                        'EnableNoConnection': str(fields.get('Sounds_EnableNoConnection')).replace('[\'', '').replace('\']', ''), \
                        'SoundReject': str(fields.get('Sounds_SoundReject')).replace('[\'', '').replace('\']', ''), \
                        'EnableReject': str(fields.get('Sounds_EnableReject')).replace('[\'', '').replace('\']', ''), \
                        'SoundError': str(fields.get('Sounds_SoundError')).replace('[\'', '').replace('\']', ''), \
                        'EnableError': str(fields.get('Sounds_EnableError')).replace('[\'', '').replace('\']', ''), \
                        'SoundRadioBOT': str(fields.get('Sounds_SoundRadioBOT')).replace('[\'', '').replace('\']', ''), \
                        'EnableRadioBOT': str(fields.get('Sounds_EnableRadioBOT')).replace('[\'', '').replace('\']', ''), \
                        'EnableConnect': str(fields.get('Sounds_EnableConnect')).replace('[\'', '').replace('\']', ''), \
                        'SoundConnect': str(fields.get('Sounds_SoundConnect')).replace('[\'', '').replace('\']', ''), \
                        'ConnectSoundCfgEnabled': str(fields.get('Sounds_ConnectSoundCfgEnabled')).replace('[\'', '').replace('\']', ''), \
                        'ConnectSoundCfgFileName': str(fields.get('Sounds_ConnectSoundCfgFileName')).replace('[\'', '').replace('\']', ''), \
                        'ConnectSoundExtEnabled': str(fields.get('Sounds_ConnectSoundExtEnabled')).replace('[\'', '').replace('\']', ''), \
                        'ConnectSoundExtScript': str(fields.get('Sounds_ConnectSoundExtScript')).replace('[\'', '').replace('\']', ''), \
                        'ConnectSoundExtDir': str(fields.get('Sounds_ConnectSoundExtDir')).replace('[\'', '').replace('\']', ''), \
                        'EnableServerBOT': str(fields.get('Sounds_EnableServerBOT')).replace('[\'', '').replace('\']', ''), \
                        'SoundServerBOT': str(fields.get('Sounds_SoundServerBOT')).replace('[\'', '').replace('\']', ''), \
                        'EnableServerEOT': str(fields.get('Sounds_EnableServerEOT')).replace('[\'', '').replace('\']', ''), \
                        'SoundServerEOT': str(fields.get('Sounds_SoundServerEOT')).replace('[\'', '').replace('\']', ''), \
                        'EnableDisconnect': str(fields.get('Sounds_EnableDisconnect')).replace('[\'', '').replace('\']', ''), \
                        'SoundDisconnect': str(fields.get('Sounds_SoundDisconnect')).replace('[\'', '').replace('\']', ''), \
                        'RogerSoundCfgEnabled': str(fields.get('Sounds_RogerSoundCfgEnabled')).replace('[\'', '').replace('\']', ''), \
                        'RogerSoundCfgFileName': str(fields.get('Sounds_RogerSoundCfgFileName')).replace('[\'', '').replace('\']', '') \
                        }
                    config['Hours'] = { \
                        'Enabled': str(fields.get('Hours_Enabled')).replace('[\'', '').replace('\']', ''), \
                        'Dir': str(fields.get('Hours_Dir')).replace('[\'', '').replace('\']', ''), \
                        'Interval': str(fields.get('Hours_Interval')).replace('[\'', '').replace('\']', ''), \
                        'Correction': str(fields.get('Hours_Correction')).replace('[\'', '').replace('\']', ''), \
                        'ExtEnabled': str(fields.get('Hours_ExtEnabled')).replace('[\'', '').replace('\']', ''), \
                        'ExtScript': str(fields.get('Hours_ExtScript')).replace('[\'', '').replace('\']', ''), \
                        'ExtDir': str(fields.get('Hours_ExtDir')).replace('[\'', '').replace('\']', ''), \
                        'ExtTempDir': str(fields.get('Hours_ExtTempDir')).replace('[\'', '').replace('\']', ''), \
                        'TimeRange': str(fields.get('Hours_TimeRange')).replace('[\'', '').replace('\']', '') \
                        }
                    config['Informer'] = { \
                        'Enabled': str(fields.get('Informer_Enabled')).replace('[\'', '').replace('\']', ''), \
                        'Dir': str(fields.get('Informer_Dir')).replace('[\'', '').replace('\']', ''), \
                        'Interval': str(fields.get('Informer_Interval')).replace('[\'', '').replace('\']', ''), \
                        'Mode': str(fields.get('Informer_Mode')).replace('[\'', '').replace('\']', ''), \
                        'SilenceEnabled': str(fields.get('Informer_SilenceEnabled')).replace('[\'', '').replace('\']', ''), \
                        'SilenceInterval': str(fields.get('Informer_SilenceInterval')).replace('[\'', '').replace('\']', ''), \
                        'SilenceTime': str(fields.get('Informer_SilenceTime')).replace('[\'', '').replace('\']', ''), \
                        'ExtEnabled': str(fields.get('Informer_ExtEnabled')).replace('[\'', '').replace('\']', ''), \
                        'ExtScript': str(fields.get('Informer_ExtScript')).replace('[\'', '').replace('\']', ''), \
                        'ExtDir': str(fields.get('Informer_ExtDir')).replace('[\'', '').replace('\']', ''), \
                        'ExtTempDir': str(fields.get('Informer_ExtTempDir')).replace('[\'', '').replace('\']', '') \
                        }
                    config['Recorder'] = { \
                        'Enabled': str(fields.get('Recorder_Enabled')).replace('[\'', '').replace('\']', ''), \
                        'Dir': str(fields.get('Recorder_Dir')).replace('[\'', '').replace('\']', ''), \
                        'Direction': str(fields.get('Recorder_Recorder_Direction')).replace('[\'', '').replace('\']', ''), \
                        'FileNameFormat': str(fields.get('Recorder_FileNameFormat')).replace('[\'', '').replace('\']', ''), \
                        'SubdirMode': str(fields.get('Recorder_SubdirMode')).replace('[\'', '').replace('\']', ''), \
                        'Script': str(fields.get('Recorder_Script')).replace('[\'', '').replace('\']', '') \
                        }
                    config['Command'] = { \
                        'CommandEnabled': str(fields.get('Command_CommandEnabled')).replace('[\'', '').replace('\']', ''), \
                        'CommandPort': str(fields.get('Command_CommandPort')).replace('[\'', '').replace('\']', ''), \
                        'CommandIPVersion': str(fields.get('Command_CommandIPVersion')).replace('[\'', '').replace('\']', ''), \
                        'CommandPreferIPv4': str(fields.get('Command_CommandPreferIPv4')).replace('[\'', '').replace('\']', ''), \
                        'AmplitudeEnabled': str(fields.get('Command_AmplitudeEnabled')).replace('[\'', '').replace('\']', ''), \
                        'AmplitudePort': str(fields.get('Command_AmplitudePort')).replace('[\'', '').replace('\']', '') \
                        }

                    with open(r'/home/pi/frnconsole.cfg', 'w') as configfile:
                        config.write(configfile)

                    output = "<html>"
                    output += "<head>"
                    output += "<title>FRN Client Console</title>"
                    output += "<meta http-equiv='refresh' content='3; url=index.html'>"
                    output += "</head>"
                    output += "<body bgcolor='#000000' text='#16C60C'>"
                    output += "<b>FRN Client Console:</b><p style='color: #cccccc;'>Config saved successfully! You will redirect to home after a few seconds.</p>"
                    output += "</br></br>"
                    output += "</body>"
                    output += "</html>"
                    self.wfile.write(output.encode())
                    print(output)
                else:
                    output = "<html>"
                    output += "<head>"
                    output += "<title>FRN Client Console</title>"
                    output += "<meta http-equiv='refresh' content='3; url=index.html'>"
                    output += "</head>"
                    output += "<body bgcolor='#000000' text='#16C60C'>"
                    output += "<b>FRN Client Console:</b><p style='color: #cccccc;'>Wrong password! You will redirect to home after a few seconds.</p>"
                    output += "</body>"
                    output += "</html>"
                    self.wfile.write(output.encode())
                    print(output)
        except:
            raise

    def do_GET(self):
        pathSplit = self.path.split("?")
        pathSection = pathSplit[0].split("/")
        if self.path == '/':
            self.path = WEBPATH+'/index.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        elif path.exists(WEBPATH+pathSplit[0]) is True:
            self.path = WEBPATH+pathSplit[0]
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        elif pathSection[1] == "stats.json":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            log_out_rx = str(self.get_log_rx())
            log_out_rx = log_out_rx.replace('[\'', '')
            log_out_rx = log_out_rx.replace('\', \'', '')
            log_out_rx = log_out_rx.replace('\']', '')
            log_out_rx = log_out_rx.replace('RX; ', '')
            log_out_rx = log_out_rx.replace('[gCLNT 5.03.0]', '')
            log_out_rx = log_out_rx.replace('[gCLNT 4.09.0]', '')
            log_out_rx = log_out_rx[:-3]
            outputJson = { \
                "platform":platform.system(), \
                "ramfree":str(self.get_ramFree())+" MB", \
                "ramtotal":str(self.get_ramTotal())+" MB", \
                "cpuspeed":str(self.get_cpu_speed())+" MHz", \
                "cputemp":str(self.get_temperature())+" °C", \
                "cpuuse":str(self.get_cpu_use())+" %", \
                "load":str(self.get_load()), \
                "host":str(self.get_host()), \
                "ip":str(self.get_ipaddress()), \
                "uptime":str(self.get_uptime()), \
                "log_rx":log_out_rx, \
                "callsign":str(config['Auth']['Callsign']), \
                "hours":str(config['Hours']['Enabled']), \
                "informer":str(config['Informer']['Enabled']), \
                "recorder":str(config['Recorder']['Enabled']), \
                "command":str(config['Command']['CommandEnabled']), \
                "master":str(config['Server']['ServerAddress']), \
                "target":str(config['Auth']['BandChannel']), \
                "type":str(config['Auth']['ClientType']) \
                }
            return self.wfile.write(bytes(json.dumps(outputJson), "utf-8"))
        elif pathSection[1] == "configs.json":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            outputJson = { \
                "Auth_Callsign":str(config['Auth']['Callsign']), \
                "Auth_OperatorName":str(config['Auth']['OperatorName']), \
                "Auth_EMailAddress":str(config['Auth']['EMailAddress']), \
                "Auth_City":str(config['Auth']['City']), \
                "Auth_CityPart":str(config['Auth']['CityPart']), \
#                "Auth_Password":str(config['Auth']['Password']), \
                "Auth_Country":str(config['Auth']['Country']), \
                "Auth_Description":str(config['Auth']['Description']), \
                "Auth_BandChannel":str(config['Auth']['BandChannel']), \
                "Auth_ClientType":str(config['Auth']['ClientType']), \
                "Auth_CharsetName":str(config['Auth']['CharsetName']), \
                "Audio_InDevice":str(config['Audio']['InDevice']), \
                "Audio_InSampleRate":str(config['Audio']['InSampleRate']), \
                "Audio_InQuality":str(config['Audio']['InQuality']), \
                "Audio_InFactor":str(config['Audio']['InFactor']), \
                "Audio_InPreCapturedTime":str(config['Audio']['InPreCapturedTime']), \
                "Audio_InAgcEnabled":str(config['Audio']['InAgcEnabled']), \
                "Audio_InAgcLevel":str(config['Audio']['InAgcLevel']), \
                "Audio_InAgcMaxGain":str(config['Audio']['InAgcMaxGain']), \
                "Audio_InHpfEnabled":str(config['Audio']['InHpfEnabled']), \
                "Audio_InHpfOrder":str(config['Audio']['InHpfOrder']), \
                "Audio_InDtmfEnabled":str(config['Audio']['InDtmfEnabled']), \
                "Audio_OutDevice":str(config['Audio']['OutDevice']), \
                "Audio_OutSampleRate":str(config['Audio']['OutSampleRate']), \
                "Audio_OutQuality":str(config['Audio']['OutQuality']), \
                "Audio_OutFactor":str(config['Audio']['OutFactor']), \
                "Audio_OutAgcEnabled":str(config['Audio']['OutAgcEnabled']), \
                "Audio_OutAgcLevel":str(config['Audio']['OutAgcLevel']), \
                "Audio_OutAgcMaxGain":str(config['Audio']['OutAgcMaxGain']), \
                "Audio_OutHpfEnabled":str(config['Audio']['OutHpfEnabled']), \
                "Audio_OutHpfOrder":str(config['Audio']['OutHpfOrder']), \
                "Audio_OutDelayConst":str(config['Audio']['OutDelayConst']), \
                "Audio_ReInitAudioEngine":str(config['Audio']['ReInitAudioEngine']), \
                "Radio_PttEnabled":str(config['Radio']['PttEnabled']), \
                "Radio_CosEnabled":str(config['Radio']['CosEnabled']), \
                "Radio_PTT":str(config['Radio']['PTT']), \
                "Radio_COS":str(config['Radio']['COS']), \
                "Radio_LIGHT":str(config['Radio']['LIGHT']), \
                "Radio_STATIC":str(config['Radio']['STATIC']), \
                "Radio_CONNECT":str(config['Radio']['CONNECT']), \
                "Radio_CTCSSWakeTime":str(config['Radio']['CTCSSWakeTime']), \
                "Radio_CarrierCatchTime":str(config['Radio']['CarrierCatchTime']), \
                "Radio_CarrierLostTime":str(config['Radio']['CarrierLostTime']), \
                "Radio_SquelchSettlingTime":str(config['Radio']['SquelchSettlingTime']), \
                "Radio_DtmfTimeout":str(config['Radio']['DtmfTimeout']), \
                "Radio_DtmfCommands":str(config['Radio']['DtmfCommands']), \
                "Radio_IdNoSoundListFileName":str(config['Radio']['IdNoSoundListFileName']), \
                "Manager_ManagerAddress":str(config['Manager']['ManagerAddress']), \
                "Manager_ManagerPort":str(config['Manager']['ManagerPort']), \
                "Manager_DynamicPasswordMode":str(config['Manager']['DynamicPasswordMode']), \
                "Server_ServerReconnectCount":str(config['Server']['ServerReconnectCount']), \
                "Server_ServerReconnectInterval":str(config['Server']['ServerReconnectInterval']), \
                "Server_ServerAddress":str(config['Server']['ServerAddress']), \
                "Server_ServerPort":str(config['Server']['ServerPort']), \
                "Server_VisibleStatus":str(config['Server']['VisibleStatus']), \
                "Server_Network":str(config['Server']['Network']), \
                "Server_BackupServerMode":str(config['Server']['BackupServerMode']), \
                "Server_ForcedBackupServerAddress":str(config['Server']['ForcedBackupServerAddress']), \
                "Server_ForcedBackupServerPort":str(config['Server']['ForcedBackupServerPort']), \
                "Server_ForcedBackupServerNetwork":str(config['Server']['ForcedBackupServerNetwork']), \
                "Server_RxTxHookScript":str(config['Server']['RxTxHookScript']), \
                "Server_InvalidStaticPasswordScript":str(config['Server']['InvalidStaticPasswordScript']), \
                "Server_ProtoListFormat":str(config['Server']['ProtoListFormat']), \
                "Server_ProtoSpeakerInfo":str(config['Server']['ProtoSpeakerInfo']), \
                "Server_ProtoMessagesFromServer":str(config['Server']['ProtoMessagesFromServer']), \
                "Server_ProtoShortFrames":str(config['Server']['ProtoShortFrames']), \
                "System_WriteDir":str(config['System']['WriteDir']), \
                "Internet_PreferIPv4":str(config['Internet']['PreferIPv4']), \
                "Message_PrivateAutoResponse":str(config['Message']['PrivateAutoResponse']), \
                "Message_MessageHookScript":str(config['Message']['MessageHookScript']), \
                "System_CharsetName":str(config['System']['CharsetName']), \
                "System_PidFile":str(config['System']['PidFile']), \
                "System_LogFile":str(config['System']['LogFile']), \
                "System_LogControlSound":str(config['System']['LogControlSound']), \
                "System_LogExternalSound":str(config['System']['LogExternalSound']), \
                "System_LogClientList":str(config['System']['LogClientList']), \
                "System_LogCarrier":str(config['System']['LogCarrier']), \
                "System_LogTiming":str(config['System']['LogTiming']), \
                "System_LogBackupServerMode":str(config['System']['LogBackupServerMode']), \
                "System_LogCheckServer":str(config['System']['LogCheckServer']), \
                "System_LogDtmfTones":str(config['System']['LogDtmfTones']), \
                "System_LogDtmfCommands":str(config['System']['LogDtmfCommands']), \
                "System_LogClientListDelimiter":str(config['System']['LogClientListDelimiter']), \
                "System_LogCache":str(config['System']['LogCache']), \
                "System_LogPTT":str(config['System']['LogPTT']), \
                "System_LogExec":str(config['System']['LogExec']), \
                "System_LogRecorder":str(config['System']['LogRecorder']), \
                "Sounds_SoundsDir":str(config['Sounds']['SoundsDir']), \
                "Sounds_SoundCourtesy":str(config['Sounds']['SoundCourtesy']), \
                "Sounds_EnableCourtesy":str(config['Sounds']['EnableCourtesy']), \
                "Sounds_SoundCourtesyEmptyNet":str(config['Sounds']['SoundCourtesyEmptyNet']), \
                "Sounds_EnableCourtesyEmptyNet":str(config['Sounds']['EnableCourtesyEmptyNet']), \
                "Sounds_SoundRoger":str(config['Sounds']['SoundRoger']), \
                "Sounds_EnableRoger":str(config['Sounds']['EnableRoger']), \
                "Sounds_SoundNoConnection":str(config['Sounds']['SoundNoConnection']), \
                "Sounds_EnableNoConnection":str(config['Sounds']['EnableNoConnection']), \
                "Sounds_SoundReject":str(config['Sounds']['SoundReject']), \
                "Sounds_EnableReject":str(config['Sounds']['EnableReject']), \
                "Sounds_SoundError":str(config['Sounds']['SoundError']), \
                "Sounds_EnableError":str(config['Sounds']['EnableError']), \
                "Sounds_SoundRadioBOT":str(config['Sounds']['SoundRadioBOT']), \
                "Sounds_EnableRadioBOT":str(config['Sounds']['EnableRadioBOT']), \
                "Sounds_EnableConnect":str(config['Sounds']['EnableConnect']), \
                "Sounds_SoundConnect":str(config['Sounds']['SoundConnect']), \
                "Sounds_ConnectSoundCfgEnabled":str(config['Sounds']['ConnectSoundCfgEnabled']), \
                "Sounds_ConnectSoundCfgFileName":str(config['Sounds']['ConnectSoundCfgFileName']), \
                "Sounds_ConnectSoundExtEnabled":str(config['Sounds']['ConnectSoundExtEnabled']), \
                "Sounds_ConnectSoundExtScript":str(config['Sounds']['ConnectSoundExtScript']), \
                "Sounds_ConnectSoundExtDir":str(config['Sounds']['ConnectSoundExtDir']), \
                "Sounds_EnableServerBOT":str(config['Sounds']['EnableServerBOT']), \
                "Sounds_SoundServerBOT":str(config['Sounds']['SoundServerBOT']), \
                "Sounds_EnableServerEOT":str(config['Sounds']['EnableServerEOT']), \
                "Sounds_SoundServerEOT":str(config['Sounds']['SoundServerEOT']), \
                "Sounds_EnableDisconnect":str(config['Sounds']['EnableDisconnect']), \
                "Sounds_SoundDisconnect":str(config['Sounds']['SoundDisconnect']), \
                "Sounds_RogerSoundCfgEnabled":str(config['Sounds']['RogerSoundCfgEnabled']), \
                "Sounds_RogerSoundCfgFileName":str(config['Sounds']['RogerSoundCfgFileName']), \
                "Hours_Enabled":str(config['Hours']['Enabled']), \
                "Hours_Dir":str(config['Hours']['Dir']), \
                "Hours_Interval":str(config['Hours']['Interval']), \
                "Hours_Correction":str(config['Hours']['Correction']), \
                "Hours_ExtEnabled":str(config['Hours']['ExtEnabled']), \
                "Hours_ExtScript":str(config['Hours']['ExtScript']), \
                "Hours_ExtDir":str(config['Hours']['ExtDir']), \
                "Hours_ExtTempDir":str(config['Hours']['ExtTempDir']), \
                "Hours_TimeRange":str(config['Hours']['TimeRange']), \
                "Informer_Enabled":str(config['Informer']['Enabled']), \
                "Informer_Dir":str(config['Informer']['Dir']), \
                "Informer_Interval":str(config['Informer']['Interval']), \
                "Informer_Mode":str(config['Informer']['Mode']), \
                "Informer_SilenceEnabled":str(config['Informer']['SilenceEnabled']), \
                "Informer_SilenceInterval":str(config['Informer']['SilenceInterval']), \
                "Informer_SilenceTime":str(config['Informer']['SilenceTime']), \
                "Informer_ExtEnabled":str(config['Informer']['ExtEnabled']), \
                "Informer_ExtScript":str(config['Informer']['ExtScript']), \
                "Informer_ExtDir":str(config['Informer']['ExtDir']), \
                "Informer_ExtTempDir":str(config['Informer']['ExtTempDir']), \
                "Recorder_Enabled":str(config['Recorder']['Enabled']), \
                "Recorder_Dir":str(config['Recorder']['Dir']), \
                "Recorder_Direction":str(config['Recorder']['Direction']), \
                "Recorder_FileNameFormat":str(config['Recorder']['FileNameFormat']), \
                "Recorder_SubdirMode":str(config['Recorder']['SubdirMode']), \
                "Recorder_Script":str(config['Recorder']['Script']), \
                "Command_CommandEnabled":str(config['Command']['CommandEnabled']), \
                "Command_CommandPort":str(config['Command']['CommandPort']), \
                "Command_CommandIPVersion":str(config['Command']['CommandIPVersion']), \
                "Command_CommandPreferIPv4":str(config['Command']['CommandPreferIPv4']), \
                "Command_AmplitudeEnabled":str(config['Command']['AmplitudeEnabled']), \
                "Command_AmplitudePort":str(config['Command']['AmplitudePort']) \
            }
            return self.wfile.write(bytes(json.dumps(outputJson), "utf-8"))
        elif pathSection[1] == "run":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            if self.getPass(self.path) == PASS:
                if pathSection[2] == "reboot":
                    self.wfile.write(bytes('{"html":"Rebooting System!","cmd":null}', "utf-8"))
                    os.system("sudo reboot &")
                elif pathSection[2] == "poweroff":
                    self.wfile.write(bytes('{"html":"Shutdown System!","cmd":null}', "utf-8"))
                    os.system("sudo poweroff &")
                elif pathSection[2] == "service":
                    if pathSection[3] == "start" and pathSection[4] is not None:
                        self.wfile.write(bytes('{"html":"Starting the ' + pathSection[4] + ' service.","cmd":null}', "utf-8"))
                        os.system("sudo systemctl start " + pathSection[4])   
                    elif pathSection[3] == "stop" and pathSection[4] is not None:
                        self.wfile.write(bytes('{"html":"Stoping the ' + pathSection[4] + ' service.","cmd":null}', "utf-8"))
                        os.system("sudo systemctl stop " + pathSection[4])
                    elif pathSection[3] == "restart" and pathSection[4] is not None:
                        self.wfile.write(bytes('{"html":"Restarting the ' + pathSection[4] + ' service.","cmd":null}', "utf-8"))
                        os.system("sudo systemctl restart " + pathSection[4])
                    else:
                        self.wfile.write(bytes('{"html":"Unknown service command!","cmd":null}', "utf-8"))
                else:
                    self.wfile.write(bytes('{"html":"Wrong command!","cmd":null}', "utf-8"))
            else:
                self.wfile.write(bytes('{"html":"Wrong password!","cmd":null}', "utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            output = "<html>"
            output += "<head>"
            output += "<title>FRN Client Console</title>"
            output += "<meta http-equiv='refresh' content='3; url=index.html'>"
            output += "</head>"
            output += "<body bgcolor='#000000' text='#16C60C'>"
            output += "<b>FRN Client Console:</b><p style='color: #cccccc;'>Document requested is not found! You will redirect to home after a few seconds.</p>"
            output += "</body>"
            output += "</html>"
            self.wfile.write(output.encode())
        return
        
    def getPass(self,url):
        parsed = urlparse.urlparse("http://localhost"+url)
        return str(parse_qs(parsed.query)['pass']).replace("['","").replace("']","")

    def get_ramTotal(self):
        memory = psutil.virtual_memory()
        return round(memory.total/1024.0/1024.0,1)
        
    def get_ramFree(self):
        memory = psutil.virtual_memory()
        return round(memory.available/1024.0/1024.0,1)       
    
    def get_cpu_use(self):
        return psutil.cpu_percent()

    def get_temperature(self):
        cpu = CPUTemperature()
        return cpu.temperature

    def get_uptime(self):
        try:
            s = subprocess.check_output(["uptime","-p"])
            return s.decode().replace("\n","")
        except:
            return "n/a"

    def get_load(self):
        try:
            s = subprocess.check_output(["uptime"])
            load_split = s.decode().split("load average:")
            return load_split[1].replace("\n","")
        except:
            return "n/a"
    
    def get_ipaddress(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 1))
            return s.getsockname()[0]
        except:
            return "0.0.0.0"
    
    def get_host(self):
        try:
            s = subprocess.check_output(["hostname","-s"])
            return s.decode().replace("\n","")
        except:
            return ""

    def get_cpu_speed(self):
        try:
            f = os.popen('vcgencmd get_config arm_freq')
            cpu = f.read()
            if cpu != "":
                return cpu.split("=")[1].replace("\n","")
            else:
                return "n/a"
        except:
            return "n/a"

    def get_log_rx(self):
        log = []

        with open(r'/home/pi/frnclientconsole.log', 'r') as fp:
            lines = fp.readlines()
            for line in lines:
                if line.find('; ; ; ; ; -') != -1:
                    line = line
                elif line.find('RX is started:') != -1:
                    line = line[:-25]
                    line = line.replace(': ', '; ')
                    line = line.replace('RX is started', 'RX')
                    line += '| '
                    log.append(line)

        output = log[-10:]
        output.reverse()
        return output

handler_object = MyHttpRequestHandler
my_server = socketserver.TCPServer(("", PORT), handler_object)
my_server.serve_forever()
