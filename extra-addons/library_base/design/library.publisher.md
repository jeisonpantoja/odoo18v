# library.publisher — Design Specification

## Purpose
Represents publishing companies or organizations that publish books. This model serves as the foundational entity for publisher attribution and contact management in the library system.

## Public API (Contract)

### Fields (Public Interface)
- **id** (int): Primary key
- **name** (char, required): Name of the publishing company
- **display_name** (computed): Formatted name for UI display
- **contact_id** (many2one res.partner, optional): Link to publisher's contact information

### Methods (Public Interface)
- **get_books(self, domain=None)** → recordset(library.book): Returns books published by this company
- **as_dict(self, fields=None)** → dict: Returns publisher data as dictionary for API usage
- **search_publishers(domain, limit)** (static): Helper for efficient publisher searches

## Fields (Detailed Implementation)

### Core Fields
- **name**: Char(required=True, index=True)
  - Help: "Name of the publishing company"
  - Normalized on create/write (trim spaces, collapse multiple spaces)
- **website**: Char(optional)
  - Help: "Publisher's official website URL"
- **founded_year**: Integer(optional)
  - Help: "Year the publisher was founded"
  - Constraint: Cannot be in the future, must be reasonable (e.g., >= 1400)
- **country**: Char(optional)
  - Help: "Country where publisher is based"
- **description**: Text(optional)
  - Help: "Brief description of the publisher"

### System Fields
- **contact_id**: Many2one('res.partner', ondelete='set null')
  - Help: "Contact information for the publisher"
- **active**: Boolean(default=True)
  - Help: "Uncheck to archive the publisher"

## Relations

### Direct Relations
- **book_ids**: One2many('library.book', 'publisher_id')
  - Shows all books published by this company
  - Inverse of library.book.publisher_id

## Constraints & Validations

### Essential Constraints
1. **Name validation**:
   ```python
   @api.constrains('name')
   def _check_name_not_empty(self):
       if not self.name or not self.name.strip():
           raise ValidationError("Publisher name is required")
   ```

2. **Founded year validation**:
   ```python
   @api.constrains('founded_year')
   def _check_founded_year_reasonable(self):
       current_year = fields.Date.today().year
       if self.founded_year and (self.founded_year > current_year or self.founded_year < 1400):
           raise ValidationError("Founded year must be between 1400 and current year")
   ```

3. **Website format validation** (optional):
   ```python
   @api.constrains('website')
   def _check_website_format(self):
       if self.website and not self.website.startswith(('http://', 'https://')):
           raise ValidationError("Website must start with http:// or https://")
   ```

## Tests (TDD Implementation)

### Priority High - Essential Behavior
```python
def test_create_publisher_minimal(self):
    """Test creating publisher with minimal required data"""

def test_create_publisher_empty_name_fails(self):
    """Test that empty or whitespace-only names raise ValidationError"""

def test_founded_year_validation(self):
    """Test that invalid founded years are rejected"""

def test_website_format_validation(self):
    """Test that websites must have proper protocol"""
```

### Priority Medium - Relations & Helpers
```python
def test_contact_id_optional(self):
    """Test that contact_id can be None or valid res.partner"""

def test_get_books_helper(self):
    """Test that get_books() returns correct book recordset"""

def test_book_ids_relation(self):
    """Test that book_ids One2many relationship works correctly"""
```

## External IDs & Compatibility

### Stable External IDs
- Use pattern: `library_base.publisher_demo_penguin`, `library_base.publisher_demo_oxford`

### Backwards Compatibility Guarantees
- Field `name` remains required until major version bump
- Method `get_books()` signature will remain stable
- Field `contact_id` will remain optional