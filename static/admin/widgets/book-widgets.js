// static/admin/widgets/book-widgets.js
const SlugGeneratorWidget = createClass({
  getInitialState() {
    return {
      value: this.props.value || "",
      regenerateButton: false,
    };
  },

  componentDidMount() {
    if (!this.props.value) {
      const book_title = document.querySelector(
        '[data-field-name="Params.book_title "]',
      )?.value;
      if (book_title) {
        const newSlug = this.generateSlug(book_title);
        this.setState({ value: newSlug });
        this.props.onChange(newSlug);
      }
    }
    this.setState({ regenerateButton: Boolean(this.props.value) });
  },

  generateSlug(title) {
    if (!title) return Math.random().toString(36).substring(2, 10);

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

    const baseSlug = transliterate(title)
      .toLowerCase()
      .replace(/[^\w\s-]/g, "")
      .replace(/\s+/g, "-")
      .replace(/-+/g, "-")
      .trim();

    return `${baseSlug}-${Math.random().toString(36).substring(2, 8)}`;
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
      }),
      this.state.regenerateButton &&
        h(
          "button",
          {
            type: "button",
            className: "regenerate-button",
            onClick: () => {
              const book_title = document.querySelector(
                '[data-field-name="Params.book_title "]',
              )?.value;
              const newSlug = this.generateSlug(book_title);
              this.setState({ value: newSlug });
              this.props.onChange(newSlug);
            },
          },
          "Regenerate Slug",
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
