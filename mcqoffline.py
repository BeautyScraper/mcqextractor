from MCQextractorV3 import QuotesSpider
import re
x = QuotesSpider()
x.resultFile = "new.txt"

filename = 'mcq.txt'

with open(filename,'r') as fp:
    fc = fp.read()
    alphabet = " abcdefghijklmnopqrstuvwxyz"
    
    for question_sec in fc.split('@@'):
        # breakpoint()
        try:
            question = re.sub('\d+\. ','',question_sec.split('?')[0])
            options = [x.strip() for x in re.split('\w\)',question_sec.split('?')[1].split('Answer:')[0])[1:]]
            correct = alphabet.find(re.search('\((\w)\)',question_sec.split('?')[1].split('Answer:')[-1])[1])
            x.writeQuestionN(question, options, correct)
        except:
            continue