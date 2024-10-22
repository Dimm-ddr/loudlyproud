// static/admin/widgets/book-widgets.js
/**
 * Custom Decap CMS widgets for book entries
 * Includes:
 * - SlugGeneratorWidget: Automatically generates slugs from book titles
 * - BookTitleWidget: Handles book title input with page title auto-fill
 */

const SlugGeneratorWidget = createClass({
  generateRandomString() {
    return Math.random().toString(36).substring(2, 10);
  },

  generateSlug(title) {
    if (!title) return "";
    const baseSlug = title
      .toLowerCase()
      .replace(/[^\w\s-]/g, "") // Remove special characters
      .replace(/\s+/g, "-") // Replace spaces with hyphens
      .replace(/-+/g, "-") // Remove consecutive hyphens
      .trim(); // Trim leading/trailing spaces

    return `${baseSlug}-${this.generateRandomString()}`;
  },

  render() {
    const { forID, classNameWrapper, setActiveStyle, setInactiveStyle, value } =
      this.props;

    return h(
      "div",
      { className: classNameWrapper },
      h("input", {
        type: "text",
        id: forID,
        className: classNameWrapper,
        value: value || "",
        onFocus: setActiveStyle,
        onBlur: setInactiveStyle,
        readonly: true,
      }),
    );
  },
});

// Auto-fill page title when book title changes
const BookTitleWidget = createClass({
  handleChange(e) {
    const value = e.target.value;
    this.props.onChange(value);

    // Find the page title field and update it
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
CMS.registerWidget("book-title", BookTitleWidget);
