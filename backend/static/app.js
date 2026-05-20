const REGIONS = ["India", "USA", "Indonesia", "Malaysia"];

function $(id) {
  return document.getElementById(id);
}

function setStatus(text, isError = false) {
  const el = $("status");
  el.textContent = text;
  el.classList.toggle("error", isError);
}

function currentBrand() {
  return $("brandName").value.trim();
}

function currentRegion() {
  return $("region").value.trim();
}

function googleQueryFor(fieldId) {
  const b = currentBrand();
  const r = currentRegion();
  switch (fieldId) {
    case "official_brand_name":
      return `${b} ${r} official brand name`;
    case "parent_organisation":
      return `${b} ${r} parent organisation`;
    case "terms_conditions":
      return `${b} ${r} terms and conditions`;
    case "privacy_policy":
      return `${b} ${r} privacy policy`;
    case "description":
      return `${b} ${r} brand description`;
    case "facebook":
      return `${b} ${r} official facebook page`;
    case "instagram":
      return `${b} ${r} official instagram profile`;
    case "youtube":
      return `${b} ${r} official youtube channel`;
    case "logo_url":
      return `${b} ${r} logo png jpg`;
    default:
      return `${b} ${r} ${fieldId}`;
  }
}

function openGoogle(query) {
  window.open(`https://www.google.com/search?q=${encodeURIComponent(query)}`, "_blank");
}

async function research() {
  const brand = currentBrand();
  const region = currentRegion();

  if (!brand) {
    setStatus("Please enter a brand/product name.", true);
    return;
  }

  const btn = $("researchBtn");
  btn.disabled = true;
  setStatus("Research in progress...");

  try {
    const res = await fetch("/research", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ brand_name: brand, region }),
    });

    const payload = await res.json();
    if (!res.ok) {
      throw new Error(payload?.detail || "Request failed");
    }

    $("official_brand_name").value = payload.official_brand_name || "";
    $("parent_organisation").value = payload.parent_organisation || "";
    $("terms_conditions").value = payload.terms_conditions || "";
    $("privacy_policy").value = payload.privacy_policy || "";
    $("description").value = payload.description || "";

    const social = payload.social_media || {};
    $("facebook").value = social.facebook || "";
    $("instagram").value = social.instagram || "";
    $("youtube").value = social.youtube || "";
    $("logo_url").value = payload.logo_url || "";

    setStatus("Research complete.");
  } catch (e) {
    setStatus(`Error: ${e.message || e}`, true);
  } finally {
    btn.disabled = false;
  }
}

async function copyField(fieldId) {
  const el = $(fieldId);
  const value = (el?.value || "").trim();
  if (!value) {
    setStatus("Nothing to copy.", true);
    return;
  }
  await navigator.clipboard.writeText(value);
  setStatus("Copied.");
}

function initTheme() {
  const saved = localStorage.getItem("theme") || "dark";
  document.documentElement.setAttribute("data-theme", saved);
  $("themeToggle").addEventListener("click", () => {
    const cur = document.documentElement.getAttribute("data-theme") || "dark";
    const next = cur === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
  });
}

function bindButtons() {
  $("researchBtn").addEventListener("click", research);

  document.querySelectorAll("[data-copy]").forEach((btn) => {
    btn.addEventListener("click", () => copyField(btn.dataset.copy));
  });

  document.querySelectorAll("[data-search]").forEach((btn) => {
    btn.addEventListener("click", () => openGoogle(googleQueryFor(btn.dataset.search)));
  });
}

function boot() {
  initTheme();
  bindButtons();
  setStatus("Ready.");
}

boot();

