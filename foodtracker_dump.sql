PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE user (
	id INTEGER NOT NULL, 
	email VARCHAR(150), 
	confirmed BOOLEAN, 
	password VARCHAR(150), 
	first_name VARCHAR(150), 
	PRIMARY KEY (id), 
	UNIQUE (email)
);
INSERT INTO user VALUES(1,'derrickmacha1@gmail.com',1,'pbkdf2:sha256:1000000$Z5sJ7xxMpxnyiFfV$fe613c5873825faf6c62af99f224e7bce703f5195e5a1913417db8221b085bf2','Derrick');
CREATE TABLE food (
	id INTEGER NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	proteins INTEGER NOT NULL, 
	carbs INTEGER NOT NULL, 
	fats INTEGER NOT NULL, 
	user_id INTEGER, 
	PRIMARY KEY (id), 
	UNIQUE (name), 
	FOREIGN KEY(user_id) REFERENCES user (id)
);
CREATE TABLE log (
	id INTEGER NOT NULL, 
	date DATE NOT NULL, 
	user_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES user (id)
);
CREATE TABLE log_food (
	log_id INTEGER NOT NULL, 
	food_id INTEGER NOT NULL, 
	PRIMARY KEY (log_id, food_id), 
	FOREIGN KEY(log_id) REFERENCES log (id), 
	FOREIGN KEY(food_id) REFERENCES food (id)
);
COMMIT;
