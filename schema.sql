

CREATE TABLE
IF NOT EXISTS Users
(
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    profile_pic TEXT NOT NULL
);



CREATE TABLE
IF NOT EXISTS  Subs
(

    subid TEXT PRIMARY KEY,
    id TEXT,
    FOREIGN KEY
(id) REFERENCES Users
(id),
    subreddit TEXT NOT NULL,
    frequency TEXT NOT NULL
);