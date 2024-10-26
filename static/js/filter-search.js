document.addEventListener("DOMContentLoaded", function () {
  // At this point, the `books` variable is already declared in the <script> tag from baseof.html

  const searchField = document.getElementById("search-field");
  const tagFilters = document.querySelectorAll(".tag-filter");
  const authorFilters = document.querySelectorAll(".author-filter");
  const bookList = document.getElementById("book-list");

  // Initialize Fuse.js
  const fuse = new Fuse(books, {
    keys: ["title", "authors", "tags", "book_description"],
    threshold: 0.4,
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

  // Search functionality
  searchField.addEventListener("input", (event) => {
    const results = fuse.search(event.target.value);
    const filteredBooks = results.map((result) => result.item);
    renderBooks(filteredBooks);
  });

  // Filter functionality
  function applyFilters() {
    let filteredBooks = books;

    const selectedTags = [...tagFilters]
      .filter((checkbox) => checkbox.checked)
      .map((checkbox) => checkbox.value);

    const selectedAuthors = [...authorFilters]
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

  // Attach filter event listeners
  tagFilters.forEach((checkbox) =>
    checkbox.addEventListener("change", applyFilters),
  );
  authorFilters.forEach((checkbox) =>
    checkbox.addEventListener("change", applyFilters),
  );

  // Initial render
  renderBooks(books);
});
