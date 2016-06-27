# NewsClassification

### What is it about?
This is a project aimed at training and evaluating various classifiers on news articles collected from [NU.nl](http://www.nu.nl),
to then predict their popularity as expressed in number of comments.

### What are its components?
`crawling` contains a script to collect articles from the news site, save them to a database,
and update them with the number of comments they have received.
<br />
`preprocessing` contains a script for preprocessing all text in the collected articles.
<br />
`learning` contains scripts to transform the collected data into input for the classifiers,
and a script to train and evaluate classifiers on the data.

### What about results?
Currently, when trained on a thousand articles, the _multinomial Naive Bayes_ classifier can classify 50% of the articles correctly
while the _linear Support Vector Machine_ scores around 48%.

### What next?
Some of the ideas for trying to improve classification performance are:
* Collecting more data
* Applying feature selection
* Investigating the effects of training the classifiers with different parameters

### Further details?
See the [wiki](https://github.com/S-Ercan/NewsClassification/wiki).
