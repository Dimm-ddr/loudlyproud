const BookPreview = createClass({
  render: function() {
    const entry = this.props.entry;
    const params = entry.getIn(['data', 'params']);

    // Helper function to safely get and join array values
    const getList = (path) => {
      const list = params.getIn(path);
      return list ? list.toJS() : [];
    };

    // Helper function to safely get single values
    const getValue = (path, defaultValue = '') => {
      return params.getIn(path) || defaultValue;
    };

    return h('div', {className: "book-preview"},
      h('div', {className: "book-header"},
        h('h1', {className: "book-title"}, getValue(['book_title'])),
        h('div', {className: "book-authors"},
          getList(['authors']).map((author, idx) =>
            h('span', {key: idx, className: "author"}, author)
          )
        ),
        getValue(['series']) && h('div', {className: "book-series"},
          getValue(['series'])
        )
      ),
      h('div', {className: "book-content"},
        getValue(['cover']) && h('div', {className: "book-cover-container"},
          h('img', {
            className: "book-cover",
            src: getValue(['cover']),
            alt: getValue(['cover_alt'], 'Book cover')
          })
        ),
        h('div', {className: "book-details"},
          getValue(['book_description']) && h('div', {className: "book-description"},
            getValue(['book_description'])
          ),
          h('div', {className: "book-metadata"},
            h('div', {className: "metadata-group"},
              getValue(['publication_year']) && h('p', {className: "metadata-item"},
                h('span', {className: "metadata-label"}, "Publication Year: "),
                h('span', {}, getValue(['publication_year']))
              ),
              getValue(['isbn']) && h('p', {className: "metadata-item"},
                h('span', {className: "metadata-label"}, "ISBN: "),
                h('span', {}, getValue(['isbn']))
              ),
              getValue(['page_count']) && h('p', {className: "metadata-item"},
                h('span', {className: "metadata-label"}, "Pages: "),
                h('span', {}, getValue(['page_count']))
              )
            ),
            getList(['publishers']).length > 0 && h('p', {className: "metadata-item"},
              h('span', {className: "metadata-label"}, "Publishers: "),
              h('span', {}, getList(['publishers']).join(', '))
            ),
            getList(['languages']).length > 0 && h('p', {className: "metadata-item"},
              h('span', {className: "metadata-label"}, "Languages: "),
              h('span', {}, getList(['languages']).join(', '))
            ),
            getValue(['russian_translation_status']) && h('p', {className: "metadata-item"},
              h('span', {className: "metadata-label"}, "Translation Status: "),
              h('span', {className: "status"}, getValue(['russian_translation_status']))
            )
          ),
          getList(['tags']).length > 0 && h('div', {className: "book-tags"},
            getList(['tags']).map((tag, idx) =>
              h('span', {key: idx, className: "tag"}, tag)
            )
          )
        )
      )
    );
  }
});

// Register the preview template
CMS.registerPreviewTemplate("books", BookPreview);

// Register the preview styles
CMS.registerPreviewStyle("/admin/admin.css");
