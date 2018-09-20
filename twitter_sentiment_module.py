import pickle

classifier_f = open("final_model.pickle", "rb")
MyVotingClassifier = pickle.load(classifier_f)
classifier_f.close()

def sentiment(tweet):
    sentiment_polarity = MyVotingClassifier.predict([tweet])
    return sentiment_polarity
