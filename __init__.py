import eg
import requests
import json

eg.RegisterPlugin(
    name = "Wink Plugin",
    author = "Alexandre Fournier",
    version = "0.1.0",
    kind = "other",
    description = "This is a plugin to control Wink devices like the Wink app",
    createMacrosOnAdd = True,
    icon=("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")
)

class WinkUser():
	def __init__(self, username="", password=""):
		self.username = username
		self.password = password

class Device():
	def __init__(self, id="", alias="", type="", state=""):
		self.id = id
		self.alias = alias
		self.type = type
		self.state = state
		
	def toString(self):
		return self.id + " " + self.alias + " : " + self.type + " @ " + self.url
        
class LightBulbState():
    def __init__(self, powered=false, brightness=0):
		self.powered = powered
		self.brightness = brightness
        
class Authenticate(eg.ActionBase):
    name = "Authenticate"
    description = "This action will authenticate the user with the Wink API"
    def __call__(self):
	print("Authenticating...")
	self.url = "https://api.wink.com/oauth2/token"
	self.data = {
        "client_id": "512d1e06a9cc39d0e49b09b0809c9f73",
        "client_secret": "1b71a6cdbd2910bf191d0d981711f31b",
        "grant_type": "password",
        "username": self.plugin.username,
        "password": self.plugin.password
      }
	self.headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	
	self.r = requests.post(self.url, data=json.dumps(self.data), headers=self.headers, verify=False)
	self.plugin.token = json.loads(self.r.text)['data']['access_token']
		

class GetDeviceList(eg.ActionBase):
    name = "Get Device List"
    description = "This action will retrieve all devices associated with the users's account"
    def __call__(self):
        print "Retrieving device list..."
        
        try:
            #Options
            url = "https://api.wink.com/users/me/wink_devices"
            headers = {'Authorization': 'Bearer ' + self.plugin.token, 'Content-type': 'application/json', 'Accept': 'text/plain'}
            #Get device list
            r = requests.get(url, headers=headers, verify=False)'
            deviceList = json.loads(r.text)['data']
            
            self.plugin.devices = []
            self.plugin.deviceAlias = []
            for device in deviceList:
                if(hasattr(device, "light_bulb_id")):
                    state = device['desired_state']
                    device = Device(device['light_bulb_id'], device['name'], state, "Light Bulb")
                    self.plugin.devices.append(device)
                    self.plugin.deviceAlias.append(device.alias)
        except AttributeError:
            eg.PrintError("Something went wrong. Please make sure you called Authenticate!")

class GetLightBulbState(eg.ActionBase):
    name = "Get Light Bulb State"
    description ="Retrieves the state of the light bulb and its brightness"
        
    def __call__(self, deviceIndex):
        print("Retrieving light bulb state...")
        try:
            device = self.plugin.devices[deviceIndex]
            
            #Get current state
            url = "https://api.wink.com/light_bulbs/" + device.id
            headers = {'Authorization': 'Bearer ' + self.plugin.token, 'Content-type': 'application/json', 'Accept': 'text/plain'}
            r = requests.get(url, headers=headers, verify=False)
            response = json.loads(r.text)['result']['responseData']
            currentState = json.loads(response)["desired_state"]
            if(currentState['powered'] == False):
                state = "OFF"
            else:
                state = "ON : " + currentState['brightness']
            
            print "State is " + state
            
            #Dispatch Event
            self.plugin.TriggerEvent("WinkLightBulbStateEvent", LightBulbState(currentState['powered'] == false, currentState['brightness']))            
        except AttributeError as attrErr:
            eg.PrintError("Something went wrong. Please make sure you called Authenticate and Get Device List! Error ")
            eg.PrintError(attrErr)
        except KeyError as keyErr:
            eg.PrintError("Something went wrong. Error ")
            eg.PrintError(keyErr)
        
    def Configure(self, deviceIndex=0):
        try:
            panel = eg.ConfigPanel()
            device = self.plugin.devices[deviceIndex]
           
            self.label1 = wx.StaticText(panel,label = "Select Device" ,style = wx.ALIGN_LEFT) 
            panel.sizer.Add(self.label1, 0 , wx.ALIGN_LEFT)
            
            self.deviceCombo = wx.ComboBox(panel, -1, size=(150, -1), value=device.alias,choices=self.plugin.deviceAlias)
            panel.sizer.Add(self.deviceCombo, 0, wx.ALIGN_CENTER_VERTICAL)
            
            while panel.Affirmed():
                deviceIndex = self.deviceCombo.GetCurrentSelection()
                panel.SetResult(deviceIndex)
        except AttributeError:
            eg.PrintError("Something went wrong. Please make sure you called Authenticate and Get Device List!")
            
class SetLightBulbState(eg.ActionBase):
    name = "Set Device State"
    description ="Change device state and brightness"
    
    def __call__(self, deviceIndex, state):
        print("Changing device state...")
        try:
            device = self.plugin.devices[deviceIndex]
            newState = str(state)
            #Options
            url = "https://api.wink.com/light_bulbs/" + device.id
            headers = {'Authorization': 'Bearer ' + self.plugin.token, 'Content-type': 'application/json', 'Accept': 'text/plain'}
            #Get device list
            r = requests.put(url, data=json.dumps(state), headers=headers, verify=False)
        except AttributeError:
            eg.PrintError("Something went wrong. Please make sure you called Authenticate and Get Device List!")
        
    def Configure(self, deviceIndex = 0, state = LightBulbState(False, 0)):
        try:
            panel = eg.ConfigPanel()
            device = self.plugin.devices[deviceIndex]
           
            self.label1 = wx.StaticText(panel,label = "Select Device" ,style = wx.ALIGN_LEFT) 
            panel.sizer.Add(self.label1, 0 , wx.ALIGN_LEFT)
            
            self.deviceCombo = wx.ComboBox(panel, -1, size=(150, -1), value=device.alias,choices=self.plugin.deviceAlias)
            panel.sizer.Add(self.deviceCombo, 0, wx.ALIGN_CENTER_VERTICAL)
            
            self.label1 = wx.StaticText(panel,label = "Select State" ,style = wx.ALIGN_LEFT) 
            panel.sizer.Add(self.label1, 0, wx.ALIGN_LEFT, 20)
            
            self.states = ["OFF", "ON"]        
            self.stateCombo = wx.ComboBox(panel, -1, size=(150, -1), value=self.states[state], choices=self.states)
            panel.sizer.Add(self.stateCombo, 0, wx.ALIGN_LEFT)
            
            self.label1 = wx.StaticText(panel,label = "Select Brightness" ,style = wx.ALIGN_LEFT) 
            panel.sizer.Add(self.label1, 0, wx.ALIGN_LEFT, 20)
            
            self.brightnessSlider = wx.Slider(panel, -1, size=(150, -1), value=state.brightness, minValue=0, maxValue=100)
            panel.sizer.Add(self.stateCombo, 0, wx.ALIGN_LEFT)
            
            while panel.Affirmed():
                powered = True
                if(self.stateCombo.GetCurrentSelection() == 0):
                    powered = False
                    
                brightness = brightnessSlider.getValue()
                state = LightBulbState(powered, brightness)
                deviceIndex = self.deviceCombo.GetCurrentSelection()
                panel.SetResult(deviceIndex, state)
        except AttributeError:
            eg.PrintError("Something went wrong. Please make sure you called Authenticate and Get Device List!")

class ToggleLightBulbDeviceState(eg.ActionBase):
    name = "Toggle Light Bulb State"
    description ="Toggles the device state"
    
    def __call__(self, deviceIndex):
        print("Changing device state...")
        try:
            device = self.plugin.devices[deviceIndex]
            
            #Get current state
            url = "https://api.wink.com/light_bulbs/" + device.id
            headers = {'Authorization': 'Bearer ' + self.plugin.token, 'Content-type': 'application/json', 'Accept': 'text/plain'}
            r = requests.get(url, headers=headers, verify=False)
            response = json.loads(r.text)['result']['responseData']
            currentState = json.loads(response)["desired_state"]
            
            if(currentState['powered'] == False):
                newState = LightBulbState(True, currentState['brightness'])
                print "Will turn " + device.alias + " off"
            else:
                newState = LightBulbState(False, currentState['brightness'])
                print "Will turn " + device.alias + " on"
            
            url = "https://api.wink.com/light_bulbs/" + device.id
            headers = {'Authorization': 'Bearer ' + self.plugin.token, 'Content-type': 'application/json', 'Accept': 'text/plain'}
            r = requests.put(url, data=json.dumps(newState), headers=headers, verify=False)
        except AttributeError:
            eg.PrintError("Something went wrong. Please make sure you called Authenticate and Get Device List!")
        
    def Configure(self, deviceIndex = 0):
        try:
            panel = eg.ConfigPanel()
            device = self.plugin.devices[deviceIndex]
           
            self.label1 = wx.StaticText(panel,label = "Select Device" ,style = wx.ALIGN_LEFT) 
            panel.sizer.Add(self.label1, 0 , wx.ALIGN_LEFT)
            
            self.deviceCombo = wx.ComboBox(panel, -1, size=(150, -1), value=device.alias,choices=self.plugin.deviceAlias)
            panel.sizer.Add(self.deviceCombo, 0, wx.ALIGN_CENTER_VERTICAL)
            
            while panel.Affirmed():
                deviceIndex = self.deviceCombo.GetCurrentSelection()
                panel.SetResult(deviceIndex)
        except AttributeError:
            eg.PrintError("Something went wrong. Please make sure you called Authenticate and Get Device List!")
        
def getDeviceFromAliasIndex(self, index):   
    return self.plugin.devices[index]
		
class WinkPlugin(eg.PluginBase):
	def __init__(self): 
	  print "Wink Plugin is inited."
	  self.AddAction(Authenticate)
	  self.AddAction(GetDeviceList)
	  self.AddAction(GetLightBulbState)
	  self.AddAction(SetLightBulbState)
	  self.AddAction(ToggleDeviceState)

	def __start__(self, winkUser):
			print "Wink Plugin is started with user: " + winkUser.username + " boiiiiiiiiiii"
			self.username = winkUser.username
			self.password = winkUser.password

	def __stop__(self):
			print "Wink Plugin is stopped."

	def __close__(self):
			print "Wink Plugin is closed."

	def Configure(self, winkUser=WinkUser("", "")):
            panel = eg.ConfigPanel()
        
            label = wx.StaticText(panel, label="Email", style=wx.ALIGN_LEFT)
            panel.sizer.Add(label, 0, wx.ALIGN_LEFT)
        
            userText = wx.TextCtrl(panel, -1, winkUser.username)
            panel.sizer.Add(userText, 0, wx.ALIGN_LEFT)
            
            label = wx.StaticText(panel, label="Password", style=wx.ALIGN_LEFT)
            panel.sizer.Add(label, 0, wx.ALIGN_LEFT)
		
            pwdText = wx.TextCtrl(panel, -1, winkUser.password, style=wx.ALIGN_LEFT|wx.TE_PASSWORD)
            panel.sizer.Add(pwdText, 0, wx.ALIGN_LEFT)
		
            while panel.Affirmed():
                panel.SetResult(WinkUser(userText.GetValue(), pwdText.GetValue()))