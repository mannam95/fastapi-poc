-- Insert a user (needed because created_by_id is required everywhere)
-- do not insert ids as they are auto-incremented
INSERT INTO users (title, created_at)
VALUES ('Test User', NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert departments
INSERT INTO departments (title, created_at, created_by_id)
VALUES 
    ('Engineering', NOW(), 1),
    ('HR', NOW(), 1)
ON CONFLICT (id) DO NOTHING;

-- Insert locations
INSERT INTO locations (title, created_at, created_by_id)
VALUES 
    ('New York Office', NOW(), 1),
    ('San Francisco Office', NOW(), 1)
ON CONFLICT (id) DO NOTHING;

-- Insert resources
INSERT INTO resources (title, created_at, created_by_id)
VALUES 
    ('AWS Server', NOW(), 1),
    ('Internal Wiki', NOW(), 1)
ON CONFLICT (id) DO NOTHING;

-- Insert roles
INSERT INTO roles (title, created_at, created_by_id)
VALUES 
    ('Admin', NOW(), 1),
    ('Editor', NOW(), 1)
ON CONFLICT (id) DO NOTHING;

-- Optionally, insert a test process
INSERT INTO process (title, description, created_at, created_by_id)
VALUES 
    ('Onboarding Process', 'Handles onboarding of new employees', NOW(), 1)
ON CONFLICT (id) DO NOTHING;

-- Optional: link the process with departments/locations/resources/roles if your M2M tables exist
-- Example for department_process junction table:
INSERT INTO department_process (department_id, process_id)
VALUES 
    (1, 1),
    (2, 1)
ON CONFLICT DO NOTHING;

-- Similarly for location_process:
INSERT INTO location_process (location_id, process_id)
VALUES 
    (1, 1),
    (2, 1)
ON CONFLICT DO NOTHING;

-- Similarly for resource_process:
INSERT INTO resource_process (resource_id, process_id)
VALUES 
    (1, 1),
    (2, 1)
ON CONFLICT DO NOTHING;

-- Similarly for role_process:
INSERT INTO role_process (role_id, process_id)
VALUES 
    (1, 1),
    (2, 1)
ON CONFLICT DO NOTHING;
