-- Cassandra Exercise: Online Education Platform
-- Use Case 1: List student comments on a course, filtered by rating (e.g., only 5-star comments), ordered by date.

-- 1) Entidades (Table Design)
-- Table to store student comments on courses, optimized for filtering by course and rating, and ordering by date.
-- Partition key: (course_id, rating) to efficiently retrieve comments for a specific course and rating.
-- Clustering keys: comment_date (descending) for ordering by date, and comment_id for uniqueness.
CREATE TABLE course_comments_by_rating (
    course_id UUID,
    rating INT,
    comment_date TIMESTAMP,
    comment_id UUID,
    student_id UUID,
    comment_text TEXT,
    PRIMARY KEY ((course_id, rating), comment_date, comment_id)
) WITH CLUSTERING ORDER BY (comment_date DESC);

-- Explanation for PRIMARY KEY:
-- - The partition key is ((course_id, rating)). This design allows for efficient lookups of comments
--   for a particular course AND a particular rating. Cassandra will store data for this combination
--   of course_id and rating on the same node or set of nodes, minimizing network hops.
-- - The clustering keys are comment_date and comment_id.
--   - comment_date DESC ensures that comments for a given course and rating are retrieved in
--     reverse chronological order (newest first) by default.
--   - comment_id ensures uniqueness in cases where multiple comments might have the exact same timestamp
--     for the same course and rating.

-- 2) Inserts (Sample Data)
-- Sample UUIDs for courses and students
-- course_id_1 = 123e4567-e89b-12d3-a456-426614174000
-- course_id_2 = 123e4567-e89b-12d3-a456-426614174001
-- student_id_1 = 123e4567-e89b-12d3-a456-426614174002
-- student_id_2 = 123e4567-e89b-12d3-a456-426614174003

INSERT INTO course_comments_by_rating (course_id, rating, comment_date, comment_id, student_id, comment_text) VALUES (123e4567-e89b-12d3-a456-426614174000, 5, '2023-10-26 10:00:00+0000', 00000000-0000-0000-0000-000000000001, 123e4567-e89b-12d3-a456-426614174002, 'Excellent course, very informative!');
INSERT INTO course_comments_by_rating (course_id, rating, comment_date, comment_id, student_id, comment_text) VALUES (123e4567-e89b-12d3-a456-426614174000, 5, '2023-10-27 11:30:00+0000', 00000000-0000-0000-0000-000000000002, 123e4567-e89b-12d3-a456-426614174003, 'Loved the content and the teacher!');
INSERT INTO course_comments_by_rating (course_id, rating, comment_date, comment_id, student_id, comment_text) VALUES (123e4567-e89b-12d3-a456-426614174000, 4, '2023-10-25 09:00:00+0000', 00000000-0000-0000-0000-000000000003, 123e4567-e89b-12d3-a456-426614174002, 'Good course, but some parts were a bit slow.');
INSERT INTO course_comments_by_rating (course_id, rating, comment_date, comment_id, student_id, comment_text) VALUES (123e4567-e89b-12d3-a456-426614174001, 5, '2023-11-01 14:00:00+0000', 00000000-0000-0000-0000-000000000004, 123e4567-e89b-12d3-a456-426614174003, 'Fantastic! Highly recommend this course.');
INSERT INTO course_comments_by_rating (course_id, rating, comment_date, comment_id, student_id, comment_text) VALUES (123e4567-e89b-12d3-a456-426614174001, 3, '2023-11-02 08:00:00+0000', 00000000-0000-0000-0000-000000000005, 123e4567-e89b-12d3-a456-426614174002, 'It was okay, but expected more depth.');

-- 3) Respuestas de caso de uso (CQL Query)
-- Use Case: List student comments on a course, filtered by rating (e.g., only 5-star comments), ordered by date.
SELECT comment_date, student_id, comment_text
FROM course_comments_by_rating
WHERE course_id = 123e4567-e89b-12d3-a456-426614174000 AND rating = 5;

-- Explanation:
-- - SELECT comment_date, student_id, comment_text: Retrieves the specific fields required for the comments.
-- - FROM course_comments_by_rating: Specifies the table to query.
-- - WHERE course_id = 123e4567-e89b-12d3-a456-426614174000 AND rating = 5:
--   This clause efficiently filters the data. Since (course_id, rating) is the partition key,
--   Cassandra can directly go to the correct partitions containing the data for the specified course and rating.
--   The CLUSTERING ORDER BY (comment_date DESC) defined in the table schema ensures that the results
--   are automatically ordered by comment_date in descending order without needing an ORDER BY clause in the query,
--   which would be inefficient if not on the clustering key.

-- 4) Valor del Token y su CQL
-- First, get the token value for a specific partition (course_id, rating).
-- The actual token value will vary depending on the cluster and hashing, but this query shows how to obtain it.
SELECT token(course_id, rating) FROM course_comments_by_rating WHERE course_id = 123e4567-e89b-12d3-a456-426614174000 AND rating = 5 LIMIT 1;

-- Assuming the token value returned by the above query is '1234567890123456789' (this is an example value)
-- Query using the TOKEN value:
SELECT comment_date, student_id, comment_text
FROM course_comments_by_rating
WHERE token(course_id, rating) = 1234567890123456789;

-- Explanation:
-- - token(course_id, rating): This function computes the token for the specified partition key.
-- - Querying by token allows directly accessing partitions based on their token range, which can be useful
--   for efficient data distribution or specific pagination strategies, especially in large clusters.
--   It bypasses the need to specify the actual partition key components (course_id, rating) once the token is known.
