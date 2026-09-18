# Add support for PostgREST and media_analysis
``` postgresql
CREATE OR REPLACE VIEW media_review AS
SELECT 
    -- Record Identification & Bucketing
    r.id,
    r.file_name,
    r.file_path,
    r.hostname,
    r.disposition,       -- Serves as your review bucket (KEEP, SIMILAR, BINARY_DUP, etc.)
    r.classification,
    
    -- File Properties & Hashes
    r.phash,
    r.sha256,
    r.filetype,
    r.file_size,
    r.resolution,
    r.pixel_count,
    r.duration,
    r.bitrate,
    
    -- EXIF Data
    r.exif_dt,
    r.exif_exposure_time,
    r.exif_exposure_compensation,
    r.exif_iso,
    r.exif_fnumber,
    
    -- Image Data (Encodes BYTEA to Base64 for instant React grid rendering)
    encode(r.image_data, 'base64') AS thumbnail_base64,
    
    -- Embeddings (LEFT JOIN ensures records display even if vector generation is pending)
    e.collection_name,
    e.embedding,
    
    -- Timestamps
    r.created_at,
    r.updated_at
FROM media_reference r
LEFT JOIN media_embeddings e ON e.media_id = r.id;

-- Create helper view to filter by collection_name
CREATE OR REPLACE VIEW media_collections AS
SELECT DISTINCT collection_name 
FROM media_embeddings 
WHERE collection_name IS NOT NULL;

GRANT SELECT ON media_collections TO postgrest_anon;

-- Grant PostgREST read permissions on the new view
GRANT SELECT ON media_review TO postgrest_anon;

GRANT USAGE ON SCHEMA public TO postgrest_anon;
GRANT SELECT, UPDATE ON media_reference TO postgrest_anon;
GRANT SELECT ON media_review TO postgrest_anon;

-- Allow authenticating as postgrest_anon with password
ALTER ROLE postgrest_anon WITH PASSWORD 'AnonPassword123';
```

