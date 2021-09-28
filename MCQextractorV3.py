import scrapy
from scrapy.crawler import CrawlerProcess
import re
import datetime

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    resultFile = "BPM 2.txt"

    def start_requests(self):
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
            if "gkseries.com" in url:
                yield scrapy.Request(url=url, callback=self.gkseries)


    def QuizExe(self, response):
        self.resultFile = response.url.split('/')[5] + '.txt'
        alphabet = " abcdefghijklmnopqrstuvwxyz"
        questionSections = response.css(".quescontainer")
        for questionSection in questionSections:
            question = questionSection.css(".questionpre::text").extract()[0]
            # import pdb;pdb.set_trace()
            question = question + "<br>" + questionSection.css(' *> pre').get(default="").replace("\n", "<br>")
            options = questionSection.css(".questionpre::text").extract()[1:-1]
            correctOption = questionSection.css(".ans-Div span::text").extract()[1][2]
            correct = alphabet.find(correctOption)
            # print(correct)
            self.writeQuestionN(question,options,correct)

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
            questionEntire = questionSection.css("::text").extract()[0].strip()
            questionEntire = re.sub("\d+\.\s","",questionEntire)
            # options = [re.sub("^[A-Z]\. ","",x.strip()) for x in questionSection.css("::text").extract()[1:-1]]
            options = questionSection.css("::text").extract()[1:]
            options = re.sub("[\t\r\n]","","".join(options))
            Astring = options.split("Answer: Option ")[-1][1].lower()
            options = options.split("Answer: Option ")[:-1][0]
            options = re.split("\[\D\] ",options)[1:] 
            Astring = Astring.lower()
            correct = alphabet.find(Astring)
            self.writeQuestionN(questionEntire.strip(), options, correct)
            
            
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

    def writeQuestionN(self,question,option,correct = 1):
        optionInOne = ""
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

        print(formedLine)
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


35
44
93