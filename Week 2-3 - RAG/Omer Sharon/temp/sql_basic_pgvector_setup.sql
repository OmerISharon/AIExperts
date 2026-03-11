-- CREATE DATABASE ezpresence_rag;
-- CREATE EXTENSION VECTOR;
-- SELECT * FROM pg_extension WHERE extname = 'vector';

-- CREATE TABLE test_vectors (
--     id SERIAL PRIMARY KEY,
--     label TEXT NOT NULL,
--     embedding VECTOR(3) NOT NULL
-- );

-- INSERT INTO test_vectors (label, embedding)
-- VALUES
-- ('dog chase', '[1,2,3]'),
-- ('phone footage', '[2,3,4]'),
-- ('sunset beach', '[9,9,9]');

-- SELECT id, label, embedding
-- FROM test_vectors
-- ORDER BY embedding <-> '[1,2,2]'
-- LIMIT 3;