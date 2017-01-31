## This script reads one or more Mallet state files and calculates instantaneous mutual information
##  between documents and words for each topic.

import sys, gzip, random, math, getopt
from collections import Counter

try:
    opts, args = getopt.getopt(sys.argv[1:], "t:g:w:r:")
except getopt.GetoptError as err:
    print("Usage: mutual_info_ppc.py [-t target topic] [-g grouping file] [-w num words] [-r num replications] state_file [state_file...]")
    print("  * \"grouping file\" should be one group tag per line, one line for each document.")
    print("  * Use -w 0 to calculate overall mutual information for all words, -w [n>0] for information about specific words. [Default 20]")
    print("  * Default number of replications is 20.")
    sys.exit(2)

target_topic = None
grouping = []

top_words = 20
num_replications = 20
full_vocabulary = False

for option, argument in opts:
    if option == "-t":
        target_topic = int(argument)
    elif option == "-g":
        with open(argument) as grouping_file:
            for line in grouping_file:
                grouping.append(line)
    elif option == "-w":
        top_words = int(argument)
        if top_words <= 0:
            full_vocabulary = True
    elif option == "-r":
        num_replications = int(argument)

vocab_ids = dict()
id_vocab = dict()

tokens = []

group_counter = Counter()
word_counter = Counter()


for state_file in args:
    with gzip.open(state_file, 'rt') as f:
        for line in f:
            if line.startswith("#"):
                continue
            
            fields = line.split(" ")
            topic = int(fields[5])
            
            if target_topic != None and topic != target_topic:
                continue
            
            doc_id = int(fields[0])
            if len(grouping) != 0:
                group_id = grouping[doc_id]
            else:
                group_id = doc_id
            
            token_id = int(fields[3])
            word = fields[4]
            
            if not word in vocab_ids:
                vocab_ids[word] = token_id
                id_vocab[token_id] = word
            
            word_counter[token_id] += 1
            group_counter[group_id] += 1
            
            tokens.append((token_id, group_id))

def elementwise_mutual_information(tokens, tag):
    rank = 1
    for word, n in top_words:
        p_word = word_counter[word] / n_tokens
        word_group_counts = Counter([x[1] for x in tokens if x[0] == word])
    
        score = 0.0
        for group in word_group_counts.keys():
            p_group = group_counter[group] / n_tokens
            p_word_given_group = word_group_counts[group] / group_counter[group]
            score += p_group * p_word_given_group * math.log(p_word_given_group / p_word)
            
        print("{}\t{}\t{}\t{}\t{}".format(id_vocab[word], tag, score, rank, p_word, target_topic))
        
        rank += 1

def mutual_information(tokens, tag):
    score = 0.0
    for word, n in word_counter.most_common():
        p_word = word_counter[word] / n_tokens
        word_group_counts = Counter([x[1] for x in tokens if x[0] == word])
        
        for group in word_group_counts.keys():
            p_group = group_counter[group] / n_tokens
            p_word_given_group = word_group_counts[group] / group_counter[group]
            score += p_group * p_word_given_group * math.log(p_word_given_group / p_word)
            
    print("{}\t{}\t{}".format(tag, score, target_topic))

n_tokens = len(tokens)

if full_vocabulary:
    mutual_information(tokens, "Real")
    
    for sample in range(num_replications):
        words = [x[0] for x in tokens]
        groups = [x[1] for x in tokens]
    
        random.shuffle(words)
    
        shuffled_tokens = list(zip(words, groups))
    
        mutual_information(shuffled_tokens, "Replicated")
else:
    top_words = word_counter.most_common(top_words)
    
    elementwise_mutual_information(tokens, "Real")
    
    for sample in range(num_replications):
        words = [x[0] for x in tokens]
        groups = [x[1] for x in tokens]
    
        random.shuffle(words)
    
        shuffled_tokens = list(zip(words, groups))
    
        elementwise_mutual_information(shuffled_tokens, "Replicated")
    