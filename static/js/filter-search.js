// src/js/filter-search.ts
document.addEventListener("DOMContentLoaded", function() {
  let fuseInstance = null;

  // Initialize search
  function initSearch() {
    // Clean up existing instance if it exists
    fuseInstance = new window.Fuse(window.books, {
      keys: ["title", "authors", "tags", "book_description"],
      threshold: 0.4
    });
  }

  // Initialize search on load
  initSearch();

  // Clean up on page unload
  window.addEventListener('unload', () => {
    fuseInstance = null;
  });

  const searchField = document.getElementById(
    "search-field"
  );
  const tagFilters = document.querySelectorAll(".tag-filter");
  const authorFilters = document.querySelectorAll(".author-filter");
  const bookList = document.getElementById("book-gallery");
  function getTagStyle(tag) {
    const normalizedTag = tag.toLowerCase().replace(/\s+/g, "-");
    const colorKey = window.tagMapping[normalizedTag] || "fallback";
    return window.tagStyles[colorKey] || window.tagStyles["fallback"];
  }
  function renderTags(tags) {
    return tags.map((tag) => {
      const style = getTagStyle(tag);
      return `<span class="tag ${style.bg} ${style.text} dark:${style.darkBg} dark:${style.darkText}">${tag}</span>`;
    }).join("");
  }
  function renderBooks(filteredBooks) {
    bookList.innerHTML = "";
    filteredBooks.forEach((book) => {
      const tagsHTML = renderTags(book.tags);
      const bookHTML = `
        <article class="book-card bg-secondary shadow-lg rounded-lg overflow-hidden transition duration-300 ease-in-out transform hover:shadow-xl flex flex-col">
          <!-- Image Container -->
          <div class="h-64 overflow-hidden relative">
            <a href="${book.buy_link || "#"}" class="block w-full h-full">
              <img class="w-full h-full object-contain transition-opacity duration-300"
                   src="${book.cover || "/images/placeholder.jpg"}"
                   onerror="this.onerror=null; this.src='/images/placeholder.jpg'"
                   alt="${book.book_title}"
                   loading="lazy">
            </a>
          </div>
          <!-- Content -->
          <div class="p-4 flex flex-col flex-grow">
            <h2 class="text-xl font-black mb-2 text-primary">
              <a href="${book.buy_link || "#"}" class="hover:underline focus:outline-none focus:ring-2 focus:ring-accent1 rounded">
                ${book.book_title}
              </a>
            </h2>
            <!-- Tags -->
            <div class="flex flex-wrap gap-2">
              ${tagsHTML}
            </div>
          </div>
        </article>
      `;
      bookList.innerHTML += bookHTML;
    });
  }
  function applyFilters() {
    let filteredBooks = window.books;
    const selectedTags = Array.from(tagFilters).filter((checkbox) => checkbox.checked).map((checkbox) => checkbox.value);
    const selectedAuthors = Array.from(authorFilters).filter((checkbox) => checkbox.checked).map((checkbox) => checkbox.value);
    if (selectedTags.length) {
      filteredBooks = filteredBooks.filter(
        (book) => book.tags.some((tag) => selectedTags.includes(tag))
      );
    }
    if (selectedAuthors.length) {
      filteredBooks = filteredBooks.filter(
        (book) => book.authors.some((author) => selectedAuthors.includes(author))
      );
    }
    renderBooks(filteredBooks);
  }
  if (searchField) {
    searchField.addEventListener("input", (event) => {
      const target = event.target;
      const results = fuseInstance.search(target.value);
      const filteredBooks = results.map((result) => result.item);
      renderBooks(filteredBooks);
    });
  }
  tagFilters.forEach(
    (checkbox) => checkbox.addEventListener("change", applyFilters)
  );
  authorFilters.forEach(
    (checkbox) => checkbox.addEventListener("change", applyFilters)
  );
  renderBooks(window.books);
});
//# sourceMappingURL=filter-search.js.map
