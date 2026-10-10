# encoding: utf-8
from __future__ import division, print_function, unicode_literals
import objc
import webbrowser
from GlyphsApp import *
from GlyphsApp.plugins import *
from AppKit import NSApp, NSButton

objc_NSObject = objc.lookUpClass("NSObject")

class UnicodeHandler(objc_NSObject):
    def showInUnicodeChecker_(self, sender):
        orig = getattr(self, "_orig", None)
        if orig:
            orig_target, orig_action = orig
            try:
                if not Glyphs.font: return
                layers = Glyphs.font.selectedLayers
                if not layers or len(layers) < 1: return
                glyph = layers[0].parent
                if glyph.script == 'han' and glyph.string:
                    zi = glyph.string
                    zi = zi.encode('utf-8')
                    zi = ''.join(['%%%02X' % b for b in zi])
                    webbrowser.open("https://zi.tools/zi/" + zi)
                else:
                    # sendAction:to:from:
                    NSApp.sendAction_to_from_(orig_action, orig_target, sender)
                return
            except Exception as e:
                NSApp.sendAction_to_from_(orig_action, orig_target, sender)
                return


def find_buttons_with_action(root, needle="showInUnicodeChecker"):
    """Helper function to find buttons with a specific action in a view hierarchy."""
    found = []
    try:
        for v in root.subviews():
            try:
                act = None
                if v.respondsToSelector_("action"):
                    act = v.action()
                act_str = ""
                if act is not None:
                    act_str = act if isinstance(act, str) else str(act)
                if "showInUnicodeChecker" in act_str and (
                    isinstance(v, NSButton) or v.className() == "NSButton"
                ):
                    found.append(v)
            except Exception:
                pass
            try:
                found += find_buttons_with_action(v, needle)
            except Exception:
                pass
    except Exception:
        pass
    return found



class ZiToolsImpact(GeneralPlugin):

    @objc.python_method
    def settings(self):
        self.hooked_handlers = []
        return

    @objc.python_method
    def start(self):
        def hook_current_info_panel(*kwargs):
            if not Glyphs.font or not Glyphs.font.currentTab: return
            iv = Glyphs.font.currentTab.infoView()
            buttons = find_buttons_with_action(iv, "showInUnicodeChecker")

            if not buttons:
                return

            for btn in buttons:
                orig_target = btn.target()
                if isinstance(orig_target, UnicodeHandler):
                    # Already hooked
                    continue
                orig_action = btn.action()
                handler = UnicodeHandler.alloc().init()
                self.hooked_handlers.append(handler)
                handler._orig = (orig_target, orig_action)
                btn.setTarget_(handler)
        Glyphs.addCallback(hook_current_info_panel, UPDATEINTERFACE)
        return

    @objc.python_method
    def __file__(self):
        """Please leave this method unchanged"""
        return __file__
