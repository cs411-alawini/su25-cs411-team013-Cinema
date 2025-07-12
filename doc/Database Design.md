# Database Design Document

## 1\. ER Diagram

![ER Diagram](ERD.png)

-----

## 2\. Design Rationale and Assumptions

*In designing this database, our guiding principle was that any concept with its own distinct attributes that is referenced multiple times should be its own table. This approach ensures data integrity and reduces redundancy, aligning with the principles of database normalization.*

### Entity Descriptions

  * **User**: Stores credentials and account information. It's the core entity for tracking user activity, such as which majors they choose to save for comparison.
  * **InterestArea**: Acts as a lookup table for categories, preventing the need to repeat text values within the `Major` table. This is used to filter majors by subject area.
  * **UserInterestArea**: A **junction table** that resolves the many-to-many relationship between `User` and `InterestArea`, allowing a user to follow or select multiple areas of interest.
  * **Major**: Stores the details for each academic major, such as its name and description.
  * **DataSource**: Stores information about the external sources from which we get our data (e.g., Bureau of Labor Statistics).
  * **MajorStatistic**: Stores the yearly figures for each major (e.g., average salary, graduation count). Making this its own table avoids having repeating columns in the `Major` table.
  * **SavedComparison**: A **junction table** that resolves the many-to-many relationship between `User` and `Major`. It also stores a timestamp to track when the comparison was saved.

### **Relationship Descriptions**

*This section explicitly details each relationship and its cardinality as shown in the ER Diagram*

  * **selects / is selected by**: A one-to-many relationship between `User` and the `UserInterestArea` table. One user can select many interest areas.
  * **saves / is saved in**: A one-to-many relationship between `User` and the `SavedComparison` table. One user can save many major comparisons.
  * **categorizes**: A one-to-many relationship from `InterestArea` to `Major`. One interest area can categorize multiple majors, but each major belongs to only one interest area.
  * **has stats**: A one-to-many relationship from `Major` to `MajorStats`. One major can have many different statistical records (e.g., for different years or from different sources).
  * **provides**: A one-to-many relationship from `DataSource` to `MajorStats`. One data source can provide the statistics for many records.

-----

## 3\. Relational Schema

*The following schema is the logical blueprint for the database, defining all tables, columns, data types, and key constraints.*

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
  url:VARCHAR(2083)
)

MajorStats(
  stat_id:INT [PK],
  major_id:INT [FK to Major.major_id],
  source_id:INT [FK to DataSource.source_id],
  year:INT,
  avg_salary:DECIMAL(10, 2),
  job_growth_rate:DECIMAL(5, 4),
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

## 4\. Normalization Analysis

*Our database schema is in **Boyce-Codd Normal Form (BCNF)**. Each table's non-key attributes are fully functionally dependent on the primary key, and there are no transitive or partial dependencies.*

### **User**

  * **Primary Key**: `user_id`
  * **Analysis**: This table is in BCNF. All attributes (`username`, `email`, `password_hash`) depend solely on the primary key `user_id`.

### **InterestArea**

  * **Primary Key**: `interest_area_id`
  * **Analysis**: This table is in BCNF. The `name` attribute depends only on the primary key `interest_area_id`.

### **DataSource**

  * **Primary Key**: `source_id`
  * **Analysis**: This table is in BCNF. The `name` and `url` attributes depend only on the primary key `source_id`.

### **Major**

  * **Primary Key**: `major_id`
  * **Analysis**: This table is in BCNF. The attributes `major_name` and `interest_area_id` depend only on the primary key `major_id`.

### **MajorStats**

  * **Primary Key**: `stat_id`
  * **Analysis**: This table is in BCNF. All other attributes depend on the surrogate primary key `stat_id`.

### **UserInterestArea**

  * **Primary Key**: (`user_id`, `interest_area_id`)
  * **Analysis**: This junction table is in BCNF. Its only non-key attribute, `saved_at`, is fully dependent on the entire composite primary key.

### **SavedComparison**

  * **Primary Key**: (`user_id`, `major_id`)
  * **Analysis**: This junction table is in BCNF. Its only non-key attribute, `saved_at`, is fully dependent on the entire composite primary key.
  * **Analysis**: This junction table is in BCNF. Its only non-key attribute, `saved_at`, is fully dependent on the entire composite primary key.
