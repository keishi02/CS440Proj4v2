##############################################
##
##  CS440 Project 4
##  
##  Important: fill you name and PUID
##  
##  Name: Keishi Vannithamby
##  PUID: 00326543721
#############################################

from pyspark import SparkConf,SparkContext
from pyspark.streaming import StreamingContext
from pyspark.sql import Row,SQLContext
from pyspark.sql.functions import explode
from pyspark.sql.functions import col
import sys
import heapq

def aggregate_global_topk(new_values, global_topk):

    #HINT: $new_values format is [integer1, integer2 .....]
    #       return values format should also be a integer list
    ########### TODO Start #####################################
    if len(new_values) >= 10:
        new_values = heapq.nlargest(10, new_values)
    else:
        new_values = heapq.nlargest(len(new_values), new_values)
    if global_topk == None: 
        global_topk = new_values
    else:
        global_topk.extend(new_values)
        
    print("global")
    print(global_topk)
 #   if len(new_values) >= 10:
 #       global_topk = new_values-10:]

    ########### TODO End #####################################
    return global_topk


def get_sql_context_instance(spark_context):
    if ('sqlContextSingletonInstance' not in globals()):
        globals()['sqlContextSingletonInstance'] = SQLContext(spark_context)
    return globals()['sqlContextSingletonInstance']

def process_global(time, rdd):
    try:
        # Get spark sql singleton context from the current context
        sql_context = get_sql_context_instance(rdd.context)
        # convert the RDD to Row RDD
        row_rdd = rdd.map(lambda w: Row(global_topk=w[1]))
        python_list = []

        # HINT: row_rdd now only have one row, format is as following
        #
        # ------- global_topk--------
        # - [7868, 9478, ...., 8898]-
        # ---------------------------
        #
        # Sort the integers if necessary, and extract top 10 integers
        # to variable $python_list


        ########### TODO Start #####################################
        rdd_list = row_rdd.map(list)
        for i in rdd_list.collect():
            python_list.extend(i)
        python_list = [item for items in python_list for item in items]
        if (len(python_list) >= 10):
            python_list = heapq.nlargest(10, python_list)
        else:
            python_list = heapq.nlargest(len(python_list), python_list)
        ########### TODO End ######################################
        print("python_list")
        print(python_list)
        if (len(python_list) != 0):
            fd = open("./result/task2.txt", "a")
            fd.write(' '.join( str(ele) for ele in python_list ))
            fd.write('\n')
            fd.close()
    except:
        e1 = sys.exc_info()[0]
        e2 = sys.exc_info()[1]
        print("Error: %s %s" % (e1, e2))

def process_window(time, rdd):
    try:
        print("----------- %s -----------" % str(time))
        
        python_list = []

        # HINT: rdd have many rows, each row only contains one integer
        #   Sort these integers and extract the largest 10 integers to
        #   variable $python_list
        ########### TODO Start #####################################
        for i in rdd.collect():
            python_list.append(i)
        if len(python_list) >= 10:
            python_list = heapq.nlargest(10, python_list)
        else:
            python_list = heapq.nlargest(len(python_list), python_list)
        #print(python_list)
        ########### TODO End ######################################
        if (len(python_list) != 0): 
            fd = open("./result/task1.txt", "a")
            fd.write(' '.join( str(ele) for ele in python_list ))
            fd.write('\n')
            fd.close()
    except:
        e1 = sys.exc_info()[0]
        e2 = sys.exc_info()[1]
        print("Error: %s %s" % (e1, e2))

# create spark configuration
conf = SparkConf()
conf.setAppName("StreamApp")

# create spark context with the above configuration
sc = SparkContext(conf=conf)
sc.setLogLevel("ERROR")

# create the Streaming Context from the above spark context with interval size 3 seconds
ssc = StreamingContext(sc, 3)

# setting a checkpoint to allow RDD recovery
ssc.checkpoint("checkpoint_topk")

# read data from port 9009
dataStream = ssc.socketTextStream("localhost",9009)

# parse input from string to integer
dataStream = dataStream.map(lambda x: int(x))

# do processing for each RDD generated in each interval
dataStream.foreachRDD(process_window)

tags = dataStream.map(lambda x: (1, x))

tags_totals = tags.updateStateByKey(aggregate_global_topk)

# do processing for global topk
tags_totals.foreachRDD(process_global)

# start the streaming computation
ssc.start()
# wait for the streaming to finish
ssc.awaitTermination()
