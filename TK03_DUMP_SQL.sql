
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

INSERT INTO PENGGUNA (email, password, salutation, first_mid_name, last_name, country_code, mobile_number, tanggal_lahir, kewarganegaraan) VALUES
('member1@gmail.com', 'hash1', 'Mr.', 'Member', 'Satu', '+62', '811000001', '1990-01-01', 'Indonesia'),
('member2@gmail.com', 'hash2', 'Mrs.', 'Member', 'Dua', '+62', '811000002', '1990-01-02', 'Indonesia'),
('member3@gmail.com', 'hash3', 'Mr.', 'Member', 'Tiga', '+62', '811000003', '1990-01-03', 'Indonesia'),
('member4@gmail.com', 'hash4', 'Mrs.', 'Member', 'Empat', '+62', '811000004', '1990-01-04', 'Indonesia'),
('member5@gmail.com', 'hash5', 'Mr.', 'Member', 'Lima', '+62', '811000005', '1990-01-05', 'Indonesia'),
('member6@gmail.com', 'hash6', 'Mrs.', 'Member', 'Enam', '+62', '811000006', '1990-01-06', 'Indonesia'),
('member7@gmail.com', 'hash7', 'Mr.', 'Member', 'Tujuh', '+62', '811000007', '1990-01-07', 'Indonesia'),
('member8@gmail.com', 'hash8', 'Mrs.', 'Member', 'Delapan', '+62', '811000008', '1990-01-08', 'Indonesia'),
('member9@gmail.com', 'hash9', 'Mr.', 'Member', 'Sembilan', '+62', '811000009', '1990-01-09', 'Indonesia'),
('member10@gmail.com', 'hash10', 'Mrs.', 'Member', 'Sepuluh', '+62', '811000010', '1990-01-10', 'Indonesia'),
('member11@gmail.com', 'hash11', 'Mr.', 'Member', 'Sebelas', '+62', '811000011', '1990-01-11', 'Indonesia'),
('member12@gmail.com', 'hash12', 'Mrs.', 'Member', 'Duabelas', '+62', '811000012', '1990-01-12', 'Indonesia'),
('member13@gmail.com', 'hash13', 'Mr.', 'Member', 'Tigabelas', '+62', '811000013', '1990-01-13', 'Indonesia'),
('member14@gmail.com', 'hash14', 'Mrs.', 'Member', 'Empatbelas', '+62', '811000014', '1990-01-14', 'Indonesia'),
('member15@gmail.com', 'hash15', 'Mr.', 'Member', 'Limabelas', '+62', '811000015', '1990-01-15', 'Indonesia'),
('member16@gmail.com', 'hash16', 'Mrs.', 'Member', 'Enambelas', '+62', '811000016', '1990-01-16', 'Indonesia'),
('member17@gmail.com', 'hash17', 'Mr.', 'Member', 'Tujuhbelas', '+62', '811000017', '1990-01-17', 'Indonesia'),
('member18@gmail.com', 'hash18', 'Mrs.', 'Member', 'Delapanbelas', '+62', '811000018', '1990-01-18', 'Indonesia'),
('member19@gmail.com', 'hash19', 'Mr.', 'Member', 'Sembilanbelas', '+62', '811000019', '1990-01-19', 'Indonesia'),
('member20@gmail.com', 'hash20', 'Mrs.', 'Member', 'Duapuluh', '+62', '811000020', '1990-01-20', 'Indonesia'),
('member21@gmail.com', 'hash21', 'Mr.', 'Member', 'Duasatu', '+62', '811000021', '1990-01-21', 'Indonesia'),
('member22@gmail.com', 'hash22', 'Mrs.', 'Member', 'Duadua', '+62', '811000022', '1990-01-22', 'Indonesia'),
('member23@gmail.com', 'hash23', 'Mr.', 'Member', 'Duatiga', '+62', '811000023', '1990-01-23', 'Indonesia'),
('member24@gmail.com', 'hash24', 'Mrs.', 'Member', 'Duaempat', '+62', '811000024', '1990-01-24', 'Indonesia'),
('member25@gmail.com', 'hash25', 'Mr.', 'Member', 'Dualima', '+62', '811000025', '1990-01-25', 'Indonesia'),
('member26@gmail.com', 'hash26', 'Mrs.', 'Member', 'Duaenam', '+62', '811000026', '1990-01-26', 'Indonesia'),
('member27@gmail.com', 'hash27', 'Mr.', 'Member', 'Duatujuh', '+62', '811000027', '1990-01-27', 'Indonesia'),
('member28@gmail.com', 'hash28', 'Mrs.', 'Member', 'Duadelapan', '+62', '811000028', '1990-01-28', 'Indonesia'),
('member29@gmail.com', 'hash29', 'Mr.', 'Member', 'Duasembilan', '+62', '811000029', '1990-01-29', 'Indonesia'),
('member30@gmail.com', 'hash30', 'Mrs.', 'Member', 'Tigapuluh', '+62', '811000030', '1990-01-30', 'Indonesia'),
('member31@gmail.com', 'hash31', 'Mr.', 'Member', 'Tigasatu', '+62', '811000031', '1990-01-31', 'Indonesia'),
('member32@gmail.com', 'hash32', 'Mrs.', 'Member', 'Tigadua', '+62', '811000032', '1990-02-01', 'Indonesia'),
('member33@gmail.com', 'hash33', 'Mr.', 'Member', 'Tigatiga', '+62', '811000033', '1990-02-02', 'Indonesia'),
('member34@gmail.com', 'hash34', 'Mrs.', 'Member', 'Tigaempat', '+62', '811000034', '1990-02-03', 'Indonesia'),
('member35@gmail.com', 'hash35', 'Mr.', 'Member', 'Tigalima', '+62', '811000035', '1990-02-04', 'Indonesia'),
('member36@gmail.com', 'hash36', 'Mrs.', 'Member', 'Tigaenam', '+62', '811000036', '1990-02-05', 'Indonesia'),
('member37@gmail.com', 'hash37', 'Mr.', 'Member', 'Tigatujuh', '+62', '811000037', '1990-02-06', 'Indonesia'),
('member38@gmail.com', 'hash38', 'Mrs.', 'Member', 'Tigadelapan', '+62', '811000038', '1990-02-07', 'Indonesia'),
('member39@gmail.com', 'hash39', 'Mr.', 'Member', 'Tigasembilan', '+62', '811000039', '1990-02-08', 'Indonesia'),
('member40@gmail.com', 'hash40', 'Mrs.', 'Member', 'Empatpuluh', '+62', '811000040', '1990-02-09', 'Indonesia'),
('member41@gmail.com', 'hash41', 'Mr.', 'Member', 'Empatsatu', '+62', '811000041', '1990-02-10', 'Indonesia'),
('member42@gmail.com', 'hash42', 'Mrs.', 'Member', 'Empatdua', '+62', '811000042', '1990-02-11', 'Indonesia'),
('member43@gmail.com', 'hash43', 'Mr.', 'Member', 'Empattiga', '+62', '811000043', '1990-02-12', 'Indonesia'),
('member44@gmail.com', 'hash44', 'Mrs.', 'Member', 'Empatempat', '+62', '811000044', '1990-02-13', 'Indonesia'),
('member45@gmail.com', 'hash45', 'Mr.', 'Member', 'Empatlima', '+62', '811000045', '1990-02-14', 'Indonesia'),
('member46@gmail.com', 'hash46', 'Mrs.', 'Member', 'Empatenam', '+62', '811000046', '1990-02-15', 'Indonesia'),
('member47@gmail.com', 'hash47', 'Mr.', 'Member', 'Empattujuh', '+62', '811000047', '1990-02-16', 'Indonesia'),
('member48@gmail.com', 'hash48', 'Mrs.', 'Member', 'Empatdelapan', '+62', '811000048', '1990-02-17', 'Indonesia'),
('member49@gmail.com', 'hash49', 'Mr.', 'Member', 'Empatsembilan', '+62', '811000049', '1990-02-18', 'Indonesia'),
('member50@gmail.com', 'hash50', 'Mrs.', 'Member', 'Limapuluh', '+62', '811000050', '1990-02-19', 'Indonesia'),
('staf1@aeromiles.com', 'hashS1', 'Mr.', 'Staf', 'Satu', '+62', '822000001', '1985-01-01', 'Indonesia'),
('staf2@aeromiles.com', 'hashS2', 'Mrs.', 'Staf', 'Dua', '+62', '822000002', '1985-01-02', 'Indonesia'),
('staf3@aeromiles.com', 'hashS3', 'Mr.', 'Staf', 'Tiga', '+62', '822000003', '1985-01-03', 'Indonesia'),
('staf4@aeromiles.com', 'hashS4', 'Mrs.', 'Staf', 'Empat', '+62', '822000004', '1985-01-04', 'Indonesia'),
('staf5@aeromiles.com', 'hashS5', 'Mr.', 'Staf', 'Lima', '+62', '822000005', '1985-01-05', 'Indonesia'),
('staf6@aeromiles.com', 'hashS6', 'Mrs.', 'Staf', 'Enam', '+62', '822000006', '1985-01-06', 'Indonesia'),
('staf7@aeromiles.com', 'hashS7', 'Mr.', 'Staf', 'Tujuh', '+62', '822000007', '1985-01-07', 'Indonesia'),
('staf8@aeromiles.com', 'hashS8', 'Mrs.', 'Staf', 'Delapan', '+62', '822000008', '1985-01-08', 'Indonesia'),
('staf9@aeromiles.com', 'hashS9', 'Mr.', 'Staf', 'Sembilan', '+62', '822000009', '1985-01-09', 'Indonesia'),
('staf10@aeromiles.com', 'hashS10', 'Mrs.', 'Staf', 'Sepuluh', '+62', '822000010', '1985-01-10', 'Indonesia');

INSERT INTO TIER (id_tier, nama, minimal_frekuensi_terbang, minimal_tier_miles) VALUES
('T01', 'Blue', 0, 0),
('T02', 'Silver', 10, 10000),
('T03', 'Gold', 30, 30000),
('T04', 'Platinum', 50, 50000);

INSERT INTO PENYEDIA (id) VALUES (1), (2), (3), (4), (5), (6), (7), (8), (9), (10);

INSERT INTO MASKAPAI (kode_maskapai, nama_maskapai, id_penyedia) VALUES
('GA', 'Garuda Indonesia', 1),
('SQ', 'Singapore Airlines', 2),
('QZ', 'Indonesia AirAsia', 3),
('JT', 'Lion Air', 4),
('AK', 'AirAsia', 5);

INSERT INTO MEMBER (email, nomor_member, tanggal_bergabung, id_tier, award_miles, total_miles) VALUES
('member1@gmail.com', 'M0001', '2023-01-01', 'T01', 5000, 5000),
('member2@gmail.com', 'M0002', '2023-01-02', 'T02', 15000, 15000),
('member3@gmail.com', 'M0003', '2023-01-03', 'T03', 35000, 35000),
('member4@gmail.com', 'M0004', '2023-01-04', 'T04', 60000, 60000),
('member5@gmail.com', 'M0005', '2023-01-05', 'T01', 2000, 2000),
('member6@gmail.com', 'M0006', '2023-01-06', 'T01', 3000, 3000),
('member7@gmail.com', 'M0007', '2023-01-07', 'T02', 12000, 12000),
('member8@gmail.com', 'M0008', '2023-01-08', 'T01', 4000, 4000),
('member9@gmail.com', 'M0009', '2023-01-09', 'T03', 31000, 31000),
('member10@gmail.com', 'M0010', '2023-01-10', 'T01', 1000, 1000),
('member11@gmail.com', 'M0011', '2023-01-11', 'T01', 5000, 5000),
('member12@gmail.com', 'M0012', '2023-01-12', 'T01', 5000, 5000),
('member13@gmail.com', 'M0013', '2023-01-13', 'T01', 5000, 5000),
('member14@gmail.com', 'M0014', '2023-01-14', 'T01', 5000, 5000),
('member15@gmail.com', 'M0015', '2023-01-15', 'T01', 5000, 5000),
('member16@gmail.com', 'M0016', '2023-01-16', 'T01', 5000, 5000),
('member17@gmail.com', 'M0017', '2023-01-17', 'T01', 5000, 5000),
('member18@gmail.com', 'M0018', '2023-01-18', 'T01', 5000, 5000),
('member19@gmail.com', 'M0019', '2023-01-19', 'T01', 5000, 5000),
('member20@gmail.com', 'M0020', '2023-01-20', 'T01', 5000, 5000),
('member21@gmail.com', 'M0021', '2023-01-21', 'T01', 5000, 5000),
('member22@gmail.com', 'M0022', '2023-01-22', 'T01', 5000, 5000),
('member23@gmail.com', 'M0023', '2023-01-23', 'T01', 5000, 5000),
('member24@gmail.com', 'M0024', '2023-01-24', 'T01', 5000, 5000),
('member25@gmail.com', 'M0025', '2023-01-25', 'T01', 5000, 5000),
('member26@gmail.com', 'M0026', '2023-01-26', 'T01', 5000, 5000),
('member27@gmail.com', 'M0027', '2023-01-27', 'T01', 5000, 5000),
('member28@gmail.com', 'M0028', '2023-01-28', 'T01', 5000, 5000),
('member29@gmail.com', 'M0029', '2023-01-29', 'T01', 5000, 5000),
('member30@gmail.com', 'M0030', '2023-01-30', 'T01', 5000, 5000),
('member31@gmail.com', 'M0031', '2023-01-31', 'T01', 5000, 5000),
('member32@gmail.com', 'M0032', '2023-02-01', 'T01', 5000, 5000),
('member33@gmail.com', 'M0033', '2023-02-02', 'T01', 5000, 5000),
('member34@gmail.com', 'M0034', '2023-02-03', 'T01', 5000, 5000),
('member35@gmail.com', 'M0035', '2023-02-04', 'T01', 5000, 5000),
('member36@gmail.com', 'M0036', '2023-02-05', 'T01', 5000, 5000),
('member37@gmail.com', 'M0037', '2023-02-06', 'T01', 5000, 5000),
('member38@gmail.com', 'M0038', '2023-02-07', 'T01', 5000, 5000),
('member39@gmail.com', 'M0039', '2023-02-08', 'T01', 5000, 5000),
('member40@gmail.com', 'M0040', '2023-02-09', 'T01', 5000, 5000),
('member41@gmail.com', 'M0041', '2023-02-10', 'T01', 5000, 5000),
('member42@gmail.com', 'M0042', '2023-02-11', 'T01', 5000, 5000),
('member43@gmail.com', 'M0043', '2023-02-12', 'T01', 5000, 5000),
('member44@gmail.com', 'M0044', '2023-02-13', 'T01', 5000, 5000),
('member45@gmail.com', 'M0045', '2023-02-14', 'T01', 5000, 5000),
('member46@gmail.com', 'M0046', '2023-02-15', 'T01', 5000, 5000),
('member47@gmail.com', 'M0047', '2023-02-16', 'T01', 5000, 5000),
('member48@gmail.com', 'M0048', '2023-02-17', 'T01', 5000, 5000),
('member49@gmail.com', 'M0049', '2023-02-18', 'T01', 5000, 5000),
('member50@gmail.com', 'M0050', '2023-02-19', 'T01', 5000, 5000);

INSERT INTO STAF (email, id_staf, kode_maskapai) VALUES
('staf1@aeromiles.com', 'S0001', 'GA'),
('staf2@aeromiles.com', 'S0002', 'SQ'),
('staf3@aeromiles.com', 'S0003', 'QZ'),
('staf4@aeromiles.com', 'S0004', 'JT'),
('staf5@aeromiles.com', 'S0005', 'AK'),
('staf6@aeromiles.com', 'S0006', 'GA'),
('staf7@aeromiles.com', 'S0007', 'SQ'),
('staf8@aeromiles.com', 'S0008', 'QZ'),
('staf9@aeromiles.com', 'S0009', 'JT'),
('staf10@aeromiles.com', 'S0010', 'AK');

INSERT INTO MITRA (email_mitra, id_penyedia, nama_mitra, tanggal_kerja_sama) VALUES
('contact@traveloka.com', 6, 'Traveloka', '2020-01-01'),
('halo@tiket.com', 7, 'Tiket.com', '2021-05-15'),
('admin@booking.com', 8, 'Booking.com', '2019-10-10'),
('info@agoda.com', 9, 'Agoda', '2018-02-20'),
('support@blibli.com', 10, 'Blibli', '2022-07-07');

INSERT INTO IDENTITAS (nomor, email_member, tanggal_habis, tanggal_terbit, negara_penerbit, jenis) VALUES
('ID001', 'member1@gmail.com', '2028-01-01', '2023-01-01', 'Indonesia', 'KTP'),
('ID002', 'member2@gmail.com', '2028-01-02', '2023-01-02', 'Indonesia', 'Paspor'),
('ID003', 'member3@gmail.com', '2028-01-03', '2023-01-03', 'Indonesia', 'SIM'),
('ID004', 'member4@gmail.com', '2028-01-04', '2023-01-04', 'Indonesia', 'KTP'),
('ID005', 'member5@gmail.com', '2028-01-05', '2023-01-05', 'Indonesia', 'Paspor'),
('ID006', 'member6@gmail.com', '2028-01-06', '2023-01-06', 'Indonesia', 'SIM'),
('ID007', 'member7@gmail.com', '2028-01-07', '2023-01-07', 'Indonesia', 'KTP'),
('ID008', 'member8@gmail.com', '2028-01-08', '2023-01-08', 'Indonesia', 'Paspor'),
('ID009', 'member9@gmail.com', '2028-01-09', '2023-01-09', 'Indonesia', 'SIM'),
('ID010', 'member10@gmail.com', '2028-01-10', '2023-01-10', 'Indonesia', 'KTP'),
('ID011', 'member11@gmail.com', '2028-01-11', '2023-01-11', 'Indonesia', 'Paspor'),
('ID012', 'member12@gmail.com', '2028-01-12', '2023-01-12', 'Indonesia', 'SIM'),
('ID013', 'member13@gmail.com', '2028-01-13', '2023-01-13', 'Indonesia', 'KTP'),
('ID014', 'member14@gmail.com', '2028-01-14', '2023-01-14', 'Indonesia', 'Paspor'),
('ID015', 'member15@gmail.com', '2028-01-15', '2023-01-15', 'Indonesia', 'SIM'),
('ID016', 'member16@gmail.com', '2028-01-16', '2023-01-16', 'Indonesia', 'KTP'),
('ID017', 'member17@gmail.com', '2028-01-17', '2023-01-17', 'Indonesia', 'Paspor'),
('ID018', 'member18@gmail.com', '2028-01-18', '2023-01-18', 'Indonesia', 'SIM'),
('ID019', 'member19@gmail.com', '2028-01-19', '2023-01-19', 'Indonesia', 'KTP'),
('ID020', 'member20@gmail.com', '2028-01-20', '2023-01-20', 'Indonesia', 'Paspor'),
('ID021', 'member21@gmail.com', '2028-01-21', '2023-01-21', 'Indonesia', 'SIM'),
('ID022', 'member22@gmail.com', '2028-01-22', '2023-01-22', 'Indonesia', 'KTP'),
('ID023', 'member23@gmail.com', '2028-01-23', '2023-01-23', 'Indonesia', 'Paspor'),
('ID024', 'member24@gmail.com', '2028-01-24', '2023-01-24', 'Indonesia', 'SIM'),
('ID025', 'member25@gmail.com', '2028-01-25', '2023-01-25', 'Indonesia', 'KTP'),
('ID026', 'member26@gmail.com', '2028-01-26', '2023-01-26', 'Indonesia', 'Paspor'),
('ID027', 'member27@gmail.com', '2028-01-27', '2023-01-27', 'Indonesia', 'SIM'),
('ID028', 'member28@gmail.com', '2028-01-28', '2023-01-28', 'Indonesia', 'KTP'),
('ID029', 'member29@gmail.com', '2028-01-29', '2023-01-29', 'Indonesia', 'Paspor'),
('ID030', 'member30@gmail.com', '2028-01-30', '2023-01-30', 'Indonesia', 'SIM');

INSERT INTO AWARD_MILES_PACKAGE (id, harga_paket, jumlah_award_miles) VALUES
('AMP-001', 150000.00, 1000), ('AMP-002', 300000.00, 2000), ('AMP-003', 450000.00, 3000), ('AMP-004', 600000.00, 4000),
('AMP-005', 750000.00, 5000), ('AMP-006', 900000.00, 6000), ('AMP-007', 1050000.00, 7000), ('AMP-008', 1200000.00, 8000),
('AMP-009', 1350000.00, 9000), ('AMP-010', 1500000.00, 10000), ('AMP-011', 1650000.00, 11000), ('AMP-012', 1800000.00, 12000),
('AMP-013', 1950000.00, 13000), ('AMP-014', 2100000.00, 14000), ('AMP-015', 2250000.00, 15000), ('AMP-016', 2400000.00, 16000),
('AMP-017', 2550000.00, 17000), ('AMP-018', 2700000.00, 18000), ('AMP-019', 2850000.00, 19000), ('AMP-020', 3000000.00, 20000);

INSERT INTO MEMBER_AWARD_MILES_PACKAGE (id_award_miles_package, email_member, timestamp) VALUES
('AMP-001', 'member1@gmail.com', '2024-03-01 10:00:00'), ('AMP-002', 'member2@gmail.com', '2024-03-02 10:00:00'),
('AMP-003', 'member3@gmail.com', '2024-03-03 10:00:00'), ('AMP-004', 'member4@gmail.com', '2024-03-04 10:00:00'),
('AMP-005', 'member5@gmail.com', '2024-03-05 10:00:00'), ('AMP-006', 'member6@gmail.com', '2024-03-06 10:00:00'),
('AMP-007', 'member7@gmail.com', '2024-03-07 10:00:00'), ('AMP-008', 'member8@gmail.com', '2024-03-08 10:00:00'),
('AMP-009', 'member9@gmail.com', '2024-03-09 10:00:00'), ('AMP-010', 'member10@gmail.com', '2024-03-10 10:00:00'),
('AMP-011', 'member11@gmail.com', '2024-03-11 10:00:00'), ('AMP-012', 'member12@gmail.com', '2024-03-12 10:00:00'),
('AMP-013', 'member13@gmail.com', '2024-03-13 10:00:00'), ('AMP-014', 'member14@gmail.com', '2024-03-14 10:00:00'),
('AMP-015', 'member15@gmail.com', '2024-03-15 10:00:00'), ('AMP-016', 'member16@gmail.com', '2024-03-16 10:00:00'),
('AMP-017', 'member17@gmail.com', '2024-03-17 10:00:00'), ('AMP-018', 'member18@gmail.com', '2024-03-18 10:00:00'),
('AMP-019', 'member19@gmail.com', '2024-03-19 10:00:00'), ('AMP-020', 'member20@gmail.com', '2024-03-20 10:00:00');

INSERT INTO BANDARA (iata_code, nama, kota, negara) VALUES
('CGK', 'Soekarno-Hatta', 'Tangerang', 'Indonesia'), ('DPS', 'Ngurah Rai', 'Denpasar', 'Indonesia'),
('SIN', 'Changi', 'Singapore', 'Singapore'), ('KNO', 'Kualanamu', 'Medan', 'Indonesia'),
('SUB', 'Juanda', 'Surabaya', 'Indonesia'), ('BDO', 'Husein Sastranegara', 'Bandung', 'Indonesia'),
('YIA', 'Yogyakarta International', 'Yogyakarta', 'Indonesia'), ('JOG', 'Adisutjipto', 'Yogyakarta', 'Indonesia'),
('SRG', 'Ahmad Yani', 'Semarang', 'Indonesia'), ('SOC', 'Adisumarmo', 'Surakarta', 'Indonesia'),
('LOP', 'Lombok International', 'Mataram', 'Indonesia'), ('UPG', 'Sultan Hasanuddin', 'Makassar', 'Indonesia'),
('MDC', 'Sam Ratulangi', 'Manado', 'Indonesia'), ('BPN', 'Sepinggan', 'Balikpapan', 'Indonesia'),
('PNK', 'Supadio', 'Pontianak', 'Indonesia');

INSERT INTO CLAIM_MISSING_MILES (email_member, email_staf, maskapai, bandara_asal, bandara_tujuan, tanggal_penerbangan, flight_number, nomor_tiket, kelas_kabin, pnr, status_penerimaan, timestamp) VALUES
('member1@gmail.com', NULL, 'GA', 'CGK', 'DPS', '2024-01-01', 'GA400', 'TK-001', 'Economy', 'PNR001', 'Menunggu', '2024-01-02 08:00:00'),
('member2@gmail.com', 'staf1@aeromiles.com', 'SQ', 'SIN', 'CGK', '2024-01-02', 'SQ950', 'TK-002', 'Business', 'PNR002', 'Disetujui', '2024-01-03 08:00:00'),
('member3@gmail.com', 'staf2@aeromiles.com', 'QZ', 'SUB', 'DPS', '2024-01-03', 'QZ100', 'TK-003', 'Economy', 'PNR003', 'Ditolak', '2024-01-04 08:00:00'),
('member4@gmail.com', NULL, 'JT', 'CGK', 'KNO', '2024-01-04', 'JT200', 'TK-004', 'Economy', 'PNR004', 'Menunggu', '2024-01-05 08:00:00'),
('member5@gmail.com', 'staf3@aeromiles.com', 'AK', 'KNO', 'SIN', '2024-01-05', 'AK300', 'TK-005', 'First', 'PNR005', 'Disetujui', '2024-01-06 08:00:00'),
('member6@gmail.com', NULL, 'GA', 'DPS', 'CGK', '2024-01-06', 'GA401', 'TK-006', 'Economy', 'PNR006', 'Menunggu', '2024-01-07 08:00:00'),
('member7@gmail.com', 'staf4@aeromiles.com', 'SQ', 'CGK', 'SIN', '2024-01-07', 'SQ951', 'TK-007', 'Business', 'PNR007', 'Ditolak', '2024-01-08 08:00:00'),
('member8@gmail.com', NULL, 'QZ', 'DPS', 'SUB', '2024-01-08', 'QZ101', 'TK-008', 'Economy', 'PNR008', 'Menunggu', '2024-01-09 08:00:00'),
('member9@gmail.com', 'staf5@aeromiles.com', 'JT', 'KNO', 'CGK', '2024-01-09', 'JT201', 'TK-009', 'Economy', 'PNR009', 'Disetujui', '2024-01-10 08:00:00'),
('member10@gmail.com', NULL, 'AK', 'SIN', 'KNO', '2024-01-10', 'AK301', 'TK-010', 'First', 'PNR010', 'Menunggu', '2024-01-11 08:00:00'),
('member11@gmail.com', 'staf1@aeromiles.com', 'GA', 'YIA', 'CGK', '2024-01-11', 'GA402', 'TK-011', 'Economy', 'PNR011', 'Disetujui', '2024-01-12 08:00:00'),
('member12@gmail.com', NULL, 'SQ', 'SIN', 'SUB', '2024-01-12', 'SQ952', 'TK-012', 'Business', 'PNR012', 'Menunggu', '2024-01-13 08:00:00'),
('member13@gmail.com', 'staf2@aeromiles.com', 'QZ', 'BDO', 'DPS', '2024-01-13', 'QZ102', 'TK-013', 'Economy', 'PNR013', 'Ditolak', '2024-01-14 08:00:00'),
('member14@gmail.com', NULL, 'JT', 'SRG', 'CGK', '2024-01-14', 'JT202', 'TK-014', 'Economy', 'PNR014', 'Menunggu', '2024-01-15 08:00:00'),
('member15@gmail.com', 'staf3@aeromiles.com', 'AK', 'PNK', 'CGK', '2024-01-15', 'AK302', 'TK-015', 'First', 'PNR015', 'Disetujui', '2024-01-16 08:00:00'),
('member16@gmail.com', NULL, 'GA', 'CGK', 'YIA', '2024-01-16', 'GA403', 'TK-016', 'Economy', 'PNR016', 'Menunggu', '2024-01-17 08:00:00'),
('member17@gmail.com', 'staf4@aeromiles.com', 'SQ', 'SUB', 'SIN', '2024-01-17', 'SQ953', 'TK-017', 'Business', 'PNR017', 'Ditolak', '2024-01-18 08:00:00'),
('member18@gmail.com', NULL, 'QZ', 'DPS', 'BDO', '2024-01-18', 'QZ103', 'TK-018', 'Economy', 'PNR018', 'Menunggu', '2024-01-19 08:00:00'),
('member19@gmail.com', 'staf5@aeromiles.com', 'JT', 'CGK', 'SRG', '2024-01-19', 'JT203', 'TK-019', 'Economy', 'PNR019', 'Disetujui', '2024-01-20 08:00:00'),
('member20@gmail.com', NULL, 'AK', 'CGK', 'PNK', '2024-01-20', 'AK303', 'TK-020', 'First', 'PNR020', 'Menunggu', '2024-01-21 08:00:00');

INSERT INTO TRANSFER (email_member_1, email_member_2, timestamp, jumlah, catatan) VALUES
('member1@gmail.com', 'member2@gmail.com', '2024-04-01 10:00:00', 1000, 'Kado ulang tahun'),
('member2@gmail.com', 'member3@gmail.com', '2024-04-02 10:00:00', 1500, 'Utang'),
('member3@gmail.com', 'member4@gmail.com', '2024-04-03 10:00:00', 2000, 'Patungan'),
('member4@gmail.com', 'member5@gmail.com', '2024-04-04 10:00:00', 2500, 'Hadiah'),
('member5@gmail.com', 'member6@gmail.com', '2024-04-05 10:00:00', 3000, 'Bonus'),
('member6@gmail.com', 'member7@gmail.com', '2024-04-06 10:00:00', 3500, ''),
('member7@gmail.com', 'member8@gmail.com', '2024-04-07 10:00:00', 4000, ''),
('member8@gmail.com', 'member9@gmail.com', '2024-04-08 10:00:00', 4500, ''),
('member9@gmail.com', 'member10@gmail.com', '2024-04-09 10:00:00', 5000, ''),
('member10@gmail.com', 'member11@gmail.com', '2024-04-10 10:00:00', 5500, ''),
('member11@gmail.com', 'member12@gmail.com', '2024-04-11 10:00:00', 6000, ''),
('member12@gmail.com', 'member13@gmail.com', '2024-04-12 10:00:00', 6500, ''),
('member13@gmail.com', 'member14@gmail.com', '2024-04-13 10:00:00', 7000, ''),
('member14@gmail.com', 'member15@gmail.com', '2024-04-14 10:00:00', 7500, ''),
('member15@gmail.com', 'member16@gmail.com', '2024-04-15 10:00:00', 8000, '');

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
