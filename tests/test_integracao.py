"""Testa efeitos reais no MCP e persistência; somente respostas LLM são fixas."""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
TEMP = tempfile.TemporaryDirectory(prefix='rh-testes-')
os.environ['RH_SAIDAS'] = TEMP.name
from apoio import preparar_grafo
g, PATCHES = preparar_grafo()
from dados.casos import CASOS
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from etapa05_cliente_mcp import chamar_mcp
from etapa10_observabilidade import resumo


class Integracao(unittest.TestCase):
    def setUp(self):
        self.app = g.construir(MemorySaver())

    def rodar(self, nome):
        return self.app.invoke({'thread_id': nome, 'texto': CASOS[nome]['pedido']}, g.config_de(nome))

    def test_01_doze_casos_mcp_real(self):
        esperados = {'C1': ('registrado', 'ae788d33'), 'C2': ('pausado', None),
                     'C3': ('recusado', None), 'C4': ('recusado', None), 'C5': ('pediu_dados', None),
                     'C6': ('registrado', '6f1b47d7'), 'C7': ('recusado', None),
                     'C8': ('duplicado', 'ae788d33'), 'C9': ('pediu_dados', None),
                     'C10': ('pediu_dados', None), 'C11': ('pausado', None),
                     'C12': ('registrado', '7c458e62')}
        resultados = {}
        for nome in CASOS:
            with self.subTest(caso=nome):
                estado = self.rodar(nome)
                atual = ('pausado' if '__interrupt__' in estado else estado['resultado'], estado.get('protocolo'))
                self.assertEqual(atual, esperados[nome.split('_')[0]])
                resultados[nome] = {k: estado.get(k) for k in ('caminho', 'resultado', 'protocolo', 'decisao')}
                if nome.startswith(('C1_', 'C6_', 'C12_')):
                    self.assertEqual(estado['caminho'].count('consolidar'), 1)
        for nome, chefia in [('C2_ferias_com_venda', '1010'), ('C11_diaria_exterior', '1011')]:
            estado = self.app.invoke(Command(resume={'aprovado': True, 'aprovador': chefia, 'motivo': ''}), g.config_de(nome))
            self.assertEqual(estado['resultado'], 'registrado')
            resultados[nome] = {k: estado.get(k) for k in ('caminho', 'resultado', 'protocolo', 'decisao')}
        self.assertEqual(len(json.loads((Path(TEMP.name)/'registros.json').read_text(encoding='utf-8'))), 5)
        Path(ROOT/'evidencias').mkdir(exist_ok=True)
        (ROOT/'evidencias/casos_sem_llm.json').write_text(json.dumps(resultados,ensure_ascii=False,indent=2),encoding='utf-8')
        (ROOT/'evidencias/observabilidade_sem_llm.json').write_text(json.dumps(resumo('C2_ferias_com_venda'),ensure_ascii=False,indent=2),encoding='utf-8')

    def test_02_autorizacao_antes_de_idempotencia(self):
        p = {'protocolo': 'ae788d33', 'matricula': '1001', 'tipo': 'abono', 'inicio': '2027-04-09',
             'fim': '2027-04-09', 'decisao': 'deferido', 'aprovador': 'sistema', 'despacho': 'teste', 'token': 'errado'}
        self.assertFalse(chamar_mcp('registrar_decisao', p)['sucesso'])

    def test_03_saida_invalida_nao_grava(self):
        estado = {'pedido': {'matricula': '1001', 'tipo': 'abono', 'data_inicio': '2027-04-09', 'data_fim': '2027-04-09'},
                  'despacho': 'deferido', 'decisao': 'deferido', 'tentativas': 3, 'erro_validacao': 'falta matrícula'}
        self.assertEqual(g.registrar(estado)['resultado'], 'falha_validacao')
        estado['despacho'] = 'CPF 123.456.789-09'
        self.assertEqual(g.registrar(estado)['resultado'], 'bloqueado_na_saida')

    def test_04_datas_invalidas_e_diaria_incompleta(self):
        p = {'tipo': 'ferias', 'matricula': '1002', 'data_inicio': '2027-02-30', 'data_fim': '2027-03-01'}
        self.assertEqual(g.rotear_extracao({'pedido': p}), 'incompleto')
        p.update(data_inicio='2027-03-10', data_fim='2027-03-01')
        self.assertEqual(g.rotear_extracao({'pedido': p}), 'incompleto')
        p.update(tipo='diaria', data_fim='2027-03-11')
        self.assertEqual(g.rotear_extracao({'pedido': p}), 'incompleto')

    def test_05_decisao_redator_nao_substitui_regra(self):
        e = {'pedido': {'matricula': '1002', 'data_inicio': '2027-04-12'},
             'despacho': 'Matrícula 1002, início 2027-04-12: deferido.', 'decisao': 'indeferido'}
        self.assertIn('decisão objetiva', g.validar(e)['erro_validacao'])

    def test_06_persistencia_entre_processos(self):
        with tempfile.TemporaryDirectory(prefix='rh-checkpoint-') as out:
            for fase in ('iniciar', 'retomar'):
                r = subprocess.run([sys.executable, str(ROOT/'tests/apoio.py'), fase, out],
                                   cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=60,
                                   env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
                self.assertEqual(r.returncode, 0, r.stdout+r.stderr)
                if fase == 'retomar':
                    self.assertIn('RETOMADO EM OUTRO PROCESSO', r.stdout)

    def test_07_auditoria_sem_segredos(self):
        linhas = (Path(TEMP.name)/'auditoria.jsonl').read_text(encoding='utf-8').splitlines()
        acessos = set()
        for linha in linhas:
            registro = json.loads(linha)
            acessos.add(registro['decisao_acesso'])
            self.assertNotIn('token', registro['parametros'])
            self.assertNotIn('despacho', registro['parametros'])
            self.assertNotIn(os.environ['TOKEN_REGISTRO'], linha)
        self.assertEqual(acessos, {'ALLOW','DENY'})

    def test_08_contas_N2_N7(self):
        from calculos_financeiros import venda, diarias
        self.assertEqual(venda(10, 9500), 3166.67)
        r = diarias('2027-06-08', '2027-06-11', 320, 'USD', 5)
        self.assertEqual((r['pernoites'], r['quantidade_diarias'], r['total'], r['total_brl']), (3, 3.5, 1120, 5600))
        self.assertIsNone(diarias('2027-06-08','2027-06-11',320,'USD')['total_brl'])

    def test_09_sugestoes_respeitam_N3_N5(self):
        from sugestoes_periodo import sugerir_periodo
        p = {'tipo': 'ferias', 'matricula': '1003', 'data_inicio': '2027-04-30', 'data_fim': '2027-05-14'}
        self.assertEqual(sugerir_periodo(p, {'limite_afastados': 1, 'afastamentos': []}, ['N3: início proibido']),
                         {'data_inicio': '2027-05-03', 'data_fim': '2027-05-17', 'dias_corridos': 15})
        p.update(matricula='1004',data_inicio='2027-07-12',data_fim='2027-07-26')
        e = {'limite_afastados': 1, 'afastamentos': [{'matricula':'1006','inicio':'2027-07-05','fim':'2027-07-19'}]}
        self.assertEqual(sugerir_periodo(p,e,['N5: conflito'])['data_inicio'],'2027-07-20')
        self.assertIsNone(sugerir_periodo(p,e,[]))

    def test_10_férias_nao_confundem_corridos_com_uteis(self):
        e = {'pedido': {'tipo':'ferias', 'matricula':'1002','data_inicio':'2027-04-12'},
             'periodo': {'dias_corridos':15}, 'decisao':'deferido',
             'despacho':'Matrícula 1002. Início 2027-04-12. Deferido: dias gozados (10).'}
        self.assertIn('15 dias CORRIDOS', g.validar(e)['erro_validacao'])
        e['despacho'] = e['despacho'].replace('(10)', '(15)')
        self.assertEqual(g.validar(e)['erro_validacao'], '')

    def test_11_abono_deferido_nao_exige_chefia(self):
        e = {'pedido': {'tipo':'abono','matricula':'1001','data_inicio':'2027-04-09'},
             'decisao':'deferido','violacoes':[],
             'despacho':'Matrícula 1001. Início 2027-04-09. Deferido. Depende da aprovação da chefia.'}
        self.assertIn('N8:', g.validar(e)['erro_validacao'])
        e['despacho'] = e['despacho'].replace('Depende da aprovação da chefia.', 'Não depende da chefia.')
        self.assertEqual(g.validar(e)['erro_validacao'],'')

    def test_12_sugestao_deve_usar_datas_verificadas(self):
        e = {'pedido': {'tipo':'ferias','matricula':'1003','data_inicio':'2027-04-30'},
             'decisao':'indeferido','alternativa_periodo':{'data_inicio':'2027-05-03','data_fim':'2027-05-17'},
             'despacho':'Matrícula 1003. Início 2027-04-30. Indeferido. Sugestão: 2027-05-17 a 2027-05-31.'}
        self.assertIn('2027-05-03', g.validar(e)['erro_validacao'])
        e['despacho'] = e['despacho'].replace('2027-05-17 a 2027-05-31','2027-05-03 a 2027-05-17')
        self.assertEqual(g.validar(e)['erro_validacao'],'')

    def test_13_status_N8_vem_do_codigo(self):
        from redacao_segura import normalizar_autorizacao
        e = {'pedido':{'tipo':'diaria','matricula':'1003','data_inicio':'2027-06-08','data_fim':'2027-06-11'},
             'decisao':'deferido','violacoes':[]}
        errado = 'Matrícula 1003. Início 2027-06-08. Deferido.\nA diária não depende da chefia.'
        corrigido = normalizar_autorizacao(errado,e)
        self.assertNotIn('não depende',corrigido)
        self.assertIn('aguarda aprovação',corrigido)
        e.update(aprovado=True,aprovador='1011')
        self.assertIn('ratificado pela chefia 1011',normalizar_autorizacao(corrigido,e))
        e['pedido']['tipo'] = 'abono'
        e['aprovado'] = False
        self.assertIn('sem necessidade de chefia',normalizar_autorizacao(errado,e))


if __name__ == '__main__':
    unittest.main()
