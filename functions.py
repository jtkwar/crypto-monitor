# -*- coding: utf-8 -*-
"""
Created on Sun May  1 22:07:14 2022

@author: stark
"""

from packages import *

def send_sms_via_email(
        number: str,
        message: str,
        provider: str,
        sender_credentials: tuple,
        subject: str,
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 465
):
    
    sender_email, email_password = sender_credentials
    receiver_email               = f"{number}@{SMS}"
    email_message = f"Subject:{subject}\nTo:{receiver_email}\n{message}"
    
    with smtplib.SMTP_SSL(
            smtp_server, smtp_port, context=ssl.create_default_context()
    ) as server:
        server.login(sender_email, email_password)
        server.sendmail(sender_email, receiver_email, email_message)

def send_mms_via_email(
    number: str,
    message: str,
    file_path: str,
    mime_maintype: str,
    mime_subtype: str,
    provider: str,
    sender_credentials: tuple,
    subject: str = "sent using etext",
    smtp_server: str = "smtp.gmail.com",
    smtp_port: int = 465,
):

    sender_email, email_password = sender_credentials
    receiver_email = f'{number}@{SMS}'

    email_message=MIMEMultipart()
    email_message["Subject"] = subject
    email_message["From"] = sender_email
    email_message["To"] = receiver_email

    email_message.attach(MIMEText(message, "plain"))

    with open(file_path, "rb") as attachment:
        part = MIMEBase(mime_maintype, mime_subtype)
        part.set_payload(attachment.read())

        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={basename(file_path)}",
        )

        email_message.attach(part)

    text = email_message.as_string()

    with smtplib.SMTP_SSL(
        smtp_server, smtp_port, context=ssl.create_default_context()
    ) as email:
        email.login(sender_email, email_password)
        email.sendmail(sender_email, receiver_email, text)
       

def make_request(url: str
                 
                 ):
    page   = requests.get(url)
    soup   = BeautifulSoup(page.text, "html5lib")
    tables = soup.findAll("table")
    table  = tables[0]
    
    headers = []
    for th in table.find_all("th"):
        headers.append(th.text)
    table_data = []
    for tr in table.tbody.find_all("tr"): # find all tr's from table's tbody
        t_row = {}
        # Each table row is stored in the form of
        # t_row = {'Rank': '', 'Country/Territory': '', 'GDP(US$million)': ''}
    
        # find all td's(3) in tr and zip it with t_header
        for td, th in zip(tr.find_all("td"), headers): 
            t_row[th] = td.text.replace('\n', '').strip()
        table_data.append(t_row)
    return table_data

def make_request_v2(coin:str):
    """
    function that queries coinmarketcap.com for information regarding crypto
    assets currently held.  Returns various stats and prices at time of request.

    Parameters
    ----------
    coin : str
        abbreviation of crypto asset for stats extraction

    Returns
    -------
    out_dict : Dict
        returns dictionary containing:
            name, date, time, spot_price (USD), market_cap (USD),
            undiluted market_cap (USD), 24hr volume (USD),
            Volume/Market Cap Ratio,
            Circulating Supply of asset

    """
    url = urls_dict[coin]
    ts_now = datetime.now()
    date = ts_now.strftime("%Y-%m-%d")
    time = ts_now.strftime("%H:%M:%S")
    page   = requests.get(url)
    soup   = BeautifulSoup(page.text, "html5lib")
    price  = soup.find("div", attrs={"class":"priceValue"})
    stats  = soup.findAll("div", attrs={"class":"statsValue"})
    stats_vals = [x.text.lstrip('$').replace(",", "") for x in stats]
    stats_vals[0:4] = [float(x) for x in stats_vals[0:4]]
    stats_vals[-1] = stats_vals[-1].split(" ")[0]
    if 'B' in stats_vals[-1]:
        stats_vals[-1] = float(stats_vals[-1].rstrip("B"))*1e9
    else:
        stats_vals[-1] = float(stats_vals[-1])
    out_dict = {"coin":coin,
                "date": date,
                "time": time,
                "spot_price_USD": float(price.text.lstrip('$').replace(",","")),
                "mkt_cap_USD": stats_vals[0],
                "undiluted_mkt_cap_USD": stats_vals[1],
                "vol_24hr_USD": stats_vals[2],
                "vol/mkt_cap": stats_vals[3],
                "circ_supply": stats_vals[4]
                }
    return out_dict

def load_assets(filename:str):
    """
    function to load assets .csv file
    converts date to a date object and computes weights of individual
        investment size

    Parameters
    ----------
    filename : str
        name of assets file

    Returns
    -------
    df : pd.DataFrame
        pandas DataFrame object

    """
    df = pd.read_csv(filename)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    tmp = []
    for x in urls_dict.keys():
        tmp_df = df[df['crypto'] == x]
        tmp_df['weights'] = tmp_df['crypto_amount']/tmp_df['crypto_amount'].sum()
        tmp.append(tmp_df)
    return pd.concat(tmp)

def compute_spot_returns(assets_df: pd.DataFrame,
                         prices_df: pd.DataFrame
                         ):
    """
    function to compute some simple stats on performance of crypto investments

    Parameters
    ----------
    assets_df : pd.DataFrame
        assets data
    prices_df : pd.DataFrame
        web-scraped data for current price and other stats

    Returns
    -------
    pd.DataFrame
        output dataframe for all assets and their spot performance stats

    """
    output = []
    for x in urls_dict.keys():
        coin_assets = assets_df[assets_df['crypto'] == x]
        coin_prices = prices_df[prices_df['coin'] == x]
        #print(x)
        #chng = np.round(100*(coin_prices['spot_price_USD'].values[0] - coin_assets['crypto_spot_price_USD'])/coin_prices['spot_price_USD'].values[0],2)
        chng = np.round(100*(coin_prices['spot_price_USD'].values[0] - coin_assets['crypto_spot_price_USD'])/coin_assets['crypto_spot_price_USD'],2)
        num_days = (coin_prices['date'].values[0] - coin_assets['date'])
        num_days = num_days.dt.days
        out_df = pd.DataFrame(list(zip([x]*len(num_days),
                                    [coin_prices['date'].dt.date.values[0]]*len(num_days),
                                    coin_assets['date'].dt.date,
                                    [coin_prices['spot_price_USD'].values[0]]*len(num_days),
                                    coin_assets['crypto_spot_price_USD'],
                                    chng,
                                    num_days,
                                    coin_assets['weights'].round(5))))
        out_df.columns = ['coin',
                          'spot_price_date',
                          'acquisition_date',
                          'spot_price',
                          'acquisition_price',
                          'perc_return',
                          'days_held',
                          'weights'
                          ]
        output.append(out_df)
    return pd.concat(output)

def message_constructor(df:pd.DataFrame):
    s = "\n".join(",".join(map(str, xs)) for xs in df.itertuples(index=False))
    return s