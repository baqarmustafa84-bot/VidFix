document.addEventListener("DOMContentLoaded", () => {
  const input = document.querySelector("input[name='videos']");
  const list = document.querySelector(".file-list");
  if (!input) return;
  input.addEventListener("change", () => {
    list.innerHTML = "";
    [...input.files].forEach((f, i) => {
      const li = document.createElement("li");
      li.textContent = `${i+1}. ${f.name}`;
      list.appendChild(li);
    });
  });
});
