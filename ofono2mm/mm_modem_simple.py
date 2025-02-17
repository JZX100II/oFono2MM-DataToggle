from dbus_next.service import (ServiceInterface, method, dbus_property, signal)
from dbus_next.constants import PropertyAccess
from dbus_next import Variant

import os

class MMModemSimpleInterface(ServiceInterface):
    def __init__(self, mm_modem, ofono_interfaces, ofono_interface_props):
        super().__init__('org.freedesktop.ModemManager1.Modem.Simple')
        self.mm_modem = mm_modem
        self.ofono_interfaces = ofono_interfaces
        self.ofono_interface_props = ofono_interface_props
        self.props = {
             'state': Variant('u', 7), # on runtime enabled MM_MODEM_STATE_ENABLED
             'signal-quality': Variant('(ub)', [0, True]),
             'current-bands': Variant('au', []),
             'access-technologies': Variant('u', 0), # on runtime unknown MM_MODEM_ACCESS_TECHNOLOGY_UNKNOWN
             'm3gpp-registration-state': Variant('u', 0), # on runtime idle MM_MODEM_3GPP_REGISTRATION_STATE_IDLE
             'm3gpp-operator-code': Variant('s', ''),
             'm3gpp-operator-name': Variant('s', ''),
             'cdma-cdma1x-registration-state': Variant('u', 0),
             'cdma-evdo-registration-state': Variant('u', 0),
             'cdma-sid': Variant('u', 0),
             'cdma-nid': Variant('u', 0)
        }

    async def set_props(self):
        old_props = self.props.copy()
        if 'org.ofono.NetworkRegistration' in self.ofono_interface_props:
            self.props['m3gpp-operator-name'] = Variant('s', self.ofono_interface_props['org.ofono.NetworkRegistration']['Name'].value if "Name" in self.ofono_interface_props['org.ofono.NetworkRegistration'] else '')

            if 'MobileCountryCode' in self.ofono_interface_props['org.ofono.NetworkRegistration']:
                MCC = self.ofono_interface_props['org.ofono.NetworkRegistration']['MobileCountryCode'].value
            else:
                MCC = ''

            if 'MobileNetworkCode' in self.ofono_interface_props['org.ofono.NetworkRegistration']:
                MNC = self.ofono_interface_props['org.ofono.NetworkRegistration']['MobileNetworkCode'].value
            else:
                MNC = ''

            self.props['m3gpp-operator-code'] = Variant('s', f'{MCC}-{MNC}')

            if 'Strength' in self.ofono_interface_props['org.ofono.NetworkRegistration']:
                self.props['signal-quality'] = Variant('(ub)', [self.ofono_interface_props['org.ofono.NetworkRegistration']['Strength'].value, True])

            if 'Status' in self.ofono_interface_props['org.ofono.NetworkRegistration']:
                if self.ofono_interface_props['org.ofono.NetworkRegistration']['Status'].value == 'registered' or self.ofono_interface_props['org.ofono.NetworkRegistration']['Status'].value == 'roaming':
                    self.props['state'] = Variant('u', 9) # registered MM_MODEM_STATE_REGISTERED
                elif self.ofono_interface_props['org.ofono.NetworkRegistration']['Status'].value == 'searching':
                    self.props['state'] = Variant('u', 8) # searching MM_MODEM_STATE_SEARCHING
                else:
                    self.props['state'] = Variant('u', 7) # enabled MM_MODEM_STATE_ENABLED

            if 'Status' in self.ofono_interface_props['org.ofono.NetworkRegistration']:
                if self.ofono_interface_props['org.ofono.NetworkRegistration']['Status'].value == "unregisered":
                    self.props['m3gpp-registration-state'] = Variant('u', 0) # idle MM_MODEM_3GPP_REGISTRATION_STATE_IDLE
                elif self.ofono_interface_props['org.ofono.NetworkRegistration']['Status'].value == "registered":
                    self.props['m3gpp-registration-state'] = Variant('u', 1) # home MM_MODEM_3GPP_REGISTRATION_STATE_HOME
                elif self.ofono_interface_props['org.ofono.NetworkRegistration']['Status'].value == "searching":
                    self.props['m3gpp-registration-state'] = Variant('u', 2) # searching MM_MODEM_3GPP_REGISTRATION_STATE_SEARCHING
                elif self.ofono_interface_props['org.ofono.NetworkRegistration']['Status'].value == "denied":
                    self.props['m3gpp-registration-state'] = Variant('u', 3) # denied MM_MODEM_3GPP_REGISTRATION_STATE_DENIED
                elif self.ofono_interface_props['org.ofono.NetworkRegistration']['Status'].value == "unknown":
                    self.props['m3gpp-registration-state'] = Variant('u', 4) # unknown MM_MODEM_3GPP_REGISTRATION_STATE_UNKNOWN
                elif self.ofono_interface_props['org.ofono.NetworkRegistration']['Status'].value == "roaming":
                    self.props['m3gpp-registration-state'] = Variant('u', 5) # MM_MODEM_3GPP_REGISTRATION_STATE_ROAMING
            else:
                self.props['m3gpp-registration-state'] = Variant('u', 4) # unknown MM_MODEM_3GPP_REGISTRATION_STATE_UNKNOWN
        else:
            self.props['m3gpp-operator-name'] = Variant('s', '')
            self.props['m3gpp-operator-code'] = Variant('s', '')
            self.props['signal-quality'] = Variant('(ub)', [0, True])
            self.props['state'] = Variant('u', 7) # enabled MM_MODEM_STATE_ENABLED

        if 'org.ofono.NetworkRegistration' in self.ofono_interface_props and self.props['state'].value == 7:
            if "Technology" in self.ofono_interface_props['org.ofono.NetworkRegistration']:
                current_tech = 0
                if self.ofono_interface_props['org.ofono.NetworkRegistration']["Technology"].value == "nr":
                    current_tech |= 1 << 15 # network is 5g MM_MODEM_ACCESS_TECHNOLOGY_5GNR
                elif self.ofono_interface_props['org.ofono.NetworkRegistration']["Technology"].value == "lte":
                    current_tech |= 1 << 14 # network is lte MM_MODEM_ACCESS_TECHNOLOGY_LTE
                elif self.ofono_interface_props['org.ofono.NetworkRegistration']["Technology"].value == "umts" or self.ofono_interface_props['org.ofono.NetworkRegistration']["Technology"].value == "hspa" or self.ofono_interface_props['org.ofono.NetworkRegistration']["Technology"].value == "hsdpa" or self.ofono_interface_props['org.ofono.NetworkRegistration']["Technology"].value == "hsupa":
                    current_tech |= 1 << 5 # network is umts MM_MODEM_ACCESS_TECHNOLOGY_UMTS
                elif self.ofono_interface_props['org.ofono.NetworkRegistration']["Technology"].value == "gsm" or self.ofono_interface_props['org.ofono.NetworkRegistration']["Technology"].value == "edge" or self.ofono_interface_props['org.ofono.NetworkRegistration']["Technology"].value == "gprs":
                    current_tech |= 1 << 1 # network is gsm MM_MODEM_ACCESS_TECHNOLOGY_GSM

                self.props['access-technologies'] = Variant('u', current_tech)
            else:
                self.props['access-technologies'] = Variant('u', 0) # network is unknown MM_MODEM_ACCESS_TECHNOLOGY_UNKNOWN
        else:
            self.props['access-technologies'] = Variant('u', 0) # network is unknown MM_MODEM_ACCESS_TECHNOLOGY_UNKNOWN

    @method()
    async def Connect(self, properties: 'a{sv}') -> 'o':
        try:
            await self.props()
        except Exception as e:
            pass

        for b in self.mm_modem.bearers:
            if self.mm_modem.bearers[b].props['Properties'].value['apn'] == properties['apn']:
                await self.mm_modem.bearers[b].add_auth_ofono(properties['username'].value if 'username' in properties else '',
                                                                properties['password'].value if 'password' in properties else '')
                self.mm_modem.bearers[b].props['Properties'] = Variant('a{sv}', properties)
                await self.mm_modem.bearers[b].doConnect()
                return b

        try:
            bearer = await self.mm_modem.doCreateBearer(properties)
            await self.mm_modem.bearers[bearer].doConnect()
        except Exception as e:
            bearer = f'/org/freedesktop/ModemManager/Bearer/0'

        #print('saving toggle mode: Connecting...')
        await self.saveToggleMode('True')

        return bearer
    
    async def saveToggleMode(self, mode):
        toggleModeDir = os.path.join('/var/lib/ofono2mm')
        toggleModePath = os.path.join(toggleModeDir, 'toggleMode')

        if not os.path.exists(toggleModeDir):
            os.makedirs(toggleModeDir)
        
        with open (toggleModePath, 'w') as toggleMode:
            toggleMode.write(mode)

    @method()
    async def Disconnect(self, path: 'o'):
        if path == '/':
            for b in self.mm_modem.bearers:
                try:
                    await self.mm_modem.bearers[b].doDisconnect()
                except Exception as e:
                    pass
        if path in self.mm_modem.bearers:
            try:
                await self.mm_modem.bearers[path].doDisconnect()
            except Exception as e:
                pass

        #print('saving toggle mode: Disconnecting...')
        await self.saveToggleMode('False')

    @method()
    async def GetStatus(self) -> 'a{sv}':
        await self.set_props()
        return self.props
