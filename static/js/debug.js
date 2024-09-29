// Assuming jsVisibleAttributes is passed via script in the template
console.log("Visible Attributes from Hugo:", jsVisibleAttributes);

// Function to render book attributes dynamically (for debugging or other purposes)
function displayBookAttributes(books, visibleAttributes) {
  if (!books || !visibleAttributes) {
    console.error("Books or visible attributes are not defined.");
    return;
  }
  console.log("Loaded books:", books);

  // Dynamically display attributes for each book
  Object.keys(books).forEach(function (bookCategory) {
    const bookData = books[bookCategory];
    Object.keys(bookData).forEach(function (bookKey) {
      const book = bookData[bookKey];
      visibleAttributes.forEach(function (attr) {
        if (book[attr]) {
          console.log(`${attr}: ${book[attr]}`);
        }
      });
    });
  });
}

// Ensure both variables are defined and then call the function
if (
  typeof books !== "undefined" &&
  typeof jsVisibleAttributes !== "undefined"
) {
  displayBookAttributes(books, jsVisibleAttributes);
} else {
  console.error("Books or visible attributes are missing.");
}
