-- Placeholder schema (will be wired when connecting to Neon)

-- Raw sections queue table (future)
-- CREATE TABLE raw_sections (
--   section_id BIGINT PRIMARY KEY,
--   page_id BIGINT,
--   page_title TEXT,
--   title TEXT,
--   text TEXT NOT NULL,
--   topic TEXT,
--   keywords TEXT[],
--   status TEXT NOT NULL DEFAULT 'pending',
--   idempotency_key TEXT,
--   created_at TIMESTAMP DEFAULT now()
-- );

-- Output lesson steps (simplified per spec)
-- CREATE TABLE lesson_steps (
--   lesson_id BIGSERIAL,
--   lesson_title TEXT NOT NULL,
--   section_id INT NOT NULL,
--   section_style TEXT NOT NULL,
--   content TEXT NOT NULL,
--   created_at TIMESTAMP DEFAULT now(),
--   PRIMARY KEY (lesson_id, section_id)
-- );


