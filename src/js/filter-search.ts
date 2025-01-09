import { Book } from "../types";

declare global {
  interface Window {
    books: Book[];
    Fuse: any; // Consider installing @types/fuse.js for better typing
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const searchField = document.getElementById(
    "search-field",
  ) as HTMLInputElement;
  const tagFilters = document.querySelectorAll<HTMLInputElement>(".tag-filter");
  const authorFilters =
    document.querySelectorAll<HTMLInputElement>(".author-filter");
  const bookList = document.getElementById("book-gallery") as HTMLDivElement; // Updated ID

  const fuse = new window.Fuse(window.books, {
    keys: ["title", "authors", "tags", "book_description"],
    threshold: 0.4,
  });

  function getTagStyle(tag: string): {
    bg: string;
    text: string;
    darkBg: string;
    darkText: string;
  } {
    const normalizedTag = tag.toLowerCase().replace(/\s+/g, "-"); // Assuming urlize replaces spaces with hyphens
    const colorKey = window.tagMapping[normalizedTag] || "fallback";
    return window.tagStyles[colorKey] || window.tagStyles["fallback"];
  }

  function renderTags(tags: string[]): string {
    return tags
      .map((tag) => {
        const style = getTagStyle(tag);
        return `<span class="tag ${style.bg} ${style.text} dark:${style.darkBg} dark:${style.darkText}">${tag}</span>`;
      })
      .join("");
  }

  function renderBooks(filteredBooks: Book[]): void {
    bookList.innerHTML = "";
    filteredBooks.forEach((book) => {
      // Generate Tag HTML using the `renderTags` function
      const tagsHTML = renderTags(book.tags);

      // Construct Book Card HTML
      const bookHTML = `
        <article class="book-card bg-secondary shadow-lg rounded-lg overflow-hidden transition duration-300 ease-in-out transform hover:shadow-xl flex flex-col">
          <!-- Image Container -->
          <div class="h-64 overflow-hidden relative">
            <a href="${book.buy_link || "#"}" class="block w-full h-full">
              <img class="w-full h-full object-contain transition-opacity duration-300"
                   src="${book.cover || "/images/placeholder.webp"}"
                   onerror="this.onerror=null; this.src='/images/placeholder.webp'"
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

  function applyFilters(): void {
    let filteredBooks = window.books;

    const selectedTags = Array.from(tagFilters)
      .filter((checkbox) => checkbox.checked)
      .map((checkbox) => checkbox.value);

    const selectedAuthors = Array.from(authorFilters)
      .filter((checkbox) => checkbox.checked)
      .map((checkbox) => checkbox.value);

    if (selectedTags.length) {
      filteredBooks = filteredBooks.filter((book) =>
        book.tags.some((tag) => selectedTags.includes(tag)),
      );
    }

    if (selectedAuthors.length) {
      filteredBooks = filteredBooks.filter((book) =>
        book.authors.some((author) => selectedAuthors.includes(author)),
      );
    }

    renderBooks(filteredBooks);
  }

  if (searchField) {
    searchField.addEventListener("input", (event) => {
      const target = event.target as HTMLInputElement;
      const results = fuse.search(target.value);
      const filteredBooks = results.map((result: any) => result.item);
      renderBooks(filteredBooks);
    });
  }

  tagFilters.forEach((checkbox) =>
    checkbox.addEventListener("change", applyFilters),
  );
  authorFilters.forEach((checkbox) =>
    checkbox.addEventListener("change", applyFilters),
  );

  renderBooks(window.books);
});
