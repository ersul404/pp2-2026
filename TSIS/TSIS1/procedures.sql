-- ============================================================
-- TSIS 1 — New Stored Procedures & Functions
-- (Practice 8 procedures are NOT duplicated here)
-- ============================================================

-- ----------------------------------------------------------
-- 1. add_phone(contact_name, phone, type)
--    Adds a new phone number to an existing contact.
-- ----------------------------------------------------------
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR  -- 'home' | 'work' | 'mobile'
)
LANGUAGE plpgsql AS $$
DECLARE
    v_id INTEGER;
BEGIN
    SELECT id INTO v_id FROM contacts WHERE first_name = p_contact_name LIMIT 1;

    IF v_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;

    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Phone type must be home, work, or mobile (got "%")', p_type;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_id, p_phone, p_type);
END;
$$;


-- ----------------------------------------------------------
-- 2. move_to_group(contact_name, group_name)
--    Moves a contact to a group; creates the group if needed.
-- ----------------------------------------------------------
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id   INTEGER;
BEGIN
    -- Find or create group
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;
    IF v_group_id IS NULL THEN
        INSERT INTO groups (name) VALUES (p_group_name) RETURNING id INTO v_group_id;
        RAISE NOTICE 'Created new group "%"', p_group_name;
    END IF;

    -- Find contact
    SELECT id INTO v_contact_id FROM contacts WHERE first_name = p_contact_name LIMIT 1;
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;

    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;
END;
$$;


-- ----------------------------------------------------------
-- 3. search_contacts(query)
--    Extended search: matches name, email, AND all phones
--    in the phones table (replaces the Practice 8 pattern fn).
-- ----------------------------------------------------------
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    contact_id  INTEGER,
    first_name  VARCHAR,
    email       VARCHAR,
    birthday    DATE,
    group_name  VARCHAR,
    phone       VARCHAR,
    phone_type  VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT ON (c.id, ph.phone)
           c.id,
           c.first_name,
           c.email,
           c.birthday,
           g.name        AS group_name,
           ph.phone,
           ph.type       AS phone_type
    FROM   contacts c
    LEFT   JOIN groups g  ON g.id  = c.group_id
    LEFT   JOIN phones ph ON ph.contact_id = c.id
    WHERE  c.first_name ILIKE '%' || p_query || '%'
        OR c.email      ILIKE '%' || p_query || '%'
        OR ph.phone     ILIKE '%' || p_query || '%'
    ORDER  BY c.id, ph.phone;
END;
$$;


-- ----------------------------------------------------------
-- Kept from Practice 8 (paginated query — referenced by Python)
-- Safe to re-run; CREATE OR REPLACE is idempotent.
-- ----------------------------------------------------------
CREATE OR REPLACE FUNCTION get_contacts_paginated(limit_val INT, offset_val INT)
RETURNS TABLE (
    id         INTEGER,
    first_name VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_name VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.first_name, c.email, c.birthday, g.name
    FROM   contacts c
    LEFT   JOIN groups g ON g.id = c.group_id
    ORDER  BY c.first_name
    LIMIT  limit_val OFFSET offset_val;
END;
$$ LANGUAGE plpgsql;