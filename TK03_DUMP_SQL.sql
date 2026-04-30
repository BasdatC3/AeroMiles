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

INSERT INTO PENGGUNA (
    email,
    password,
    salutation,
    first_mid_name,
    last_name,
    country_code,
    mobile_number,
    tanggal_lahir,
    kewarganegaraan
)
-- looping untuk 50 pengguna
SELECT
    'member' || g || '@email.com',
    'password123',
    CASE
        WHEN g % 4 = 1 THEN 'Mr.'
        WHEN g % 4 = 2 THEN 'Mrs.'
        WHEN g % 4 = 3 THEN 'Ms.'
        ELSE 'Dr.'
    END,
    'Member ' || g,
    'Dummy',
    '+62',
    '8120000' || lpad(g::text, 4, '0'),
    DATE '1990-01-01' + (g * INTERVAL '30 days'),
    'Indonesia'
FROM generate_series(1, 50) AS g;

-- insert data staf
INSERT INTO PENGGUNA (
    email,
    password,
    salutation,
    first_mid_name,
    last_name,
    country_code,
    mobile_number,
    tanggal_lahir,
    kewarganegaraan
)
-- looping juga dilakukan di sini untuk 10 pengguna lainnya
SELECT
    'staf' || g || '@email.com',
    'password123',
    CASE
        WHEN g % 4 = 1 THEN 'Mr.'
        WHEN g % 4 = 2 THEN 'Mrs.'
        WHEN g % 4 = 3 THEN 'Ms.'
        ELSE 'Dr.'
    END,
    'Staf ' || g,
    'Maskapai',
    '+62',
    '8130000' || lpad(g::text, 4, '0'),
    DATE '1985-01-01' + (g * INTERVAL '60 days'),
    'Indonesia'
FROM generate_series(1, 10) AS g;

INSERT INTO TIER (
    id_tier,
    nama,
    minimal_frekuensi_terbang,
    minimal_tier_miles
)
VALUES
('BRZ', 'Bronze', 0, 0),
('SLV', 'Silver', 5, 10000),
('GLD', 'Gold', 15, 30000),
('PLT', 'Platinum', 30, 60000);

INSERT INTO PENYEDIA (id)
SELECT g
FROM generate_series(1, 10) AS g;

INSERT INTO MEMBER (
    email,
    tanggal_bergabung,
    id_tier,
    award_miles,
    total_miles
)
-- looping untuk menentukan tier
SELECT
    'member' || g || '@email.com',
    DATE '2023-01-01' + (g * INTERVAL '3 days'),
    CASE
        WHEN g <= 15 THEN 'BRZ'
        WHEN g <= 30 THEN 'SLV'
        WHEN g <= 45 THEN 'GLD'
        ELSE 'PLT'
    END,
    g * 1000,
    g * 1500
FROM generate_series(1, 50) AS g;

-- penyedia adalah sebuah maskapai ATAU mitra dan TIDAK KEDUANYA
INSERT INTO MASKAPAI (
    kode_maskapai,
    nama_maskapai,
    id_penyedia
)
VALUES
('GA', 'Garuda Indonesia', 1),
('JT', 'Lion Air', 2),
('QZ', 'AirAsia Indonesia', 3),
('ID', 'Batik Air', 4),
('SJ', 'Sriwijaya Air', 5);

INSERT INTO MITRA (
    email_mitra,
    id_penyedia,
    nama_mitra,
    tanggal_kerja_sama
)
VALUES
('hotel@mitra.com', 6, 'Aero Hotel Group', DATE '2022-01-10'),
('rental@mitra.com', 7, 'Aero Rental Car', DATE '2022-03-15'),
('travel@mitra.com', 8, 'Aero Travel Partner', DATE '2022-06-20'),
('shop@mitra.com', 9, 'Aero Lifestyle Shop', DATE '2023-02-05'),
('bank@mitra.com', 10, 'Aero Bank Partner', DATE '2023-05-12'); 

INSERT INTO STAF (
    email,
    kode_maskapai
)
-- looping untuk menentukan maskapai untuk staf
SELECT
    'staf' || g || '@email.com',
    CASE
        WHEN g % 5 = 1 THEN 'GA'
        WHEN g % 5 = 2 THEN 'JT'
        WHEN g % 5 = 3 THEN 'QZ'
        WHEN g % 5 = 4 THEN 'ID'
        ELSE 'SJ'
    END
FROM generate_series(1, 10) AS g;

INSERT INTO HADIAH (
    nama,
    miles,
    deskripsi,
    valid_start_date,
    program_end,
    id_penyedia
)
VALUES
('Upgrade Bagasi Garuda', 8000, 'Tambahan kuota bagasi untuk penerbangan Garuda.', DATE '2024-01-01', DATE '2026-12-31', 1),
('Voucher Lion Air', 6500, 'Voucher penerbangan Lion Air.', DATE '2024-01-01', DATE '2026-12-31', 2),
('AirAsia Seat Selection', 2500, 'Gratis pilihan kursi AirAsia.', DATE '2024-01-01', DATE '2026-12-31', 3),
('Batik Air Lounge', 9000, 'Akses lounge untuk penerbangan Batik Air.', DATE '2024-01-01', DATE '2026-12-31', 4),
('Sriwijaya Priority Check-in', 4000, 'Layanan priority check-in Sriwijaya Air.', DATE '2024-01-01', DATE '2026-12-31', 5),
('Voucher Hotel 1 Malam', 5000, 'Voucher menginap satu malam di hotel partner.', DATE '2024-01-01', DATE '2026-12-31', 6),
('Diskon Rental Mobil', 3000, 'Potongan harga rental mobil partner.', DATE '2024-01-01', DATE '2026-12-31', 7),
('Travel Voucher', 7000, 'Voucher perjalanan dari mitra travel.', DATE '2024-02-01', DATE '2026-12-31', 8),
('Lifestyle Gift Card', 4500, 'Gift card untuk toko lifestyle partner.', DATE '2024-02-01', DATE '2026-12-31', 9),
('Bank Reward Voucher', 6000, 'Voucher reward dari bank partner.', DATE '2024-03-01', DATE '2026-12-31', 10);

INSERT INTO REDEEM (
    email_member,
    kode_hadiah,
    timestamp
)
SELECT
    'member' || g || '@email.com',
    'RWD-' || lpad((((g - 1) % 10) + 1)::text, 3, '0'),
    TIMESTAMP '2024-05-01 11:00:00' + (g * INTERVAL '1 day')
FROM generate_series(1, 20) AS g;

SELECT setval(pg_get_serial_sequence('penyedia', 'id'), 10, true);
SELECT setval('seq_member_nomor', 50, true);
SELECT setval('seq_staf_id', 10, true);
SELECT setval('seq_hadiah_kode', 10, true);
