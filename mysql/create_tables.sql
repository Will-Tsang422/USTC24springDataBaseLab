CREATE TABLE `Canteen` (
  `cid` integer PRIMARY KEY,
  `cname` varchar(10) NOT NULL
);

CREATE TABLE `CanteenHours` (
  `cid` integer,
  `meal_type` varchar(10),
  `open_time` time,
  `close_time` time,
  PRIMARY KEY (`cid`, `meal_type`)
);

CREATE TABLE `Window` (
  `wid` integer PRIMARY KEY,
  `wname` varchar(10),
  `cid` integer NOT NULL
);

CREATE TABLE `Income` (
  `iid` integer PRIMARY KEY AUTO_INCREMENT,
  `wid` integer,
  `fid` integer,
  `quantity` integer NOT NULL,
  `deal_time` timestamp NOT NULL,
  `sid` varchar(10)
);

CREATE TABLE `Admin` (
  `aid` varchar(10) PRIMARY KEY
);

CREATE TABLE `Employee` (
  `eid` varchar(10) PRIMARY KEY,
  `ename` varchar(10) NOT NULL,
  `age` integer NOT NULL,
  `gender` char(1) NOT NULL,
  `Tel` char(11) UNIQUE,
  `wid` integer
);

CREATE TABLE `Food` (
  `fid` integer PRIMARY KEY AUTO_INCREMENT,
  `fname` varchar(10) NOT NULL,
  `price` float NOT NULL,
  `on_sale` bool DEFAULT 1,
  `path` varchar(255)
);

CREATE TABLE `Supply` (
  `wid` integer,
  `fid` integer,
  `meal_type` varchar(10),
  PRIMARY KEY (`wid`, `fid`, `meal_type`)
);

CREATE TABLE `Student` (
  `sid` varchar(10) PRIMARY KEY,
  `sname` varchar(10) NOT NULL,
  `age` integer NOT NULL,
  `gender` char(1) NOT NULL,
  `Tel` char(11) UNIQUE,
  `degree` varchar(10) NOT NULL,
  `money` float DEFAULT 0
);

CREATE TABLE `identification` (
  `id` varchar(10) PRIMARY KEY,
  `password` varchar(255) NOT NULL
);

ALTER TABLE `CanteenHours` ADD FOREIGN KEY (`cid`) REFERENCES `Canteen` (`cid`);

ALTER TABLE `Window` ADD FOREIGN KEY (`cid`) REFERENCES `Canteen` (`cid`);

ALTER TABLE `Income` ADD FOREIGN KEY (`wid`) REFERENCES `Window` (`wid`);

ALTER TABLE `Income` ADD FOREIGN KEY (`fid`) REFERENCES `Food` (`fid`);

ALTER TABLE `Income` ADD FOREIGN KEY (`sid`) REFERENCES `Student` (`sid`);

ALTER TABLE `Admin` ADD FOREIGN KEY (`aid`) REFERENCES `identification` (`id`);

ALTER TABLE `Employee` ADD FOREIGN KEY (`eid`) REFERENCES `identification` (`id`);

ALTER TABLE `Employee` ADD FOREIGN KEY (`wid`) REFERENCES `Window` (`wid`);

ALTER TABLE `Supply` ADD FOREIGN KEY (`wid`) REFERENCES `Window` (`wid`);

ALTER TABLE `Supply` ADD FOREIGN KEY (`fid`) REFERENCES `Food` (`fid`);

ALTER TABLE `Student` ADD FOREIGN KEY (`sid`) REFERENCES `identification` (`id`);
