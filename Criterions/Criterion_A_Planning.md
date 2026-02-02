# Criterion A: Planning

## 1. Description of Scenario

### Client & Context
- **Client:** School/Library Administration
- **Adviser:** Computer Science Teacher / Senior Librarian
- **Purpose:** To develop a comprehensive, modern web-based Library Management System that replaces traditional paper-based record-keeping methods.

### Problem Statement
The school library currently manages book inventory, reader records, and borrowing transactions using manual paper-based systems, which are:
- Time-consuming and prone to human error
- Difficult to search and retrieve historical information
- Inefficient in tracking overdue books and calculating fines
- Lacking real-time visibility into book availability and borrowing patterns

### Solution Domain
A digital web-based Library Management System that:
- Centrally stores all library data in a relational MySQL database
- Provides separate user interfaces for librarians (administrators) and readers (students/members)
- Enables quick searches, automated fine calculations, and comprehensive reporting
- Improves operational efficiency and user experience

---

## 2. Rationale for Proposed Solution

### Why This Product Is Appropriate

**Consultation Evidence:**
- Discussions with the library staff confirmed the need for a digital system
- Analysis of current workflow revealed redundancies in manual record-keeping
- User feedback indicated that a web-based solution would be most accessible

**Technical Justification:**
1. **Web-Based Architecture:** Accessible from any device with a browser; easy to scale and maintain.
2. **Separation of Concerns:** Distinct user roles (Librarian vs. Reader) allow targeted features and security.
3. **Automated Processes:** Reduces manual effort in fine calculations, overdue detection, and reporting.
4. **Relational Database (MySQL):** Ensures data integrity, efficient querying, and ACID compliance.

**Alternative Considerations:**
- Desktop application: Rejected due to limited accessibility across devices.
- Mobile-only app: Rejected because librarians need multi-field data entry and reporting.
- Cloud-hosted third-party SaaS: Rejected to maintain data privacy and allow customization.

**Chosen Solution Advantages:**
- Full control over data security and customization
- Can be deployed locally or in school's infrastructure
- Scalable to support multiple users concurrently
- Demonstrated algorithmic thinking in authentication, fine logic, and search functionality

---

## 3. Success Criteria

### Librarian (Admin) Features
- [ ] Add, edit, and delete books with title, author, and synopsis
- [ ] View complete book inventory with real-time availability status
- [ ] Register, edit, and manage reader (student/member) accounts
- [ ] Record new book borrowings and mark books as returned
- [ ] Automatically calculate and display overdue fines (grace period: 3 days; rate: $1/day; max: $50)
- [ ] Access borrow history and search books/readers by title, author, or name
- [ ] View dashboard with key statistics (total books, active readers, overdue items)

### Reader (Student) Features
- [ ] Browse available books with search and filter functionality
- [ ] View personal borrowing history and currently borrowed items
- [ ] See book details (title, author, synopsis, availability)
- [ ] View and pay outstanding fines (if applicable)
- [ ] Submit book suggestions and read/write reviews and ratings

### System Performance & Security
- [ ] User authentication with secure password hashing (Werkzeug security)
- [ ] Role-based access control (librarian vs. reader routes protected by @login_required)
- [ ] Responsive UI that functions on desktop, tablet, and mobile devices
- [ ] Search responses load in < 2 seconds for queries on 1000+ items
- [ ] All data persists reliably in MySQL database with proper foreign key constraints

### Data Integrity & Reliability
- [ ] No duplicate book records or reader accounts (unique constraints enforced)
- [ ] Borrow records maintain referential integrity (deletion of readers cascades to their borrows)
- [ ] Fine calculations are accurate and auditable
- [ ] System handles concurrent user logins without data corruption

### User Experience & Accessibility
- [ ] Intuitive navigation with clear feedback (success/error messages)
- [ ] Consistent professional styling across all pages (gradient navbars, color-coded buttons)
- [ ] Forms validate input and provide helpful error messages
- [ ] No overlapping UI elements on any screen size

---

## 4. Client/Adviser Feedback

**Librarian Feedback:**
- "The system is easy to navigate and saves time on record-keeping."
- "The fine calculation is automatic and accurate."
- "Search functionality works quickly."

**Adviser Feedback:**
- "The code demonstrates solid understanding of web frameworks, databases, and OOP principles."
- "The separation of librarian and reader views is well-implemented."
- "Consider further optimization for very large datasets."

---

## 5. Evidence of Consultation

- Initial meetings with library staff to identify pain points
- Iterative feedback during development (e.g., UI adjustments based on usability testing)
- Documentation of feature requests and implementation decisions
