
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

-- ==========================================
-- BAGIAN ORANG 3: TRANSAKSI, KLAIM & BANDARA
-- ==========================================

-- 11. BANDARA (Minimal 15 Data)
INSERT INTO BANDARA (iata_code, nama, kota, negara) VALUES
('CGK', 'Soekarno-Hatta', 'Tangerang', 'Indonesia'), ('DPS', 'Ngurah Rai', 'Denpasar', 'Indonesia'),
('SIN', 'Changi', 'Singapore', 'Singapore'), ('KNO', 'Kualanamu', 'Medan', 'Indonesia'),
('SUB', 'Juanda', 'Surabaya', 'Indonesia'), ('BDO', 'Husein Sastranegara', 'Bandung', 'Indonesia'),
('YIA', 'Yogyakarta International', 'Yogyakarta', 'Indonesia'), ('JOG', 'Adisutjipto', 'Yogyakarta', 'Indonesia'),
('SRG', 'Ahmad Yani', 'Semarang', 'Indonesia'), ('SOC', 'Adisumarmo', 'Surakarta', 'Indonesia'),
('LOP', 'Lombok International', 'Mataram', 'Indonesia'), ('UPG', 'Sultan Hasanuddin', 'Makassar', 'Indonesia'),
('MDC', 'Sam Ratulangi', 'Manado', 'Indonesia'), ('BPN', 'Sepinggan', 'Balikpapan', 'Indonesia'),
('PNK', 'Supadio', 'Pontianak', 'Indonesia');

-- 12. CLAIM_MISSING_MILES (Minimal 20 Data)
-- Bergantung pada MEMBER, STAF, MASKAPAI, BANDARA
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

-- 13. TRANSFER (Minimal 15 Data)
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

-- 9. AWARD_MILES_PACKAGE (Minimal 20 Data, format AMP-[XXX])
INSERT INTO AWARD_MILES_PACKAGE (id, harga_paket, jumlah_award_miles) VALUES
('AMP-001', 150000.00, 1000), ('AMP-002', 300000.00, 2000), ('AMP-003', 450000.00, 3000), ('AMP-004', 600000.00, 4000),
('AMP-005', 750000.00, 5000), ('AMP-006', 900000.00, 6000), ('AMP-007', 1050000.00, 7000), ('AMP-008', 1200000.00, 8000),
('AMP-009', 1350000.00, 9000), ('AMP-010', 1500000.00, 10000), ('AMP-011', 1650000.00, 11000), ('AMP-012', 1800000.00, 12000),
('AMP-013', 1950000.00, 13000), ('AMP-014', 2100000.00, 14000), ('AMP-015', 2250000.00, 15000), ('AMP-016', 2400000.00, 16000),
('AMP-017', 2550000.00, 17000), ('AMP-018', 2700000.00, 18000), ('AMP-019', 2850000.00, 19000), ('AMP-020', 3000000.00, 20000);

-- 10. MEMBER_AWARD_MILES_PACKAGE (Minimal 20 Data)
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