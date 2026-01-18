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
            "ai.generate": "AI Brain / LLM Access",
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

class SettingsDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Settings & Configuration", transient_for=parent, flags=0)
        self.set_default_size(500, 600)
        self.get_style_context().add_class("settings-dialog")
        
        box = self.get_content_area()
        box.set_spacing(10)
        
        # Tabs
        notebook = Gtk.Notebook()
        notebook.set_vexpand(True)
        box.pack_start(notebook, True, True, 0)
        
        # --- TAB 1: SECURITY ---
        security_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        security_box.set_margin_top(15)
        security_box.set_margin_bottom(15)
        security_box.set_margin_start(15)
        security_box.set_margin_end(15)
        
        tab_label1 = Gtk.Label(label="Security")
        notebook.append_page(security_box, tab_label1)
        
        # Security Header
        sec_header = Gtk.Label()
        sec_header.set_markup("<span size='large' weight='bold'>Skill Permissions</span>")
        sec_header.set_xalign(0)
        security_box.pack_start(sec_header, False, False, 0)
        
        # Permissions List
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        scrolled.add(list_box)
        security_box.pack_start(scrolled, True, True, 0)
        
        self._populate_permissions(list_box)

        # --- TAB 2: BRAINS ---
        brains_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        brains_box.set_margin_top(20)
        brains_box.set_margin_bottom(20)
        brains_box.set_margin_start(20)
        brains_box.set_margin_end(20)
        
        tab_label2 = Gtk.Label(label="Brains")
        notebook.append_page(brains_box, tab_label2)
        
        self._build_brains_tab(brains_box)
        
        self.show_all()

    def _populate_permissions(self, list_box):
        """Populate the permissions list in the Security tab."""
        from core.skill_manager import skill_manager
        all_perms = skill_manager.get_all_required_permissions()
        from core.persistence import storage
        granted_perms = storage.get_allowed_permissions()
        
        PERMISSION_LABELS = {
            "system.read": "System Information",
            "apps.launch": "App Launcher",
            "audio.record": "Microphone Access",
            "ai.generate": "AI Brain / LLM Access",
        }
        
        for perm in all_perms:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            row.get_style_context().add_class("settings-row")
            
            icon = Gtk.Image.new_from_icon_name("security-high-symbolic", Gtk.IconSize.MENU)
            row.pack_start(icon, False, False, 0)
            
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            display_text = PERMISSION_LABELS.get(perm, perm)
            p_label = Gtk.Label(label=display_text)
            p_label.set_xalign(0)
            p_label.get_style_context().add_class("settings-skill-label")
            vbox.pack_start(p_label, False, False, 0)
            row.pack_start(vbox, True, True, 0)
            
            sw = Gtk.Switch()
            sw.set_valign(Gtk.Align.CENTER)
            sw.set_active(perm in granted_perms)
            sw.connect("state-set", self.on_perm_toggled, perm)
            row.pack_end(sw, False, False, 0)
            list_box.pack_start(row, False, False, 0)

    def on_perm_toggled(self, switch, state, perm):
        """Handle permission toggle."""
        from core.skill_manager import skill_manager
        skill_manager.toggle_permission(perm, state)
        return False

    def _build_brains_tab(self, box):
        """Build the Brain Manager UI tab."""
        from core.brain_manager import brain_manager
        
        # Header
        header = Gtk.Label()
        header.set_markup("<span size='large' weight='bold'>LLM Brain Manager</span>")
        header.set_xalign(0)
        box.pack_start(header, False, False, 0)
        
        # Description
        desc = Gtk.Label(label="Configure which LLM provider AVA uses for reasoning.")
        desc.set_xalign(0)
        desc.set_line_wrap(True)
        desc.get_style_context().add_class("widget-status")
        box.pack_start(desc, False, False, 0)
        
        # Separator
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        box.pack_start(sep, False, False, 10)
        
        # Active Brain Section
        active_label = Gtk.Label()
        active_label.set_markup("<b>Active Brain</b>")
        active_label.set_xalign(0)
        box.pack_start(active_label, False, False, 0)
        
        # Active Brain Selector
        self.active_brain_combo = Gtk.ComboBoxText()
        self.active_brain_combo.get_style_context().add_class("settings-combo-box")
        
        # Populate with available Brains
        all_brains = brain_manager.get_all_brains()
        active_brain = brain_manager.get_active_brain()
        
        for brain in all_brains:
            privacy_badge = {"local": "🔒", "trusted_cloud": "☁️", "external_cloud": "🌐"}.get(
                brain.get_privacy_level().value, ""
            )
            display_name = f"{privacy_badge} {brain.name}"
            self.active_brain_combo.append(brain.id, display_name)
            
        if active_brain:
            self.active_brain_combo.set_active_id(active_brain.id)
        
        self.active_brain_combo.connect("changed", self.on_active_brain_changed)
        box.pack_start(self.active_brain_combo, False, False, 0)
        
        # Rules-only mode toggle
        rules_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        rules_label = Gtk.Label(label="Rules-Only Mode (Disable all LLMs)")
        rules_label.set_xalign(0)
        rules_box.pack_start(rules_label, True, True, 0)
        
        self.rules_only_switch = Gtk.Switch()
        self.rules_only_switch.set_active(brain_manager.rules_only_mode)
        self.rules_only_switch.connect("state-set", self.on_rules_only_toggled)
        rules_box.pack_end(self.rules_only_switch, False, False, 0)
        box.pack_start(rules_box, False, False, 5)
        
        # Separator
        sep2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        box.pack_start(sep2, False, False, 10)
        
        # Installed Brains Section
        installed_label = Gtk.Label()
        installed_label.set_markup("<b>Installed Brains</b>")
        installed_label.set_xalign(0)
        box.pack_start(installed_label, False, False, 0)
        
        # Scrolled window for Brains list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(200)
        
        self.brains_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        scrolled.add(self.brains_list_box)
        box.pack_start(scrolled, True, True, 0)
        
        self._populate_brains_list()
        
        # Add Brain Button
        add_btn = Gtk.Button(label="+ Add Brain")
        add_btn.get_style_context().add_class("send-btn")
        add_btn.connect("clicked", self.on_add_brain_clicked)
        box.pack_end(add_btn, False, False, 0)

    def _populate_brains_list(self):
        """Populate the list of installed Brains."""
        from core.brain_manager import brain_manager
        
        # Clear existing
        for child in self.brains_list_box.get_children():
            self.brains_list_box.remove(child)
        
        all_brains = brain_manager.get_all_brains()
        
        for brain in all_brains:
            brain_row = self._create_brain_row(brain)
            self.brains_list_box.pack_start(brain_row, False, False, 0)
        
        self.brains_list_box.show_all()
    
    def _create_brain_row(self, brain):
        """Create a row widget for a Brain."""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row.get_style_context().add_class("settings-row")
        
        # Privacy badge icon
        privacy_level = brain.get_privacy_level().value
        privacy_icons = {
            "local": "🔒",
            "trusted_cloud": "☁️",
            "external_cloud": "🌐"
        }
        icon_label = Gtk.Label(label=privacy_icons.get(privacy_level, "❓"))
        row.pack_start(icon_label, False, False, 0)
        
        # Brain info
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        
        name_label = Gtk.Label(label=brain.name)
        name_label.set_xalign(0)
        name_label.get_style_context().add_class("settings-skill-label")
        vbox.pack_start(name_label, False, False, 0)
        
        # Provider and status
        health = brain.health_check()
        status_text = f"{brain.provider} • {health.status.value}"
        status_label = Gtk.Label(label=status_text)
        status_label.set_xalign(0)
        status_label.get_style_context().add_class("widget-status")
        vbox.pack_start(status_label, False, False, 0)
        
        row.pack_start(vbox, True, True, 0)
        
        # Status indicator
        status_icon = "✓" if health.status.value == "available" else "⚠"
        status_indicator = Gtk.Label(label=status_icon)
        status_indicator.get_style_context().add_class("permission-status-tag")
        row.pack_end(status_indicator, False, False, 0)
        
        # Test button (only for non-rules Brains)
        if brain.id != "rules":
            test_btn = Gtk.Button(label="Test")
            test_btn.get_style_context().add_class("app-launch-btn")
            test_btn.connect("clicked", self.on_test_brain_clicked, brain)
            row.pack_end(test_btn, False, False, 5)
        
        return row
    
    def on_active_brain_changed(self, combo):
        """Handle active Brain selection change."""
        from core.brain_manager import brain_manager
        brain_id = combo.get_active_id()
        if brain_id:
            brain_manager.set_active_brain(brain_id)
            # Reload Brain system
            from core.brain import brain
            brain.reload_config()
            print(f"✅ Active Brain changed to: {brain_id}")
    
    def on_rules_only_toggled(self, switch, state):
        """Handle rules-only mode toggle."""
        from core.brain_manager import brain_manager
        brain_manager.set_rules_only_mode(state)
        
        # Disable/enable active Brain combo
        self.active_brain_combo.set_sensitive(not state)
        return False
    
    def on_test_brain_clicked(self, button, brain):
        """Test a Brain's health."""
        button.set_label("Testing...")
        button.set_sensitive(False)
        
        def test_thread():
            health = brain.health_check()
            
            def show_result():
                # Show dialog with result
                dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.INFO if health.status.value == "available" else Gtk.MessageType.WARNING,
                    buttons=Gtk.ButtonsType.OK,
                    text=f"Brain Test: {brain.name}"
                )
                dialog.format_secondary_text(
                    f"Status: {health.status.value}\n"
                    f"Message: {health.message}\n"
                    + (f"Latency: {health.latency_ms:.0f}ms" if health.latency_ms else "")
                )
                dialog.run()
                dialog.destroy()
                
                button.set_label("Test")
                button.set_sensitive(True)
                
                # Refresh the list
                self._populate_brains_list()
            
            GLib.idle_add(show_result)
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def on_add_brain_clicked(self, button):
        """Show dialog to add a new Brain."""
        dialog = AddBrainDialog(self)
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            # Get Brain configuration from dialog
            provider, name, config_data = dialog.get_brain_config()
            
            # Create Brain instance
            from core.brain_interface import BrainConfig
            from core.brain_manager import brain_manager
            from core.brains.ollama_brain import OllamaBrain
            from core.brains.lmstudio_brain import LMStudioBrain
            from core.brains.google_brain import GoogleBrain
            from core.brains.openai_brain import OpenAIBrain
            from core.brains.claude_brain import ClaudeBrain
            from core.persistence import storage
            import uuid
            
            # Generate unique ID
            brain_id = f"{provider}_{uuid.uuid4().hex[:8]}"
            
            brain_config = BrainConfig(
                id=brain_id,
                name=name,
                provider=provider,
                config_data=config_data
            )
            
            # Create Brain based on provider
            try:
                if provider == "ollama":
                    new_brain = OllamaBrain(brain_config)
                elif provider == "lmstudio":
                    new_brain = LMStudioBrain(brain_config)
                elif provider == "google":
                    new_brain = GoogleBrain(brain_config)
                elif provider == "openai":
                    new_brain = OpenAIBrain(brain_config)
                elif provider == "claude":
                    new_brain = ClaudeBrain(brain_config)
                else:
                    raise ValueError(f"Unknown provider: {provider}")
                
                # Register Brain
                brain_manager.register_brain(new_brain)
                
                # Save to database
                capabilities = [cap.value for cap in new_brain.get_capabilities()]
                storage.save_brain_config(
                    brain_id,
                    name,
                    provider,
                    new_brain.get_privacy_level().value,
                    config_data,
                    capabilities
                )
                
                print(f"✅ Added new Brain: {name}")
                
                # Refresh the Brains list
                self._populate_brains_list()
                
                # Update active Brain combo
                all_brains = brain_manager.get_all_brains()
                
                self.active_brain_combo.remove_all()
                for brain in all_brains:
                    privacy_badge = {"local": "🔒", "trusted_cloud": "☁️", "external_cloud": "🌐"}.get(
                        brain.get_privacy_level().value, ""
                    )
                    display_name = f"{privacy_badge} {brain.name}"
                    self.active_brain_combo.append(brain.id, display_name)
                
            except Exception as e:
                # Show error dialog
                error_dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text="Failed to Add Brain"
                )
                error_dialog.format_secondary_text(str(e))
                error_dialog.run()
                error_dialog.destroy()
        
        dialog.destroy()


class AddBrainDialog(Gtk.Dialog):
    """Dialog for adding a new Brain."""
    
    def __init__(self, parent):
        super().__init__(title="Add New Brain", transient_for=parent, flags=0)
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        )
        self.set_default_size(400, 400)
        
        box = self.get_content_area()
        box.set_spacing(15)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        # Provider selection
        lbl = Gtk.Label(label="Provider")
        lbl.set_xalign(0)
        lbl.get_style_context().add_class("settings-skill-label")
        box.pack_start(lbl, False, False, 0)
        
        self.provider_combo = Gtk.ComboBoxText()
        self.provider_combo.append("ollama", "🔒 Ollama (Local)")
        self.provider_combo.append("lmstudio", "🔒 LM Studio (Local)")
        self.provider_combo.append("google", "☁️ Google Gemini")
        self.provider_combo.append("openai", "🌐 OpenAI")
        self.provider_combo.append("claude", "🌐 Anthropic Claude")
        self.provider_combo.set_active(0)
        self.provider_combo.connect("changed", self.on_provider_changed)
        box.pack_start(self.provider_combo, False, False, 0)
        
        # Brain name
        lbl = Gtk.Label(label="Brain Name")
        lbl.set_xalign(0)
        lbl.get_style_context().add_class("settings-skill-label")
        box.pack_start(lbl, False, False, 0)
        
        self.name_entry = Gtk.Entry()
        self.name_entry.set_placeholder_text("My Brain")
        box.pack_start(self.name_entry, False, False, 0)
        
        # Dynamic config area
        self.config_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.pack_start(self.config_box, True, True, 0)
        
        # Initial config for Ollama
        self.on_provider_changed(self.provider_combo)
        
        self.show_all()
    
    def on_provider_changed(self, combo):
        """Update config fields based on selected provider."""
        # Clear existing config fields
        for child in self.config_box.get_children():
            self.config_box.remove(child)
        
        provider = combo.get_active_id()
        
        if provider == "ollama":
            self._add_config_field("Ollama Host", "http://localhost:11434", "host_entry")
            self._add_config_field("Model Name", "llama3", "model_entry")
        
        elif provider == "lmstudio":
            self._add_config_field("LM Studio Endpoint", "http://localhost:1234/v1", "endpoint_entry")
            self._add_config_field("Model Name", "local-model", "model_entry")
        
        elif provider in ["google", "openai", "claude"]:
            self._add_config_field("API Key", "", "api_key_entry", password=True)
            
            default_models = {
                "google": "gemini-1.5-flash",
                "openai": "gpt-4o-mini",
                "claude": "claude-3-5-sonnet-20241022"
            }
            self._add_config_field("Model Name", default_models.get(provider, ""), "model_entry")
        
        self.config_box.show_all()
    
    def _add_config_field(self, label_text, placeholder, entry_name, password=False):
        """Helper to add a config field."""
        lbl = Gtk.Label(label=label_text)
        lbl.set_xalign(0)
        lbl.get_style_context().add_class("settings-skill-label")
        self.config_box.pack_start(lbl, False, False, 0)
        
        entry = Gtk.Entry()
        entry.set_placeholder_text(placeholder)
        if password:
            entry.set_visibility(False)
        setattr(self, entry_name, entry)
        self.config_box.pack_start(entry, False, False, 0)
    
    def get_brain_config(self):
        """Get the configured Brain settings."""
        provider = self.provider_combo.get_active_id()
        name = self.name_entry.get_text() or f"{provider.capitalize()} Brain"
        
        config_data = {}
        
        if provider == "ollama":
            config_data = {
                "host": self.host_entry.get_text() or "http://localhost:11434",
                "model": self.model_entry.get_text() or "llama3"
            }
        elif provider == "lmstudio":
            config_data = {
                "endpoint": self.endpoint_entry.get_text() or "http://localhost:1234/v1",
                "model": self.model_entry.get_text() or "local-model"
            }
        elif provider in ["google", "openai", "claude"]:
            config_data = {
                "api_key": self.api_key_entry.get_text(),
                "model": self.model_entry.get_text()
            }
        
        return provider, name, config_data

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
        
        # Schedule Startup Checks
        GLib.idle_add(self.check_startup_permissions)

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

    def check_startup_permissions(self):
        """Checks if critical permissions (Mic, AI) are granted on startup."""
        from core.persistence import storage
        from core.skill_manager import skill_manager
        
        allowed = storage.get_allowed_permissions()
        
        # 1. Microphone Check
        if "audio.record" not in allowed:
            print("🎙️ Requesting Microphone Access...")
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

        # 2. AI Brain Check (LLM)
        if "ai.generate" not in allowed:
            print("🧠 Requesting AI/LLM Access...")
            granted = skill_manager._request_permission("AVVA Core", "ai.generate")
            if granted:
                skill_manager.toggle_permission("ai.generate", True)
                print("✅ AI Access granted.")
            else:
                print("❌ AI Access denied. LLM features disabled.")
        else:
            if "ai.generate" not in skill_manager.allowed_permissions:
                skill_manager.allowed_permissions.append("ai.generate")

    def on_security_clicked(self, button):
        dialog = SettingsDialog(self)
        dialog.run()
        dialog.destroy()
        # Re-sync state
        self.check_startup_permissions()

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