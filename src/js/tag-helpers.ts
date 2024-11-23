export interface TagHelpers {
  formatTagClass: (tag: string) => string;
  getTagClasses: (tag: string) => string;
  hasCustomStyle: (tag: string) => boolean;
}

export const tagHelpers: TagHelpers = {
  formatTagClass: (tag: string): string => {
    return 'tag-' + tag.toLowerCase().replace(/\s+/g, '-');
  },

  getTagClasses: (tag: string): string => {
    const baseClass = 'tag';
    const specificClass = tagHelpers.formatTagClass(tag);
    return `${baseClass} ${specificClass}`;
  },

  hasCustomStyle: (tag: string): boolean => {
    const style = getComputedStyle(document.documentElement);
    const className = tagHelpers.formatTagClass(tag);
    return style.getPropertyValue(`--${className}-bg`) !== '';
  }
};
