# ui.py
from Screens.Screen import Screen
from Components.Label import Label
from Components.ActionMap import ActionMap

class AboutChannelSorter(Screen):
    skin = """
    <screen name="AboutChannelSorter" position="center,center" size="600,200" title="About Channel Sorter">
        <widget name="label" position="10,10" size="580,180" font="Regular;20" />
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self["label"] = Label("Channel Sorter Plugin\n\nVersion 1.0\nAuthor: Your Name")
        self["actions"] = ActionMap(["OkCancelActions"], {
            "cancel": self.close,
            "ok": self.close
        }, -1)
