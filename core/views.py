# core/views.py
import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse

# ATUALIZAR ESTES IMPORTS:
from .forms import DocumentoFiscalForm, PagamentoForm # Importa os formulários originais
from .models import DocumentoFiscal, Pagamento # Importa os modelos originais

# --- Função Auxiliar para o Descritor (Cabeçalho do XML) ---
def gerar_descritor_xml(tipo_documento):
    ano_exercicio = datetime.date.today().year
    municipio = '6300'  # Código de Barueri
    entidade = '1'    # Código da entidade principal (geralmente 1 para a prefeitura)
    data_criacao_xml = datetime.date.today().strftime('%Y-%m-%d')

    return f"""
    <Descritor>
        <gen:AnoExercicio>{ano_exercicio}</gen:AnoExercicio>
        <gen:TipoDocumento>{tipo_documento}</gen:TipoDocumento>
        <gen:Entidade>{entidade}</gen:Entidade>
        <gen:Municipio>{municipio}</gen:Municipio>
        <gen:DataCriacaoXML>{data_criacao_xml}</gen:DataCriacaoXML>
    </Descritor>
    """

# --- View para a Página Inicial ---
def home(request):
    return render(request, 'core/home.html')

# --- View para Gerar XML de Documento Fiscal (VERSÃO SIMPLES, UM EMPENHO POR LANCAMENTO) ---
def gerar_xml_documento_fiscal(request):
    if request.method == 'POST':
        form = DocumentoFiscalForm(request.POST)
        if form.is_valid():
            df = form.save() # Salva os dados no banco de dados

            xml_content = f"""<?xml version="1.0" encoding="ISO-8859-1"?>
<DocumentoFiscal xmlns="http://www.tce.sp.gov.br/audesp/xml/documentofiscal"
                 xmlns:gen="http://www.tce.sp.gov.br/audesp/xml/generico"
                 xmlns:tag="http://www.tce.sp.gov.br/audesp/xml/tagcomum"
                 xsi:schemaLocation="http://www.tce.sp.gov.br/audesp/xml/documentofiscal ../documentofiscal/AUDESP4_DOCUMENTOFISCAL_2025_A.XSD"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  {gerar_descritor_xml('DOCUMENTOFISCAL')}
  <ArrayDocumentoFiscal>
    <CodigoAjuste>{df.codigo_ajuste}</CodigoAjuste>
    <DocFiscal>
      <MedicaoNumero>{df.medicao_numero}</MedicaoNumero>
      <NotaEmpenhoNumero>{df.nota_empenho_numero}</NotaEmpenhoNumero>
      <NotaEmpenhoDataEmissao>{df.nota_empenho_data_emissao.strftime('%Y-%m-%d')}</NotaEmpenhoDataEmissao>
      <DocumentoFiscalNumero>{df.documento_fiscal_numero}</DocumentoFiscalNumero>
      <DocumentoFiscalUF>{df.documento_fiscal_uf}</DocumentoFiscalUF>
      <DocumentoFiscalValor>{df.documento_fiscal_valor:.2f}</DocumentoFiscalValor>
      <DocumentoFiscalDataEmissao>{df.documento_fiscal_data_emissao.strftime('%Y-%m-%d')}</DocumentoFiscalDataEmissao>
    </DocFiscal>
  </ArrayDocumentoFiscal>
</DocumentoFiscal>
            """
            response = HttpResponse(xml_content, content_type='application/xml')
            response['Content-Disposition'] = f'attachment; filename="documento_fiscal_{df.pk}.xml"'
            return response
    else: # Requisição GET
        form = DocumentoFiscalForm()

    return render(request, 'core/gerar_df.html', {'form': form}) # Não precisa de 'formset' aqui

# --- View para Gerar XML de Pagamento (continua a mesma) ---
def gerar_xml_pagamento(request):
    if request.method == 'POST':
        form = PagamentoForm(request.POST) # Popula o formulário com dados do POST
        if form.is_valid():
            pg = form.save() # Salva os dados no banco de dados

            # Monta o conteúdo do XML de Pagamento
            xml_content = f"""<?xml version="1.0" encoding="ISO-8859-1"?>
<Pagamento xmlns="http://www.tce.sp.gov.br/audesp/xml/pagamento"
           xmlns:gen="http://www.tce.sp.gov.br/audesp/xml/generico"
           xmlns:tag="http://www.tce.sp.gov.br/audesp/xml/tagcomum"
           xsi:schemaLocation="http://www.tce.sp.gov.br/audesp/xml/pagamento ../pagamento/AUDESP4_PAGAMENTO_2025_A.XSD"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  {gerar_descritor_xml('PAGAMENTO')}
  <ArrayPagamento>
    <CodigoAjuste>{pg.codigo_ajuste}</CodigoAjuste>
    <Pagto>
      <MedicaoNumero>{pg.medicao_numero}</MedicaoNumero>
      <NotaEmpenhoNumero>{pg.nota_empenho_numero}</NotaEmpenhoNumero>
      <NotaEmpenhoDataEmissao>{pg.nota_empenho_data_emissao.strftime('%Y-%m-%d')}</NotaEmpenhoDataEmissao>
      <DocumentoFiscalNumero>{pg.documento_fiscal_numero}</DocumentoFiscalNumero>
      <DocumentoFiscalDataEmissao>{pg.documento_fiscal_data_emissao.strftime('%Y-%m-%d')}</DocumentoFiscalDataEmissao>
      <DocumentoFiscalUF>{pg.documento_fiscal_uf}</DocumentoFiscalUF>
      <NotaFiscalValorPago>{pg.nota_fiscal_valor_pago:.2f}</NotaFiscalValorPago>
      <NotaFiscalPagtoDt>{pg.nota_fiscal_pagto_dt.strftime('%Y-%m-%d')}</NotaFiscalPagtoDt>
      <RecolhidoEncargosPrevidenciario>{pg.recolhido_encargos_previdenciario if pg.recolhido_encargos_previdenciario else 'N'}</RecolhidoEncargosPrevidenciario>
    </Pagto>
  </ArrayPagamento>
</Pagamento>
            """
            response = HttpResponse(xml_content, content_type='application/xml')
            response['Content-Disposition'] = f'attachment; filename="pagamento_{pg.pk}.xml"'
            return response
    else: # Requisição GET
        form = PagamentoForm()

    return render(request, 'core/gerar_pg.html', {'form': form})