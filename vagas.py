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
    'ambev' : 'https://ambev.gupy.io/',
    'flexxo': 'http://www.flexxo.com.br/Caxias+do+Sul/oportunidades/',
    'fruki': 'https://jobs.kenoby.com/fruki/position',
    'fsg': 'http://centraldecarreiras.fsg.br/candidatos',
    'hg': 'https://www.hgcs.com.br/trabalhe_conosco.php',
    'ilumisol': 'https://www.ilumisolenergiasolar.com.br/trabalhe-conosco/',
    'intercity': 'https://ich.peoplenect.com/ats/external_applicant/index.php?page=ajax_quick_job&action=view',
    'mundial-sa': 'http://mundial-sa.com.br/carreira_vagas-disponiveis.php',
    'nl': 'https://www.nl.com.br/trabalhe-conosco/',
    'randon': 'https://randon.gupy.io',
    'sicredi': 'https://sicredi.gupy.io',
    'sperinde': 'https://www.sperinde.com/trabalhe/',
    'swan': 'https://www.swanhoteis.com.br/trabalhe-conosco?hotel=4',
    'twtransportes': 'https://www.twtransportes.com.br/trabalhe/#',
    'ucs': 'https://sou.ucs.br/recursos_humanos/cadastro_curriculo/',
    'uniftec': 'https://ceo.ftec.com.br/vagas.php?cat=0',
    'unimed': 'https://sistemas.unimednordesters.com.br/vagas/'}
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
    job = str(job.text).replace('\u0095', '').strip().title()
    job = ''.join([c for c in job if c.isalnum() or ' '])
    return job

def hg_get_description(job):
    soup = BeautifulSoup(str(job), 'html.parser')
    desc = soup.find('p')
    desc = str(desc)
    desc = desc.replace('<p style="text-align: justify;">', '').replace('<p style="text-align:justify">', '')
    desc = desc.replace('</p>', '').replace('<p>', '').replace('</span>', '').replace('<span style="color:rgb(34, 34, 34); font-family:arial,helvetica,sans-serif; font-size:small">', '')
    desc = desc.replace('<br/>','\n').replace('<strong>', '').replace('</strong>', '')
    desc = desc.split('\n')
    descs = []
    for d in desc:
        x = d.split(':')
        x = {x[0].strip(): x[1].strip()}
        descs.append(x)
    return descs

@get('/jobs_hg')
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

def flexxo_job(link):
    return link.text.strip()

def flexxo_link(link):
    return link['href']

def flexxo_description(link):
    url = 'http://www.flexxo.com.br/' + link['href']
    soup = get_soup(url)
    return soup.find('div', {'class': 'texto'}).text


@get('/jobs_flexxo')
def flexxo_get_all_jobs():
    jobs_flexxo = []
    soup = soup_flexxo()
    for job in zip(soup[0], soup[1]):
        try:
            soup = BeautifulSoup(str(job), 'html.parser')
            links = soup.find_all('a')
            for link in links:
                try:
                    vaga = flexxo_job(link)
                except:
                    vaga = None
                try:
                    descricao = flexxo_description(link)
                except:
                    descricao = None
                try:
                    link = flexxo_link(link)
                except:
                    link = None
                if (vaga is not None) or (descricao is not None) or (link is not None):
                    jobs_flexxo.append({'vaga': vaga, 'descricao': descricao, 'link': link})
                else:
                    print('flexxo não adiciou vaga')
        except:
            print('except flexxo')

        return json.dumps(jobs_flexxo)

#         print('erro em flexxo')
    return json.dumps(jobs_flexxo)

    
'''
Randon
'''
def soup_randon():
    soup = get_soup(urls['randon'])
    return soup.find_all('tr', {'data-workplace': 'Caxias do Sul'})

def randon_job(soup):
    vaga = soup.find('span', {'class': 'title'})
    return str(vaga.text).strip()

def randon_url(job):
    return urls['randon'] + job.a['href']

def randon_description(job):
    url = randon_url(job)
    soup = get_soup(url)
    description = soup.find('div', {'class': 'description'})
    soup = BeautifulSoup(str(description), 'html.parser')

    d = str(soup.text)
    p1 = d.find('Descrição da vaga')
    p2 = d.find('AS EMPRESAS RANDON')
    d = d[p1:p2]
    d = d.strip()
    d = d.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ').replace('        ', ' ')

    d1 = d.find('Descrição da vaga')
    d2 = d.find('Responsabilidades e atribuições')
    descricao = d[d1+len('Descrição da vaga'):d2]

    a1 = d.find('Responsabilidades e atribuições')
    a2 = d.find('Requisitos e qualificações')
    responsabilidades = d[a1+len('Responsabilidades e atribuições'):a2]

    q1 = d.find('Requisitos e qualificações')
    q2 = d.find('Informações adicionais')
    requisitos = d[q1+len('Requisitos e qualificações'):q2]

    i1 = d.find('Informações adicionais')
    informacoes = d[i1+len('Informações adicionais'):]

    description = {
        'descricao': descricao.strip(),
        'responsabilidades': responsabilidades.strip(),
        'requisitos': requisitos.strip(),
        'informacoes': informacoes.strip()}

    return description

@get('/jobs_randon')
def randon_get_all_jobs():
    v_randon = []
    try:
        for job in soup_randon():
            soup = BeautifulSoup(str(job), 'html.parser')

            vaga = randon_job(soup)
            url = randon_url(job)
            description = randon_description(job)

            d_randon = {'vaga': vaga, 'link': url, 'descricao': description}
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
            vaga = job.text.strip()
            vaga = vaga.replace('\xa0- \xa0', '').replace('\xa0p/ \xa0', '')
            vaga = vaga.replace('\xa0', '')
            d_menon = {'vaga': vaga}
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
                d = {'vaga':i['cargo'].title(),
                     'url': i['url']}
                jobs_anhanguera.append(d)
        return json.dumps(jobs_anhanguera)
    except:
        return json.dumps(jobs_anhanguera)

'''
FSG
'''
def soup_fsg():
    soup = get_soup(urls['fsg'])
    return soup.find_all('div', {'class': 'box-single'})

def fsg_job(job):
    return str(job.find('h3').text).title().strip()

def fsg_publish_date(job):
    return str(job.find('div', {'class': 'data'}).text).strip()

def fsg_link(job):
    a = job.find('a')
    return 'http://centraldecarreiras.fsg.br'+a['href']

def fsg_description(link):
    description = get_soup(link)
    description = description.find_all('div', {'class': 'sessao'})
    d = ''
    for desc in description:
        desc = str(desc.text).replace('\n', ' ').replace('\t', ' ').replace('\r', ' ').replace('  ', ' ')
        d = d + desc
    return d

@get('/jobs_fsg')
def fsg_get_all_jobs():
    soup = soup_fsg()
    jobs_fsg = []
    for job in soup:
        job = BeautifulSoup(str(job), 'html.parser')
        try:
            title = fsg_job(job)
            date = fsg_publish_date(job)
            link = fsg_link(job)
            description = fsg_description(link)
            jobs_fsg.append({'vaga': title, 'data': date, 'descricao': description, 'link': link})
        except:
            pass
    return json.dumps(jobs_fsg) 


'''
Ilumisol
'''


def soup_ilumisol():
    soup = get_soup(urls['ilumisol'])
    return soup.find_all('td', {'class': 'td-actions text-right'})


def ilumisol_link():
    links = []
    for t in soup_ilumisol():
        if 'caxias-do-sul' in str(t):
            links.append(t.a['href'])
    return links


@get('/jobs_ilumisol')
def soup_ilumisol_job():
    jobs_ilumisol = []
    try:
        for job in ilumisol_link():
            soup = get_soup(job)
            h1 = soup.find('h1')
            jobs_ilumisol.append({'vaga': h1.text, 'link': job})
        return json.dumps(jobs_ilumisol)
    except:
        pass
    return json.dumps(jobs_ilumisol)


'''
Sperinde
'''


def soup_sperinde():
    soup = get_soup(urls['sperinde'])
    return soup.find_all('div', {'class': 'panel panel-default'})


@get('/jobs_sperinde')
def sperinde_jobs():
    jobs_sperinde = []
    try:
        for job in soup_sperinde():
            soup = BeautifulSoup(str(job), 'html.parser')
            job = soup.h4.text
            job = str(job).strip()
            soup = BeautifulSoup(str(soup), 'html.parser')
            desc = soup.find('div', {'class': 'panel-body'})
            soup = BeautifulSoup(str(desc), 'html.parser')
            b = soup.find_all('b')
            texto = (soup.text).replace(b[0].text, ' ').replace(b[1].text, ' ')
            texto = texto.split('\n')
            l = []
            for t in texto:
                t = t.strip()
                if len(t) > 0:
                    l.append(t)
            jobs_sperinde.append({'vaga': job, str(b[0].text).replace(':', ''): l[0], str(b[1].text).replace(':', ''): l[1]})
        return json.dumps(jobs_sperinde)
    except:
        pass
    return json.dumps(jobs_sperinde)


'''
TW Transportes
'''


@get('/jobs_tw')
def soup_tw():
    soup = get_soup(urls['twtransportes'])
    corp = soup.find_all('tr', {'class': 'corp'})
    desc = soup.find_all('tr', {'class': 'desc'})

    jobs = []
    for i, c in enumerate(corp):
        c = str(c)
        if 'CAXIAS DO SUL/RS' in c:
            job = BeautifulSoup(c, 'html.parser')
            job = job.find('td')
            jobs.append((i, job.text))
    items_dict = []
    jobs_tw = []
    for i, x in enumerate(range(len(jobs))):
        x = desc[jobs[i][0]]
        x = BeautifulSoup(str(x), 'html.parser')
        d = x.find_all('p')
        s = x.find_all('strong')
        for s, p in zip(s, d):
            chave = s.text
            valor = str(p.text).replace(chave, '').replace('\r\n', ' ').strip()
            items_dict.append((chave, valor))
        dict_tw = {}
        dict_tw['vaga']= jobs[i][1]
        for i in items_dict:
            dict_tw[i[0]] = i[1]
        jobs_tw.append(dict_tw)
    return json.dumps(jobs_tw)


'''
Unimed
'''


@get('/jobs_unimed')
def soup_unimed():
    jobs_unimed = []
    soup = get_soup(urls['unimed'])
    soup = soup.find('form', {'id': 'frmVagas'})
    soup = BeautifulSoup(str(soup), 'html.parser')
    soup = soup.find('tbody')
    soup = BeautifulSoup(str(soup), 'html.parser')
    soup = soup.find_all('tr')
    for tr in soup:
        tr = BeautifulSoup(str(tr), 'html.parser')
        td = tr.find_all('td')
        vaga = str(td[0].text).strip()
        try:
            det0 = vaga.find('(')
            det1 = vaga.find(')', det0)
            det = vaga[det0+1:det1].capitalize()
            vaga = vaga[:det0]
        except:
            det = 'Não informado.'
        local = str(td[1].text).strip()
        jobs_unimed.append({'vaga': vaga, 'descricao': det, 'local': local})
    return json.dumps(jobs_unimed)


'''
Intercity
'''

@get('/jobs_intercity')
def soup_intercity():
    import ssl
    gcontext = ssl.SSLContext()
    req = urllib.request.Request(urls['intercity'], headers=headers)
    page = urllib.request.urlopen(req, context=gcontext)
    soup = BeautifulSoup(page, 'html.parser')
    soup = soup.find_all('tr')
    jobs_intercity = []
    for tr in soup:
        tr = str(tr)
        if 'Caxias do Sul-RS' in tr:
            tr = BeautifulSoup(tr, 'html.parser')
            tr = tr.find_all('td')
            vaga = str(tr[3].text).strip()
            codigo = str(tr[2].text).strip()
            url_vaga = 'https://ich.peoplenect.com/ats/external_applicant/?page=view_jobs_details&job_id=' + \
                       str(codigo) + \
                       '&pageno=1'
            req = urllib.request.Request(url_vaga, headers=headers)
            page = urllib.request.urlopen(req, context=gcontext)
            soup = BeautifulSoup(page, 'html.parser')
            soup = soup.find_all('div', {'class': 'container'})
            for s in soup:
                if 'Descrição de Vaga' in str(s):
                    table = BeautifulSoup(str(s), 'html.parser')
                    table = table.find('table')
                    tr = BeautifulSoup(str(table), 'html.parser')
                    tr = tr.findAll('tr')
                    dict_intercity = {}
                    for td in tr:
                        td = BeautifulSoup(str(td), 'html.parser')
                        td = td.findAll('td')
                        chave = str(td[0].text).strip()
                        valor = str(td[1].text).strip()
                        dict_intercity[chave] = valor
                    dict_intercity['vaga'] = dict_intercity.pop('Título da vaga:')
                    jobs_intercity.append(dict_intercity)
    return json.dumps(jobs_intercity)


'''
Fruki
'''


def soup_fruki():
    soup = get_soup(urls['fruki'])
    return soup.findAll('div', {'class': 'segment'})


def job_link():
    links = []
    soup = soup_fruki()
    for segment in soup:
        det = BeautifulSoup(str(segment), 'html.parser')
        a = det.findAll('a')
        for link in a:
            if 'caxias-do-sul' in link['href']:
                links.append(link['href'])
    return links


@get('/jobs_fruki')
def fruki():
    jobs_fruki = []
    for link in job_link():
        soup = get_soup(link)
        soup = soup.find('article')
        vaga = str(soup.h1.text).strip()
        segmento = str(soup.h3.text).strip()
        det = soup.find('div', {'class': 'description'})
        det = str(det.text).strip()
        jobs_fruki.append({'vaga': vaga, 'segmento': segmento, 'detalhes': det})
    return json.dumps(jobs_fruki)


'''
Ambev
'''


def soup_ambev():
    soup = get_soup(urls['ambev'])
    soup = soup.findAll('div', {'class': 'job-list jobs-to-filter'})
    soup = BeautifulSoup(str(soup), 'html.parser')
    soup = soup.findAll('tr', {'data-type': 'Efetivo'})
    soup = BeautifulSoup(str(soup), 'html.parser')
    soup = soup.findAll('tr', {'data-workplace': 'Caxias do Sul'})
    return soup

def get_links():
    links = []
    soup = soup_ambev()
    for a in soup:
        links.append(a.a['href'])
    return links

@get('/jobs_ambev')
def get_job():
    jobs_ambev = []
    links = get_links()
    for job in links:
        url = 'https://ambev.gupy.io' + job
        soup = get_soup(url)
        job = soup.title.text
        # soup = soup.find('script', {'type': 'application/ld+json'})
        # soup = soup.contents[0]
        # json_soup = json.loads(soup)
        # desc = json_soup['description']
        # desc = BeautifulSoup(str(desc), 'html.parser')        
        # det = ''
        # for d in desc:
            # if len(d) > 0:
            #     print(len(d), d)

            # det = det + str(d.text) + '\n'
        # print(det)
        jobs_ambev.append({'vaga': job, 'link': url})
        
    return json.dumps(jobs_ambev)

'''
NL
'''


@get('/jobs_nl')
def soup_nl():
    req = urllib.request.Request(urls['nl'], headers=headers)
    page = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(page, 'html.parser')
    jobs = soup.find_all('span', {'class': 'edgtf-tab-title-inner'})
    desc1 = soup.find_all('span', {'class': 'edgtf-st-text-text'})
    
    jobs_nl = []
    for i in range(0, len(jobs)):
        job = str(jobs[i].text).strip().title()
        d1 = str(desc1[i].text).strip()
        jobs_nl.append({'vaga': job, 'descricao': d1})

    return json.dumps(jobs_nl)


'''
Mundial SA
'''

def soup_mundial_sa():
    soup = get_soup(urls['mundial-sa'])
    soup = soup.find('div', {'class': 'wrap'})
    soups = []
    for s in soup:
        if 'Caxias do Sul' in str(s) and 'Unidade de atuação:' in str(s):
            soups.append(s)
    return soups

@get('/jobs_mundial_sa')
def jobs_mundial_sa():
    soups = soup_mundial_sa()
    list_mundial_sa = []
    for soup in soups:
        titulo_vaga = soup.find('div', {'class': 'titulo_vagas'}).text
        titulo_vaga = str(titulo_vaga).title()
        p = soup.find('p')
        chave = p.findAll('strong')
        value = []
        dict_mundial_sa = {}
        for i in p:
            if len(i) > 1 and 'strong' not in str(i):
                value.append(i)
        dict_mundial_sa['vaga'] = titulo_vaga
        for k, v in zip(chave, value):
            k = k.text
            k = str(k).replace(':', '')
            v = str(v).strip()
            dict_mundial_sa[k] = v

        list_mundial_sa.append(dict_mundial_sa)
    return json.dumps(list_mundial_sa)


'''
Sicredi
'''

def soup_sicredi():
    soup = get_soup(urls['sicredi'])
    return soup.find_all('tr', {'data-workplace': 'Caxias do Sul'})

def sicredi_jobs(soup):
    vaga = soup.find('span', {'class': 'title'})
    return str(vaga.text).strip()

def sicredi_url(job):
    return urls['sicredi'] + job.a['href']

@get('/jobs_sicredi')
def sicredi_get_all_jobs():
    v_sicredi = []
    try:
        for job in soup_sicredi():
            vaga = sicredi_jobs(job)
            url = sicredi_url(job)
            d_sicredi = {'vaga': vaga, 'url': url}
            v_sicredi.append(d_sicredi)
        return json.dumps(v_sicredi)
    except:
        print('erro em sicredi')
        pass

    return json.dumps(v_sicredi)


'''
Swan
'''
@get('/jobs_swan')
def soup_swan():
    v_swan = []
    soup = get_soup(urls['swan'])
    soup = soup.findAll('div', {'class': 'trabalhe-conosco-vagas'})
    for s in soup:
        job = str(s.h4.text).strip()
        p = BeautifulSoup(str(s), 'html.parser')
        p = p.findAll('p')
        desc = ''
        for i in p:
            desc = desc + i.text + '\n'
        d_swan = {'vaga': job, 'desc': desc}
        v_swan.append(d_swan)
    return json.dumps(v_swan)


'''
Uniftec
'''
def soup_uniftec():
    soup = get_soup(urls['uniftec'])
    soup = soup.find('fieldset')
    soup = BeautifulSoup(str(soup), 'html.parser')
    return soup.findAll('div', {'class': 'Caxias-do-Sul'})

def uniftec_get_link():
    links_emprego = []
    links_estagio = []
    url = 'https://ceo.ftec.com.br/'
    for i in soup_uniftec():
        link = url + i.a['href']
        if 'Estágio' not in str(i) and 'estágio' not in str(i):
            links_emprego.append(link)
        else:
            links_estagio.append(link)
    return links_emprego, links_estagio

def uniftec_get_job(link):
    soup = get_soup(link)
    soup = soup.find('div', {'id': 'cont'})
    soup = str(soup.h1.text).title()
    return soup

def unifet_get_job_desc(link):
    soup = get_soup(link)
    soup = soup.find('fieldset', {'id': 'detalheVaga'})
    desc = soup.dl.text
    desc = str(desc).lstrip('''Unidade
 Caxias do Sul
Tipo da Vaga
 Emprego
Mais Informações''')
    desc = desc.rstrip('''

Para se cadastrar precisa fazer o login.''')
    return desc

@get('/jobs_uniftec')
def unifet_get_all_jobs():
    v_uniftec = []
    cont = 0
    for link in uniftec_get_link()[0]:
        vaga = uniftec_get_job(link)
        desc = unifet_get_job_desc(link)
        d_uniftec = {'vaga': vaga, 'desc': desc, 'link': link}
        v_uniftec.append(d_uniftec)
        cont += 1
        if cont >= 12:
            break     
            
    return json.dumps(v_uniftec)



run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
