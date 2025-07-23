# core/models.py
from django.db import models

class DocumentoFiscal(models.Model):
    # Campos conforme o XSD original de Documento Fiscal
    codigo_ajuste = models.CharField(max_length=20, verbose_name="Código do Ajuste/Empenho")
    medicao_numero = models.IntegerField(verbose_name="Número da Medição")
    nota_empenho_numero = models.CharField(max_length=35, verbose_name="Número da Nota de Empenho")
    nota_empenho_data_emissao = models.DateField(verbose_name="Data de Emissão da Nota de Empenho")
    documento_fiscal_numero = models.CharField(max_length=15, verbose_name="Número do Documento Fiscal (NF)")
    documento_fiscal_uf = models.CharField(max_length=4, verbose_name="UF do Documento Fiscal (Ex: SP)")
    documento_fiscal_valor = models.DecimalField(max_digits=17, decimal_places=2, verbose_name="Valor do Documento Fiscal")
    documento_fiscal_data_emissao = models.DateField(verbose_name="Data de Emissão do Documento Fiscal")

    def __str__(self):
        return f"NF {self.documento_fiscal_numero} - Ajuste {self.codigo_ajuste}"

class Pagamento(models.Model):
    # Campos conforme o XSD original de Pagamento
    codigo_ajuste = models.CharField(max_length=20, verbose_name="Código do Ajuste/Empenho")
    medicao_numero = models.IntegerField(verbose_name="Número da Medição")
    nota_empenho_numero = models.CharField(max_length=35, verbose_name="Número da Nota de Empenho")
    nota_empenho_data_emissao = models.DateField(verbose_name="Data de Emissão da Nota de Empenho")
    documento_fiscal_numero = models.CharField(max_length=15, verbose_name="Número do Documento Fiscal (NF)")
    documento_fiscal_data_emissao = models.DateField(verbose_name="Data de Emissão do Documento Fiscal")
    documento_fiscal_uf = models.CharField(max_length=4, verbose_name="UF do Documento Fiscal (Ex: SP)")
    nota_fiscal_valor_pago = models.DecimalField(max_digits=17, decimal_places=2, verbose_name="Valor Pago da Nota Fiscal")
    nota_fiscal_pagto_dt = models.DateField(verbose_name="Data Efetiva do Pagamento")
    recolhido_encargos_previdenciario = models.CharField(
        max_length=1,
        blank=True,
        null=True,
        choices=[('S', 'Sim'), ('N', 'Não')],
        verbose_name="Recolhido Encargos Previdenciários?"
    )

    def __str__(self):
        return f"Pagamento NF {self.documento_fiscal_numero} - Ajuste {self.codigo_ajuste}"