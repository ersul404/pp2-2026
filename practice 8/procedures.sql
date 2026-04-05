CREATE OR REPLACE PROCEDURE upsert_contact(p_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM contacts WHERE name = p_name) THEN
        UPDATE contacts SET phone = p_phone WHERE name = p_name;
    ELSE
        INSERT INTO contacts(name, phone) VALUES(p_name, p_phone);
    END IF;
END;
$$;



CREATE OR REPLACE PROCEDURE delete_contact(p_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM contacts
    WHERE (p_name IS NOT NULL AND name = p_name)
       OR (p_phone IS NOT NULL AND phone = p_phone);
END;
$$;



CREATE OR REPLACE PROCEDURE insert_many_contacts(
    names TEXT[],
    phones TEXT[]
)
LANGUAGE plpgsql AS $$
DECLARE
    i INT;
BEGIN
    FOR i IN 1..array_length(names, 1) LOOP

        -- проверка телефона (только цифры и длина 11)
        IF phones[i] ~ '^[0-9]{11}$' THEN

            -- если существует → обновить
            IF EXISTS (SELECT 1 FROM contacts WHERE name = names[i]) THEN
                UPDATE contacts SET phone = phones[i] WHERE name = names[i];
            ELSE
                INSERT INTO contacts(name, phone)
                VALUES (names[i], phones[i]);
            END IF;

        ELSE
            RAISE NOTICE 'Invalid phone: %', phones[i];
        END IF;

    END LOOP;
END;
$$;