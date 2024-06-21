DELIMITER //
CREATE PROCEDURE delete_food(IN in_fid INT)
BEGIN
    DELETE FROM `Supply` WHERE `fid` = in_fid;
    UPDATE `Food` SET `on_sale` = 0 WHERE `fid` = in_fid;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE insert_food(IN in_fid INT, IN in_fname VARCHAR(10), IN in_price FLOAT, IN in_wid INT, IN in_meal_type VARCHAR(10))
BEGIN
    IF EXISTS (SELECT * FROM `Food` WHERE `fid` = in_fid) THEN
        INSERT INTO `supply` (`wid`, `fid`, `meal_type`) VALUES (in_wid, in_fid, in_meal_type);
    ELSE
        SET FOREIGN_KEY_CHECKS = 0;
        INSERT INTO `Food` (`fname`, `price`) VALUES (in_fname, in_price);
        SELECT MAX(`fid`) INTO in_fid FROM `Food`;
        INSERT INTO `supply` (`wid`, `fid`, `meal_type`) VALUES (in_wid, in_fid, in_meal_type);
        SET FOREIGN_KEY_CHECKS = 1;
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE update_img(IN in_fid INT, IN in_path VARCHAR(255))
BEGIN
    IF EXISTS (SELECT * FROM `avatar` WHERE id = in_fid) THEN
        UPDATE `avatar` SET `path` = in_path WHERE `id` = in_fid;
    ELSE
        INSERT INTO `avatar` (`id`, `path`) VALUES (in_fid, in_path);
    END IF;
END //

DELIMITER //
CREATE PROCEDURE buy_food(IN userID VARCHAR(10), IN in_fid INT, IN amount INT, IN in_wid INT, OUT state INT)
BEGIN
    DECLARE total_price FLOAT;
    DECLARE balance FLOAT;
    DECLARE opentime TIME;
    DECLARE closetime TIME;
    SET state = 0;
    SELECT `open_time`, `close_time` INTO opentime, closetime FROM `CanteenHours` WHERE `cid` = (SELECT `cid` FROM `Window` WHERE `wid` = in_wid) AND `meal_type` = (SELECT `meal_type` FROM `Supply` WHERE `fid` = in_fid AND `wid` = in_wid);
    IF NOW() >= opentime AND NOW() <= closetime THEN
        SET state = 2;
        START TRANSACTION;
        INSERT INTO `Income` (`wid`, `fid`, `quantity`, `deal_time`, `sid`)
                VALUES (in_wid, in_fid, amount, NOW(), userID);
        SELECT price * amount INTO total_price FROM `food` WHERE `fid` = in_fid;
        SELECT `money` INTO balance FROM `Student` WHERE `sid` = userID;
        IF balance >= total_price THEN
            SET state = 1;
            UPDATE `Student` SET `money` = balance - total_price WHERE `sid` = userID;
            COMMIT;
        ELSE
            SET state = -1;
            ROLLBACK;
        END IF;
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE insert_canteen(IN in_cid INT, IN in_cname VARCHAR(10), IN in_meal_type VARCHAR(10), IN in_open_time TIME, IN in_close_time TIME)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        -- 发生错误时回滚事务
        ROLLBACK;
    END;

    -- 开始事务
    START TRANSACTION;

    IF EXISTS (SELECT * FROM `Canteen` WHERE `cid` = in_cid) THEN
        UPDATE `Canteen` SET `cname` = in_cname WHERE `cid` = in_cid;
        IF EXISTS (SELECT * FROM `CanteenHours` WHERE `cid` = in_cid AND `meal_type` = in_meal_type) THEN
            UPDATE `CanteenHours` SET `open_time` = in_open_time, `close_time` = in_close_time WHERE `cid` = in_cid AND `meal_type` = in_meal_type;
        ELSE
            INSERT INTO `CanteenHours` (`cid`, `meal_type`, `open_time`, `close_time`) VALUES (in_cid, in_meal_type, in_open_time, in_close_time);
        END IF;
    ELSE
        INSERT INTO `Canteen` (`cid`, `cname`) VALUES (in_cid, in_cname);
        INSERT INTO `CanteenHours` (`cid`, `meal_type`, `open_time`, `close_time`) VALUES (in_cid, in_meal_type, in_open_time, in_close_time);
    END IF;

    -- 如果没有错误，提交事务
    COMMIT;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE insert_window(IN in_wid INT, IN in_wname VARCHAR(10), IN in_cid INT)
BEGIN
    IF EXISTS (SELECT * FROM `Window` WHERE `wid` = in_wid) THEN
        IF EXISTS (SELECT * FROM `Canteen` WHERE `cid` = in_cid) THEN
            UPDATE `Window` SET `wname` = in_wname, `cid` = in_cid WHERE `wid` = in_wid;
        ELSE
            UPDATE `employee` SET `wid` = NULL WHERE `wid` = in_wid;
            DELETE FROM `Supply` WHERE `wid` = in_wid;
            UPDATE `Income` SET `wid` = NULL WHERE `wid` = in_wid;
            DELETE FROM `Window` WHERE `wid` = in_wid;
        END IF;
    ELSE
        INSERT INTO `Window` (`wid`, `wname`, `cid`) VALUES (in_wid, in_wname, in_cid);
    END IF;
END //

DELIMITER //
CREATE PROCEDURE delete_canteen(IN in_cid INT)
BEGIN
    DELETE FROM `CanteenHours` WHERE `cid` = in_cid;
    DELETE FROM `Canteen` WHERE `cid` = in_cid;
    SELECT wid FROM `Window` WHERE `cid` = in_cid;
END //