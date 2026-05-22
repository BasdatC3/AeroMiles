from main.db import execute_query, execute_write


def list_all():
    return execute_query(
        """SELECT email_mitra, id_penyedia, nama_mitra, tanggal_kerja_sama
           FROM mitra ORDER BY nama_mitra""",
        fetch_all=True,
    ) or []


def get(email_mitra):
    return execute_query(
        "SELECT * FROM mitra WHERE email_mitra = %s",
        (email_mitra,),
        fetch_one=True,
    )


def email_exists(email_mitra):
    return get(email_mitra) is not None


def next_penyedia_id():
    row = execute_query(
        "SELECT COALESCE(MAX(id), 0) + 1 AS new_id FROM penyedia",
        fetch_one=True,
    )
    return row['new_id']


def create_penyedia(new_id):
    execute_write("INSERT INTO penyedia (id) VALUES (%s)", (new_id,))


def create(email_mitra, id_penyedia, nama_mitra, tanggal_kerja_sama):
    execute_write(
        """INSERT INTO mitra (email_mitra, id_penyedia, nama_mitra, tanggal_kerja_sama)
           VALUES (%s, %s, %s, %s)""",
        (email_mitra, id_penyedia, nama_mitra, tanggal_kerja_sama),
    )


def update(email_mitra, nama_mitra, tanggal_kerja_sama):
    execute_write(
        """UPDATE mitra SET nama_mitra = %s, tanggal_kerja_sama = %s
           WHERE email_mitra = %s""",
        (nama_mitra, tanggal_kerja_sama, email_mitra),
    )


def delete(email_mitra, id_penyedia):
    execute_write("DELETE FROM mitra WHERE email_mitra = %s", (email_mitra,))
    execute_write("DELETE FROM penyedia WHERE id = %s", (id_penyedia,))
