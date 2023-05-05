echo 'BENCHMARK START'
for i in {1..15}
do
    echo iter $i
    for j in {3,4}
    do
        for d in {5,20}
        do
            python main.py -pid $j -iid $i -d $d -pt 1 -n 'ModCMA'
            python main.py -pid $j -iid $i -d $d -pt 1 -n 'ModCMA-[0]' -im center
            python main.py -pid $j -iid $i -d $d -pt 2 -n 'SP-CMA[50]'
            python main.py -pid $j -iid $i -d $d -pt 3 -n 'SP-CMA[20]'
            python main.py -pid $j -iid $i -d $d -pt 4 -n 'SP-CMA[10]'
        done
    done
done
echo 'BENCHMARK COMPLETE'