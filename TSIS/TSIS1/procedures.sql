DROP FUNCTION IF EXISTS search_contacts(TEXT);
DROP FUNCTION IF EXISTS search_phonebook(TEXT);
DROP FUNCTION IF EXISTS get_phonebook_paginated(INT, INT);
DROP PROCEDURE IF EXISTS insert_or_update_user(TEXT, TEXT);
DROP PROCEDURE IF EXISTS insert_many_users(TEXT[], TEXT[]);
DROP PROCEDURE IF EXISTS delete_from_phonebook(TEXT);
DROP PROCEDURE IF EXISTS add_phone(VARCHAR, VARCHAR, VARCHAR);
DROP PROCEDURE IF EXISTS move_to_group(VARCHAR, VARCHAR);

CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    id INT,
    name VARCHAR(100),
    email VARCHAR(100),
    birthday DATE,
    group_name VARCHAR(50),
    phones TEXT,
    created_at TIMESTAMP
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.name,
        c.email,
        c.birthday,
        g.name AS group_name,
        COALESCE(
            STRING_AGG(ph.type || ': ' || ph.phone, ', ' ORDER BY ph.type, ph.phone),
            ''
        ) AS phones,
        c.created_at
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones ph ON ph.contact_id = c.id
    WHERE c.name ILIKE '%' || p_query || '%'
       OR COALESCE(c.email, '') ILIKE '%' || p_query || '%'
       OR COALESCE(g.name, '') ILIKE '%' || p_query || '%'
       OR EXISTS (
            SELECT 1
            FROM phones p2
            WHERE p2.contact_id = c.id
              AND p2.phone ILIKE '%' || p_query || '%'
       )
    GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
    ORDER BY c.name;
END;
$$;

CREATE OR REPLACE FUNCTION search_phonebook(pattern TEXT)
RETURNS TABLE (
    id INT,
    name VARCHAR(100),
    phone VARCHAR(20)
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.name,
        COALESCE(MIN(ph.phone), '')
    FROM contacts c
    LEFT JOIN phones ph ON ph.contact_id = c.id
    WHERE c.name ILIKE '%' || pattern || '%'
       OR EXISTS (
            SELECT 1
            FROM phones p2
            WHERE p2.contact_id = c.id
              AND p2.phone ILIKE '%' || pattern || '%'
       )
    GROUP BY c.id, c.name
    ORDER BY c.name;
END;
$$;

CREATE OR REPLACE PROCEDURE insert_or_update_user(p_name TEXT, p_phone TEXT)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    INSERT INTO contacts(name, group_id)
    VALUES (
        p_name,
        (SELECT id FROM groups WHERE name = 'Other')
    )
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO v_contact_id
    FROM contacts
    WHERE name = p_name;

    IF EXISTS (
        SELECT 1
        FROM phones
        WHERE contact_id = v_contact_id
          AND type = 'mobile'
    ) THEN
        UPDATE phones
        SET phone = p_phone
        WHERE contact_id = v_contact_id
          AND type = 'mobile';
    ELSE
        INSERT INTO phones(contact_id, phone, type)
        VALUES (v_contact_id, p_phone, 'mobile')
        ON CONFLICT (contact_id, phone) DO NOTHING;
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE insert_many_users(
    p_names TEXT[],
    p_phones TEXT[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INTEGER;
BEGIN
    CREATE TEMP TABLE IF NOT EXISTS incorrect_data (
        name TEXT,
        phone TEXT,
        reason TEXT
    ) ON COMMIT DROP;

    DELETE FROM incorrect_data;

    IF array_length(p_names, 1) IS DISTINCT FROM array_length(p_phones, 1) THEN
        RAISE EXCEPTION 'Names and phones arrays must have the same length';
    END IF;

    FOR i IN 1..array_length(p_names, 1) LOOP
        IF p_phones[i] ~ '^\+?\d{5,15}$' THEN
            CALL insert_or_update_user(p_names[i], p_phones[i]);
        ELSE
            INSERT INTO incorrect_data(name, phone, reason)
            VALUES (p_names[i], p_phones[i], 'Invalid phone format');
        END IF;
    END LOOP;
END;
$$;

CREATE OR REPLACE FUNCTION get_phonebook_paginated(p_limit INT, p_offset INT)
RETURNS TABLE (
    id INT,
    name VARCHAR(100),
    email VARCHAR(100),
    birthday DATE,
    group_name VARCHAR(50),
    phones TEXT,
    created_at TIMESTAMP
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.name,
        c.email,
        c.birthday,
        g.name AS group_name,
        COALESCE(
            STRING_AGG(ph.type || ': ' || ph.phone, ', ' ORDER BY ph.type, ph.phone),
            ''
        ) AS phones,
        c.created_at
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones ph ON ph.contact_id = c.id
    GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
    ORDER BY c.created_at, c.id
    LIMIT p_limit OFFSET p_offset;
END;
$$;

CREATE OR REPLACE PROCEDURE delete_from_phonebook(p_value TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM contacts
    WHERE name = p_value
       OR id IN (
            SELECT contact_id
            FROM phones
            WHERE phone = p_value
       );
END;
$$;

CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Phone type must be home, work, or mobile';
    END IF;

    SELECT id INTO v_contact_id
    FROM contacts
    WHERE name = p_contact_name;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact % does not exist', p_contact_name;
    END IF;

    INSERT INTO phones(contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type)
    ON CONFLICT (contact_id, phone) DO UPDATE
    SET type = EXCLUDED.type;
END;
$$;

CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_group_id INTEGER;
BEGIN
    INSERT INTO groups(name)
    VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO v_group_id
    FROM groups
    WHERE name = p_group_name;

    UPDATE contacts
    SET group_id = v_group_id
    WHERE name = p_contact_name;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Contact % does not exist', p_contact_name;
    END IF;
END;
$$;