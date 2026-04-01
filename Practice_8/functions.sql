-- 1. Drop existing functions first
DROP FUNCTION IF EXISTS public.search_contacts(text);
DROP FUNCTION IF EXISTS public.get_contacts_paged(int, int);

-- 2. Create Pattern Search Function
CREATE OR REPLACE FUNCTION public.search_contacts(p_pattern TEXT)
RETURNS TABLE(id INT, username VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY 
    SELECT p.id, p.username, p.phone 
    FROM phonebook p
    WHERE p.username ILIKE '%' || p_pattern || '%' 
       OR p.phone LIKE '%' || p_pattern || '%';
END;
$$ LANGUAGE plpgsql;

-- 3. Create Pagination Function
CREATE OR REPLACE FUNCTION public.get_paged(p_limit INT, p_offset INT)
RETURNS TABLE(id INT, username VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY 
    SELECT p.id, p.username, p.phone 
    FROM phonebook p
    ORDER BY p.id
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;