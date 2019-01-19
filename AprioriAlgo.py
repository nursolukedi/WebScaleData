''''
    -f DATASET.csv -s minSupport -c minConfidence
'''

import sys
import time

from itertools import chain, combinations
from collections import defaultdict
from optparse import OptionParser

def subsets(arr):
    #Returns non empty subsets of arr
    return chain(*[combinations(arr, i+1) for i, a in enumerate(arr)])

def returnItemsWithMinSupport(itemSet, transcationList, minSupport, freqSet):
    #Calculates the support for items in the itemSet and returns a subset of
    #the itemSet each of whose elements satisfies the minimum support
    _itemSet = set()
    localSet = defaultdict(int)

    for item in itemSet:
        for transaction in transcationList:
            if item.issubset(transaction):
                freqSet[item] += 1
                localSet[item] +=1
    for item, count in localSet.items():
        support = float(count)/len(transcationList)
        if support >= minSupport:
            _itemSet.add(item)

    return _itemSet

def joinSet(itemSet, lenght):
    #Join a set with itself and returns the n-element itemset
    return set([i.union(j) for i in itemSet for j in itemSet if len(i.union(j)) == lenght])

def getItemSetTransactionList(data_iterator):
    transactionList = list()
    itemSet = set()
    for record in data_iterator:
        transaction = frozenset(record)
        transactionList.append(transaction)
        for item in transaction:
            itemSet.add(frozenset([item]))
    return itemSet, transactionList

def runApriori(data_iter, minSupport, minConfidence):
    #Run the Apriori algorithm. data_iter is a record iterator
    #Return both
    #   -items(tuple, support)
    #   - rules ((pretuple, posttuple), confidence)
    itemSet, transactionList = getItemSetTransactionList(data_iter)
    freqSet = defaultdict(int)
    largeSet = dict()

    oneCSet = returnItemsWithMinSupport(itemSet, transactionList, minSupport, freqSet)

    currentLSet = oneCSet
    k = 2
    while(currentLSet != set([])):
        largeSet[k-1] = currentLSet
        currentLSet = joinSet(currentLSet, k)
        currentCSet = returnItemsWithMinSupport(currentLSet, transactionList, minSupport, freqSet)
        currentLSet = currentCSet
        k = k+1

    def getSupport(item):
        #Local function which returns the support of an item
        return float(freqSet[item])/len(transactionList)

    toRetItems = []
    for key, value in largeSet.items():
        toRetItems.extend([(tuple(item), getSupport(item)) for item in value])


    toRetRules = []
    for key, value in largeSet.items():
        for item in value:
            _subsets = map(frozenset, [x for x in subsets(item)])
            for element in _subsets:
                remain = item.difference(element)
                if len(remain) > 0:
                    confidence = getSupport(item)/getSupport(element)
                    if confidence >= minConfidence:
                        toRetRules.append(((tuple(element), tuple(remain)), confidence))

    return toRetItems, toRetRules

def printResults(items, rules):
    #Prints the generated itemsets sorted by support and the confidence ruşes sorted by confidence
    for item, support in sorted(items, key=lambda support: support):
        print("item: ", str(item), " , support : ", support)
    print("\n------------------------ RULES:")

    for rule,confidence in sorted(rules, key=lambda confidence: confidence):
        pre, post = rule
        print("Rule: ", str(pre), " ==> ", str(post), " , confidence : ", confidence)

def dataFromFile(fname):
    #Function which reads from the file and yields a generator
    file_iter = open(fname, "rU")
    for line in file_iter:
        line = line.strip().rstrip(",")
        record = frozenset(line.split(","))
        yield record

if __name__ == "__main__":
    start = time.clock()
    optparser = OptionParser()
    optparser.add_option('-f',"--inputFile", dest='input', help='filename containing csv', default=None)
    optparser.add_option('-s',"--minSupport", dest='minS', help='minimum support value', default=0.15, type='float')
    optparser.add_option('-c',"--minConfidence", dest='minC', help='minimum confidence value', default=0.6, type='float')

    (options, args) = optparser.parse_args()

    inFile = None
    if options.input is None:
        inFile = sys.stdin
    elif options.input is not None:
        inFile = dataFromFile(options.input)
    else:
        print("No dataset filenema specified, system with ext \n")
        sys.exit('System will exit')

    minSupport = options.minS
    minConfidence = options.minC

    items, rules = runApriori(inFile, minSupport, minConfidence)
    printResults(items, rules)
    print("Time:", time.clock() - start)









