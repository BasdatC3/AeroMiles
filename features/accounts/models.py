from django.db import models


class Pengguna(models.Model):
    SALUTATION_CHOICES = [
        ('Mr.', 'Mr.'),
        ('Mrs.', 'Mrs.'),
        ('Ms.', 'Ms.'),
        ('Dr.', 'Dr.'),
    ]

    email = models.CharField(max_length=100, primary_key=True)
    password = models.CharField(max_length=255)
    salutation = models.CharField(max_length=10, choices=SALUTATION_CHOICES)
    first_mid_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=5)
    mobile_number = models.CharField(max_length=20)
    tanggal_lahir = models.DateField()
    kewarganegaraan = models.CharField(max_length=50)

    class Meta:
        db_table = 'pengguna'
        managed = False

    def __str__(self):
        return self.email


class Tier(models.Model):
    id_tier = models.CharField(max_length=10, primary_key=True)
    nama = models.CharField(max_length=50)
    minimal_frekuensi_terbang = models.IntegerField()
    minimal_tier_miles = models.IntegerField()

    class Meta:
        db_table = 'tier'
        managed = False

    def __str__(self):
        return self.nama


class Penyedia(models.Model):
    id = models.AutoField(primary_key=True)
    nama = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'penyedia'
        managed = False

    def __str__(self):
        return self.nama


class Member(models.Model):
    email = models.CharField(max_length=100, primary_key=True)
    nomor_member = models.CharField(max_length=20, unique=True)
    tanggal_bergabung = models.DateField()
    id_tier = models.CharField(max_length=10)
    award_miles = models.IntegerField(default=0)
    total_miles = models.IntegerField(default=0)

    class Meta:
        db_table = 'member'
        managed = False

    def __str__(self):
        return f"{self.email} - {self.nomor_member}"


class Maskapai(models.Model):
    kode_maskapai = models.CharField(max_length=10, primary_key=True)
    nama_maskapai = models.CharField(max_length=100)
    id_penyedia = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'maskapai'
        managed = False

    def __str__(self):
        return f"{self.kode_maskapai} - {self.nama_maskapai}"


class Staf(models.Model):
    email = models.CharField(max_length=100, primary_key=True)
    id_staf = models.CharField(max_length=20, null=True, blank=True)
    kode_maskapai = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        db_table = 'staf'
        managed = False

    def __str__(self):
        return f"{self.email} - {self.id_staf}"


class Mitra(models.Model):
    email_mitra = models.CharField(max_length=100, primary_key=True)
    id_penyedia = models.IntegerField()
    nama_mitra = models.CharField(max_length=100)
    tanggal_kerja_sama = models.DateField()

    class Meta:
        db_table = 'mitra'
        managed = False

    def __str__(self):
        return self.nama_mitra


class Identitas(models.Model):
    JENIS_CHOICES = [
        ('Paspor', 'Paspor'),
        ('KTP', 'KTP'),
        ('SIM', 'SIM'),
    ]

    nomor = models.CharField(max_length=50, primary_key=True)
    email_member = models.CharField(max_length=100)
    tanggal_habis = models.DateField()
    tanggal_terbit = models.DateField()
    negara_penerbit = models.CharField(max_length=50)
    jenis = models.CharField(max_length=30, choices=JENIS_CHOICES)

    class Meta:
        db_table = 'identitas'
        managed = False

    def __str__(self):
        return f"{self.email_member} - {self.jenis} - {self.nomor}"


class Bandara(models.Model):
    iata_code = models.CharField(max_length=3, primary_key=True)
    nama = models.CharField(max_length=100)
    kota = models.CharField(max_length=100)
    negara = models.CharField(max_length=100)

    class Meta:
        db_table = 'bandara'
        managed = False

    def __str__(self):
        return f"{self.iata_code} - {self.nama}"


class ClaimMissingMiles(models.Model):
    STATUS_CHOICES = [
        ('Menunggu', 'Menunggu'),
        ('Disetujui', 'Disetujui'),
        ('Ditolak', 'Ditolak'),
    ]
    KELAS_CHOICES = [
        ('Economy', 'Economy'),
        ('Business', 'Business'),
        ('First', 'First'),
    ]

    id = models.AutoField(primary_key=True)
    email_member = models.CharField(max_length=100)
    email_staf = models.CharField(max_length=100, null=True, blank=True)
    maskapai = models.CharField(max_length=10)
    bandara_asal = models.CharField(max_length=3)
    bandara_tujuan = models.CharField(max_length=3)
    tanggal_penerbangan = models.DateField()
    flight_number = models.CharField(max_length=10)
    nomor_tiket = models.CharField(max_length=20)
    kelas_kabin = models.CharField(max_length=20, choices=KELAS_CHOICES)
    pnr = models.CharField(max_length=10)
    status_penerimaan = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Menunggu')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'claim_missing_miles'
        managed = False

    def __str__(self):
        return f"{self.email_member} - {self.flight_number}"


class TransferMiles(models.Model):
    email_member_1 = models.CharField(max_length=100)
    email_member_2 = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    jumlah = models.IntegerField()
    catatan = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'transfer'
        managed = False

    def __str__(self):
        return f"{self.email_member_1} -> {self.email_member_2}: {self.jumlah}"


class Hadiah(models.Model):
    kode_hadiah = models.CharField(max_length=20, primary_key=True)
    nama = models.CharField(max_length=100)
    miles = models.IntegerField()
    deskripsi = models.TextField(blank=True)
    valid_start_date = models.DateField()
    program_end = models.DateField()
    id_penyedia = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'hadiah'
        managed = False

    def __str__(self):
        return f"{self.kode_hadiah} - {self.nama}"


class Redeem(models.Model):
    email_member = models.CharField(max_length=100)
    kode_hadiah = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'redeem'
        managed = False

    def __str__(self):
        return f"{self.email_member} - {self.kode_hadiah}"


class AwardMilesPackage(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    harga_paket = models.DecimalField(max_digits=15, decimal_places=2)
    jumlah_award_miles = models.IntegerField()

    class Meta:
        db_table = 'award_miles_package'
        managed = False

    def __str__(self):
        return f"{self.id} - {self.jumlah_award_miles} miles"