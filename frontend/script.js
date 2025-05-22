async function fetchArticles() {
  const res = await fetch("http://localhost:5000/articles");
  const articles = await res.json();
  const container = document.getElementById("news-container");

  if (articles.length === 0) {
    container.innerHTML = "<p>Inga nyheter ännu.</p>";
    return;
  }

  container.innerHTML = "";
  articles.forEach((article) => {
    const box = document.createElement("div");
    box.className = "article";

    box.innerHTML = `
      <h2>${article.swedish_title || article.orignal_title}</h2>
      <p class="source">${article.source} • ${new Date(article.date).toLocaleString("sv-SE")}</p>
      <p class="short">${article.short_summary}</p>
      <details>
        <summary>Visa mer</summary>
        <p>${article.full_summary}</p>
        <a href="${article.url}" target="_blank">Läs originalartikeln</a>
      </details>
    `;

    container.appendChild(box);
  });
}

fetchArticles();
