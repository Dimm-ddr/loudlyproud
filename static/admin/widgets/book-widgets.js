// static/admin/widgets/book-widgets.js
const SlugGeneratorWidget = createClass({
  getInitialState() {
    return {
      value: this.props.value || "",
      error: null,
    };
  },

  generateAndSetSlug() {
    // Get title from the book title field
    const titleField = document.querySelector('input[id^="book_title-field"]');
    if (!titleField?.value) {
      this.setState({ error: "Please fill in the Book Title field first" });
      setTimeout(() => this.setState({ error: null }), 3000); // Clear error after 3 seconds
      return;
    }

    const title = titleField.value;

    // Transliterate Cyrillic to Latin characters
    const translitMap = {
      а: "a",
      б: "b",
      в: "v",
      г: "g",
      д: "d",
      е: "e",
      ё: "yo",
      ж: "zh",
      з: "z",
      и: "i",
      й: "y",
      к: "k",
      л: "l",
      м: "m",
      н: "n",
      о: "o",
      п: "p",
      р: "r",
      с: "s",
      т: "t",
      у: "u",
      ф: "f",
      х: "h",
      ц: "ts",
      ч: "ch",
      ш: "sh",
      щ: "sch",
      ъ: "",
      ы: "y",
      ь: "",
      э: "e",
      ю: "yu",
      я: "ya",
    };

    const transliterate = (str) => {
      return str
        .toLowerCase()
        .split("")
        .map((char) => translitMap[char] || char)
        .join("");
    };

    // Generate base slug from title
    const baseSlug = transliterate(title)
      .toLowerCase()
      .replace(/[^\w\s-]/g, "") // Remove non-word chars except spaces and dashes
      .replace(/\s+/g, "-") // Replace spaces with dashes
      .replace(/-+/g, "-") // Replace multiple dashes with single dash
      .trim(); // Trim dashes from start and end

    // Generate a hash using title and random component
    const titleHash = title.split("").reduce((acc, char) => {
      return ((acc << 5) - acc + char.charCodeAt(0)) | 0;
    }, 0);
    const uniqueHash = Math.abs(titleHash).toString(36).substring(0, 4);
    const randomPart = Math.random().toString(36).substring(2, 4);

    // Combine everything into final slug
    const newSlug = `${baseSlug}-${uniqueHash}${randomPart}`;
    this.setState({ value: newSlug, error: null });
    this.props.onChange(newSlug);
  },

  render() {
    const { forID, classNameWrapper, setActiveStyle, setInactiveStyle } =
      this.props;
    const buttonStyle = {
      marginLeft: "10px",
      padding: "0 12px",
      height: "36px",
      backgroundColor: "#3b82f6", // Bright blue color
      color: "white",
      border: "none",
      borderRadius: "4px",
      cursor: "pointer",
      fontSize: "14px",
      fontWeight: "500",
      transition: "background-color 0.2s ease",
      ":hover": {
        backgroundColor: "#2563eb", // Darker blue on hover
      },
    };

    return h(
      "div",
      {
        className: "slug-generator-wrapper",
        style: {
          display: "flex",
          alignItems: "center",
          flexDirection: "column",
        },
      },
      [
        h(
          "div",
          {
            key: "input-row",
            style: { display: "flex", width: "100%", alignItems: "center" },
          },
          [
            h("input", {
              key: "input",
              type: "text",
              id: forID,
              className: classNameWrapper,
              value: this.state.value || "",
              onFocus: setActiveStyle,
              onBlur: setInactiveStyle,
              readOnly: true,
              required: true,
              style: { flexGrow: 1 },
            }),
            h(
              "button",
              {
                key: "button",
                type: "button",
                style: buttonStyle,
                onMouseOver: (e) => {
                  e.target.style.backgroundColor = "#2563eb";
                },
                onMouseOut: (e) => {
                  e.target.style.backgroundColor = "#3b82f6";
                },
                onClick: () => this.generateAndSetSlug(),
              },
              this.state.value ? "Regenerate Slug" : "Generate Slug",
            ),
          ],
        ),
        this.state.error &&
          h(
            "small",
            {
              key: "error",
              style: {
                marginTop: "0.5em",
                color: "#dc2626",
                alignSelf: "flex-start",
              },
            },
            this.state.error,
          ),
        h(
          "small",
          {
            key: "helper",
            style: {
              marginTop: "0.5em",
              opacity: "0.7",
              alignSelf: "flex-start",
            },
          },
          "Fill in the Book Title field first, then click the button to generate a URL-friendly slug. The hash at the end ensures unique URLs for books with identical titles.",
        ),
      ],
    );
  },
});

const book_titleWidget = createClass({
  handleChange(e) {
    const value = e.target.value;
    this.props.onChange(value);

    const pageTitle = document.querySelector('[data-field-name="title"]');
    if (pageTitle) {
      const pageTitleWidget = pageTitle.__cms_widget;
      if (pageTitleWidget && pageTitleWidget.props.onChange) {
        pageTitleWidget.props.onChange(value);
      }
    }
  },

  render() {
    const { forID, classNameWrapper, setActiveStyle, setInactiveStyle, value } =
      this.props;

    return h("input", {
      type: "text",
      id: forID,
      className: classNameWrapper,
      value: value || "",
      onChange: this.handleChange,
      onFocus: setActiveStyle,
      onBlur: setInactiveStyle,
      required: true,
    });
  },
});

// Make sure we register the widgets after the CMS is loaded
if (window.CMS) {
  CMS.registerWidget("slug-generator", SlugGeneratorWidget);
  CMS.registerWidget("book-title", book_titleWidget);
} else {
  console.error(
    "CMS not found! Make sure Decap CMS is loaded before this script.",
  );
}
