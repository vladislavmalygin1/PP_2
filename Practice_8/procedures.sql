-- Procedure to insert or update (Upsert)
CREATE OR REPLACE PROCEDURE upsert_contact(p_name VARCHAR, p_phone VARCHAR)
AS $$
BEGIN
    INSERT INTO phonebook (username, phone) 
    VALUES (p_name, p_phone)
    ON CONFLICT (username) 
    DO UPDATE SET phone = EXCLUDED.phone;
END;
$$ LANGUAGE plpgsql;

-- Procedure to delete
CREATE OR REPLACE PROCEDURE delete_contact_proc(p_identifier VARCHAR)
AS $$
BEGIN
    DELETE FROM phonebook 
    WHERE username = p_identifier OR phone = p_identifier;
END;
$$ LANGUAGE plpgsql;

-- Procedure for bulk insert with validation
CREATE OR REPLACE PROCEDURE bulk_insert_contacts(names TEXT[], phones TEXT[])
AS $$
DECLARE
    i INT;
BEGIN
    FOR i IN 1 .. array_upper(names, 1) LOOP
        -- Simple validation: phone must be at least 10 digits
        IF LENGTH(phones[i]) >= 10 THEN
            INSERT INTO phonebook (username, phone) 
            VALUES (names[i], phones[i])
            ON CONFLICT (phone) DO NOTHING;
        ELSE
            RAISE NOTICE 'Invalid phone for user %: %', names[i], phones[i];
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;