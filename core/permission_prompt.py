import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Handy', '1')
from gi.repository import Gtk, Gdk, Handy, Gio
import sys
import os

class PermissionPrompt(Gtk.Window):
    def __init__(self, skill_name, permission):
        super().__init__(title="AVVA Permission Request")
        Handy.init()
        
        # Window Setup
        self.set_default_size(400, 200)
        self.set_keep_above(True)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # CSS Styling for Premium Look
        css = b"""
        window {
            background-color: #1e1e2e;
            color: #cdd6f4;
            border-radius: 12px;
        }
        .header {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #89b4fa;
        }
        .permission-box {
            background-color: #313244;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .btn-allow {
            background-color: #a6e3a1;
            color: #11111b;
            font-weight: bold;
            padding: 8px 16px;
            border-radius: 6px;
        }
        .btn-deny {
            background-color: #f38ba8;
            color: #11111b;
            font-weight: bold;
            padding: 8px 16px;
            border-radius: 6px;
        }
        """
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        vbox.set_margin_top(20)
        vbox.set_margin_bottom(20)
        vbox.set_margin_start(20)
        vbox.set_margin_end(20)
        self.add(vbox)

        # Title
        title_label = Gtk.Label(label="🛡️ Permission Request")
        title_label.get_style_context().add_class("header")
        vbox.pack_start(title_label, False, False, 0)

        # Message
        msg = f"The skill <b>{skill_name}</b> is requesting the following permission:"
        msg_label = Gtk.Label()
        msg_label.set_markup(msg)
        msg_label.set_line_wrap(True)
        vbox.pack_start(msg_label, False, False, 0)

        # Permission Detail
        perm_box = Gtk.Box()
        perm_box.get_style_context().add_class("permission-box")
        perm_label = Gtk.Label(label=f"🔑 {permission}")
        perm_box.pack_start(perm_label, True, True, 10)
        vbox.pack_start(perm_box, False, False, 0)

        # Buttons
        bbox = Gtk.ButtonBox(spacing=10, layout_style=Gtk.ButtonBoxStyle.CENTER)
        
        deny_btn = Gtk.Button(label="Deny")
        deny_btn.get_style_context().add_class("btn-deny")
        deny_btn.connect("clicked", self.on_deny)
        bbox.add(deny_btn)

        allow_btn = Gtk.Button(label="Allow")
        allow_btn.get_style_context().add_class("btn-allow")
        allow_btn.connect("clicked", self.on_allow)
        bbox.add(allow_btn)

        vbox.pack_start(bbox, False, False, 0)

        self.response = None
        self.connect("destroy", Gtk.main_quit)

    def on_allow(self, btn):
        self.response = True
        self.close()

    def on_deny(self, btn):
        self.response = False
        self.close()

def run_prompt(skill, perm):
    win = PermissionPrompt(skill, perm)
    win.show_all()
    Gtk.main()
    return win.response

if __name__ == "__main__":
    if len(sys.argv) > 2:
        res = run_prompt(sys.argv[1], sys.argv[2])
        # Exit with code 0 for Allow, 1 for Deny
        sys.exit(0 if res else 1)
    else:
        print("Usage: permission_prompt.py <skill_name> <permission>")
        sys.exit(2)
