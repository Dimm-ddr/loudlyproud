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
    // Clear existing content
    while (bookList.firstChild) {
      bookList.removeChild(bookList.firstChild);
    }

    // Create document fragment for batch DOM updates
    const fragment = document.createDocumentFragment();

    filteredBooks.forEach((book) => {
      const article = document.createElement("article");
      article.className =
        "book-card bg-secondary shadow-lg rounded-lg overflow-hidden transition duration-300 ease-in-out transform hover:shadow-xl flex flex-col";

      // Image Container
      const imageContainer = document.createElement("div");
      imageContainer.className = "h-64 overflow-hidden relative";

      const link = document.createElement("a");
      link.href = book.buy_link || "#";
      link.className = "block w-full h-full";

      const img = document.createElement("img");
      img.className =
        "w-full h-full object-contain transition-opacity duration-300";
      img.src = book.cover || "/images/placeholder.webp";
      img.onerror = () => {
        img.src = "/images/placeholder.webp";
      };
      img.alt = book.book_title;
      img.loading = "lazy";

      link.appendChild(img);
      imageContainer.appendChild(link);

      // Content Container
      const content = document.createElement("div");
      content.className = "p-4 flex flex-col flex-grow";

      const title = document.createElement("h2");
      title.className = "text-xl font-black mb-2 text-primary";

      const titleLink = document.createElement("a");
      titleLink.href = book.buy_link || "#";
      titleLink.className =
        "hover:underline focus:outline-none focus:ring-2 focus:ring-accent1 rounded";
      titleLink.textContent = book.book_title;

      title.appendChild(titleLink);

      // Tags Container
      const tagsContainer = document.createElement("div");
      tagsContainer.className = "flex flex-wrap gap-2";

      // Add tags
      book.tags.forEach((tag) => {
        const style = getTagStyle(tag);
        const tagSpan = document.createElement("span");
        tagSpan.className = `tag ${style.bg} ${style.text} dark:${style.darkBg} dark:${style.darkText}`;
        tagSpan.textContent = tag;
        tagsContainer.appendChild(tagSpan);
      });

      // Assemble the components
      content.appendChild(title);
      content.appendChild(tagsContainer);
      article.appendChild(imageContainer);
      article.appendChild(content);
      fragment.appendChild(article);
    });

    // Single DOM update
    bookList.appendChild(fragment);
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
