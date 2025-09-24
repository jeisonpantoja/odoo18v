# Library Base - Entity Relationship Diagram

```mermaid
erDiagram
    %% Core Models
    LIBRARY_BOOK {
        int id PK
        varchar name "required, index"
        varchar subtitle "optional"
        varchar original_title "optional"
        text summary "optional"
        varchar language "optional"
        varchar original_language "optional"
        date date_created "optional"
        boolean active "default=True"
    }

    LIBRARY_EDITION {
        int id PK
        int book_id FK "required, index"
        int publisher_id FK "optional"
        date date_published "optional"
        varchar format "default=paperback"
        varchar isbn "index, unique"
        varchar isbn_10 "optional"
        varchar edition_number "optional"
        int pages "optional"
        varchar language "optional"
        varchar dimensions "optional"
        float weight "optional"
        varchar name "computed, stored"
        int copy_count "computed, stored"
        int available_count "computed, stored"
        boolean active "default=True"
        text notes "optional"
    }

    LIBRARY_BOOK_COPY {
        int id PK
        varchar name "required, index, unique"
        int edition_id FK "required, index"
        int book_id FK "related, stored, index"
        varchar status "required, index, default=available"
        varchar condition "default=good"
        int branch_id FK "required"
        varchar location "optional"
        varchar area "optional"
        date acquired_date "default=today"
        varchar acquisition_type "default=purchase"
        decimal purchase_price "optional"
        int currency_id FK "optional"
        varchar current_loan_ref "optional"
        int current_reservation_partner_id FK "optional"
        date last_loan_date "optional"
        int loan_count "default=0"
        boolean is_reference_only "default=False"
        boolean is_reservable "default=True"
        varchar title "related, stored, index"
        varchar isbn "related, stored, index"
        varchar publisher_name "related, stored"
        boolean active "default=True"
        text notes "optional"
    }

    %% Supporting Models
    LIBRARY_AUTHOR {
        int id PK
        varchar name "required, index"
        date birth_date "optional"
        date death_date "optional"
        varchar country "optional"
        text biography "optional"
        int partner_id FK "optional"
        boolean active "default=True"
    }

    LIBRARY_PUBLISHER {
        int id PK
        varchar name "required, index"
        varchar website "optional"
        int founded_year "optional"
        varchar country "optional"
        text description "optional"
        int contact_id FK "optional"
        boolean active "default=True"
    }

    LIBRARY_GENRE {
        int id PK
        varchar name "required, index"
        varchar code "optional, index"
        text description "optional"
        int color "optional"
        int parent_id FK "optional"
        varchar parent_path "index"
        boolean active "default=True"
    }

    LIBRARY_BRANCH {
        int id PK
        varchar name "required, index"
        varchar code "optional, index, unique"
        text address "required"
        varchar phone "optional"
        varchar email "optional"
        text opening_hours "optional"
        int capacity "default=0"
        boolean is_main_branch "default=False"
        varchar status "default=draft"
        int manager_id FK "optional"
        varchar region "optional"
        varchar timezone "optional"
        int company_id FK "required"
        boolean active "default=True"
    }

    %% Odoo System Models (Referenced)
    RES_PARTNER {
        int id PK
        varchar name
        text address
        varchar email
        varchar phone
    }

    RES_USERS {
        int id PK
        varchar name
        varchar login
        int partner_id FK
    }

    RES_COMPANY {
        int id PK
        varchar name
        int currency_id FK
    }

    RES_CURRENCY {
        int id PK
        varchar name
        varchar symbol
    }

    %% Relationship Tables (M2M)
    LIBRARY_BOOK_AUTHOR_REL {
        int book_id FK
        int author_id FK
    }

    LIBRARY_BOOK_GENRE_REL {
        int book_id FK
        int genre_id FK
    }

    LIBRARY_BRANCH_STAFF_REL {
        int branch_id FK
        int user_id FK
    }

    %% Main Relationships
    LIBRARY_BOOK ||--o{ LIBRARY_EDITION : "has editions"
    LIBRARY_EDITION ||--o{ LIBRARY_BOOK_COPY : "has copies"

    %% Publisher Relationships
    LIBRARY_PUBLISHER ||--o{ LIBRARY_EDITION : "publishes"
    LIBRARY_PUBLISHER }o--|| RES_PARTNER : "contact info"

    %% Branch Relationships
    LIBRARY_BRANCH ||--o{ LIBRARY_BOOK_COPY : "houses"
    LIBRARY_BRANCH }o--|| RES_USERS : "managed by"
    LIBRARY_BRANCH }o--|| RES_COMPANY : "belongs to"

    %% Genre Hierarchy
    LIBRARY_GENRE ||--o{ LIBRARY_GENRE : "parent/child"

    %% Author Relationships
    LIBRARY_AUTHOR }o--|| RES_PARTNER : "contact info"

    %% Many-to-Many Relationships
    LIBRARY_BOOK ||--o{ LIBRARY_BOOK_AUTHOR_REL : ""
    LIBRARY_BOOK_AUTHOR_REL }o--|| LIBRARY_AUTHOR : ""

    LIBRARY_BOOK ||--o{ LIBRARY_BOOK_GENRE_REL : ""
    LIBRARY_BOOK_GENRE_REL }o--|| LIBRARY_GENRE : ""

    LIBRARY_BRANCH ||--o{ LIBRARY_BRANCH_STAFF_REL : ""
    LIBRARY_BRANCH_STAFF_REL }o--|| RES_USERS : ""

    %% Copy Operational References
    LIBRARY_BOOK_COPY }o--|| RES_PARTNER : "reserved by"
    LIBRARY_BOOK_COPY }o--|| RES_CURRENCY : "purchase currency"
```

## Relaciones y Cardinalidades

### Relaciones Principales (1:N)

- **Book → Edition**: 1 libro puede tener múltiples ediciones (0 o más)
- **Edition → Copy**: 1 edición puede tener múltiples copias (0 o más)
- **Publisher → Edition**: 1 editorial puede publicar múltiples ediciones
- **Branch → Copy**: 1 sucursal puede tener múltiples copias
- **Genre → Genre**: autoreferencial para jerarquía (parent_id)

### Relaciones Many-to-Many

- **Book ↔ Author**: libros pueden tener múltiples autores, autores múltiples libros
- **Book ↔ Genre**: libros pueden pertenecer a múltiples géneros
- **Branch ↔ Users**: sucursales pueden tener múltiples staff members

### Relaciones Opcionales (FK nullable)

- **Author → Partner**: para información de contacto extendida
- **Publisher → Partner**: para datos de contacto
- **Branch → User**: manager opcional
- **Copy → Partner**: para reservas actuales

### Constraints Importantes

- **ISBN único**: a nivel de edición
- **Barcode único**: a nivel de copia
- **Una sola sucursal principal**: constraint en Branch
- **Fechas válidas**: birth_date < death_date en Author
