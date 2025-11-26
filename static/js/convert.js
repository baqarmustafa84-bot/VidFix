document.addEventListener("DOMContentLoaded", () => {
  const select = document.querySelector("select[name='format']");
  if (!select) return;
  const hint = document.createElement("div");
  hint.className = "info-hint";
  select.parentElement.appendChild(hint);
  const info = {
    mp3: "MP3 — widely supported, good for music and speech.",
    wav: "WAV — uncompressed, large file size.",
    aac: "AAC — efficient, good quality for streaming.",
    m4a: "M4A — Apple-friendly container."
  };
  const update = () => hint.textContent = info[select.value] || "";
  select.addEventListener("change", update);
  update();
});
