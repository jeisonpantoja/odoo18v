# library.book_copy — Design Specification

## Purpose

Represents individual physical or digital items in the library's inventory. Each copy represents a specific, trackable instance that can be loaned, reserved, maintained, or tracked through its operational lifecycle.

## Public API (Contract)

### Fields (Public Interface)

- **id** (int): Primary key
- **name** (char, required): Barcode or inventory identifier
- **edition_id** (many2one library.edition, required): The edition this copy represents
- **status** (selection): Current operational status
- **branch_id** (many2one library.branch): Current location
- **condition** (selection): Physical condition

### Methods (Public Interface)

- **is_available(self)** → bool: Quick availability check
- **can_be_loaned(self, partner_id=None)** → tuple(bool, reason): Validates loan eligibility
- **mark_on_loan(self, external_ref=None, actor_id=None)** → bool: Transition to on_loan status
- **mark_returned(self, actor_id=None)** → bool: Transition to available status
- **mark_reserved(self, partner_id=None, external_ref=None)** → bool: Transition to reserved status
- **as_dict(self, fields=None)** → dict: Returns copy data for API usage

## Fields (Detailed Implementation)

### Core Identification

- **name**: Char(required=True, index=True, size=50)
  - Help: "Barcode, RFID tag, or inventory code for this copy"
  - Must be unique across all copies
- **edition_id**: Many2one('library.edition', required=True, ondelete='cascade', index=True)
  - Help: "The specific edition this copy represents"
- **book_id**: Many2one('library.book', related='edition_id.book_id', store=True, index=True)
  - Help: "The work this copy represents (for quick searches)"

### Operational Status

- **status**: Selection([
  ('available', 'Available'),
  ('on_loan', 'On Loan'),
  ('reserved', 'Reserved'),
  ('maintenance', 'Under Maintenance'),
  ('lost', 'Lost'),
  ('missing', 'Missing'),
  ('archived', 'Archived')
  ], default='available', required=True, index=True)

  - Help: "Current operational status of this copy"

- **condition**: Selection([
  ('excellent', 'Excellent'),
  ('good', 'Good'),
  ('fair', 'Fair'),
  ('poor', 'Poor'),
  ('damaged', 'Damaged')
  ], default='good')
  - Help: "Physical condition of this copy"

### Location and Management

- **branch_id**: Many2one('library.branch', required=True, ondelete='restrict')
  - Help: "Current branch location of this copy"
- **location**: Char(size=100)
  - Help: "Specific location within branch (shelf, room, etc.)"
- **area**: Char(size=50)
  - Help: "General area classification (Reference, Fiction, etc.)"

### Acquisition and Ownership

- **acquired_date**: Date(default=fields.Date.today)
  - Help: "Date this copy was acquired by the library"
- **acquisition_type**: Selection([
  ('purchase', 'Purchase'),
  ('donation', 'Donation'),
  ('exchange', 'Exchange'),
  ('other', 'Other')
  ], default='purchase')
  - Help: "How this copy was acquired"
- **purchase_price**: Monetary(currency_field='currency_id')
  - Help: "Purchase price of this copy"
- **currency_id**: Many2one('res.currency', default=lambda self: self.env.company.currency_id)

### Operational Tracking (Neutral External References)

- **current_loan_ref**: Char(size=100)
  - Help: "External reference to current loan (managed by library_management)"
- **current_reservation_partner_id**: Many2one('res.partner', ondelete='set null')
  - Help: "Partner who has reserved this copy"
- **last_loan_date**: Date()
  - Help: "Date of most recent loan"
- **loan_count**: Integer(default=0)
  - Help: "Total number of times this copy has been loaned"

### Special Properties

- **is_reference_only**: Boolean(default=False)
  - Help: "Check if this copy cannot leave the library premises"
- **is_reservable**: Boolean(default=True)
  - Help: "Check if this copy can be reserved by patrons"

### System Fields

- **active**: Boolean(default=True)
  - Help: "Uncheck to archive this copy"
- **notes**: Text()
  - Help: "Additional notes about this copy"

## Relations

### Computed Display Fields (Performance Optimization)

- **title**: Char(related='edition_id.book_id.name', store=True, index=True)
  - Help: "Work title for quick searches and displays"
- **isbn**: Char(related='edition_id.isbn', store=True, index=True)
  - Help: "ISBN for quick searches"
- **publisher_name**: Char(related='edition_id.publisher_id.name', store=True)
  - Help: "Publisher name for displays"

## Constraints & Validations

### Database Constraints

```python
_sql_constraints = [
    ('uniq_copy_name', 'unique(name)', 'Copy barcode/identifier must be unique'),
    ('check_purchase_price_positive', 'check(purchase_price >= 0)', 'Purchase price must be positive'),
    ('check_loan_count_positive', 'check(loan_count >= 0)', 'Loan count cannot be negative'),
]
```

### Model Constraints

1. **Status transition validation**:

   ```python
   @api.constrains('status', 'is_reference_only')
   def _check_status_transitions(self):
       for record in self:
           if record.status == 'on_loan' and record.is_reference_only:
               raise ValidationError("Reference-only copies cannot be marked as on loan")
   ```

2. **Reservation consistency**:

   ```python
   @api.constrains('status', 'current_reservation_partner_id')
   def _check_reservation_consistency(self):
       for record in self:
           if record.status == 'reserved' and not record.current_reservation_partner_id:
               raise ValidationError("Reserved copies must have a reservation partner")
           if record.status != 'reserved' and record.current_reservation_partner_id:
               record.current_reservation_partner_id = False
   ```

3. **Location requirements**:
   ```python
   @api.constrains('branch_id', 'status')
   def _check_location_for_available(self):
       for record in self:
           if record.status in ('available', 'reserved') and not record.branch_id:
               raise ValidationError("Available and reserved copies must have a branch location")
   ```

## Business Logic Methods

### Availability Checks

```python
def is_available(self):
    """Quick check if copy is available for loan"""
    return self.status == 'available' and self.active

def can_be_loaned(self, partner_id=None):
    """Comprehensive loan eligibility check"""
    if not self.active:
        return False, "Copy is archived"

    if self.is_reference_only:
        return False, "Reference copy cannot be loaned"

    if self.status == 'maintenance':
        return False, "Copy is under maintenance"

    if self.status == 'lost':
        return False, "Copy is marked as lost"

    if self.status == 'reserved':
        if partner_id and self.current_reservation_partner_id.id == partner_id:
            return True, "Available for reserved partner"
        return False, "Copy is reserved by another patron"

    if self.status == 'on_loan':
        return False, "Copy is currently on loan"

    if self.condition == 'damaged':
        return False, "Copy is damaged"

    return self.status == 'available', "Copy is available"
```

### State Transition Methods (Neutral/Decoupled)

```python
def mark_on_loan(self, external_ref=None, actor_id=None):
    """Mark copy as on loan with external reference"""
    can_loan, reason = self.can_be_loaned()
    if not can_loan:
        raise ValidationError(f"Cannot loan copy: {reason}")

    vals = {
        'status': 'on_loan',
        'current_loan_ref': external_ref,
        'last_loan_date': fields.Date.today(),
        'loan_count': self.loan_count + 1,
        'current_reservation_partner_id': False  # Clear reservation
    }

    self.write(vals)
    self._post_status_change_message('on_loan', actor_id, external_ref)
    return True

def mark_returned(self, actor_id=None):
    """Mark copy as returned and available"""
    if self.status != 'on_loan':
        raise ValidationError("Only loaned copies can be returned")

    vals = {
        'status': 'available',
        'current_loan_ref': False,
    }

    self.write(vals)
    self._post_status_change_message('returned', actor_id)
    return True

def mark_reserved(self, partner_id=None, external_ref=None):
    """Mark copy as reserved for specific partner"""
    if not self.is_available():
        raise ValidationError("Only available copies can be reserved")

    if not self.is_reservable:
        raise ValidationError("This copy cannot be reserved")

    vals = {
        'status': 'reserved',
        'current_reservation_partner_id': partner_id,
    }

    self.write(vals)
    self._post_status_change_message('reserved', partner_id, external_ref)
    return True

def mark_lost(self, actor_id=None, reason=None):
    """Mark copy as lost"""
    vals = {
        'status': 'lost',
        'current_loan_ref': False,
        'current_reservation_partner_id': False,
    }

    self.write(vals)
    self._post_status_change_message('lost', actor_id, reason)
    return True
```

### Utility Methods

```python
def _post_status_change_message(self, action, actor_id=None, reference=None):
    """Post audit message for status changes"""
    actor_name = 'System'
    if actor_id:
        actor = self.env['res.users'].browse(actor_id)
        actor_name = actor.name if actor.exists() else f'User {actor_id}'

    message = f"Copy {action} by {actor_name}"
    if reference:
        message += f" (Ref: {reference})"

    self.message_post(body=message, message_type='comment')

def assign_to_branch(self, branch, location=None):
    """Move copy to different branch with validation"""
    if self.status == 'on_loan':
        raise ValidationError("Cannot move copies that are currently on loan")

    vals = {'branch_id': branch.id}
    if location:
        vals['location'] = location

    self.write(vals)
    return True
```

## Tests (TDD Implementation)

### Priority High - Core Functionality

```python
def test_create_copy_minimal(self):
    """Test creating copy with minimal required data"""

def test_copy_barcode_uniqueness(self):
    """Test that duplicate barcodes raise IntegrityError"""

def test_is_available_basic_check(self):
    """Test basic availability checking"""

def test_can_be_loaned_reference_only(self):
    """Test that reference copies cannot be loaned"""

def test_mark_on_loan_valid_transition(self):
    """Test successful loan marking"""

def test_mark_on_loan_invalid_status(self):
    """Test loan marking fails for non-available copies"""

def test_mark_returned_valid_transition(self):
    """Test successful return marking"""

def test_mark_reserved_valid_transition(self):
    """Test successful reservation marking"""
```

### Priority Medium - Business Logic

```python
def test_status_transition_validation(self):
    """Test that invalid status transitions are prevented"""

def test_reservation_consistency_constraint(self):
    """Test that reserved status requires partner_id"""

def test_loan_count_increment(self):
    """Test that loan_count increments on each loan"""

def test_assign_to_branch_validation(self):
    """Test branch assignment with validation"""

def test_message_posting_on_status_change(self):
    """Test that status changes create audit messages"""
```

### Priority Low - Edge Cases

```python
def test_related_fields_computation(self):
    """Test that related fields (title, isbn) compute correctly"""

def test_cascade_delete_from_edition(self):
    """Test that deleting edition cascades to copies"""

def test_archived_copy_cannot_be_loaned(self):
    """Test that archived copies are excluded from operations"""
```

## Performance Considerations

### Indexing Strategy

- Primary searches: `name` (barcode), `status`, `branch_id`
- Related field indexes: `title`, `isbn` for quick searches
- Composite indexes: consider `(status, branch_id)` for availability queries

### Stored Related Fields

- `title`, `isbn`, `publisher_name` stored for list view performance
- Trade-off: faster reads vs slower writes on edition updates
- Justified for high-read, low-write scenarios

## External IDs & Compatibility

### Stable External IDs

- Use pattern: `library_base.copy_[branch_code]_[sequence]`
- Example: `library_base.copy_main_001`, `library_base.copy_north_123`

### Migration Support

- `external_id` field for legacy system references
- Batch import utilities should validate barcode uniqueness
- Support for barcode format conversion/standardization

## Integration Notes

### API Usage by library_management

```python
# Check availability before creating loan
copy = env['library.book_copy'].browse(copy_id)
can_loan, reason = copy.can_be_loaned(partner.id)
if can_loan:
    loan = create_loan_record(copy, partner)
    copy.mark_on_loan(external_ref=loan.name, actor_id=current_user.id)
```

### Search Integration

- Barcode searches target this model directly
- Title/author searches can filter by copy availability
- Branch-specific availability through `branch_id` filtering

## Usage Examples

```python
# Create new copy
copy = env['library.book_copy'].create({
    'name': 'BC-2025-001',
    'edition_id': edition.id,
    'branch_id': main_branch.id,
    'location': 'A-3-15',
    'condition': 'excellent'
})

# Check if can be loaned
available, reason = copy.can_be_loaned(partner.id)

# Loan process (called by library_management)
if available:
    copy.mark_on_loan(external_ref='LOAN-2025-001', actor_id=librarian.id)

# Return process
copy.mark_returned(actor_id=librarian.id)
```
