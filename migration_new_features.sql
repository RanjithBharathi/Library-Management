-- Migration script for Library Management System
-- New Features: Analytics, Fine Calculator, Feedback/Rating, Book Suggestions, Chatbot

-- =============================================
-- ADD NEW COLUMNS TO EXISTING TABLES
-- =============================================

-- Add new columns to Reader table (ignore error if already exists)
ALTER TABLE reader ADD COLUMN total_fines_owed DECIMAL(10,2) DEFAULT 0.00;

-- Add new columns to Book table (ignore error if already exists)
ALTER TABLE book ADD COLUMN category VARCHAR(100) NULL;
ALTER TABLE book ADD COLUMN total_borrows INT DEFAULT 0;

-- Add new columns to Borrow table (ignore error if already exists)
ALTER TABLE borrow ADD COLUMN fine_amount DECIMAL(10,2) DEFAULT 0.00;
ALTER TABLE borrow ADD COLUMN fine_paid BOOLEAN DEFAULT FALSE;

-- =============================================
-- CREATE NEW TABLES
-- =============================================

-- Create Rating table for book feedback/reviews
CREATE TABLE IF NOT EXISTS rating (
    id INT PRIMARY KEY AUTO_INCREMENT,
    book_id INT NOT NULL,
    reader_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review TEXT,
    date_posted DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (book_id) REFERENCES book(id) ON DELETE CASCADE,
    FOREIGN KEY (reader_id) REFERENCES reader(id) ON DELETE CASCADE,
    UNIQUE KEY unique_rating (book_id, reader_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Create Suggestion table for book suggestions
CREATE TABLE IF NOT EXISTS suggestion (
    id INT PRIMARY KEY AUTO_INCREMENT,
    reader_id INT NOT NULL,
    suggested_title VARCHAR(255) NOT NULL,
    suggested_author VARCHAR(255) NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    date_suggested DATE DEFAULT (CURRENT_DATE),
    librarian_notes TEXT,
    FOREIGN KEY (reader_id) REFERENCES reader(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- =============================================
-- UPDATE EXISTING DATA
-- =============================================

-- Update total_borrows for existing books
UPDATE book b
SET total_borrows = (
    SELECT COUNT(*) FROM borrow WHERE book_id = b.id
);

-- =============================================
-- SAMPLE DATA FOR TESTING (OPTIONAL)
-- =============================================

-- Sample ratings (uncomment to add test data)
-- INSERT INTO rating (book_id, reader_id, rating, review) VALUES
-- (17, 1, 5, 'Amazing classic! A must-read for everyone.'),
-- (18, 2, 4, 'Great sci-fi, loved the concepts.'),
-- (19, 3, 5, 'Jules Verne at his best!');

-- Sample suggestions (uncomment to add test data)
-- INSERT INTO suggestion (reader_id, suggested_title, suggested_author, reason) VALUES
-- (1, 'The Great Gatsby', 'F. Scott Fitzgerald', 'Classic American literature that should be in every library.'),
-- (2, 'Dune', 'Frank Herbert', 'One of the greatest sci-fi novels of all time.');

-- =============================================
-- INDEXES FOR PERFORMANCE
-- =============================================

CREATE INDEX idx_rating_book ON rating(book_id);
CREATE INDEX idx_rating_reader ON rating(reader_id);
CREATE INDEX idx_suggestion_status ON suggestion(status);
CREATE INDEX idx_suggestion_reader ON suggestion(reader_id);
CREATE INDEX idx_borrow_fine ON borrow(fine_amount);

COMMIT;
