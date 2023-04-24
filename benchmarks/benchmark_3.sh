echo 'BENCHMARK START'
for i in {1..3}
do
    echo iter $i
    for j in {3,4}
    do
        for d in {5,20}
        do
            python main.py -pid $j -iid $i -d $d -pt 1 -n 'ModCMA'
            python main.py -pid $j -iid $i -d $d -pt 3 -n 'SP[20]-CMA'
            python main.py -pid $j -iid $i -d $d -pt 3 -n 'SP[20]-CMA-INFO(500)' -sp 500
            python main.py -pid $j -iid $i -d $d -pt 3 -n 'SP[20]-CMA-INFO(5000)' -sp 5000
        done
    done
done
echo 'BENCHMARK COMPLETE'