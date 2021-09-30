# Use gnuplot5 to run this script
#

LOOP = "#4671d5"; PVS = "#cc1414"; P4 = "#2eb519"
FONTL = ",22"
set auto x
set grid xtics ytics lw 1.6
set xtics 100
set ytics 0.2

set yrange[0:1]
#set xrange[12:24]
set xlabel '{/Helvetica:Bold Time (ms)}'
set ylabel '{/Helvetica:Bold CDF}'
set key outside horizontal center top width -1.2
set terminal postscript eps enhanced color font 'Helvetica,20'
set size 1, 0.6
set title font FONTL
set xtics font FONTL
set ytics font FONTL
set xlabel font FONTL
set ylabel font FONTL
set output 'plot.eps'

set datafile separator ';'

set style rectangle fs solid border lw 4

plot    'table.csv' using 1:2 with steps title "vIFC" lw 4 lt rgb P4, \
        'table.csv' using 1:3 with steps title "No vIFC" lw 4 lt rgb PVS
