create table authors(
    email varchar(50) primary key,
    name varchar(50) not null,
    passwd varchar(20) not null
);
create table posts(
    email varchar(50) not null,
    title varchar(100) not null,
    post varchar(500) not null,
    date datetime default now(),
    foreign key(email) references authors(email),
    constraint composite primary key(email,title)
);