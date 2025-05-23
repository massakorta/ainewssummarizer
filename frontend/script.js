// Globala variabler för paginering
let isLoading = false;
let currentOffset = 0;
const ARTICLES_PER_PAGE = 20;
const API_URL = "http://localhost:10123"; // Lokal utvecklingsserver

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

async function fetchArticles(offset = 0) {
    if (isLoading) return;
    isLoading = true;

    try {
        const res = await fetch(`${API_URL}/articles?limit=${ARTICLES_PER_PAGE}&offset=${offset}`);
        const articles = await res.json();
        const container = document.getElementById("news-container");
        
        // Rensa containern endast om det är första laddningen
        if (offset === 0) {
            container.innerHTML = "";
        }

        articles.forEach((article) => {
            const li = document.createElement("li");
            li.className = "article";
            li.innerHTML = `
                <h2>${article.swedish_title || article.orignal_title}</h2>
                <div class="short">${article.short_summary}</div>
                <div class="meta">${article.source} • ${formatFriendlyTime(article.date)}</div>
            `;

            li.addEventListener("click", () => {
                const modal = document.getElementById("modal");
                const modalTitle = document.getElementById("modal-title");
                const modalSummary = document.getElementById("modal-summary");
                const modalLink = document.getElementById("modal-link");
                const modalMeta = document.getElementById("modal-meta");
                
                modalTitle.textContent = article.swedish_title || article.orignal_title;
                modalSummary.textContent = article.full_summary;
                modalMeta.textContent = article.source + " • " + new Date(article.date).toLocaleString("sv-SE");
                modalLink.href = article.url;
                
                // Uppdatera URL:en med artikelns titel (för historik)
                const titleSlug = (article.swedish_title || article.orignal_title)
                    .toLowerCase()
                    .replace(/[^a-z0-9]+/g, '-')
                    .replace(/^-+|-+$/g, '');
                history.pushState({ articleId: article.id }, '', `#${titleSlug}`);
                
                modal.classList.remove("hidden");
                document.body.classList.add("no-scroll"); // Lägg till no-scroll klass
                modal.scrollTop = 0; // Återställ scroll-position till toppen
            });

            container.appendChild(li);
        });

        // Uppdatera offset endast om vi fick artiklar
        if (articles.length > 0) {
            currentOffset = offset + articles.length;
        }

        return articles.length;
    } catch (error) {
        console.error("Error fetching articles:", error);
        return 0;
    } finally {
        isLoading = false;
    }
}

// Infinite scroll hantering
function handleScroll() {
    const scrollPosition = window.innerHeight + window.scrollY;
    const bodyHeight = document.documentElement.scrollHeight;
    
    // Ladda mer när vi är nära botten (300px från botten)
    if (scrollPosition > bodyHeight - 300) {
        fetchArticles(currentOffset);
    }
}

// Initiera första laddningen och lägg till scroll-lyssnare
document.addEventListener("DOMContentLoaded", () => {
    fetchArticles();
    
    // Lägg till scroll event listener
    window.addEventListener("scroll", handleScroll);
    
    // Hantera tillbaka-knappen
    const modal = document.getElementById("modal");
    const backButton = document.querySelector(".back-button");
    
    backButton.textContent = "Tillbaka";
    
    backButton.addEventListener("click", () => {
        modal.classList.add("hidden");
        document.body.classList.remove("no-scroll"); // Ta bort no-scroll klass
        history.back();
    });
    
    // Hantera webbläsarens tillbaka-knapp
    window.addEventListener('popstate', () => {
        modal.classList.add("hidden");
        document.body.classList.remove("no-scroll"); // Ta bort no-scroll klass
    });
});