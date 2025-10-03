# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class LibraryAuthor(models.Model):
    """
    Represents a person who writes or contributes to books.
    This model serves as the foundational entity for author attribution in the library management system.

    Public API (Contract):
    - Fields: id, name, display_name, partner_id
    - Methods: get_books(), as_dict()
    """

    _name = 'library.author'
    _description = 'Library Author'
    _order = 'name'

    # Inherit for mail features and activity tracking
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Main Fields

    name = fields.Char(
        string='Full Name',
        required=True,
        index=True,
        tracking=True,
        help='Full name of the author'
    )

    birth_date = fields.Date(
        string='Date of Birth',
        tracking=True,
        help='Date of birth of the author'
    )

    death_date = fields.Date(
        string='Date of Death',
        tracking=True,
        help='Date of death of the author'
    )

    country = fields.Char(
        string='Country of Origin',
        help='Country where the author originates from'
    )

    biography = fields.Text(
        string='Biography',
        help='A brief biography of the author'
    )

    # System Fields

    partner_id = fields.Many2one(
        'res.partner',
        string='Contact Information',
        ondelete='set null',
        help='Related contact record for additional information'
    )

    active = fields.Boolean(
        default=True,
        help='Uncheck to archive the author'
    )

    # RELATIONS

    book_ids = fields.Many2many(
        'library.book',
        'library_book_author_rel',
        'author_id',
        'book_id',
        string='Books',
        help='Books authored by this author'
    )

    # COMPUTED FIELDS

    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
        help='Formatted name for UI display with dates'
    )

    books_count = fields.Integer(
        string='Books Count',
        compute='_compute_books_count',
        help='Number of books authored by this author'
    )

    @api.depends('name', 'birth_date', 'death_date')
    def _compute_display_name(self):
        """
        Compute the name to be displayed in the UI, including birth and death years if available.

        @api.depends('name', 'birth_date', 'death_date'):
          - Say to Odoo that this method depends on these fields.
          - If any of these fields change, recalculate the display_name.
          - This ensures the display_name is always up-to-date with the latest data.

        NOTE:  self can be a recordset with multiple records, so always iterate over self.
        """
        for record in self:
            display = record.name or 'Unknown Author'

            # Build information of the dates if available
            if record.birth_date or record.death_date:
                dates = []
                if record.birth_date:
                    dates.append(str(record.birth_date.year))
                if record.death_date:
                    dates.append(str(record.death_date.year))
                display += f" ({' - '.join(dates)})"

            record.display_name = display

    @api.depends('book_ids')
    def _compute_books_count(self):
        """
        Compute the number of books associated with each author.
        """
        for record in self:
            record.books_count = len(record.book_ids)

    @api.constrains('name')
    def _check_name_not_empty(self):
        """
        Ensure that the author's name is not empty.

        @api.constrains('name'):
          - This execute when the 'name' field is set or changed.
          - In create and write operations.
          - If the constraint is violated, a ValidationError is raised. This prevents saving invalid data.
        """
        for record in self:
            if not record.name or not record.name.strip():
                raise ValidationError(
                    "Author's name is required and cannot be empty.")

    @api.constrains('birth_date')
    def _check_birth_date_not_future(self):
        """
        Ensure that the birth date is not set in the future.

        Rules:
        - Nobody can be born in the future.
        - This execute in create and write operations.
        - If the constraint is violated, a ValidationError is raised. This prevents saving invalid data.
        """

        for record in self:
            if record.birth_date and record.birth_date > fields.Date.today():
                raise ValidationError(
                    "The birth date cannot be set in the future.")

    @api.constrains('death_date', 'birth_date')
    def _check_death_after_birth(self):
        """
        Ensure that the death date is after the birth date.

        Rules:
        - An author cannot die before they are born.
        - This execute in create and write operations.
        - If the constraint is violated, a ValidationError is raised. This prevents saving invalid data.
        """

        for record in self:
            if record.death_date and record.birth_date and record.death_date < record.birth_date:
                raise ValidationError(
                    "The death date cannot be before the birth date.")

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override the create method to normalize data.

        @api.model_create_multi:
          - This decorator allows the method to handle the creation of multiple records at once.
          - The vals_list parameter is a list of dictionaries, each containing the values for a new record. This can contain [{'name': 'Author 1'}, {'name': 'Author 2'}, ...].
          - This is more efficient than creating records one by one, especially when dealing with large datasets.

        Custom Behavior:
        - To apply business logic before saving records in the database.
        - Normalization, validation or logging can be performed here, etc.
        - Perform any additional setup or validation as needed before calling super().
        """
        for vals in vals_list:
            if 'name' in vals:
                vals['name'] = self._normalize_name(vals['name'])
        return super().create(vals_list)

    def write(self, vals):
        """
        Override the write method to normalize data in updates.

        write() execute in update operations.
        - author.write({'name': 'New Name'})
        - author.name = "New Name" (in this case, Odoo calls write() behind the scenes)
        """

        if 'name' in vals:
            vals['name'] = self._normalize_name(vals['name'])

        return super().write(vals)

    def _normalize_name(self, name):
        """
        Normalize the author's name by stripping extra spaces and capitalizing each word.
        """
        if not name:
            return name
        return ' '.join(part.capitalize() for part in name.strip().split())

    # PUBLIC API METHODS

    def get_books(self, domain=None):
        """
        Retrieve books associated with the author, optionally filtered by a domain.

        Args:
            domain (list, optional): Optional domain to filter the books.

        Returns:
            recordset: library.book records.

        Use example:
            author = env['library.author'].browse(author_id)
            books = author.get_books([('language', '=', 'en_US')])
        """
        # Now return empty recorset until the library.book model is defined
        if not self:
            return self.env['library.book']
        base_domain = [('author_ids', 'in', self.ids)]
        if domain:
            base_domain.extend(domain)
        # This will fail if library.book model is not defined
        try:
            return self.env['library.book'].search(base_domain)
        except KeyError:
            return self.env['library.book'].browse()

    def as_dict(self, fields=None):
        """
        Return author data as a dictionary to use in APIs.

        Args:
            fields (list, optional): List of fields to include in the dictionary. If not provided, all fields are included.

        Returns:
            dict: Author data as a dictionary.

        Use example:
            author.as_dict(['name', 'country'])
            # {'name': 'Gabriel Garcia Marquez', 'country': 'Colombia'}
        """
        if not fields:
            fields = ['id', 'name', 'country', 'birth_date', 'death_date']

        result = {}
        for field in fields:
            if hasattr(self, field):
                value = getattr(self, field)
                # Manage date fields to serialize them as JSON
                if hasattr(value, 'isoformat'):
                    value = value.isoformat() if value else None
                result[field] = value
        return result

    # STATIC METHOD TO OPTIMIZE SEARCHES
    @api.model
    def search_authors(self, domain=None, limit=None):
        """
        Search for authors based on a domain and return their display names.

        @api.model:
          - This method does not depend on a specific record.
          - It can be called on the model itself, e.g., self.env['library.author'].search_authors(...).
          - Class method, not instance method.

        Args:
            domain (list, optional): Domain to filter authors.
            limit (int, optional): Maximum number of authors to return.

        Returns:
            recordset:  author records.
        """
        if domain is None:
            domain = []
        return self.search(domain, limit=limit, order='name')

    # mail.thread integration

    def _track_subtype(self, init_values):
        """
        Customize the subtypes of tracking for messages.

        mail.thread: 
        - message_post(): Send messages
        - message_ids: View history of messages
        - followers_ids:  Manage followers
        - activity_ids:  Manage activities
        """
        self.ensure_one()
        if 'active' in init_values and not self.active:
            return self.env.ref('library_base.mt_author_archived')
        return super()._track_subtype(init_values)
