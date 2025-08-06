-- Stored procedure for enhanced signup with hot majors
DELIMITER $$

CREATE PROCEDURE sp_basic_signup (
    IN  p_username       VARCHAR(50),
    IN  p_email          VARCHAR(255),
    IN  p_password_hash  VARCHAR(255)
)
BEGIN
    DECLARE v_user_id INT;

    -- Check for duplicate username or email
    IF EXISTS (SELECT 1 FROM User
               WHERE username = p_username
                  OR email    = p_email) THEN
        SIGNAL SQLSTATE '45000'
               SET MESSAGE_TEXT = 'Username or e-mail already taken';
    END IF;

    -- Insert new user
    INSERT INTO User (username, email, password_hash)
    VALUES (p_username, p_email, p_password_hash);

    SET v_user_id = LAST_INSERT_ID();

    -- Insert top 3 "hot" majors based on recent SavedComparison activity
    INSERT INTO SavedComparison (user_id, major_id, saved_at)
    SELECT v_user_id, major_id, NOW()
    FROM (
        SELECT sc.major_id
        FROM   SavedComparison sc
        WHERE  sc.saved_at >= NOW() - INTERVAL 30 DAY
        GROUP  BY sc.major_id
        ORDER  BY COUNT(*) DESC
        LIMIT 3
    ) AS hot;
END$$

DELIMITER ;

INSERT INTO SavedComparison (user_id, major_id, saved_at) VALUES 
(1, 1, NOW() - INTERVAL 1 DAY),
(1, 2, NOW() - INTERVAL 2 DAY),
(2, 1, NOW() - INTERVAL 3 DAY),
(2, 3, NOW() - INTERVAL 4 DAY),
(3, 1, NOW() - INTERVAL 5 DAY),
(3, 2, NOW() - INTERVAL 6 DAY),
(4, 1, NOW() - INTERVAL 7 DAY),
(4, 4, NOW() - INTERVAL 8 DAY); 