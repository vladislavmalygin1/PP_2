-- Single Upsert Procedure
CREATE OR REPLACE PROCEDURE public.upsert_contact(p_name TEXT, p_phone TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO phonebook (username, phone) 
    VALUES (p_name, p_phone)
    ON CONFLICT (username) 
    DO UPDATE SET phone = EXCLUDED.phone;
END;
$$;

-- Bulk Insert Procedure with Validation
CREATE OR REPLACE PROCEDURE public.bulk_insert_contacts(p_names TEXT[], p_phones TEXT[])
LANGUAGE plpgsql AS $$
DECLARE
    i INT;
BEGIN
    FOR i IN 1 .. array_upper(p_names, 1) LOOP
        -- Simple validation: phone must be at least 10 chars
        IF LENGTH(p_phones[i]) >= 10 THEN
            INSERT INTO phonebook (username, phone) 
            VALUES (p_names[i], p_phones[i])
            ON CONFLICT (username) DO UPDATE SET phone = EXCLUDED.phone;
        ELSE
            RAISE NOTICE 'Skipping invalid phone for %: %', p_names[i], p_phones[i];
        END IF;
    END LOOP;
END;
$$;

-- Delete Procedure
CREATE OR REPLACE PROCEDURE public.delete_contact_proc(p_identifier TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM phonebook 
    WHERE username = p_identifier OR phone = p_identifier;
END;
$$;