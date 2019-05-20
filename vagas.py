import os
import json
from bs4 import BeautifulSoup
import urllib.request
import bottle
from bottle import get, response, run
import requests

from pprint import pprint

app = bottle.default_app()

urls = {
    'flexxo': 'http://www.flexxo.com.br/Caxias+do+Sul/oportunidades/',
    'hg': 'https://www.hgcs.com.br/vagas_disponiveis.php',
    'randon': 'https://randon.gupy.io',
    'ucs': 'https://sou.ucs.br/recursos_humanos/cadastro_curriculo/'}
headers = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linu…) Gecko/20100101 Firefox/65.0'.encode('utf-8')}

def get_soup(url):
    req = urllib.request.Request(url, headers=headers)
    page = urllib.request.urlopen(req)
    return BeautifulSoup(page, 'html.parser')

'''
UCS
'''
def ucs_soup():
    soup = get_soup(urls['ucs'])
    return soup.find_all('li')

def ucs_get_job(job_ucs):
    pos_start = job_ucs.find('"/>')
    pos_end = job_ucs.find('<', pos_start)
    job_ucs = job_ucs[pos_start + 3:pos_end].strip()
    return job_ucs

def ucs_get_formation(job_ucs):
    pos_reference = job_ucs.find('<label>Formação:</label>')
    if pos_reference > 0:
        pos_start = job_ucs.find('">', pos_reference)
        pos_end = job_ucs.find('</div>', pos_start)
        return job_ucs[pos_start + 2:pos_end].strip()
    else:
        return 'Não informado.'

def ucs_get_locale(job_ucs):
    pos_reference = job_ucs.find('<label>Localidade:</label>')
    pos_start = job_ucs.find('">', pos_reference)
    pos_end = job_ucs.find('</div>', pos_start)
    return job_ucs[pos_start + 2:pos_end].strip()

def ucs_get_turn(job_ucs):
    pos_reference = job_ucs.find('<label>Turno:</label>')
    pos_start = job_ucs.find('">', pos_reference)
    pos_end = job_ucs.find('</div>', pos_start)
    return job_ucs[pos_start + 2:pos_end].strip().replace('\n', '').replace(' ', '').replace(',', ', ')

def ucs_get_description(job_ucs):
    pos_ini = job_ucs.find('Descrição:')
    pos_ini = job_ucs.find('">', pos_ini)
    pos_fin = job_ucs.find('</div>', pos_ini)
    return job_ucs[pos_ini + 2:pos_fin].replace('\r\n', ' ')

@get('/jobs_ucs')
def ucs_get_all_jobs():
    jobs_ucs = ucs_soup()
    v_ucs = []
    try:
        for job_ucs in jobs_ucs:
            job_ucs = str(job_ucs)
            d_ucs = {'vaga': ucs_get_job(job_ucs),
                     'formacao': ucs_get_formation(job_ucs),
                     'localidade': ucs_get_locale(job_ucs),
                     'turno': ucs_get_turn(job_ucs),
                     'descricao': ucs_get_description(job_ucs)}
            v_ucs.append(d_ucs)
        return json.dumps(v_ucs)
    except:
        print('erro em ucs')
        return json.dumps(v_ucs)

'''
HG
'''
def hg_soup():
    soup = get_soup(urls['hg'])
    return soup.find_all('div', {'class': 'list-vagas'})

def hg_get_job(job):
    soup = BeautifulSoup(str(job), 'html.parser')
    job = soup.find('div', {'class': 'titulo_vagas'})
    job = str(job.text).strip()
    return job.title()

def hg_get_description(job):
    soup = BeautifulSoup(str(job), 'html.parser')
    job = soup.find('p')
    return job

def hg_get_all_jobs():
    jobs_hg = hg_soup()
    v_hg = []
    try:
        for job in jobs_hg:
            job = str(job)
            d_hg = {'vaga': hg_get_job(job),
                    'descricao': hg_get_description(job)}
            v_hg.append(d_hg)
        return json.dumps(v_hg)
    except:
        print('erro em hg')
        return json.dumps(v_hg)

'''
Flexxo
'''
def soup_flexxo():
    soup = get_soup(urls['flexxo'])
    return (soup.find_all('div', {'class': 'oportunidade rounded'}),
            soup.find_all('div', {'class': 'oportunidade rounded last'}))

@get('/jobs_flexxo')
def flexxo_get_all_jobs():
    jobs_flexxo = []
    soup = soup_flexxo()
    try:
        for job in zip(soup[0], soup[1]):
            soup = BeautifulSoup(str(job), 'html.parser')
            links = soup.find_all('a')
            for link in links:
                jobs_flexxo.append({'vaga': link.text.strip(), 'link': link['href']})
        return json.dumps(jobs_flexxo)
    except:
        print('erro em flexxo')
        return json.dumps(jobs_flexxo)

'''
Randon
'''
def soup_randon():
    soup = get_soup(urls['randon'])
    return soup.find_all('tr', {'data-workplace': 'Caxias do Sul'})

@get('/jobs_randon')
def randon_get_all_jobs():
    v_randon = []
    try:
        jobs_randon1 = soup_randon()
        for job in jobs_randon1:
            soup = BeautifulSoup(str(job), 'html.parser')
            titulo = soup.find('span', {'class': 'title'})
            url_vaga = urls['randon'] + job.a['href']
            d_randon = {'vaga': str(titulo.text).strip(), 'link': url_vaga}
            v_randon.append(d_randon)
        return json.dumps(v_randon)
    except:
        print('erro em randon')
        return json.dumps(v_randon)
        
'''
Menon
'''

@get('/jobs_menon')
def menon_get_all_jobs():
    v_menon = []
    try:
        url='http://www.menonatacadista.com.br/trabalhe-conosco'
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linu…) Gecko/20100101 Firefox/65.0'.encode('utf-8')}
        req = urllib.request.Request(url, headers=headers)
        page = urllib.request.urlopen(req)
        soup = BeautifulSoup(page, 'html.parser')
        container = soup.find_all('div', {'class': 'container'})
        soup = BeautifulSoup(str(container), 'html.parser')
        jobs = soup.find_all('p', {'style': 'text-align: justify; '})
        for job in jobs:
            d_menon = {'vaga': job.text.strip()}
            v_menon.append(d_menon)
        return json.dumps(v_menon)
    except:
        print('erro em menon')
        return json.dumps(v_menon)
    
'''
RBS
'''
@get('/jobs_rbs')
def rbs_get_all_jobs():
    jobs_rbs = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linu…) Gecko/20100101 Firefox/65.0'.encode('utf-8')}
        url='http://www.gruporbs.com.br/talentosrbs/trabalhe-conosco/page/'
        n = 1
        all_jobs = []
        while True:
            req = urllib.request.Request(url+str(n), headers=headers)
            page = urllib.request.urlopen(req)
            soup = BeautifulSoup(page, 'html.parser')
            jobs = soup.find_all('article', {'class': 'post'})
            all_jobs.append(jobs)
            if '<li class="next">' in str(soup):
                n += 1
            else:
                break
        for jobs in all_jobs:
            for job in jobs:
                soup = BeautifulSoup(str(job), 'html.parser')
                titulo = soup.find('h1')
                if 'Caxias do Sul' in titulo.text:
                    vaga = titulo.text
                    link = soup.find('a')
                    link = link['href']
                    desc = soup.find_all('div', {'class': 'blog-content text'})
                    soup_desc = BeautifulSoup(str(desc), 'html.parser')
                    desc = soup_desc.text.strip()
                    pos_start = desc.find('lidades:')
                    pos_end = desc.find('Requisitos:', pos_start)
                    responsabilidades = desc[pos_start+8:pos_end]
                    responsabilidades = responsabilidades.replace('\n\n', ' ').strip()
                    pos_start = desc.find('itos:')
                    pos_end = desc.find('Para proteção', pos_start)
                    requisitos = desc[pos_start+5:pos_end]
                    requisitos = requisitos.replace('\n\n', ' ').strip()
                    d = {'vaga': vaga, 'responsabilidades': responsabilidades, 'requisitos': requisitos, 'link': link}
                    jobs_rbs.append(d)
        return json.dumps(jobs_rbs)
    except:
        return json.dumps(jobs_rbs)

'''
Circulo
'''

@get('/jobs_circulo')
def circulo_get_all_jobs():
    jobs_circulo = []
    try:
        url = 'https://circulosaude.com.br/fale-conosco/trabalhe-conosco/'
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linu…) Gecko/20100101 Firefox/65.0'.encode('utf-8')}
        req = urllib.request.Request(url, headers=headers)
        page = urllib.request.urlopen(req)
        soup = BeautifulSoup(page, 'html.parser')
        jobs = soup.find_all('div', {'class': 'l-oportunidade'})
        for job in jobs:
            soup = BeautifulSoup(str(job), 'html.parser')
            vaga = soup.find('p', {'class': 'negrito'})
            vaga = vaga.text
            desc = soup.find('ul')
            desc = str(desc.text)
            pos1 = desc.find('Horário:')
            pos2 = desc.find('Local:', pos1)
            horario = (desc[pos1+8:pos2]).strip()
            pos1 = desc.find('Requisitos:')
            local = (desc[pos2+6:pos1]).strip()
            pos2 = desc.find('Competências necessárias:')
            requisitos = (desc[pos1+11:pos2]).strip()
            competencias = (desc[pos2+len('Competências necessárias:'):]).strip()
            d = {'vaga': vaga,
                 'horario': horario,
                 'requisitos': requisitos,
                 'competencias': competencias}
            jobs_circulo.append(d)
        return json.dumps(jobs_circulo)
    except:
        return json.dumps(jobs_circulo)

'''
Senac
'''

@get('/jobs_senac')
def senac_get_all_jobs():
    jobs_senac = []
    try:
        url = ' https://trabalheconosco.senacrs.com.br/vagas/em-processo-de-selecao'
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linu…) Gecko/20100101 Firefox/65.0'.encode('utf-8')}
        req = urllib.request.Request(url, headers=headers)
        page = urllib.request.urlopen(req)
        soup = BeautifulSoup(page, 'html.parser')
        jobs = soup.find('dl', {'class': 'vagas'})
        links = []
        if '<dt>Caxias do Sul</dt>' in str(jobs):
            pos_start = str(jobs).find('<dt>Caxias do Sul</dt>')
            pos_end = str(jobs).find('<dt>', pos_start+1)
            jobs = str(jobs)[pos_start:pos_end]
            soup = BeautifulSoup(str(jobs), 'html.parser')
            jobs = soup.find_all('a')
            url = 'https://trabalheconosco.senacrs.com.br'
            for job in jobs:
                links.append(url+job['href'])
        for link in links:
            req = urllib.request.Request(link, headers=headers)
            page = urllib.request.urlopen(req)
            soup = BeautifulSoup(page, 'html.parser')
            detalhes = soup.find('dl', {'class': 'detalhes-vaga'})
            soup = BeautifulSoup(str(detalhes), 'html.parser')
            vaga = soup.find('dt')
            desc = []
            for v in vaga:
                desc.append(str(v).strip())
                break
            dados = soup.find_all('div', {'class': 'dados'})
            for dado in dados:
                soup = BeautifulSoup(str(dado), 'html.parser')
                span = soup.find('span')
                desc.append(str(span.text).strip())
            d_senac = {'vaga': desc[0],
                       'unidade': desc[1],
                       'area': desc[3],
                       'formacao': desc[4],
                       'requisitos': desc[5],
                       'beneficios': desc[6],
                       'publicado': desc[7]}
            jobs_senac.append(d_senac)
        return json.dumps(jobs_senac)
    except:
        return json.dumps(jobs_senac)
        
'''
STV
'''
@get('/jobs_stv')
def stv_get_all_jobs():
    jobs_stv = []
    try:
        url = 'http://rh.stv.com.br/'
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linu…) Gecko/20100101 Firefox/65.0'.encode('utf-8')}
        req = urllib.request.Request(url, headers=headers)
        page = urllib.request.urlopen(req)
        soup = BeautifulSoup(page, 'html.parser')
        table = soup.find('table', {'class': 'table table-striped'})
        soup = BeautifulSoup(str(table), 'html.parser')
        tr = soup.find_all('tr')
        links = []
        for td in tr:
            if 'Caxias do Sul' in str(td):
                soup = BeautifulSoup(str(td), 'html.parser')
                a = soup.find('a')
                links.append((a.text, a['href']))
        for link in links:
            req = urllib.request.Request(link[1], headers=headers)
            page = urllib.request.urlopen(req)
            soup = BeautifulSoup(page, 'html.parser')
            vaga = soup.find('div', {'class': 'col-md-12'})
            vaga = str(vaga.text).strip()
            pos1 = vaga.find('Descrição:')
            pos2 = vaga.find('Habilidades:')
            descricao = (vaga[pos1+10:pos2]).strip()
            pos1 = vaga.find('Localidade:', pos2)
            habilidade = (vaga[pos2+12:pos1]).strip()
            pos2 = vaga.find('Horário:')
            localidade = (vaga[pos1+11:pos2]).strip()
            pos1 = vaga.find('Forma de Contratação', pos2)
            horario = (vaga[pos2+8:pos1]).strip()
            pos2 = vaga.find('Benefícios:', pos1)
            contrato = (vaga[pos1+20:pos2]).strip()
            pos1 = vaga.find('Remuneração:', pos2)
            beneficios = (vaga[pos2+11:pos1]).strip()
            pos2 = vaga.find('Observação:', pos1)
            remuneracao = (vaga[pos1+12:pos2]).strip()
            pos1 = vaga.find('Candidatar-se', pos2)
            observacao = (vaga[pos2+11:pos1]).strip()
            d = {'vaga': link[0], 'descricao': descricao, 'habilidades': habilidade, 'localidade': localidade, 'horario': horario,
                 'contrato': contrato, 'beneficios': beneficios, 'remuneracao': remuneracao, 'observacao': observacao}
            jobs_stv.append(d)

        return json.dumps(jobs_stv)
    except:
        return json.dumps(jobs_stv)

'''
Anhanguera
'''

@get('/jobs_anhanguera')
def anhanguera_get_all_jobs():
    jobs_anhanguera = []
    try:
        api = 'https://eb.vagas.com.br/pesquisa-vagas/kroton.json?c[]=Caxias+do+Sul&div[]=40464&div[]=60086&div[]=60081&div[]=60082&div[]=60084&div[]=63697&div[]=60085&div[]=60083&div[]=47132&div[]=60110&div[]=60111&div[]=60112&div[]=60113&div[]=60114&div[]=63698&page=1&page_size=135&q=caxias+do+sul'
        response = requests.get(api)
        vagas = json.loads(response.text)
        for i in vagas['anuncios']:
            if 'Anhanguera' in i['empresa']:
                d = {'vaga':i['cargo'],
                     'url': i['url']}
                jobs_anhanguera.append(d)
        return json.dumps(jobs_anhanguera)
    except:
        return json.dumps(jobs_anhanguera)


run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
