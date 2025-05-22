function formatFriendlyTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMin = Math.floor(diffMs / 60000);
    const isToday = date.toDateString() === now.toDateString();
  
    const yesterday = new Date();
    yesterday.setDate(now.getDate() - 1);
    const isYesterday = date.toDateString() === yesterday.toDateString();
  
    if (diffMin < 60) {
      return `${diffMin} minuter sedan`;
    }
  
    const time = date.toLocaleTimeString("sv-SE", { hour: "2-digit", minute: "2-digit" });
  
    if (isToday) {
      return time;
    }
  
    if (isYesterday) {
      return `Igår, ${time}`;
    }
  
    const day = date.toISOString().split("T")[0]; // YYYY-MM-DD
    return `${day} ${time}`;
  }

async function fetchArticles() {
    const res = await fetch("https://ainewssummarizer-api.onrender.com/articles");
    const articles = await res.json();
    const container = document.getElementById("news-container");
    const modal = document.getElementById("modal");
    const modalTitle = document.getElementById("modal-title");
    const modalSummary = document.getElementById("modal-summary");
    const modalLink = document.getElementById("modal-link");
    const modalMeta = document.getElementById("modal-meta");
    const closeButton = document.querySelector(".close-button");
  
    container.innerHTML = "";
  
    articles.forEach((article) => {
      const li = document.createElement("li");
      li.className = "article";
      li.innerHTML = `
        <h2>${article.swedish_title || article.orignal_title}</h2>
        <div class="short">${article.short_summary}</div>
        <div class="meta">${article.source} • ${formatFriendlyTime(article.date)}</div>
      `;
  
      li.addEventListener("click", () => {
        modalTitle.textContent = article.swedish_title || article.orignal_title;
        modalSummary.textContent = article.full_summary;
        modalMeta.textContent = article.source + " • " + new Date(article.date).toLocaleString("sv-SE");
        modalLink.href = article.url;
        modal.classList.remove("hidden");
      });
  
      container.appendChild(li);
    });
  
    closeButton.addEventListener("click", () => {
      modal.classList.add("hidden");
    });
  
    modal.addEventListener("click", (e) => {
      if (e.target === modal) {
        modal.classList.add("hidden");
      }
    });
  }
  
  fetchArticles();

  // Theme toggle med localStorage
const toggle = document.getElementById("mode-toggle");

// Läs från localStorage vid start
if (localStorage.getItem("theme") === "dark") {
  document.body.classList.add("dark");
}

toggle.addEventListener("click", () => {
  document.body.classList.toggle("dark");
  const theme = document.body.classList.contains("dark") ? "dark" : "light";
  localStorage.setItem("theme", theme);
});