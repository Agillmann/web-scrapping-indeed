import click
import requests
import time
from random import randint
from yaspin import yaspin
from bs4 import BeautifulSoup
from pyfiglet import Figlet

f = Figlet(font='slant')
print(f.renderText('Search job indeed.fr'))

BASE_URL = 'https://www.indeed.fr'


@click.command()
@click.option('--search', prompt='What job', help='job you want')
@click.option('--location', prompt='Where', help='job you want')
def scrapping(**kwargs):
    location = kwargs.get('location', None)
    search = kwargs.get('search', None)
    confirm = False
    match = []
    while confirm == False:
        filter = click.prompt(
            'Add filters (Press enter when finished)', default='ok')
        if filter == 'ok':
            confirm = True
            break
        match.append(filter)

    click.clear()
    click.echo('\n---------------------------------------\n')
    click.echo('Search for job : ' + search)
    click.echo('In : ' + location)
    click.echo('With filters : ' + ' '.join(map(str, match)))
    click.echo('\n---------------------------------------\n')
    with yaspin(text='Loading', color='green') as spinner:
        time.sleep(2)
        url_format = BASE_URL + \
            '/emplois?q={0}&l={1}&radius=10&start='.format(
                search.replace(' ', '+'), location)
        match_results = {}
        for i in range(0, 2000, 10):
            page = requests.get(url_format + str(i))
            soup = BeautifulSoup(page.content, 'html.parser')
            results = soup.find(id='resultsCol')
            job_elems = results.find_all('div', class_='result')
            for job_elem in job_elems:
                id_elem = job_elem['id']
                link_elem = job_elem.find('a', class_='jobtitle')
                title_elem = job_elem.find('h2', class_='title')
                company_elem = job_elem.find('span', class_='company')
                location_elem = job_elem.find('span', class_='location')
                if location_elem is None:
                    location_elem = job_elem.find('div', class_='location')
                if None in (title_elem, company_elem, location_elem):
                    continue
                title = title_elem.text.strip().lower()
                if len(match) > 0:
                    for elem in match:
                        if elem in title:
                            match_results[id_elem] = {'title': title_elem.text.strip().upper(),
                                                      'company': company_elem.text.strip(),
                                                      'location': location_elem.text.strip(),
                                                      'link': BASE_URL + link_elem['href']}
                else:
                    match_results[id_elem] = {'title': title_elem.text.strip().upper(),
                                              'company': company_elem.text.strip(),
                                              'location': location_elem.text.strip(),
                                              'link': BASE_URL + link_elem['href']}

        nb_result = len(match_results)
        success = 1
        if success:
            spinner.ok('✔')
        for val in match_results.items():
            click.echo(val[1]['location'])
            click.echo(click.style(val[1]['title'], fg='green'))
            click.echo(click.style(val[1]['company'], fg='blue'))
            click.echo(click.style(val[1]['link'], fg='yellow'))
            click.echo()
        click.echo(click.style('Results: ' + str(nb_result), fg="red"))


if __name__ == '__main__':
    scrapping()
