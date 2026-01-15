import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Handy', '1')
from gi.repository import Gtk, Gdk, GLib, Handy
import threading
import time

# AVVA Core Imports
from core.stt import listen
from core.tts import speak
from core.brain import brain
from core.config import config

class Bubble(Gtk.Box):
    def __init__(self, text, sender="user"):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
        self.get_style_context().add_class("bubble-row")
        
        label = Gtk.Label(label=text)
        label.set_line_wrap(True)
        label.set_max_width_chars(40)
        label.set_xalign(0 if sender == "avva" else 1)
        
        box = Gtk.EventBox()
        box.add(label)
        box.get_style_context().add_class("bubble")
        box.get_style_context().add_class(sender)
        
        if sender == "user":
            self.pack_end(box, False, False, 10)
        else:
            self.pack_start(box, False, False, 10)
        
        self.show_all()

class Dashboard(Gtk.Window):
    def __init__(self):
        super().__init__(title=f"{config.NAME} Dashboard")
        Handy.init()
        
        # Window Config
        self.set_default_size(450, 700)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Load CSS
        style_provider = Gtk.CssProvider()
        style_provider.load_from_path("ui/style.css")
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Main Layout
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.main_box.get_style_context().add_class("main-layout")
        self.add(self.main_box)

        # 1. The Orb
        self.orb_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.orb_container.get_style_context().add_class("orb-container")
        self.orb = Gtk.Box()
        self.orb.set_size_request(80, 80)
        self.orb.get_style_context().add_class("orb")
        self.orb_container.pack_start(self.orb, True, False, 0)
        self.main_box.pack_start(self.orb_container, False, False, 20)

        # 2. Conversation Stream
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.get_style_context().add_class("chat-scroll")
        self.main_box.pack_start(self.scroll, True, True, 0)

        self.chat_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.scroll.add(self.chat_box)

        # 3. Bottom Bar
        bottom_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        bottom_bar.get_style_context().add_class("bottom-bar")
        self.main_box.pack_start(bottom_bar, False, False, 15)

        self.status_label = Gtk.Label(label="Initialized")
        self.status_label.get_style_context().add_class("status-label")
        bottom_bar.pack_start(self.status_label, True, False, 0)

        # Entry for manual typing
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Type a command...")
        self.entry.connect("activate", self.on_entry_activated)
        bottom_bar.pack_end(self.entry, True, True, 0)

        self.connect("destroy", Gtk.main_quit)
        self.show_all()

        # Start Background Listen Thread
        self.active = True
        self.thread = threading.Thread(target=self.voice_loop, daemon=True)
        self.thread.start()

    def add_message(self, text, sender="user"):
        GLib.idle_add(self._do_add_message, text, sender)

    def _do_add_message(self, text, sender):
        bubble = Bubble(text, sender)
        self.chat_box.pack_start(bubble, False, False, 0)
        # Auto-scroll to bottom
        adj = self.scroll.get_vadjustment()
        adj.set_value(adj.get_upper())

    def update_orb(self, state):
        GLib.idle_add(self._do_update_orb, state)

    def _do_update_orb(self, state):
        ctx = self.orb.get_style_context()
        ctx.remove_class("listening")
        ctx.remove_class("thinking")
        ctx.remove_class("speaking")
        if state:
            ctx.add_class(state)
        
        status_map = {
            "listening": "Listening...",
            "thinking": "Thinking...",
            "speaking": "Speaking...",
            None: "Idle"
        }
        self.status_label.set_text(status_map.get(state, "Idle"))

    def on_entry_activated(self, entry):
        text = entry.get_text()
        if text:
            entry.set_text("")
            threading.Thread(target=self.process_command, args=(text,), daemon=True).start()

    def process_command(self, command):
        self.add_message(command, "user")
        self.update_orb("thinking")
        
        response = brain.process(command)
        
        if response:
            self.add_message(response, "avva")
            self.update_orb("speaking")
            speak(response)
        
        self.update_orb(None)

    def voice_loop(self):
        """Background thread for continuous voice interaction."""
        while self.active:
            self.update_orb("listening")
            command = listen()
            
            if command:
                self.process_command(command)
            else:
                # Brief pause to avoid CPU spiking if listen() returns instantly
                time.sleep(0.1)

if __name__ == "__main__":
    win = Dashboard()
    Gtk.main()
