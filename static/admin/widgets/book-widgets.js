// static/admin/widgets/book-widgets.js
const SlugGeneratorWidget = createClass({
  getInitialState() {
    return {
      value: this.props.value || "",
    };
  },

  generateAndSetSlug() {
    console.log("Generate button clicked"); // Debug log

    // Get form data from CMS
    const formData = this.props.entry.get("data");
    console.log("Form data:", formData && formData.toJS()); // Debug log

    // Try to get book title from form data
    let title = "";
    if (formData) {
      const params = formData.get("params");
      if (params) {
        title = params.get("book_title");
      }
    }

    // If no title in form data, try to get it from the DOM
    if (!title) {
      const titleField = document.querySelector(
        'input[id^="book_title-field"]',
      );
      console.log("Title field from DOM:", titleField); // Debug log
      if (titleField) {
        title = titleField.value;
      }
    }

    console.log("Found title:", title); // Debug log

    if (!title) {
      console.log("No title found"); // Debug log
      return;
    }

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
    console.log("Generated slug:", newSlug); // Debug log
    this.setState({ value: newSlug });
    this.props.onChange(newSlug);
  },

  render() {
    const { forID, classNameWrapper, setActiveStyle, setInactiveStyle } =
      this.props;
    const buttonStyle = {
      marginLeft: "10px",
      padding: "4px 10px",
      backgroundColor: "#798291",
      color: "white",
      border: "none",
      borderRadius: "3px",
      cursor: "pointer",
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
                onClick: () => this.generateAndSetSlug(),
              },
              this.state.value ? "Regenerate Slug" : "Generate Slug",
            ),
          ],
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
          "The hash at the end ensures unique URLs for books with identical titles",
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
