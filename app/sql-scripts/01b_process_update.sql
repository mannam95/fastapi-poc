-- A function to update a process with m2m tables
-- p_created_by_id is not used in the update
-- Example usage:
-- SELECT * FROM update_process_with_m2m(
--     1,
--     'Process 1',
--     'Description 1',
--     1, ARRAY[1, 2], ARRAY[1, 2], ARRAY[1, 2], ARRAY[1, 2]);
CREATE OR REPLACE FUNCTION update_process_with_m2m(
    p_id INTEGER,
    p_title TEXT,
    p_description TEXT,
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
    -- Update the process
    UPDATE process
    SET title = p_title, description = p_description
    WHERE process.id = p_id
    RETURNING process.id INTO p_process_id;

    -- Delete + Insert the m2m items between the process and roles
    DELETE FROM role_process WHERE process_id = p_process_id;
    IF array_length(m2m_roles, 1) > 0 THEN
        INSERT INTO role_process (process_id, role_id)
        SELECT p_process_id, unnest(m2m_roles)
        ON CONFLICT DO NOTHING;
    END IF;

    -- Delete + Insert the m2m items between the process and departments
    DELETE FROM department_process WHERE process_id = p_process_id;
    IF array_length(m2m_departments, 1) > 0 THEN
        INSERT INTO department_process (process_id, department_id)
        SELECT p_process_id, unnest(m2m_departments)
        ON CONFLICT DO NOTHING;
    END IF;

    -- Delete + Insert the m2m items between the process and locations
    DELETE FROM location_process WHERE process_id = p_process_id;
    IF array_length(m2m_locations, 1) > 0 THEN
        INSERT INTO location_process (process_id, location_id)
        SELECT p_process_id, unnest(m2m_locations)
        ON CONFLICT DO NOTHING;
    END IF;

    -- Delete + Insert the m2m items between the process and resources
    DELETE FROM resource_process WHERE process_id = p_process_id;
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

