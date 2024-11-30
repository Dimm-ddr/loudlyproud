// src/js/tag-helpers.ts
var tagHelpers = {
  formatTagClass: (tag) => {
    return "tag-" + tag.toLowerCase().replace(/\s+/g, "-");
  },
  getTagClasses: (tag) => {
    const baseClass = "tag";
    const specificClass = tagHelpers.formatTagClass(tag);
    return `${baseClass} ${specificClass}`;
  },
  hasCustomStyle: (tag) => {
    const style = getComputedStyle(document.documentElement);
    const className = tagHelpers.formatTagClass(tag);
    return style.getPropertyValue(`--${className}-bg`) !== "";
  }
};
export {
  tagHelpers
};
//# sourceMappingURL=tag-helpers.js.map
