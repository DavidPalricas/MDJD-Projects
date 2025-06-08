///
//  LifeCycleEvent CLASS
//
//  generates LifeCycleEvent XML Sintaxe
///
var LifeCycleEvent = (function () {
    function LifeCycleEvent(Source, Target, RequestID, ContextID) {
        this.root = "<root></root>";
        this.namespaceMMI = "http://www.w3.org/2008/04/mmi-arch";
        this.parser = new DOMParser();
        this.Source = Source;
        this.Target = Target;
        this.RequestID = RequestID;
        this.ContextID = ContextID;
        this._doc = this.parser.parseFromString(this.root, "text/xml");
    }
    ///CREATE BASE ELEM
    LifeCycleEvent.prototype.doBaseMMI = function () {
        var mmi = this._doc.createElementNS(this.namespaceMMI, "mmi:mmi");
        mmi.setAttributeNS(this.namespaceMMI, "mmi:version", "1.0");
        this._doc.documentElement.appendChild(mmi);
        return mmi;
    };
    ///FILL PARAMS IN LifeCycleEvent
    LifeCycleEvent.prototype.setBaseParm = function (el) {
        el.setAttributeNS(this.namespaceMMI, "mmi:source", this.Source);
        el.setAttributeNS(this.namespaceMMI, "mmi:target", this.Target);
        el.setAttributeNS(this.namespaceMMI, "mmi:requestId", this.RequestID);
        if (this.ContextID != null)
            el.setAttributeNS(this.namespaceMMI, "mmi:context", this.ContextID);
    };
    ///GENERATE XML for NEWCONTEXTREQUEST
    LifeCycleEvent.prototype.doNewContextRequest = function () {
        var mmi = this.doBaseMMI();
        var newContextRequest = this._doc.createElementNS(this.namespaceMMI, "mmi:newContextRequest");
        mmi.appendChild(newContextRequest);
        this.setBaseParm(newContextRequest);
        return this;
    };
    ///GENERATE XML for STARTREQUEST
    LifeCycleEvent.prototype.doStartRequest = function (emma) {
        var mmi = this.doBaseMMI();
        var startRequest = this._doc.createElementNS(this.namespaceMMI, "mmi:startRequest");
        mmi.appendChild(startRequest);
        this.setBaseParm(startRequest);
        var data = this._doc.createElementNS(this.namespaceMMI, "mmi:data");
        startRequest.appendChild(data);
        data.appendChild(emma.getElem());
        return this;
    };
    LifeCycleEvent.prototype.doExtensionNotification = function (emma) {
        var mmi = this.doBaseMMI();
        var ExtensionNotification = this._doc.createElementNS(this.namespaceMMI, "mmi:ExtensionNotification");
        mmi.appendChild(ExtensionNotification);
        this.setBaseParm(ExtensionNotification);
        var data = this._doc.createElementNS(this.namespaceMMI, "mmi:data");
        ExtensionNotification.appendChild(data);
        data.appendChild(emma.getElem());
        return this;
    };
    //return LifeCycleEvent string
    LifeCycleEvent.prototype.toString = function () {
        return this._doc.documentElement.innerHTML;
    };
    //print LifeCycleEvent string
    LifeCycleEvent.prototype.consolePrint = function () {
        console.log(this._doc.documentElement.innerHTML);
    };
    return LifeCycleEvent;
}());
///
//  EMMA CLASS
//
//  generates EMMA XML Sintaxe
///
var EMMA = (function () {
    function EMMA(Id, medium, mode, confidence, start, end) {
        this.root = "<root></root>";
        this.namespaceEMMA = "http://www.w3.org/2003/04/emma";
        this.parser = new DOMParser();
        this.Id = Id;
        this.medium = medium;
        this.mode = mode;
        this.start = start;
        this.end = end;
        this.confidence = confidence;
        this._doc = this.parser.parseFromString(this.root, "text/xml");
    }
    /// SET TextContent
    EMMA.prototype.setValue = function (val) {
        this.Value = val;
        return this;
    };
    ///GET EMMA Element
    EMMA.prototype.getElem = function () {
        var emma = this._doc.createElementNS(this.namespaceEMMA, "emma:emma");
        emma.setAttributeNS(this.namespaceEMMA, "emma:version", "1.0");
        this._doc.documentElement.appendChild(emma);
        var interp = this._doc.createElementNS(this.namespaceEMMA, "emma:interpretation");
        interp.setAttributeNS(this.namespaceEMMA, "emma:id", this.Id);
        interp.setAttributeNS(this.namespaceEMMA, "emma:medium", this.medium);
        interp.setAttributeNS(this.namespaceEMMA, "emma:mode", this.mode);
        interp.setAttributeNS(this.namespaceEMMA, "emma:start", this.start.toString());
        if (this.end = null)
            interp.setAttributeNS(this.namespaceEMMA, "emma:end", this.end.toString());
        interp.setAttributeNS(this.namespaceEMMA, "emma:confidence", this.confidence.toString());
        emma.appendChild(interp);
        var command = this._doc.createElement("command");
        command.textContent = this.Value;
        interp.appendChild(command);
        return this._doc.documentElement.firstChild;
    };
    return EMMA;
}());
var MMICLient = (function () {
    function MMICLient(IMAdd, FusionAdd) {
        this.onArrive = new LiteEvent(); ///
        this.onResponse = new LiteEvent(); ///
        this.IMAdd = IMAdd;
        this.FusionAdd = FusionAdd;
    }
    Object.defineProperty(MMICLient.prototype, "OnArrive", {
        get: function () { return this.onArrive.expose(); },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(MMICLient.prototype, "OnResponse", {
        get: function () { return this.onResponse.expose(); },
        enumerable: true,
        configurable: true
    });
    MMICLient.prototype.sendToIM = function (lce) {
        var sender = new XMLHttpRequest();
        sender.open('POST', this.FusionAdd, true);
        var cli = this;
        sender.onload = function () {
            if (sender.status == 200) {
                // console.log('send response: '+ sender.responseText);
                cli.result = sender.responseText;
                cli.onResponse.trigger(sender.responseText);
            }
        };
        sender.send(lce.toString());
    };
    MMICLient.prototype.startPoolIM = function () {
        var cli = this;
        cli.getter = new XMLHttpRequest();
        cli.getter.open('GET', this.IMAdd, true);
        var call = setInterval(function () {
            // console.log('start ready?');
            cli.getter.onreadystatechange = function () {
                if (cli.getter.readyState == 4 && cli.getter.response != "") {
                    clearInterval(call);
                    var xml = cli.getter.response;
                    cli.onArrive.trigger(xml);
                    cli.startPoolIM();
                }
            };
        }, 100);
        cli.getter.send();
    };
    return MMICLient;
}());
var LiteEvent = (function () {
    function LiteEvent() {
        this.handlers = [];
    }
    LiteEvent.prototype.on = function (handler) {
        this.handlers.push(handler);
    };
    LiteEvent.prototype.off = function (handler) {
        this.handlers = this.handlers.filter(function (h) { return h !== handler; });
    };
    LiteEvent.prototype.trigger = function (data) {
        this.handlers.slice(0).forEach(function (h) { return h(data); });
    };
    LiteEvent.prototype.expose = function () {
        return this;
    };
    return LiteEvent;
}());
///EXAMPLES DELETE AFTER
//new LifeCycleEvent("TOUCH", "IM", "touch-1").doNewContextRequest().consolePrint();
//new LifeCycleEvent("TOUCH", "IM", "touch-1", "ctx-1").doStartRequest(new EMMA("touch", "display", "type", 1,0).setValue('{"recognized" : ["T1"], "text": ""}')).consolePrint();
/*
var  cli = new MMICLient("http://localhost:8801/IM?GUI","http://localhost:9876/IM/");
cli.OnArrive.on((data) => {
    console.log(data);
});

cli.OnResponse.on((data) => {
    console.log("RESP: "+data);
});

cli.startPoolIM();

//cli.sendToIM(new LifeCycleEvent("TOUCH", "IM", "touch-1").doNewContextRequest());
cli.sendToIM(new LifeCycleEvent("TOUCH", "IM", "touch-1", "ctx-1").doStartRequest(new EMMA("touch", "display", "type", 1,0).setValue('{"recognized" : ["T1"], "text": ""}')));
*/
