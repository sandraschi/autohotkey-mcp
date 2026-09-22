"""CUA HUD overlay - "CUA at work" blinking red + e-stop button.

Spawning a HUD:
    hud = CuaHUD()
    hud.start()

During operations:
    hud.ensure_focus(hwnd)   # refocus target window

On e-stop:
    if hud.estopped(): raise RuntimeError("CUA cancelled by user")

Shutdown:
    hud.stop()
"""

import logging
import threading
import time
from typing import Any

logger = logging.getLogger(__name__)


class CuaHUD:
    """Always-on-top HUD: blinking red "CUA at work" + e-stop button."""

    def __init__(self):
        self._estop = threading.Event()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._root: Any = None  # tkinter root
        self._label: Any = None
        self._blink_state = False

    def _run(self):
        """Run tkinter loop in background thread."""
        try:
            import tkinter as tk
        except ImportError:
            logger.warning("tkinter not available - HUD disabled")
            return

        root = tk.Tk()
        root.title("")
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-alpha", 0.85)
        root.configure(bg="darkred")
        root.geometry("200x80+50+50")

        # Blinking label
        label = tk.Label(
            root,
            text="CUA at work",
            fg="white",
            bg="darkred",
            font=("Segoe UI", 16, "bold"),
        )
        label.pack(expand=True, fill="both")

        # E-stop button
        btn = tk.Button(
            root,
            text="STOP",
            bg="red",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            activebackground="#cc0000",
            command=self._trigger_estop,
            cursor="hand2",
        )
        btn.pack(pady=(0, 4))

        self._root = root
        self._label = label

        def _check_stop():
            # Tkinter's Tcl interpreter is not thread-safe: quit()/destroy() must
            # run on the thread that owns the mainloop, never from stop()'s caller
            # thread directly (doing so crashes the whole process with
            # "Tcl_AsyncDelete: async handler deleted by the wrong thread").
            # stop() only sets self._stop; this poll, running on the Tk thread via
            # root.after(), is what actually tears the window down.
            if self._stop.is_set():
                try:
                    root.quit()
                    root.destroy()
                except Exception:
                    pass
                return
            root.after(100, _check_stop)

        root.after(100, _check_stop)

        def _blink():
            # Must run on the Tk-owning thread (via root.after, not a separate
            # threading.Thread) -- widget.configure() from another thread is the
            # same class of Tcl-interpreter violation as calling quit()/destroy()
            # cross-thread, and this one ran every 600ms for as long as the HUD
            # was up, making it the likelier source of the async-handler crash.
            if self._stop.is_set():
                return
            try:
                self._blink_state = not self._blink_state
                if self._label and self._label.winfo_exists():
                    fg = "red" if self._blink_state else "white"
                    bg = "white" if self._blink_state else "darkred"
                    self._label.configure(fg=fg, bg=bg)
                    self._root.configure(bg=bg)
            except Exception:
                pass
            root.after(600, _blink)

        root.after(600, _blink)

        try:
            root.mainloop()
        except Exception:
            pass

    def start(self):
        """Launch HUD in background thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._estop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """Signal the HUD to shut down.

        Thread-safe: only sets an Event. Actual Tk teardown happens on the
        HUD's own thread via the _check_stop poll in _run() -- see the note
        there for why calling root.quit()/destroy() from here directly used
        to crash the process.
        """
        self._stop.set()

    def _trigger_estop(self):
        self._estop.set()
        self.stop()

    def estopped(self) -> bool:
        if self._estop.is_set():
            return True
        # Also check if thread died unexpectedly
        if self._thread and not self._thread.is_alive():
            self._estop.set()
            return True
        return False

    def ensure_focus(self, hwnd: int) -> bool:
        """Refocus target window. Returns True if successful."""
        if self.estopped():
            raise RuntimeError("CUA cancelled by user via e-stop")
        try:
            import win32gui

            current = win32gui.GetForegroundWindow()
            if current != hwnd:
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.05)
                return True
            return False
        except Exception as exc:
            logger.warning("ensure_focus failed: %s", exc)
            return False
