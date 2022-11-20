from utils import *
from dataset import Datasets
from stopwords import Stopwords
from base_model import Model


#TODO: make data sets
#TODO: update visual
#TODO: make documentation
#TODO: First process and save the document data, then just fetch the query
#TODO: reuse dataset
class VectorModel(Model):
    def __init__(self):
        """
        :param stopwords: list of stopwords
        :param docterms: dictionary with terms and their frequency, tf, idf and w
        :param queryterms: dictionary with query terms and their weight
        :param querysim: dictionary with documents and their similarity
        """
        super().__init__()
        # dictionary with keys as terms and values as a dictionary with keys as documents and values as a dictionary with keys as freq, tf, idf and w
        # {terms: {docs: {freq, tf, idf, w}}}
        self.docterms= dict()
        # dictionary with keys as query terms and values as their weight
        self.queryterms= dict()
        # dictionary with keys as documents and values as their similarity
        self.querysim= dict()
        # list of stopwords
        


    def run(self, query:str, dataset:str, limit:int= None, umbral:float= None, alpha:float=0.5, sensitive:bool= False):
        """
        Do the search of the query in the given dataset
        :param query: query to search
        :param dataset: dataset name
        :param limit: limit of documents to return
        :param umbral: similarity umbral
        :param alpha: alpha value for the similarity calculation of the query
        :param sensitive: if the query is case sensitive
        :return: ranked list of documents
        """
        self.clean_query_data()
        if not self.compare_datasets(dataset):
            self.docs_data(dataset, sensitive)
        return self.find(query, limit, umbral, alpha, sensitive)


    def docs_data(self, dataset:str, sensitive:bool= False):
        self.dataset.get_dataset(dataset)
        self.__docterms_data(sensitive)


    def find(self, query:str, limit:int= None, umbral:float= None, alpha:float=0.5, sensitive:bool= False):
        """
        :param query: query to search
        :param documents: list of documents
        :get docterms: dictionary with terms and their frequency, tf, idf and w
        :get queryterms: dictionary with query terms and their weight
        :get querysim: dictionary with documents and their similarity
        :return: list of documents sorted by similarity
        """
        if sensitive:
            self.__query_data(query, alpha)
        else:
            self.__query_data(query.lower(), alpha)
        self.__sim()
        rank= self.__ranking(limit, umbral)
        
        return rank
    
    
    def __ranking(self, limit:int, umbral:float):
        """
        Sort the documents by similarity and return the list based on the restrictions
        :get querysim: dictionary with documents and their similarity
        :return: list of documents sorted by similarity
        """
        new_querysim= dict()
        for doc in self.querysim:
            if self.querysim[doc] != 0:
                new_querysim[doc]= self.querysim[doc]
        self.querysim= new_querysim

        rank= sorted(self.querysim.items(), key=lambda x: x[1], reverse=True)
        if umbral != None:
            rank= self.__umbral(rank, umbral)
        if limit != None:
            rank= rank[:limit]
        return rank

    def __umbral(self, rank:list, umbral:float):
        """
        Filter the documents by the similarity using the umbral
        :param rank: list of documents sorted by similarity
        :param umbral: similarity umbral
        :return: list of documents that pass the umbral
        """
        newrank= []
        for doc in rank:
            if doc[1] >= umbral:
                newrank.append(doc)
        return newrank
    
    def __sim(self):
        """
        Calculate the similarity between the query and the documents and store it in the querysim dictionary
        :get queryterms: dictionary with query terms and their weight
        :get docterms: dictionary with terms and their frequency, tf, idf and w
        :get querysim: empty dictionary to store documents and their similarity
        :return: dictionary with documents and their similarity"""

        sim= dict()
        aux= dict()
        for term in self.docterms:
            if term in self.queryterms:
                aux[term]= self.queryterms[term]
            else:
                aux[term]= 0

        for term in aux:
            for doc in self.docterms[term]:
                if sim.get(doc) == None:
                    sim[doc]= {'wiq2': pow(aux[term], 2), 'wij2': pow(self.docterms[term][doc]['w'], 2), 'wijxwiq': aux[term] * self.docterms[term][doc]['w']}
                else:
                    sim[doc]['wiq2'] += pow(aux[term], 2)
                    sim[doc]['wij2'] += pow(self.docterms[term][doc]['w'], 2)
                    sim[doc]['wijxwiq'] += aux[term] * self.docterms[term][doc]['w']
        for doc in sim:
            if pow(sim[doc]['wiq2'], 1/2) * pow(sim[doc]['wij2'], 1/2) != 0:
                self.querysim[doc] = round(sim[doc]['wijxwiq'] / ( pow(sim[doc]['wiq2'], 1/2) * pow(sim[doc]['wij2'], 1/2) ), 3)
            else:
                self.querysim[doc]= 0


    def __query_data(self, query:str, alpha:float):
        """
        Calculate the weight of the query terms and store it in the queryterms dictionary
        :param query: query to search
        :get queryterms: empty dictionary to store terms and their weight
        :param alpha: parameter to calculate w
        :return: dictionary with the query terms and their weight
        """
        terms= self.__get_query_terms_docs(query)
        terms_count= self.__get_count(terms)
        max= self.__get_max_count(terms_count)
        
        for term in terms_count:
            idf= 0
            for freq in self.docterms[term].values():
                idf= freq['idf']
            if max != 0:
                self.queryterms[term] = (alpha + (1 - alpha) * ((terms_count[term])/(max)))*idf
            else:
                self.queryterms[term] = 0
        return self.queryterms
    
    
    def __get_query_terms_docs(self, query:str):
        """
        Get the terms of the query and store it in a list
        :param query: query to search
        :return: list of terms
        """
        terms= []
        for term in self.get_split_terms(query):
            if self.docterms.get(term) != None:
                terms.append(term)
        return terms


    def __docterms_data(self, sensitive:bool):
        """
        Calculate the frequency, tf, idf and w of the terms in the documents and store it in the docterms dictionary
        :param documents: list of documents
        :get docterms: empty dictionary to store terms and their frequency, tf, idf and w
        :param sensitive: boolean to know if the search is sensitive or not
        """
        for doc in self.dataset.get_docs_data():
            if sensitive:
                terms_freq= self.__get_count(self.get_split_terms(doc['text']))
            else:
                terms_freq= self.__get_count(self.get_split_terms(doc['text'].lower()))
            
            max= self.__get_max_count(terms_freq)
            
            for term in terms_freq:
                if self.docterms.get(term) == None:
                    self.docterms[term] = {doc['id']:{'freq':terms_freq[term], 'tf':terms_freq[term]/max, 'idf':0, 'w':0}}
                else:
                    self.docterms[term][doc['id']] = {'freq':terms_freq[term], 'tf':terms_freq[term]/max, 'idf':0, 'w':0}
            
        for term in self.docterms:
            for doc in self.docterms[term]:
                self.docterms[term][doc]['idf'] = log(self.dataset.docslen / len(self.docterms[term]), 10)
                self.docterms[term][doc]['w'] = self.docterms[term][doc]['tf'] * self.docterms[term][doc]['idf']
    

    def __get_count(self, elements:list):
        """
        Get the frequency of the terms in the query and store it in a dictionary of key as term and value as frequency
        :param terms: list of terms
        :return: dictionary with terms and their frequency
        """
        count= dict()
        for element in elements:
            count[element]= elements.count(element)
        return count
    

    def __get_max_count(self, count:dict):
        """
        Get the max frequency of the terms in the query
        :param count: dictionary with terms and their frequency
        :return: max frequency
        """
        max=0
        for term in count:
            if max < count[term]:
                max = count[term]
        return max
