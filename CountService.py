import nltk
nltk.download('brown')
nltk.download('universal_tagset')
import string
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

class CountService:
    def __init__(self):
        super().__init__()
    
    def wordCount(self, article):
        count = 0
        for word in article:
            if word[0] != '<':
                count += 1
        return count
    
    def paragraphCount(self, article):
        wordCount = self.wordCount(article)
        if wordCount != '0':
                count = 1
        else:
            count = 0

        for word in article:
            if word == '<br>':
                count += 1
        return count
    
    def sentenceCount(self, article):
        if self.wordCount(article) == 0:
            return 0
        
        count = 1
        end = False

        for word in article:
            if end == True:
                end = False
                count += 1
            if word[-1] in '.?!' and end == False:
                end = True
            else:
                end = False
        
        return count

    def characterCountNoSpaces(self, article):
        if self.wordCount(article) == 0:
            return 0
        
        count = 0
        words = ""
        for word in article:
            if word[0] != "<":
                words += word
        for c in words:
            count += 1
        return count
    
    def characterCountSpaces(self, article):
        if self.wordCount(article) == 0:
            return 0
        
        count = 0
        words = ""
        for word in article:
            if word[0] != "<":
                words += word + " "
        for c in words:
            count += 1
        count -= 1
        return count
    
    def avgWordsPerSentence(self, article):
        return self.wordCount(article) / self.sentenceCount(article)
    
    def readingTime(self, article):
        wordCount = self.wordCount(article)
        time = wordCount / 200
        return time

    def getType(self, w):
        tagged = nltk.corpus.brown.tagged_words()
        for (word, tag) in tagged:
            if w == word:
                return tag
    
    def findOxfordComma(self, article):
        words_in_article = []
        for word in article:
            if word[-1] in string.punctuation:
                words_in_article.append(word[:-1].lower())
                words_in_article.append(word[-1])
            else:
                words_in_article.append(word.lower())
        
        detectedOxfordComma = []
        isList = False
        previousWord = ""
        phrase = ""
        numItems = 0

        currentIndex = 0
        phraseIndex = 0

        for word in words_in_article:
            if word == "," and isList == False:
                isList = True
                phrase += previousWord + word
                numItems += 1
                phraseIndex = currentIndex - (1 + len(previousWord))
            elif word == "," and isList:
                phrase += word
            elif word == "and" and previousWord == "," and isList:
                phrase += " " + word
            elif word == "and" and previousWord != "," and isList:
                isList = False
                phrase = ""
            elif previousWord == "and" and isList and numItems >= 2:
                isList = False
                phrase += " " + word
                data = {
                    "phrase": phrase,
                    "position": phraseIndex,
                    "length": len(phrase)
                }
                detectedOxfordComma.append(data)
                phrase = ""
                numItems = 0
            elif previousWord == "," and isList:
                phrase += " " + word
                numItems += 1
            else:
                isList = False
                phrase = ""
                numItems = 0
            
            previousWord = word
            currentIndex += len(word) + 1

        return detectedOxfordComma

    def passiveVoiceCount(self, article):
        count = 0
        words_in_article = []
        for word in article:
            if word[-1] in '.?!':
                words_in_article.append(word[:-1].lower())
                words_in_article.append(word[-1])
            else:
                words_in_article.append(word.lower())
        
        passiveWords = ['is', 'am', 'are', 'was', 'to be', 'were', 'being', 'been', 'be']
        tagged = nltk.corpus.brown.tagged_words()
        verbs = [word for (word, tag) in tagged if 'VB' in tag]

        passive = False
        for word in words_in_article:
            if word in '.?!':
                passive = False
            
            elif passive == True and word in verbs:
                passive = False
                count += 1

            elif word in passiveWords:
                passive = True

            else:
                passive = False
        
        return count
    
    def findPassive(self, article):
        words_in_article = []
        for word in article:
            if word[-1] in '.?!':
                words_in_article.append(word[:-1].lower())
                words_in_article.append(word[-1])
            else:
                words_in_article.append(word.lower())
        
        passiveWords = ['is', 'am', 'are', 'was', 'to be', 'were', 'being', 'been', 'be']
        tagged = nltk.corpus.brown.tagged_words()
        verbs = [word for (word, tag) in tagged if 'VB' in tag]

        detectedPhrases = []

        passive = False
        phrase = ""
        currentIndex = 0
        phraseIndex = 0
        for word in words_in_article:
            if word in '.?!':
                passive = False
                phrase = ""
                currentIndex += 1
            
            elif passive == True and word in verbs:
                passive = False
                phrase += word
                data = {
                    "phrase": phrase,
                    "position": phraseIndex,
                    "length": len(phrase)
                }
                detectedPhrases.append(data)
                phrase = ""
                currentIndex += len(word) + 1

            elif word in passiveWords:
                passive = True
                phrase += word + " "
                phraseIndex = currentIndex
                currentIndex += len(word) + 1

            else:
                passive = False
                phrase = ""
                currentIndex += len(word) + 1

        return detectedPhrases

    def authenticate_client(self):
        ta_credential = AzureKeyCredential("904f17729424442cb4e586af6c157a34")
        text_analytics_client = TextAnalyticsClient(
                endpoint="https://swayseast-text-analytics-dev.cognitiveservices.azure.com/", credential=ta_credential)
        return text_analytics_client
    
    def sentimentAnalysis(self, article, client):
        documents = []
        text = ""
        for word in article:
            if word[0] != "<":
                text += word + " "
        text = text[:-1]
        documents.append(text)
        response = client.analyze_sentiment(documents = documents)[0]

        s = []

        for idx, sentence in enumerate(response.sentences):
            sentence_data = {
                "Sentence": format(sentence.text),
                "Sentence Sentiment": format(sentence.sentiment),
                "Sentence Scores": {
                    "positive": format(sentence.confidence_scores.positive),
                    "neutral": format(sentence.confidence_scores.neutral),
                    "negative": format(sentence.confidence_scores.negative)
                }
            }
            s.append(sentence_data)
        
        data = {
            "Document Sentiment:": format(response.sentiment),
            "Overall Scores": {
                "positive": format(response.confidence_scores.positive),
                "neutral": format(response.confidence_scores.neutral),
                "negative": format(response.confidence_scores.negative)
            },
            "Sentence Data": s
        }
        
        return data
    
    def keyPhrase(self, article, client):

        try:
            documents = []
            text = ""
            for word in article:
                if word[0] != "<":
                    text += word + " "
            text = text[:-1]
            documents.append(text)
            
            response = client.extract_key_phrases(documents = documents)[0]

            if not response.is_error:
                phrases = []
                for phrase in response.key_phrases:
                    phrases.append(phrase)
                return phrases
            else:
                return (response.id, response.error)

        except Exception as err:
            data = {
                "Exception": format(err)
            }
            return data
    
    def countKeyPhrases(self, article, phrases):
        words_in_article = []
        for word in article:
            if word[-1] in '.?!,':
                words_in_article.append(word[:-1].lower())
                words_in_article.append(word[-1])
            else:
                if word[0] != '<':
                    words_in_article.append(word.lower())

        p = []

        for phrase in phrases:
            length = self.wordCount(phrase.split())
            count = 0
            
            for i in range(len(words_in_article) - length + 1):
                currentPhrase = ""
                for j in range(length):
                    currentPhrase += words_in_article[i + j] + " "
                currentPhrase = currentPhrase[:-1]

                print('-----------')
                print(phrase, currentPhrase)

                if currentPhrase == phrase.lower():
                    count += 1
            
            p_data = {
                "Phrase": phrase,
                "Count": count
            }
            p.append(p_data)
        
        data = {
            "data": p
        }
        
        return data
