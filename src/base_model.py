from utils import *
from dataset import Datasets
from stopwords import Stopwords


class Model:
    def __init__(self):
        self.stopwords= Stopwords('english')
        self.dataset= Datasets()

    def run(): ...

    def compare_datasets(self, dataset:str):
        """
        Compare the documents with the set of documents
        :param documents: list of documents
        :get documents: set of documents
        :return: True if the documents are the same, False if not
        """
        if self.dataset.dataset_name == dataset:
            return True
        return False
    
    def clean_query_data(self):
        """
        Clean the query data
        :get queryterms: empty dictionary to store query terms and their weight
        :get querysim: empty dictionary to store documents and their similarity
        """
        self.queryterms.clear()
        self.querysim.clear()

    def get_split_terms(self, document:str):
        """
        Get the terms of the document that are not stopwords and store it in a list
        :param document: document to split
        :return: list of terms
        """
        doc= split_words(document)
        return self.stopwords.not_stopwords_terms(doc)