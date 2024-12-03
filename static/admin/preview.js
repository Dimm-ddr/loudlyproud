const BookPreview = createClass({
  render: function() {
    const entry = this.props.entry;
    const params = entry.getIn(['data', 'params']);

    return h('div', {className: "book-preview"},
      h('div', {className: "book-header"},
        h('h1', {}, params.getIn(['book_title'])),
        h('div', {className: "book-authors"},
          params.getIn(['authors']).map(author => h('span', {className: "author"}, author))
        )
      ),
      h('div', {className: "book-content"},
        params.getIn(['cover']) && h('img', {
          className: "book-cover",
          src: params.getIn(['cover']),
          alt: params.getIn(['cover_alt']) || 'Book cover'
        }),
        h('div', {className: "book-details"},
          h('div', {className: "book-description"}, params.getIn(['book_description'])),
          h('div', {className: "book-metadata"},
            h('p', {}, `Publication Year: ${params.getIn(['publication_year'])}`),
            h('p', {}, `ISBN: ${params.getIn(['isbn'])}`),
            h('p', {}, `Pages: ${params.getIn(['page_count'])}`),
            params.getIn(['publishers']) && h('p', {},
              `Publishers: ${params.getIn(['publishers']).join(', ')}`
            ),
            params.getIn(['languages']) && h('p', {},
              `Languages: ${params.getIn(['languages']).join(', ')}`
            ),
            params.getIn(['tags']) && h('div', {className: "book-tags"},
              params.getIn(['tags']).map(tag =>
                h('span', {className: "tag"}, tag)
              )
            )
          )
        )
      )
    );
  }
});

CMS.registerPreviewStyle('/css/book.css');
CMS.registerPreviewTemplate('books', BookPreview);
