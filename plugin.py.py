# plugin.py

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.config import config, ConfigSelection, getConfigListEntry
from Components.Label import Label
from Components.ActionMap import ActionMap
import random
import os

config.plugins.channelsorter = ConfigSelection(default="alphabetical", choices=[
    ("alphabetical", "Alphabetical"),
    ("frequency", "By Frequency"),
    ("random", "Random")
])
config.plugins.channeltype = ConfigSelection(default="TV", choices=[
    ("TV", "TV"),
    ("Radio", "Radio"),
    ("Data", "Data")
])

class ChannelSorter(Screen, ConfigListScreen):
    skin = """
    <screen name="ChannelSorter" position="center,center" size="600,400" title="Channel Sorter">
        <widget name="config" position="10,10" size="580,150" />
        <widget name="status" position="10,170" size="580,200" font="Regular;20" />
    </screen>
    """

    def __init__(self, session, **kwargs):
        Screen.__init__(self, session)
        self.session = session
        self["status"] = Label("Press OK to sort the current bouquet.")
        self.list = [
            getConfigListEntry("Sort Order", config.plugins.channelsorter),
            getConfigListEntry("Channel Type", config.plugins.channeltype)
        ]
        ConfigListScreen.__init__(self, self.list)
        self["actions"] = ActionMap(["OkCancelActions"], {
            "ok": self.sort_current_bouquet,
            "cancel": self.close
        }, -1)

    def sort_current_bouquet(self):
        bouquet = self.get_current_bouquet()
        if not bouquet:
            self["status"].setText("No bouquet found for the selected channel type.")
            return

        try:
            metadata, services = self.get_services_from_bouquet(bouquet)
            method = config.plugins.channelsorter.value

            if method == "alphabetical":
                services.sort()
            elif method == "random":
                random.shuffle(services)
            elif method == "frequency":
                lamedb_map = self.parse_lamedb()
                services.sort(key=lambda s: self.get_frequency_from_service(s, lamedb_map))

            self.write_services_to_bouquet(bouquet, metadata, services)
            self["status"].setText(f"{len(services)} channels sorted by {method}.")
        except Exception as e:
            self["status"].setText(f"Error: {str(e)}")

    def get_current_bouquet(self):
        channel_type = config.plugins.channeltype.value.lower()
        path = "/etc/enigma2/"
        for filename in os.listdir(path):
            if filename.startswith("userbouquet.") and filename.endswith(f".{channel_type}"):
                return os.path.join(path, filename)
        return None

    def get_services_from_bouquet(self, bouquet):
        services = []
        metadata = []
        with open(bouquet, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    metadata.append(line)
                else:
                    services.append(line)
        return metadata, services

    def write_services_to_bouquet(self, bouquet, metadata, services):
        with open(bouquet, "w") as f:
            for line in metadata:
                f.write(line + "\n")
            for s in services:
                f.write(s + "\n")

    def parse_lamedb(self):
        lamedb_path = "/etc/enigma2/lamedb"
        freq_map = {}
        try:
            with open(lamedb_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except IOError:
            return freq_map

        index = 0
        while index < len(lines):
            line = lines[index].strip()
            if line.count(":") == 2:
                sid_tsid_nid = line.lower()
                index += 2
                if index < len(lines):
                    freq_line = lines[index].strip()
                    parts = freq_line.split()
                    if len(parts) >= 2:
                        try:
                            frequency = int(parts[1])
                        except ValueError:
                            frequency = 0
                        freq_map[sid_tsid_nid] = frequency
                index += 1
            else:
                index += 1
        return freq_map

    def get_frequency_from_service(self, service_line, freq_map):
        try:
            if not service_line.startswith("1:"):
                return 0
            parts = service_line.split(":")
            sid = parts[3].lower()
            tsid = parts[4].lower()
            nid = parts[5].lower()
            key = f"{sid}:{tsid}:{nid}"
            return freq_map.get(key, 0)
        except Exception:
            return 0

def main(session, **kwargs):
    session.open(ChannelSorter)

def Plugins(**kwargs):
    return [
        PluginDescriptor(
            name="Channel Sorter",
            description="Sort bouquet channels by name, frequency, or randomly",
            where=[PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU],
            fnc=main
        )
    ]
