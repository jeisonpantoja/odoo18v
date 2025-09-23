# library.edition — Design Specification

## Purpose

Represents specific manifestations or editions of intellectual works. This model captures publication-specific information like ISBN, publisher, format, and publication date that varies between different editions of the same work.

## Public API (Contract)

### Fields (Public Interface)

- **id** (int): Primary key
- **name** (char, computed): Display name combining work title and edition details
- **book_id** (many2one library.book, required): The intellectual work this edition represents
- **publisher_id** (many2one library.publisher): Publisher of this specific edition
- **isbn** (char): ISBN-13 identifier for this edition
- **format** (selection): Physical format (hardcover, paperback, ebook, etc.)

### Methods (Public Interface)

- **get_copies(self, domain=None)** → recordset(library.book_copy): Returns physical copies of this edition
- **get_availability(self, branch=None)** → dict: Returns availability statistics for this edition
- **normalize_isbn(self, isbn_value)** → str: Normalizes and validates ISBN input
- **as_dict(self, fields=None)** → dict: Returns edition data as dictionary for API usage

## Fields (Detailed Implementation)

### Core Bibliographic Fields

- **book_id**: Many2one('library.book', required=True, ondelete='cascade', index=True)
  - Help: "The intellectual work this edition represents"
- **publisher_id**: Many2one('library.publisher', ondelete='set null')
  - Help: "Publisher of this specific edition"
- **date_published**: Date(optional)
  - Help: "Publication date of this edition"
- **format**: Selection([
  ('hardcover', 'Hardcover'),
  ('paperback', 'Paperback'),
  ('ebook', 'E-book'),
  ('audiobook', 'Audiobook'),
  ('magazine', 'Magazine'),
  ('other', 'Other')
  ], default='paperback')
  - Help: "Physical format of this edition"

### ISBN and Identification

- **isbn**: Char(size=17, index=True)
  - Help: "ISBN-13 identifier for this edition"
  - Normalized automatically (spaces and hyphens removed)
- **isbn_10**: Char(size=10)
  - Help: "Legacy ISBN-10 (automatically converted from ISBN-13)"
- **edition_number**: Char(optional)
  - Help: "Edition number (1st, 2nd, Revised, etc.)"

### Physical Properties

- **pages**: Integer(optional)
  - Help: "Number of pages in this edition"
- **language**: Char(optional)
  - Help: "Language of this edition (if different from work language)"
- **dimensions**: Char(optional)
  - Help: "Physical dimensions (e.g., '23 x 15 cm')"
- **weight**: Float(optional)
  - Help: "Weight in grams"

### System Fields

- **name**: Char(compute='\_compute_name', store=True)
  - Computed display name for UI
- **active**: Boolean(default=True)
  - Help: "Uncheck to archive this edition"
- **notes**: Text(optional)
  - Help: "Additional notes about this edition"

## Relations

### Direct Relations

- **copy_ids**: One2many('library.book_copy', 'edition_id')
  - Physical copies of this edition
  - Cascade delete: if edition deleted, copies are deleted

### Computed Relations

- **copy_count**: Integer(compute='\_compute_copy_stats', store=True)
  - Total number of copies of this edition
- **available_count**: Integer(compute='\_compute_copy_stats', store=True)
  - Number of copies currently available

## Constraints & Validations

### Database Constraints

```python
_sql_constraints = [
    ('uniq_edition_isbn', 'unique(isbn)', 'ISBN must be unique across all editions'),
    ('check_pages_positive', 'check(pages > 0)', 'Number of pages must be positive'),
]
```

### Model Constraints

1. **ISBN validation**:

   ```python
   @api.constrains('isbn', 'isbn_10')
   def _check_isbn_valid(self):
       for record in self:
           if record.isbn and not self._is_valid_isbn13(record.isbn):
               raise ValidationError("Invalid ISBN-13 format")
           if record.isbn_10 and not self._is_valid_isbn10(record.isbn_10):
               raise ValidationError("Invalid ISBN-10 format")
   ```

2. **Date validation**:

   ```python
   @api.constrains('date_published')
   def _check_date_not_future(self):
       if self.date_published and self.date_published > fields.Date.today():
           raise ValidationError("Publication date cannot be in the future")
   ```

3. **Work relationship validation**:
   ```python
   @api.constrains('book_id')
   def _check_book_exists(self):
       if not self.book_id:
           raise ValidationError("Edition must be linked to a work")
   ```

## Computed Fields Implementation

### Display Name

```python
@api.depends('book_id.name', 'publisher_id.name', 'date_published', 'format')
def _compute_name(self):
    for record in self:
        parts = [record.book_id.name if record.book_id else 'Unknown Work']
        if record.publisher_id:
            parts.append(record.publisher_id.name)
        if record.date_published:
            parts.append(str(record.date_published.year))
        if record.format:
            parts.append(record.format.title())
        record.name = ' - '.join(parts)
```

### Copy Statistics

```python
@api.depends('copy_ids.status')
def _compute_copy_stats(self):
    for record in self:
        copies = record.copy_ids
        record.copy_count = len(copies)
        record.available_count = len(copies.filtered(lambda c: c.status == 'available'))
```

## Business Logic Methods

### ISBN Handling

```python
def normalize_isbn(self, isbn_value):
    """Normalize ISBN by removing spaces and hyphens, converting to uppercase"""
    if not isbn_value:
        return False

    # Remove common separators
    normalized = ''.join(isbn_value.split())
    normalized = normalized.replace('-', '').replace(' ', '').upper()

    # Convert empty strings to False for database NULL handling
    return normalized if normalized else False

@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if 'isbn' in vals:
            vals['isbn'] = self.normalize_isbn(vals['isbn'])
            # Auto-convert to ISBN-10 if needed
            if vals['isbn'] and len(vals['isbn']) == 13 and vals['isbn'].startswith('978'):
                vals['isbn_10'] = self._convert_isbn13_to_isbn10(vals['isbn'])
    return super().create(vals_list)

def write(self, vals):
    if 'isbn' in vals:
        vals['isbn'] = self.normalize_isbn(vals['isbn'])
        if vals['isbn'] and len(vals['isbn']) == 13 and vals['isbn'].startswith('978'):
            vals['isbn_10'] = self._convert_isbn13_to_isbn10(vals['isbn'])
    return super().write(vals)
```

### Availability Methods

```python
def get_availability(self, branch=None):
    """Returns availability statistics for this edition"""
    domain = [('edition_id', '=', self.id)]
    if branch:
        domain.append(('branch_id', '=', branch.id))

    copies = self.env['library.book_copy'].search(domain)
    available = copies.filtered(lambda c: c.status == 'available')

    branch_stats = {}
    for copy in available:
        branch_name = copy.branch_id.name if copy.branch_id else 'No Branch'
        branch_stats[branch_name] = branch_stats.get(branch_name, 0) + 1

    return {
        'total_copies': len(copies),
        'available_copies': len(available),
        'branch_availability': branch_stats,
        'is_available': len(available) > 0
    }
```

## ISBN Utility Functions (External)

### Location: `library_base/utils/isbn.py`

```python
def is_valid_isbn13(isbn):
    """Validate ISBN-13 checksum"""
    if not isbn or len(isbn) != 13 or not isbn.isdigit():
        return False

    checksum = sum(int(digit) * (1 if i % 2 == 0 else 3)
                  for i, digit in enumerate(isbn[:-1]))
    return (10 - (checksum % 10)) % 10 == int(isbn[-1])

def is_valid_isbn10(isbn):
    """Validate ISBN-10 checksum"""
    if not isbn or len(isbn) != 10:
        return False

    checksum = sum(int(digit) * (10 - i) for i, digit in enumerate(isbn[:-1]))
    check_digit = isbn[-1]
    expected = (11 - (checksum % 11)) % 11

    if expected == 10:
        return check_digit.upper() == 'X'
    return int(check_digit) == expected

def convert_isbn10_to_isbn13(isbn10):
    """Convert ISBN-10 to ISBN-13"""
    if not is_valid_isbn10(isbn10):
        return None

    isbn13_base = '978' + isbn10[:-1]
    checksum = sum(int(digit) * (1 if i % 2 == 0 else 3)
                  for i, digit in enumerate(isbn13_base))
    check_digit = (10 - (checksum % 10)) % 10
    return isbn13_base + str(check_digit)
```

## Tests (TDD Implementation)

### Priority High - Core Functionality

```python
def test_create_edition_minimal(self):
    """Test creating edition with minimal required data (book_id)"""

def test_create_edition_without_book_fails(self):
    """Test that editions without book_id raise ValidationError"""

def test_isbn_normalization_on_create(self):
    """Test that ISBNs are normalized automatically"""

def test_isbn_uniqueness_constraint(self):
    """Test that duplicate ISBNs raise IntegrityError"""

def test_multiple_blank_isbn_allowed(self):
    """Test that multiple editions can have empty ISBN"""

def test_isbn13_validation(self):
    """Test ISBN-13 checksum validation"""

def test_isbn10_validation(self):
    """Test ISBN-10 checksum validation"""
```

### Priority Medium - Business Logic

```python
def test_display_name_computation(self):
    """Test that display name includes work, publisher, year, format"""

def test_copy_count_statistics(self):
    """Test that copy_count and available_count compute correctly"""

def test_get_availability_method(self):
    """Test availability statistics by branch"""

def test_isbn10_auto_conversion(self):
    """Test automatic conversion from ISBN-13 to ISBN-10"""

def test_date_published_not_future(self):
    """Test that future publication dates are rejected"""
```

### Priority Low - Edge Cases

```python
def test_edition_cascade_delete(self):
    """Test that deleting work cascades to editions"""

def test_special_format_handling(self):
    """Test handling of ebook and audiobook formats"""
```

## External IDs & Compatibility

### Stable External IDs

- Use pattern: `library_base.edition_quixote_penguin_2010`, `library_base.edition_hamlet_oxford_2015`

### Backwards Compatibility Guarantees

- Field `book_id` will remain required
- ISBN normalization behavior will remain consistent
- Method `get_availability()` signature will remain stable

## Integration Notes

### Search Integration

- ISBN searches target this model primarily
- Title searches go to work level, then navigate to editions
- Format-specific searches use this model's format field

### Future Extensions

- ONIX import/export compatibility
- Multiple ISBN support (ISBN table)
- Digital rights management for ebooks
- Print-on-demand integration

## Usage Examples

```python
# Create edition with ISBN validation
edition = env['library.edition'].create({
    'book_id': work.id,
    'publisher_id': penguin.id,
    'isbn': '978-0-14-044729-4',
    'format': 'paperback',
    'date_published': '2003-01-01',
    'pages': 1056
})

# Get availability across branches
availability = edition.get_availability()
# {'total_copies': 3, 'available_copies': 2, 'branch_availability': {'Main': 1, 'North': 1}}

# Search by ISBN
edition = env['library.edition'].search([('isbn', '=', '9780140447294')])
```
