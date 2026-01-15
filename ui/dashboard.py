import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Handy', '1')
from gi.repository import Gtk, Gdk, GLib, Handy
import threading
import time
import os

# AVVA Core Imports
from core.stt import listen
from core.tts import speak
from core.brain import brain
from core.config import config

class StatsWidget(Gtk.Box):
    def __init__(self, cpu, ram, disk):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.get_style_context().add_class("stats-widget")
        self.set_margin_top(5)
        self.set_margin_bottom(5)
        
        self._add_row("CPU Usage", cpu)
        self._add_row("RAM Usage", ram)
        self._add_row("Disk Space", disk)

    def _add_row(self, title, value):
        row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        
        # Label with value
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        label = Gtk.Label(label=title)
        label.get_style_context().add_class("widget-label")
        val_label = Gtk.Label(label=f"{value}%")
        val_label.get_style_context().add_class("widget-value")
        
        header.pack_start(label, False, False, 0)
        header.pack_end(val_label, False, False, 0)
        row.pack_start(header, False, False, 0)
        
        # Progress Bar
        bar = Gtk.ProgressBar()
        bar.set_fraction(value / 100.0)
        bar.get_style_context().add_class("widget-progress")
        row.pack_start(bar, False, False, 0)
        
        self.pack_start(row, False, False, 0)

class Bubble(Gtk.Box):
    def __init__(self, text, sender="user", data=None):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
        self.get_style_context().add_class("bubble-row")
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        if text:
            label = Gtk.Label(label=text)
            label.set_line_wrap(True)
            label.set_line_wrap_mode(2)  # WORD_CHAR mode
            label.set_max_width_chars(50)
            label.set_xalign(0 if sender == "avva" else 1)
            label.set_selectable(True)
            vbox.pack_start(label, False, False, 0)

        # Handle Rich Widgets
        if data and data.get("type") == "system_stats":
            widget = StatsWidget(data['cpu'], data['ram'], data['disk'])
            vbox.pack_start(widget, False, False, 0)
            
        box = Gtk.EventBox()
        box.add(vbox)
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
        self.set_default_size(480, 750)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Load CSS
        style_provider = Gtk.CssProvider()
        # Resolve absolute path to style.css
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        css_path = os.path.join(base_dir, "ui", "style.css")
        style_provider.load_from_path(css_path)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Main Layout
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.main_box.get_style_context().add_class("main-layout")
        self.add(self.main_box)

        # Header with title and controls
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header.get_style_context().add_class("header")
        
        title_label = Gtk.Label(label=config.NAME.upper())
        title_label.get_style_context().add_class("title-label")
        header.pack_start(title_label, False, False, 0)
        
        # Spacer
        header.pack_start(Gtk.Box(), True, True, 0)
        
        # Mic toggle button
        self.mic_toggle = Gtk.ToggleButton()
        self.mic_toggle.set_active(True)
        mic_icon = Gtk.Label(label="🎙")
        self.mic_toggle.add(mic_icon)
        self.mic_toggle.get_style_context().add_class("control-btn")
        self.mic_toggle.connect("toggled", self.on_mic_toggled)
        header.pack_end(self.mic_toggle, False, False, 0)
        
        self.main_box.pack_start(header, False, False, 0)

        # The Orb with pulsing animation
        self.orb_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.orb_container.get_style_context().add_class("orb-container")
        
        orb_wrapper = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.orb = Gtk.Box()
        self.orb.set_size_request(100, 100)
        self.orb.get_style_context().add_class("orb")
        orb_wrapper.pack_start(self.orb, True, False, 0)
        self.orb_container.pack_start(orb_wrapper, False, False, 0)
        
        # Status text below orb
        self.orb_status = Gtk.Label(label="Ready")
        self.orb_status.get_style_context().add_class("orb-status")
        self.orb_container.pack_start(self.orb_status, False, False, 0)
        
        self.main_box.pack_start(self.orb_container, False, False, 15)

        # Conversation Stream
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.get_style_context().add_class("chat-scroll")
        self.main_box.pack_start(self.scroll, True, True, 0)

        self.chat_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.chat_box.set_margin_top(10)
        self.chat_box.set_margin_bottom(10)
        self.scroll.add(self.chat_box)

        # Input Area
        input_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        input_container.get_style_context().add_class("input-container")
        self.main_box.pack_start(input_container, False, False, 0)

        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Type your message...")
        self.entry.get_style_context().add_class("message-input")
        self.entry.connect("activate", self.on_entry_activated)
        input_container.pack_start(self.entry, True, True, 0)

        # Send button
        send_btn = Gtk.Button(label="➤")
        send_btn.get_style_context().add_class("send-btn")
        send_btn.connect("clicked", lambda _: self.on_entry_activated(self.entry))
        input_container.pack_end(send_btn, False, False, 0)

        # Footer status
        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        footer.get_style_context().add_class("footer")
        
        self.status_label = Gtk.Label(label="● Online")
        self.status_label.get_style_context().add_class("status-label")
        footer.pack_start(self.status_label, False, False, 0)
        
        self.main_box.pack_start(footer, False, False, 0)

        self.connect("destroy", Gtk.main_quit)
        self.show_all()

        # Start Background Listen Thread
        self.active = True
        self.listening_enabled = True
        self.thread = threading.Thread(target=self.voice_loop, daemon=True)
        self.thread.start()

    def on_mic_toggled(self, button):
        self.listening_enabled = button.get_active()
        if not self.listening_enabled:
            self.update_orb(None)

    def add_message(self, text, sender="user", data=None):
        GLib.idle_add(self._do_add_message, text, sender, data)

    def _do_add_message(self, text, sender, data):
        bubble = Bubble(text, sender, data)
        self.chat_box.pack_start(bubble, False, False, 0)
        
        # Auto-scroll to bottom with slight delay for animation
        GLib.timeout_add(50, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        adj = self.scroll.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())
        return False

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
            None: "Ready"
        }
        status_text = status_map.get(state, "Ready")
        self.orb_status.set_text(status_text)
        
        # Update footer status
        online_status = "● Online" if self.listening_enabled else "○ Mic Off"
        self.status_label.set_text(online_status)

    def on_entry_activated(self, entry):
        text = entry.get_text().strip()
        if text:
            entry.set_text("")
            threading.Thread(target=self.process_command, args=(text,), daemon=True).start()

    def process_command(self, command):
        self.add_message(command, "user")
        self.update_orb("thinking")
        
        response = brain.process(command)
        
        if response:
            if isinstance(response, dict):
                text = response.get("text")
                data = response
            else:
                text = response
                data = None
                
            self.add_message(text, "avva", data)
            self.update_orb("speaking")
            speak(text)
        
        self.update_orb(None)

    def voice_loop(self):
        """Background thread for continuous voice interaction."""
        while self.active:
            if self.listening_enabled:
                self.update_orb("listening")
                command = listen()
                
                if command:
                    self.process_command(command)
                else:
                    time.sleep(0.1)
            else:
                time.sleep(0.5)

if __name__ == "__main__":
    win = Dashboard()
    Gtk.main()