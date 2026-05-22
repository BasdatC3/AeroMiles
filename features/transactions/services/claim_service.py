from main.db import execute_query, execute_write


CLAIM_KELAS_MILES = {
    'Economy': 1000,
    'Business': 2000,
    'First': 3000,
}


def list_for_member(email, status_filter=''):
    query = "SELECT * FROM claim_missing_miles WHERE email_member = %s"
    params = [email]
    if status_filter:
        query += " AND status_penerimaan = %s"
        params.append(status_filter)
    query += " ORDER BY timestamp DESC"
    return execute_query(query, tuple(params), fetch_all=True) or []


def list_for_staff(status_filter='', maskapai_filter=''):
    query = """SELECT c.*, p.first_mid_name, p.last_name
               FROM claim_missing_miles c
               LEFT JOIN pengguna p ON c.email_member = p.email
               WHERE 1=1"""
    params = []
    if status_filter:
        query += " AND c.status_penerimaan = %s"
        params.append(status_filter)
    if maskapai_filter:
        query += " AND c.maskapai = %s"
        params.append(maskapai_filter)
    query += " ORDER BY c.timestamp DESC"
    return execute_query(query, tuple(params) if params else None, fetch_all=True) or []


def get(claim_id):
    return execute_query(
        "SELECT * FROM claim_missing_miles WHERE id = %s",
        (claim_id,), fetch_one=True,
    )


def is_duplicate(email, flight_number, tanggal, nomor_tiket):
    return execute_query(
        """SELECT id FROM claim_missing_miles
           WHERE email_member = %s AND flight_number = %s
             AND tanggal_penerbangan = %s AND nomor_tiket = %s""",
        (email, flight_number, tanggal, nomor_tiket), fetch_one=True,
    ) is not None


def create(email, data):
    execute_write(
        """INSERT INTO claim_missing_miles
           (email_member, maskapai, bandara_asal, bandara_tujuan, tanggal_penerbangan,
            flight_number, nomor_tiket, kelas_kabin, pnr, status_penerimaan, timestamp)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Menunggu', CURRENT_TIMESTAMP)""",
        (email, data['maskapai'], data['bandara_asal'], data['bandara_tujuan'],
         data['tanggal_penerbangan'], data['flight_number'], data['nomor_tiket'],
         data['kelas_kabin'], data['pnr']),
    )


def update(claim_id, data):
    execute_write(
        """UPDATE claim_missing_miles
           SET maskapai = %s, bandara_asal = %s, bandara_tujuan = %s,
               tanggal_penerbangan = %s, flight_number = %s, nomor_tiket = %s,
               kelas_kabin = %s, pnr = %s
           WHERE id = %s""",
        (data['maskapai'], data['bandara_asal'], data['bandara_tujuan'],
         data['tanggal_penerbangan'], data['flight_number'], data['nomor_tiket'],
         data['kelas_kabin'], data['pnr'], claim_id),
    )


def delete(claim_id):
    execute_write("DELETE FROM claim_missing_miles WHERE id = %s", (claim_id,))


def approve(claim_id, staff_email, member_email, kelas_kabin):
    miles = CLAIM_KELAS_MILES.get(kelas_kabin, 1000)
    execute_write(
        """UPDATE claim_missing_miles
           SET status_penerimaan = 'Disetujui', email_staf = %s
           WHERE id = %s""",
        (staff_email, claim_id),
    )
    execute_write(
        """UPDATE member
           SET award_miles = award_miles + %s,
               total_miles = total_miles + %s
           WHERE email = %s""",
        (miles, miles, member_email),
    )
    return miles


def reject(claim_id, staff_email):
    execute_write(
        """UPDATE claim_missing_miles
           SET status_penerimaan = 'Ditolak', email_staf = %s
           WHERE id = %s""",
        (staff_email, claim_id),
    )


def list_maskapai():
    return execute_query(
        "SELECT kode_maskapai, nama_maskapai FROM maskapai ORDER BY nama_maskapai",
        fetch_all=True,
    ) or []


def list_bandara():
    return execute_query(
        "SELECT iata_code, nama, kota FROM bandara ORDER BY iata_code",
        fetch_all=True,
    ) or []
