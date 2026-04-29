from django.db import models


class Airline(models.Model):
    """Map to MASKAPAI table"""
    kode_maskapai = models.CharField(max_length=10, primary_key=True)
    nama_maskapai = models.CharField(max_length=100)

    class Meta:
        db_table = 'maskapai'
        managed = False  # Don't create/modify table

    def __str__(self):
        return f"{self.kode_maskapai} - {self.nama_maskapai}"


class Flight(models.Model):
    """Map to BANDARA table"""
    iata_code = models.CharField(max_length=3, primary_key=True)
    nama = models.CharField(max_length=100)
    kota = models.CharField(max_length=100)
    negara = models.CharField(max_length=100)

    class Meta:
        db_table = 'bandara'
        managed = False

    def __str__(self):
        return f"{self.iata_code} - {self.nama}"