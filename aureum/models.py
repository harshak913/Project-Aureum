# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Balance(models.Model):
    accession_number = models.ForeignKey('Scrape', on_delete=models.CASCADE, db_column='accession_number', related_name='accession_balance')
    member = models.CharField(max_length=500, blank=True, null=True)
    header = models.CharField(max_length=500, blank=True, null=True)
    eng_name = models.CharField(max_length=5000, blank=True, null=True)
    acc_name = models.CharField(max_length=5000, blank=True, null=True)
    value = models.CharField(max_length=500, blank=True, null=True)
    unit = models.CharField(max_length=500, blank=True, null=True)
    year = models.DateField(blank=True, null=True)
    statement = models.CharField(max_length=500, blank=True, null=True)
    report_period = models.DateField(blank=True, null=True)
    filing_type = models.CharField(max_length=45, blank=True, null=True)
    months_ended = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'balance'


class CashFlow(models.Model):
    accession_number = models.ForeignKey('Scrape', on_delete=models.CASCADE, db_column='accession_number', related_name='accession_cash')
    member = models.CharField(max_length=500, blank=True, null=True)
    header = models.CharField(max_length=500, blank=True, null=True)
    eng_name = models.CharField(max_length=5000, blank=True, null=True)
    acc_name = models.CharField(max_length=5000, blank=True, null=True)
    value = models.CharField(max_length=500, blank=True, null=True)
    unit = models.CharField(max_length=500, blank=True, null=True)
    year = models.DateField(blank=True, null=True)
    statement = models.CharField(max_length=500, blank=True, null=True)
    report_period = models.DateField(blank=True, null=True)
    filing_type = models.CharField(max_length=45, blank=True, null=True)
    months_ended = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cash_flow'


class Company(models.Model):
    cik = models.IntegerField(primary_key=True)
    ticker = models.CharField(max_length=10, blank=True, null=True)
    name = models.CharField(max_length=445, blank=True, null=True)
    classification = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'company'


class Income(models.Model):
    accession_number = models.ForeignKey('Scrape', on_delete=models.CASCADE, db_column='accession_number', related_name='accession_income')
    member = models.CharField(max_length=500, blank=True, null=True)
    header = models.CharField(max_length=500, blank=True, null=True)
    eng_name = models.CharField(max_length=5000, blank=True, null=True)
    acc_name = models.CharField(max_length=5000, blank=True, null=True)
    value = models.CharField(max_length=500, blank=True, null=True)
    unit = models.CharField(max_length=500, blank=True, null=True)
    year = models.DateField(blank=True, null=True)
    statement = models.CharField(max_length=500, blank=True, null=True)
    report_period = models.DateField(blank=True, null=True)
    filing_type = models.CharField(max_length=45, blank=True, null=True)
    months_ended = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'income'


class MasterIdx(models.Model):
    master_file = models.CharField(max_length=25, blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'master_idx'


class NonStatement(models.Model):
    accession_number = models.ForeignKey('Scrape', on_delete=models.CASCADE, db_column='accession_number', related_name='accession_non')
    member = models.CharField(max_length=500, blank=True, null=True)
    header = models.CharField(max_length=500, blank=True, null=True)
    eng_name = models.CharField(max_length=5000, blank=True, null=True)
    acc_name = models.CharField(max_length=5000, blank=True, null=True)
    value = models.CharField(max_length=500, blank=True, null=True)
    unit = models.CharField(max_length=500, blank=True, null=True)
    year = models.DateField(blank=True, null=True)
    statement = models.CharField(max_length=500, blank=True, null=True)
    report_period = models.DateField(blank=True, null=True)
    filing_type = models.CharField(max_length=45, blank=True, null=True)
    months_ended = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'non_statement'


class Scrape(models.Model):
    cik = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='cik_id')
    filing_type = models.CharField(max_length=45, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    file_name = models.CharField(max_length=445, blank=True, null=True)
    accession_number = models.CharField(primary_key=True, max_length=445)
    inter_or_htm = models.CharField(max_length=5, blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'scrape'