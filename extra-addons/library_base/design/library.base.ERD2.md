# Library Base Models - Database Structure

## Core Models

### library_book (Intellectual Works)

| Field             | Type         | Required | Default | Index | Constraint | Description                     |
| ----------------- | ------------ | -------- | ------- | ----- | ---------- | ------------------------------- |
| id                | Integer      | Yes      | auto    | PK    |            | Primary key                     |
| name              | Varchar(255) | Yes      |         | Yes   | not empty  | Title of the work               |
| subtitle          | Varchar(255) | No       |         |       |            | Subtitle if applicable          |
| original_title    | Varchar(255) | No       |         |       |            | Original title if translated    |
| summary           | Text         | No       |         |       |            | Brief description/synopsis      |
| language          | Varchar(10)  | No       |         |       |            | Primary language                |
| original_language | Varchar(10)  | No       |         |       |            | Original language if translated |
| date_created      | Date         | No       |         |       | not future | Original creation date          |
| active            | Boolean      | No       | True    |       |            | Archive flag                    |

### library_edition (Book Manifestations)

| Field           | Type         | Required | Default   | Index  | Constraint    | Description               |
| --------------- | ------------ | -------- | --------- | ------ | ------------- | ------------------------- |
| id              | Integer      | Yes      | auto      | PK     |               | Primary key               |
| book_id         | Integer      | Yes      |           | FK     | cascade       | Link to library_book      |
| publisher_id    | Integer      | No       |           | FK     | set null      | Link to library_publisher |
| date_published  | Date         | No       |           |        | not future    | Publication date          |
| format          | Varchar(20)  | No       | paperback |        |               | Physical format           |
| isbn            | Varchar(17)  | No       |           | Unique | valid ISBN-13 | ISBN identifier           |
| isbn_10         | Varchar(10)  | No       |           |        | valid ISBN-10 | Legacy ISBN-10            |
| edition_number  | Varchar(50)  | No       |           |        |               | Edition number            |
| pages           | Integer      | No       |           |        | positive      | Number of pages           |
| language        | Varchar(10)  | No       |           |        |               | Edition language          |
| dimensions      | Varchar(50)  | No       |           |        |               | Physical dimensions       |
| weight          | Float        | No       |           |        | positive      | Weight in grams           |
| name            | Varchar(255) | No       | computed  |        |               | Display name              |
| copy_count      | Integer      | No       | computed  |        |               | Total copies              |
| available_count | Integer      | No       | computed  |        |               | Available copies          |
| active          | Boolean      | No       | True      |        |               | Archive flag              |
| notes           | Text         | No       |           |        |               | Additional notes          |

### library_book_copy (Physical Items)

| Field                          | Type          | Required | Default   | Index  | Constraint   | Description                    |
| ------------------------------ | ------------- | -------- | --------- | ------ | ------------ | ------------------------------ |
| id                             | Integer       | Yes      | auto      | PK     |              | Primary key                    |
| name                           | Varchar(50)   | Yes      |           | Unique | not empty    | Barcode/identifier             |
| edition_id                     | Integer       | Yes      |           | FK     | cascade      | Link to library_edition        |
| book_id                        | Integer       | No       | related   | FK     |              | Link to library_book (related) |
| status                         | Varchar(20)   | Yes      | available | Yes    | valid status | Operational status             |
| condition                      | Varchar(20)   | No       | good      |        |              | Physical condition             |
| branch_id                      | Integer       | Yes      |           | FK     | restrict     | Current location               |
| location                       | Varchar(100)  | No       |           |        |              | Specific location              |
| area                           | Varchar(50)   | No       |           |        |              | General area                   |
| acquired_date                  | Date          | No       | today     |        |              | Acquisition date               |
| acquisition_type               | Varchar(20)   | No       | purchase  |        |              | How acquired                   |
| purchase_price                 | Decimal(10,2) | No       |           |        | positive     | Purchase price                 |
| currency_id                    | Integer       | No       | company   | FK     |              | Currency                       |
| current_loan_ref               | Varchar(100)  | No       |           |        |              | External loan reference        |
| current_reservation_partner_id | Integer       | No       |           | FK     | set null     | Reserved by partner            |
| last_loan_date                 | Date          | No       |           |        |              | Most recent loan               |
| loan_count                     | Integer       | No       | 0         |        | non-negative | Total loans                    |
| is_reference_only              | Boolean       | No       | False     |        |              | Cannot be loaned               |
| is_reservable                  | Boolean       | No       | True      |        |              | Can be reserved                |
| title                          | Varchar(255)  | No       | related   | Yes    |              | Work title (related)           |
| isbn                           | Varchar(17)   | No       | related   | Yes    |              | ISBN (related)                 |
| publisher_name                 | Varchar(255)  | No       | related   |        |              | Publisher (related)            |
| active                         | Boolean       | No       | True      |        |              | Archive flag                   |
| notes                          | Text          | No       |           |        |              | Additional notes               |

## Supporting Models

### library_author (Authors)

| Field      | Type         | Required | Default | Index | Constraint    | Description         |
| ---------- | ------------ | -------- | ------- | ----- | ------------- | ------------------- |
| id         | Integer      | Yes      | auto    | PK    |               | Primary key         |
| name       | Varchar(255) | Yes      |         | Yes   | not empty     | Full name           |
| birth_date | Date         | No       |         |       | not future    | Date of birth       |
| death_date | Date         | No       |         |       | >= birth_date | Date of death       |
| country    | Varchar(100) | No       |         |       |               | Country of origin   |
| biography  | Text         | No       |         |       |               | Brief biography     |
| partner_id | Integer      | No       |         | FK    | set null      | Contact information |
| active     | Boolean      | No       | True    |       |               | Archive flag        |

### library_publisher (Publishers)

| Field        | Type         | Required | Default | Index | Constraint   | Description         |
| ------------ | ------------ | -------- | ------- | ----- | ------------ | ------------------- |
| id           | Integer      | Yes      | auto    | PK    |              | Primary key         |
| name         | Varchar(255) | Yes      |         | Yes   | not empty    | Publisher name      |
| website      | Varchar(255) | No       |         |       | valid URL    | Official website    |
| founded_year | Integer      | No       |         |       | 1400-current | Year founded        |
| country      | Varchar(100) | No       |         |       |              | Country based       |
| description  | Text         | No       |         |       |              | Brief description   |
| contact_id   | Integer      | No       |         | FK    | set null     | Contact information |
| active       | Boolean      | No       | True    |       |              | Archive flag        |

### library_genre (Categories/Genres)

| Field       | Type         | Required | Default  | Index  | Constraint   | Description       |
| ----------- | ------------ | -------- | -------- | ------ | ------------ | ----------------- |
| id          | Integer      | Yes      | auto     | PK     |              | Primary key       |
| name        | Varchar(255) | Yes      |          | Yes    | not empty    | Genre name        |
| code        | Varchar(20)  | No       |          | Unique |              | Short code        |
| description | Text         | No       |          |        |              | Genre description |
| color       | Integer      | No       |          |        |              | UI color code     |
| parent_id   | Integer      | No       |          | FK     | no recursion | Parent genre      |
| parent_path | Varchar(255) | No       | computed | Yes    |              | Materialized path |
| active      | Boolean      | No       | True     |        |              | Archive flag      |

### library_branch (Library Branches)

| Field          | Type         | Required | Default | Index  | Constraint    | Description        |
| -------------- | ------------ | -------- | ------- | ------ | ------------- | ------------------ |
| id             | Integer      | Yes      | auto    | PK     |               | Primary key        |
| name           | Varchar(255) | Yes      |         | Yes    | not empty     | Branch name        |
| code           | Varchar(10)  | No       |         | Unique |               | Short code         |
| address        | Text         | Yes      |         |        | not empty     | Full address       |
| phone          | Varchar(50)  | No       |         |        |               | Phone number       |
| email          | Varchar(100) | No       |         |        | valid email   | Contact email      |
| opening_hours  | Text         | No       |         |        |               | Operating hours    |
| capacity       | Integer      | No       | 0       |        | non-negative  | Max occupancy      |
| is_main_branch | Boolean      | No       | False   |        | only one main | Main branch flag   |
| status         | Varchar(20)  | No       | draft   |        |               | Operational status |
| manager_id     | Integer      | No       |         | FK     | set null      | Branch manager     |
| region         | Varchar(100) | No       |         |        |               | Geographic region  |
| timezone       | Varchar(50)  | No       |         |        |               | Local timezone     |
| company_id     | Integer      | Yes      | company | FK     |               | Owning company     |
| active         | Boolean      | No       | True    |        |               | Archive flag       |

## Relationship Tables (Many-to-Many)

### library_book_author_rel (Books ↔ Authors)

| Field     | Type    | Required | Index        | Description            |
| --------- | ------- | -------- | ------------ | ---------------------- |
| book_id   | Integer | Yes      | Composite PK | Link to library_book   |
| author_id | Integer | Yes      | Composite PK | Link to library_author |

### library_book_genre_rel (Books ↔ Genres)

| Field    | Type    | Required | Index        | Description           |
| -------- | ------- | -------- | ------------ | --------------------- |
| book_id  | Integer | Yes      | Composite PK | Link to library_book  |
| genre_id | Integer | Yes      | Composite PK | Link to library_genre |

### library_branch_staff_rel (Branches ↔ Staff)

| Field     | Type    | Required | Index        | Description            |
| --------- | ------- | -------- | ------------ | ---------------------- |
| branch_id | Integer | Yes      | Composite PK | Link to library_branch |
| user_id   | Integer | Yes      | Composite PK | Link to res_users      |

## Model Relationships and Cardinalities

### Primary Relationships (One-to-Many)

| Parent Model      | Child Model       | Cardinality | FK Field                       | ondelete | Description                                        |
| ----------------- | ----------------- | ----------- | ------------------------------ | -------- | -------------------------------------------------- |
| library_book      | library_edition   | 1:N (0..\*) | book_id                        | cascade  | One work can have multiple editions                |
| library_edition   | library_book_copy | 1:N (0..\*) | edition_id                     | cascade  | One edition can have multiple copies               |
| library_publisher | library_edition   | 1:N (0..\*) | publisher_id                   | set null | One publisher can publish multiple editions        |
| library_branch    | library_book_copy | 1:N (1..\*) | branch_id                      | restrict | One branch houses multiple copies                  |
| library_genre     | library_genre     | 1:N (0..\*) | parent_id                      | cascade  | Genre hierarchy (self-referential)                 |
| res_users         | library_branch    | 1:N (0..\*) | manager_id                     | set null | One user can manage multiple branches              |
| res_company       | library_branch    | 1:N (1..\*) | company_id                     | restrict | One company owns multiple branches                 |
| res_partner       | library_author    | 1:N (0..\*) | partner_id                     | set null | One partner can be linked to multiple authors      |
| res_partner       | library_publisher | 1:N (0..\*) | contact_id                     | set null | One partner can be contact for multiple publishers |
| res_partner       | library_book_copy | 1:N (0..\*) | current_reservation_partner_id | set null | One partner can reserve multiple copies            |
| res_currency      | library_book_copy | 1:N (0..\*) | currency_id                    | restrict | One currency used for multiple purchases           |

### Many-to-Many Relationships

| Left Model     | Right Model    | Cardinality | Relation Table           | Description                                                           |
| -------------- | -------------- | ----------- | ------------------------ | --------------------------------------------------------------------- |
| library_book   | library_author | M:N         | library_book_author_rel  | Books can have multiple authors, authors can write multiple books     |
| library_book   | library_genre  | M:N         | library_book_genre_rel   | Books can belong to multiple genres, genres contain multiple books    |
| library_branch | res_users      | M:N         | library_branch_staff_rel | Branches can have multiple staff, users can work at multiple branches |

### Computed/Related Relationships

| Model             | Field           | Type     | Source                             | Description                    |
| ----------------- | --------------- | -------- | ---------------------------------- | ------------------------------ |
| library_book_copy | book_id         | related  | edition_id.book_id                 | Quick access to work from copy |
| library_book_copy | title           | related  | edition_id.book_id.name            | Work title for searches        |
| library_book_copy | isbn            | related  | edition_id.isbn                    | Edition ISBN for searches      |
| library_book_copy | publisher_name  | related  | edition_id.publisher_id.name       | Publisher for displays         |
| library_edition   | copy_count      | computed | count(copy_ids)                    | Number of physical copies      |
| library_edition   | available_count | computed | count(copy_ids filtered available) | Available copies count         |

### Relationship Rules and Business Logic

#### Cascade Rules

- **Book deletion**: Cascades to all editions and their copies (Complete removal)
- **Edition deletion**: Cascades to all copies of that edition
- **Genre deletion**: Cascades to child genres (hierarchy maintained)

#### Restrict Rules

- **Branch deletion**: Blocked if copies exist (Operational safety)
- **Currency deletion**: Blocked if used in copy purchases

#### Set Null Rules

- **Publisher deletion**: Edition.publisher_id becomes null (Edition survives)
- **Manager departure**: Branch.manager_id becomes null (Branch continues)
- **Partner deletion**: Author.partner_id becomes null (Author data preserved)

#### Cardinality Constraints

- **Required relationships**: Copy must have branch and edition
- **Optional relationships**: Author doesn't require partner contact
- **Unique relationships**: One main branch per system
- **Hierarchical**: Genres support unlimited nesting depth

### Reference Integrity Notes

#### Strong Dependencies (Cannot exist without)

- Copy → Edition → Book (Three-tier dependency)
- Branch → Company (Organizational requirement)

#### Weak Dependencies (Can exist independently)

- Author ↔ Partner (Contact info optional)
- Publisher ↔ Partner (External contact optional)
- Edition ↔ Publisher (Self-published works possible)

#### Business Rule Dependencies

- Reserved copy must have reservation partner
- On-loan copy should have loan reference
- Main branch cannot be deleted or set inactive

## Key Constraints Summary

### Unique Constraints

- `library_edition.isbn` - ISBN must be unique
- `library_book_copy.name` - Barcode must be unique
- `library_genre.code` - Genre code must be unique (if specified)
- `library_branch.code` - Branch code must be unique (if specified)

### Foreign Key Constraints

- Most FKs use `RESTRICT` to prevent accidental deletion
- Parent-child relationships use `CASCADE` (edition→book, copy→edition)
- Optional relationships use `SET NULL` (publisher, manager, contact)

### Business Logic Constraints

- Only one main branch allowed across system
- Death date must be after birth date
- ISBN validation with checksum
- Status transitions validated in application layer
- Reference copies cannot be marked as on_loan

## Indexes for Performance

### Primary Indexes

- All `name` fields for text searches
- `status` and `branch_id` on copies for availability queries
- `isbn` fields for ISBN searches
- Foreign keys automatically indexed

### Composite Indexes (Recommended)

- `(status, branch_id)` on library_book_copy
- `(book_id, date_published)` on library_edition
- `(parent_id, name)` on library_genre
