echo 'BENCHMARK START'
for i in {1..15}
do
    echo iter $i
    for j in {3,4}
    do
        for d in {5,20}
        do
            python main.py -pid $j -iid $i -d $d -pt 2 -n 'SP-CMA[50]-UNIF'
            python main.py -pid $j -iid $i -d $d -pt 2 -n 'SP-CMA[50]-LHS' -im lhs
            python main.py -pid $j -iid $i -d $d -pt 2 -n 'SP-CMA[50]-SOBOL' -im sobol
            python main.py -pid $j -iid $i -d $d -pt 2 -n 'SP-CMA[50]-HALTON' -im halton
            python main.py -pid $j -iid $i -d $d -pt 2 -n 'SP-CMA[50]-GAUSSIAN' -im gaussian

            python main.py -pid $j -iid $i -d $d -pt 3 -n 'SP-CMA[20]-UNIF'
            python main.py -pid $j -iid $i -d $d -pt 3 -n 'SP-CMA[20]-LHS' -im lhs
            python main.py -pid $j -iid $i -d $d -pt 3 -n 'SP-CMA[20]-SOBOL' -im sobol
            python main.py -pid $j -iid $i -d $d -pt 3 -n 'SP-CMA[20]-HALTON' -im halton
            python main.py -pid $j -iid $i -d $d -pt 3 -n 'SP-CMA[20]-GAUSSIAN' -im gaussian

            python main.py -pid $j -iid $i -d $d -pt 4 -n 'SP-CMA[10]-UNIF'
            python main.py -pid $j -iid $i -d $d -pt 4 -n 'SP-CMA[10]-LHS' -im lhs
            python main.py -pid $j -iid $i -d $d -pt 4 -n 'SP-CMA[10]-SOBOL' -im sobol
            python main.py -pid $j -iid $i -d $d -pt 4 -n 'SP-CMA[10]-HALTON' -im halton
            python main.py -pid $j -iid $i -d $d -pt 4 -n 'SP-CMA[10]-GAUSSIAN' -im gaussian
        done
    done
done
echo 'BENCHMARK COMPLETE'