echo 'BENCHMARK START'
for i in {1..15}
do
    echo iter $i
    for j in {3,4}
    do
        echo problem $j
        for d in {5,20}
        do
            python main.py -pid $j -iid $i -d $d -pt 2 -n 'SP-CMA[50]'
            python main.py -pid $j -iid $i -d $d -pt 3 -n 'SP-CMA[20]'
            python main.py -pid $j -iid $i -d $d -pt 4 -n 'SP-CMA[10]'

            if [ $d -eq 5 ]; then
                python main.py -pid $j -iid $i -d $d -pt 2 -n 'SP-CMA[50]-INFO(500)' -is 500 4
                python main.py -pid $j -iid $i -d $d -pt 3 -n 'SP-CMA[20]-INFO(500)' -is 500 4
                python main.py -pid $j -iid $i -d $d -pt 4 -n 'SP-CMA[10]-INFO(500)' -is 500 4
            fi

            if [ $d -eq 20 ]; then
                python main.py -pid $j -iid $i -d $d -pt 2 -n 'SP-CMA[50]-INFO(500)' -is 1000 2
                python main.py -pid $j -iid $i -d $d -pt 3 -n 'SP-CMA[20]-INFO(500)' -is 1000 2
                python main.py -pid $j -iid $i -d $d -pt 4 -n 'SP-CMA[10]-INFO(500)' -is 1000 2
            fi
        done
    done
done
echo 'BENCHMARK COMPLETE'