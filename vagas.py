import os
import time
from splinter import Browser
from bs4 import BeautifulSoup
import urllib.request
import bottle
from bottle import get, response, run
import json

app = bottle.default_app()

'''
UCS
'''

page = urllib.request.urlopen('https://sou.ucs.br/recursos_humanos/cadastro_curriculo/')
soup = BeautifulSoup(page, 'html.parser')
jobs = soup.find_all('li')

def ucs_get_job(job):
    pos_start = job.find('"/>')
    pos_end = job.find('<',pos_start)
    job = job[pos_start+3:pos_end].strip()
    return job

def ucs_get_formation(job):
    pos_reference = job.find('<label>Formação:</label>')
    if pos_reference > 0:
        pos_start = job.find('">', pos_reference)
        pos_end = job.find('</div>', pos_start)
        return job[pos_start+2:pos_end].strip()
    else:
        return '(não informado)'

def ucs_get_locale(job):
    pos_reference = job.find('<label>Localidade:</label>')
    pos_start = job.find('">', pos_reference)
    pos_end = job.find('</div>', pos_start)
    return job[pos_start+2:pos_end].strip()

def ucs_get_turn(job):
    pos_reference = job.find('<label>Turno:</label>')
    pos_start = job.find('">', pos_reference)
    pos_end = job.find('</div>', pos_start)
    return job[pos_start+2:pos_end].strip().replace('\n', '').replace(' ', '').replace(',', ', ')

def ucs_get_description(job):
    pos_ini = job.find('Descrição:')
    pos_ini = job.find('">', pos_ini)
    pos_fin = job.find('</div>', pos_ini)
    return job[pos_ini + 2:pos_fin].replace('\r\n', ' ')

@get('/jobs_ucs')
def get_all_jobs():
    v=[]

    response.headers['Content-Type'] = 'application/json'
    response.headers['Cache-Control'] = 'no-cache'

    for job in jobs:
        job = str(job)
        d = {'vaga': ucs_get_job(job),
             'formacao': ucs_get_formation(job),
             'localidade': ucs_get_locale(job),
             'turno': ucs_get_turn(job),
             'descricao': ucs_get_description(job)}
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

    browser = Browser('firefox', executable_path='PATH')
    browser.visit('http://educacional.ftec.com.br:8080/RM/Rhu-BancoTalentos/#/RM/Rhu-BancoTalentos/painelVagas/lista')
    time.sleep(10)
    soup = BeautifulSoup(browser.html, 'html.parser')

    jobs = []
    for titulo, data, local, desc in zip(ftec_get_names(soup), ftec_get_date_published(soup), ftec_get_place(soup), ftec_get_description(soup)):
        d = {'nome': titulo, 'data': data, 'local': local, 'descricao': desc}
        jobs.append(d)
    browser.quit()

    return json.dumps(jobs)

run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
