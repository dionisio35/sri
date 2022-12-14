from base_model import *


class ProbabilisticModel(Model):

    def __init__(self):
        super().__init__()

        # dictionary with keys as terms and values as lists of documents
        self.term_docs = dict()
        
        # set of terms of the query
        self.queryterms = set()

    	# dictonary with the similarity between the query and documents
        self.query_doc_sim = dict()

        # dictionary with keys as terms and values as the values of p and r for the term
        self.term_p_r = dict()


    def run(self, query: str, dataset: str, threshold: float=None):
        self.clear([self.queryterms, self.query_doc_sim])

        if not self.reuse_data(dataset):
            self.dataset.build_dataset(dataset)
            self.clear([self.term_docs, self.term_p_r])
            self.data()

        return self.find(query, threshold)

    
    def find(self, query: str, threshold: float=None):
        """
        :param query: query to search
        :param documents: list of documents
        :get query: list with query terms
        :return: list of documents sorted by similarity
        """
        self.query_data(query)
        self.sim(False) # computes de similarity
        rank = self.ranking(threshold, self.query_doc_sim) # computes the ranking with the siilarity values

        # Pseudo-feedback
        i = 0

        while i in range(0, 2):
            self.pseudo_feedback_p_r(rank) # computes the values of p and r for all terms based on the relevant recovered documents

            # self.sim_feedback(True, rank) # computes de similarity with new term's p and r values 

            self.sim(True) # compute de similarity with new term's p and r values 

            i = i + 1

            rank = self.ranking(threshold, self.query_doc_sim) # computes the ranking again with the new similarity values

        return rank


    def data(self):
        """
        For each term saves a in a list the document in which it appears
        :param document: document from which the terms will be search analyzed
        :get doc_terms: dictionary in which the terms of the document are saved 
        :get terms_doc: dictionary in which the list of documents that contain the term will be saved
        """    
        for doc in self.dataset.get_docs_data():
            doc_split = self.normalize(doc['text'])

            for term in doc_split:
                self.term_p_r[term] = (0.5, 0)
                
                if not self.term_docs.get(term):
                    self.term_docs[term] = [doc['id']]

                else:
                    if doc not in self.term_docs[term]:
                        self.term_docs[term].append(doc['id'])


    def query_data(self, query: str):
        """
        Saves the query terms in a list
        :param query: the query string
        :get query_terms: list of query terms
        """
        for term in self.normalize_query(query):
            self.queryterms.add(term)


    def sim(self, feedback: bool):
        """
        Computes the similarity between the query and the documents from the collection
        :get query_doc_sim: saves the similarity between the query and a documents
        """
        self.query_doc_sim.clear()

        for term in self.term_docs: # for each term
            r_term = len(self.term_docs[term]) / self.dataset.docslen # term r value

            if feedback is False:                
                self.term_p_r[term] = (0.5, r_term) # safes in the dictionary the value of r for the term and p stays constant (p = 0.5)

            for doc in self.term_docs[term]:                
                if term in self.queryterms: # if the term is a query term                                                                            
                    if not self.query_doc_sim.get(doc): # if it's the first time that the doc has a term in common with the query                             
                        if self.term_p_r[term][0] / (1 - self.term_p_r[term][0]) > 0 and (1 - self.term_p_r[term][1]) / self.term_p_r[term][1] > 0:                       
                            self.query_doc_sim[doc] = np.log10(self.term_p_r[term][0] / (1 - self.term_p_r[term][0])) + np.log10((1 - self.term_p_r[term][1]) / self.term_p_r[term][1]) 

                        else: 
                            self.query_doc_sim[doc] = 0

                    else: # if at least one term has already been found common between the document and the query
                        if self.term_p_r[term][0] / (1 - self.term_p_r[term][0]) > 0 and (1 - self.term_p_r[term][1]) / self.term_p_r[term][1] > 0:
                           self.query_doc_sim[doc] = self.query_doc_sim[doc] + np.log10(self.term_p_r[term][0] / (1 - self.term_p_r[term][0])) + np.log10((1 - self.term_p_r[term][1]) / self.term_p_r[term][1]) 

                else: # if the term in the document isn't a query term                                  
                    if not self.query_doc_sim.get(doc):
                        self.query_doc_sim[doc] = 0 
        
        # Normalize similarity values
        max = 0
        for doc in self.query_doc_sim:
            if self.query_doc_sim[doc] > max:
                max = self.query_doc_sim[doc]
        
        if max != 0:
            for doc in self.query_doc_sim:
                self.query_doc_sim[doc] = self.query_doc_sim[doc] / max
            	

    def pseudo_feedback_p_r(self, rank: list):
        """"
        Computes the term's p (probability of a term appearing in a document relevant to the query) 
        and r (probability of a term appearing in a nonrelevant document) values
        """

        rr_doc = len(rank) # number of relevant recovered documents

        for term in self.term_docs:
            v_term = self.count_recov_with_term(term, rank)

            p_term = (v_term + 0.5) / (rr_doc + 1)

            r_term = (len(self.term_docs[term]) - v_term + 0.5) / (self.dataset.docslen - rr_doc + 1)

            self.term_p_r[term] = (p_term, r_term)


    def count_recov_with_term(self, term: str, rank: list):
        """
        Computes the number of relevant documents in which "term" appears
        """

        v_term = 0

        for doc in self.term_docs[term]:
            if doc in rank:
                v_term = v_term + 1

        return v_term

    # def sim_1(self, feedback: bool):
    #     """
    #     Computes the similarity between the query and the documents from the collection
    #     takes as a constant value p_i = 0.5
    #     :get query_doc_sim: saves the similarity between the query and a documents
    #     """
    #     self.query_doc_sim.clear()

    #     for term in self.term_docs: # for each term

    #         for doc in self.term_docs[term]: # for each doc in which the term apppears
    #             if term in self.queryterms: # if the term is a query term                                                    
    #                 if not self.query_doc_sim.get(doc): # if it's the first time that the doc has a term in common with the query                             
    #                     self.query_doc_sim[doc] = np.log10(self.dataset.docslen / len(self.term_docs[term]))
    #                 else: # if at least one term has already been found common between the document and the query
    #                     # if self.term_p_r[term][1] > 0 and self.term_p_r[term][0] > 0: # if the values don't indetermine the log function
    #                     self.query_doc_sim[doc] = self.query_doc_sim[doc] + np.log10(self.dataset.docslen / len(self.term_docs[term])) # sum the similarity already saved from the others terms that coincide in the document and the query 
                
    #             else: # if the term in the document isn't a query term     
    #                 if not self.query_doc_sim.get(doc): # if the document hasn't been analyzed   
    #                     self.query_doc_sim[doc] = 0 # the current similarity between the doc and the query is 0
    
    #     # Normalize similarity values
    #     max = 0
    #     for doc in self.query_doc_sim:
    #         if self.query_doc_sim[doc] > max:
    #             max = self.query_doc_sim[doc]
       
    #     if max != 0:
    #         for doc in self.query_doc_sim:
    #             self.query_doc_sim[doc] = self.query_doc_sim[doc] / max

    # def sim_feedback(self, feedback: bool, rank: list):
    #     """
    #     Computes the similarity between the query and the documents from the collection
    #     takes as a constant value p_i = 0.5
    #     :get query_doc_sim: saves the similarity between the query and a documents
    #     """
    #     v = len(rank)

    #     self.query_doc_sim.clear()

    #     for term in self.term_docs: # for each term
    #         v_t = self.count_recov_with_term(term, rank)

    #         r_term = len(self.term_docs[term]) / self.dataset.docslen # term r value

    #         # if feedback is False:                
    #         #     self.term_p_r[term] = (0.5, r_term) # safes in the dictionary the value of r for the term and p stays constant (p = 0.5)

    #         for doc in self.term_docs[term]: # for each doc in which the term apppears
    #             if term in self.queryterms: # if the term is a query term                                                    
    #                 if not self.query_doc_sim.get(doc): # if it's the first time that the doc has a term in common with the query                             
    #                     self.query_doc_sim[doc] = np.log10((v_t + 1/2) / (v - v_t + 1)) + np.log10(self.dataset.docslen / len(self.term_docs[term]))
    #                 else: # if at least one term has already been found common between the document and the query
    #                     # if self.term_p_r[term][1] > 0 and self.term_p_r[term][0] > 0: # if the values don't indetermine the log function
    #                     self.query_doc_sim[doc] = self.query_doc_sim[doc] + np.log10((v_t + 1/2) / (v - v_t + 1)) + np.log10(self.dataset.docslen / len(self.term_docs[term])) # sum the similarity already saved from the others terms that coincide in the document and the query 
                
    #             else: # if the term in the document isn't a query term     
    #                 if not self.query_doc_sim.get(doc): # if the document hasn't been analyzed   
    #                     self.query_doc_sim[doc] = 0 # the current similarity between the doc and the query is 0
    
    #     # Normalize similarity values
    #     max = 0
    #     for doc in self.query_doc_sim:
    #         if self.query_doc_sim[doc] > max:
    #             max = self.query_doc_sim[doc]
       
    #     if max != 0:
    #         for doc in self.query_doc_sim:
    #             self.query_doc_sim[doc] = self.query_doc_sim[doc] / max
        