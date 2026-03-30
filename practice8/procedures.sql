-- Процедура для вставки или обновления одного контакта
CREATE OR REPLACE PROCEDURE upsert_contact(p_first_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM contacts WHERE first_name = p_first_name) THEN
        UPDATE contacts SET phone = p_phone WHERE first_name = p_first_name;
    ELSE
        INSERT INTO contacts(first_name, phone) VALUES(p_first_name, p_phone);
    END IF;
END;
$$;

-- Процедура для удаления контакта по имени или телефону
CREATE OR REPLACE PROCEDURE delete_contact(p_first_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM contacts
    WHERE (p_first_name IS NOT NULL AND first_name = p_first_name)
       OR (p_phone IS NOT NULL AND phone = p_phone);
END;
$$;

-- Процедура для массовой вставки/обновления контактов из массивов
CREATE OR REPLACE PROCEDURE insert_many_contacts(
    first_names TEXT[],
    phones TEXT[]
)
LANGUAGE plpgsql AS $$
DECLARE
    i INT;
BEGIN
    -- Проверка массивов
    IF array_length(first_names, 1) IS NULL OR array_length(phones, 1) IS NULL THEN
        RAISE NOTICE 'Empty array provided';
        RETURN;
    END IF;

    IF array_length(first_names, 1) <> array_length(phones, 1) THEN
        RAISE EXCEPTION 'Arrays must have the same length';
    END IF;

    FOR i IN 1..array_length(first_names, 1) LOOP
        -- проверка телефона (только цифры и длина 11)
        IF phones[i] ~ '^[0-9]{11}$' THEN
            -- если существует → обновить
            IF EXISTS (SELECT 1 FROM contacts WHERE first_name = first_names[i]) THEN
                UPDATE contacts 
                SET phone = phones[i] 
                WHERE first_name = first_names[i];
            ELSE
                INSERT INTO contacts(first_name, phone)
                VALUES (first_names[i], phones[i]);
            END IF;
        ELSE
            RAISE NOTICE 'Invalid phone: %', phones[i];
        END IF;
    END LOOP;
END;
$$;