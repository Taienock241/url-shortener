const form = document.querySelector("#shorten-form");
const urlInput = document.querySelector("#url-input");
const shortenButton = document.querySelector("#shorten-button");
const formMessage = document.querySelector("#form-message");
const successCard = document.querySelector("#success-card");
const newShortUrl = document.querySelector("#new-short-url");
const newOriginalUrl = document.querySelector("#new-original-url");
const copyButton = document.querySelector("#copy-button");
const linksBody = document.querySelector("#links-body");
const linksStatus = document.querySelector("#links-status");
const emptyState = document.querySelector("#empty-state");

function escapeHtml(value) {
  const element = document.createElement("div");
  element.textContent = value;
  return element.innerHTML;
}
function formatDate(value) {
  return new Intl.DateTimeFormat(undefined, {dateStyle: "medium"}).format(new Date(value));
}
function setStats(links) {
  const clicks = links.reduce((total, link) => total + link.click_count, 0);
  document.querySelector("#total-links").textContent = links.length.toLocaleString();
  document.querySelector("#total-clicks").textContent = clicks.toLocaleString();
  document.querySelector("#average-clicks").textContent = links.length ? (clicks / links.length).toFixed(1) : "0.0";
}
function renderLinks(links) {
  linksBody.replaceChildren();
  setStats(links);
  emptyState.hidden = links.length !== 0;
  if (!links.length) { linksStatus.textContent = ""; return; }
  linksStatus.textContent = `${links.length} link${links.length === 1 ? "" : "s"} in your history`;
  links.forEach((link) => {
    const row = document.createElement("tr");
    const original = escapeHtml(link.original_url);
    const short = escapeHtml(link.short_url);
    row.innerHTML = `<td title="${original}"><a class="original-link" href="${original}" target="_blank" rel="noopener">${original}</a></td><td><a class="short-link" href="${short}" target="_blank" rel="noopener">${short}</a></td><td class="date">${formatDate(link.created_at)}</td><td class="clicks">${link.click_count.toLocaleString()}</td><td><button class="row-copy" type="button" aria-label="Copy ${short}" data-copy="${short}">⧉</button></td>`;
    linksBody.append(row);
  });
}
async function readError(response) {
  try {
    const data = await response.json();
    if (Array.isArray(data.detail)) return data.detail.map((item) => item.msg).join(" ");
    return data.detail || "The server could not complete that request.";
  } catch { return "The server could not complete that request."; }
}
async function loadLinks() {
  linksStatus.textContent = "Loading your links…";
  try {
    const response = await fetch("/api/urls?limit=100");
    if (!response.ok) throw new Error(await readError(response));
    renderLinks(await response.json());
  } catch (error) {
    linksStatus.textContent = `Could not load links: ${error.message}`;
    linksBody.replaceChildren(); emptyState.hidden = true; setStats([]);
  }
}
form.addEventListener("submit", async (event) => {
  event.preventDefault(); formMessage.textContent = ""; successCard.hidden = true;
  shortenButton.disabled = true; shortenButton.classList.add("is-loading");
  try {
    const response = await fetch("/api/urls", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({url: urlInput.value})});
    if (!response.ok) throw new Error(await readError(response));
    const link = await response.json();
    newShortUrl.href = link.short_url; newShortUrl.textContent = link.short_url; newOriginalUrl.textContent = link.original_url;
    successCard.hidden = false; urlInput.value = ""; await loadLinks();
  } catch (error) { formMessage.textContent = error.message || "Unable to shorten this URL. Please try again."; }
  finally { shortenButton.disabled = false; shortenButton.classList.remove("is-loading"); }
});
async function copyText(value, button) {
  try {
    await navigator.clipboard.writeText(value);
    const original = button.textContent; button.textContent = "Copied!";
    window.setTimeout(() => { button.textContent = original; }, 1800);
  } catch { formMessage.textContent = "Clipboard access was unavailable. You can copy the link manually."; }
}
copyButton.addEventListener("click", () => copyText(newShortUrl.textContent, copyButton));
linksBody.addEventListener("click", (event) => { const button = event.target.closest("[data-copy]"); if (button) copyText(button.dataset.copy, button); });
document.querySelector("#refresh-button").addEventListener("click", loadLinks);
loadLinks();
