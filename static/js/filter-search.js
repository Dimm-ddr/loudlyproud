// src/js/filter-search.ts
document.addEventListener("DOMContentLoaded", function() {
  const searchField = document.getElementById("search-field");
  const tagFilters = document.querySelectorAll(".tag-filter");
  const authorFilters = document.querySelectorAll(".author-filter");
  const bookList = document.getElementById("book-list");
  const fuse = new window.Fuse(window.books, {
    keys: ["title", "authors", "tags", "book_description"],
    threshold: 0.4
  });
  function renderBooks(filteredBooks) {
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
  searchField.addEventListener("input", (event) => {
    const target = event.target;
    const results = fuse.search(target.value);
    const filteredBooks = results.map((result) => result.item);
    renderBooks(filteredBooks);
  });
  tagFilters.forEach(
    (checkbox) => checkbox.addEventListener("change", applyFilters)
  );
  authorFilters.forEach(
    (checkbox) => checkbox.addEventListener("change", applyFilters)
  );
  renderBooks(window.books);
});
//# sourceMappingURL=filter-search.js.map
