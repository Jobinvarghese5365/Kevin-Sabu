from __future__ import annotations

import threading
import webbrowser
from typing import Callable
from urllib.parse import quote_plus

import customtkinter as ctk
import requests

REGIONS = ["India", "USA", "Indonesia", "Malaysia"]
API_BASE = "http://127.0.0.1:8000"


def google_url(query: str) -> str:
    return f"https://www.google.com/search?q={quote_plus(query)}"


class BrandResearchDesktopPro(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Brand Research Desktop Pro")
        self.geometry("1020x860")
        self.minsize(900, 700)
        ctk.set_default_color_theme("blue")
        ctk.set_appearance_mode("system")

        self._busy = False
        self._build_ui()

    def _build_ui(self) -> None:
        root = ctk.CTkFrame(self, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(
            root, text="Brand Research Desktop Pro", font=ctk.CTkFont(size=22, weight="bold")
        ).pack(anchor="w")

        controls = ctk.CTkFrame(root)
        controls.pack(fill="x", pady=(12, 8))
        controls.grid_columnconfigure(0, weight=1)
        controls.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(controls, text="Brand/Product Name").grid(
            row=0, column=0, sticky="w", padx=12, pady=(12, 4)
        )
        self.brand_entry = ctk.CTkEntry(controls, placeholder_text="e.g. Nike")
        self.brand_entry.grid(row=1, column=0, columnspan=3, sticky="ew", padx=12, pady=(0, 8))

        ctk.CTkLabel(controls, text="Region").grid(row=2, column=0, sticky="w", padx=12, pady=(4, 4))
        self.region_menu = ctk.CTkComboBox(controls, values=REGIONS, width=220)
        self.region_menu.grid(row=3, column=0, sticky="w", padx=12, pady=(0, 12))
        self.region_menu.set(REGIONS[0])

        self.research_btn = ctk.CTkButton(controls, text="Research Brand", command=self._on_research)
        self.research_btn.grid(row=3, column=2, sticky="e", padx=12, pady=(0, 12))

        self.status = ctk.CTkLabel(root, text="Ready.", text_color="gray")
        self.status.pack(anchor="w", pady=(0, 8))

        results = ctk.CTkScrollableFrame(root, label_text="Research Output")
        results.pack(fill="both", expand=True)

        self.entries: dict[str, ctk.CTkEntry] = {}
        self._add_row(results, "Official Brand Name", "official_brand_name", self._q_brand)
        self._add_row(results, "Parent Organisation", "parent_organisation", self._q_parent)
        self._add_row(results, "Terms & Conditions", "terms_conditions", self._q_terms)
        self._add_row(results, "Privacy Policy", "privacy_policy", self._q_privacy)

        ctk.CTkLabel(results, text="Description").pack(anchor="w", padx=4, pady=(10, 4))
        desc_row = ctk.CTkFrame(results, fg_color="transparent")
        desc_row.pack(fill="x")
        self.description = ctk.CTkTextbox(desc_row, height=140)
        self.description.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(desc_row, text="Copy", width=90, command=self._copy_description).pack(side="left", padx=(0, 6))
        ctk.CTkButton(desc_row, text="Google Search", width=120, command=self._search_description).pack(side="left")

        self._add_row(results, "Facebook", "facebook", self._q_facebook)
        self._add_row(results, "Instagram", "instagram", self._q_instagram)
        self._add_row(results, "YouTube", "youtube", self._q_youtube)
        self._add_row(results, "Logo", "logo_url", self._q_logo)

    def _add_row(
        self,
        parent: ctk.CTkScrollableFrame,
        label: str,
        key: str,
        query_fn: Callable[[], str],
    ) -> None:
        ctk.CTkLabel(parent, text=label).pack(anchor="w", padx=4, pady=(8, 4))
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x")
        entry = ctk.CTkEntry(row)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(row, text="Copy", width=90, command=lambda: self._copy_entry(key)).pack(
            side="left", padx=(0, 6)
        )
        ctk.CTkButton(
            row, text="Google Search", width=120, command=lambda: webbrowser.open(google_url(query_fn()))
        ).pack(side="left")
        self.entries[key] = entry

    def _brand_region(self) -> tuple[str, str]:
        return self.brand_entry.get().strip(), self.region_menu.get().strip()

    def _q_brand(self) -> str:
        b, r = self._brand_region()
        return f"{b} {r} official brand name"

    def _q_parent(self) -> str:
        b, r = self._brand_region()
        return f"{b} {r} parent organisation"

    def _q_terms(self) -> str:
        b, r = self._brand_region()
        return f"{b} {r} terms and conditions"

    def _q_privacy(self) -> str:
        b, r = self._brand_region()
        return f"{b} {r} privacy policy"

    def _q_facebook(self) -> str:
        b, r = self._brand_region()
        return f"{b} {r} official facebook page"

    def _q_instagram(self) -> str:
        b, r = self._brand_region()
        return f"{b} {r} official instagram profile"

    def _q_youtube(self) -> str:
        b, r = self._brand_region()
        return f"{b} {r} official youtube channel"

    def _q_logo(self) -> str:
        b, r = self._brand_region()
        return f"{b} {r} logo png jpg"

    def _set_status(self, text: str, error: bool = False) -> None:
        self.status.configure(text=text, text_color="#ff6b6b" if error else "gray")

    def _set_entry(self, key: str, value: str) -> None:
        e = self.entries[key]
        e.delete(0, "end")
        e.insert(0, value or "")

    def _copy_entry(self, key: str) -> None:
        value = self.entries[key].get().strip()
        if not value:
            self._set_status("Nothing to copy.", error=True)
            return
        self.clipboard_clear()
        self.clipboard_append(value)
        self._set_status("Copied.")

    def _copy_description(self) -> None:
        value = self.description.get("1.0", "end").strip()
        if not value:
            self._set_status("Nothing to copy.", error=True)
            return
        self.clipboard_clear()
        self.clipboard_append(value)
        self._set_status("Copied.")

    def _search_description(self) -> None:
        b, r = self._brand_region()
        webbrowser.open(google_url(f"{b} {r} brand description"))

    def _on_research(self) -> None:
        if self._busy:
            return
        brand, region = self._brand_region()
        if not brand:
            self._set_status("Please enter a brand/product name.", error=True)
            return

        self._busy = True
        self.research_btn.configure(state="disabled")
        self._set_status("Research in progress...")

        def worker() -> None:
            try:
                response = requests.post(
                    f"{API_BASE}/research",
                    json={"brand_name": brand, "region": region},
                    timeout=180,
                )
                response.raise_for_status()
                payload = response.json()
                self.after(0, lambda: self._apply_payload(payload))
            except Exception as exc:
                self.after(0, lambda: self._set_status(f"Error: {exc}", error=True))
            finally:
                self.after(0, self._reset_busy)

        threading.Thread(target=worker, daemon=True).start()

    def _apply_payload(self, payload: dict) -> None:
        self._set_entry("official_brand_name", payload.get("official_brand_name", ""))
        self._set_entry("parent_organisation", payload.get("parent_organisation", ""))
        self._set_entry("terms_conditions", payload.get("terms_conditions", ""))
        self._set_entry("privacy_policy", payload.get("privacy_policy", ""))
        social = payload.get("social_media") or {}
        self._set_entry("facebook", social.get("facebook", ""))
        self._set_entry("instagram", social.get("instagram", ""))
        self._set_entry("youtube", social.get("youtube", ""))
        self._set_entry("logo_url", payload.get("logo_url", ""))
        self.description.delete("1.0", "end")
        self.description.insert("1.0", payload.get("description", ""))
        self._set_status("Research complete.")

    def _reset_busy(self) -> None:
        self._busy = False
        self.research_btn.configure(state="normal")


def run_frontend() -> None:
    app = BrandResearchDesktopPro()
    app.mainloop()


if __name__ == "__main__":
    run_frontend()

