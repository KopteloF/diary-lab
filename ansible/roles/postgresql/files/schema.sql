CREATE TABLE IF NOT EXISTS entries (
  id BIGSERIAL PRIMARY KEY, 
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(), 
  title TEXT NOT NULL, 
  details TEXT, 
  minutes INTEGER, 
  commands TEXT, 
  stack TEXT
);
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE entries TO roman;
GRANT USAGE, SELECT ON SEQUENCE entries_id_seq TO roman;
