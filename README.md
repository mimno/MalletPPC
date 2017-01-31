## Calculate mutual information between words and another variable

A topic model asserts that word choice depends solely on topics, and that no further information about a document has any effect.
This *posterior predictive check* evaluates whether that assumption holds.
Conditioning on a given topic, we consider whether there is mutual information between two variables: the observed word token and a property of the document containing that token.
By default, the property of the document is its identity. We can also specify a file that maps each document to a value, such as a date or a grouping of documents.

The first step is to generate mallet state files representing saved Gibbs sampling states.
Here I'll use an example consisting of online business reviews.

	bin/mallet import-file --input reviews.20k.txt --output reviews.seq --stoplist-file stopwords.txt --keep-sequence
	bin/mallet train-topics --input reviews.seq --num-topics 100 --output-state state-1000.gz
	bin/mallet train-topics --input reviews.seq --num-topics 100 --input-state state-1000.gz --output-state state-1100.gz --num-iterations 100
	bin/mallet train-topics --input reviews.seq --num-topics 100 --input-state state-1100.gz --output-state state-1200.gz --num-iterations 100

Now we have three saved sampling states. These files should be gzipped. The format for these files is one row per token, with the following fields separated by a single space:
document order, an unused field, token position within the document, numeric word id, word string, topic id. Lines beginning with "#" are ignored.
For example, 

	0 NA 0 0 lately 8
	0 NA 1 1 feeling 20
	0 NA 2 2 homesick 94
	0 NA 3 3 asian 52
	0 NA 4 4 hitting 71

Now we can run a PPC. This will select topic 56, report scores for the top 20 words, and run 20 replications.

	python mutual_info_ppc.py -t 56 -w 20 -r 20 state-*.gz > by-doc-56.tsv

Using the PPC file, we can now generate a PDF for the top words. This command will look for a file called `topic98.tsv` and create a visualization of actual mutual information values and their replicated values. Using more states results in smoother estimates.

	R -f plot_ppc.R --args by-doc-56.tsv by-doc-56.png

This plot shows the real and replicated discrepancy when we measure the association of words to documents. Are different documents using the topic in the same way, or is there local variation?

![Topic 56 by documents](../master/by-doc-56.png?raw=true)

The dark circles show actual values of the doc/word association function. More frequent words show more association with their documents.
The lighter triangles show replicated values of the doc/word association function.
We see the same pattern: higher ranked, more frequent words are further to the right. Therefore most of the pattern we saw in the real values can be explained just rhough word frequency.
But not all! There is also a consistent pattern that the real values are greater than the range of replicated values.
Documents are not using the topics as consistently as we would expect if the model were true.

What might explain this variation?
The next step is to generate a "labels" file with one line for each document that indicates some interesting grouping of words.
I'll use a file with star ratings, from 1 to 5.
What words are present regardless of star rating, and which are sensitive to the rating?

This will select topic 56, group by star rating, and report scores for the top 20 words, and run 20 replications.

	python mutual_info_ppc.py -t 56 -g ratings.txt -w 20 -r 20 state-*.gz > by-rating-56.tsv

Using the PPC file, we can now generate a PDF for the top words. This command will look for a file called `topic98.tsv` and create a visualization of actual mutual information values and their replicated values. Using more states results in smoother estimates.

	R -f plot_ppc.R --args by-rating-56.tsv by-rating-56.png

![Topic 56 by ratings](../master/by-rating-56.png?raw=true)