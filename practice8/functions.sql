CREATE OR REPLACE FUNCTION get_contacts_by_pattern(p text)
RETURNS TABLE(first_name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT c.first_name, c.phone
    FROM contacts c
    WHERE c.first_name ILIKE '%' || p || '%'
       OR c.phone ILIKE '%' || p || '%';
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION get_contacts_paginated(limit_val INT, offset_val INT)
RETURNS TABLE(first_name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT c.first_name, c.phone
    FROM contacts c
    LIMIT limit_val OFFSET offset_val;
END;
$$ LANGUAGE plpgsql;