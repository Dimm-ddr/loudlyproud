// static/admin/widgets/book-widgets.js
const SlugGeneratorWidget = createClass({
  getInitialState() {
    return {
      value: this.props.value || "",
    };
  },

  generateAndSetSlug() {
    const titleInput = document.querySelector(
      '[data-field-name="Params.book_title"]',
    );
    const title = titleInput?.value;
    if (!title) return;

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
    this.setState({ value: newSlug });
    this.props.onChange(newSlug);
  },

  render() {
    const { forID, classNameWrapper, setActiveStyle, setInactiveStyle } =
      this.props;

    return h(
      "div",
      { className: "slug-generator-wrapper" },
      h("input", {
        type: "text",
        id: forID,
        className: classNameWrapper,
        value: this.state.value || "",
        onFocus: setActiveStyle,
        onBlur: setInactiveStyle,
        readOnly: true,
        required: true,
      }),
      h(
        "button",
        {
          type: "button",
          className: "regenerate-button",
          onClick: () => this.generateAndSetSlug(),
        },
        this.state.value ? "Regenerate Slug" : "Generate Slug",
      ),
      h(
        "small",
        {
          style: {
            display: "block",
            marginTop: "0.5em",
            opacity: "0.7",
          },
        },
        "The hash at the end ensures unique URLs for books with identical titles",
      ),
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

CMS.registerWidget("slug-generator", SlugGeneratorWidget);
CMS.registerWidget("book-title", book_titleWidget);
