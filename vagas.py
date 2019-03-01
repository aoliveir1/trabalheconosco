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
        return '(Não informado.)'

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

    #response.headers['Content-Type'] = 'application/json'
    #response.headers['Cache-Control'] = 'no-cache'

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
    job = job[pos_start+15:pos_end].strip()
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
    v=[]

    #response.headers['Content-Type'] = 'application/json'
    #response.headers['Cache-Control'] = 'no-cache'

    for job in jobs:
        job = str(job)
        d = {'vaga': hg_get_job(job),
             'setor': hg_get_sector(job),
             'carga horaria': hg_get_working_hours(job),
             'horario': hg_get_schedule(job),
             'contrato': hg_get_contract(job),
             'requisito': hg_get_requirements(job)}
        v.append(d)

    return json.dumps(v)



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
  
    #options = Options()
    #options.add_argument('--disable-gpu')
    #options.add_argument('--no-sandbox')
    
    #browser = Browser('chrome', chrome_options=options)
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

run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
