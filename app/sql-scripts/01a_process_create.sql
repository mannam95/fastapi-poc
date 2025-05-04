-- A function to create a process with m2m tables
-- Example usage:
-- SELECT * FROM create_process_with_m2m(
--     'Process 1',
--     'Description 1',
--     1, ARRAY[1, 2], ARRAY[1, 2], ARRAY[1, 2], ARRAY[1, 2]);
CREATE OR REPLACE FUNCTION create_process_with_m2m(
    p_title TEXT,
    p_description TEXT,
    p_created_by_id INTEGER,
    m2m_roles INTEGER[],
    m2m_departments INTEGER[],
    m2m_locations INTEGER[],
    m2m_resources INTEGER[]
) RETURNS TABLE (
    id INTEGER,
    title VARCHAR,
    description VARCHAR,
    created_by_id INTEGER,
    created_at TIMESTAMP
) AS $$
DECLARE
    p_process_id INTEGER;
BEGIN
    -- Insert the process
    INSERT INTO process (title, description, created_by_id)
    VALUES (p_title, p_description, p_created_by_id)
    RETURNING process.id INTO p_process_id;

    -- Insert the m2m items between the process and roles
    IF array_length(m2m_roles, 1) > 0 THEN
        INSERT INTO role_process (process_id, role_id)
        SELECT p_process_id, unnest(m2m_roles)
        ON CONFLICT DO NOTHING;
    END IF;

    -- Insert the m2m items between the process and departments
    IF array_length(m2m_departments, 1) > 0 THEN
        INSERT INTO department_process (process_id, department_id)
        SELECT p_process_id, unnest(m2m_departments)
        ON CONFLICT DO NOTHING;
    END IF;

    -- Insert the m2m items between the process and locations
    IF array_length(m2m_locations, 1) > 0 THEN
        INSERT INTO location_process (process_id, location_id)
        SELECT p_process_id, unnest(m2m_locations)
        ON CONFLICT DO NOTHING;
    END IF;

    -- Insert the m2m items between the process and resources
    IF array_length(m2m_resources, 1) > 0 THEN
        INSERT INTO resource_process (process_id, resource_id)
        SELECT p_process_id, unnest(m2m_resources)
        ON CONFLICT DO NOTHING;
    END IF;

    -- Return the process
    RETURN QUERY
    SELECT p.id, p.title, p.description, p.created_by_id, p.created_at
    FROM process p
    WHERE p.id = p_process_id;
END;
$$ LANGUAGE plpgsql;
