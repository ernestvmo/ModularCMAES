echo 'BENCHMARK START'
for i in {1..15}
do
    echo iter $i
    for j in {3,4}
    do
        for d in {5,20}
        do
            python main.py -pid $j -iid $i -d $d -pt 2 -n 'SP-CMA[50]'
            python main.py -pid $j -iid $i -d $d -pt 2 -n 'SP-CMA[50]-SVMi' -ic svm-i
            python main.py -pid $j -iid $i -d $d -pt 2 -n 'SP-CMA[50]-LHS-SVMi' -im lhs -ic svm-i
            python main.py -pid $j -iid $i -d $d -pt 2 -n 'SP-CMA[50]-SVMo' -ic svm-o
            python main.py -pid $j -iid $i -d $d -pt 2 -n 'SP-CMA[50]-LHS-SVMo' -im lhs -ic svm-o

            python main.py -pid $j -iid $i -d $d -pt 3 -n 'SP-CMA[20]'
            python main.py -pid $j -iid $i -d $d -pt 3 -n 'SP-CMA[20]-SVMi' -ic svm-i
            python main.py -pid $j -iid $i -d $d -pt 3 -n 'SP-CMA[20]-LHS-SVMi' -im lhs -ic svm-i
            python main.py -pid $j -iid $i -d $d -pt 3 -n 'SP-CMA[20]-SVMo' -ic svm-o            
            python main.py -pid $j -iid $i -d $d -pt 3 -n 'SP-CMA[20]-LHS-SVMo' -im lhs -ic svm-o
            
            python main.py -pid $j -iid $i -d $d -pt 4 -n 'SP-CMA[10]'
            python main.py -pid $j -iid $i -d $d -pt 4 -n 'SP-CMA[10]-SVMi' -ic svm-i
            python main.py -pid $j -iid $i -d $d -pt 4 -n 'SP-CMA[10]-LHS-SVMi' -im lhs -ic svm-i
            python main.py -pid $j -iid $i -d $d -pt 4 -n 'SP-CMA[10]-SVMo' -ic svm-o
            python main.py -pid $j -iid $i -d $d -pt 4 -n 'SP-CMA[10]-LHS-SVMo' -im lhs -ic svm-o
        done
    done
done
echo 'BENCHMARK COMPLETE'