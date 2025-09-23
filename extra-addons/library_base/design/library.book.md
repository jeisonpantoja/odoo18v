# library.book — Design Specification

## Purpose

Represents intellectual works (abstract works) independent of their physical manifestations. This model captures bibliographic information that remains constant across different editions, formats, and copies.

## Public API (Contract)

### Fields (Public Interface)

- **id** (int): Primary key
- **name** (char, required): Title of the work
- **display_name** (computed): Formatted title with primary author for UI display
- **author_ids** (many2many library.author): Authors who contributed to this work

### Methods (Public Interface)

- **get_editions(self, domain=None)** → recordset(library.edition): Returns editions of this work
- **get_availability_summary(self)** → dict: Returns availability across all branches
- **get_primary_author(self)** → recordset(library.author): Returns main author for display
- **as_dict(self, fields=None)** → dict: Returns work data as dictionary for API usage

## Fields (Detailed Implementation)

### Core Fields

- **name**: Char(required=True, index=True, translate=True)
  - Help: "Title of the intellectual work"
  - Normalized on create/write (trim spaces, collapse multiple spaces)
- **subtitle**: Char(optional, translate=True)
  - Help: "Subtitle if applicable"
- **original_title**: Char(optional)
  - Help: "Original title if this is a translation"
- **summary**: Text(optional, translate=True)
  - Help: "Brief description or synopsis of the work"
- **subject**: Text(optional)
  - Help: "Subject keywords for cataloging"

### Classification Fields

- **language**: Selection(optional)
  - Help: "Primary language of the work"
  - Options: [('en', 'English'), ('es', 'Spanish'), ('fr', 'French'), ...]
- **original_language**: Selection(optional)
  - Help: "Original language if translated"
- **date_created**: Date(optional)
  - Help: "Original creation/publication date"

### System Fields

- **active**: Boolean(default=True)
  - Help: "Uncheck to archive the work"

## Relations

### Direct Relations

- **author_ids**: Many2many('library.author', 'library_book_author_rel', 'book_id', 'author_id')

  - Authors who contributed to this work
  - Inverse of library.author.book_ids

- **genre_ids**: Many2many('library.genre', 'library_book_genre_rel', 'book_id', 'genre_id')

  - Genres/categories this work belongs to
  - Inverse of library.genre.book_ids

- **edition_ids**: One2many('library.edition', 'book_id')
  - Different editions/manifestations of this work
  - Cascade delete: if work is deleted, editions are deleted

### Computed Relations

- **copy_ids**: One2many('library.book_copy', 'book_id', compute='\_compute_copy_ids', store=False)
  - All physical copies across all editions (computed for convenience)
  - Implementation: aggregates copies from all editions

## Constraints & Validations

### Essential Constraints

1. **Title validation**:

   ```python
   @api.constrains('name')
   def _check_name_not_empty(self):
       if not self.name or not self.name.strip():
           raise ValidationError("Work title is required")
   ```

2. **Author requirement** (business rule):

   ```python
   @api.constrains('author_ids')
   def _check_has_authors(self):
       if not self.author_ids:
           raise ValidationError("A work must have at least one author")
   ```

3. **Date validation**:

   ```python
   @api.constrains('date_created')
   def _check_date_not_future(self):
       if self.date_created and self.date_created > fields.Date.today():
           raise ValidationError("Creation date cannot be in the future")
   ```

4. **Language consistency**:
   ```python
   @api.constrains('language', 'original_language')
   def _check_language_logic(self):
       if self.original_language and self.language == self.original_language:
           raise ValidationError("Original language cannot be the same as current language")
   ```

## Computed Fields Implementation

### Display Name

```python
@api.depends('name', 'author_ids')
def _compute_display_name(self):
    for record in self:
        if record.author_ids:
            primary_author = record.author_ids[0].name
            record.display_name = f"{record.name} - {primary_author}"
        else:
            record.display_name = record.name
```

### Copy IDs (Aggregated)

```python
@api.depends('edition_ids.copy_ids')
def _compute_copy_ids(self):
    for record in self:
        record.copy_ids = record.edition_ids.mapped('copy_ids')
```

## Business Logic Methods

### Availability Summary

```python
def get_availability_summary(self):
    """Returns availability statistics across all editions/copies"""
    copies = self.copy_ids
    total = len(copies)
    available = len(copies.filtered(lambda c: c.status == 'available'))

    branch_stats = {}
    for copy in copies.filtered(lambda c: c.status == 'available'):
        branch = copy.branch_id.name
        branch_stats[branch] = branch_stats.get(branch, 0) + 1

    return {
        'total_copies': total,
        'available_copies': available,
        'branch_availability': branch_stats,
        'is_available': available > 0
    }
```

### Primary Author

```python
def get_primary_author(self):
    """Returns the first author for display purposes"""
    return self.author_ids[:1] if self.author_ids else self.env['library.author']
```

## Tests (TDD Implementation)

### Priority High - Essential Behavior

```python
def test_create_work_minimal(self):
    """Test creating work with minimal required data (title + author)"""

def test_create_work_empty_title_fails(self):
    """Test that empty or whitespace-only titles raise ValidationError"""

def test_work_must_have_authors(self):
    """Test that works without authors raise ValidationError"""

def test_date_created_not_future(self):
    """Test that future creation dates are rejected"""

def test_language_consistency_validation(self):
    """Test that original_language cannot equal current language"""
```

### Priority Medium - Relations & Computed Fields

```python
def test_author_ids_many2many_relation(self):
    """Test that author_ids Many2many relationship works correctly"""

def test_genre_ids_many2many_relation(self):
    """Test that genre_ids Many2many relationship works correctly"""

def test_display_name_computation(self):
    """Test that display_name includes primary author"""

def test_copy_ids_computed_aggregation(self):
    """Test that copy_ids aggregates from all editions"""

def test_get_availability_summary(self):
    """Test availability summary returns correct statistics"""

def test_get_primary_author(self):
    """Test primary author selection logic"""
```

### Priority Low - Advanced Features

```python
def test_name_normalization(self):
    """Test that titles are properly normalized"""

def test_translation_fields(self):
    """Test that translatable fields work correctly"""
```

## Performance Considerations

### Indexing Strategy

- Index on `name` for title searches
- Index on `author_ids` relation table for author-based queries
- Consider full-text search index for `summary` and `subject`

### Caching

- `copy_ids` computed field not stored to avoid cache invalidation complexity
- `display_name` could be stored if frequently accessed in lists

## External IDs & Compatibility

### Stable External IDs

- Use pattern: `library_base.work_don_quixote`, `library_base.work_hamlet`
- For classics: `library_base.classic_[author_surname]_[short_title]`

### Backwards Compatibility Guarantees

- Field `name` remains required until major version bump
- Many2many relations (`author_ids`, `genre_ids`) will remain stable
- Method `get_availability_summary()` signature will remain stable

## Integration with Search/UX

### Search Behavior

- Primary search target for title/author queries
- Results show `display_name` and availability summary
- Link to editions for detailed manifestation selection

### UI Organization

- Form view tabs: Basic Info, Authors & Classification, Editions, Availability
- Tree view shows: title, primary author, edition count, availability status

## Usage Examples

```python
# Create work with authors and genres
work = env['library.book'].create({
    'name': 'Don Quixote de la Mancha',
    'subtitle': 'El ingenioso hidalgo',
    'summary': 'The adventures of an idealistic knight...',
    'language': 'es',
    'date_created': '1605-01-16',
    'author_ids': [(4, cervantes.id)],
    'genre_ids': [(4, fiction.id), (4, classics.id)]
})

# Get availability across all editions
availability = work.get_availability_summary()
# {'total_copies': 5, 'available_copies': 2, 'branch_availability': {'Central': 1, 'West': 1}}

# Find primary author for display
primary = work.get_primary_author()
```

## Migration & Evolution Notes

### Future Extensions

- Consider ORCID integration for author disambiguation
- Potential for series/collection relationships
- Subject heading standardization (LCSH, Dewey)

### Data Quality

- Import processes should validate ISBN at edition level
- Author name normalization should happen at library.author level
- Duplicate detection should consider title + primary author + date
