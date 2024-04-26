CREATE TABLE users (
    id INT AUTO_INCREMENT,
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL,
    create_time DATETIME NOT NULL,
    update_time DATETIME NOT NULL
);

INSERT INTO users (username, password, email, create_time, update_time)
VALUES ('admin', '827ccb0eea8a706c4c34a16891f84e', 'qq.com', '2024-04-18 21:58:14', '2024-04-18 22:00:31');