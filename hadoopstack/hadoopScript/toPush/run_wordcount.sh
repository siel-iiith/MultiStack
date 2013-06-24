#!/bin/bash
# Run the famous WordCount example on Hadoop cluster
# Run this script on Master

mkdir -p /tmp/wordcount
cd /tmp/wordcount
#wget http://www.gutenberg.org/cache/epub/20417/pg20417.txt
#wget http://www.gutenberg.org/ebooks/20417.txt.utf8
#wget http://www.gutenberg.org/cache/epub/5000/pg5000.txt
wget http://norvig.com/big.txt

cd /usr/local/hadoop/bin

# create input directory
./hadoop fs -mkdir wordcount_input

# copy data to input directory
echo "Copying input files to hdfs..."
./hadoop fs -copyFromLocal /tmp/wordcount/* wordcount_input/

# verify
./hadoop fs -ls wordcount_input/

# Run the example
./hadoop jar ../hadoop-examples-*.jar wordcount wordcount_input wordcount_output

# verify the output
./hadoop dfs -cat wordcount_output/part-* | less


