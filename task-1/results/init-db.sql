create table client
(
  client_id serial primary key,
--
  client_name varchar(100) not null,
  email varchar(50) not null,
  registration_date date not null,
  loyalty_level varchar(50) not null,
--
  unique (email)
);

insert into client values
  (1, 'Петров О.А.', 'petrov@example.com', '2024-02-17', 'bronze'),
  (2, 'Иванов С.С.', 'ivanov@example.com', '2024-07-23', 'silver'),
  (3, 'Сидоров А.П.', 'sidorov@example.com', '2025-05-12', 'gold');

create table order_
(
  order_id serial primary key,
--
  client_id integer not null,
  order_date date not null,
  amount decimal(15,2) not null,
  status varchar(50) not null,
--
  foreign key (client_id) references client
);

insert into order_ values
  (1, 1, '2025-04-02', 12000.00, 'completed'),
  (2, 2, '2025-05-31', 22000.00, 'cancelled'),
  (3, 3, '2025-06-22', 1400.00, 'completed'),
  (4, 3, '2025-06-12', 1000.00, 'completed'),
  (5, 2, '2025-07-01', 8000.00, 'completed');

create table report
(
  report_id serial primary key,
--
  processing_type varchar(10) not null,
  delivered_amount decimal(15,2) not null,
--
  created_at timestamptz default now() not null
);
