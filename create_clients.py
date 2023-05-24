import random
from datetime import datetime, timedelta

clienti = [    
    ["asap", 1000, "04/01/2022", "06/01/2022"],
    ["metal", 2400, "04/02/2022", "13/02/2022"],
    ["canad", 1700, "06/03/2022", "19/03/2022"],
    ["santox", 4890, "07/04/2022", "20/04/2022"],
    ["prazor", 1600, "08/05/2022", "22/05/2022"],
    ["indian", 1235, "09/06/2022", "17/06/2022"],
    ["gbpsp", 300, "09/07/2022", "29/07/2022"],
    ["canad", 1980, "06/08/2022", "19/08/2022"],
    ["santox", 4890, "07/09/2022", "20/09/2022"],
    ["prazor", 1890, "08/10/2022", "22/10/2022"],
    ["indian", 1054, "09/11/2022", "17/11/2022"],
    ["gbpsp", 3000, "09/12/2022", "29/12/2022"],
]

ordine_format = "{cliente}\t{pezzi_venduti}\t{data_ordine}\t{data_spedizione}"

def genera_ordine_casuale():
    cliente = random.choice(clienti)
    nome, pezzi_venduti, data_ordine, data_spedizione = cliente
    data_ordine = datetime.strptime(data_ordine, "%d/%m/%Y")
    data_spedizione = datetime.strptime(data_spedizione, "%d/%m/%Y")
    delta = (data_spedizione - data_ordine).days
    max_delta = min(delta, 20)  # massimo 20 giorni di differenza
    pezzi_venduti_casuali = "".join(random.sample(str(pezzi_venduti), len(str(pezzi_venduti))))
    data_ordine_casuale = data_ordine + timedelta(days=random.randint(0, max_delta))
    data_spedizione_casuale = data_ordine_casuale + timedelta(days=random.randint(1, max_delta))
    return ordine_format.format(cliente=nome, pezzi_venduti=pezzi_venduti_casuali, data_ordine=data_ordine_casuale.strftime("%d/%m/%Y"), data_spedizione=data_spedizione_casuale.strftime("%d/%m/%Y"))

ordini_casuali = [genera_ordine_casuale() for _ in range(300)]
ordini_casuali_ordinati = sorted(ordini_casuali, key=lambda x: datetime.strptime(x.split("\t")[2], "%d/%m/%Y"))

risultati = []
for ordine in ordini_casuali_ordinati:
    risultati.append(ordine.split('\t'))

for e in risultati:
    date_inizio=e[2]
    print(date_inizio)
print('------------------------------------')
for e in risultati:
    date_inizio=e[3]
    print(date_inizio)
