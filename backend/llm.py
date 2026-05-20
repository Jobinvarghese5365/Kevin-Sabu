from __future__ import annotations

import json
import os
from typing import Any

import requests
from requests.exceptions import Timeout

from backend.models import ResearchResult, SocialLinks

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent"
)


def _build_prompt(brand_name: str, region: str) -> str:
    return f"""
You are a precise brand researcher.
Return ONLY valid JSON with this exact shape.
Format constraints:
- The response MUST be a JSON object (first non-whitespace char is '{{' and last non-whitespace char is '}}').
- No markdown and no surrounding text.
{{
  "official_brand_name": "string",
  "parent_organisation": "string",
  "terms_conditions": "https://...",
  "privacy_policy": "https://...",
  "description": "2 sentence factual summary",
  "social_media": {{
    "facebook": "https://...",
    "instagram": "https://...",
    "youtube": "https://..."
  }},
  "logo_url": "https://...png or https://...jpg"
}}

Research brand/product: "{brand_name}"
Region focus: "{region}".

Rules:
- prefer official sources
- do not invent links
- use empty string if uncertain
- parent_organisation must be plain company name only
""".strip()


def _clean_parent_org(parent: str) -> str:
    base = (parent or "").strip().lower()
    return f"{base}-_org" if base else ""


def _extract_text(payload: dict[str, Any]) -> str:
    candidates = payload.get("candidates") or []
    if not candidates:
        raise ValueError("Gemini returned no candidates.")
    parts = (candidates[0].get("content") or {}).get("parts") or []
    return "".join(str(p.get("text", "")) for p in parts).strip()


def _strip_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()
        return "\n".join(lines[1:-1]).strip()
    return text


def _extract_json_object(text: str) -> str:
    """
    Gemini may return whitespace or extra text around the JSON.
    Try to isolate the outermost JSON object.
    """
    if text is None:
        return ""
    t = str(text).strip()
    if not t:
        return ""

    # Handle trivial fenced responses.
    t = _strip_fence(t).strip()
    if not t:
        return ""

    start = t.find("{")
    end = t.rfind("}")
    if start != -1 and end != -1 and end > start:
        return t[start : end + 1].strip()
    return t


def _parse_json_response(raw_text: str) -> dict[str, Any]:
    json_text = _extract_json_object(raw_text)
    if not json_text:
        raise ValueError("Gemini returned an empty response (no JSON detected).")
    try:
        parsed = json.loads(json_text)
    except json.JSONDecodeError as exc:
        snippet = str(raw_text).strip()[:500].replace("\n", " ")
        raise ValueError(
            f"Failed to parse Gemini JSON: {exc}. Raw (first 500 chars): {snippet}"
        ) from exc
    if not isinstance(parsed, dict):
        raise ValueError("Gemini JSON was not a top-level object.")
    return parsed


def research_brand(brand_name: str, region: str) -> ResearchResult:
    api_key = (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()
    if not api_key:
        raise ValueError("Missing Gemini key. Set GEMINI_API_KEY or GOOGLE_API_KEY.")

    url = f"{GEMINI_URL}?key={api_key}"
    generation_config = {
        # Keep responses small and fast to reduce timeouts.
        "temperature": 0.15,
        # Must be large enough to output the full JSON object.
        "maxOutputTokens": 2048,
        # Ask Gemini to return JSON (reduces invalid JSON issues).
        "responseMimeType": "application/json",
    }

    def _request(prompt_text: str) -> dict[str, Any]:
        body = {
            "contents": [{"parts": [{"text": prompt_text}]}],
            "generationConfig": generation_config,
        }
        try:
            response = requests.post(url, json=body, timeout=90)
        except Timeout as exc:
            raise ValueError(
                "Gemini request timed out (took longer than 90s). "
                "Please try again in a moment or simplify the query."
            ) from exc
        response.raise_for_status()
        raw_text = _extract_text(response.json())
        return _parse_json_response(raw_text)

    prompt = _build_prompt(brand_name=brand_name, region=region)
    try:
        data = _request(prompt)
    except ValueError:
        # If Gemini returned malformed JSON, retry once with a stricter instruction.
        strict_prompt = (
            _build_prompt(brand_name=brand_name, region=region)
            + "\n\nSTRICT MODE: Your previous response was not valid JSON. "
            + "Return ONLY a valid JSON object with correct quoting and no extra text. "
            + "If you cannot verify a URL, set it to \"\"."
        )
        data = _request(strict_prompt)

    social = data.get("social_media") or {}
    result = ResearchResult(
        official_brand_name=str(data.get("official_brand_name", "") or ""),
        parent_organisation=_clean_parent_org(str(data.get("parent_organisation", "") or "")),
        terms_conditions=str(data.get("terms_conditions", "") or ""),
        privacy_policy=str(data.get("privacy_policy", "") or ""),
        description=str(data.get("description", "") or ""),
        social_media=SocialLinks(
            facebook=str(social.get("facebook", "") or ""),
            instagram=str(social.get("instagram", "") or ""),
            youtube=str(social.get("youtube", "") or ""),
        ),
        logo_url=str(data.get("logo_url", "") or ""),
    )
    return result

