from main.db import execute_query, execute_write


def get_pengguna(email):
    return execute_query(
        "SELECT * FROM pengguna WHERE email = %s",
        (email,),
        fetch_one=True,
    )


def get_member(email):
    return execute_query(
        "SELECT * FROM member WHERE email = %s",
        (email,),
        fetch_one=True,
    )


def get_member_with_tier(email):
    return execute_query(
        """SELECT m.*, t.nama AS tier_nama
           FROM member m LEFT JOIN tier t ON m.id_tier = t.id_tier
           WHERE m.email = %s""",
        (email,),
        fetch_one=True,
    )


def get_staf(email):
    return execute_query(
        "SELECT * FROM staf WHERE email = %s",
        (email,),
        fetch_one=True,
    )


def get_staf_with_maskapai(email):
    return execute_query(
        """SELECT s.*, m.nama_maskapai
           FROM staf s LEFT JOIN maskapai m ON s.kode_maskapai = m.kode_maskapai
           WHERE s.email = %s""",
        (email,),
        fetch_one=True,
    )


def list_tiers():
    return execute_query(
        "SELECT * FROM tier ORDER BY minimal_tier_miles",
        fetch_all=True,
    ) or []


def list_airlines():
    return execute_query(
        "SELECT kode_maskapai, nama_maskapai FROM maskapai ORDER BY nama_maskapai",
        fetch_all=True,
    ) or []


def update_pengguna(email, data):
    execute_write(
        """UPDATE pengguna SET salutation = %s, first_mid_name = %s, last_name = %s,
           country_code = %s, mobile_number = %s, tanggal_lahir = %s, kewarganegaraan = %s
           WHERE email = %s""",
        (
            data['salutation'], data['first_mid_name'], data['last_name'],
            data['country_code'], data['mobile_number'],
            data.get('tanggal_lahir') or None, data['kewarganegaraan'],
            email,
        ),
    )


def update_staf_maskapai(email, kode_maskapai):
    execute_write(
        "UPDATE staf SET kode_maskapai = %s WHERE email = %s",
        (kode_maskapai, email),
    )
