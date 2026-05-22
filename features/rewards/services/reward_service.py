from datetime import date

from main.db import execute_query, execute_write


def list_all():
    return execute_query(
        "SELECT * FROM hadiah ORDER BY kode_hadiah",
        fetch_all=True,
    ) or []


def get(kode):
    return execute_query(
        "SELECT * FROM hadiah WHERE kode_hadiah = %s",
        (kode,), fetch_one=True,
    )


def list_maskapai_penyedia():
    return execute_query(
        "SELECT id_penyedia, nama_maskapai FROM maskapai", fetch_all=True,
    ) or []


def list_mitra_penyedia():
    return execute_query(
        "SELECT id_penyedia, nama_mitra FROM mitra", fetch_all=True,
    ) or []


def annotate_with_provider(hadiah_list):
    """Tambah field tipe_penyedia, nama_penyedia, is_expired ke setiap hadiah."""
    maskapai_map = {m['id_penyedia']: m['nama_maskapai']
                    for m in list_maskapai_penyedia() if m['id_penyedia']}
    mitra_map = {m['id_penyedia']: m['nama_mitra']
                 for m in list_mitra_penyedia()}
    today = date.today()

    for h in hadiah_list:
        pid = h['id_penyedia']
        if pid in maskapai_map:
            h['tipe_penyedia'] = 'airline'
            h['nama_penyedia'] = maskapai_map[pid]
        else:
            h['tipe_penyedia'] = 'partner'
            h['nama_penyedia'] = mitra_map.get(pid, f'Penyedia {pid}')
        h['is_expired'] = h['program_end'] < today
    return hadiah_list


def list_all_penyedia():
    items = []
    for m in list_maskapai_penyedia():
        if m['id_penyedia']:
            items.append({'id': m['id_penyedia'], 'nama': m['nama_maskapai'], 'tipe': 'airline'})
    for m in list_mitra_penyedia():
        items.append({'id': m['id_penyedia'], 'nama': m['nama_mitra'], 'tipe': 'partner'})
    return items


def next_kode():
    last = execute_query(
        "SELECT kode_hadiah FROM hadiah ORDER BY kode_hadiah DESC LIMIT 1",
        fetch_one=True,
    )
    if last:
        try:
            num = int(last['kode_hadiah'].split('-')[1]) + 1
        except (IndexError, ValueError):
            num = 1
    else:
        num = 1
    return f'RWD-{num:03d}'


def create(nama, miles, deskripsi, valid_start, program_end, id_penyedia):
    execute_write(
        """INSERT INTO hadiah (nama, miles, deskripsi, valid_start_date,
           program_end, id_penyedia)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (nama, miles, deskripsi, valid_start, program_end, id_penyedia),
    )


def update(kode, nama, miles, deskripsi, valid_start, program_end, id_penyedia):
    execute_write(
        """UPDATE hadiah SET nama = %s, miles = %s, deskripsi = %s,
           valid_start_date = %s, program_end = %s, id_penyedia = %s
           WHERE kode_hadiah = %s""",
        (nama, miles, deskripsi, valid_start, program_end, id_penyedia, kode),
    )


def delete(kode):
    execute_write("DELETE FROM hadiah WHERE kode_hadiah = %s", (kode,))


def is_expired(hadiah):
    return hadiah['program_end'] < date.today()
