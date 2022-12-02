# Introduction


The research will investigate if WordNet's human-annotated semantic relations database is better at capturing word meanings than machine-learned word embedding like word2vec or BERT's embedding layer. We hypothesise that, as long as we are in the lexical database's vocabulary, WordNet is superior in describing semantic relationships between words compared to trained word embeddings.

To compare the word representational power of both approaches, we propose a novel metric that utilises an exciting phenomenon found in Wikipedia. Starting from any randomly selected Wikipedia article and continually clicking on one of the first few hyperlinks in the current article, we eventually end up with the article for Philosophy. Apart from two edge cases (cycles and dead-ends), the phenomenon is measurable for all articles. It stems from Wikipedia's nature to describe an entity's category in the first few paragraphs of an article. At every traversal step, we move up one or a few steps in the category (abstraction) chain, eventually ending up at the (arguably) most abstract entity, Philosophy.

The proposed metric is as follows. From a carefully selected set of starter articles (more on selection strategies in Section 3), traverse the hyperlink chain until one of the three terminating conditions is reached (cycle, dead-end, and Philosophy article) for each of the three word-selection strategies. The baseline word selection strategy is to select a hyperlink randomly (from the first X hyperlinks in the article). We select the word with the shortest concept relationship path to 'philosophy' in the WordNet word selection strategy. In the embedding word selection strategy, we select the word whose vector has the smallest cosine similarity metric to the vector of 'philosophy'. This metric can accurately describe and compare how well human-annotated taxonomies and trained word embeddings capture semantic relations.

The possible impact of the research is three-fold:
It provides insight into how well WordNet captures word meanings compared to trained word embeddings.
The proposed metric can be re-used to measure the semantic relationship capturing capacity of newly created word embeddings and taxonomies.
It allows comparing the concept relation capturing capacity of word embedding methods.


# Background and related work


One of the central subjects of the research is WordNet: a manually created database of more than 150 000 words with their semantic and syntactic relations. It was introduced in 1995 in REF, and has been immensely influential in the field of (computational) linguistics. Fundamentally, it categorises words along two axes: synonyms and hyponyms. Words are grouped into sets of synonyms called synsets. These synsets are nodes in the WordNet, where vertices represent the hyponym relations. 

Word embedding or word representation is an umbrella term that describes the Natural Language Processing task of feature selection and extraction for words REF. It is a technique to encode words as real-valued vectors that represent word meanings. Thus, words that approximately mean the same thing are closer together in the multi-dimensional vector space. During the research, we will investigate two different word embedding techniques: word2vec and the embedding layer of the transformer model BERT. word2vec was introduced in 2013 in REF, and it utilises a simple shallow, two-layer neural network to produce word vectors. It has numerous advantages compared to earlier strategies, such as latent semantic analysis REF. BERT is an influential transformer model introduced in 2018 in the paper REF. It is a predecessor to newly released transformer models such as GPT-2 and GPT-3. Transformer models utilise word embedding layers to encode text before they process them. In this research, we evaluate classical and more cutting-edge word embedding techniques to ensure that our results are representative.

As the introduction mentions, our research utilises the "hop2phil" property of Wikipedia articles. We have conducted a preliminary investigation into the validity of this property and found that it stands for the majority of randomly selected articles. The source code for this investigation is accessible through LINK. Note that this was only a preliminary inquiry, so the randomly selected starter pages might not have been perfectly distributed uniformly. However, the test shows that only a tiny fraction of traversals lead to either cycles or dead-ends. As this phenomenon is almost trivial from the structure of Wikipedia, no research has been found that thoroughly investigates the dynamics behind it.

However, previous research that utilises the semantic connectivity of Wikipedia articles has been conducted. REF uses Wikipedia's categorical system and semantic connectivity to compile a large-scale taxonomy. They have compared their generated database with the two well-established taxonomies, WordNet and ResearchCyc, and found that their Wikipedia-derived taxonomy was competitive with theirs. They reason this might be because they have utilised a well-maintained and already structured knowledge base to feed into their derivation processes.

REF proposed concept vectorisation methods by making use of Wikipedia's category system. These concept vectors describe what concept belongs to what categories and can be used in many applications, such as information extraction and document classification. The research, however, did not demonstrate concrete applications of their algorithms. Their Vector-based Vector Generation method (VVG) has been used in other research papers (REF, REF) to calculate the membership scores of a concept.

REF uses Wikipedia's category and page network to construct a novel semantic similarity metric. As an example, their metric shows a semantic similarity between "train" and "car" of 6.31 but only 0.92 for "stock" and "jaguar" on a scale of 0 to 10. Comparing their metric with other similar metrics, they say they have proved its "reasonableness". 

The previous research papers elaborated on the last three paragraphs show that using Wikipedia's semantic connectivity nature is a reasonable choice as it can provide valuable insight into the semantic similarity of words.


# Research question


The question the research aims to answer is the following. Using the proposed metric based on Wikipedia's hyperlink network, and that we only consider words inside WordNet's vocabulary, does WordNet perform better at capturing semantic relationships than trained word embedding models word2vec and BERT's embedding layer?

The proposed approach is as follows. Select a set of articles from Wikipedia. For each of these pages, try to traverse to the Philosophy article by hopping from hyperlink to hyperlink. Repeat this process for every starter page and word selection strategy. Not all traversals lead to the target article. We define three possible terminating conditions: a) the target article is reached, b) a cycle is detected, and c) a dead-end is reached. A cycle means the traversal enters an infinite loop, hopping around the same articles. A dead-end can mean a parsing error in the article or an article that does not have enough hyperlinks.

Word selection strategies are applied at every traversal step and determine the next node in the traversal chain. A well-performing strategy would select words semantically closest to the target word 'philosophy', thus minimising the number of hops to reach the target article. An ill-performing strategy would wander around either never finding the target article (maybe ending up in a terminating condition) or finding it with a sub-optimal number of steps. 

Baseline word selection strategy. A baseline word selection strategy will be used to compare results. In this strategy, we select a hyperlink randomly from the first N links in an article. This strategy would likely be ill-performing.

WordNet word selection strategy. Select one with the shortest concept relationship path to the word 'philosophy' from the first N hyperlinks in an article. The exact implementation details are unclear at this stage, but the NLTK Python module's WordNet integration will determine the shortest path between two synsets.

Embedding word selection strategy. Select one with the highest cosine similarity to the target word from the first N hyperlinks in an article. This strategy will have two versions. Version A will use word2vec's embedding vectors to determine similarity scores, and Version B will use BERT's word embedding layer.

Correctly selecting the set of starter Wikipedia articles is a crucial prerequisite for representative results.

The articles have to be uniformly distributed in terms of abstractiveness. The set has to contain an equal number of articles explaining concrete concepts (like "BMW X1") and more abstract concepts (like "religion"). A possible way could be to measure the number of hops to get to Philosophy by just using the first links in an article. This way, the hop length will be higher for concrete articles and lower for more abstract articles. However, this approach has many edge cases, so some of the pages will have to be selected manually, as there is no efficient and reliable automation available to determine an article's concreteness.

The number of articles has to be sufficiently high. Considering that the time required to hop between 15 articles is around 7 seconds (due to a series of GET requests and HTML parsing steps), a reasonable starter page size could be in the thousands. This number can be increased in future experiments when more powerful machines are available. However, as the research involves manual starter page set selection, in the first experiments, this number will be in the dozens.

After running the hopping algorithm for every article in the starter set, we take the mean M of the hops required to reach the Philosophy for every word selection strategy. The hypothesis is that M will be the highest for the baseline selection strategy and that the WordNet selection strategy M will be lower than the embedding selection M. This would mean that from a set of words, WordNet can more accurately find the closest to a target word in terms of semantic similarity compared to trained word embeddings.