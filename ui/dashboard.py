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

class AppWidget(Gtk.Box):
    def __init__(self, name, icon, exec_cmd=None):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.get_style_context().add_class("app-widget")
        self.set_margin_top(5)
        self.set_margin_bottom(5)
        self.exec_cmd = exec_cmd
        self.app_name = name
        
        # Icon
        image = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.LARGE_TOOLBAR)
        image.set_pixel_size(48)
        self.pack_start(image, False, False, 0)
        
        # Details
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        label = Gtk.Label(label=name)
        label.set_xalign(0)
        label.get_style_context().add_class("widget-label-large")
        vbox.pack_start(label, False, False, 0)
        
        status = Gtk.Label(label="Ready to Launch")
        status.set_xalign(0)
        status.get_style_context().add_class("widget-status")
        vbox.pack_start(status, False, False, 0)
        
        self.pack_start(vbox, True, True, 0)
        
        # Launch Button
        btn = Gtk.Button(label="Open")
        btn.get_style_context().add_class("app-launch-btn")
        btn.connect("clicked", self.on_launch_clicked)
        self.pack_end(btn, False, False, 0)

    def on_launch_clicked(self, button):
        if self.exec_cmd:
            from core.ipc_bridge import ipc_bridge
            ipc_bridge.call("launch_app", exec_cmd=self.exec_cmd, name=self.app_name)

class PermissionWidget(Gtk.Box):
    def __init__(self, perms):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.get_style_context().add_class("permission-list-widget")
        self.set_margin_top(5)
        self.set_margin_bottom(5)
        
        header = Gtk.Label()
        header.set_markup("<b>Active Security Permissions</b>")
        header.set_xalign(0)
        header.get_style_context().add_class("widget-header")
        self.pack_start(header, False, False, 4)
        
        PERMISSION_LABELS = {
            "system.read": "System Information",
            "apps.launch": "App Launcher",
            "audio.record": "Microphone",
        }
        
        for p in perms:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            row.get_style_context().add_class("permission-row")
            
            icon = Gtk.Image.new_from_icon_name("security-high-symbolic", Gtk.IconSize.MENU)
            row.pack_start(icon, False, False, 0)
            
            raw_perm = p['permission']
            display_text = PERMISSION_LABELS.get(raw_perm, raw_perm)
            
            label = Gtk.Label(label=display_text)
            label.set_xalign(0)
            label.get_style_context().add_class("permission-label")
            row.pack_start(label, True, True, 0)
            
            status = Gtk.Label(label="Allowed")
            status.get_style_context().add_class("permission-status-tag")
            row.pack_end(status, False, False, 0)
            
            self.pack_start(row, False, False, 0)

class PermissionSettingsDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Security & Permissions", transient_for=parent, flags=0)
        self.set_default_size(400, 500)
        self.get_style_context().add_class("settings-dialog")
        
        box = self.get_content_area()
        box.set_spacing(10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        # Header
        label = Gtk.Label()
        label.set_markup("<span size='large' weight='bold'>Skill Permissions</span>")
        label.set_xalign(0)
        box.pack_start(label, False, False, 10)
        
        # Scrolled window for permission list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(350)
        
        list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        scrolled.add(list_box)
        box.pack_start(scrolled, True, True, 0)
        
        # Load all permissions
        from core.skill_manager import skill_manager
        all_perms = skill_manager.get_all_required_permissions()
        from core.persistence import storage
        granted_perms = storage.get_allowed_permissions() # list of strings
        
        for perm in all_perms:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            row.get_style_context().add_class("settings-row")
            
            icon = Gtk.Image.new_from_icon_name("security-high-symbolic", Gtk.IconSize.MENU)
            row.pack_start(icon, False, False, 0)
            
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            
            PERMISSION_LABELS = {
                "system.read": "System Information",
                "apps.launch": "App Launcher",
                "audio.record": "Microphone Access",
            }
            display_text = PERMISSION_LABELS.get(perm, perm)
            
            p_label = Gtk.Label(label=display_text)
            p_label.set_xalign(0)
            p_label.get_style_context().add_class("settings-skill-label") # Reuse bold style
            vbox.pack_start(p_label, False, False, 0)
            
            row.pack_start(vbox, True, True, 0)
            
            sw = Gtk.Switch()
            sw.set_valign(Gtk.Align.CENTER)
            
            # Check if granted
            is_granted = perm in granted_perms
            sw.set_active(is_granted)
            
            sw.connect("state-set", self.on_switch_toggled, perm)
            row.pack_end(sw, False, False, 0)
            
            list_box.pack_start(row, False, False, 0)
            
        self.show_all()

    def on_switch_toggled(self, switch, state, perm):
        from core.skill_manager import skill_manager
        skill_manager.toggle_permission(perm, state)
        return False # Accept state change

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
        elif data and data.get("type") == "app_launcher":
            widget = AppWidget(
                data.get("app_name", "App"), 
                data.get("icon", "system-run"),
                data.get("exec_cmd")
            )
            vbox.pack_start(widget, False, False, 0)
        elif data and data.get("type") == "permissions":
            widget = PermissionWidget(data.get("permissions", []))
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
        super().__init__(title=f"{config.NAME} Desktop")
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
        
        # Security Settings button
        self.security_btn = Gtk.Button()
        sec_icon = Gtk.Label(label="🛡️")
        self.security_btn.add(sec_icon)
        self.security_btn.get_style_context().add_class("control-btn")
        self.security_btn.connect("clicked", self.on_security_clicked)
        header.pack_end(self.security_btn, False, False, 5)
        
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
        self.scroll.set_vexpand(True)
        self.scroll.get_style_context().add_class("conversation-area")
        
        self.chat_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.chat_box.set_margin_start(15)
        self.chat_box.set_margin_end(15)
        self.chat_box.set_margin_top(15)
        self.chat_box.set_margin_bottom(15)
        self.scroll.add(self.chat_box)
        
        self.main_box.pack_start(self.scroll, True, True, 0)
        
        self.show_all()
        
        # Schedule Mic Check
        GLib.idle_add(self.check_mic_permission)

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

    def check_mic_permission(self):
        """Checks if microphone access is granted on startup."""
        from core.persistence import storage
        from core.skill_manager import skill_manager
        
        allowed = storage.get_allowed_permissions()
        if "audio.record" not in allowed:
            print("🎙️ Requesting Microphone Access...")
            # We use a custom 'AVVA' label for the requester
            granted = skill_manager._request_permission("AVVA Core", "audio.record")
            if granted:
                skill_manager.toggle_permission("audio.record", True)
                self.mic_toggle.set_active(True)
                print("✅ Microphone access granted.")
            else:
                self.mic_toggle.set_active(False)
                print("❌ Microphone access denied.")
        else:
            if "audio.record" not in skill_manager.allowed_permissions:
                skill_manager.allowed_permissions.append("audio.record")

    def on_security_clicked(self, button):
        dialog = PermissionSettingsDialog(self)
        dialog.run()
        dialog.destroy()
        # Re-sync mic state in case permission was toggled
        self.check_mic_permission()

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