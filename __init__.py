import eg
import requests
import json
import pycurl
import StringIO
import urllib
try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

eg.RegisterPlugin(
    name = "Wink Plugin",
    author = "Alexandre Fournier",
    version = "0.2.0",
    kind = "other",
    description = "This is a plugin to control Wink devices like the Wink app",
    createMacrosOnAdd = True,
    icon=("iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABAElEQVQ4T53TwUoCURjF8Z9XCfItmqFNtugZooVRj2FUG8UXKQgiJF8jSJCeoYW0K2rvXhCSNndkGmdU/O/unXPO/ebe76slo6kCR+jgHAdx7wuvGOIjL67lAvZwh1uEYmpkgWf0MYNGzvyCswpjRsA1DmOF8+yk+zJzN93XTfdXYziN1WqgFVNXzL20uVw/fM6Kkhs8hXhh9XXmXtosq6SOTkB7nTmjIqQdkBSFVZR8S6qea1vmITbJrvyE2GG7Mq4lo+kx3osvsQW/OAmYYLBJXcIAk+wS+xhvMOR5i57l0Mxxgcc4MFUs4smX0fNvGjNauIoNlkThd6xwGH95yR9ZTDgHaQ8loAAAAABJRU5ErkJggg==")
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
    def __init__(self, powered=False, brightness=0):
		self.powered = powered
		self.brightness = brightness
    
    def toString(self):
        if(self.powered == True):
            b = str(self.brightness)
            return "ON:" + b
        return "OFF"
        
class Authenticate(eg.ActionBase):
    name = "Authenticate"
    description = "This action will authenticate the user with the Wink API"
    def __call__(self):
        print("Authenticating...")
        url = "https://api.wink.com/oauth2/token"
        data = {
            "client_id": "512d1e06a9cc39d0e49b09b0809c9f73",
            "client_secret": "1b71a6cdbd2910bf191d0d981711f31b",
            "grant_type": "password",
            "username": self.plugin.username,
            "password": self.plugin.password}
        buffer = BytesIO()
        b = StringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(pycurl.HTTPHEADER,['Content-Type: application/json'])
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(pycurl.WRITEFUNCTION, b.write)
        c.setopt(c.POSTFIELDS, json.dumps(data))
        c.perform()
        c.close()
        
        r = b.getvalue()
        print(json.loads(r)['data']['access_token'])
        self.plugin.token = "Bearer " + json.loads(r)['data']['access_token']
		

class GetDeviceList(eg.ActionBase):
    name = "Get Device List"
    description = "This action will retrieve all devices associated with the users's account"
    def __call__(self):
        print "Retrieving device list..."
        
        try:
            #Options
            url = "https://api.wink.com/users/me/wink_devices"
            
            #Get device list
            buffer = BytesIO()
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(pycurl.HTTPHEADER,['Authorization: ' + self.plugin.token, 'Content-Type: application/json'])
            c.setopt(c.WRITEFUNCTION, buffer.write)
            c.perform()
            c.close()
            
            r = buffer.getvalue()
            deviceList = json.loads(r)['data']
            
            self.plugin.devices = []
            self.plugin.deviceAlias = []
            count = str(len(deviceList))
            
            for device in deviceList:
                if "light_bulb_id" in device:
                    state = device['desired_state']
                    device = Device(device['light_bulb_id'], device['name'], state, "Light Bulb")
                    self.plugin.devices.append(device)
                    self.plugin.deviceAlias.append(device.alias)
            count = str(len(self.plugin.deviceAlias))
            print("Saved " + count + " devices")
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
            
            #Get device state
            buffer = BytesIO()
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(pycurl.HTTPHEADER,['Authorization: ' + self.plugin.token, 'Content-Type: application/json'])
            c.setopt(c.WRITEFUNCTION, buffer.write)
            c.perform()
            c.close()
            
            r = buffer.getvalue()
            response = json.loads(r)['data']
            currentState = response["desired_state"]
            print(currentState)
            if(currentState['powered'] == False):
                state = "OFF"
            else:
                state = "ON : " + currentState['brightness']
            
            print "State is " + state
            
            #Dispatch Event
            deviceState = LightBulbState(currentState['powered'] == True, currentState['brightness'])
            message = device.alias + " is " + deviceState.toString()
            self.plugin.TriggerEvent("WinkLightBulbStateEvent", message)            
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
            
            #Options
            url = "https://api.wink.com/light_bulbs/" + device.id
            
            data = {
                    "desired_state": {
                      "powered": state.powered,
                      "brightness": state.brightness
                    }
                  }
                  
            #Set state
            buffer = BytesIO()
            b = StringIO.StringIO()
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(pycurl.HTTPHEADER,['Authorization: ' + self.plugin.token, 'Content-Type: application/json'])
            c.setopt(pycurl.CUSTOMREQUEST, "PUT")
            c.setopt(pycurl.POST, 1)
            c.setopt(c.WRITEDATA, buffer)
            c.setopt(pycurl.WRITEFUNCTION, b.write)
            c.setopt(c.POSTFIELDS, json.dumps(data))
            c.perform()
            c.close()
            
            r = b.getvalue()
            print(r)
        except AttributeError:
            eg.PrintError("Something went wrong. Please make sure you called Authenticate and Get Device List!")
        
    def Configure(self, deviceIndex = 0, state = LightBulbState(False, 0)):
        try:
            panel = eg.ConfigPanel()
            device = self.plugin.devices[deviceIndex]
           
            self.labelDevice = wx.StaticText(panel,label = "Select Device" ,style = wx.ALIGN_LEFT) 
            panel.sizer.Add(self.labelDevice, 0 , wx.ALIGN_LEFT)
            
            self.deviceCombo = wx.ComboBox(panel, -1, size=(150, -1), value=device.alias,choices=self.plugin.deviceAlias)
            panel.sizer.Add(self.deviceCombo, 0, wx.ALIGN_CENTER_VERTICAL)
            
            self.labelState = wx.StaticText(panel,label = "Select State" ,style = wx.ALIGN_LEFT) 
            panel.sizer.Add(self.labelState, 0, wx.ALIGN_LEFT, 20)
            
            self.states = ["OFF", "ON"]        
            self.stateCombo = wx.ComboBox(panel, -1, size=(150, -1), value="ON", choices=self.states)
            panel.sizer.Add(self.stateCombo, 0, wx.ALIGN_LEFT)
            
            self.labelBrightness = wx.StaticText(panel,label = "Select Brightness" ,style = wx.ALIGN_LEFT) 
            panel.sizer.Add(self.labelBrightness, 0, wx.ALIGN_LEFT, 20)
            
            self.brightnessSlider = wx.Slider(panel, -1, size=(150, -1), value=state.brightness, minValue=0, maxValue=100, style = wx.SL_HORIZONTAL|wx.SL_LABELS)
            panel.sizer.Add(self.brightnessSlider, 0, wx.ALIGN_LEFT)
            
            while panel.Affirmed():
                powered = True
                if(self.stateCombo.GetCurrentSelection() == 0):
                    powered = False
                    
                brightness = self.brightnessSlider.GetValue()
                state = LightBulbState(powered, brightness)
                print(state.toString())
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
            
            #Get device state
            buffer = BytesIO()
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(pycurl.HTTPHEADER,['Authorization: ' + self.plugin.token, 'Content-Type: application/json'])
            c.setopt(c.WRITEFUNCTION, buffer.write)
            c.perform()
            c.close()
            
            r = buffer.getvalue()
            response = json.loads(r)['data']
            currentState = response["desired_state"]
            
            if(currentState['powered'] == False):
                newState = LightBulbState(True, currentState['brightness'])
                print "Will turn " + device.alias + " off"
            else:
                newState = LightBulbState(False, currentState['brightness'])
                print "Will turn " + device.alias + " on"
            
            #Options
            url = "https://api.wink.com/light_bulbs/" + device.id
            
            data = {
                    "desired_state": {
                      "powered": newState.powered,
                      "brightness": newState.brightness
                    }
                  }
            
            #Set state
            buffer = BytesIO()
            b = StringIO.StringIO()
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(pycurl.HTTPHEADER,['Authorization: ' + self.plugin.token, 'Content-Type: application/json'])
            c.setopt(pycurl.CUSTOMREQUEST, "PUT")
            c.setopt(pycurl.POST, 1)
            c.setopt(c.WRITEDATA, buffer)
            c.setopt(pycurl.WRITEFUNCTION, b.write)
            c.setopt(c.POSTFIELDS, json.dumps(data))
            c.perform()
            c.close()
            
            r = b.getvalue()
            print(r)
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
	  self.AddAction(ToggleLightBulbDeviceState)

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