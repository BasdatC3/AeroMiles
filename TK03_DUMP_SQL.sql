-- DDL

CREATE TABLE PENGGUNA (
    email VARCHAR(100) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    salutation VARCHAR(10) NOT NULL CHECK (salutation IN ('Mr.', 'Mrs.', 'Ms.', 'Dr.')),
    first_mid_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    country_code VARCHAR(5) NOT NULL,
    mobile_number VARCHAR(20) NOT NULL,
    tanggal_lahir DATE NOT NULL,
    kewarganegaraan VARCHAR(50) NOT NULL
);


CREATE TABLE TIER (
    id_tier VARCHAR(10) PRIMARY KEY,
    nama VARCHAR(50) NOT NULL,
    minimal_frekuensi_terbang INT NOT NULL,
    minimal_tier_miles INT NOT NULL
);


CREATE TABLE PENYEDIA (
    id SERIAL PRIMARY KEY
);


CREATE SEQUENCE seq_member_nomor START 1;
CREATE TABLE MEMBER (
    email VARCHAR(100) PRIMARY KEY REFERENCES PENGGUNA(email),
    nomor_member VARCHAR(20) NOT NULL UNIQUE DEFAULT 'M' || lpad(nextval('seq_member_nomor')::text, 4, '0'),
    tanggal_bergabung DATE NOT NULL,
    id_tier VARCHAR(10) NOT NULL REFERENCES TIER(id_tier),
    award_miles INT DEFAULT 0,
    total_miles INT DEFAULT 0 
);


CREATE TABLE MASKAPAI (
    kode_maskapai VARCHAR(10) PRIMARY KEY,
    nama_maskapai VARCHAR(100) NOT NULL,
    id_penyedia INT NOT NULL REFERENCES PENYEDIA(id)
);


CREATE SEQUENCE seq_staf_id START 1;
CREATE TABLE STAF (
    email VARCHAR(100) PRIMARY KEY REFERENCES PENGGUNA(email),
    id_staf VARCHAR(20) NOT NULL UNIQUE DEFAULT 'S' || lpad(nextval('seq_staf_id')::text, 4, '0'),
    kode_maskapai VARCHAR(10) NOT NULL REFERENCES MASKAPAI(kode_maskapai)
);


CREATE TABLE MITRA (
    email_mitra VARCHAR(100) PRIMARY KEY,
    id_penyedia INT NOT NULL UNIQUE REFERENCES PENYEDIA(id) ON DELETE CASCADE,
    nama_mitra VARCHAR(100) NOT NULL,
    tanggal_kerja_sama DATE NOT NULL
);


CREATE TABLE IDENTITAS (
    nomor VARCHAR(50) PRIMARY KEY,
    email_member VARCHAR(100) NOT NULL REFERENCES MEMBER(email) ON DELETE CASCADE,
    tanggal_habis DATE NOT NULL,
    tanggal_terbit DATE NOT NULL,
    negara_penerbit VARCHAR(50) NOT NULL,
    jenis VARCHAR(30) NOT NULL CHECK (jenis IN ('Paspor', 'KTP', 'SIM'))
);


CREATE SEQUENCE seq_amp_id START 1;
CREATE TABLE AWARD_MILES_PACKAGE (
    id VARCHAR(20) PRIMARY KEY DEFAULT 'AMP-' || lpad(nextval('seq_amp_id')::text, 3, '0'),
    harga_paket DECIMAL(15,2) NOT NULL,
    jumlah_award_miles INT NOT NULL
);


CREATE TABLE MEMBER_AWARD_MILES_PACKAGE (
    id_award_miles_package VARCHAR(20) NOT NULL REFERENCES AWARD_MILES_PACKAGE(id),
    email_member VARCHAR(100) NOT NULL REFERENCES MEMBER(email) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL,
    PRIMARY KEY (id_award_miles_package, email_member, timestamp)
);


CREATE TABLE BANDARA (
    iata_code CHAR(3) PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    kota VARCHAR(100) NOT NULL,
    negara VARCHAR(100) NOT NULL
);


CREATE TABLE CLAIM_MISSING_MILES (
    id SERIAL PRIMARY KEY,
    email_member VARCHAR(100) NOT NULL REFERENCES MEMBER(email) ON DELETE CASCADE,
    email_staf VARCHAR(100) REFERENCES STAF(email),
    maskapai VARCHAR(10) NOT NULL REFERENCES MASKAPAI(kode_maskapai),
    bandara_asal VARCHAR(3) NOT NULL REFERENCES BANDARA(iata_code),
    bandara_tujuan VARCHAR(3) NOT NULL REFERENCES BANDARA(iata_code),
    tanggal_penerbangan DATE NOT NULL,
    flight_number VARCHAR(10) NOT NULL,
    nomor_tiket VARCHAR(20) NOT NULL,
    kelas_kabin VARCHAR(20) NOT NULL CHECK (kelas_kabin IN ('Economy', 'Business', 'First')),
    pnr VARCHAR(10) NOT NULL,
    status_penerimaan VARCHAR(20) NOT NULL DEFAULT 'Menunggu',
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_klaim UNIQUE (email_member, flight_number, tanggal_penerbangan, nomor_tiket)
);


CREATE TABLE TRANSFER (
    email_member_1 VARCHAR(100) NOT NULL REFERENCES MEMBER(email) ON DELETE CASCADE,
    email_member_2 VARCHAR(100) NOT NULL REFERENCES MEMBER(email) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    jumlah INT NOT NULL,
    catatan VARCHAR(255),
    PRIMARY KEY (email_member_1, email_member_2, timestamp),

    CONSTRAINT cek_bukan_diri_sendiri CHECK (email_member_1 != email_member_2)
);


CREATE SEQUENCE seq_hadiah_kode START 1;
CREATE TABLE HADIAH (
    kode_hadiah VARCHAR(20) PRIMARY KEY DEFAULT 'RWD-' || lpad(nextval('seq_hadiah_kode')::text, 3, '0'),
    nama VARCHAR(100) NOT NULL,
    miles INT NOT NULL,
    deskripsi TEXT,
    valid_start_date DATE NOT NULL,
    program_end DATE NOT NULL,
    id_penyedia INT NOT NULL REFERENCES PENYEDIA(id) ON DELETE CASCADE
);


CREATE TABLE REDEEM (
    email_member VARCHAR(100) NOT NULL REFERENCES MEMBER(email) ON DELETE CASCADE,
    kode_hadiah VARCHAR(20) NOT NULL REFERENCES HADIAH(kode_hadiah),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (email_member, kode_hadiah, timestamp)
);

-- DML

-- PENYEDIA
INSERT INTO PENYEDIA (id) VALUES (1), (2), (3), (4), (5), (6), (7), (8), (9), (10);

-- MASKAPAI
INSERT INTO MASKAPAI (kode_maskapai, nama_maskapai, id_penyedia) VALUES
('GA', 'Garuda Indonesia', 1), ('SQ', 'Singapore Airlines', 2),
('QZ', 'Indonesia AirAsia', 3), ('JT', 'Lion Air', 4), ('AK', 'AirAsia', 5);

-- STAF
INSERT INTO STAF (email, id_staf, kode_maskapai) VALUES
('staf1@aeromiles.com', 'S0001', 'GA'), ('staf2@aeromiles.com', 'S0002', 'SQ'),
('staf3@aeromiles.com', 'S0003', 'QZ'), ('staf4@aeromiles.com', 'S0004', 'JT'),
('staf5@aeromiles.com', 'S0005', 'AK'), ('staf6@aeromiles.com', 'S0006', 'GA'),
('staf7@aeromiles.com', 'S0007', 'SQ'), ('staf8@aeromiles.com', 'S0008', 'QZ'),
('staf9@aeromiles.com', 'S0009', 'JT'), ('staf10@aeromiles.com', 'S0010', 'AK');

-- MITRA
INSERT INTO MITRA (email_mitra, id_penyedia, nama_mitra, tanggal_kerja_sama) VALUES
('contact@traveloka.com', 6, 'Traveloka', '2020-01-01'), ('halo@tiket.com', 7, 'Tiket.com', '2021-05-15'),
('admin@booking.com', 8, 'Booking.com', '2019-10-10'), ('info@agoda.com', 9, 'Agoda', '2018-02-20'),
('support@blibli.com', 10, 'Blibli', '2022-07-07');

-- HADIAH
INSERT INTO HADIAH (kode_hadiah, nama, miles, deskripsi, valid_start_date, program_end, id_penyedia) VALUES
('RWD-001', 'Voucher Hotel', 5000, 'Potongan 500rb', '2024-01-01', '2024-12-31', 6),
('RWD-002', 'Upgrade Business', 15000, 'Upgrade kelas penerbangan', '2024-01-01', '2024-12-31', 1),
('RWD-003', 'Akses Lounge', 3000, 'Akses ruang tunggu premium', '2024-01-01', '2024-12-31', 1),
('RWD-004', 'Voucher Resto', 2000, 'Makan gratis 200rb', '2024-01-01', '2024-12-31', 7),
('RWD-005', 'Merchandise', 1000, 'Kaos eksklusif', '2024-01-01', '2024-12-31', 8),
('RWD-006', 'Voucher Taksi', 500, 'Diskon taksi bandara', '2024-01-01', '2024-12-31', 9),
('RWD-007', 'Ekstra Bagasi 10kg', 4000, 'Tambahan kapasitas bagasi', '2024-01-01', '2024-12-31', 2),
('RWD-008', 'Voucher Belanja', 3500, 'Voucher e-commerce', '2024-01-01', '2024-12-31', 10),
('RWD-009', 'Asuransi Perjalanan', 2500, 'Asuransi gratis untuk 1 trip', '2024-01-01', '2024-12-31', 3),
('RWD-010', 'Priority Boarding', 1500, 'Naik pesawat lebih dulu', '2024-01-01', '2024-12-31', 4);

-- REDEEM
INSERT INTO REDEEM (email_member, kode_hadiah, timestamp) VALUES
('member1@gmail.com', 'RWD-001', '2024-04-10 10:00:00'), ('member2@gmail.com', 'RWD-002', '2024-04-11 10:00:00'),
('member3@gmail.com', 'RWD-003', '2024-04-12 10:00:00'), ('member4@gmail.com', 'RWD-004', '2024-04-13 10:00:00'),
('member5@gmail.com', 'RWD-005', '2024-04-14 10:00:00'), ('member6@gmail.com', 'RWD-006', '2024-04-15 10:00:00'),
('member7@gmail.com', 'RWD-007', '2024-04-16 10:00:00'), ('member8@gmail.com', 'RWD-008', '2024-04-17 10:00:00'),
('member9@gmail.com', 'RWD-009', '2024-04-18 10:00:00'), ('member10@gmail.com', 'RWD-010', '2024-04-19 10:00:00'),
('member11@gmail.com', 'RWD-001', '2024-04-20 10:00:00'), ('member12@gmail.com', 'RWD-002', '2024-04-21 10:00:00'),
('member13@gmail.com', 'RWD-003', '2024-04-22 10:00:00'), ('member14@gmail.com', 'RWD-004', '2024-04-23 10:00:00'),
('member15@gmail.com', 'RWD-005', '2024-04-24 10:00:00'), ('member16@gmail.com', 'RWD-006', '2024-04-25 10:00:00'),
('member17@gmail.com', 'RWD-007', '2024-04-26 10:00:00'), ('member18@gmail.com', 'RWD-008', '2024-04-27 10:00:00'),
('member19@gmail.com', 'RWD-009', '2024-04-28 10:00:00'), ('member20@gmail.com', 'RWD-010', '2024-04-29 10:00:00');

