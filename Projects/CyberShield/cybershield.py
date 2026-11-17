"""
CyberShield — Cybersecurity File Integrity & Password Safety Toolkit
====================================================================
A Python Tkinter desktop application built as an individual college project.

Modules:
  1. Dashboard     — Project introduction and navigation hub.
  2. File Integrity Checker  — SHA-256 hash generation and reference comparison.
  3. Password Safety Analyzer — Offline password strength scoring with checklist.

Author      : [Kapil M]
Register No : [RA2511030010209]
Institution : [SRMIST]
Date        : 27/10/2026

Libraries used:
  tkinter / ttk  — GUI framework (standard library)
  hashlib        — SHA-256 hashing (standard library)
  json           — Storing reference hashes (standard library)
  pathlib        — Cross-platform file paths (standard library)
  re             — Regular expressions for password analysis (standard library)
"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import hashlib
import json
import re
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

# ---------------------------------------------------------------------------
# Application-wide constants  (colours, fonts, sizes)
# ---------------------------------------------------------------------------

# Colour palette
BG_DARK       = "#0D1117"   # main window background (near-black navy)
BG_PANEL      = "#161B22"   # panel / card background
BG_HOVER      = "#1C2330"   # subtle hover state
BG_INPUT      = "#0D1117"   # entry widget background
BORDER_COLOR  = "#30363D"   # subtle border lines
ACCENT_TEAL   = "#238636"   # primary accent - teal/green
ACCENT_LIGHT  = "#2EA043"   # lighter accent for hover
TEXT_PRIMARY   = "#E6EDF3"  # main readable text
TEXT_SECONDARY = "#8B949E"  # dimmed labels / metadata
TEXT_MUTED     = "#484F58"  # very dim, decorative
TEXT_SUCCESS   = "#3FB950"  # success / OK messages
TEXT_WARNING   = "#D29922"  # warnings
TEXT_ERROR     = "#F85149"  # errors
TEXT_INFO      = "#58A6FF"  # informational blue
HIGHLIGHT_BG   = "#1F6FEB"  # selected / active highlight

# Typography
FONT_TITLE  = ("Segoe UI", 20, "bold")
FONT_HEAD   = ("Segoe UI", 13, "bold")
FONT_SUB    = ("Segoe UI", 11, "bold")
FONT_BODY   = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 9)
FONT_MONO   = ("Consolas", 10)
FONT_MONO_S = ("Consolas", 9)

# Layout
PAD    = 16
PAD_S  = 8
PAD_XS = 4

# Reference hash file stored alongside the script
REFERENCE_FILE = Path(__file__).parent / "hash_references.json"


# ===========================================================================
# Utility helpers
# ===========================================================================

def sha256_of_file(filepath: Path) -> str:
    """
    Compute the SHA-256 hash of a file in 64 KB chunks.
    This avoids loading the entire file into memory at once.
    Returns the 64-character lowercase hex string.
    """
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_references() -> dict:
    """
    Load saved reference hashes from hash_references.json.
    Returns an empty dict if the file is missing or invalid.

    JSON structure:
      {
        "/path/to/file": {
            "hash": "<64-char sha256 hex>",
            "saved_at": "YYYY-MM-DD HH:MM:SS"
        }
      }
    """
    if not REFERENCE_FILE.exists():
        return {}
    try:
        with open(REFERENCE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {}
        return data
    except (json.JSONDecodeError, OSError):
        return {}


def save_reference(filepath: Path, file_hash: str) -> None:
    """Save or update a reference hash entry for the given file path."""
    import datetime
    refs = load_references()
    refs[str(filepath)] = {
        "hash": file_hash,
        "saved_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(REFERENCE_FILE, "w", encoding="utf-8") as f:
        json.dump(refs, f, indent=2)


def analyze_password(password: str) -> dict:
    """
    Structural strength analysis of a password string.

    Returns a dict with individual check results, a score (0-7),
    a human-readable label, and improvement suggestions.

    NOTE: This is an educational estimate only.
    """
    COMMON_PASSWORDS = {
        "password", "123456", "12345678", "qwerty", "abc123", "111111",
        "password1", "iloveyou", "admin", "letmein", "monkey", "1234567890",
        "sunshine", "princess", "welcome", "shadow", "dragon", "master",
        "pass", "test", "1234", "12345", "password123",
    }

    length        = len(password)
    length_ok     = length >= 8
    length_strong = length >= 12
    has_upper     = bool(re.search(r"[A-Z]", password))
    has_lower     = bool(re.search(r"[a-z]", password))
    has_digit     = bool(re.search(r"\d", password))
    has_special   = bool(re.search(r"[^A-Za-z0-9]", password))
    no_common     = password.lower() not in COMMON_PASSWORDS

    score = sum([length_ok, length_strong, has_upper, has_lower,
                 has_digit, has_special, no_common])

    if score <= 2:
        label = "Very Weak";  label_color = TEXT_ERROR
    elif score <= 3:
        label = "Weak";       label_color = TEXT_WARNING
    elif score <= 4:
        label = "Fair";       label_color = "#E3B341"
    elif score <= 5:
        label = "Good";       label_color = TEXT_SUCCESS
    else:
        label = "Strong";     label_color = TEXT_SUCCESS

    suggestions = []
    if not length_ok:      suggestions.append("Use at least 8 characters.")
    if not length_strong:  suggestions.append("Aim for 12+ characters for stronger security.")
    if not has_upper:      suggestions.append("Add at least one uppercase letter (A-Z).")
    if not has_lower:      suggestions.append("Add at least one lowercase letter (a-z).")
    if not has_digit:      suggestions.append("Include at least one digit (0-9).")
    if not has_special:    suggestions.append("Add a special character (e.g. @, #, $, !).")
    if not no_common:      suggestions.append("Avoid commonly used passwords.")
    if not suggestions:    suggestions.append("Looks good! Consider using a password manager.")

    return {
        "length": length, "score": score,
        "label": label, "label_color": label_color,
        "length_ok": length_ok, "length_strong": length_strong,
        "has_upper": has_upper, "has_lower": has_lower,
        "has_digit": has_digit, "has_special": has_special,
        "no_common": no_common, "suggestions": suggestions,
    }


# ===========================================================================
# Reusable GUI widgets
# ===========================================================================

def make_separator(parent, pady=(0, PAD)):
    """1px horizontal divider line."""
    sep = tk.Frame(parent, height=1, bg=BORDER_COLOR)
    sep.pack(fill="x", pady=pady)
    return sep


def styled_button(parent, text, command, style="primary", **kwargs):
    """Return a styled tk.Button. style = 'primary' | 'secondary' | 'danger'"""
    colours = {
        "primary":   (ACCENT_TEAL,  TEXT_PRIMARY,   ACCENT_LIGHT),
        "secondary": (BG_PANEL,     TEXT_SECONDARY, BG_HOVER),
        "danger":    ("#B91C1C",    TEXT_PRIMARY,   "#EF4444"),
    }
    bg, fg, active_bg = colours.get(style, colours["primary"])
    return tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg, activebackground=active_bg, activeforeground=TEXT_PRIMARY,
        relief="flat", bd=0, padx=PAD, pady=PAD_S, font=FONT_BODY, cursor="hand2",
        **kwargs,
    )


def panel_frame(parent, title=""):
    """
    Create a dark panel with an optional title bar.
    Returns (outer_frame, inner_frame).
    """
    outer = tk.Frame(parent, bg=BG_PANEL, bd=0, relief="flat")
    if title:
        tk.Label(outer, text=title, font=FONT_SUB,
                 bg=BG_PANEL, fg=TEXT_PRIMARY).pack(anchor="w", padx=PAD, pady=(PAD_S, 0))
        tk.Frame(outer, height=1, bg=BORDER_COLOR).pack(fill="x", padx=PAD)
    inner = tk.Frame(outer, bg=BG_PANEL)
    inner.pack(fill="both", expand=True, padx=PAD, pady=PAD_S)
    return outer, inner


# ===========================================================================
# Frame: Dashboard
# ===========================================================================

class DashboardFrame(tk.Frame):
    """Landing screen with navigation to tool modules."""

    def __init__(self, parent, switch_cb, **kwargs):
        super().__init__(parent, bg=BG_DARK, **kwargs)
        self.switch_cb = switch_cb
        self._build()

    def _build(self):
        # Hero
        hero = tk.Frame(self, bg=BG_DARK)
        hero.pack(fill="x", padx=PAD * 2, pady=(PAD * 3, PAD))

        tk.Label(hero, text="CyberShield",
                 font=("Segoe UI", 28, "bold"), bg=BG_DARK, fg=TEXT_PRIMARY).pack(anchor="w")
        tk.Label(hero, text="Cybersecurity File Integrity & Password Safety Toolkit",
                 font=("Segoe UI", 12), bg=BG_DARK, fg=TEXT_SECONDARY).pack(anchor="w", pady=(2, 0))
        make_separator(hero, pady=(PAD_S, 0))

        abstract = (
            "CyberShield is a lightweight, offline desktop utility demonstrating "
            "two core cybersecurity concepts:\n\n"
            "  -  File Integrity Verification: detect whether a file has been tampered "
            "with or corrupted by comparing its SHA-256 hash against a saved reference.\n\n"
            "  -  Password Safety Analysis: evaluate the structural strength of a password "
            "using character-variety checks and provide improvement suggestions.\n\n"
            "Built entirely with the Python standard library. All processing is local."
        )
        tk.Label(hero, text=abstract, font=FONT_BODY, bg=BG_DARK, fg=TEXT_SECONDARY,
                 justify="left", wraplength=700).pack(anchor="w", pady=(PAD, 0))

        # Module cards
        cards_row = tk.Frame(self, bg=BG_DARK)
        cards_row.pack(fill="x", padx=PAD * 2, pady=(PAD * 2, 0))

        self._card(
            cards_row,
            title="File Integrity Checker",
            desc=(
                "Select any file to compute its SHA-256 hash. Save as a trusted "
                "reference, then later verify the file has not changed. Detects "
                "accidental corruption and tampering."
            ),
            btn_text="Open File Integrity Checker  ->",
            cmd=lambda: self.switch_cb("integrity"),
        ).pack(side="left", fill="both", expand=True, padx=(0, PAD_S))

        self._card(
            cards_row,
            title="Password Safety Analyzer",
            desc=(
                "Type a sample password for an instant structural analysis: "
                "length, character variety, and strength score with a checklist. "
                "Passwords are never stored or transmitted."
            ),
            btn_text="Open Password Analyzer  ->",
            cmd=lambda: self.switch_cb("password"),
        ).pack(side="left", fill="both", expand=True, padx=(PAD_S, 0))

        # Status bar
        status = tk.Frame(self, bg=BG_PANEL)
        status.pack(fill="x", side="bottom", pady=(PAD * 2, 0))
        make_separator(status, pady=(0, 0))
        tk.Label(status,
                 text="  Educational tool only. No data leaves your machine. Not a production security product.",
                 font=FONT_SMALL, bg=BG_PANEL, fg=TEXT_MUTED, anchor="w"
                 ).pack(fill="x", padx=PAD, pady=PAD_XS)

    def _card(self, parent, title, desc, btn_text, cmd):
        card = tk.Frame(parent, bg=BG_PANEL, bd=1, relief="flat")
        tk.Frame(card, height=3, bg=ACCENT_TEAL).pack(fill="x")  # accent bar
        inner = tk.Frame(card, bg=BG_PANEL)
        inner.pack(fill="both", expand=True, padx=PAD, pady=PAD)
        tk.Label(inner, text=title, font=FONT_HEAD, bg=BG_PANEL, fg=TEXT_PRIMARY).pack(anchor="w")
        tk.Label(inner, text=desc, font=FONT_BODY, bg=BG_PANEL, fg=TEXT_SECONDARY,
                 justify="left", wraplength=300).pack(anchor="w", pady=(PAD_S, PAD))
        styled_button(inner, btn_text, cmd).pack(anchor="w")
        return card


# ===========================================================================
# Frame: File Integrity Checker
# ===========================================================================

class IntegrityFrame(tk.Frame):
    """SHA-256 file integrity checker with save/compare workflow."""

    def __init__(self, parent, switch_cb, **kwargs):
        super().__init__(parent, bg=BG_DARK, **kwargs)
        self.switch_cb = switch_cb
        self._cur_file  = tk.StringVar()
        self._cur_hash  = tk.StringVar()
        self._status    = tk.StringVar()
        self._cmp_file  = tk.StringVar()
        self._cmp_hash  = tk.StringVar()
        self._cmp_status = tk.StringVar()
        self._build()

    def _build(self):
        # Nav bar
        nav = tk.Frame(self, bg=BG_DARK)
        nav.pack(fill="x", padx=PAD * 2, pady=(PAD, 0))
        styled_button(nav, "<- Back to Dashboard",
                      lambda: self.switch_cb("dashboard"), style="secondary").pack(side="left")

        # Title
        tb = tk.Frame(self, bg=BG_DARK)
        tb.pack(fill="x", padx=PAD * 2, pady=(PAD, 0))
        tk.Label(tb, text="File Integrity Checker", font=FONT_TITLE, bg=BG_DARK, fg=TEXT_PRIMARY).pack(anchor="w")
        tk.Label(tb, text="Compute, save, and verify SHA-256 hashes to detect file changes.",
                 font=FONT_BODY, bg=BG_DARK, fg=TEXT_SECONDARY).pack(anchor="w", pady=(2, 0))
        make_separator(tb, pady=(PAD_S, 0))

        # Scrollable container
        canvas_frame = tk.Frame(self, bg=BG_DARK)
        canvas_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(canvas_frame, bg=BG_DARK, bd=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        self._scroll_frame = tk.Frame(canvas, bg=BG_DARK)

        self._scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self._scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        body = tk.Frame(self._scroll_frame, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=PAD * 2, pady=PAD)

        self._section_compute(body)
        tk.Label(body, text="", bg=BG_DARK).pack()
        self._section_compare(body)
        tk.Label(body, text="", bg=BG_DARK).pack()
        self._section_refs(body)

        # Mouse wheel scrolling
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def _section_compute(self, parent):
        outer, inner = panel_frame(parent, title="Step 1 - Compute Hash")
        outer.pack(fill="x")

        # File row
        fr = tk.Frame(inner, bg=BG_PANEL)
        fr.pack(fill="x", pady=PAD_XS)
        tk.Label(fr, text="File:", font=FONT_BODY, bg=BG_PANEL, fg=TEXT_SECONDARY, width=8, anchor="w").pack(side="left")
        tk.Entry(fr, textvariable=self._cur_file, font=FONT_MONO_S,
                 bg=BG_INPUT, fg=TEXT_SECONDARY, insertbackground=TEXT_PRIMARY,
                 relief="flat", state="readonly").pack(side="left", fill="x", expand=True, padx=(0, PAD_S))
        styled_button(fr, "Browse...", self._browse).pack(side="left")

        # Hash row
        hr = tk.Frame(inner, bg=BG_PANEL)
        hr.pack(fill="x", pady=PAD_XS)
        tk.Label(hr, text="SHA-256:", font=FONT_BODY, bg=BG_PANEL, fg=TEXT_SECONDARY, width=8, anchor="w").pack(side="left")
        tk.Entry(hr, textvariable=self._cur_hash, font=FONT_MONO_S,
                 bg=BG_INPUT, fg=TEXT_INFO, insertbackground=TEXT_PRIMARY,
                 relief="flat", state="readonly").pack(side="left", fill="x", expand=True, padx=(0, PAD_S))
        styled_button(hr, "Copy", self._copy_hash, style="secondary").pack(side="left")

        # Buttons
        br = tk.Frame(inner, bg=BG_PANEL)
        br.pack(fill="x", pady=(PAD_S, PAD_XS))
        styled_button(br, "Compute Hash", self._compute).pack(side="left", padx=(0, PAD_S))
        styled_button(br, "Save as Reference", self._save_ref, style="secondary").pack(side="left", padx=(0, PAD_S))
        styled_button(br, "Reset", self._reset_compute, style="secondary").pack(side="left")

        self._status_lbl = tk.Label(inner, textvariable=self._status,
                                    font=FONT_BODY, bg=BG_PANEL, fg=TEXT_SECONDARY,
                                    anchor="w", justify="left", wraplength=580)
        self._status_lbl.pack(fill="x", pady=(PAD_XS, 0))

    def _section_compare(self, parent):
        outer, inner = panel_frame(parent, title="Step 2 - Compare Against Reference")
        outer.pack(fill="x")

        tk.Label(inner,
                 text=("Select a file to check against its saved reference. "
                       "A match confirms identical content -- it does NOT prove the file is safe "
                       "unless the original reference was from a trusted source."),
                 font=FONT_SMALL, bg=BG_PANEL, fg=TEXT_MUTED,
                 justify="left", wraplength=580, anchor="w").pack(anchor="w", pady=(0, PAD_S))

        fr = tk.Frame(inner, bg=BG_PANEL)
        fr.pack(fill="x", pady=PAD_XS)
        tk.Label(fr, text="File:", font=FONT_BODY, bg=BG_PANEL, fg=TEXT_SECONDARY, width=8, anchor="w").pack(side="left")
        tk.Entry(fr, textvariable=self._cmp_file, font=FONT_MONO_S,
                 bg=BG_INPUT, fg=TEXT_SECONDARY, relief="flat", state="readonly"
                 ).pack(side="left", fill="x", expand=True, padx=(0, PAD_S))
        styled_button(fr, "Browse...", self._browse_cmp).pack(side="left")

        hr = tk.Frame(inner, bg=BG_PANEL)
        hr.pack(fill="x", pady=PAD_XS)
        tk.Label(hr, text="SHA-256:", font=FONT_BODY, bg=BG_PANEL, fg=TEXT_SECONDARY, width=8, anchor="w").pack(side="left")
        tk.Entry(hr, textvariable=self._cmp_hash, font=FONT_MONO_S,
                 bg=BG_INPUT, fg=TEXT_INFO, relief="flat", state="readonly"
                 ).pack(side="left", fill="x", expand=True)

        br = tk.Frame(inner, bg=BG_PANEL)
        br.pack(fill="x", pady=(PAD_S, PAD_XS))
        styled_button(br, "Compare File", self._compare).pack(side="left", padx=(0, PAD_S))
        styled_button(br, "Reset", self._reset_cmp, style="secondary").pack(side="left")

        self._cmp_lbl = tk.Label(inner, textvariable=self._cmp_status,
                                 font=FONT_SUB, bg=BG_PANEL, fg=TEXT_SECONDARY,
                                 anchor="w", justify="left", wraplength=580)
        self._cmp_lbl.pack(fill="x", pady=(PAD_XS, 0))

    def _section_refs(self, parent):
        outer, inner = panel_frame(parent, title="Saved References")
        outer.pack(fill="x")

        styled_button(inner, "Refresh List", self._refresh_refs, style="secondary").pack(anchor="w", pady=(0, PAD_S))

        lf = tk.Frame(inner, bg=BG_PANEL)
        lf.pack(fill="both", expand=True)
        sb = tk.Scrollbar(lf, bg=BG_PANEL, troughcolor=BG_DARK)
        sb.pack(side="right", fill="y")
        self._listbox = tk.Listbox(lf, font=FONT_MONO_S, bg=BG_INPUT, fg=TEXT_SECONDARY,
                                   selectbackground=HIGHLIGHT_BG, selectforeground=TEXT_PRIMARY,
                                   bd=0, relief="flat", height=5, yscrollcommand=sb.set)
        self._listbox.pack(side="left", fill="both", expand=True)
        sb.config(command=self._listbox.yview)
        self._refresh_refs()

    # ── Event handlers ────────────────────────────────────────────────────

    def _browse(self):
        p = filedialog.askopenfilename(title="Select a file to hash")
        if p:
            self._cur_file.set(p)
            self._cur_hash.set("")
            self._status.set("")

    def _compute(self):
        p = self._cur_file.get().strip()
        if not p:
            return self._set_status("No file selected. Click Browse...", TEXT_WARNING)
        path = Path(p)
        if not path.exists():
            return self._set_status(f"File not found: {p}", TEXT_ERROR)
        try:
            h = sha256_of_file(path)
            self._cur_hash.set(h)
            size_kb = path.stat().st_size / 1024
            self._set_status(f"Hash computed successfully.  File size: {size_kb:.1f} KB", TEXT_SUCCESS)
        except PermissionError:
            self._set_status("Permission denied - cannot read this file.", TEXT_ERROR)
        except OSError as e:
            self._set_status(f"Error reading file: {e}", TEXT_ERROR)

    def _copy_hash(self):
        h = self._cur_hash.get()
        if not h:
            return self._set_status("Nothing to copy - compute a hash first.", TEXT_WARNING)
        self.clipboard_clear()
        self.clipboard_append(h)
        self._set_status("Hash copied to clipboard.", TEXT_SUCCESS)

    def _save_ref(self):
        p = self._cur_file.get().strip()
        h = self._cur_hash.get().strip()
        if not p:
            return self._set_status("Select a file first.", TEXT_WARNING)
        if not h:
            return self._set_status("Compute the hash first, then save.", TEXT_WARNING)
        try:
            save_reference(Path(p), h)
            self._set_status(f"Reference saved for: {Path(p).name}", TEXT_SUCCESS)
            self._refresh_refs()
        except OSError as e:
            self._set_status(f"Could not save reference: {e}", TEXT_ERROR)

    def _reset_compute(self):
        self._cur_file.set("")
        self._cur_hash.set("")
        self._status.set("")

    def _browse_cmp(self):
        p = filedialog.askopenfilename(title="Select a file to verify")
        if p:
            self._cmp_file.set(p)
            self._cmp_hash.set("")
            self._cmp_status.set("")
            self._cmp_lbl.config(fg=TEXT_SECONDARY)

    def _compare(self):
        p = self._cmp_file.get().strip()
        if not p:
            return self._set_cmp("No file selected. Click Browse...", TEXT_WARNING)
        path = Path(p)
        if not path.exists():
            return self._set_cmp(f"File not found: {p}", TEXT_ERROR)
        refs = load_references()
        if not refs:
            return self._set_cmp("No saved references found. Use Step 1 to save a reference first.", TEXT_WARNING)
        if str(path) not in refs:
            return self._set_cmp(f"No saved reference for '{path.name}'. Save a reference using Step 1 first.", TEXT_WARNING)
        ref_entry = refs[str(path)]
        if "hash" not in ref_entry or not isinstance(ref_entry["hash"], str):
            return self._set_cmp("Reference entry is malformed. Please re-save the reference.", TEXT_ERROR)
        ref_hash = ref_entry["hash"]
        saved_at = ref_entry.get("saved_at", "unknown date")
        try:
            cur = sha256_of_file(path)
            self._cmp_hash.set(cur)
            if cur == ref_hash:
                self._set_cmp(
                    f"MATCH - File is identical to the reference saved on {saved_at}.\n"
                    "Note: This only confirms content is unchanged, not that the file is safe.",
                    TEXT_SUCCESS
                )
            else:
                self._set_cmp(
                    f"MISMATCH - File content has changed since {saved_at}.\n"
                    "The file may have been modified, corrupted, or replaced.",
                    TEXT_ERROR
                )
        except PermissionError:
            self._set_cmp("Permission denied.", TEXT_ERROR)
        except OSError as e:
            self._set_cmp(f"Error reading file: {e}", TEXT_ERROR)

    def _reset_cmp(self):
        self._cmp_file.set("")
        self._cmp_hash.set("")
        self._cmp_status.set("")
        self._cmp_lbl.config(fg=TEXT_SECONDARY)

    def _refresh_refs(self):
        self._listbox.delete(0, "end")
        refs = load_references()
        if not refs:
            self._listbox.insert("end", "  (no saved references yet)")
            return
        for fp, entry in refs.items():
            name = Path(fp).name
            saved_at = entry.get("saved_at", "")
            h_short = entry.get("hash", "?")[:16]
            self._listbox.insert("end", f"  {name:<28}  {saved_at}  |  {h_short}...")

    def _set_status(self, msg, color=TEXT_SECONDARY):
        self._status.set(msg)
        self._status_lbl.config(fg=color)

    def _set_cmp(self, msg, color=TEXT_SECONDARY):
        self._cmp_status.set(msg)
        self._cmp_lbl.config(fg=color)


# ===========================================================================
# Frame: Password Safety Analyzer
# ===========================================================================

class PasswordFrame(tk.Frame):
    """Offline password structural strength analyzer."""

    CHECK_META = [
        ("length_ok",     "At least 8 characters"),
        ("length_strong", "12+ characters (recommended)"),
        ("has_upper",     "Contains uppercase letters (A-Z)"),
        ("has_lower",     "Contains lowercase letters (a-z)"),
        ("has_digit",     "Contains digits (0-9)"),
        ("has_special",   "Contains special characters (@, #, $, ...)"),
        ("no_common",     "Not a commonly used password"),
    ]

    def __init__(self, parent, switch_cb, **kwargs):
        super().__init__(parent, bg=BG_DARK, **kwargs)
        self.switch_cb = switch_cb
        self._pwd_var  = tk.StringVar()
        self._show_var = tk.BooleanVar(value=False)
        self._build()

    def _build(self):
        nav = tk.Frame(self, bg=BG_DARK)
        nav.pack(fill="x", padx=PAD * 2, pady=(PAD, 0))
        styled_button(nav, "<- Back to Dashboard",
                      lambda: self.switch_cb("dashboard"), style="secondary").pack(side="left")

        tb = tk.Frame(self, bg=BG_DARK)
        tb.pack(fill="x", padx=PAD * 2, pady=(PAD, 0))
        tk.Label(tb, text="Password Safety Analyzer", font=FONT_TITLE, bg=BG_DARK, fg=TEXT_PRIMARY).pack(anchor="w")
        tk.Label(tb, text="Offline structural check. Passwords are never stored or transmitted.",
                 font=FONT_BODY, bg=BG_DARK, fg=TEXT_SECONDARY).pack(anchor="w", pady=(2, 0))
        make_separator(tb, pady=(PAD_S, 0))

        body = tk.Frame(self, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=PAD * 2, pady=PAD)

        self._build_input(body)
        tk.Label(body, text="", bg=BG_DARK).pack()
        self._build_results(body)

    def _build_input(self, parent):
        outer, inner = panel_frame(parent, title="Enter Password to Analyze")
        outer.pack(fill="x")

        tk.Label(inner,
                 text="Use a sample or test password -- not your real account password. "
                      "This is an educational estimate only, not a security guarantee.",
                 font=FONT_SMALL, bg=BG_PANEL, fg=TEXT_WARNING,
                 justify="left", wraplength=580, anchor="w").pack(anchor="w", pady=(0, PAD_S))

        pwd_row = tk.Frame(inner, bg=BG_PANEL)
        pwd_row.pack(fill="x", pady=PAD_XS)
        tk.Label(pwd_row, text="Password:", font=FONT_BODY, bg=BG_PANEL, fg=TEXT_SECONDARY).pack(side="left", padx=(0, PAD_S))

        self._pwd_entry = tk.Entry(
            pwd_row, textvariable=self._pwd_var, show="*",
            font=("Consolas", 12), bg=BG_INPUT, fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY, relief="flat", width=36,
        )
        self._pwd_entry.pack(side="left", padx=(0, PAD_S))
        self._pwd_entry.bind("<Return>", lambda _e: self._analyze())

        def toggle():
            self._pwd_entry.config(show="" if self._show_var.get() else "*")

        tk.Checkbutton(
            pwd_row, text="Show", variable=self._show_var, command=toggle,
            bg=BG_PANEL, fg=TEXT_SECONDARY, selectcolor=BG_INPUT,
            activebackground=BG_PANEL, font=FONT_SMALL, bd=0,
        ).pack(side="left")

        br = tk.Frame(inner, bg=BG_PANEL)
        br.pack(fill="x", pady=(PAD_S, PAD_XS))
        styled_button(br, "Analyze", self._analyze).pack(side="left", padx=(0, PAD_S))
        styled_button(br, "Reset", self._reset, style="secondary").pack(side="left")

    def _build_results(self, parent):
        outer, inner = panel_frame(parent, title="Analysis Results")
        outer.pack(fill="x")

        # Score row
        sr = tk.Frame(inner, bg=BG_PANEL)
        sr.pack(fill="x", pady=(PAD_XS, PAD_S))
        tk.Label(sr, text="Score:", font=FONT_BODY, bg=BG_PANEL, fg=TEXT_SECONDARY).pack(side="left", padx=(0, PAD_S))
        self._score_lbl  = tk.Label(sr, text="--", font=("Segoe UI", 14, "bold"), bg=BG_PANEL, fg=TEXT_MUTED)
        self._score_lbl.pack(side="left")
        self._rating_lbl = tk.Label(sr, text="", font=("Segoe UI", 11), bg=BG_PANEL, fg=TEXT_MUTED)
        self._rating_lbl.pack(side="left", padx=(PAD_S, 0))

        self._len_lbl = tk.Label(inner, text="", font=FONT_SMALL, bg=BG_PANEL, fg=TEXT_SECONDARY, anchor="w")
        self._len_lbl.pack(fill="x")
        make_separator(inner, pady=(PAD_S, PAD_S))

        # Checklist
        tk.Label(inner, text="Checks:", font=FONT_SUB, bg=BG_PANEL, fg=TEXT_SECONDARY, anchor="w").pack(anchor="w")
        cf = tk.Frame(inner, bg=BG_PANEL)
        cf.pack(fill="x", pady=(PAD_XS, PAD_S))
        self._check_lbls = {}
        for key, text in self.CHECK_META:
            row = tk.Frame(cf, bg=BG_PANEL)
            row.pack(fill="x", pady=1)
            lbl = tk.Label(row, text=f"  o  {text}", font=FONT_BODY, bg=BG_PANEL, fg=TEXT_MUTED, anchor="w")
            lbl.pack(anchor="w")
            self._check_lbls[key] = lbl

        make_separator(inner, pady=(PAD_S, PAD_S))

        # Suggestions
        tk.Label(inner, text="Suggestions:", font=FONT_SUB, bg=BG_PANEL, fg=TEXT_SECONDARY, anchor="w").pack(anchor="w")
        self._sugg_lbl = tk.Label(inner, text="Run an analysis to see suggestions.",
                                  font=FONT_BODY, bg=BG_PANEL, fg=TEXT_MUTED,
                                  justify="left", wraplength=560, anchor="w")
        self._sugg_lbl.pack(anchor="w", pady=(PAD_XS, PAD_S))

        # Disclaimer
        tk.Label(inner,
                 text=("Disclaimer: This score reflects structural characteristics only. "
                       "A high score does not make a password unguessable. "
                       "Use a reputable password manager and enable multi-factor authentication."),
                 font=FONT_SMALL, bg=BG_PANEL, fg=TEXT_MUTED,
                 justify="left", wraplength=560, anchor="w").pack(anchor="w", pady=(0, PAD_S))

    # ── Event handlers ────────────────────────────────────────────────────

    def _analyze(self):
        pwd = self._pwd_var.get()
        if not pwd:
            self._score_lbl.config(text="--", fg=TEXT_MUTED)
            self._rating_lbl.config(text="Enter a password above.", fg=TEXT_MUTED)
            self._len_lbl.config(text="")
            self._sugg_lbl.config(text="Type a password and click Analyze.", fg=TEXT_MUTED)
            for lbl in self._check_lbls.values():
                lbl.config(fg=TEXT_MUTED)
            return

        r = analyze_password(pwd)

        self._score_lbl.config(text=f"{r['score']} / 7", fg=r["label_color"])
        self._rating_lbl.config(text=f"({r['label']})", fg=r["label_color"])

        if r["length"] < 8:
            len_note = " -- too short"
        elif r["length"] < 12:
            len_note = " -- acceptable, longer is better"
        else:
            len_note = " -- good length"
        self._len_lbl.config(text=f"Length: {r['length']} characters{len_note}")

        check_texts = {k: t for k, t in self.CHECK_META}
        for key, lbl in self._check_lbls.items():
            passed = r.get(key, False)
            icon   = "v" if passed else "x"
            color  = TEXT_SUCCESS if passed else TEXT_ERROR
            lbl.config(text=f"  [{icon}]  {check_texts[key]}", fg=color)

        sugg = "\n".join(f"  - {s}" for s in r["suggestions"])
        self._sugg_lbl.config(text=sugg, fg=TEXT_SECONDARY)

    def _reset(self):
        self._pwd_var.set("")
        self._show_var.set(False)
        self._pwd_entry.config(show="*")
        self._score_lbl.config(text="--", fg=TEXT_MUTED)
        self._rating_lbl.config(text="", fg=TEXT_MUTED)
        self._len_lbl.config(text="")
        self._sugg_lbl.config(text="Run an analysis to see suggestions.", fg=TEXT_MUTED)
        check_texts = {k: t for k, t in self.CHECK_META}
        for key, lbl in self._check_lbls.items():
            lbl.config(text=f"  o  {check_texts[key]}", fg=TEXT_MUTED)


# ===========================================================================
# Main Application Window
# ===========================================================================

class CyberShieldApp(tk.Tk):
    """Root window managing frame navigation."""

    def __init__(self):
        super().__init__()
        self.title("CyberShield -- Cybersecurity Toolkit")
        self.geometry("860x680")
        self.minsize(800, 600)
        self.configure(bg=BG_DARK)

        container = tk.Frame(self, bg=BG_DARK)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self._frames: dict = {}
        for name, Cls in [("dashboard", DashboardFrame),
                           ("integrity",  IntegrityFrame),
                           ("password",   PasswordFrame)]:
            f = Cls(container, switch_cb=self.show_frame)
            f.grid(row=0, column=0, sticky="nsew")
            self._frames[name] = f

        self.show_frame("dashboard")

    def show_frame(self, name: str):
        f = self._frames.get(name)
        if f:
            f.tkraise()
        else:
            messagebox.showerror("Navigation Error", f"Unknown frame: {name}")


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == "__main__":
    app = CyberShieldApp()
    app.mainloop()
