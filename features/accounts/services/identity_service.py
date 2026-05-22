from main.db import execute_query, execute_write


def list_for_member(email):
    return execute_query(
        "SELECT * FROM identitas WHERE email_member = %s ORDER BY tanggal_terbit DESC",
        (email,),
        fetch_all=True,
    ) or []


def get(nomor):
    return execute_query(
        "SELECT * FROM identitas WHERE nomor = %s",
        (nomor,),
        fetch_one=True,
    )


def exists(nomor):
    return get(nomor) is not None


def create(nomor, email_member, jenis, negara_penerbit, tanggal_terbit, tanggal_habis):
    execute_write(
        """INSERT INTO identitas (nomor, email_member, jenis, negara_penerbit,
           tanggal_terbit, tanggal_habis)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (nomor, email_member, jenis, negara_penerbit, tanggal_terbit, tanggal_habis),
    )


def update(nomor, jenis, negara_penerbit, tanggal_terbit, tanggal_habis):
    execute_write(
        """UPDATE identitas
           SET jenis = %s, negara_penerbit = %s, tanggal_terbit = %s, tanggal_habis = %s
           WHERE nomor = %s""",
        (jenis, negara_penerbit, tanggal_terbit, tanggal_habis, nomor),
    )


def delete(nomor):
    execute_write("DELETE FROM identitas WHERE nomor = %s", (nomor,))
