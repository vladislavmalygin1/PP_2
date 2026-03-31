-- Pattern matching function
CREATE OR REPLACE FUNCTION public.search_contacts(pattern TEXT)
RETURNS TABLE(id INT, username VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY 
    SELECT p.id, p.username, p.phone 
    FROM phonebook p
    WHERE p.username ILIKE '%' || pattern || '%' 
       OR p.phone LIKE '%' || pattern || '%';
END;
$$ LANGUAGE plpgsql;

-- Pagination function
CREATE OR REPLACE FUNCTION public.get_contacts_paged(p_limit INT, p_offset INT)
RETURNS TABLE(id INT, username VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY 
    SELECT p.id, p.username, p.phone 
    FROM phonebook p
    ORDER BY p.id
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;