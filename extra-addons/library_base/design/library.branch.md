# library.branch — Design Specification

## Purpose

Represents physical library locations or branches for multi-location library systems. This model serves as the foundational entity for location-based operations, inventory management, and regional administration.

## Public API (Contract)

### Fields (Public Interface)

- **id** (int): Primary key
- **name** (char, required): Name of the library branch
- **display_name** (computed): Formatted name for UI display
- **code** (char, optional): Short code for the branch (for reports, barcodes)
- **manager_id** (many2one res.users, optional): Branch manager
- **region_id** (many2one res.country.state, optional): Region/area for higher-level reporting
- **book_copy_ids** (one2many library.book_copy): Copies held at this branch

### Methods (Public Interface)

- **get_book_copies(self, domain=None)** → recordset(library.book_copy): Returns book copies located in this branch
- **get_active_staff(self)** → recordset(res.users): Returns active staff assigned to this branch
- **as_dict(self, fields=None)** → dict: Returns branch data as dictionary for API usage
- **is_operational(self)** → bool: Returns True if branch is open and operational

## Fields (Detailed Implementation)

### Core Fields

- **name**: Char(required=True, index=True)
  - Help: "Name of the library branch"
  - Normalized on create/write (trim spaces, collapse multiple spaces)
- **code**: Char(optional, index=True, size=10)
  - Help: "Short code for the branch (e.g., 'MAIN', 'NORTH', 'DT01')"
  - Used for reports, integration, and quick reference
- **address**: Text(required=True)
  - Help: "Full address of the branch"
- **phone**: Char(optional)
  - Help: "Main phone number for the branch"
- **email**: Char(optional)
  - Help: "Contact email for the branch"

### Operational Fields

- **opening_hours**: Text(optional)
  - Help: "Branch operating hours (free text or structured)"
- **capacity**: Integer(optional, default=0)
  - Help: "Maximum occupancy or seating capacity"
- **is_main_branch**: Boolean(default=False)
  - Help: "Check if this is the main/headquarters branch"
- **status**: Selection([
  ('draft', 'Draft'),
  ('active', 'Active'),
  ('maintenance', 'Under Maintenance'),
  ('closed', 'Permanently Closed')
  ], default='draft')
  - Help: "Current operational status of the branch"

### Management Fields

- **manager_id**: Many2one('res.users', ondelete='set null')
  - Help: "Branch manager or head librarian"
- **region**: Char(optional)
  - Help: "Geographic region or administrative area"
- **timezone**: Selection(optional)
  - Help: "Local timezone for the branch"
  - Default: from company settings

### System Fields

- **company_id**: Many2one('res.company', default=lambda self: self.env.company)
  - Help: "Company this branch belongs to"
- **active**: Boolean(default=True)
  - Help: "Uncheck to archive the branch"

```python
name = fields.Char(required=True, index=True, help="Branch official name")
address = fields.Text(string="Address")
region_id = fields.Many2one('res.country.state', string="Region", ondelete='set null')
manager_id = fields.Many2one('res.users', string="Branch Manager", ondelete='set null')
active = fields.Boolean(default=True)
book_copy_ids = fields.One2many('library.book_copy', 'branch_id', string="Book Copies")
books_count = fields.Integer(compute='_compute_books_count', store=True)
```
- books_count: computed field for reporting dashboards; uses len(book_copy_ids.mapped('book_id')).

## Relations

### Direct Relations

- **book_copy_ids**: One2many('library.book_copy', 'branch_id')
  - Shows all book copies located in this branch
  - Inverse of library.book_copy.branch_id
- **staff_ids**: Many2many('res.users', 'library_branch_staff_rel', 'branch_id', 'user_id')
  - Staff members assigned to this branch
  - Used for access control and reporting

## Constraints & Validations

### Essential Constraints

1. **Name validation**:

   ```python
   @api.constrains('name')
   def _check_name_not_empty(self):
       if not self.name or not self.name.strip():
           raise ValidationError("Branch name is required")
   ```

2. **Address validation**:

   ```python
   @api.constrains('address')
   def _check_address_not_empty(self):
       if not self.address or not self.address.strip():
           raise ValidationError("Branch address is required")
   ```

3. **Code uniqueness** (if used):

   ```python
   @api.constrains('code')
   def _check_code_unique(self):
       if self.code and self.search_count([('code', '=', self.code), ('id', '!=', self.id)]) > 0:
           raise ValidationError("Branch code must be unique")
   ```

4. **Main branch logic**:

   ```python
   @api.constrains('is_main_branch')
   def _check_single_main_branch(self):
       if self.is_main_branch:
           main_branches = self.search([('is_main_branch', '=', True), ('id', '!=', self.id)])
           if main_branches:
               raise ValidationError("Only one branch can be designated as main branch")
   ```

5. **Operational status logic**:
   ```python
   @api.constrains('status')
   def _check_main_branch_status(self):
       if self.is_main_branch and self.status == 'closed':
           raise ValidationError("Main branch cannot be permanently closed")
   ```

## Tests (TDD Implementation)

### Priority High - Essential Behavior

```python
def test_create_branch_minimal(self):
    """Test creating branch with minimal required data (name + address)"""

def test_create_branch_empty_name_fails(self):
    """Test that empty or whitespace-only names raise ValidationError"""

def test_create_branch_empty_address_fails(self):
    """Test that empty address raises ValidationError"""

def test_code_uniqueness_validation(self):
    """Test that branch codes must be unique when specified"""

def test_single_main_branch_constraint(self):
    """Test that only one branch can be main branch"""
```

### Priority Medium - Business Logic

```python
def test_main_branch_cannot_be_closed(self):
    """Test that main branch cannot have status 'closed'"""

def test_manager_id_optional(self):
    """Test that manager_id can be None or valid res.users"""

def test_is_operational_method(self):
    """Test that is_operational returns correct boolean based on status"""

def test_get_active_staff(self):
    """Test that get_active_staff returns correct user recordset"""
```

### Priority Low - Relations

```python
def test_book_copy_ids_relation(self):
    """Test that book_copy_ids One2many relationship works correctly"""

def test_staff_ids_relation(self):
    """Test that staff_ids Many2many relationship works correctly"""
```

## Business Logic Implementation

### Operational Status Methods

```python
def is_operational(self):
    """Returns True if branch is open and operational"""
    return self.status == 'active'

def get_active_staff(self):
    """Returns active staff assigned to this branch"""
    return self.staff_ids.filtered('active')
```

## External IDs & Compatibility

### Stable External IDs

- Use pattern: `library_base.branch_main`, `library_base.branch_north`, `library_base.branch_downtown`

### Backwards Compatibility Guarantees

- Fields `name` and `address` remain required until major version bump
- Field `is_main_branch` logic will remain stable
- Method `is_operational()` signature will remain stable

## Integration Notes

### Future Extensions (library_management)

- This model will be referenced by loan records for location tracking
- Regional managers will use this for territory-based reporting
- Inventory transfers will use branch_id for tracking movements

### Security Considerations

- Branch-based record rules will use this model for data segregation
- Regional access control will depend on staff_ids relationship

## Usage Examples

```python
# Create main branch
main_branch = env['library.branch'].create({
    'name': 'Main Library',
    'code': 'MAIN',
    'address': '123 Library Street, City, State 12345',
    'is_main_branch': True,
    'status': 'active',
})

# Check if operational
if main_branch.is_operational():
    print("Branch is open for business")

# Get branch inventory
branch_books = main_branch.get_book_copies()
```
