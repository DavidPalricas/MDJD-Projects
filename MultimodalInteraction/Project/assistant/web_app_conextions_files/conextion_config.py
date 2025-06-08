import websockets
from xml.dom.minidom import parseString
import ssl
import httpx

class LiteEvent():

    def __init__(self):
        self.handlers = []

    def on(self, handler):
        self.handlers.append(handler)
        return self
    
    def off(self, handler):
        self.handlers.remove(handler)
        return self
    
    def trigger(self, data):
        for h in self.handlers:
            h(data)

    def expose(self):
        return self
    
class EMMA():
    
    def __init__(self, Id, medium, mode, confidence, start, end = None):
        self.root = "<root></root>"
        self.namespaceEMMA = "http://www.w3.org/2003/04/emma"
        self.Id = Id
        self.medium = medium
        self.mode = mode
        self.start = start
        self.end = end
        self.confidence = confidence
        self._doc = parseString(self.root)

    #SET TextContent
    def setValue(self, value):
        self.Value = value
        return self
    
    #GET EMMA Element
    def getElem(self):
        emma = self._doc.createElementNS(self.namespaceEMMA, "emma:emma")
        emma.setAttributeNS(self.namespaceEMMA, "emma:version", "1.0")
        emma.setAttribute("xmlns:emma", self.namespaceEMMA)
        self._doc.documentElement.appendChild(emma)
        interp = self._doc.createElementNS(self.namespaceEMMA, "emma:interpretation")
        interp.setAttributeNS(self.namespaceEMMA, "emma:id", self.Id)
        interp.setAttributeNS(self.namespaceEMMA, "emma:medium", self.medium)
        interp.setAttributeNS(self.namespaceEMMA, "emma:mode", self.mode)
        interp.setAttributeNS(self.namespaceEMMA, "emma:start", str(self.start))
        if self.end is not None:
            interp.setAttributeNS(self.namespaceEMMA, "emma:end", str(self.end))
        interp.setAttributeNS(self.namespaceEMMA, "emma:confidence", str(self.confidence))
        emma.appendChild(interp)
        command = self._doc.createElement("command")
        command.appendChild(self._doc.createTextNode(self.Value))
        interp.appendChild(command)
        return self._doc.documentElement.firstChild

#
# LifeCycleEvent CLASS
#
# generates LifeCycleEvent XML Sintaxe
#
class LifeCycleEvent():

    def __init__(self, Source, Target, RequestID, ContextID):
        self.root = "<root></root>"
        self.namespaceMMI = "http://www.w3.org/2008/04/mmi-arch"
        self.Source = Source
        self.Target = Target
        self.RequestID = RequestID
        self.ContextID = ContextID
        self._doc = parseString(self.root)

    #CREATE BASE ELEM
    def doBaseMMI(self):
        mmi = self._doc.createElementNS(self.namespaceMMI, "mmi:mmi")
        mmi.setAttributeNS(self.namespaceMMI, "mmi:version", "1.0")
        mmi.setAttribute("xmlns:mmi", self.namespaceMMI)
        self._doc.documentElement.appendChild(mmi)
        return mmi

    #FILL PARAMS IN LifeCycleEvent
    def setBaseParm(self, el):
        el.setAttributeNS(self.namespaceMMI, "mmi:source", self.Source)
        el.setAttributeNS(self.namespaceMMI, "mmi:target", self.Target)
        el.setAttributeNS(self.namespaceMMI, "mmi:requestId", self.RequestID)
        if self.ContextID is not None:
            el.setAttributeNS(self.namespaceMMI, "mmi:context", self.ContextID)

    #GENERATE XML for NEWCONTEXTREQUEST
    def doNewContextRequest(self):
        mmi = self.doBaseMMI()
        newContextRequest = self._doc.createElementNS(self.namespaceMMI, "mmi:newContextRequest")
        mmi.appendChild(newContextRequest)
        self.setBaseParm(newContextRequest)
        return self
    
    #GENERATE XML for STARTREQUEST
    def doStartRequest(self, emma: EMMA):
        mmi = self.doBaseMMI()
        startRequest = self._doc.createElementNS(self.namespaceMMI, "mmi:startRequest")
        mmi.appendChild(startRequest)
        self.setBaseParm(startRequest)
        data = self._doc.createElementNS(self.namespaceMMI, "mmi:data")
        startRequest.appendChild(data)
        data.appendChild(emma.getElem())
        return self
    
    def doExtensionNotification(self, emma):
        mmi = self.doBaseMMI()
        ExtensionNotification = self._doc.createElementNS(self.namespaceMMI, "mmi:ExtensionNotification")
        mmi.appendChild(ExtensionNotification)
        self.setBaseParm(ExtensionNotification)
        data = self._doc.createElementNS(self.namespaceMMI, "mmi:data")
        ExtensionNotification.appendChild(data)
        data.appendChild(emma.getElem())
        return self
    
    def __str__(self) -> str:
        return self._doc.documentElement.toxml()
    
    def consolePrint(self):
        print(self.__str__())

class MMIClientSocket():

    def __init__(self, address):
        self.onOpen = LiteEvent()
        self.onMessage = LiteEvent()
        self.address = address
        self.socket = None

    @property
    def OnOpen(self):
        return self.onOpen.expose()
    
    @property
    def OnMessage(self):
        return self.onMessage.expose()
    
    async def sendToIM(self, lce: LifeCycleEvent):
        if self.socket is not None:
            await self.socket.send(str(lce))
            print("MESSAGE SENT TO " + self.address)

    async def openSocket(self):

        ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        self.socket = await websockets.connect(self.address, ssl=ssl_context) # ssl = ssl_context para ignorar certificado (menos seguro)
        async for message in self.socket:
            self.onMessage.trigger(message)
        self.onOpen.trigger(None)

    async def closeSocket(self):
        if self.socket is not None:
            await self.socket.close()


    def closeSocket(self):
        if self.socket != None:
            self.socket.close()


class MMIClient():

    def __init__(self, IMAdd, FusionAdd):
        self.onArrive = LiteEvent()
        self.onResponse = LiteEvent()
        self.IMAdd = IMAdd
        self.FusionAdd = FusionAdd

    @property
    def OnArrive(self):
        return self.onArrive.expose()
    
    @property
    def OnResponse(self):
        return self.onResult.expose()
    
    def sendToIM(self, lce: LifeCycleEvent):
        # print(str(lce))
        response = httpx.post(self.FusionAdd, data=str(lce), verify=False) # verify = False para ignorar certificado (menos seguro)
        if response.status_code == 200:
            #print('send response: ' + response.text)
            self.onResponse.trigger(response.text)
            print("POST SENT TO " + self.FusionAdd)

    def startPoolIM(self):
        response = httpx.get(self.IMAdd, verify=False) # verify = False para ignorar certificado (menos seguro)
        if response.status_code == 200 and response.text != "":
            self.onArrive.trigger(response.text)
            self.startPoolIM()
        print("GET SENT TO " + self.IMAdd)

