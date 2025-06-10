# Hugo Template Optimization Plan

## Overview
This document outlines a comprehensive plan to address Hugo template warnings and optimize the project structure. The current warnings indicate unused templates and missing section layouts that need to be resolved.

## Current Issues Analysis

### 1. Missing Section Layout Warning
**Issue**: `WARN found no layout file for "html" for kind "section"`
**Root Cause**: Content pages like `content/en/main.md` have `type: "main"` but are being treated as section pages, yet no section layout exists.

### 2. Unused Template Files
**Issue**: Multiple template files are marked as unused:
- `/_default/main.html` - Complex template for book catalog display
- `/_default/taxonomy.html` - Template for tag/taxonomy pages  
- `/_default/single.html` - Basic single page template
- Various partial templates under `/partials/book/components/`
- Feedback-related partials
- Theme toggle and no-results partials

## Action Plan

### Phase 1: Template Architecture Reorganization

#### 1.1 Fix Main Page Layout Issues
- **Target Files**: `content/en/main.md`, `content/ru/main.md`, `content/fa/main.md`, `content/ku/main.md`
- **Action**: These pages currently have `type: "main"` and `layout: "main"` but the system can't find the appropriate template
- **Solution**: 
  - Create `layouts/main/single.html` to handle pages with `type: "main"`
  - Move the content from `layouts/_default/main.html` to `layouts/main/single.html`
  - This will resolve the "no layout file for html for kind section" warning

#### 1.2 Consolidate Single Page Templates
- **Target Files**: `layouts/_default/single.html`, `layouts/books/single.html`
- **Action**: The `_default/single.html` is unused because `books/single.html` handles book pages
- **Solution**: 
  - Keep `layouts/books/single.html` for book-specific pages
  - Update `layouts/_default/single.html` to be a generic fallback for other content types
  - Ensure it's actually used by content that doesn't have specific layouts

#### 1.3 Taxonomy Template Optimization
- **Target Files**: `layouts/_default/taxonomy.html`, `layouts/tags/term.html`
- **Action**: `_default/taxonomy.html` is unused because `tags/term.html` handles tag pages
- **Solution**:
  - Review if `_default/taxonomy.html` should be the fallback for other taxonomies
  - If not needed, remove it; if needed, ensure it's properly referenced

### Phase 2: Partial Template Cleanup

#### 2.1 Book Component Partials Review
- **Target Files**: 
  - `layouts/partials/book/components/authors.html`
  - `layouts/partials/book/components/metadata.html`
  - `layouts/partials/book/components/title-section.html`
  - `layouts/partials/book/metadata.html`
  - `layouts/partials/book/metadata/external-links.html`
- **Action**: These are unused according to warnings
- **Solution**:
  - Audit `layouts/books/single.html` and other book templates to see if these should be used
  - If they represent better modular design, refactor book templates to use them
  - If they're truly obsolete, remove them

#### 2.2 Feedback System Partials
- **Target Files**:
  - `layouts/partials/feedback/fa.html`
  - `layouts/partials/feedback/ku.html`
- **Action**: These language-specific feedback partials are unused
- **Solution**:
  - Review `layouts/feedback/` directory structure
  - Integrate these partials into the feedback system if they're meant to be used
  - Remove if they're obsolete

#### 2.3 UI Component Partials
- **Target Files**:
  - `layouts/partials/no-results.html`
  - `layouts/partials/theme-toggle.html`
- **Action**: These UI components are unused
- **Solution**:
  - Check if `no-results.html` should be used in search functionality
  - Verify if `theme-toggle.html` should be integrated into the site header
  - Integrate into appropriate templates or remove if obsolete

### Phase 3: Content Type Organization

#### 3.1 Create Proper Content Type Structure
- **Target**: Content organization for different page types
- **Action**: Establish clear content type hierarchy
- **Solution**:
  - Define content types: `main`, `books`, `feedback`, `tags`
  - Ensure each content type has appropriate layouts
  - Update front matter in content files to use correct types

#### 3.2 Section vs Single Page Clarification
- **Target**: Content pages that should be sections vs singles
- **Action**: Determine which pages should be section indexes vs single pages
- **Solution**:
  - Convert main catalog pages to proper section indexes if they should list content
  - Or ensure they're properly configured as single pages with correct layouts

### Phase 4: Template Performance and Maintainability

#### 4.1 Template Consolidation
- **Target**: Reduce template redundancy
- **Action**: Identify and merge similar templates
- **Solution**:
  - Create base templates for common layouts
  - Use Hugo's template inheritance more effectively
  - Consolidate similar functionality across templates

#### 4.2 Partial Template Organization
- **Target**: Better organization of partial templates
- **Action**: Reorganize partials for better maintainability
- **Solution**:
  - Group related partials in logical directories
  - Ensure all partials are actually used
  - Document partial template dependencies

### Phase 5: Testing and Validation

#### 5.1 Template Usage Verification
- **Target**: Ensure all templates are properly used
- **Action**: Verify that template fixes resolve warnings
- **Solution**:
  - Test build after each template change
  - Verify that content renders correctly
  - Ensure no new warnings are introduced

#### 5.2 Content Rendering Tests
- **Target**: All content types render correctly
- **Action**: Test each content type and language
- **Solution**:
  - Verify main pages render with correct layouts
  - Test book pages display properly
  - Check feedback pages work correctly
  - Validate tag/taxonomy pages function as expected

## Implementation Priority

### High Priority (Immediate)
1. Fix main page layout issues (Phase 1.1)
2. Remove or integrate unused partial templates (Phase 2)

### Medium Priority (Next Sprint)
3. Consolidate single page templates (Phase 1.2)
4. Organize content types properly (Phase 3)

### Low Priority (Future Enhancement)
5. Template performance optimization (Phase 4)
6. Comprehensive testing suite (Phase 5.2)

## Success Metrics

- [ ] Zero Hugo template warnings during build
- [ ] All content pages render correctly
- [ ] No broken links or missing templates
- [ ] Improved build performance
- [ ] Better template maintainability

## Files to Modify

### Templates to Create/Modify:
- `layouts/main/single.html` (new)
- `layouts/_default/single.html` (update)
- `layouts/_default/taxonomy.html` (review/remove)

### Partials to Review:
- All files in `layouts/partials/book/components/`
- All files in `layouts/partials/feedback/`
- `layouts/partials/no-results.html`
- `layouts/partials/theme-toggle.html`

### Content Files to Update:
- `content/*/main.md` files (front matter)
- Any content with incorrect type/layout specifications

## Notes

- This plan prioritizes fixing immediate warnings while setting up for long-term maintainability  
- Each phase should be implemented and tested separately
- Template changes should be backed up before modification
- Consider Hugo's template lookup order when making changes 