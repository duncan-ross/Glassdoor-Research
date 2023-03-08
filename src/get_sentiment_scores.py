import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from helpers import json_data
from definitions import WRITTEN_REVIEW_TOKENS

class SentimentAnalysis():
    def __init__(self, data) -> None:
        self.analyzer = SentimentIntensityAnalyzer()
        self.data = data
        pass

    def tokenize_text(self, text):
        return text.lower().split(".")

    def tokenize(self, company):
        reviews = self.data[company]
        for review in reviews:
            if review == "PAGE_FAILURE":
                continue
            for key in WRITTEN_REVIEW_TOKENS:
                try:
                    if review[key] is not None:
                        tokenized_text = self.tokenize_text(review[key])
                    else:
                        tokenized_text = []
                except TypeError:
                    print("TypeError: {}".format(review))
                    raise SystemExit
                review[key] = tokenized_text
        return
    
    def analyze(self, company):
        reviews = self.data[company]
        for review in reviews:
            if review == "PAGE_FAILURE":
                continue
            for key in WRITTEN_REVIEW_TOKENS:
                try:
                    if review[key] is not None:
                        review[key] = [(sentence, self.analyzer.polarity_scores(sentence)) for sentence in review[key]]
                    else:
                        review[key] = []
                except TypeError:
                    print("TypeError: {}".format(review))
                    raise SystemExit
        return


def write_reviews_to_file(reviewsData):
    with open("{}/company_reviews_analyzed.json".format("../data"), "w+") as f:
        f.write(json.dumps(reviewsData, sort_keys=True, indent=2))


def main():
    data = json_data("company_reviews")
    sa = SentimentAnalysis(data)
    for company in data:
        print(company)
        sa.tokenize(company)
        sa.analyze(company)
    data = sa.data
    write_reviews_to_file(data)

if __name__ == "__main__":
    main()
