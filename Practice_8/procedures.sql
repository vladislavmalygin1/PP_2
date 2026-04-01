-- 1. Drop existing procedures
DROP PROCEDURE IF EXISTS public.upsert_contact(text, text);
DROP PROCEDURE IF EXISTS public.bulk_insert_with_errors(text[], text[]);
DROP PROCEDURE IF EXISTS public.delete_by_id(text);

-- 2. Bulk Insert with Loop, IF Validation, and Error Tracking
CREATE OR REPLACE PROCEDURE public.bulk_insert_with_errors(p_names TEXT[], p_phones TEXT[])
LANGUAGE plpgsql AS $$
DECLARE
    i INT;
BEGIN
    CREATE TEMP TABLE IF NOT EXISTS bulk_errors (name TEXT, phone TEXT) ON COMMIT DROP;
    DELETE FROM bulk_errors; 
    FOR i IN 1 .. array_upper(p_names, 1) LOOP
        
        IF p_phones[i] ~ '^[0-9]+$' AND LENGTH(p_phones[i]) >= 10 THEN
            INSERT INTO phonebook (username, phone) 
            VALUES (p_names[i], p_phones[i])
            ON CONFLICT (username) DO UPDATE SET phone = EXCLUDED.phone;
        ELSE
            INSERT INTO bulk_errors VALUES (p_names[i], p_phones[i]);
        END IF;
    END LOOP;
END;
$$;

CREATE OR REPLACE PROCEDURE public.upsert_contact(p_name TEXT, p_phone TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO phonebook (username, phone) 
    VALUES (p_name, p_phone)
    ON CONFLICT (username) DO UPDATE SET phone = EXCLUDED.phone;
END;
$$;

CREATE OR REPLACE PROCEDURE public.delete_by_id(p_val TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM phonebook WHERE username = p_val OR phone = p_val;
END;
$$;