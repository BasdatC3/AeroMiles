from main.db import execute_query, execute_write


def list_all():
    return execute_query(
        """SELECT m.email, m.nomor_member, m.tanggal_bergabung, m.id_tier,
                  m.award_miles, m.total_miles,
                  p.salutation, p.first_mid_name, p.last_name
           FROM member m JOIN pengguna p ON m.email = p.email
           ORDER BY m.nomor_member""",
        fetch_all=True,
    ) or []


def get(email):
    return execute_query(
        "SELECT * FROM member WHERE email = %s",
        (email,),
        fetch_one=True,
    )


def update_tier(email, id_tier):
    execute_write(
        "UPDATE member SET id_tier = %s WHERE email = %s",
        (id_tier, email),
    )


def tier_exists(id_tier):
    return execute_query(
        "SELECT id_tier FROM tier WHERE id_tier = %s",
        (id_tier,),
        fetch_one=True,
    ) is not None


def delete_cascade(email):
    """Hapus member beserta seluruh data terkait."""
    execute_write("DELETE FROM identitas WHERE email_member = %s", (email,))
    execute_write("DELETE FROM claim_missing_miles WHERE email_member = %s", (email,))
    execute_write("DELETE FROM transfer WHERE email_member_1 = %s", (email,))
    execute_write("DELETE FROM transfer WHERE email_member_2 = %s", (email,))
    execute_write("DELETE FROM redeem WHERE email_member = %s", (email,))
    execute_write("DELETE FROM member_award_miles_package WHERE email_member = %s", (email,))
    execute_write("DELETE FROM member WHERE email = %s", (email,))
    execute_write("DELETE FROM pengguna WHERE email = %s", (email,))
