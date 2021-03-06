import csv
count = 0
tweetNum=0
tweets = []
import NLPlib
import sys


print (sys.argv)
tagger = NLPlib.NLPlib()
html = ['&#32', '&#33', '&#34', '&#35', '&#36', '&#37', '&#38', '&#39', '&#40', '&#41', '&#42','&#43', '&#44', '&#45', '&#46', '&#47'  ]
symbols = ['<', '>', '"', '&', '%', '&', '\'', '(', ')', '*', '+', ',', '-', '.', '//']
altHtml = ['&lt;', '&gt;', '&quot;', '&amp;', '&#36', '&#37', '&#38', '&#39', '&#40', '&#41', '&#42','&#43', '&#44', '&#45', '&#46', '&#47'  ]
#helper functions
def check_abbrev(word):
    f = open('/u/cs401/Wordlists/abbrev.english', 'r')
    for line in f:
        if word in line:
            return True
        return False
    f.close()

def punctuation_counter(word):
    count = 0
    for i in word:
        if i == '!' or i == '?' or i == '.':
            count += 1
    return count

def sanitize(text):
    newText = []
    for word in text:
        if word:
            if "www" in word or "http" in word:
                word = ""
            else:
                if word[0] == '@' or word[0] == '#':
                    word = word[1:]
                for i in range (0, 4):
                    a = word
                    word = word.replace(altHtml[i], symbols[i] )
                newText.append(word)
    tags = tagger.tag(newText)
    final = []
    for index in range(0,len(tags)):
         final.append(newText[index]+"/"+tags[index])
    return final


def own_line(text):
    #run through abbrev.english to ensure these don't cause a new line
    #else, whenever coming across an exclamation point, full stop, or question mark, move sentence onto a new line,
    #but if there's multiple don't split, need to be on the same line
    
    newText = []
    for word in text:
        if len(word) > 2:
            if word[-1] == '!' or word[-1] == '?' or word[-1] == '.':
                if check_abbrev(word) == False:
                    newText.append(word)
                    newText.append("\n")
                else:
                    newText.append(word)
            else:
                newText.append(word)
        else:
            newText.append(word)
    return newText 


def punctuation_separator(text):
    #look at last character in word. If it is a piece of punctuation,cycle back and see when
    #the punctuation stops by comparing the next punc to the current punc. Then return the
    #number of pieces of punctuation

    newText = []

    for word in text:
        appended = False

        if "'" in word:
            temp = ["",""]
            temp[0] = word[0:word.find("'")]
            temp[1] = word[word.find("'"):]
            newText.append(temp[0])
            appended = True
            word = temp[1]

        if len(word) > 1:
            if word[-1] == '!' or word[-1] == '?' or word[-1] == '.' or word[-1] == "'":
                temp = ["",""]
                temp[0] = word[:-punctuation_counter(word)]
                temp[1] = word[-punctuation_counter(word):]
                newText.append(temp[0])
                newText.append(temp[1])
                appended = True

        if not appended:
            newText.append(word)

    return newText     

groupID = int(sys.argv[2])
with open(sys.argv[1], 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
        if len(sys.argv) < 5:
            if (count>(groupID*5500) and count<((groupID+1)*5500)):
                tweets.append([row[0], row[5][1:-1]])
                tweetNum+= 1
            if (count>800000 + (groupID*5500) and count<(800000 + (groupID+1)*5500)):
                tweets.append([row[0], row[5][1:-1]])
                tweetNum+= 1
        else:
            tweets.append([row[0], row[5][1:-1]])
            tweetNum+= 1

        count = count + 1
    test = open(sys.argv[3], 'w')
    for tweet in tweets:
        fullSentence = tweet[:]
        tweet[1] = tweet[1].split(" ")
        tweet[1] = own_line(tweet[1])
        tweet[1] = punctuation_separator(tweet[1])
        tweet[1] = sanitize(tweet[1])
        #print(fullSentence)
        test.write("<A="+str(tweet[0])+">\n")
        if tweet[1]:
            if tweet[1][-1] == "\n/NN":
                tweet[1] = tweet[1][:-1]
        for word in tweet[1]:
            if word == "\n/NN":
                word = "\n"
            #Bonus: pretty can also be used as an adjective when it follows a determiner. This will not add
            #new bugs elsewhere, since "pretty" being used as an adjective will only follow "a" or "the". All
            #other instances of "pretty" will therefore be left as adverbs.
            if word == "pretty/RB":
                getIndex = tweet[1].index(word)
                if tweet[1][getIndex-1] == "a/DT" or tweet[1][getIndex-1] == "the/DT" or tweet[1][getIndex-1] == "A/DT" or tweet[1][getIndex-1] == "The/DT":
                    word = "pretty/JJ"
            test.write(word)
            test.write(" ")
        test.write("\n")
    test.close()
    print("done")

