DELIMITER //
CREATE TRIGGER check_hours_before_insert BEFORE INSERT ON `CanteenHours`
FOR EACH ROW
BEGIN
  IF NEW.open_time >= NEW.close_time THEN 
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid hours';
  END IF;
END;
//
DELIMITER ;

DELIMITER //
CREATE TRIGGER check_hours_before_update BEFORE UPDATE ON `CanteenHours`
FOR EACH ROW
BEGIN
  IF NEW.open_time >= NEW.close_time THEN 
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid hours';
  END IF;
END;
//
DELIMITER ;

DELIMITER //
CREATE TRIGGER check_student_gender_before_insert BEFORE INSERT ON `Student`
FOR EACH ROW
BEGIN
  IF NEW.gender NOT IN ('男', '女') THEN 
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid value for gender';
  END IF;
END;
//
DELIMITER ;

DELIMITER //
CREATE TRIGGER check_employee_gender_before_insert BEFORE INSERT ON `Employee`
FOR EACH ROW
BEGIN
  IF NEW.gender NOT IN ('男', '女') THEN 
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid value for gender';
  END IF;
END;
//
DELIMITER ;

DELIMITER //
CREATE TRIGGER delete_id_after_empl_deleted AFTER DELETE ON `Employee`
FOR EACH ROW
BEGIN
  DELETE FROM `identification` WHERE `id` = OLD.eid;
END;
//
DELIMITER ;
