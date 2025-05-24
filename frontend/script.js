// Globala variabler för paginering
let isLoading = false;
let currentOffset = 0;
const ARTICLES_PER_PAGE = 20;

// Välj API URL baserat på om vi kör lokalt eller inte
const API_URL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://localhost:10123"  // Lokal utvecklingsserver
    : "https://ainewssummarizer-api.onrender.com";  // Produktionsserver

function formatFriendlyTime(dateString) {
    if (!dateString) return "";
    
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return "";
    
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
  
    return date.toLocaleDateString("sv-SE", { 
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit"
    });
}

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function getCategoryClass(category) {
    const validCategories = [
        'kultur', 'politik', 'hälsa', 'sport', 'miljö', 
        'mode', 'utbildning', 'forskning', 'hem, kök och trädgård', 
        'utrikes', 'ekonomi', 'film', 'hållbarhet', 'teknik', 'övrigt'
    ];
    
    // Normalisera kategorin för CSS-klass användning
    const normalizedCategory = category.toLowerCase()
        .replace(/[,\s]+/g, '-')  // Ersätt komma och mellanslag med bindestreck
        .replace(/[åä]/g, 'a')    // Ersätt å och ä med a
        .replace(/ö/g, 'o');      // Ersätt ö med o
    
    return validCategories.includes(category) 
        ? `category-${normalizedCategory}` 
        : 'category-default';
}

async function fetchArticles(offset = 0) {
    if (isLoading) return;
    isLoading = true;

    const container = document.getElementById("news-container");
    
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 sekunders timeout
        
        const res = await fetch(`${API_URL}/articles?limit=${ARTICLES_PER_PAGE}&offset=${offset}`, {
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        
        const articles = await res.json();
        
        // Rensa containern endast om det är första laddningen
        if (offset === 0) {
            container.innerHTML = "";
        }

        if (articles.length === 0 && offset === 0) {
            container.innerHTML = `
                <div class="error-message">
                    <h2>Inga artiklar hittades</h2>
                    <p>Det finns inga artiklar att visa just nu.</p>
                </div>`;
            return 0;
        }

        articles.forEach((article) => {
            const li = document.createElement("li");
            li.className = "article";
            li.dataset.source = article.source;
            const categoryClass = getCategoryClass(article.category);
            li.innerHTML = `
                <div class="category-tag ${categoryClass}">${capitalizeFirstLetter(article.category)}</div>
                <h2>${article.swedish_title || article.original_title}</h2>
                <div class="short">${article.short_summary}</div>
                <div class="meta">${formatFriendlyTime(article.published)}</div>
            `;

            li.addEventListener("click", () => {
                const modal = document.getElementById("modal");
                const modalTitle = document.getElementById("modal-title");
                const modalSummary = document.getElementById("modal-summary");
                const modalLink = document.getElementById("modal-link");
                const modalMeta = document.getElementById("modal-meta");
                const modalCategory = document.getElementById("modal-category");
                const modalKeywords = document.getElementById("modal-keywords");
                
                modalTitle.textContent = article.swedish_title || article.original_title;
                modalSummary.textContent = article.full_summary;
                modalMeta.textContent = article.source + (article.published ? ` • ${new Date(article.published).toLocaleString("sv-SE")}` : "");
                modalLink.href = article.url;
                modalCategory.textContent = capitalizeFirstLetter(article.category);
                modalCategory.className = `category-tag ${getCategoryClass(article.category)}`;
                
                // Hantera nyckelord
                if (article.keywords && article.keywords.length > 0) {
                    const keywordTags = article.keywords
                        .map(keyword => `<span class="keyword-tag">${capitalizeFirstLetter(keyword)}</span>`)
                        .join("");
                    modalKeywords.innerHTML = keywordTags;
                    modalKeywords.style.display = "block";
                } else {
                    modalKeywords.style.display = "none";
                }
                
                // Uppdatera URL:en med artikelns titel (för historik)
                const titleSlug = (article.swedish_title || article.original_title)
                    .toLowerCase()
                    .replace(/[åä]/g, 'a')
                    .replace(/ö/g, 'o')
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
        
        // Visa felmeddelande endast om det är första laddningen
        if (offset === 0) {
            container.innerHTML = `
                <div class="error-message">
                    <h2>Kunde inte ladda artiklar</h2>
                    <p>${error.name === 'AbortError' 
                        ? 'Servern svarar inte. Försök igen om en stund.' 
                        : 'Ett fel uppstod när artiklarna skulle hämtas. Försök igen senare.'}</p>
                    <button onclick="retryLoad()" class="retry-button">Försök igen</button>
                </div>`;
        }
        return 0;
    } finally {
        isLoading = false;
    }
}

function retryLoad() {
    fetchArticles(0);
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