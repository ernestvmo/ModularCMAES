echo "BENCHMARK START"
for i in {1..15}
do
    echo iter $i
    for j in {3,4}
    do
        echo problem $j
        for d in {5,20}
        do
            python main.py -pid $j -iid $i -d $d -pt 2 -n "SP-CMA[50]"
            python main.py -pid $j -iid $i -d $d -pt 3 -n "SP-CMA[20]"
            python main.py -pid $j -iid $i -d $d -pt 4 -n "SP-CMA[10]"
            
            for t in {500,1000}
            do
                for r in {.1,.2}
                do
                    python main.py -pid $j -iid $i -d $d -pt 2 -n "SP-CMA[50]-INFO(${t}x${r})" -is $t $r
                    python main.py -pid $j -iid $i -d $d -pt 3 -n "SP-CMA[20]-INFO(${t}x${r})" -is $t $r
                    python main.py -pid $j -iid $i -d $d -pt 4 -n "SP-CMA[10]-INFO(${t}x${r})" -is $t $r
                done
            done
        done
    done
done
echo "BENCHMARK COMPLETE"