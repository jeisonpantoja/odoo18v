# Library Base Models - Overview

## Purpose
This document provides a high-level view of all models in `library_base` module. It serves as a dependency map and implementation roadmap for TDD development.

## Models Summary

### library.author
**- Purpose**: Represent a person who writes/contributes to books  
**- Key fields**: `id`, `name (Char, required)`, `country (Char)`, `partner_id (M2O res.partner, optional)`  
**- Public relations**: `book_ids (computed One2many)` or `contribution_ids` if using bridge model  
**- Dependencies**: base (res.partner optional)  
**- TDD Priority**: High  

### library.publisher
**- Purpose**: Represent publishing companies/organizations  
**- Key fields**: `id`, `name (Char, required)`, `website (Char)`, `contact_id (M2O res.partner, optional)`  
**- Public relations**: `book_ids (computed One2many)`  
**- Dependencies**: base (res.partner optional)  
**- TDD Priority**: High  

### library.genre
**- Purpose**: Categorization system for books (hierarchical taxonomy)  
**- Key fields**: `id`, `name (Char, required)`, `parent_id (M2O library.genre, optional)`  
**- Public relations**: `child_ids (One2many)`, `book_ids (M2M through library.book)`  
**- Dependencies**: none  
**- TDD Priority**: High  

### library.branch  
**- Purpose**: Physical library locations/branches for multi-location management  
**- Key fields**: `id`, `name (Char, required)`, `address (Text)`, `manager_id (M2O res.users)`  
**- Public relations**: `book_copy_ids (One2many)`  
**- Dependencies**: base (res.users)  
**- TDD Priority**: Medium  

### library.book
**- Purpose**: Represent intellectual works (not physical copies)  
**- Key fields**: `id`, `name (Char, required)`, `isbn (Char)`, `summary (Text)`, `language (Selection)`, `date_published (Date)`  
**- Public relations**: `author_ids (M2M library.author)`, `publisher_id (M2O library.publisher)`, `genre_ids (M2M library.genre)`, `copy_ids (One2many library.book_copy)`  
**- Dependencies**: library.author, library.publisher, library.genre  
**- TDD Priority**: High  

### library.book_copy
**- Purpose**: Physical/digital instances of books (inventory items)  
**- Key fields**: `id`, `name (Char, barcode)`, `book_id (M2O library.book)`, `status (Selection)`, `branch_id (M2O library.branch)`, `location (Char)`  
**- Public relations**: `loan_ids (One2many, future in library_management)`  
**- Dependencies**: library.book, library.branch  
**- TDD Priority**: Medium  

## Implementation Order (TDD)
Based on dependency analysis:

**Phase 1 - Independent models**:
1. library.author
2. library.publisher  
3. library.genre
4. library.branch

**Phase 2 - Dependent models**:
5. library.book (requires Phase 1 models)
6. library.book_copy (requires library.book and library.branch)

## Notes
- All models inherit from `mail.thread` for activity tracking
- External IDs will use pattern: `library_base.model_record_identifier`
- Public API methods follow pattern: `get_*`, `search_*`, `as_dict`
