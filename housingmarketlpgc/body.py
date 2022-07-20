from housingmarketlpgc.gmail import gmail_authenticate, list_messages, get_email_details
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import date


service = gmail_authenticate()

list_messages(service=service, user_id='me', label='Idealista', query='Nuevos anuncios hoy')

#tst = get_email_details(service=service, )

msg_id='18219132b77cc215'


def build_flat_details(msg_id):
    
    body_email = get_email_details(service=service, msg_id=msg_id)

    all_flat_data = [img_tag.get('alt') for img_tag in body_email['body'].find_all('img') if img_tag.get('alt')]

    flat_type = [i.split()[0] for i in all_flat_data]

    price = [int(item.text.strip().replace('.','').replace('€/mes','')) for item in body_email['body'].find_all('span') if not item.text.startswith(' ') and '€/mes' in item.text]

    flat_details = [item.text.strip() for item in body_email['body'].find_all('td') if 'm²' in item.text and '€' not in item.text]

    m_squared = [int(re.findall('\d+', item)[0]) for item in flat_details]

    url = [a['href'].split('/?xts')[0] for a in body_email['body'].find_all('a', href=True) if a.text and 'inmueble' in a['href']]
    url = list(sorted(set(url), key=url.index))

    id = [item.split('/')[-1] for item in url]

    #rooms = [int(re.findall('\d+', item)[1]) for item in flat_details]

    dict_all = {
        'id': id,
        'msg_id': [msg_id] * len(all_flat_data),
        'address': all_flat_data,
        'flat_type': flat_type,
        'price': price,
        'flat_details': flat_details,
        'area': m_squared,
        'url': url,
        'processed_date': [date.today().strftime("%Y-%m-%d")] * len(all_flat_data)
        }

    df = pd.DataFrame.from_dict(dict_all, orient='index').transpose()

    return df




def msgs_to_be_processed(csv_file):
    df = pd.read_csv(csv_file)
    msgs = list_messages(service=service, user_id='me', label='Idealista', query='Nuevos anuncios hoy')


