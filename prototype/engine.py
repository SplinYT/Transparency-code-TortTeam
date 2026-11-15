"""ЗакупКонтроль 1.0. Объяснимые эвристики для учебного прототипа."""
import csv, io, json, hashlib
from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation
FIELDS=['id','buyer','supplier','category','published','deadline','initial_price','contract_price','bidders']
RULE_VERSION='1.0'
def analyze(rows):
    if not rows: raise ValueError('Файл не содержит закупок')
    if len(rows)>10000: raise ValueError('Допускается не более 10000 строк')
    clean=[]; ids=set()
    for num,r in enumerate(rows,2):
        if any(not str(r.get(k,'')).strip() for k in FIELDS): raise ValueError(f'Строка {num}: заполните все обязательные поля')
        r={k:str(r[k]).strip() for k in FIELDS}
        if r['id'] in ids: raise ValueError(f'Повтор идентификатора {r["id"]}')
        ids.add(r['id'])
        try:
            a,b=Decimal(r['initial_price']),Decimal(r['contract_price']); n=int(r['bidders'])
            days=(date.fromisoformat(r['deadline'])-date.fromisoformat(r['published'])).days
            if not a.is_finite() or not b.is_finite() or a<=0 or b<0 or b>a or n<1 or days<0: raise ValueError()
        except (ValueError,InvalidOperation): raise ValueError(f'Строка {num}: неверные цены, даты или число участников')
        clean.append((r,a,b,n,days))
    totals=Counter(r['buyer'] for r,*_ in clean)
    pairs=Counter((r['buyer'],r['supplier']) for r,*_ in clean)
    result=[]
    for r,a,b,n,days in clean:
        reasons=[]; score=0
        def add(code,points,text):
            nonlocal score
            score+=points; reasons.append({'code':code,'points':points,'text':text})
        if n==1: add('R1',30,'Один участник: bidders = 1')
        savings=(a-b)/a*100
        if savings<1: add('R2',20,f'Снижение цены {savings:.2f}% меньше 1%')
        if days<=3: add('R3',20,f'Срок подачи {days} календарных дн. не больше 3')
        cnt=pairs[r['buyer'],r['supplier']]; total=totals[r['buyer']]
        if total>=5 and cnt*100>=60*total: add('R4',30,f'Поставщик получил {cnt} из {total} закупок заказчика ({cnt/total:.0%}) в загруженном наборе')
        result.append(dict(r,score=score,reasons=reasons,review=score>=50,savings=float(savings),days=days))
    result.sort(key=lambda r:(-r['score'],r['id']))
    canonical=json.dumps(sorted([r for r,*_ in clean],key=lambda r:r['id']),ensure_ascii=False,sort_keys=True,separators=(',',':'))
    digest=hashlib.sha256((RULE_VERSION+'\n'+canonical).encode()).hexdigest()
    return {'version':RULE_VERSION,'fingerprint':digest,'total':len(result),'review':sum(r['review'] for r in result),'rows':result}
def read_csv(text):
    return list(csv.DictReader(io.StringIO(text.lstrip('\ufeff'))))
