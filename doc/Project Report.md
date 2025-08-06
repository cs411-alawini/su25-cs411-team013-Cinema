## College Major Explorer: Final Project Report

This report provides a comprehensive overview of the College Major Explorer project, detailing its final implementation, design evolution, and fulfillment of all technical requirements.

### 1. Project Direction and Proposal Alignment

The final project is a direct and successful realization of the vision outlined in the original proposal. Unlike many projects that pivot during development, the College Major Explorer maintained its core direction from inception to completion.

In summary, there were no significant deviations from the original plan. The final product is a testament to a clear initial vision and a well-executed development process.

---

### 2. Application Usefulness: Achievements and Failures

* **Achievements:** The application successfully provides a centralized, easy-to-use platform for exploring college majors based on real-world outcomes. Its primary achievement is the robust filtering capability, allowing users to ask complex questions like, "Show me all Engineering majors with an average salary of at least $70,000 and a job growth rate of 5% or more." The ability for users to create accounts and save personalized comparisons adds significant utility.

* **Failures:** The application's main shortcoming is its dependence on a **static, pre-loaded database**. The data on salaries and job growth is not sourced from a live API, meaning it will become outdated over time. While the backend is robust, its full usefulness is contingent on a polished user interface.

---

### 3. Changes to Data Schema and Source

* **Data Source:** The source of the data (pre-loaded MySQL tables) remained consistent throughout the project.

* **Schema Implementation:** While the table structures themselves did not change, our **interpretation and use of the schema evolved significantly**. We transitioned from treating the `MajorStats` table as having a one-to-one relationship with the `Major` table to a more flexible **one-to-many relationship**. This allows one major to have multiple statistical entries, enabling the storage of data from different years and sources. The final application performs aggregations on the fly to provide more balanced and accurate insights.

---

### 4. Changes to E-R Diagram and Table Implementations

The most critical change was to the relationship between the **`Major`** and **`MajorStats`** entities.

* **Original Design vs. Final Design:** The design shifted from a rigid **one-to-one** relationship to a more robust **one-to-many** relationship.
    * **Original E-R Diagram:** Implied a simple link where each `Major` had exactly one `MajorStats` entry. 
    * **Final E-R Diagram:** Shows that one `Major` can have many `MajorStats` entries. 

* **Table Implementation Differences:** This E-R change directly impacted the SQL queries. The initial implementation used a simple `JOIN`. The final implementation uses **`GROUP BY` and aggregate functions (`AVG()`, `COUNT()`)** to consolidate multiple data points into a single, averaged summary for each major.

* **Why the Change?** The initial design was too simplistic. Real-world data varies by year and source. The final one-to-many design is **more suitable** because it embraces this variability, allowing the database to store historical and multi-source data, making the application's output more scalable and statistically sound.

---

### 5. Functionalities Added or Removed

* **Functionalities Added:**
    1.  **Advanced Major Filtering:** We added query parameters (`area_id`, `min_salary`, `min_growth`) to the `/majors` endpoint, transforming it from a static list into an interactive discovery tool.
    2.  **User Profile Updates:** We implemented a `PUT` method for the `/user/<int:user_id>` endpoint, allowing users to update their account information.
    3.  **Remove Saved Comparison:** We added a `DELETE` endpoint (`/saved-comparisons/<user_id>/<major_id>`) to allow users to remove majors from their personalized list, completing the CRUD cycle for this feature.

* **Functionalities Removed:**
    1.  **Application-Layer Validation:** We removed Python helper functions for validating email and password formats.
    2.  **Why?** This decision was made to centralize business logic. Frontend validation provides instant user feedback, while database constraints (`UNIQUE`) and stored procedures provide the ultimate guarantee of data integrity, simplifying the application layer.

---

### 6. Role of Advanced Database Programs

Our application leverages advanced database features to ensure data integrity, performance, and security.

* **Transactions:** All write operations (`INSERT`, `UPDATE`, `DELETE`) are wrapped in transactions. This ensures that multi-step operations (like checking for a unique username before updating) are **atomic**—they either complete fully or not at all, preventing inconsistent data.

* **Stored Procedures:** The user signup logic is handled by the `sp_basic_signup` stored procedure. This reduces network latency by bundling multiple commands into a single database call and abstracts the database logic from the application code for easier maintenance.

* **Triggers:** The application is designed to work with a `BEFORE INSERT` trigger on the `SavedComparison` table. By catching a specific custom error from the database, the application gracefully handles attempts to save a duplicate major. This is superior to an application-level check as it prevents race conditions and enforces the business rule at the data layer.

---

### 7. Technical Challenge Encountered

* **Challenge:** The most significant technical challenge was preventing **race conditions** during user profile updates. A naive implementation might first check if a new username is available and then perform the update. However, two users could attempt to claim the same username simultaneously, with both checks passing before either update is committed, leading to a data integrity violation.
* **Solution:** We solved this by wrapping the entire check-and-update logic within a **database transaction**. By executing the `SELECT` (to check for duplicates) and the `UPDATE` within a single, atomic transaction block, we leverage the database's locking mechanism. This ensures that only one session can complete the operation for a specific username at a time, completely mitigating the race condition. This approach is robust and centralizes the integrity logic within the database.

---

### 8. Other Changes from Original Proposal

The most notable other change was the rigorous implementation of **explicit transaction control** for all write operations in the final application. The previous version did not consistently use transactions, making the final version much safer and more reliable against data inconsistencies.

---

### 9. Future Work

Beyond improving the interface, the application could be enhanced in several key areas:

1.  **Personalized Recommendations:** Implement a recommendation engine to suggest other majors based on a user's saved items and browsing history.
2.  **Live Data Integration:** Develop a data pipeline to automatically fetch and integrate the latest statistics from official sources like the Bureau of Labor Statistics API.
3.  **Career Path Visualization:** Integrate with job APIs to show potential career paths and progression for a given major.
4.  **University Data:** Expand the database to include which universities offer specific majors and link to their course catalogs.

---

### 10. Final Division of Labor and Teamwork

The project was managed with a clear separation of duties, which proved highly effective.

* **Database Architect:** Designed the E-R diagram, wrote all DDL, and implemented the stored procedures and triggers. All team members participated in this part.
* **Backend API Developer:** Wrote the entire Flask application, implemented all API endpoints, and handled business logic and transaction management. This was mostly done by Shengwen and Artha.
* **Frontend Developer:** Designed the user interface and integrated it with the API. This was mostly done by Antoni and Shrikar.

Teamwork was managed through daily syncs on Discord. The communication was smooth, and every member made significant contributions to the project, leading to a successful and well-integrated final product.
