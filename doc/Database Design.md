# Database Design Document

This document outlines the relational schema and normalization analysis for the project database.

-----

## Relational Schema

The following schema defines the tables, columns, and key relationships for the database.

```sql
User(
  user_id:INT [PK],
  username:VARCHAR(50),
  email:VARCHAR(255),
  password_hash:VARCHAR(255)
)

InterestArea(
  interest_area_id:INT [PK],
  name:VARCHAR(100)
)

Major(
  major_id:INT [PK],
  major_name:VARCHAR(100),
  interest_area_id:INT [FK to InterestArea.interest_area_id]
)

DataSource(
  source_id:INT [PK],
  name:VARCHAR(100),
  url:VARCHAR(255)
)

MajorStats(
  stat_id:INT [PK],
  major_id:INT [FK to Major.major_id],
  source_id:INT [FK to DataSource.source_id],
  year:INT,
  avg_salary:DECIMAL,
  job_growth_rate:DECIMAL,
  grad_count:INT
)

UserInterestArea(
  user_id:INT [FK to User.user_id],
  interest_area_id:INT [FK to InterestArea.interest_area_id],
  saved_at:DATETIME,
  [PK: (user_id, interest_area_id)]
)

SavedComparison(
  user_id:INT [FK to User.user_id],
  major_id:INT [FK to Major.major_id],
  saved_at:DATETIME,
  [PK: (user_id, major_id)]
)
```

-----

## Database Normalization Analysis

Our database schema is in **Boyce-Codd Normal Form (BCNF)**. Each table's non-key attributes are fully functionally dependent on the primary key, and there are no transitive or partial dependencies.

### User

**Primary Key**: `user_id`

**Analysis**: This table is in BCNF. All attributes (`username`, `email`, `password_hash`) depend solely on the primary key `user_id`. There are no other dependencies.

-----

### InterestArea

**Primary Key**: `interest_area_id`

**Analysis**: This table is in BCNF. The `name` attribute depends only on the primary key `interest_area_id`.

-----

### DataSource

**Primary Key**: `source_id`

**Analysis**: This table is in BCNF. The `name` and `url` attributes depend only on the primary key `source_id`.

-----

### Major

**Primary Key**: `major_id`

**Analysis**: This table is in BCNF. The attributes `major_name` and the foreign key `interest_area_id` depend only on the primary key `major_id`.

-----

### MajorStats

**Primary Key**: `stat_id`

**Analysis**: This table is in BCNF. All other attributes (`major_id`, `source_id`, `year`, `avg_salary`, `job_growth_rate`, `grad_count`) depend on the surrogate primary key `stat_id`. There are no partial or transitive dependencies.

-----

### UserInterestArea

**Primary Key**: (`user_id`, `interest_area_id`)

**Analysis**: This junction table is in BCNF. Its only non-key attribute, `saved_at`, is fully dependent on the entire composite primary key. This correctly models the many-to-many relationship between users and interest areas.

-----

### SavedComparison

**Primary Key**: (`user_id`, `major_id`)

**Analysis**: This junction table is in BCNF. Its only non-key attribute, `saved_at`, is fully dependent on the entire composite primary key. This correctly models the many-to-many relationship of users saving major comparisons.
