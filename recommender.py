import math
import pandas as pd
import re
from collections import Counter

class DeveloperRecommender:

    vector = None
    iss_titles_and_username_df = None
    pr_unique_titles_and_username_df= None

    def __init__(self,pr_data,isssue_data):

        pr_data['pr_title'] = pr_data['pr_title'].str.lower()
        isssue_data['issue_title'] = isssue_data['issue_title'].str.lower()  
        pr_titles_and_username_df = pr_data.filter(['pr_number','pr_title','user'], axis=1)

        self.iss_titles_and_username_df = isssue_data[isssue_data['closed_at'].notna()][['issue_number','issue_title','user','closed_at']]

        self.pr_unique_titles_and_username_df = pr_titles_and_username_df.drop_duplicates(subset=['pr_number'])



    def get_cosine(self,wordVectorOne, wordVectorTwo):
        intersection = set(wordVectorOne.keys()) & set(wordVectorTwo.keys())
        numerator = sum([wordVectorOne[x] * wordVectorTwo[x] for x in intersection])

        sum_wordVectorOne = sum([wordVectorOne[x] ** 2 for x in list(wordVectorOne.keys())])
        sum_wordVectorTwo = sum([wordVectorTwo[x] ** 2 for x in list(wordVectorTwo.keys())])
        denominator = math.sqrt(sum_wordVectorOne) * math.sqrt(sum_wordVectorTwo)

        if not denominator:
            return 0.0
        else:
            return float(numerator) / denominator


    def text_to_vector(self,text):
        WORD = re.compile(r"\w+")
        words = WORD.findall(text)
        return Counter(words)

    def get_similarity(self,text):
        vector = self.text_to_vector(text)
        return self.get_cosine(vector, self.vector)

    def recommender_developer(self, issue_title):
        self.vector = self.text_to_vector(issue_title)

        self.pr_unique_titles_and_username_df['similarity'] = self.pr_unique_titles_and_username_df['pr_title'].apply(self.get_similarity)

        self.iss_titles_and_username_df['similarity'] = self.iss_titles_and_username_df['issue_title'].apply(self.get_similarity)

        pr_developer_list = self.pr_unique_titles_and_username_df.sort_values('similarity',ascending = False).head(5).filter(['user','similarity'], axis=1)

        issue_developer_list = self.iss_titles_and_username_df.sort_values('similarity',ascending = False).head(5).filter(['user','similarity'], axis=1)

        developer_list = pd.concat([pr_developer_list,issue_developer_list])
        devloper_objs = developer_list.to_dict('records')
        
            
        return devloper_objs




