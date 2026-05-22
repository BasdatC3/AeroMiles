from main.db import execute_query, execute_write


def list_all():
    return execute_query(
        "SELECT * FROM award_miles_package ORDER BY harga_paket",
        fetch_all=True,
    ) or []


def get(package_id):
    return execute_query(
        "SELECT * FROM award_miles_package WHERE id = %s",
        (package_id,), fetch_one=True,
    )


def get_member(email):
    return execute_query(
        "SELECT * FROM member WHERE email = %s",
        (email,), fetch_one=True,
    )


def list_purchases(email):
    return execute_query(
        """SELECT m.id_award_miles_package, m.timestamp,
                  a.harga_paket, a.jumlah_award_miles
           FROM member_award_miles_package m
           LEFT JOIN award_miles_package a ON m.id_award_miles_package = a.id
           WHERE m.email_member = %s
           ORDER BY m.timestamp DESC""",
        (email,), fetch_all=True,
    ) or []


def execute_purchase(email, package_id, jumlah_miles):
    execute_write(
        """UPDATE member
           SET award_miles = award_miles + %s,
               total_miles = total_miles + %s
           WHERE email = %s""",
        (jumlah_miles, jumlah_miles, email),
    )
    execute_write(
        """INSERT INTO member_award_miles_package
           (id_award_miles_package, email_member, timestamp)
           VALUES (%s, %s, CURRENT_TIMESTAMP)""",
        (package_id, email),
    )
