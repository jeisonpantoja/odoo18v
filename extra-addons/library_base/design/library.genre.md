# library.genre — Design Specification

## Purpose

Represents hierarchical categorization system for books (genres, subjects, themes). Supports parent-child relationships to create taxonomies like "Fiction > Science Fiction > Cyberpunk" or "Non-Fiction > Science > Biology".

## Public API (Contract)

### Fields (Public Interface)

- **id** (int): Primary key
- **name** (char, required): Name of the genre/category
- **display_name** (computed): Formatted name for UI display (includes hierarchy)
- **parent_id** (many2one library.genre, optional): Parent genre in hierarchy
- **child_ids** (one2many library.genre, inverse of parent_id)
- **active** (boolean): archive flag
- **sequence** (integer): ordering among siblings
- **full_path** (computed, stored): cached path like "Fiction / Science Fiction / Space Opera"

### Methods (Public Interface)

- **get_books(self, domain=None, include_children=False)** → recordset(library.book): Returns books in this genre (optionally including child genres)
- **get_hierarchy_path(self)** → list: Returns full path from root to this genre
- **get_all_children(self, include_self=False)** → recordset(library.genre): Returns all descendant genres
- **as_dict(self, fields=None)** → dict: Returns genre data as dictionary for API usage

## Fields (Detailed Implementation)

### Core Fields

- **name**: Char(required=True, index=True)
  - Help: "Name of the genre or category"
  - Normalized on create/write (trim spaces, collapse multiple spaces)
- **code**: Char(optional, index=True)
  - Help: "Short code for the genre (e.g., 'SCI-FI', 'HIST')"
  - Used for quick reference and imports
- **description**: Text(optional)
  - Help: "Detailed description of what this genre encompasses"
- **color**: Integer(optional)
  - Help: "Color code for UI display (kanban views, charts)"

### Hierarchy Fields

- **parent_id**: Many2one('library.genre', ondelete='cascade')
  - Help: "Parent genre in the hierarchy"
  - Index: True for performance
- **parent_path**: Char(index=True)
  - Help: "Materialized path for efficient hierarchy queries"
  - Auto-computed by Odoo's hierarchy support
- **child_ids**: One2many('library.genre', 'parent_id')

  - Help: "Direct child genres"

## Diagram

library_genre (self-referential)
│
├─ id (PK)
├─ name
├─ parent_id (FK → library_genre.id) ◄── Relación recursiva
└─ child_ids (computed, inverse of parent_id)

Cardinalidad: 
- Cada género puede tener 0 ó 1 padre (Many2one)
- Cada género puede tener 0 a N hijos (One2many)

┌─────────────────────────────────────┐
│         library.genre               │
├─────────────────────────────────────┤
│ PK  id            INTEGER           │
│     name          VARCHAR(255)      │
│     code          VARCHAR(20)       │
│     description   TEXT              │
│     color         INTEGER           │
│ FK  parent_id     INTEGER           │◄────┐
│     parent_path   VARCHAR(255)      │     │
│     sequence      INTEGER           │     │
│     active        BOOLEAN           │     │
└─────────────────────────────────────┘     │
                │                           |
                │                           │
                │    "is parent of"         │
                │    (1:N - recursive)      │
                └───────────────────────────┘
                     ↑
                     │
                Relación reflexiva
                (self-referential)

### System Fields

- **active**: Boolean(default=True)
  - Help: "Uncheck to archive the genre"

  ```python
  name = fields.Char(string='Genre', required=True, index=True)
  parent_id = fields.Many2one('library.genre', string='Parent Genre', ondelete='restrict')
  child_ids = fields.One2many('library.genre', 'parent_id', string='Sub Genres')
  sequence = fields.Integer(default=10)
  active = fields.Boolean(default=True)
  full_path = fields.Char(string='Full Path', compute='_compute_full_path', store=True)
  book_count = fields.Integer(string='Books Count', compute='_compute_book_count', store=True)
  ```
- Notes:
  - ondelete='restrict' prevents accidental deletion of parent with children; consider cascade only if you want to remove subtree.
  - full_path computed and stored for fast UI display and faceted search.
  - book_count computed/stored for performance in lists and dashboards.

## Relations

### Direct Relations

- **book_ids**: Many2many('library.book', 'library_book_genre_rel', 'genre_id', 'book_id')
  - Shows all books directly assigned to this genre
  - Inverse of library.book.genre_ids

## Constraints & Validations

### Essential Constraints

1. **Name validation**:

   ```python
   @api.constrains('name')
   def _check_name_not_empty(self):
       if not self.name or not self.name.strip():
           raise ValidationError("Genre name is required")
   ```

2. **Hierarchy validation**:

   ```python
   @api.constrains('parent_id')
   def _check_parent_hierarchy(self):
       if not self._check_recursion():
           raise ValidationError("You cannot create recursive genre hierarchies")
   ```

3. **Code uniqueness** (if used):

   ```python
   @api.constrains('code')
   def _check_code_unique(self):
       if self.code and self.search_count([('code', '=', self.code), ('id', '!=', self.id)]) > 0:
           raise ValidationError("Genre code must be unique")
   ```

4. **Parent-child logic**:
   ```python
   @api.constrains('parent_id')
   def _check_parent_not_self(self):
       if self.parent_id and self.parent_id.id == self.id:
           raise ValidationError("A genre cannot be its own parent")
   ```

## Tests (TDD Implementation)

### Priority High - Essential Behavior

```python
def test_create_genre_minimal(self):
    """Test creating genre with minimal required data"""

def test_create_genre_empty_name_fails(self):
    """Test that empty or whitespace-only names raise ValidationError"""

def test_parent_hierarchy_validation(self):
    """Test that recursive hierarchies are prevented"""

def test_genre_cannot_be_own_parent(self):
    """Test self-referential parent relationship fails"""
```

### Priority Medium - Hierarchy & Relations

```python
def test_parent_child_relationship(self):
    """Test parent-child relationships work correctly"""

def test_get_hierarchy_path(self):
    """Test that hierarchy path method returns correct sequence"""

def test_get_all_children(self):
    """Test that all descendants are returned correctly"""

def test_get_books_include_children(self):
    """Test books retrieval including child genres"""
```

### Priority Low - Features

```python
def test_code_uniqueness(self):
    """Test that genre codes are unique when specified"""

def test_display_name_hierarchy(self):
    """Test that display_name shows hierarchy context"""
```

## Hierarchy Implementation Notes

### Performance Considerations

- Use `parent_path` for efficient hierarchy queries
- Index on `parent_id` for tree traversal
- Consider materialized path pattern for deep hierarchies

### Hierarchy Methods Implementation

```python
def get_hierarchy_path(self):
    """Returns list of genre names from root to current"""
    path = []
    current = self
    while current:
        path.insert(0, current.name)
        current = current.parent_id
    return path

def get_all_children(self, include_self=False):
    """Returns recordset of all descendant genres"""
    domain = [('parent_path', '=like', self.parent_path + '%')]
    if not include_self:
        domain.append(('id', '!=', self.id))
    return self.search(domain)
```

## External IDs & Compatibility

### Stable External IDs

- Use pattern: `library_base.genre_fiction`, `library_base.genre_science_fiction`
- For hierarchy: `library_base.genre_fiction_fantasy_urban`

### Backwards Compatibility Guarantees

- Field `name` remains required until major version bump
- Hierarchy structure (parent_id/child_ids) will remain stable
- Method signatures for hierarchy navigation will remain stable

## Usage Examples

```python
# Create hierarchy: Fiction > Fantasy > Urban Fantasy
fiction = env['library.genre'].create({'name': 'Fiction'})
fantasy = env['library.genre'].create({'name': 'Fantasy', 'parent_id': fiction.id})
urban_fantasy = env['library.genre'].create({'name': 'Urban Fantasy', 'parent_id': fantasy.id})

# Get all fantasy books (including subgenres)
fantasy_books = fantasy.get_books(include_children=True)

# Get hierarchy path
path = urban_fantasy.get_hierarchy_path()  # ['Fiction', 'Fantasy', 'Urban Fantasy']
```
