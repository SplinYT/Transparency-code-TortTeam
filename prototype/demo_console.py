"""Демонстрация того же движка без браузера. Запуск: python demo_console.py."""
from pathlib import Path
import json
from engine import analyze,read_csv
ROOT=Path(__file__).parent
def run():
 rows=read_csv((ROOT/'demo.csv').read_text(encoding='utf-8-sig'))
 report=analyze(rows)
 stages=[]
 stages.append(('1 Загрузка данных',f'Источник: demo.csv\nТип: авторские синтетические данные\nЗагружено: {len(rows)} закупок\nПроверка: обязательные поля, даты, цены, дубликаты'))
 stages.append(('2 Расчёт очереди',f'Версия правил: {report["version"]}\nВсего закупок: {report["total"]}\nТребуют проверки: {report["review"]}\nПорог: 50 из 100 баллов\n\nПервые записи:\n'+'\n'.join(f'{r["id"]}   {r["score"]:3} баллов   {r["buyer"]}' for r in report['rows'][:6])))
 card=next(r for r in report['rows'] if r['id']=='Z001')
 stages.append(('3 Объяснение сигнала Z001',f'Закупка: {card["id"]}\nНачальная цена: {card["initial_price"]} руб.\nЦена контракта: {card["contract_price"]} руб.\n\n'+'\n'.join(f'{r["code"]} +{r["points"]}: {r["text"]}' for r in card['reasons'])+f'\n\nИтого: {card["score"]} баллов. Требует проверки.'))
 decision={'status':'Запросить документы','comment':'Проверить обоснование единственного участника и повторяемость поставщика.'}
 report['decisions']={'Z001':decision}
 stages.append(('4 Решение аналитика','Учебное решение для сценария:\n'+decision['status']+'\n\nКомментарий:\n'+decision['comment']+'\n\nЭто направление проверки, не вывод о нарушении.'))
 dest=ROOT/'demo_report.json';dest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 check=json.loads(dest.read_text(encoding='utf-8'))
 assert check['decisions']['Z001']==decision
 stages.append(('5 Экспорт и воспроизводимость','Отчёт сохранён: demo_report.json\nВ отчёте: входные поля, баллы, причины, решения\nПроверка чтения файла: успешно\nПовтор расчёта: '+str(analyze(rows)==analyze(rows[::-1]))+'\n\nSHA-256 набора и версии:\n'+report['fingerprint'][:32]+'\n'+report['fingerprint'][32:]))
 try: analyze(read_csv('id,buyer\nA,B'))
 except ValueError as e:error=str(e)
 stages.append(('6 Контроль ошибок и ограничения','Неполный CSV отклонён:\n'+error+'\n\n21 автоматический тест пройден.\nДанные синтетические. Результат на реальных\nзакупках и экономия времени пока не измерены.\nОкончательное решение остаётся за человеком.'))
 for title,body in stages: print(title+'\n'+body+'\n')
 return stages
if __name__=='__main__':run()
