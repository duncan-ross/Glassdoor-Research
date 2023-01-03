import code
import os
import re
import string

from definitions import DATA_DIR
from nltk.corpus import stopwords


TEXT_DIR = DATA_DIR + "/nyse_companies/sentiment_text/"

# Create the dictionary of words to be replaced. Compile a regex object to do this.
rep = {
    "work-life": "work life",
    "work/life": "work life",
    "work\life": "work life",
    "start up": "startup",
    "start-up": "startup",
    "wall st": "wall street",
}
rep = dict((re.escape(k), v) for k, v in rep.items())
pattern = re.compile("|".join(rep.keys()))

# Iterate through the files
for file_name in os.listdir(TEXT_DIR):
    if file_name.endswith(".txt"):
        print(file_name)

        # Read in the old text
        with open(TEXT_DIR + file_name, "r") as f:
            old_text = f.read()

        # Move the text to lower case. Replace the words and print out how many words were replaced.
        new_text = pattern.subn(lambda m: rep[re.escape(m.group(0))], old_text.lower())
        print("Instances of words replaced: " + str(new_text[1]))

        # Remove any non-printable characters
        printable = set(string.printable)
        new_text = filter(lambda x: x in printable, new_text[0])

        ## Correct any faulty punctuation missing spaces.
        # First, compile a regex expression that matches any instance where there is a letter ([A-Za-z]) followed by a puncutation (\.|!|\?|;) follwed by another alphanumeric character (\w). The () indicate that each of the three characters is considered its own group to be referenced later.
        p = re.compile("([A-Za-z])(\.|!|\?|;)(\w)")
        # Next, replace any instance of the regex expression above with the first character followed by the puncutaion, then a space, then the thrid character  r'\1\2 \3'. (Note: \1 references group one in the regex above, \2 represents group two, and \3 represents the third group. The r that preceeds the string ensures that the backslashes don't escape the numbers, so that it uses the character corresponding to the group instead of char(1), char(2), and char(3))
        new_text = re.subn(p, r"\1\2 \3", new_text)
        print("Instances of punctuation without spaces replaced: " + str(new_text[1]))

        # # Remove any punctuation --THIS MAY BE WRONG. UPDATE IF CLASSSIFICATION IS RUN AGAIN.
        # punctuation = set(('.','!','?',',','\'','(',')'))
        # new_text = filter(lambda x: x not x in punctuation, new_text[0])

        # Write the results to a new file
        with open(TEXT_DIR + file_name, "w+") as f:
            f.write(new_text[0])
