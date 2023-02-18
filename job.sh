#!/bin/sh
pip3 install grequests
pip3 install bs4
pip3 install python-dateutil

while :
do
 python3 scrape_v2.py
done
