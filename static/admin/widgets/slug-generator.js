// Create this as static/admin/widgets/slug-generator.js

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

// Register the custom widget
CMS.registerWidget("slug-generator", SlugGeneratorWidget);
