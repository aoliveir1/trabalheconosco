import os
import json
import time
from bs4 import BeautifulSoup
import urllib.request
import bottle
from bottle import get, response, run
from splinter import Browser
from splinter.driver.webdriver import BaseWebDriver, WebDriverElement
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

app = bottle.default_app()

'''
UCS
'''
page_ucs = urllib.request.urlopen('https://sou.ucs.br/recursos_humanos/cadastro_curriculo/')
soup_ucs = BeautifulSoup(page_ucs, 'html.parser')
jobs_ucs = soup_ucs.find_all('li')

def ucs_get_job(job_ucs):
    pos_start = job_ucs.find('"/>')
    pos_end = job_ucs.find('<',pos_start)
    job_ucs = job_ucs[pos_start+3:pos_end].strip()
    return job_ucs

def ucs_get_formation(job_ucs):
    pos_reference = job_ucs.find('<label>Formação:</label>')
    if pos_reference > 0:
        pos_start = job_ucs.find('">', pos_reference)
        pos_end = job_ucs.find('</div>', pos_start)
        return job_ucs[pos_start+2:pos_end].strip()
    else:
        return 'Não informado.'

def ucs_get_locale(job_ucs):
    pos_reference = job_ucs.find('<label>Localidade:</label>')
    pos_start = job_ucs.find('">', pos_reference)
    pos_end = job_ucs.find('</div>', pos_start)
    return job_ucs[pos_start+2:pos_end].strip()

def ucs_get_turn(job_ucs):
    pos_reference = job_ucs.find('<label>Turno:</label>')
    pos_start = job_ucs.find('">', pos_reference)
    pos_end = job_ucs.find('</div>', pos_start)
    return job_ucs[pos_start+2:pos_end].strip().replace('\n', '').replace(' ', '').replace(',', ', ')

def ucs_get_description(job_ucs):
    pos_ini = job_ucs.find('Descrição:')
    pos_ini = job_ucs.find('">', pos_ini)
    pos_fin = job_ucs.find('</div>', pos_ini)
    return job_ucs[pos_ini + 2:pos_fin].replace('\r\n', ' ')

@get('/jobs_ucs')
def ucs_get_all_jobs():
    v_ucs=[]

    for job_ucs in jobs_ucs:
        job_ucs = str(job_ucs)
        d_ucs = {'vaga': ucs_get_job(job_ucs),
                 'formacao': ucs_get_formation(job_ucs),
                 'localidade': ucs_get_locale(job_ucs),
                 'turno': ucs_get_turn(job_ucs),
                 'descricao': ucs_get_description(job_ucs)}
        v_ucs.append(d_ucs)

    return json.dumps(v_ucs)

'''
HG
'''

page = urllib.request.urlopen('https://www.hgcs.com.br/vagas_disponiveis.php')
soup = BeautifulSoup(page, 'html.parser')
jobs = soup.find_all('div', {'class': 'div_vagas'})

def hg_get_job(job):
    pos_start = job.find('titulo_vagas')
    pos_end = job.find('<',pos_start)
    job = job[pos_start+15:pos_end].strip().capitalize()
    return job

def hg_get_sector(job):
    pos_start = job.find('Setor:')
    if pos_start < 0:
        return 'Não informado.'
    pos_end = job.find('<',pos_start)
    sector = job[pos_start + 6:pos_end].strip()
    return sector

def hg_get_working_hours(job):
    pos_start = job.find('Carga')
    if pos_start < 0:
        return 'Não informado.'
    pos_end = job.find('<', pos_start)
    wh = job[pos_start+14:pos_end].strip()
    return wh

def hg_get_schedule(job):
    pos_start = job.find('Horário de Trabalho:')
    if pos_start < 0:
        return 'Não informado.'
    pos_end = job.find('<', pos_start)
    schedule = job[pos_start+20:pos_end].strip()
    return schedule

def hg_get_contract(job):
    pos_start = job.find('Contratação:')
    if pos_start < 0:
        return 'Não informado'
    pos_end = job.find('<',pos_start)
    contract = job[pos_start + 12:pos_end].strip()
    return contract

def hg_get_requirements(job):
    pos_start = job.find('equisito')
    if pos_start < 0:
        return 'Não informado.'
    pos_end = job.find('<', pos_start)
    return job[pos_start+10:pos_end].strip()

@get('/jobs_hg')
def hg_get_all_jobs():
    v_hg=[]

    for job in jobs:
        job = str(job)
        d_hg = {'vaga': hg_get_job(job),
             'setor': hg_get_sector(job),
             'carga horaria': hg_get_working_hours(job),
             'horario': hg_get_schedule(job),
             'contrato': hg_get_contract(job),
             'requisito': hg_get_requirements(job)}
        v_hg.append(d_hg)

    return json.dumps(v_hg)

'''
FTEC
'''

def ftec_get_names(soup):
    names = soup.find_all('div', attrs={'class': 'listaVagasTitulo'})
    list_names = []
    for name in names:
        list_names.append(name.text.strip())
    return list_names

def ftec_get_date_published(soup):
    date_published = soup.find_all('div', attrs={'class': 'listaVagasData'})
    list_dates = []
    for dt in date_published:
        dt = str(dt).strip()
        pos_reference = dt.find('Data de Publicação:')
        pos_start = dt.find('bolder;">', pos_reference)
        list_dates.append(dt[pos_start + 9:pos_start + 19])
    return list_dates

def ftec_get_place(soup):
    place = soup.find_all('div', attrs={'class': 'listaVagasDescritivos'})
    list_places = []
    for i, l in enumerate(place):
        if i > 0:
            l = str(l)
            pos_reference = l.find('Localidade:')
            pos_start = l.find('"ng-binding">', pos_reference)
            pos_end = l.find('</span>', pos_start)
            list_places.append(l[pos_start + 13:pos_end])
    return list_places

def ftec_get_description(soup):
    description = soup.find_all('div', attrs={'class': 'listaVagasDescritivos'})
    list_desc = []
    for i, desc in enumerate(description):
        if i > 0:
            desc = str(desc)
            pos_reference = len('controller.validaQuebradeLinha(vaga.Descricao)">')
            pos_start = desc.find('<br/>', pos_reference)
            pos_end = desc.find('</div>', pos_start)
            desc = desc[pos_start:pos_end]
            list_desc.append(desc.replace('</p>', '').replace('<br/>', '').replace('\n', ''))
    return list_desc

@get('/jobs_uniftec')
def ftec_get_all_jobs():
    response.headers['Content-Type'] = 'application/json'
    response.headers['Cache-Control'] = 'no-cache'

    browser = Browser('chrome', headless = True)
    browser.visit('http://educacional.ftec.com.br:8080/RM/Rhu-BancoTalentos/#/RM/Rhu-BancoTalentos/painelVagas/lista')
    
    jobs = [{'nome': 'titulo', 'data': 'data', 'local': 'local', 'descricao': 'desc'}]
    time.sleep(1)
    if browser.is_element_present_by_text('Data de Publicação: ', wait_time=True):
        soup = BeautifulSoup(browser.html, 'html.parser')
        for titulo, data, local, desc in zip(ftec_get_names(soup), ftec_get_date_published(soup), ftec_get_place(soup), ftec_get_description(soup)):
            d = {'nome': titulo, 'data': data, 'local': local, 'descricao': desc}
            jobs.append(d)
            
    browser.quit()

    return json.dumps(jobs)

'''
Flexxo
'''
@get('/jobs_flexxo')
def flexxo_get_all_jobs():
    url = 'http://www.flexxo.com.br/Caxias+do+Sul/oportunidades/'
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linu…) Gecko/20100101 Firefox/65.0'.encode('utf-8')}
    req = urllib.request.Request(url, headers=headers)
    page = urllib.request.urlopen(req)
    soup = BeautifulSoup(page, 'html.parser')
    jobs_flexxo1 = soup.find_all('div', {'class': 'oportunidade rounded'})
    jobs_flexxo2 = soup.find_all('div', {'class': 'oportunidade rounded last'})

    jobs_flexxo = []
    for job in zip(jobs_flexxo1, jobs_flexxo2):
        soup = BeautifulSoup(str(job), 'html.parser')
        links = soup.find_all('a')
        for link in links:
            jobs_flexxo.append({'vaga': link.text.strip(), 'link': link['href']})

    return json.dumps(jobs_flexxo)

'''
Randon
'''

@get('/jobs_randon')
def randon_get_all_jobs():
    url = 'https://randon.gupy.io'
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linu…) Gecko/20100101 Firefox/65.0'.encode('utf-8')}
    req = urllib.request.Request(url, headers=headers)
    page = urllib.request.urlopen(req)
    soup = BeautifulSoup(page, 'html.parser')
    jobs_randon1 = soup.find_all('tr', {'data-workplace': 'Caxias do Sul'})
    v_randon = []
    for job in jobs_randon1:
        soup = BeautifulSoup(str(job), 'html.parser')
        titulo = soup.find('span', {'class': 'title'})
        url_vaga = url+job.a['href']
        d_randon = {'vaga': str(titulo.text).strip(), 'link': url_vaga}
        v_randon.append(d_randon)
    return json.dumps(v_randon)
        
'''
Menon
'''

@get('/jobs_menon')
def menon_get_all_jobs():
    url='http://www.menonatacadista.com.br/trabalhe-conosco'
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linu…) Gecko/20100101 Firefox/65.0'.encode('utf-8')}
    req = urllib.request.Request(url, headers=headers)
    page = urllib.request.urlopen(req)
    soup = BeautifulSoup(page, 'html.parser')
    container = soup.find_all('div', {'class': 'container'})
    soup = BeautifulSoup(str(container), 'html.parser')
    jobs = soup.find_all('p', {'style': 'text-align: justify; '})
    v_menon = []
    for job in jobs:
        d_menon = {'vaga': job.text.strip()}
        v_menon.append(d_menon)
    return json.dumps(v_menon)
    
'''
RBS
'''
@get('/jobs_rbs')
def rbs_get_all_jobs():
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
    jobs_rbs = []
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

run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
