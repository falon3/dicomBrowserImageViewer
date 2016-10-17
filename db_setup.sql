/*to first create database, loginto mysql and use the following:

	create database dcmviewer;
	use dcmviewer;
*/

/* create all of the tables*/
create table users (
	id INT(11) NOT NUll AUTO_INCREMENT, 
	name VARCHAR(50) NOT NULL Unique,
	password VARCHAR(256) NOT NULL,
	salt VARCHAR(256) NOT NULL,
	email VARCHAR(50),
	Primary Key (id)
);

create table image_sets (
	id INT(11) NOT NUll AUTO_INCREMENT, 
	user_id INT NOT NULL,
	name VARCHAR(50)NOT NULL,
	Primary Key (id),
	Foreign key (user_id) references users(id)
);

create table images (
	id INT(11) NOT NUll AUTO_INCREMENT, 
	set_id INT NOT NULL,
	image BLOB NOT NULL,
	Primary Key (id),
	Foreign key (set_id) references image_sets(id)
);
