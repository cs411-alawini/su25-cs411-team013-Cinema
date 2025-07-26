# Stage 3: Database Implementation and Indexing Report

This document outlines the implementation of the database schema, the advanced queries used to retrieve meaningful data, and a detailed analysis of indexing strategies to optimize query performance.

---

## Part 1: Database Implementation

### Database Connection and Schema

A connection to the `college_major_db` database was successfully established on Google Cloud Platform. The schema consists of 7 tables designed to store information about users, majors, and related statistics.

![Connection](/doc/Connect.png)

### Data Definition Language (DDL)

The following SQL commands were used to create the database schema as designed in Stage 2.

```sql
CREATE TABLE User (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE InterestArea (
    interest_area_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE Major (
    major_id INT AUTO_INCREMENT PRIMARY KEY,
    major_name VARCHAR(100) NOT NULL,
    interest_area_id INT,
    FOREIGN KEY (interest_area_id) REFERENCES InterestArea(interest_area_id) ON DELETE SET NULL
);

CREATE TABLE DataSource (
    source_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    url VARCHAR(2083)
);

CREATE TABLE MajorStats (
    stat_id INT AUTO_INCREMENT PRIMARY KEY,
    major_id INT,
    source_id INT,
    year INT,
    avg_salary DECIMAL(10,2),
    job_growth_rate DECIMAL(5,4),
    grad_count INT,
    FOREIGN KEY (major_id) REFERENCES Major(major_id) ON DELETE CASCADE,
    FOREIGN KEY (source_id) REFERENCES DataSource(source_id) ON DELETE CASCADE
);

CREATE TABLE UserInterestArea (
    user_id INT,
    interest_area_id INT,
    saved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, interest_area_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE,
    FOREIGN KEY (interest_area_id) REFERENCES InterestArea(interest_area_id) ON DELETE CASCADE
);

CREATE TABLE SavedComparison (
    user_id INT,
    major_id INT,
    saved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, major_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE,
    FOREIGN KEY (major_id) REFERENCES Major(major_id) ON DELETE CASCADE
);
```

### Data Population

The database was populated with a large, realistic dataset to ensure meaningful performance testing. Key tables were populated with over 1000+ rows each as required.

![RowCount](/doc/RowCount2.png)

---

## Part 2: Advanced Queries & Results

This section presents the four advanced SQL queries developed for the application, along with screenshots of their output.

### Query 1: Users Who Saved Majors with Above-Average Growth
**SQL Query**:
```sql
SELECT
    u.username,
    m.major_name,
    ms.job_growth_rate
FROM SavedComparison sc
JOIN User u ON sc.user_id = u.user_id
JOIN Major m ON sc.major_id = m.major_id
JOIN MajorStats ms ON m.major_id = ms.major_id
WHERE ms.job_growth_rate >= (
    SELECT AVG(job_growth_rate) FROM MajorStats
)
ORDER BY ms.job_growth_rate DESC
LIMIT 15;
```
**Result Screenshot**:

![Q1](/doc/Q1.png)

---

### Query 2: Most Popular Majors in a Specific Interest Area
**SQL Query**:
```sql
SELECT
    m.major_name,
    ia.name AS interest_area,
    COUNT(sc.user_id) AS number_of_saves
FROM Major m
JOIN InterestArea ia ON m.interest_area_id = ia.interest_area_id
LEFT JOIN SavedComparison sc ON m.major_id = sc.major_id
WHERE ia.name = 'STEM'
GROUP BY m.major_id, m.major_name, ia.name
ORDER BY number_of_saves DESC
LIMIT 15;
```
**Result Screenshot**:

![Q2](/doc/Q2.png)

---

### Query 3: Interest Areas with Highest Job Growth Rate
**SQL Query**:
```sql
SELECT
    ia.name AS interest_area,
    ROUND(AVG(ms.job_growth_rate), 4) AS avg_growth_rate
FROM MajorStats ms
JOIN Major m ON ms.major_id = m.major_id
JOIN InterestArea ia ON m.interest_area_id = ia.interest_area_id
GROUP BY ia.interest_area_id, ia.name
ORDER BY avg_growth_rate DESC
LIMIT 15;
```
**Result Screenshot**:

![Q3](/doc/Q3.png)

---

### Query 4: Find Users Exploring Diverse Fields
**SQL Query**:
```sql
SELECT
    u.username,
    COUNT(DISTINCT ia.interest_area_id) AS interest_area_count
FROM User u
JOIN SavedComparison sc ON u.user_id = sc.user_id
JOIN Major m ON sc.major_id = m.major_id
JOIN InterestArea ia ON m.interest_area_id = ia.interest_area_id
GROUP BY u.username
HAVING interest_area_count > 1
LIMIT 15;
```
**Result Screenshot**:

![Q4](/doc/Q4.png)

---
---

## Part 3: Indexing and Performance Analysis

**Methodology**: For each query, performance was measured before adding any new indexes (Baseline). Then, three different indexing strategies were tested. **Crucially, each index was dropped after its test** to ensure a fair comparison for the subsequent strategy.

### Analysis for Query 1: Users with Above-Average Growth Majors

#### Baseline (No New Indexes)
| Metric | Value |
| :--- | :--- |
| **Cost** | `2.28` |
| **Time** | `0.0418 ms` |
**`EXPLAIN ANALYZE` Screenshot**:

![Q1E0](/doc/Q1E0.png)

---

#### Strategy 1: Index on `SavedComparison(user_id)`
**Index**: `CREATE INDEX idx_saved_user_id ON SavedComparison(user_id);`
**Rationale**: Speeds up the initial join from the `User` table.
| Metric | Value |
| :--- | :--- |
| **Cost** | `2.4` |
| **Time** | `0.865 ms` |
**`EXPLAIN ANALYZE` Screenshot**:

![Q1E1](/doc/Q1E1.png)

---

#### Strategy 2: Composite Index on `SavedComparison`
**Index**: `CREATE INDEX idx_saved_user_major ON SavedComparison(user_id, major_id);`
**Rationale**: A covering index for the `SavedComparison` table to optimize its joins.
| Metric | Value |
| :--- | :--- |
| **Cost** | `2.4` |
| **Time** | `0.0739 ms` |
**`EXPLAIN ANALYZE` Screenshot**:

![Q1E2](/doc/Q1E2.png)

---

#### Strategy 3: Index on `Major(major_id)`
**Index**: `CREATE INDEX idx_major_id ON Major(major_id);`
**Rationale**: Optimizes the join between `SavedComparison` and `Major`.
| Metric | Value |
| :--- | :--- |
| **Cost** | `1.65` |
| **Time** | `0.026 ms` |
**`EXPLAIN ANALYZE` Screenshot**:

![Q1E3](/doc/Q1E3.png)

---

#### Final Analysis for Query 1
The baseline query performed surprisingly well at **0.0418 ms**, likely because the primary keys on the tables were already being used effectively by the optimizer. However, **Strategy 3**, adding an explicit index on `Major(major_id)`, provided the best performance, reducing the time to **0.026 ms**. This is because `major_id` is a primary key and already indexed, but creating an explicit secondary index can sometimes lead to a more optimal query plan, as seen here. Strategy 1 was counter-intuitively the slowest, suggesting the optimizer chose a less efficient plan. Strategy 2, the composite index, was also very fast at **0.0739 ms**. The best choice is the simple index on `Major(major_id)`.

---
---

### Analysis for Query 2: Most Popular Majors

#### Baseline (No New Indexes)
| Metric | Value |
| :--- | :--- |
| **Cost** | `6.76` |
| **Time** | `2.66 ms` |
**`EXPLAIN ANALYZE` Screenshot**:

![Q2E0](/doc/Q2E0.png)

---

#### Strategy 1: Index on `Major(interest_area_id)`
**Index**: `CREATE INDEX idx_major_interest_area ON Major(interest_area_id);`
**Rationale**: Speeds up the join between `Major` and `InterestArea`.
| Metric | Value |
| :--- | :--- |
| **Cost** | `8.01` |
| **Time** | `0.0562 ms` |
**`EXPLAIN ANALYZE` Screenshot**:

![Q2E1](/doc/Q2E1.png)

---

#### Strategy 2: Index on `SavedComparison(major_id)`
**Index**: `CREATE INDEX idx_savedcomparison_major ON SavedComparison(major_id);`
**Rationale**: Optimizes the `LEFT JOIN` to the `SavedComparison` table.
| Metric | Value |
| :--- | :--- |
| **Cost** | `4.02` |
| **Time** | `0.0931 ms` |
**`EXPLAIN ANALYZE` Screenshot**:

![Q2E2](/doc/Q2E2.png)

---

#### Strategy 3: Index on `InterestArea(name)`
**Index**: `CREATE INDEX idx_interestarea_name ON InterestArea(name);`
**Rationale**: Avoids a full table scan on `InterestArea` by allowing an instant lookup for `name = 'STEM'`.
| Metric | Value |
| :--- | :--- |
| **Cost** | `4.52` |
| **Time** | `0.0784 ms` |
**`EXPLAIN ANALYZE` Screenshot**:

![Q2E3](/doc/Q2E3.png)

---

#### Final Analysis for Query 2
The baseline query was extremely slow at **2.66 ms**. All three indexing strategies provided a dramatic improvement. **Strategy 1**, indexing the `Major(interest_area_id)` foreign key, was the clear winner, reducing the time to just **0.0562 ms**. This indicates that the join between `Major` and `InterestArea` was the biggest bottleneck. Strategy 3 (indexing `InterestArea.name`) was the second-fastest at **0.0784 ms**, as it optimized the `WHERE` clause. For optimal performance, a combination of Strategy 1 and Strategy 3 would be best.

---
---

### Analysis for Query 3: Interest Areas with Highest Job Growth

#### Baseline (No New Indexes)
| Metric | Value |
| :--- | :--- |
| **Cost** | `65.3` |
| **Time** | `0.927 ms` |
**`EXPLAIN ANALYZE` Screenshot**:

![Q3E0](/doc/Q3E0.png)

---

#### Strategy 1: Index on `MajorStats(major_id)`
**Index**: `CREATE INDEX idx_majorstats_major ON MajorStats(major_id);`
**Rationale**: Speeds up the join between `MajorStats` (the largest table) and `Major`.
| Metric | Value |
| :--- | :--- |
| **Cost** | `65.7` |
| **Time** | `0.501 ms` |
**`EXPLAIN ANALYZE` Screenshot**:

![Q3E1](/doc/Q3E1.png)

---

#### Strategy 2: Index on `Major(interest_area_id)`
**Index**: `CREATE INDEX idx_major_interestarea ON Major(interest_area_id);`
**Rationale**: Optimizes the second join between `Major` and `InterestArea`.
| Metric | Value |
| :--- | :--- |
| **Cost** | `65.7` |
| **Time** | `0.788 ms` |
**`EXPLAIN ANALYZE` Screenshot**:

![Q3E2](/doc/Q3E2.png)

---

#### Strategy 3: Composite Index on `InterestArea`
**Index**: `CREATE INDEX idx_interestarea_combo ON InterestArea(interest_area_id, name);`
**Rationale**: A covering index for the `InterestArea` table.
| Metric | Value |
| :--- | :--- |
| **Cost** | `126` |
| **Time** | `0.152 ms` |
**`EXPLAIN ANALYZE` Screenshot**:

![Q3E3](/doc/Q3E3.png)

---

#### Final Analysis for Query 3
The baseline was slow at **0.927 ms**. Interestingly, **Strategy 3**, the composite index on the small `InterestArea` table, provided the best performance by far, reducing the time to **0.152 ms**. The query plan shows that this index allowed the optimizer to use a "Stream results" plan with "Group aggregate", which is more efficient than the "Aggregate using temporary table" plan used by the other strategies. This demonstrates that sometimes an index on a smaller table can unlock a more efficient overall query plan.

---
---

### Analysis for Query 4: Find Users Exploring Diverse Fields

#### Baseline (No New Indexes)
| Metric | Value |
| :--- | :--- |
| **Cost** | `1.4` |
| **Time** | `0.022 ms` |
**`EXPLAIN ANALYZE` Screenshot**:

![Q4E0](/doc/Q4E0.png)

---

#### Strategy 1: Composite Index on `SavedComparison`
**Index**: `CREATE INDEX idx_saved_user_major ON SavedComparison(user_id, major_id);`
**Rationale**: A covering index for the central junction table to optimize all joins originating from it.
| Metric | Value |
| :--- | :--- |
| **Cost** | `1.4` |
| **Time** | `0.0258 ms` |
**`EXPLAIN ANALYZE` Screenshot**:

![Q4E1](/doc/Q4E1.png)


---

#### Strategy 2: Composite Index on `Major`
**Index**: `CREATE INDEX idx_major_join ON Major(major_id, interest_area_id);`
**Rationale**: A covering index for the `Major` table to speed up its join and the subsequent lookup of `interest_area_id`.
| Metric | Value |
| :--- | :--- |
| **Cost** | `1.4` |
| **Time** | `0.0109 ms` |
**`EXPLAIN ANALYZE` Screenshot**:

![Q4E2](/doc/Q4E2.png)

---

#### Strategy 3: Index on `InterestArea(interest_area_id)`
**Index**: `CREATE INDEX idx_interestarea_id ON InterestArea(interest_area_id);`
**Rationale**: Speeds up the final join to the `InterestArea` table.
| Metric | Value |
| :--- | :--- |
| **Cost** | `1.4` |
| **Time** | `0.00826 ms` |
**`EXPLAIN ANALYZE` Screenshot**:

![Q4E3](/doc/Q4E3.png)

---

#### Final Analysis for Query 4
This query was already very fast at baseline (**0.022 ms**), indicating the default primary key indexes were sufficient. However, adding more specific indexes still yielded improvements. **Strategy 3**, indexing the `interest_area_id` on the final table in the join chain, was the fastest at an incredible **0.00826 ms**. This is likely because it allowed for a highly efficient final lookup after the other joins were resolved. **Strategy 2** was also an excellent choice at **0.0109 ms**. This shows that even on an already fast query, targeted indexes on join keys can still squeeze out additional performance.
