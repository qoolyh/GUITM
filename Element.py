class Element:
    def __init__(self, idx, eid, cls, text, desc, checkable, checked, clickable, focusable, scrollable, longClickable, password, bounds, actName='', mtype='event'):
        self.idx = idx
        self.cls = cls
        self.desc = desc
        self.checkable = checkable
        self.checked = checked
        self.clickable = clickable
        self.focusable = focusable
        self.scrollable = scrollable
        self.longClickable= longClickable
        self.password = password
        self.id = eid
        self.text = text
        self.type = mtype
        self.activity = actName
        self.bounds = bounds

