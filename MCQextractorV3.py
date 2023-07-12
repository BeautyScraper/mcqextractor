from pathlib import Path
import scrapy
from scrapy.crawler import CrawlerProcess
import re
import datetime
import pandas as pd

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    resultFile = "Containers.csv"

    def start_requests(self):
        self.df = pd.DataFrame(columns = ['questionname', 'questiontext', 	'A', 'B', 'C', 'D', 'Answer 1', 	'Answer 2'])
        urls = [
"https://iqsanswers.com/bioinformatics-multiple-choice-questions-and-answers/"
        ]
        with open("URL.txt") as fpo:
                urls = fpo.readlines()
        for url in urls:
            url = url.strip()
            sqaureP = re.search("@\[(.*)\]", url)
            if sqaureP != None:
                # lb, ub = [int(x) for x in sqaureP[1].split(",")]
                lb, ub = [int(x) for x in re.split("[-,]",sqaureP[1])]
                NewUrls = [url.replace(sqaureP[0],str(ui)) for ui in range(lb,ub)]
                [urls.append(NewUrl) for NewUrl in NewUrls]
                # urls.append(NewUrls)
                continue
            
            if "compscibits" in url or "compsciedu.com" in url:
                yield scrapy.Request(url=url, callback=self.QuizExe)

            if "examveda" in url:
                yield scrapy.Request(url=url, callback=self.examveda)
            if "sanfoundry" in url:
                yield scrapy.Request(url=url, callback=self.sanfoundry)

            if "iqsanswers.com" in url:
                yield scrapy.Request(url=url, callback=self.iqsanswers)
            if "careericons.com" in url:
                yield scrapy.Request(url=url, callback=self.careericons)
            if "gkseries.com" in url:
                yield scrapy.Request(url=url, callback=self.gkseries)
            if "mcqpoint.com" in url:
                yield scrapy.Request(url=url, callback=self.mcqpoint)
            if "r4r" in url:
                yield scrapy.Request(url=url, callback=self.r4r)

    def careericons(self,response):
        '''https://mcqpoint.com/mcq/animation/'''
        resultFile = 'careericons.txt'
        alphabet = " abcdefghijklmnopqrstuvwxyz"
        questionSections = response.css('div.panel.panel-white')
        for questionSection in questionSections:
            if len(questionSection.css('.ft_sz_20.text-justify::text').extract()) <= 0:
                continue
                # breakpoint()
            question = questionSection.css('.ft_sz_20.text-justify::text').extract()[0]
            options = questionSection.css('.ft_sz_18::text').extract()
            options = [re.search('\w\) (.*)$',x)[1] for x in options]
            correctOption =  re.search('\((\w)\)', questionSection.css('.ft_sz_20>p').extract()[0])[1]
            correct = alphabet.find(correctOption)
            self.writeQuestionN(question,options,correct)
        
    def QuizExe(self, response):
        # self.resultFile = response.url.split('/')[5] + '.csv'
        self.resultFile = 'Quiz.csv'
        alphabet = " abcdefghijklmnopqrstuvwxyz"
        questionSections = response.css(".quescontainer")
        for questionSection in questionSections:
            if len(questionSection.css("img::attr(src)").extract()) >= 1:
                continue
            question = questionSection.css(".questionpre::text").extract()[0]
            # import pdb;pdb.set_trace()
            question = question +  questionSection.css(' *> pre').get(default="").replace("\n", "<br>")
            options = questionSection.css(".questionpre::text").extract()[1:-1]
            correctOption = questionSection.css(".ans-Div span::text").extract()[1][2]
            correct = alphabet.find(correctOption)
            # print(correct)
            # self.writeQuestionN(question,options,correct)
            self.newLMS(question,options,correct)
        self.df.to_csv(self.resultFile,index=False)

    def r4r(self, response):
        # self.resultFile = response.url.split('/')[5] + '.txt'
        question = response.xpath("//pre//text()").get().strip()
        options = []
        correct_g = response.xpath("//p[starts-with(@id,'ans')]/text()").get()
        correct = int(re.search('(?<=:)\d+',correct_g)[0])
        for i in range(1,5):
            options.append(response.xpath("//p[starts-with(text(),%s)]//text()" % str(i)).get())
            # print(correct)
        self.writeQuestionN(question,options,correct)
            
    def mcqpoint(self,response):
        for question_div in response.css('div.question'):
            question = question_div.css('h3::text').get()
            optionall = question_div.css('ul.options>li:nth-child(1n+0)::text').getall()
            opt = [x.strip() for x in optionall if re.search('\w+',x)]
            correct = opt.index(question_div.css('.answer::text').getall()[-1].strip()) + 1
            question = re.sub('^\d+\.', '', question).strip()
            self.writeQuestionN(question,opt,correct)
            # import pdb;pdb.set_trace()
            # count = 1
            # for i, opt in enumerate(options_elm):
            #     if 



    def examveda(self,response):
        questionSections = response.css(".question.single-question.question-type-normal")
        for questionSection in questionSections:
            if (questionSection.css(".row") != []):
                questionEntireA = questionSection.css(".question-main::text").extract()
                questionEntire = " ".join(questionEntireA)
                if(questionSection.css("code") != []):
                    questionEntire += questionSection.css("code").extract()[0]
                questionEntire = questionEntire.replace("\n", "<br>").replace('class="p-blue"','style="color:blue;"').replace('class="p-red"','style="color:red;"').replace('class="p-green"','style="color:green;"')
                options = questionSection.css(".question-inner p label:nth-last-child(1)::text").extract()
                correct = int(questionSection.css(".question-inner p input::attr(value)").extract()[0])



                questionEntire = questionEntire.replace("’","'")
                self.writeQuestion(questionEntire, options, correct)

    def iqsanswers(self, response):
        alphabet = " abcdefghijklmnopqrstuvwxyz"
        questionSections =  response.css("div.entry-content>p")
        for questionSection in questionSections:
            questionEntire = questionSection.css("::text").extract()[0]
            questionEntire = re.sub("\d+\.\s","",questionEntire)
            # options = [re.sub("^[A-Z]\. ","",x.strip()) for x in questionSection.css("::text").extract()[1:-1]]
            options = [x.strip()[3:] for x in questionSection.css("::text").extract()[1:-1]]
            Astring = questionSection.css("::text").extract()[-1][-1]
            Astring = Astring.lower()
            correct = alphabet.find(Astring)
            self.writeQuestionN(questionEntire.strip(), options, correct)
            
    def gkseries(self, response):
        alphabet = " abcdefghijklmnopqrstuvwxyz"
        questionSections =  response.css("div.mcq")
        for questionSection in questionSections:
            questionEntire = questionSection.css("::text").extract()[3].strip()
            questionEntire = re.sub("\d+\.\s","",questionEntire)
            # options = [re.sub("^[A-Z]\. ","",x.strip()) for x in questionSection.css("::text").extract()[1:-1]]
            options = questionSection.css("::text").extract()[4:]
            opt2 = questionSection.css("::text").extract()[4:]
            opt2 = [x for x in opt2 if x.replace('\n','').replace(' ','') != ''][:-3]
            opt2 = [x.strip() for i,x in enumerate(opt2) if i%2 == 1]
            # breakpoint()
            options = re.sub("[\t\r\n]","","".join(options))
            Astring = options.split("Answer: Option ")[-1][1].lower()
            options = options.split("Answer: Option ")[:-1][0]
            options = re.split("\[\D\] ",options)[1:] 
            Astring = Astring.lower()
            correct = alphabet.find(Astring)
            self.writeQuestionN(questionEntire.strip(), opt2, correct)
            
            
    def sanfoundry(self,response):
        alphabet = " abcdefghijklmnopqrstuvwxyz"
        questionSections = response.css(".entry-content").css("p")[1:]
        i = 0
        for questionSection in questionSections:
            if(questionSection.css("p::text").extract()):
                question = questionSection.css("p::text").extract()[0]
                question = re.sub("[0-9]*\. ","",question)
            else:
                return
            choicesRaw = "".join(questionSection.css("p::text").extract()[1:-1])
            options = (re.sub("\n.\) ", "@@", choicesRaw)).split("@@")[1:]
            print(response.css(".collapseomatic_content::text").extract()[i][-1])
            correct = alphabet.find(response.css(".collapseomatic_content::text").extract()[i][-1])

            i += 2
            self.writeQuestion(question, options, correct)

    def correctify(self, formedLine):
        if "\n" in formedLine.rstrip('\n'):
            return 
        formedLine = formedLine.replace("….","...")
        formedLine = formedLine.replace("”",'"').replace("“",'"')
        formedLine = formedLine.replace("‘","'").replace("’","'")
        formedLine = formedLine.replace("‘","'")
        ReplaceChareterList = [('→','->'),('←','<-'),('×','x'),('–','-'),('Ф','phi'),('—','-'),
        ('´','\''),('…','...'),('−','-'),('Σ','Sigma'),('\xa0',' '),('′',"'"),('«','<<'),('»','>>'),('≤','<=')]
        for x in ReplaceChareterList:
            formedLine = formedLine.replace(x[0],x[1])
        print(formedLine)
        if not formedLine.isascii():
            lst_of_non_reco = [x for x in formedLine if not x.isascii()]
            print(lst_of_non_reco)
            a = input('enter i to ignore this line and other charectar to replace')
            if a == 'i':
                return
            else:
               formedLine = formedLine.replace(lst_of_non_reco[0], a)
        return formedLine


    def newLMS(self,question,option,correct = 1):
        optionInOne = ""
        if "</code>" in question:
            return 
        if option == []:
            return 
        alphabet = " abcdefghijklmnopqrstuvwxyz".upper()

        # optionInOne = "\tincorrect\t".join(option) + "\tincorrect"
        # optionInOne = self.nth_repl(optionInOne,"\tincorrect\t","\tcorrect\t",correct)
        # optionInOne = optionInOne.replace("’","'")
        # sep = ';'
        # formedLine = sep.join([question,question,*option, alphabet[correct]])+'\n'
        # formedLine = "\t%s\t%s\n" % (question,question,*option)
        new_row = [question,question,*option, alphabet[correct],""]
        new_row = list(map(self.correctify, new_row))
        if None in new_row or len(new_row) != 8:
            return
        self.df.loc[len(self.df)] = new_row

    def writeQuestionN(self,question,option,correct = 1):
        optionInOne = ""
        if "</code>" in question:
            return 
        if option == []:
            return 
        for t,o in enumerate(option):
            if (t == correct - 1):
                optionInOne = optionInOne + "\t" + o + "\tcorrect"
            else:
                optionInOne = optionInOne + "\t" + o + "\tincorrect"
        # optionInOne = "\tincorrect\t".join(option) + "\tincorrect"
        # optionInOne = self.nth_repl(optionInOne,"\tincorrect\t","\tcorrect\t",correct)
        # optionInOne = optionInOne.replace("’","'")
        formedLine = "MC\t%s\t%s\n" % (question,optionInOne)
        formedLine = formedLine.replace("….","...")
        formedLine = formedLine.replace("”",'"').replace("“",'"')
        formedLine = formedLine.replace("‘","'").replace("’","'")
        formedLine = formedLine.replace("‘","'")
        ReplaceChareterList = [('→','->'),('←','<-'),('×','x'),('–','-'),('Ф','phi'),('—','-'),
        ('´','\''),('…','...'),('−','-'),('Σ','Sigma'),('\xa0',' '),('′',"'"),('«','<<'),('»','>>'),('≤','<=')]
        for x in ReplaceChareterList:
            formedLine = formedLine.replace(x[0],x[1])
        print(formedLine)
        if not formedLine.isascii():
            lst_of_non_reco = [x for x in formedLine if not x.isascii()]
            print(lst_of_non_reco)
            a = input('enter i to ignore this line and other charectar to replace')
            if a == 'i':
                return
            else:
               formedLine = formedLine.replace(lst_of_non_reco[0], a)
            
        
        with open(self.resultFile, "a+", encoding='utf-8') as fp:
            fp.write(formedLine)



    def writeQuestion(self,question,option,correct = 1):
        optionInOne = "\tincorrect\t".join(option) + "\tincorrect"
        optionInOne = self.nth_repl(optionInOne,"\tincorrect\t","\tcorrect\t",correct)
        optionInOne = optionInOne.replace("’","'")
        formedLine = "MC\t%s\t%s\n" % (question,optionInOne)
        formedLine = formedLine.replace("….","...")
        formedLine = formedLine.replace("”",'"').replace("“",'"')

        print(formedLine)
        with open(self.resultFile, "a+", encoding='utf-8') as fp:
            fp.write(formedLine)

    def nth_repl(self,s, sub, repl, nth):
        find = s.find(sub)
        # if find is not p1 we have found at least one match for the substring
        i = find != -1
        # loop util we find the nth or we find no match
        while find != -1 and i != nth:
            # find + 1 means we start at the last match start index + 1
            find = s.find(sub, find + 1)
            i += 1
        # if i  is equal to nth we found nth matches so replace
        if i == nth:
            return s[:find] + repl + s[find + len(sub):]
        return s

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

process.crawl(QuotesSpider)
process.start()

