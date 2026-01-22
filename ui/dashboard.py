import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Handy', '1')
from gi.repository import Gtk, Gdk, GLib, Handy
import threading
import os
import psutil

# AVVA Core Imports
from core.stt import listen
from core.tts import speak
from core.brain import brain
from core.config import config

class SystemPulseWidget(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.get_style_context().add_class("system-pulse-widget")
        self.set_margin_top(20)
        self.set_margin_bottom(20)
        
        # Header (No icon in v2 for this specific widget top)
        label = Gtk.Label(label="SYSTEM PULSE")
        label.get_style_context().add_class("sidebar-section-header")
        label.set_xalign(0)
        self.pack_start(label, False, False, 0)
        
        self.cpu_row = self._add_row("CPU Usage")
        self.gpu_row = self._add_row("GPU VRAM", is_percentage=False, unit="/ 8GB")
        self.ram_row = self._add_row("System RAM", is_percentage=False, unit="/ 32GB")

        # Start Update Loop
        GLib.timeout_add(2000, self.update_stats)
        self.update_stats()

    def _add_row(self, title, is_percentage=True, unit="%"):
        row_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        # Label with value
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        label = Gtk.Label(label=title)
        label.get_style_context().add_class("pulse-label")
        
        val_label = Gtk.Label(label=f"0 {unit}")
        val_label.get_style_context().add_class("pulse-value")
        
        header.pack_start(label, False, False, 0)
        header.pack_end(val_label, False, False, 0)
        row_vbox.pack_start(header, False, False, 0)
        
        # Progress Bar
        bar = Gtk.ProgressBar()
        bar.set_fraction(0.0)
        bar.get_style_context().add_class("pulse-progress")
        row_vbox.pack_start(bar, False, False, 0)
        
        self.pack_start(row_vbox, False, False, 0)
        return {"val_label": val_label, "bar": bar, "unit": unit, "is_perc": is_percentage}

    def update_stats(self):
        """Update system statistics in real-time."""
        try:
            # CPU
            cpu_usage = psutil.cpu_percent()
            self.cpu_row['bar'].set_fraction(cpu_usage / 100.0)
            self.cpu_row['val_label'].set_text(f"{int(cpu_usage)}%")
            
            # RAM
            mem = psutil.virtual_memory()
            total_gb = mem.total / (1024**3)
            used_gb = mem.used / (1024**3)
            self.ram_row['bar'].set_fraction(mem.percent / 100.0)
            self.ram_row['val_label'].set_text(f"{used_gb:.1f} / {total_gb:.0f}GB")
            
            # GPU (Mock if no nvidia-smi)
            # In a real scenario, we might use pynvml
            vram_used = 4.2 # Mock value from design image
            vram_total = 8.0
            self.gpu_row['bar'].set_fraction(vram_used / vram_total)
            self.gpu_row['val_label'].set_text(f"{vram_used:.1f} / {int(vram_total)}GB")
            
        except Exception as e:
            print(f"Error updating stats: {e}")
            
        return True # Keep timeout alive

class NavigationWidget(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.get_style_context().add_class("navigation-widget")
        self.set_margin_top(20)
        
        header = Gtk.Label(label="NAVIGATION")
        header.get_style_context().add_class("sidebar-section-header")
        header.set_xalign(0)
        self.pack_start(header, False, False, 10)
        
        self._add_item("Active Chat", "💬", active=True)
        self._add_item("Model Hub", "⚙")
        self._add_item("Local Files", "📁")
        self._add_item("Kernel Logs", "📄")

    def _add_item(self, text, icon, active=False):
        btn = Gtk.Button()
        btn.get_style_context().add_class("nav-item-btn")
        if active:
            btn.get_style_context().add_class("active")
            
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        
        icon_lbl = Gtk.Label(label=icon)
        icon_lbl.get_style_context().add_class("nav-item-icon")
        
        label = Gtk.Label(label=text)
        label.get_style_context().add_class("nav-item-label")
        
        hbox.pack_start(icon_lbl, False, False, 0)
        hbox.pack_start(label, False, False, 0)
        btn.add(hbox)
        
        self.pack_start(btn, False, False, 0)

class ModelInfoWidget(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.get_style_context().add_class("model-info-widget")
        
        lbl = Gtk.Label(label="CURRENT MODEL")
        lbl.get_style_context().add_class("model-info-header")
        lbl.set_xalign(0)
        self.pack_start(lbl, False, False, 0)
        
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        card.get_style_context().add_class("model-info-card")
        
        name = Gtk.Label(label="Llama-3-8B-Instruct")
        name.get_style_context().add_class("model-info-name")
        name.set_xalign(0)
        
        meta = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        status = Gtk.Label(label="Stable")
        status.get_style_context().add_class("model-info-status")
        
        ver = Gtk.Label(label="v1.2.4-stable")
        ver.get_style_context().add_class("model-info-version")
        
        meta.pack_start(status, False, False, 0)
        meta.pack_end(ver, False, False, 0)
        
        card.pack_start(name, False, False, 0)
        card.pack_start(meta, False, False, 0)
        
        self.pack_start(card, False, False, 10)

class ActiveContextWidget(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.get_style_context().add_class("active-context-widget")
        self.set_margin_top(15)
        self.set_margin_bottom(15)
        self.set_margin_start(15)
        self.set_margin_end(15)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        icon = Gtk.Label(label="⠿")
        icon.get_style_context().add_class("widget-icon-small")
        label = Gtk.Label(label="ACTIVE CONTEXT")
        label.get_style_context().add_class("sidebar-widget-header")
        
        header.pack_start(icon, False, False, 8)
        header.pack_start(label, False, False, 0)
        self.pack_start(header, False, False, 10)

        # Model Indicator
        self.model_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.model_box.get_style_context().add_class("model-context-box")
        
        brain_icon = Gtk.Label(label="🧠") # Replace with proper icon name if possible
        brain_icon.get_style_context().add_class("model-icon")
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.model_name = Gtk.Label(label="Llama 3 (8B)")
        self.model_name.get_style_context().add_class("model-name-label")
        self.model_name.set_xalign(0)
        
        model_type = Gtk.Label(label="Local Instance")
        model_type.get_style_context().add_class("model-type-label")
        model_type.set_xalign(0)
        
        vbox.pack_start(self.model_name, False, False, 0)
        vbox.pack_start(model_type, False, False, 0)
        
        self.model_box.pack_start(brain_icon, False, False, 0)
        self.model_box.pack_start(vbox, True, True, 0)
        self.pack_start(self.model_box, False, False, 0)

        # File list
        self.files_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self._add_file_row("server_logs_apr.log")
        self._add_file_row("/var/log/syslog")
        self.pack_start(self.files_box, False, False, 10)

        # Optimize Button
        opt_btn = Gtk.Button(label="OPTIMIZE RESOURCES")
        opt_btn.get_style_context().add_class("optimize-btn")
        self.pack_end(opt_btn, False, False, 10)

    def _add_file_row(self, filename):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        icon = Gtk.Image.new_from_icon_name("text-x-generic-symbolic", Gtk.IconSize.MENU)
        icon.get_style_context().add_class("file-icon")
        label = Gtk.Label(label=filename)
        label.get_style_context().add_class("file-label")
        label.set_xalign(0)
        
        row.pack_start(icon, False, False, 0)
        row.pack_start(label, True, True, 0)
        self.files_box.pack_start(row, False, False, 0)

class SnippetWidget(Gtk.Box):
    def __init__(self, code, path=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.get_style_context().add_class("snippet-widget")
        self.set_margin_top(10)
        self.set_margin_bottom(10)
        
        # Code container
        code_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        code_box.get_style_context().add_class("snippet-code-box")
        
        label = Gtk.Label(label=code)
        label.get_style_context().add_class("snippet-code-text")
        label.set_xalign(0)
        label.set_selectable(True)
        code_box.pack_start(label, False, False, 15)
        self.pack_start(code_box, False, False, 0)
        
        # Buttons
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        exec_btn = Gtk.Button(label="Execute Snippet")
        exec_btn.get_style_context().add_class("snippet-btn-primary")
        btn_box.pack_start(exec_btn, False, False, 0)
        
        if path:
            open_btn = Gtk.Button(label="Open Path")
            open_btn.get_style_context().add_class("snippet-btn-secondary")
            btn_box.pack_start(open_btn, False, False, 0)
            
        self.pack_start(btn_box, False, False, 0)

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
            widget = SystemPulseWidget(data['cpu'], data['gpu'], data['vram'])
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
        elif data and data.get("type") == "snippet":
            widget = SnippetWidget(data.get("code"), data.get("path"))
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

        # --- COMMAND CENTER HEADER ---
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        header.get_style_context().add_class("command-header")
        
        # Brand/Title Group (Left)
        brand_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        logo = Gtk.Label(label="⚡")
        logo.get_style_context().add_class("brand-logo")
        
        title_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        title_label = Gtk.Label(label="AVA COMMAND CENTER")
        title_label.get_style_context().add_class("brand-title")
        title_label.set_xalign(0)
        
        status_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        status_dot = Gtk.Label(label="●")
        status_dot.get_style_context().add_class("engine-status-dot")
        self.engine_status_lbl = Gtk.Label(label="LOCAL-FIRST LLM ACTIVE")
        self.engine_status_lbl.get_style_context().add_class("engine-status-text")
        status_hbox.pack_start(status_dot, False, False, 0)
        status_hbox.pack_start(self.engine_status_lbl, False, False, 0)
        
        title_vbox.pack_start(title_label, False, False, 0)
        title_vbox.pack_start(status_hbox, False, False, 0)
        
        brand_box.pack_start(logo, False, False, 0)
        brand_box.pack_start(title_vbox, False, False, 0)
        header.pack_start(brand_box, False, False, 0)
        
        # System Controls (Right)
        ctrl_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        
        settings_btn = Gtk.Button()
        settings_btn.add(Gtk.Label(label="⚙"))
        settings_btn.get_style_context().add_class("header-ctrl-btn")
        settings_btn.connect("clicked", self.on_security_clicked)
        ctrl_box.pack_start(settings_btn, False, False, 0)
        
        layout_btn = Gtk.Button()
        layout_btn.add(Gtk.Label(label="❐"))
        layout_btn.get_style_context().add_class("header-ctrl-btn")
        ctrl_box.pack_start(layout_btn, False, False, 0)
        
        close_btn = Gtk.Button()
        close_btn.add(Gtk.Label(label="✕"))
        close_btn.get_style_context().add_class("header-ctrl-btn")
        close_btn.get_style_context().add_class("close-btn")
        close_btn.connect("clicked", lambda _: Gtk.main_quit())
        ctrl_box.pack_start(close_btn, False, False, 0)
        
        # User Avatar (Mock)
        avatar = Gtk.Label(label="👤")
        avatar.get_style_context().add_class("header-avatar")
        ctrl_box.pack_start(avatar, False, False, 5)
        
        header.pack_end(ctrl_box, False, False, 0)
        self.main_box.pack_start(header, False, False, 0)

        # --- BODY (HORIZONTAL) ---
        self.body_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.main_box.pack_start(self.body_box, True, True, 0)

        # --- SIDEBAR (LEFT) ---
        self.sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.sidebar.get_style_context().add_class("sidebar")
        self.sidebar.set_size_request(280, -1)
        
        # Sub-container for padding
        sb_inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        sb_inner.set_margin_start(24)
        sb_inner.set_margin_end(24)
        sb_inner.set_margin_top(20)
        sb_inner.set_margin_bottom(20)
        
        sb_inner.pack_start(SystemPulseWidget(), False, False, 0)
        sb_inner.pack_start(NavigationWidget(), False, False, 0)
        
        # Spacer to push model info to bottom
        spacer = Gtk.Box()
        sb_inner.pack_start(spacer, True, True, 0)
        
        sb_inner.pack_start(ModelInfoWidget(), False, False, 0)
        
        self.sidebar.pack_start(sb_inner, True, True, 0)
        self.body_box.pack_start(self.sidebar, False, False, 0)

        # --- CHAT AREA (RIGHT) ---
        chat_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.body_box.pack_start(chat_container, True, True, 0)

        # Session Header
        session_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        session_box.get_style_context().add_class("session-header-box")
        session_label = Gtk.Label(label="SESSION: LINUX ENVIRONMENT OPTIMIZATION")
        session_label.get_style_context().add_class("session-header-text")
        session_box.pack_start(session_label, True, False, 0)
        chat_container.pack_start(session_box, False, False, 20)

        # Conversation Stream
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.set_vexpand(True)
        self.scroll.get_style_context().add_class("conversation-area")
        
        self.chat_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        self.chat_box.set_margin_start(40)
        self.chat_box.set_margin_end(40)
        self.chat_box.set_margin_top(20)
        self.chat_box.set_margin_bottom(20)
        self.scroll.add(self.chat_box)
        
        chat_container.pack_start(self.scroll, True, True, 0)

        # --- FLOATING INPUT AREA ---
        input_wrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        input_wrapper.get_style_context().add_class("floating-input-wrapper")
        
        input_outer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        input_outer.get_style_context().add_class("floating-input-container")
        
        # Left Icons
        for icon in ["⌨", "🔍", "⛶"]:
            lbl = Gtk.Label(label=icon)
            lbl.get_style_context().add_class("input-icon-btn")
            input_outer.pack_start(lbl, False, False, 0)
        
        # Entry
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Ask AVA or run a system command...")
        self.entry.get_style_context().add_class("floating-message-input")
        self.entry.connect("activate", self.on_entry_activated)
        input_outer.pack_start(self.entry, True, True, 0)

        # Right Ctrl+Enter Label
        shortcut_lbl = Gtk.Label(label="CTRL + ENTER")
        shortcut_lbl.get_style_context().add_class("input-shortcut-label")
        input_outer.pack_end(shortcut_lbl, False, False, 10)

        # Send button
        send_btn = Gtk.Button(label="➤") # Or use a proper icon
        send_btn.get_style_context().add_class("floating-send-btn")
        send_btn.connect("clicked", lambda _: self.on_entry_activated(self.entry))
        input_outer.pack_end(send_btn, False, False, 0)
        
        input_wrapper.pack_start(input_outer, False, False, 0)
        
        # Bottom Badges
        badges_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=25)
        badges_box.get_style_context().add_class("input-badges-box")
        
        self._add_badge(badges_box, "⚡", "LOW LATENCY MODE")
        self._add_badge(badges_box, "🛡", "ENCRYPTED LOCAL STORAGE")
        self._add_badge(badges_box, "📚", "RAG: DESKTOP DOCS")
        
        input_wrapper.pack_start(badges_box, False, False, 15)
        chat_container.pack_end(input_wrapper, False, False, 20)
        
        self.show_all()
        
        # Schedule Startup Checks
        GLib.idle_add(self.check_startup_permissions)

        # --- FLOATING INPUT AREA ---
        input_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        input_vbox.get_style_context().add_class("floating-input-wrapper")
        
        input_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        input_container.get_style_context().add_class("floating-input-container")
        
        # Left Icons
        for icon_char in ["⌨", "🔍", "👁"]:
            btn = Gtk.Label(label=icon_char)
            btn.get_style_context().add_class("input-icon-btn")
            input_container.pack_start(btn, False, False, 0)
        
        # Entry
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Press / for commands or ask AVA anything...")
        self.entry.get_style_context().add_class("floating-message-input")
        self.entry.connect("activate", self.on_entry_activated)
        input_container.pack_start(self.entry, True, True, 0)

        # Send button
        send_btn = Gtk.Button(label="↑")
        send_btn.get_style_context().add_class("floating-send-btn")
        send_btn.connect("clicked", lambda _: self.on_entry_activated(self.entry))
        input_container.pack_end(send_btn, False, False, 0)
        
        input_vbox.pack_start(input_container, False, False, 0)
        chat_container.pack_end(input_vbox, False, False, 30)

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

    def _add_badge(self, box, icon, text):
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        icon_lbl = Gtk.Label(label=icon)
        icon_lbl.get_style_context().add_class("badge-icon")
        text_lbl = Gtk.Label(label=text)
        text_lbl.get_style_context().add_class("badge-text")
        
        hbox.pack_start(icon_lbl, False, False, 0)
        hbox.pack_start(text_lbl, False, False, 0)
        box.pack_start(hbox, False, False, 0)

    def update_orb(self, state):
        GLib.idle_add(self._do_update_orb, state)

    def _do_update_orb(self, state):
        # The 'orb' widget was removed in v2.
        # We can update the status text in the header instead.
        status_map = {
            "listening": "Listening...",
            "thinking": "Thinking...",
            "speaking": "Speaking...",
            None: "LOCAL-FIRST LLM ACTIVE"
        }
        status_text = status_map.get(state, "LOCAL-FIRST LLM ACTIVE")
        # In v2, 'engine-status-text' is what we want to update.
        # We need a reference to it.
        if hasattr(self, 'engine_status_lbl'):
             self.engine_status_lbl.set_text(status_text)
        
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