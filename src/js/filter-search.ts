import { Book } from '../types';

declare global {
  interface Window {
    books: Book[];
    Fuse: any; // Consider installing @types/fuse.js for better typing
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const searchField = document.getElementById("search-field") as HTMLInputElement;
  const tagFilters = document.querySelectorAll<HTMLInputElement>(".tag-filter");
  const authorFilters = document.querySelectorAll<HTMLInputElement>(".author-filter");
  const bookList = document.getElementById("book-list") as HTMLDivElement;

  const fuse = new window.Fuse(window.books, {
    keys: ["title", "authors", "tags", "book_description"],
    threshold: 0.4,
  });

  function renderBooks(filteredBooks: Book[]): void {
    bookList.innerHTML = "";
    filteredBooks.forEach((book) => {
      const bookHTML = `
        <div class="book-item">
          <h2>${book.title}</h2>
          <!-- Other book info here -->
        </div>`;
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
        book.tags.some((tag) => selectedTags.includes(tag))
      );
    }

    if (selectedAuthors.length) {
      filteredBooks = filteredBooks.filter((book) =>
        book.authors.some((author) => selectedAuthors.includes(author))
      );
    }

    renderBooks(filteredBooks);
  }

  // Event listeners
  searchField.addEventListener("input", (event) => {
    const target = event.target as HTMLInputElement;
    const results = fuse.search(target.value);
    const filteredBooks = results.map((result: { item: Book }) => result.item);
    renderBooks(filteredBooks);
  });

  tagFilters.forEach((checkbox) =>
    checkbox.addEventListener("change", applyFilters)
  );

  authorFilters.forEach((checkbox) =>
    checkbox.addEventListener("change", applyFilters)
  );

  // Initial render
  renderBooks(window.books);
});
