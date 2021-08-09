import json
import requests
from datetime import datetime
import pandas as pd
import smtplib, ssl
from email.message import EmailMessage
from pprint import pprint
from tabulate import tabulate


print("\n")
capital = 0
capital = input("Enter USDT amount to buy:  ")

if capital == "":
	capital = float(0)
else:
	capital=float(capital)


convert_fee = 0.00075
fut_fee_maker = 0.0001
fut_fee_taker = 0.0005
total_fees_maker = capital * convert_fee * 2 + capital * fut_fee_maker * 2
total_fees_taker = capital * convert_fee * 2 + capital * fut_fee_taker * 2

print("\n")
print("Fees de Future's MAKER: " + str(total_fees_maker))
print("Fees de Future's TAKER: " + str(total_fees_taker))
print("\n")


futuresapi = requests.get('https://dapi.binance.com/dapi/v1/premiumIndex')
futures = json.loads(futuresapi.text)

df = pd.json_normalize(futures)

df = df.drop(columns=['estimatedSettlePrice', 'lastFundingRate', 'interestRate', 'nextFundingTime', 'time', 'pair'])
df['datecode'] = df['symbol'].str[-6:]
df = df[df.datecode.apply(lambda x: x.isnumeric())]

df['days'] = ((pd.to_datetime(df['datecode'], format='%y%m%d')) - (pd.Timestamp('today'))).dt.days
df['markPrice'] = round(pd.to_numeric(df['markPrice']),3)
df['indexPrice'] = round(pd.to_numeric(df['indexPrice']),3)
df['dir_rate'] = round(((df['markPrice'] / df['indexPrice']) - 1) * 100,2)
df['annual_rate'] = round((df['dir_rate'] / df['days']) *365, 2)
df['eff_ann_rate'] = round(( (1 + df['annual_rate'] / 3) * 3 - 1) , 2)
df['dir_ret_Maker'] = round(capital*df['dir_rate']/100-total_fees_maker , 2)
df['dir_ret_Taker'] = round(capital*df['dir_rate']/100-total_fees_taker , 2)

df = df.drop(columns=['datecode'])
df = df.sort_values(by=['annual_rate'], ascending=False)

df_tab = df
#df_tab = df_tab.drop(columns=["dir_ret_Maker","dir_ret_Taker"]) Solo para server que no tiene input
df_tab = tabulate(df_tab, headers='keys', tablefmt='pretty', showindex=False)


print(df_tab)
print("\n")


#CONTRATOS APROXIMANDOSE A TASA CERO
count_neg_rate = 0
symbol_negativo = []
contrato_tasa_negativa = []
for rate,expiration,symbol in zip(df.dir_rate, df.days, df.symbol):
	if rate / expiration < 0.012: # % Tasa directa diaria < 4% Anualizada
		count_neg_rate+=1
		contrato_tasa_negativa.append(symbol)
		symbol_negativo.append(rate)
		 
	else:
		pass

df_pair = pd.DataFrame(list(zip(contrato_tasa_negativa,symbol_negativo)),columns = ["Ticker", "Rate"])


print("Cryptos con tasa aproximandose a cero = " + str(count_neg_rate) + "\n")
if contrato_tasa_negativa == []:
	pass
else:
	print(df_pair)
	print("\n")


# ENVIAR MAIL DE ALERTA TASA NEGATIVA PARA CERRAR SINTETICO AHORA
		
# if count_neg_rate >= 1:
	
# 	sender_email = ""
# 	receiver_email = [""]
# 	password = ""
# 	subject= "Alerta Tasas Sintetico"

# 	msg = EmailMessage()
#	msg.set_content(f"""Contratos con tasa aproximandose a cero: {count_neg_rate} \n \n {df_pair} \n \n \n \n Sinteticos \n\n {df}""") #email body
# 	msg["Subject"] = subject
# 	msg["From"] = 'Alertas Sinteticos <{sender_email}>'
# 	msg["To"] = receiver_email

# 	# Create a secure SSL context
# 	context = ssl.create_default_context()

# 	with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:
#     		smtp.starttls(context=context)
#     		smtp.login(sender_email, password)
#     		smtp.send_message(msg)
#     		print("\n" + 'Email Sent' + "\n")


# GENERAR EXCEL FILE
# timestr = datetime.now().strftime("%Y_%m_%d-%H_%M")
# writer = pd.ExcelWriter('sintetico_'+timestr+'.xlsx')
# df.to_excel(writer)
# writer.save()


