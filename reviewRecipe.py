import requests
import sys
import json

from alchemyapi import AlchemyAPI
alchemyapi = AlchemyAPI()

def main(sku, maxReviews):
    print "Searching Best Buy for product reviews and performing NLP analysis..."
    pages = (maxReviews/100) + 2
    reviews=[]
    apiKey= open('bestbuy_key.txt', 'r').read().strip()   
    #Call review API for single product
    for page in range(1, pages):
        try:  
            url='http://api.remix.bestbuy.com/v1/reviews(sku=%s)?format=json&pageSize=100&page=%s&apiKey=' % (sku, page) + apiKey  
            response = json.loads(requests.get(url).text)['reviews']
            for review in response:
                reviews.append(review)
        except Exception as e:
            print e
            return
   
    #Process reviews
    eReviews=[]
    reviewId=0
    for review in reviews:
	    fullReview = review['comment'] 
	    eReviews.append({'fullReview': fullReview, 'sentiment': "", 'keywords': [], 'entities': [], 'concepts': []})
	         
	    try:
	        #Sentiment
	        response = alchemyapi.sentiment("text", fullReview)	
	        eReviews[reviewId]['sentiment']=response["docSentiment"]["type"]
	            
	        #Keywords 
	        response = alchemyapi.keywords("text", fullReview)
	        for keyword in response['keywords']:
	            eReviews[reviewId]['keywords'].append(keyword['text'])
	               
	        #Entities
	        response = alchemyapi.entities("text", fullReview)
	        for entity in response['entities']:
	            eReviews[reviewId]['entities'].append(entity['text'])
	                
	        #Concepts
	        response = alchemyapi.concepts("text", fullReview)
	        for concept in response['concepts']:
	            eReviews[reviewId]['concepts'].append(concept['text'])
	            
	   
	    except Exception as e:
	        print e
	    #progress indicator
	    sys.stdout.write(".")
	    sys.stdout.flush()
	    
	    reviewId+=1
	    #exit loop if we've reached the maximum number of reviews
	    if reviewId == maxReviews:
	        break
    
    #Send to file
    toFile(eReviews)


def toFile(eReviews):
    #open all files, one with all results and one each for individual call
    g = open('reviewFullText.csv', 'w')
    s = open('sentiment.csv', 'w')
    k = open('keywords.csv', 'w')
    e = open('entities.csv', 'w')
    c = open('concepts.csv', 'w')
    
    #add headers
    g.write("'Review ID','Review Text','Sentiment','Keywords','Entities','Concepts'\n")
    s.write("'Review ID','Sentiment'\n")
    k.write("'Review ID','Keywords'\n")
    e.write("'Review ID','Entities'\n")
    c.write("'Review ID','Concepts'\n")
    
    #loop through all reviews
    for rId, review in enumerate(eReviews):
        index = str(rId)
        #add ID, full reviews, and sentiment
        g.write((index + ",'" + review['fullReview'] + "','" + review['sentiment'] + "','").encode('utf-8'))
        s.write(index + ",'" + review['sentiment'] + "'\n")
        #add keywords
        for keyword in review['keywords']:
            g.write((keyword + "\n").encode('utf-8'))
            k.write((index + ",'" + keyword + "'\n").encode('utf-8'))
        g.write("','")
        #add entities
        for entity in review['entities']:
            g.write((entity + "\n").encode('utf-8'))
            e.write((index + ",'" + entity + "'\n").encode('utf-8'))
        g.write("','")
        #add concepts
        for concept in review['concepts']:
            g.write(concept + "\n")
            c.write(index + ",'" + concept + "'\n")
        g.write("'\n")
    #close all files
    g.close()
    s.close()
    e.close()
    c.close()
    print "\nAnalysis successful.  Results in reviewFullText.csv, sentiment.csv, keywords.csv, entities.csv, and concepts.csv"
    
if __name__ == "__main__":

    #check for invalid command line input
    if not len(sys.argv) == 3:
        print "ERROR: invalid number of command line arguments"
        print "SYNTAX: python reviewRecipe.py <SKU> <MAX_RESULTS>"
        print "\t<SKU> : SKU for product on Best Buy"
        print "\t<MAX_RESULTS>  : Maximum number of reviews to analyze"
        sys.exit()

    else:
        main(sys.argv[1], int(sys.argv[2]))

